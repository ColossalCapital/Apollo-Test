"""
Unified GPU Trainer - Automatically selects best GPU provider

Priority:
1. Theta GPU (cheapest, $1/job)
2. JarvisLabs.ai (reliable, $1.78/job)

Fallback logic:
- Try Theta first
- If Theta unavailable/slow → JarvisLabs
- If both fail → Error

This ensures:
- Cost optimization (Theta is cheaper)
- Reliability (JarvisLabs as backup)
- Performance (automatic failover)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from .theta_trainer import ThetaTrainer
from .jarvis_trainer import JarvisTrainer
from config.model_config import (
    AppContext, PrivacySchema, AtlasTier, DeltTier
)

logger = logging.getLogger(__name__)


class GPUProvider(Enum):
    """GPU provider options"""
    THETA = "theta"
    JARVIS = "jarvis"
    AUTO = "auto"  # Automatic selection


class UnifiedTrainer:
    """
    Unified trainer that automatically selects best GPU provider
    
    Features:
    - Automatic provider selection
    - Cost optimization
    - Reliability failover
    - Performance monitoring
    """
    
    def __init__(
        self,
        theta_api_key: Optional[str] = None,
        jarvis_api_key: Optional[str] = None,
        preferred_provider: GPUProvider = GPUProvider.AUTO
    ):
        """
        Initialize unified trainer
        
        Args:
            theta_api_key: Theta EdgeCloud API key
            jarvis_api_key: JarvisLabs API key
            preferred_provider: Preferred GPU provider (default: auto)
        """
        self.preferred_provider = preferred_provider
        
        # Initialize providers
        self.theta = ThetaTrainer(theta_api_key) if theta_api_key else None
        self.jarvis = JarvisTrainer(jarvis_api_key) if jarvis_api_key else None
        
        # Track provider performance
        self.provider_stats = {
            "theta": {"success": 0, "failure": 0, "avg_time": 0},
            "jarvis": {"success": 0, "failure": 0, "avg_time": 0}
        }
        
        logger.info("🚀 Unified Trainer initialized")
        logger.info(f"  Theta: {'✅' if self.theta else '❌'}")
        logger.info(f"  JarvisLabs: {'✅' if self.jarvis else '❌'}")
        logger.info(f"  Preferred: {preferred_provider.value}")
    
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
        training_config: Optional[Dict[str, Any]] = None,
        force_provider: Optional[GPUProvider] = None
    ) -> Dict[str, Any]:
        """
        Submit training job to best available provider
        
        Args:
            user_id: User ID
            org_id: Organization ID
            app_context: Atlas, Delt, or Akashic
            agent_type: Agent type
            base_model: Base model
            training_data_cid: Filecoin CID
            privacy: Privacy level
            atlas_tier: Atlas tier
            delt_tier: Delt tier
            training_config: Training configuration
            force_provider: Force specific provider (optional)
        
        Returns:
            Job info with provider details
        """
        
        # Determine which provider to use
        provider = await self._select_provider(force_provider)
        
        logger.info(f"🎯 Selected provider: {provider.value.upper()}")
        
        try:
            if provider == GPUProvider.THETA:
                job = await self._submit_to_theta(
                    user_id, org_id, app_context, agent_type, base_model,
                    training_data_cid, privacy, atlas_tier, delt_tier, training_config
                )
                job["provider"] = "theta"
                self._record_success("theta")
                
            elif provider == GPUProvider.JARVIS:
                job = await self._submit_to_jarvis(
                    user_id, org_id, app_context, agent_type, base_model,
                    training_data_cid, privacy, atlas_tier, delt_tier, training_config
                )
                job["provider"] = "jarvis"
                self._record_success("jarvis")
            
            logger.info(f"✅ Job submitted to {provider.value.upper()}")
            logger.info(f"  Job ID: {job['job_id']}")
            logger.info(f"  Cost: ${job.get('estimated_cost_usd', job.get('estimated_cost_tfuel', 0)):.2f}")
            
            return job
            
        except Exception as e:
            logger.error(f"❌ {provider.value.upper()} failed: {e}")
            self._record_failure(provider.value)
            
            # Try fallback
            if provider == GPUProvider.THETA and self.jarvis:
                logger.info("🔄 Falling back to JarvisLabs...")
                return await self.submit_training_job(
                    user_id, org_id, app_context, agent_type, base_model,
                    training_data_cid, privacy, atlas_tier, delt_tier,
                    training_config, force_provider=GPUProvider.JARVIS
                )
            
            elif provider == GPUProvider.JARVIS and self.theta:
                logger.info("🔄 Falling back to Theta...")
                return await self.submit_training_job(
                    user_id, org_id, app_context, agent_type, base_model,
                    training_data_cid, privacy, atlas_tier, delt_tier,
                    training_config, force_provider=GPUProvider.THETA
                )
            
            # No fallback available
            raise RuntimeError(f"All GPU providers failed: {e}")
    
    async def _select_provider(
        self,
        force_provider: Optional[GPUProvider] = None
    ) -> GPUProvider:
        """
        Select best GPU provider
        
        Logic:
        1. If forced, use that provider
        2. If preferred and available, use that
        3. Otherwise, use cheapest available
        4. Consider reliability (success rate)
        """
        
        # If forced, use that
        if force_provider:
            return force_provider
        
        # If preferred and available
        if self.preferred_provider != GPUProvider.AUTO:
            if self.preferred_provider == GPUProvider.THETA and self.theta:
                return GPUProvider.THETA
            elif self.preferred_provider == GPUProvider.JARVIS and self.jarvis:
                return GPUProvider.JARVIS
        
        # Auto-select based on cost and reliability
        theta_available = self.theta is not None
        jarvis_available = self.jarvis is not None
        
        if not theta_available and not jarvis_available:
            raise RuntimeError("No GPU providers configured")
        
        # If only one available, use it
        if theta_available and not jarvis_available:
            return GPUProvider.THETA
        if jarvis_available and not theta_available:
            return GPUProvider.JARVIS
        
        # Both available - check reliability
        theta_success_rate = self._get_success_rate("theta")
        jarvis_success_rate = self._get_success_rate("jarvis")
        
        # If Theta has good reliability (>80%), use it (cheaper)
        if theta_success_rate > 0.8:
            return GPUProvider.THETA
        
        # If Theta has poor reliability (<50%), use JarvisLabs
        if theta_success_rate < 0.5:
            logger.warning(f"⚠️  Theta reliability low ({theta_success_rate:.1%}), using JarvisLabs")
            return GPUProvider.JARVIS
        
        # Default: Theta (cheaper)
        return GPUProvider.THETA
    
    async def _submit_to_theta(self, *args, **kwargs) -> Dict[str, Any]:
        """Submit job to Theta GPU"""
        if not self.theta:
            raise RuntimeError("Theta not configured")
        
        return await self.theta.submit_training_job(*args, **kwargs)
    
    async def _submit_to_jarvis(self, *args, **kwargs) -> Dict[str, Any]:
        """Submit job to JarvisLabs"""
        if not self.jarvis:
            raise RuntimeError("JarvisLabs not configured")
        
        return await self.jarvis.submit_training_job(*args, **kwargs)
    
    async def check_job_status(self, job_id: str, provider: str) -> Dict[str, Any]:
        """
        Check job status
        
        Args:
            job_id: Job ID
            provider: Provider name ("theta" or "jarvis")
        
        Returns:
            Job status
        """
        
        if provider == "theta":
            if not self.theta:
                raise RuntimeError("Theta not configured")
            return await self.theta.check_job_status(job_id)
        
        elif provider == "jarvis":
            if not self.jarvis:
                raise RuntimeError("JarvisLabs not configured")
            # Extract instance_id from job_id
            instance_id = job_id.split("_")[1]
            return await self.jarvis.check_job_status(job_id, instance_id)
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _record_success(self, provider: str):
        """Record successful job"""
        self.provider_stats[provider]["success"] += 1
    
    def _record_failure(self, provider: str):
        """Record failed job"""
        self.provider_stats[provider]["failure"] += 1
    
    def _get_success_rate(self, provider: str) -> float:
        """Get success rate for provider"""
        stats = self.provider_stats[provider]
        total = stats["success"] + stats["failure"]
        
        if total == 0:
            return 1.0  # No data, assume good
        
        return stats["success"] / total
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            "theta": {
                **self.provider_stats["theta"],
                "success_rate": self._get_success_rate("theta"),
                "available": self.theta is not None
            },
            "jarvis": {
                **self.provider_stats["jarvis"],
                "success_rate": self._get_success_rate("jarvis"),
                "available": self.jarvis is not None
            }
        }
    
    def get_cost_comparison(self, estimated_hours: float = 2.0) -> Dict[str, Any]:
        """
        Get cost comparison between providers
        
        Args:
            estimated_hours: Estimated training time
        
        Returns:
            Cost comparison
        """
        
        return {
            "theta": {
                "rtx3090": estimated_hours * 0.50,
                "rtx4090": estimated_hours * 0.75,
                "a100": estimated_hours * 2.00
            },
            "jarvis": {
                "rtx3090": estimated_hours * 0.59,
                "rtx4090": estimated_hours * 0.89,
                "a100_40gb": estimated_hours * 1.89,
                "a100_80gb": estimated_hours * 2.49
            },
            "savings_theta_vs_jarvis": {
                "rtx3090": f"{((0.59 - 0.50) / 0.59 * 100):.1f}%",
                "rtx4090": f"{((0.89 - 0.75) / 0.89 * 100):.1f}%",
                "a100": f"{((1.89 - 2.00) / 1.89 * 100):.1f}%"  # Theta more expensive for A100
            }
        }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize unified trainer
        trainer = UnifiedTrainer(
            theta_api_key="your_theta_key",
            jarvis_api_key="your_jarvis_key",
            preferred_provider=GPUProvider.AUTO  # Auto-select
        )
        
        # Submit training job (will auto-select provider)
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
        
        print(f"Job submitted to: {job['provider'].upper()}")
        print(f"Job ID: {job['job_id']}")
        print(f"Cost: ${job.get('estimated_cost_usd', job.get('estimated_cost_tfuel', 0)):.2f}")
        
        # Get cost comparison
        costs = trainer.get_cost_comparison(estimated_hours=2.0)
        print("\nCost Comparison (2 hours):")
        print(f"  Theta RTX3090: ${costs['theta']['rtx3090']:.2f}")
        print(f"  Jarvis RTX3090: ${costs['jarvis']['rtx3090']:.2f}")
        print(f"  Savings: {costs['savings_theta_vs_jarvis']['rtx3090']}")
        
        # Get stats
        stats = trainer.get_stats()
        print("\nProvider Stats:")
        print(f"  Theta: {stats['theta']['success']}/{stats['theta']['failure']} ({stats['theta']['success_rate']:.1%})")
        print(f"  Jarvis: {stats['jarvis']['success']}/{stats['jarvis']['failure']} ({stats['jarvis']['success_rate']:.1%})")
    
    asyncio.run(main())
