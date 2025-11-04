"""
Theta GPU Trainer - Distributed model training on Theta EdgeCloud

Cost: ~$0.10/hour (vs $3.06/hour on AWS)
Earn TFUEL while training!
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ThetaTrainer:
    """Distributed model training on Theta EdgeCloud"""
    
    def __init__(
        self,
        api_key: str,
        api_endpoint: str = "https://api.thetaedgecloud.com/v1"
    ):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def train_model(
        self,
        model_name: str,
        dataset_path: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Train a model on Theta EdgeCloud
        
        Args:
            model_name: Name of the model to train
            dataset_path: Path to training dataset
            config: Training configuration
            
        Returns:
            Training job info
        """
        logger.info(f"🎓 Starting training job for {model_name}")
        
        # 1. Prepare training job
        job = await self.create_training_job(model_name, dataset_path, config)
        job_id = job["job_id"]
        
        logger.info(f"  📋 Job ID: {job_id}")
        logger.info(f"  💰 Estimated cost: ${job['estimated_cost']:.2f}")
        logger.info(f"  ⏱️  Estimated time: {job['estimated_time']} minutes")
        
        # 2. Monitor progress
        while True:
            status = await self.get_job_status(job_id)
            
            if status["state"] == "completed":
                logger.info(f"  ✅ Training complete!")
                break
            elif status["state"] == "failed":
                logger.error(f"  ❌ Training failed: {status['error']}")
                raise RuntimeError(f"Training failed: {status['error']}")
            else:
                progress = status.get("progress", 0)
                logger.info(f"  📊 Progress: {progress}%")
                await asyncio.sleep(60)  # Check every minute
        
        # 3. Download trained model
        model_path = await self.download_model(job_id)
        logger.info(f"  💾 Model downloaded to: {model_path}")
        
        # 4. Get TFUEL rewards
        rewards = await self.get_rewards(job_id)
        logger.info(f"  🎁 Earned {rewards['tfuel']} TFUEL (${rewards['usd_value']:.2f})")
        
        return {
            "job_id": job_id,
            "model_path": model_path,
            "cost": status["actual_cost"],
            "tfuel_earned": rewards["tfuel"],
            "training_time": status["training_time"]
        }
    
    async def create_training_job(
        self,
        model_name: str,
        dataset_path: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a training job on Theta"""
        
        job_config = {
            "model_name": model_name,
            "dataset_path": dataset_path,
            "framework": config.get("framework", "pytorch"),
            "gpu_type": config.get("gpu_type", "RTX3090"),
            "num_gpus": config.get("num_gpus", 1),
            "epochs": config.get("epochs", 10),
            "batch_size": config.get("batch_size", 32),
            "learning_rate": config.get("learning_rate", 0.001),
        }
        
        async with self.session.post(
            f"{self.api_endpoint}/training/jobs",
            json=job_config
        ) as response:
            return await response.json()
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get training job status"""
        async with self.session.get(
            f"{self.api_endpoint}/training/jobs/{job_id}"
        ) as response:
            return await response.json()
    
    async def download_model(self, job_id: str) -> str:
        """Download trained model"""
        async with self.session.get(
            f"{self.api_endpoint}/training/jobs/{job_id}/model"
        ) as response:
            # Download model file
            model_data = await response.read()
            
            # Save to local file
            model_path = f"/models/{job_id}.pth"
            with open(model_path, 'wb') as f:
                f.write(model_data)
            
            return model_path
    
    async def get_rewards(self, job_id: str) -> Dict[str, Any]:
        """Get TFUEL rewards for training job"""
        async with self.session.get(
            f"{self.api_endpoint}/training/jobs/{job_id}/rewards"
        ) as response:
            return await response.json()
    
    async def estimate_cost(
        self,
        gpu_type: str = "RTX3090",
        num_gpus: int = 1,
        hours: float = 1.0
    ) -> Dict[str, Any]:
        """Estimate training cost"""
        
        # Theta pricing (approximate)
        gpu_prices = {
            "RTX3090": 0.10,  # $0.10/hour
            "RTX4090": 0.15,
            "A100": 0.50,
        }
        
        hourly_rate = gpu_prices.get(gpu_type, 0.10) * num_gpus
        total_cost = hourly_rate * hours
        
        # AWS comparison
        aws_cost = 3.06 * hours  # p3.2xlarge
        savings = aws_cost - total_cost
        savings_percent = (savings / aws_cost) * 100
        
        return {
            "theta_cost": total_cost,
            "aws_cost": aws_cost,
            "savings": savings,
            "savings_percent": savings_percent,
            "hourly_rate": hourly_rate
        }


async def example_training():
    """Example training job"""
    
    # Initialize trainer
    async with ThetaTrainer(api_key="your_api_key") as trainer:
        
        # Estimate cost
        estimate = await trainer.estimate_cost(
            gpu_type="RTX3090",
            num_gpus=1,
            hours=10.0
        )
        
        print(f"💰 Cost Estimate:")
        print(f"  Theta: ${estimate['theta_cost']:.2f}")
        print(f"  AWS: ${estimate['aws_cost']:.2f}")
        print(f"  Savings: ${estimate['savings']:.2f} ({estimate['savings_percent']:.1f}%)")
        
        # Train model
        result = await trainer.train_model(
            model_name="custom-email-classifier",
            dataset_path="/data/emails.csv",
            config={
                "framework": "pytorch",
                "gpu_type": "RTX3090",
                "num_gpus": 1,
                "epochs": 10,
                "batch_size": 32,
            }
        )
        
        print(f"\n✅ Training Complete!")
        print(f"  Model: {result['model_path']}")
        print(f"  Cost: ${result['cost']:.2f}")
        print(f"  TFUEL Earned: {result['tfuel_earned']}")
        print(f"  Time: {result['training_time']} minutes")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_training())
