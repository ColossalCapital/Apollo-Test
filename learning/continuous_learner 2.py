"""
Continuous Learning System - Tier 3 Intelligence

Automatically learns from user interactions and fine-tunes models:
1. Logs user interactions
2. Collects feedback
3. Uploads training data to Filecoin (with privacy isolation)
4. Triggers training on Theta GPU
5. Deploys personalized models

Privacy-aware:
- Personal data → Personal models only
- Team data → Team models
- Org data → Org models
- Respects Atlas/Delt tiers
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from config.model_config import (
    AppContext, PrivacySchema, AtlasTier, DeltTier,
    TrainingDataIsolation, ModelIsolationStrategy
)
from storage.isolated_storage import IsolatedStorageManager
from .unified_trainer import UnifiedTrainer, GPUProvider

logger = logging.getLogger(__name__)


class ContinuousLearner:
    """
    Manages continuous learning for all agents with privacy isolation
    
    Features:
    - Automatic interaction logging
    - Privacy-aware data collection
    - Scheduled training jobs
    - Model versioning
    - A/B testing of models
    """
    
    def __init__(
        self,
        storage_manager: IsolatedStorageManager,
        gpu_trainer: UnifiedTrainer,
        min_interactions: int = 100,
        training_interval_days: int = 7
    ):
        """
        Initialize continuous learner
        
        Args:
            storage_manager: Isolated storage manager
            gpu_trainer: Unified GPU trainer (Theta + JarvisLabs)
            min_interactions: Minimum interactions before training
            training_interval_days: Days between training runs
        """
        self.storage = storage_manager
        self.trainer = gpu_trainer
        self.min_interactions = min_interactions
        self.training_interval = timedelta(days=training_interval_days)
        
        # In-memory buffers (would be Redis in production)
        self.interaction_buffers = defaultdict(list)
        self.last_training = {}
        self.active_jobs = {}
    
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
        Log user interaction for training
        
        Args:
            user_id: User ID
            org_id: Organization ID
            team_id: Team ID
            app_context: Atlas, Delt, or Akashic
            agent_type: Type of agent
            query: User's query
            response: Agent's response
            feedback: User rating (0.0-1.0)
            privacy: Privacy level
            atlas_tier: Atlas tier
            delt_tier: Delt tier
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
        
        # Determine buffer key based on isolation level
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
        
        logger.debug(f"📝 Logged interaction: {buffer_key} ({len(self.interaction_buffers[buffer_key])} total)")
        
        # Check if ready to train
        if len(self.interaction_buffers[buffer_key]) >= self.min_interactions:
            await self._check_and_trigger_training(
                buffer_key, user_id, org_id, team_id, app_context,
                agent_type, privacy, atlas_tier, delt_tier
            )
    
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
        
        # Check if enough time has passed since last training
        last_train = self.last_training.get(buffer_key)
        if last_train and (datetime.now() - last_train) < self.training_interval:
            logger.debug(f"⏳ Too soon to train {buffer_key}, waiting...")
            return
        
        # Check if training already in progress
        if buffer_key in self.active_jobs:
            logger.debug(f"⏳ Training already in progress for {buffer_key}")
            return
        
        # Trigger training
        await self.trigger_training(
            user_id, org_id, team_id, app_context, agent_type,
            privacy, atlas_tier, delt_tier
        )
    
    # ========================================================================
    # Training Orchestration
    # ========================================================================
    
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
        Trigger model fine-tuning
        
        Returns:
            Training job info
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
        
        if len(interactions) < self.min_interactions:
            logger.warning(f"Not enough interactions for {buffer_key}: {len(interactions)}/{self.min_interactions}")
            return {"error": "Not enough interactions"}
        
        logger.info(f"🎓 Triggering training for {buffer_key}")
        logger.info(f"  Interactions: {len(interactions)}")
        logger.info(f"  Privacy: {privacy.value}")
        logger.info(f"  Isolation: {isolation['level']}")
        
        # Step 1: Upload training data to Filecoin
        logger.info(f"  📤 Uploading training data to Filecoin...")
        storage_result = await self.storage.store_training_data(
            user_id=user_id,
            org_id=org_id,
            team_id=team_id,
            app_context=app_context,
            agent_type=agent_type,
            interactions=interactions,
            privacy=privacy,
            atlas_tier=atlas_tier,
            delt_tier=delt_tier
        )
        
        training_data_cid = storage_result["cid"]
        logger.info(f"  ✅ Training data uploaded: {training_data_cid}")
        
        # Step 2: Submit training job to Theta GPU
        logger.info(f"  🚀 Submitting training job to Theta GPU...")
        
        from config.model_config import AGENT_MODELS
        model_config = AGENT_MODELS.get(agent_type, AGENT_MODELS["default"])
        base_model = model_config["base_model"]
        
        job = await self.trainer.submit_training_job(
            user_id=user_id,
            org_id=org_id,
            app_context=app_context,
            agent_type=agent_type,
            base_model=base_model,
            training_data_cid=training_data_cid,
            privacy=privacy,
            atlas_tier=atlas_tier,
            delt_tier=delt_tier
        )
        
        logger.info(f"  ✅ Training job submitted: {job['job_id']}")
        logger.info(f"  💰 Cost: {job['estimated_cost_tfuel']:.2f} TFUEL (${job['estimated_cost_usd']:.2f})")
        logger.info(f"  ⏱️  Time: ~{job['estimated_time_hours']:.1f} hours")
        
        # Step 3: Track job
        self.active_jobs[buffer_key] = {
            "job_id": job["job_id"],
            "started_at": datetime.now(),
            "user_id": user_id,
            "org_id": org_id,
            "team_id": team_id,
            "app_context": app_context,
            "agent_type": agent_type,
            "privacy": privacy,
            "training_data_cid": training_data_cid
        }
        
        # Step 4: Clear buffer
        self.interaction_buffers[buffer_key] = []
        self.last_training[buffer_key] = datetime.now()
        
        # Step 5: Start monitoring (async)
        asyncio.create_task(self._monitor_training_job(buffer_key, job["job_id"]))
        
        return job
    
    async def _monitor_training_job(self, buffer_key: str, job_id: str):
        """Monitor training job and deploy model when complete"""
        
        logger.info(f"👀 Monitoring job {job_id} for {buffer_key}")
        
        while True:
            try:
                # Check status
                status = await self.trainer.check_job_status(job_id)
                
                if status["status"] == "completed":
                    logger.info(f"✅ Training complete for {buffer_key}")
                    await self._deploy_trained_model(buffer_key, job_id, status)
                    break
                
                elif status["status"] == "failed":
                    logger.error(f"❌ Training failed for {buffer_key}: {status.get('error')}")
                    del self.active_jobs[buffer_key]
                    break
                
                else:
                    progress = status.get("progress", 0) * 100
                    logger.info(f"⏳ Training {buffer_key}: {status['status']} ({progress:.0f}%)")
                
                # Wait before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error monitoring job {job_id}: {e}")
                await asyncio.sleep(60)
    
    async def _deploy_trained_model(
        self,
        buffer_key: str,
        job_id: str,
        status: Dict[str, Any]
    ):
        """Deploy trained model to storage"""
        
        job_info = self.active_jobs.get(buffer_key)
        if not job_info:
            logger.error(f"Job info not found for {buffer_key}")
            return
        
        try:
            # Get model CID from Theta
            model_cid = status["output_cid"]
            logger.info(f"📦 Model CID: {model_cid}")
            
            # Store model metadata
            await self.storage.store_model(
                user_id=job_info["user_id"],
                org_id=job_info["org_id"],
                team_id=job_info["team_id"],
                app_context=job_info["app_context"],
                agent_type=job_info["agent_type"],
                model_path=f"filecoin://{model_cid}",
                base_model=status.get("base_model", "unknown"),
                privacy=job_info["privacy"],
                training_metadata={
                    "job_id": job_id,
                    "training_data_cid": job_info["training_data_cid"],
                    "final_loss": status.get("loss"),
                    "epochs": status.get("total_epochs"),
                    "completed_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ Model deployed for {buffer_key}")
            
            # Cleanup
            del self.active_jobs[buffer_key]
            
        except Exception as e:
            logger.error(f"Error deploying model for {buffer_key}: {e}")
    
    # ========================================================================
    # Batch Training
    # ========================================================================
    
    async def train_all_ready_agents(
        self,
        user_id: str,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Train all agents that have enough interactions
        
        Returns:
            List of training jobs
        """
        
        jobs = []
        
        for buffer_key, interactions in self.interaction_buffers.items():
            if len(interactions) < self.min_interactions:
                continue
            
            # Parse buffer key
            parts = buffer_key.split(":")
            if len(parts) < 3:
                continue
            
            key_user_id = parts[2] if len(parts) > 2 else None
            if key_user_id != user_id:
                continue
            
            # Extract info from first interaction
            if not interactions:
                continue
            
            first = interactions[0]
            app_context = AppContext(first["app_context"])
            agent_type = first["agent_type"]
            privacy = PrivacySchema(first["privacy"])
            
            # Trigger training
            try:
                job = await self.trigger_training(
                    user_id=user_id,
                    org_id=org_id,
                    team_id=first.get("team_id"),
                    app_context=app_context,
                    agent_type=agent_type,
                    privacy=privacy
                )
                
                if "error" not in job:
                    jobs.append(job)
                    
            except Exception as e:
                logger.error(f"Error training {buffer_key}: {e}")
        
        logger.info(f"✅ Started {len(jobs)} training jobs for user {user_id}")
        return jobs
    
    # ========================================================================
    # Statistics & Monitoring
    # ========================================================================
    
    def get_training_stats(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get training statistics
        
        Returns:
            {
                "total_interactions": 1234,
                "ready_for_training": 3,
                "active_jobs": 2,
                "completed_models": 5,
                "by_agent": {...}
            }
        """
        
        stats = {
            "total_interactions": 0,
            "ready_for_training": 0,
            "active_jobs": len(self.active_jobs),
            "by_agent": defaultdict(int)
        }
        
        for buffer_key, interactions in self.interaction_buffers.items():
            # Filter by user if specified
            if user_id and user_id not in buffer_key:
                continue
            
            count = len(interactions)
            stats["total_interactions"] += count
            
            if count >= self.min_interactions:
                stats["ready_for_training"] += 1
            
            # Extract agent type
            parts = buffer_key.split(":")
            if len(parts) >= 2:
                agent_type = parts[1]
                stats["by_agent"][agent_type] += count
        
        return dict(stats)
    
    def _get_buffer_key(
        self,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        isolation_level: str
    ) -> str:
        """
        Build buffer key based on isolation level
        
        Format:
        - personal: {app}:{agent_type}:{user_id}
        - team: {app}:{agent_type}:{org_id}:team:{team_id}
        - org: {app}:{agent_type}:{org_id}:org
        """
        
        app = app_context.value
        
        if isolation_level == "personal":
            return f"{app}:{agent_type}:{user_id}"
        elif isolation_level == "team":
            return f"{app}:{agent_type}:{org_id}:team:{team_id or 'default'}"
        elif isolation_level == "org":
            return f"{app}:{agent_type}:{org_id}:org"
        elif isolation_level == "public":
            return f"{app}:{agent_type}:public"
        
        return f"{app}:{agent_type}:{user_id}"


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import asyncio
    from storage.filecoin_client import FilecoinClient
    
    async def main():
        # Initialize components
        filecoin = FilecoinClient(api_token="your_token")
        storage = IsolatedStorageManager(filecoin, "your_token")
        trainer = UnifiedTrainer(
            theta_api_key="your_theta_key",
            jarvis_api_key="your_jarvis_key",
            preferred_provider=GPUProvider.AUTO
        )
        learner = ContinuousLearner(storage, trainer, min_interactions=10)
        
        # Example: Log interactions
        for i in range(15):
            await learner.log_interaction(
                user_id="user123",
                org_id=None,
                team_id=None,
                app_context=AppContext.ATLAS,
                agent_type="finance",
                query={"type": "strategy", "asset": "BTC"},
                response={"recommendation": "BUY"},
                feedback=0.9,
                privacy=PrivacySchema.PERSONAL,
                atlas_tier=AtlasTier.PERSONAL
            )
        
        # Check stats
        stats = learner.get_training_stats(user_id="user123")
        print(f"Stats: {stats}")
        
        # Training will trigger automatically after 10 interactions
        await asyncio.sleep(5)
        
        print("✅ Example complete!")
    
    asyncio.run(main())
