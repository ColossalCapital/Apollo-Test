"""
Smart Router - Routes API requests to correct models with privacy enforcement

This is the core routing logic that:
1. Parses request context
2. Determines which model to use
3. Enforces privacy/access control
4. Routes to appropriate agent
5. Logs interactions for training
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .request_models import (
    RequestContext, AgentAnalysisRequest, AgentAnalysisResponse,
    ModelInfo, AppContextEnum, PrivacySchemaEnum
)
from config.model_config import (
    ModelIsolationStrategy, ModelAccessControl,
    AppContext, PrivacySchema, AtlasTier, DeltTier
)
from learning.continuous_learner import ContinuousLearner
from agents.base_agent import AgentContext

logger = logging.getLogger(__name__)


class SmartRouter:
    """
    Routes API requests to correct models with privacy enforcement
    
    Flow:
    1. Parse request context
    2. Determine model path (personal/team/org)
    3. Check access permissions
    4. Load appropriate model
    5. Execute agent analysis
    6. Log interaction (if enabled)
    7. Return response with model info
    """
    
    def __init__(
        self,
        agent_registry: Dict[str, Any],
        continuous_learner: Optional[ContinuousLearner] = None
    ):
        """
        Initialize smart router
        
        Args:
            agent_registry: Registry of all agents
            continuous_learner: Continuous learning system (optional)
        """
        self.agents = agent_registry
        self.learner = continuous_learner
        self.request_counter = 0
    
    async def route_request(
        self,
        request: AgentAnalysisRequest
    ) -> AgentAnalysisResponse:
        """
        Route request to appropriate agent with correct model
        
        Args:
            request: Agent analysis request with full context
        
        Returns:
            Analysis response with model info
        """
        
        start_time = datetime.now()
        request_id = f"req_{self.request_counter}_{int(start_time.timestamp())}"
        self.request_counter += 1
        
        try:
            # Step 1: Parse context
            context = request.context
            logger.info(f"📥 Request {request_id}: {context.app_context}/{request.agent_type}")
            logger.info(f"  User: {context.user_id}")
            logger.info(f"  Privacy: {context.privacy}")
            logger.info(f"  Process: {context.process_name}")
            
            # Step 2: Determine model configuration
            model_config = await self._get_model_config(context, request.agent_type)
            logger.info(f"  Model: {model_config['model_type']} ({model_config['base_model']})")
            logger.info(f"  Isolation: {model_config['isolation_level']}")
            
            # Step 3: Check access permissions
            if not await self._check_access(context, model_config):
                raise PermissionError(f"User {context.user_id} cannot access this model")
            
            # Step 4: Get agent
            agent = await self._get_agent(request.agent_type, model_config)
            
            # Step 4.5: Build AgentContext for context-aware analysis
            agent_context = AgentContext(
                app_context=context.app_context,
                user_id=context.user_id,
                org_id=context.org_id,
                team_id=context.team_id,
                atlas_tier=context.atlas_tier,
                delt_tier=context.delt_tier,
                privacy=context.privacy,
                isolation_level=model_config['isolation_level'],
                can_share=model_config['can_share'],
                can_train=model_config['can_train'],
                model_path=model_config.get('model_path'),
                storage_path=self._get_storage_path(context, request.agent_type),
                parent_context=model_config.get('parent_context'),
                conflict_resolution=model_config.get('conflict_resolution', 'last_write_wins')
            )
            
            logger.info(f"  Context: {agent_context.isolation_level} (can_share={agent_context.can_share})")
            
            # Step 5: Execute analysis with context
            if request.quick_mode:
                # Quick mode: static knowledge only
                result = await agent.get_static_knowledge(request.query)
                mode = "static"
            else:
                # Full analysis with LLM and context
                result = await agent.analyze(request.query, context=agent_context)
                mode = result.get("mode", "llm_powered")
            
            # Step 6: Log interaction (if enabled)
            interaction_logged = False
            interactions_until_training = None
            
            if request.log_interaction and self.learner and mode != "static":
                await self._log_interaction(
                    context=context,
                    agent_type=request.agent_type,
                    query=request.query,
                    response=result
                )
                interaction_logged = True
                
                # Get training stats
                stats = self.learner.get_training_stats(user_id=context.user_id)
                buffer_key = self._get_buffer_key(context, request.agent_type)
                current_interactions = len(self.learner.interaction_buffers.get(buffer_key, []))
                interactions_until_training = max(0, self.learner.min_interactions - current_interactions)
            
            # Step 7: Build response
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            response = AgentAnalysisResponse(
                mode=mode,
                result=result,
                model_info=ModelInfo(**model_config),
                response_time_ms=response_time,
                confidence=result.get("confidence", 0.8),
                interaction_logged=interaction_logged,
                interactions_until_training=interactions_until_training,
                request_id=request_id
            )
            
            logger.info(f"✅ Request {request_id} complete ({response_time}ms)")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Request {request_id} failed: {e}")
            raise
    
    async def _get_model_config(
        self,
        context: RequestContext,
        agent_type: str
    ) -> Dict[str, Any]:
        """
        Determine which model to use based on context
        
        Returns model configuration including:
        - model_type: base | user_finetuned | team_finetuned | org_finetuned
        - model_path: local:// or filecoin://
        - base_model: Model name
        - isolation_level: personal | team | org | public
        - can_train: bool
        - can_share: bool
        """
        
        # Convert enums to config enums
        app_context = AppContext(context.app_context.value)
        privacy = PrivacySchema(context.privacy.value)
        atlas_tier = AtlasTier(context.atlas_tier.value) if context.atlas_tier else None
        delt_tier = DeltTier(context.delt_tier.value) if context.delt_tier else None
        
        # Get model configuration
        config = ModelIsolationStrategy.get_model_path(
            user_id=context.user_id,
            org_id=context.org_id,
            atlas_tier=atlas_tier or AtlasTier.PERSONAL,
            privacy_schema=privacy,
            app_context=app_context,
            agent_type=agent_type,
            delt_tier=delt_tier
        )
        
        return config
    
    async def _check_access(
        self,
        context: RequestContext,
        model_config: Dict[str, Any]
    ) -> bool:
        """
        Check if user has access to this model
        
        Rules:
        - Personal models: Only owner
        - Team models: Same team
        - Org models: Same org
        - Public models: Everyone
        """
        
        # For now, assume access is granted
        # In production, this would check:
        # 1. User is owner (for personal models)
        # 2. User is in team (for team models)
        # 3. User is in org (for org models)
        # 4. Model is public (for public models)
        
        return True
    
    async def _get_agent(
        self,
        agent_type: str,
        model_config: Dict[str, Any]
    ) -> Any:
        """
        Get agent instance with correct model loaded
        
        Args:
            agent_type: Type of agent
            model_config: Model configuration
        
        Returns:
            Agent instance
        """
        
        # Get agent class from registry
        if agent_type not in self.agents:
            raise ValueError(f"Agent type '{agent_type}' not found")
        
        agent_class = self.agents[agent_type]
        
        # Create agent instance
        agent = agent_class()
        
        # Configure agent with model
        if model_config["model_type"] != "base":
            # Load personalized model
            agent.model_path = model_config["model_path"]
            agent.model_type = model_config["model_type"]
        
        return agent
    
    async def _log_interaction(
        self,
        context: RequestContext,
        agent_type: str,
        query: Dict[str, Any],
        response: Dict[str, Any]
    ):
        """
        Log interaction for continuous learning
        
        Args:
            context: Request context
            agent_type: Agent type
            query: User query
            response: Agent response
        """
        
        if not self.learner:
            return
        
        # Convert enums
        app_context = AppContext(context.app_context.value)
        privacy = PrivacySchema(context.privacy.value)
        atlas_tier = AtlasTier(context.atlas_tier.value) if context.atlas_tier else None
        delt_tier = DeltTier(context.delt_tier.value) if context.delt_tier else None
        
        # Log interaction
        await self.learner.log_interaction(
            user_id=context.user_id,
            org_id=context.org_id,
            team_id=context.team_id,
            app_context=app_context,
            agent_type=agent_type,
            query=query,
            response=response,
            feedback=None,  # Will be added later via feedback endpoint
            privacy=privacy,
            atlas_tier=atlas_tier,
            delt_tier=delt_tier
        )
    
    def _get_buffer_key(self, context: RequestContext, agent_type: str) -> str:
        """Build buffer key for interaction tracking"""
        
        app = context.app_context.value
        
        if context.privacy in [PrivacySchemaEnum.PERSONAL, PrivacySchemaEnum.PRIVATE]:
            return f"{app}:{agent_type}:{context.user_id}"
        elif context.privacy == PrivacySchemaEnum.ORG_PRIVATE:
            return f"{app}:{agent_type}:{context.org_id}:team:{context.team_id or 'default'}"
        elif context.privacy == PrivacySchemaEnum.ORG_PUBLIC:
            return f"{app}:{agent_type}:{context.org_id}:org"
        else:  # PUBLIC
            return f"{app}:{agent_type}:public"
    
    def _get_storage_path(self, context: RequestContext, agent_type: str) -> str:
        """
        Get storage path for training data based on context
        
        This determines where training data is stored on Filecoin:
        - Personal: {app}/personal/{user_id}/{agent_type}/
        - Team: {app}/team/{org_id}/{team_id}/{agent_type}/
        - Org: {app}/org/{org_id}/{agent_type}/
        - Public: {app}/public/{agent_type}/
        
        The API uses this path to:
        1. Store training interactions
        2. Locate trained models
        3. Manage model versions
        """
        
        app = context.app_context.value
        privacy = context.privacy.value
        
        if context.privacy in [PrivacySchemaEnum.PERSONAL, PrivacySchemaEnum.PRIVATE]:
            return f"{app}/personal/{context.user_id}/{agent_type}/"
        elif context.privacy == PrivacySchemaEnum.ORG_PRIVATE:
            team_id = context.team_id or 'default'
            return f"{app}/team/{context.org_id}/{team_id}/{agent_type}/"
        elif context.privacy == PrivacySchemaEnum.ORG_PUBLIC:
            return f"{app}/org/{context.org_id}/{agent_type}/"
        else:  # PUBLIC
            return f"{app}/public/{agent_type}/"


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import asyncio
    from .request_models import AgentAnalysisRequest, RequestContext
    
    async def main():
        # Initialize router
        router = SmartRouter(agent_registry={})
        
        # Example request
        request = AgentAnalysisRequest(
            context=RequestContext(
                user_id="user123",
                org_id=None,
                team_id=None,
                app_context=AppContextEnum.DELT,
                privacy=PrivacySchemaEnum.PERSONAL,
                delt_tier="individual",
                process_name="trading_dashboard"
            ),
            agent_type="finance",
            query={
                "type": "turtle_trading",
                "asset": "BTC",
                "price_data": {
                    "current_price": 45000,
                    "20_day_high": 44500,
                    "atr": 2500
                }
            },
            quick_mode=False,
            use_personalized=True,
            log_interaction=True
        )
        
        # Route request
        response = await router.route_request(request)
        
        print(f"Response: {response.dict()}")
    
    asyncio.run(main())
