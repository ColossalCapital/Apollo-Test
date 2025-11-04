"""
Theta GPU Trainer - Decentralized GPU training on Theta EdgeCloud

Benefits:
- 20x cheaper than AWS ($1 vs $20 per training job)
- Decentralized (no vendor lock-in)
- Pay with TFUEL tokens
- GPU options: RTX3090, RTX4090, A100

Training Methods:
- Full fine-tuning (expensive, best quality)
- LoRA (cheap, good quality)
- QLoRA (cheapest, decent quality)
"""

import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from config.model_config import (
    AppContext, PrivacySchema, AtlasTier, DeltTier,
    ModelIsolationStrategy, AGENT_MODELS
)

logger = logging.getLogger(__name__)


class ThetaTrainer:
    """
    Train models on Theta EdgeCloud
    
    Theta EdgeCloud provides decentralized GPU compute:
    - RTX3090: $0.50/hour (~$1 for 2-hour training)
    - RTX4090: $0.75/hour (~$1.50 for 2-hour training)
    - A100: $2.00/hour (~$4 for 2-hour training)
    
    vs AWS:
    - p3.2xlarge (V100): $3.06/hour (~$6 for 2-hour training)
    - p4d.24xlarge (A100): $32.77/hour (~$65 for 2-hour training)
    """
    
    def __init__(self, api_key: str, api_url: str = "https://api.thetaedgecloud.com/v1"):
        """
        Initialize Theta trainer
        
        Args:
            api_key: Theta EdgeCloud API key
            api_url: API endpoint
        """
        self.api_key = api_key
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def submit_training_job(
        self,
        user_id: str,
        org_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        base_model: str,
        training_data_cid: str,
        privacy: PrivacySchema,
        atlas_tier: Optional[AtlasTier] = None,
        delt_tier: Optional[DeltTier] = None,
        training_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit fine-tuning job to Theta EdgeCloud
        
        Args:
            user_id: User ID
            org_id: Organization ID (if applicable)
            app_context: Atlas, Delt, or Akashic
            agent_type: Type of agent (finance, communication, etc.)
            base_model: Base model to fine-tune
            training_data_cid: Filecoin CID of training data
            privacy: Privacy level
            atlas_tier: Atlas subscription tier
            delt_tier: Delt subscription tier
            training_config: Custom training configuration
        
        Returns:
            {
                "job_id": "theta_job_123",
                "estimated_cost_tfuel": 0.5,
                "estimated_cost_usd": 0.50,
                "estimated_time_hours": 2,
                "gpu_type": "RTX3090",
                "status_url": "https://..."
            }
        """
        
        # Get model configuration
        model_config = AGENT_MODELS.get(agent_type, AGENT_MODELS["default"])
        
        # Determine isolation level
        isolation = ModelIsolationStrategy._determine_isolation(
            atlas_tier or AtlasTier.PERSONAL,
            privacy,
            app_context,
            delt_tier
        )
        
        # Build model ID
        model_id = ModelIsolationStrategy._build_model_id(
            user_id, org_id, isolation, app_context, agent_type
        )
        
        # Default training config
        default_config = {
            "method": "lora",  # LoRA is cheapest and fastest
            "learning_rate": 2e-5,
            "epochs": 3,
            "batch_size": 4,
            "lora_r": 8,
            "lora_alpha": 16,
            "lora_dropout": 0.05,
            "max_seq_length": model_config["context_size"],
            "warmup_steps": 100
        }
        
        # Merge with custom config
        final_config = {**default_config, **(training_config or {})}
        
        # Select GPU based on model size
        gpu_type = self._select_gpu(base_model, final_config["method"])
        
        # Build job request
        job_request = {
            "job_type": "fine_tune",
            "model_id": model_id,
            "base_model": base_model,
            "training_data": {
                "source": "filecoin",
                "cid": training_data_cid
            },
            "training_config": final_config,
            "gpu": {
                "type": gpu_type,
                "count": 1
            },
            "output": {
                "destination": "filecoin",
                "privacy": privacy.value,
                "isolation": isolation["level"]
            },
            "metadata": {
                "user_id": user_id,
                "org_id": org_id,
                "app_context": app_context.value,
                "agent_type": agent_type,
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Submit job
        logger.info(f"🚀 Submitting training job: {model_id}")
        logger.info(f"  Base model: {base_model}")
        logger.info(f"  GPU: {gpu_type}")
        logger.info(f"  Method: {final_config['method']}")
        
        response = await self.client.post(
            f"{self.api_url}/jobs/submit",
            json=job_request,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Job submission failed: {response.text}")
        
        result = response.json()
        
        # Calculate costs
        gpu_costs = {
            "RTX3090": 0.50,
            "RTX4090": 0.75,
            "A100": 2.00
        }
        
        estimated_hours = self._estimate_training_time(base_model, final_config)
        cost_per_hour = gpu_costs.get(gpu_type, 0.50)
        estimated_cost_usd = estimated_hours * cost_per_hour
        estimated_cost_tfuel = estimated_cost_usd / 1.0  # Assume 1 TFUEL = $1
        
        job_info = {
            "job_id": result["job_id"],
            "model_id": model_id,
            "estimated_cost_tfuel": estimated_cost_tfuel,
            "estimated_cost_usd": estimated_cost_usd,
            "estimated_time_hours": estimated_hours,
            "gpu_type": gpu_type,
            "status_url": f"{self.api_url}/jobs/{result['job_id']}/status",
            "submitted_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Job submitted: {result['job_id']}")
        logger.info(f"  💰 Estimated cost: {estimated_cost_tfuel:.2f} TFUEL (${estimated_cost_usd:.2f})")
        logger.info(f"  ⏱️  Estimated time: {estimated_hours:.1f} hours")
        
        return job_info
    
    async def check_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check training job status
        
        Returns:
            {
                "job_id": "theta_job_123",
                "status": "pending" | "running" | "completed" | "failed",
                "progress": 0.75,
                "current_epoch": 2,
                "total_epochs": 3,
                "loss": 0.05,
                "output_cid": "Qm..." (if completed),
                "error": "..." (if failed)
            }
        """
        
        response = await self.client.get(
            f"{self.api_url}/jobs/{job_id}/status",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Status check failed: {response.text}")
        
        return response.json()
    
    async def get_trained_model(self, job_id: str) -> str:
        """
        Get Filecoin CID of trained model
        
        Args:
            job_id: Training job ID
        
        Returns:
            Filecoin CID of trained model
        """
        
        status = await self.check_job_status(job_id)
        
        if status["status"] != "completed":
            raise RuntimeError(f"Job not complete: {status['status']}")
        
        return status["output_cid"]
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel running training job
        
        Returns:
            True if cancelled successfully
        """
        
        response = await self.client.post(
            f"{self.api_url}/jobs/{job_id}/cancel",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        return response.status_code == 200
    
    async def list_jobs(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List training jobs
        
        Args:
            user_id: Filter by user ID
            status: Filter by status
        
        Returns:
            List of job info
        """
        
        params = {}
        if user_id:
            params["user_id"] = user_id
        if status:
            params["status"] = status
        
        response = await self.client.get(
            f"{self.api_url}/jobs",
            params=params,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"List jobs failed: {response.text}")
        
        return response.json()["jobs"]
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _select_gpu(self, base_model: str, method: str) -> str:
        """
        Select appropriate GPU based on model size and training method
        
        Rules:
        - Small models (<7B) + LoRA → RTX3090
        - Medium models (7-13B) + LoRA → RTX4090
        - Large models (>13B) or full fine-tuning → A100
        """
        
        # Extract model size from name
        if "33b" in base_model.lower():
            return "A100"
        elif "13b" in base_model.lower() or "8x7b" in base_model.lower():
            return "RTX4090" if method == "lora" else "A100"
        else:  # 7B and smaller
            return "RTX3090" if method == "lora" else "RTX4090"
    
    def _estimate_training_time(self, base_model: str, config: Dict[str, Any]) -> float:
        """
        Estimate training time in hours
        
        Factors:
        - Model size
        - Training method (LoRA is 3x faster than full)
        - Number of epochs
        - Batch size
        """
        
        # Base times (hours per epoch for 1000 samples)
        base_times = {
            "phi-3-medium": 0.5,
            "mistral-7b": 0.5,
            "deepseek-coder-6.7b": 0.5,
            "mixtral-8x7b": 2.0,
            "deepseek-coder-33b": 3.0,
            "llava-1.6-34b": 3.0
        }
        
        # Get base time
        base_time = 0.5
        for model_name, time in base_times.items():
            if model_name in base_model.lower():
                base_time = time
                break
        
        # Adjust for method
        if config["method"] == "lora":
            base_time *= 0.3  # LoRA is 3x faster
        elif config["method"] == "qlora":
            base_time *= 0.2  # QLoRA is 5x faster
        
        # Multiply by epochs
        total_time = base_time * config["epochs"]
        
        # Add overhead (setup, validation, etc.)
        total_time *= 1.2
        
        return round(total_time, 1)
    
    # ========================================================================
    # Advanced Training Methods
    # ========================================================================
    
    async def submit_multi_agent_training(
        self,
        user_id: str,
        org_id: Optional[str],
        app_context: AppContext,
        agent_types: List[str],
        training_data_cids: Dict[str, str],
        privacy: PrivacySchema,
        atlas_tier: Optional[AtlasTier] = None,
        delt_tier: Optional[DeltTier] = None
    ) -> List[Dict[str, Any]]:
        """
        Train multiple agents in parallel
        
        Args:
            agent_types: List of agent types to train
            training_data_cids: Dict mapping agent_type to CID
        
        Returns:
            List of job info for each agent
        """
        
        jobs = []
        
        for agent_type in agent_types:
            if agent_type not in training_data_cids:
                logger.warning(f"No training data for {agent_type}, skipping")
                continue
            
            # Get base model for this agent type
            model_config = AGENT_MODELS.get(agent_type, AGENT_MODELS["default"])
            base_model = model_config["base_model"]
            
            # Submit job
            job = await self.submit_training_job(
                user_id=user_id,
                org_id=org_id,
                app_context=app_context,
                agent_type=agent_type,
                base_model=base_model,
                training_data_cid=training_data_cids[agent_type],
                privacy=privacy,
                atlas_tier=atlas_tier,
                delt_tier=delt_tier
            )
            
            jobs.append(job)
        
        logger.info(f"✅ Submitted {len(jobs)} training jobs")
        return jobs
    
    async def wait_for_completion(
        self,
        job_ids: List[str],
        check_interval: int = 60
    ) -> Dict[str, Dict[str, Any]]:
        """
        Wait for multiple jobs to complete
        
        Args:
            job_ids: List of job IDs to monitor
            check_interval: Seconds between status checks
        
        Returns:
            Dict mapping job_id to final status
        """
        
        import asyncio
        
        results = {}
        pending = set(job_ids)
        
        while pending:
            for job_id in list(pending):
                status = await self.check_job_status(job_id)
                
                if status["status"] in ["completed", "failed"]:
                    results[job_id] = status
                    pending.remove(job_id)
                    
                    if status["status"] == "completed":
                        logger.info(f"✅ Job {job_id} completed")
                    else:
                        logger.error(f"❌ Job {job_id} failed: {status.get('error')}")
                else:
                    logger.info(f"⏳ Job {job_id}: {status['status']} ({status.get('progress', 0)*100:.0f}%)")
            
            if pending:
                await asyncio.sleep(check_interval)
        
        return results


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize
        trainer = ThetaTrainer(api_key="your_theta_api_key")
        
        # Example 1: Train single agent
        job = await trainer.submit_training_job(
            user_id="user123",
            org_id=None,
            app_context=AppContext.ATLAS,
            agent_type="finance",
            base_model="deepseek-coder-6.7b",
            training_data_cid="QmXXX...",
            privacy=PrivacySchema.PERSONAL,
            atlas_tier=AtlasTier.PERSONAL
        )
        
        print(f"Job submitted: {job['job_id']}")
        print(f"Cost: ${job['estimated_cost_usd']:.2f}")
        print(f"Time: {job['estimated_time_hours']:.1f} hours")
        
        # Example 2: Train multiple agents
        jobs = await trainer.submit_multi_agent_training(
            user_id="user123",
            org_id=None,
            app_context=AppContext.DELT,
            agent_types=["finance", "trading", "portfolio"],
            training_data_cids={
                "finance": "QmAAA...",
                "trading": "QmBBB...",
                "portfolio": "QmCCC..."
            },
            privacy=PrivacySchema.PERSONAL,
            delt_tier=DeltTier.INDIVIDUAL
        )
        
        print(f"Submitted {len(jobs)} jobs")
        
        # Wait for completion
        results = await trainer.wait_for_completion([j["job_id"] for j in jobs])
        print(f"All jobs complete: {len(results)}")
    
    asyncio.run(main())
