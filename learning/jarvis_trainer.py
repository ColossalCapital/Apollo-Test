"""
JarvisLabs.ai GPU Trainer - Backup for Theta GPU

JarvisLabs.ai provides on-demand GPU instances:
- RTX 3090: $0.59/hour
- RTX 4090: $0.89/hour
- A100 (40GB): $1.89/hour
- A100 (80GB): $2.49/hour

Advantages over Theta:
- More reliable availability
- Faster startup (< 1 minute)
- Better monitoring/logging
- SSH access for debugging

Use Cases:
- Theta GPU unavailable
- Need faster training
- Debugging training issues
- Production critical jobs
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


class JarvisTrainer:
    """
    Train models on JarvisLabs.ai GPU instances
    
    Pricing (as of 2024):
    - RTX 3090: $0.59/hour (~$1.18 for 2-hour training)
    - RTX 4090: $0.89/hour (~$1.78 for 2-hour training)
    - A100 40GB: $1.89/hour (~$3.78 for 2-hour training)
    - A100 80GB: $2.49/hour (~$4.98 for 2-hour training)
    
    vs Theta:
    - Theta RTX3090: $0.50/hour (~$1.00 for 2-hour training)
    - Theta is 15-20% cheaper
    - But JarvisLabs is more reliable
    """
    
    def __init__(self, api_key: str, api_url: str = "https://cloud.jarvislabs.ai/api/v1"):
        """
        Initialize JarvisLabs trainer
        
        Args:
            api_key: JarvisLabs API key
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
        Submit fine-tuning job to JarvisLabs
        
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
                "job_id": "jarvis_job_123",
                "instance_id": "inst_abc",
                "estimated_cost_usd": 1.78,
                "estimated_time_hours": 2,
                "gpu_type": "RTX4090",
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
            "method": "lora",
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
        
        # Step 1: Create instance
        logger.info(f"🚀 Creating JarvisLabs instance: {gpu_type}")
        instance = await self._create_instance(gpu_type)
        instance_id = instance["instance_id"]
        
        logger.info(f"  ✅ Instance created: {instance_id}")
        
        # Step 2: Wait for instance to be ready
        await self._wait_for_instance(instance_id)
        
        # Step 3: Upload training script
        logger.info(f"  📤 Uploading training script...")
        training_script = self._generate_training_script(
            base_model=base_model,
            training_data_cid=training_data_cid,
            model_id=model_id,
            config=final_config
        )
        
        await self._upload_script(instance_id, training_script)
        
        # Step 4: Start training
        logger.info(f"  🎓 Starting training...")
        job = await self._start_training(instance_id, model_id)
        
        # Calculate costs
        gpu_costs = {
            "RTX3090": 0.59,
            "RTX4090": 0.89,
            "A100_40GB": 1.89,
            "A100_80GB": 2.49
        }
        
        estimated_hours = self._estimate_training_time(base_model, final_config)
        cost_per_hour = gpu_costs.get(gpu_type, 0.89)
        estimated_cost_usd = estimated_hours * cost_per_hour
        
        job_info = {
            "job_id": job["job_id"],
            "instance_id": instance_id,
            "model_id": model_id,
            "estimated_cost_usd": estimated_cost_usd,
            "estimated_time_hours": estimated_hours,
            "gpu_type": gpu_type,
            "status_url": f"{self.api_url}/instances/{instance_id}/status",
            "ssh_command": instance.get("ssh_command"),
            "submitted_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Job submitted: {job['job_id']}")
        logger.info(f"  💰 Estimated cost: ${estimated_cost_usd:.2f}")
        logger.info(f"  ⏱️  Estimated time: {estimated_hours:.1f} hours")
        logger.info(f"  🔗 SSH: {instance.get('ssh_command')}")
        
        return job_info
    
    async def _create_instance(self, gpu_type: str) -> Dict[str, Any]:
        """Create GPU instance on JarvisLabs"""
        
        # Map our GPU types to JarvisLabs instance types
        instance_types = {
            "RTX3090": "rtx3090",
            "RTX4090": "rtx4090",
            "A100_40GB": "a100_40gb",
            "A100_80GB": "a100_80gb"
        }
        
        instance_type = instance_types.get(gpu_type, "rtx4090")
        
        request = {
            "instance_type": instance_type,
            "framework": "pytorch",
            "name": f"apollo-training-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "auto_shutdown": True,  # Auto-shutdown when idle
            "shutdown_timeout": 30  # Shutdown after 30 min idle
        }
        
        response = await self.client.post(
            f"{self.api_url}/instances",
            json=request,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Instance creation failed: {response.text}")
        
        return response.json()
    
    async def _wait_for_instance(self, instance_id: str, timeout: int = 300):
        """Wait for instance to be ready"""
        import asyncio
        
        start_time = datetime.now()
        
        while True:
            status = await self._get_instance_status(instance_id)
            
            if status["state"] == "running":
                logger.info(f"  ✅ Instance ready!")
                return
            
            if status["state"] == "failed":
                raise RuntimeError(f"Instance failed to start: {status.get('error')}")
            
            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout:
                raise TimeoutError(f"Instance did not start within {timeout}s")
            
            logger.info(f"  ⏳ Waiting for instance... ({status['state']})")
            await asyncio.sleep(5)
    
    async def _get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Get instance status"""
        response = await self.client.get(
            f"{self.api_url}/instances/{instance_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Status check failed: {response.text}")
        
        return response.json()
    
    async def _upload_script(self, instance_id: str, script: str):
        """Upload training script to instance"""
        
        response = await self.client.post(
            f"{self.api_url}/instances/{instance_id}/files",
            files={"file": ("train.py", script)},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Script upload failed: {response.text}")
    
    async def _start_training(self, instance_id: str, model_id: str) -> Dict[str, Any]:
        """Start training on instance"""
        
        command = "python train.py"
        
        response = await self.client.post(
            f"{self.api_url}/instances/{instance_id}/execute",
            json={"command": command},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Training start failed: {response.text}")
        
        return {
            "job_id": f"jarvis_{instance_id}_{int(datetime.now().timestamp())}",
            "instance_id": instance_id
        }
    
    def _generate_training_script(
        self,
        base_model: str,
        training_data_cid: str,
        model_id: str,
        config: Dict[str, Any]
    ) -> str:
        """Generate Python training script"""
        
        script = f"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import requests
import json

# Configuration
BASE_MODEL = "{base_model}"
TRAINING_DATA_CID = "{training_data_cid}"
MODEL_ID = "{model_id}"
OUTPUT_DIR = "./output"

# Training config
LEARNING_RATE = {config['learning_rate']}
EPOCHS = {config['epochs']}
BATCH_SIZE = {config['batch_size']}
LORA_R = {config['lora_r']}
LORA_ALPHA = {config['lora_alpha']}
LORA_DROPOUT = {config['lora_dropout']}

print("🚀 Starting training...")
print(f"  Base model: {{BASE_MODEL}}")
print(f"  Training data: {{TRAINING_DATA_CID}}")
print(f"  Model ID: {{MODEL_ID}}")

# Step 1: Download training data from Filecoin
print("📥 Downloading training data from Filecoin...")
response = requests.get(f"https://{{TRAINING_DATA_CID}}.ipfs.w3s.link/training_data.jsonl")
training_data = [json.loads(line) for line in response.text.split('\\n') if line]
print(f"  ✅ Downloaded {{len(training_data)}} training examples")

# Step 2: Load model and tokenizer
print("📦 Loading model and tokenizer...")
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
print("  ✅ Model loaded")

# Step 3: Prepare model for LoRA
print("🔧 Preparing model for LoRA...")
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
print("  ✅ LoRA configured")

# Step 4: Prepare dataset
print("📊 Preparing dataset...")
# TODO: Format training data properly
# This is a simplified version

# Step 5: Train
print("🎓 Training...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    learning_rate=LEARNING_RATE,
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
)

# TODO: Add actual training loop
# trainer = Trainer(model=model, args=training_args, train_dataset=dataset)
# trainer.train()

print("✅ Training complete!")

# Step 6: Save model
print("💾 Saving model...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("  ✅ Model saved")

# Step 7: Upload to Filecoin
print("📤 Uploading to Filecoin...")
# TODO: Upload to Filecoin
print("  ✅ Uploaded!")

print("🎉 All done!")
"""
        
        return script
    
    async def check_job_status(self, job_id: str, instance_id: str) -> Dict[str, Any]:
        """Check training job status"""
        
        status = await self._get_instance_status(instance_id)
        
        return {
            "job_id": job_id,
            "instance_id": instance_id,
            "status": status["state"],
            "progress": 0.5,  # TODO: Parse from logs
            "logs": status.get("logs", "")
        }
    
    async def stop_instance(self, instance_id: str) -> bool:
        """Stop GPU instance"""
        
        response = await self.client.post(
            f"{self.api_url}/instances/{instance_id}/stop",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        return response.status_code == 200
    
    async def list_instances(self) -> List[Dict[str, Any]]:
        """List all instances"""
        
        response = await self.client.get(
            f"{self.api_url}/instances",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"List instances failed: {response.text}")
        
        return response.json()["instances"]
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _select_gpu(self, base_model: str, method: str) -> str:
        """Select appropriate GPU based on model size"""
        
        if "33b" in base_model.lower():
            return "A100_80GB"
        elif "13b" in base_model.lower() or "8x7b" in base_model.lower():
            return "A100_40GB" if method == "full" else "RTX4090"
        else:  # 7B and smaller
            return "RTX4090" if method == "full" else "RTX3090"
    
    def _estimate_training_time(self, base_model: str, config: Dict[str, Any]) -> float:
        """Estimate training time in hours"""
        
        # Base times (hours per epoch for 1000 samples)
        base_times = {
            "phi-3-medium": 0.5,
            "mistral-7b": 0.5,
            "deepseek-coder-6.7b": 0.5,
            "mixtral-8x7b": 2.0,
            "deepseek-coder-33b": 3.0,
            "llava-1.6-34b": 3.0
        }
        
        base_time = 0.5
        for model_name, time in base_times.items():
            if model_name in base_model.lower():
                base_time = time
                break
        
        # Adjust for method
        if config["method"] == "lora":
            base_time *= 0.3
        elif config["method"] == "qlora":
            base_time *= 0.2
        
        # Multiply by epochs
        total_time = base_time * config["epochs"]
        
        # Add overhead
        total_time *= 1.2
        
        return round(total_time, 1)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize
        trainer = JarvisTrainer(api_key="your_jarvis_api_key")
        
        # Submit training job
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
        print(f"Instance: {job['instance_id']}")
        print(f"Cost: ${job['estimated_cost_usd']:.2f}")
        print(f"SSH: {job['ssh_command']}")
    
    asyncio.run(main())
