"""
Continuous Learning with Theta EdgeCloud Integration

Uses Theta's optimized infrastructure:
- Persistent volumes for training data
- RAG chatbots for knowledge retrieval
- Model APIs for inference
- GPU clusters for training
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from config.model_config import (
    AppContext, PrivacySchema, AtlasTier, DeltTier,
    ModelIsolationStrategy
)
from .theta_edgecloud import ThetaEdgeCloud

logger = logging.getLogger(__name__)


class ThetaContinuousLearner:
    """
    Continuous learning using Theta EdgeCloud infrastructure
    
    Improvements over basic version:
    - Uses persistent volumes (no repeated downloads)
    - Uses Theta RAG (no Qdrant needed)
    - Deploys models as APIs (no manual serving)
    - Supports GPU clusters (faster training)
    """
    
    def __init__(
        self,
        theta_client: ThetaEdgeCloud,
        min_interactions: int = 100,
        training_interval_days: int = 7
    ):
        self.theta = theta_client
        self.min_interactions = min_interactions
        self.training_interval = timedelta(days=training_interval_days)
        
        # In-memory buffers
        self.interaction_buffers = defaultdict(list)
        self.last_training = {}
        self.active_jobs = {}
        
        # Track user resources
        self.user_volumes = {}  # user_id -> volume_id
        self.user_rag_chatbots = {}  # user_id -> chatbot_id
        self.user_model_apis = {}  # user_id -> api_endpoint
        
        logger.info("🚀 Theta Continuous Learner initialized")
    
    # ========================================================================
    # Initialization (Create User Resources)
    # ========================================================================
    
    async def initialize_user(
        self,
        user_id: str,
        initial_documents: List[str] = None
    ) -> Dict[str, str]:
        """
        Initialize Theta resources for new user
        
        Creates:
        - Persistent volume for training data/models
        - RAG chatbot for knowledge retrieval
        
        Args:
            user_id: User ID
            initial_documents: Initial documents for RAG
        
        Returns:
            Resource IDs
        """
        
        logger.info(f"🎬 Initializing Theta resources for user {user_id}")
        
        # Create persistent volume
        volume_id = await self.theta.create_volume(
            name=f"apollo_user_{user_id}",
            size_gb=100  # 100GB per user
        )
        self.user_volumes[user_id] = volume_id
        logger.info(f"  ✅ Volume created: {volume_id}")
        
        # Create RAG chatbot
        if initial_documents:
            chatbot_id = await self.theta.create_rag_chatbot(
                name=f"apollo_rag_{user_id}",
                documents=initial_documents,
                description=f"Personal knowledge base for user {user_id}"
            )
            self.user_rag_chatbots[user_id] = chatbot_id
            logger.info(f"  ✅ RAG chatbot created: {chatbot_id}")
        
        return {
            "volume_id": volume_id,
            "chatbot_id": chatbot_id if initial_documents else None
        }
    
    async def create_codebase_rag(
        self,
        user_id: str,
        repo_url: str = None,
        local_path: str = None
    ) -> str:
        """
        Create RAG chatbot for codebase analysis
        
        This enables agentic AI to understand codebases!
        
        Args:
            user_id: User ID
            repo_url: Git repository URL
            local_path: Local codebase path
        
        Returns:
            Chatbot ID
        """
        
        chatbot_id = await self.theta.create_codebase_rag(
            name=f"apollo_codebase_{user_id}",
            repo_url=repo_url,
            local_path=local_path,
            file_patterns=["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.rs"]
        )
        
        # Store chatbot ID
        self.user_rag_chatbots[f"{user_id}_codebase"] = chatbot_id
        
        return chatbot_id
    
    # ========================================================================
    # Interaction Logging
    # ========================================================================
    
    async def log_interaction(
        self,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        query: Dict[str, Any],
        response: Dict[str, Any],
        feedback: Optional[float] = None,
        privacy: PrivacySchema = PrivacySchema.PERSONAL,
        atlas_tier: Optional[AtlasTier] = None,
        delt_tier: Optional[DeltTier] = None
    ):
        """
        Log interaction and update RAG knowledge base
        
        Improvements:
        - Also updates Theta RAG chatbot
        - Stores on persistent volume
        """
        
        # Create interaction record
        interaction = {
            "user_id": user_id,
            "org_id": org_id,
            "team_id": team_id,
            "app_context": app_context.value,
            "agent_type": agent_type,
            "query": query,
            "response": response,
            "feedback": feedback,
            "privacy": privacy.value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine buffer key
        isolation = ModelIsolationStrategy._determine_isolation(
            atlas_tier or AtlasTier.PERSONAL,
            privacy,
            app_context,
            delt_tier
        )
        
        buffer_key = self._get_buffer_key(
            user_id, org_id, team_id, app_context, agent_type, isolation["level"]
        )
        
        # Add to buffer
        self.interaction_buffers[buffer_key].append(interaction)
        
        # Update RAG chatbot if user has one
        if user_id in self.user_rag_chatbots:
            await self._update_rag_knowledge(user_id, interaction)
        
        # Check if ready to train
        if len(self.interaction_buffers[buffer_key]) >= self.min_interactions:
            await self._check_and_trigger_training(
                buffer_key, user_id, org_id, team_id, app_context,
                agent_type, privacy, atlas_tier, delt_tier
            )
    
    async def _update_rag_knowledge(
        self,
        user_id: str,
        interaction: Dict
    ):
        """Update RAG chatbot with new interaction"""
        
        chatbot_id = self.user_rag_chatbots.get(user_id)
        if not chatbot_id:
            return
        
        # Format interaction as document
        document = f"""
        Query: {interaction['query']}
        Response: {interaction['response']}
        Timestamp: {interaction['timestamp']}
        """
        
        await self.theta.update_rag_knowledge(
            chatbot_id=chatbot_id,
            new_documents=[document]
        )
    
    # ========================================================================
    # Training with Theta Infrastructure
    # ========================================================================
    
    async def _check_and_trigger_training(
        self,
        buffer_key: str,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        privacy: PrivacySchema,
        atlas_tier: Optional[AtlasTier],
        delt_tier: Optional[DeltTier]
    ):
        """Check if training should be triggered"""
        
        # Check time interval
        last_train = self.last_training.get(buffer_key)
        if last_train and (datetime.now() - last_train) < self.training_interval:
            return
        
        # Check if already training
        if buffer_key in self.active_jobs:
            return
        
        # Trigger training
        await self.trigger_training(
            user_id, org_id, team_id, app_context, agent_type,
            privacy, atlas_tier, delt_tier
        )
    
    async def trigger_training(
        self,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        privacy: PrivacySchema,
        atlas_tier: Optional[AtlasTier] = None,
        delt_tier: Optional[DeltTier] = None
    ) -> Dict[str, Any]:
        """
        Trigger training using Theta infrastructure
        
        Improvements:
        - Uses persistent volume (no Filecoin download)
        - Deploys model as API (no manual serving)
        - Supports GPU clusters
        """
        
        isolation = ModelIsolationStrategy._determine_isolation(
            atlas_tier or AtlasTier.PERSONAL,
            privacy,
            app_context,
            delt_tier
        )
        
        buffer_key = self._get_buffer_key(
            user_id, org_id, team_id, app_context, agent_type, isolation["level"]
        )
        
        interactions = self.interaction_buffers.get(buffer_key, [])
        
        logger.info(f"🎓 Triggering Theta training for {buffer_key}")
        logger.info(f"  Interactions: {len(interactions)}")
        
        # Get or create user's volume
        volume_id = self.user_volumes.get(user_id)
        if not volume_id:
            resources = await self.initialize_user(user_id)
            volume_id = resources["volume_id"]
        
        # Write training data to persistent volume
        training_data_path = f"/volumes/{volume_id}/training/{agent_type}/"
        await self._write_training_data_to_volume(
            volume_id,
            training_data_path,
            interactions
        )
        
        # Determine if should use GPU cluster
        num_gpus = 1
        if atlas_tier == AtlasTier.ENTERPRISE or delt_tier == DeltTier.INSTITUTIONAL:
            num_gpus = 4  # Use cluster for enterprise
        
        # Submit training job
        job_id = await self.theta.create_training_job(
            model_id=f"{app_context.value}:{agent_type}:{user_id}",
            base_model="mistral-7b-instruct-v0.2",
            training_data_path=training_data_path,
            hyperparameters={
                "epochs": 3,
                "learning_rate": 2e-5,
                "batch_size": 4
            },
            instance_type="A100-40GB" if num_gpus > 1 else "A100-40GB",
            num_gpus=num_gpus
        )
        
        logger.info(f"  ✅ Training job submitted: {job_id}")
        logger.info(f"  🎮 GPUs: {num_gpus}")
        
        # Track job
        self.active_jobs[buffer_key] = {
            "job_id": job_id,
            "started_at": datetime.now(),
            "user_id": user_id,
            "volume_id": volume_id
        }
        
        # Clear buffer
        self.interaction_buffers[buffer_key] = []
        self.last_training[buffer_key] = datetime.now()
        
        # Wait for completion and deploy (async)
        import asyncio
        asyncio.create_task(self._complete_training(buffer_key, job_id, user_id, agent_type))
        
        return {
            "job_id": job_id,
            "num_gpus": num_gpus,
            "estimated_time_hours": 2.0 / num_gpus  # Faster with more GPUs
        }
    
    async def _complete_training(
        self,
        buffer_key: str,
        job_id: str,
        user_id: str,
        agent_type: str
    ):
        """Complete training and deploy model as API"""
        
        try:
            # Wait for training
            result = await self.theta.wait_for_training(job_id)
            
            logger.info(f"✅ Training completed for {buffer_key}")
            
            # Deploy model as API
            model_path = result["output_path"]
            api_endpoint = await self.theta.deploy_model_api(
                model_id=f"apollo_{user_id}_{agent_type}",
                model_path=model_path,
                instance_type="T4",  # Cheaper for inference
                auto_scaling={
                    "min_instances": 1,
                    "max_instances": 10,
                    "target_qps": 100
                }
            )
            
            # Store API endpoint
            self.user_model_apis[f"{user_id}_{agent_type}"] = api_endpoint
            
            logger.info(f"🚀 Model deployed as API: {api_endpoint}")
            
            # Remove from active jobs
            del self.active_jobs[buffer_key]
            
        except Exception as e:
            logger.error(f"❌ Training failed for {buffer_key}: {e}")
            del self.active_jobs[buffer_key]
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _get_buffer_key(
        self,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        isolation_level: str
    ) -> str:
        """Generate buffer key"""
        
        if isolation_level == "personal":
            return f"{app_context.value}:{agent_type}:{user_id}"
        elif isolation_level == "team":
            return f"{app_context.value}:{agent_type}:{org_id}:team:{team_id}"
        elif isolation_level == "org":
            return f"{app_context.value}:{agent_type}:{org_id}:org"
        else:
            return f"{app_context.value}:{agent_type}:public"
    
    async def _write_training_data_to_volume(
        self,
        volume_id: str,
        path: str,
        interactions: List[Dict]
    ):
        """Write training data to persistent volume"""
        
        import json
        
        # Format as JSONL
        data = "\n".join([json.dumps(i) for i in interactions])
        
        await self.theta.write_to_volume(
            volume_id=volume_id,
            path=f"{path}/training_data.jsonl",
            data=data.encode('utf-8')
        )
    
    # ========================================================================
    # Query Methods (Use RAG + Model APIs)
    # ========================================================================
    
    async def query_with_rag(
        self,
        user_id: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Query user's RAG chatbot
        
        This provides context from user's knowledge base
        """
        
        chatbot_id = self.user_rag_chatbots.get(user_id)
        if not chatbot_id:
            return {"error": "No RAG chatbot for user"}
        
        return await self.theta.query_rag(
            chatbot_id=chatbot_id,
            query=query,
            include_sources=True
        )
    
    async def query_model_api(
        self,
        user_id: str,
        agent_type: str,
        prompt: str
    ) -> str:
        """
        Query user's deployed model API
        
        No need to download model!
        """
        
        api_endpoint = self.user_model_apis.get(f"{user_id}_{agent_type}")
        if not api_endpoint:
            return "Model not deployed yet"
        
        return await self.theta.query_model_api(
            api_endpoint=api_endpoint,
            prompt=prompt
        )
