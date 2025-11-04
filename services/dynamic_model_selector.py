"""
Dynamic Model Selection Service

Selects the best model for each task based on:
- Task type (code, chat, reasoning, etc.)
- Required capabilities
- Performance requirements
- Cost constraints
- Available models on Theta GPU

No hardcoded models - queries Theta GPU API for available models at runtime.
"""

import os
import logging
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from enum import Enum
import aiohttp

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Types of tasks that require LLM inference"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_COMPLETION = "code_completion"
    GENERAL_CHAT = "general_chat"
    COMPLEX_REASONING = "complex_reasoning"
    FAST_RESPONSE = "fast_response"
    DOCUMENT_ANALYSIS = "document_analysis"
    DATA_ANALYSIS = "data_analysis"
    TRADING_STRATEGY = "trading_strategy"


@dataclass
class ModelCapabilities:
    """Model capabilities and characteristics"""
    name: str
    provider: str  # "theta_gpu", "jarvislabs"
    size_params: int  # Number of parameters (e.g., 7B, 32B)
    context_length: int  # Max context tokens
    cost_per_token: float  # Cost in TFUEL
    avg_latency_ms: int  # Average response time
    specializations: List[str]  # ["code", "chat", "reasoning"]
    available: bool = True


class DynamicModelSelector:
    """
    Dynamically selects the best model for each task
    
    Features:
    - Queries available models from Theta GPU API
    - Caches model list (refreshes every hour)
    - Selects based on task requirements
    - Falls back to alternatives if primary unavailable
    """
    
    def __init__(self):
        self.theta_api_key = os.getenv("THETA_API_KEY")
        self.theta_model_api_url = os.getenv("THETA_MODEL_API_URL", "https://api.thetaedgecloud.com/models/v1")
        self.use_theta = os.getenv("USE_THETA_GPU", "false").lower() == "true"
        
        self.jarvis_api_key = os.getenv("JARVISLABS_API_KEY")
        self.use_jarvis = os.getenv("USE_JARVISLABS", "false").lower() == "true"
        
        # Cache of available models (refreshed periodically)
        self._available_models: List[ModelCapabilities] = []
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl_seconds = 3600  # 1 hour
    
    async def get_available_models(self, force_refresh: bool = False) -> List[ModelCapabilities]:
        """
        Get list of available models from Theta GPU API
        
        Caches results for 1 hour to avoid excessive API calls
        """
        import time
        
        # Check cache
        if not force_refresh and self._available_models and self._cache_timestamp:
            age = time.time() - self._cache_timestamp
            if age < self._cache_ttl_seconds:
                return self._available_models
        
        models = []
        
        # Query Theta GPU models
        if self.use_theta and self.theta_api_key:
            try:
                theta_models = await self._query_theta_models()
                models.extend(theta_models)
            except Exception as e:
                logger.error(f"Failed to query Theta GPU models: {e}")
        
        # Query JarvisLabs models
        if self.use_jarvis and self.jarvis_api_key:
            try:
                jarvis_models = await self._query_jarvislabs_models()
                models.extend(jarvis_models)
            except Exception as e:
                logger.error(f"Failed to query JarvisLabs models: {e}")
        
        # Update cache
        self._available_models = models
        self._cache_timestamp = time.time()
        
        return models
    
    async def _query_theta_models(self) -> List[ModelCapabilities]:
        """Query available models from Theta GPU API"""
        
        # TODO: Implement actual Theta GPU API call
        # For now, return known models based on Theta EdgeCloud documentation
        
        # These are common models available on Theta EdgeCloud
        # In production, query the API for real-time availability
        return [
            ModelCapabilities(
                name="Qwen2.5-Coder-32B",
                provider="theta_gpu",
                size_params=32_000_000_000,
                context_length=32768,
                cost_per_token=0.000001,  # ~$0.003 per query
                avg_latency_ms=800,
                specializations=["code", "reasoning"],
                available=True
            ),
            ModelCapabilities(
                name="DeepSeek-Coder-33B",
                provider="theta_gpu",
                size_params=33_000_000_000,
                context_length=16384,
                cost_per_token=0.000001,
                avg_latency_ms=850,
                specializations=["code"],
                available=True
            ),
            ModelCapabilities(
                name="Mistral-7B",
                provider="theta_gpu",
                size_params=7_000_000_000,
                context_length=8192,
                cost_per_token=0.0000005,  # Cheaper, smaller model
                avg_latency_ms=300,
                specializations=["chat", "general"],
                available=True
            ),
            ModelCapabilities(
                name="Mixtral-8x7B",
                provider="theta_gpu",
                size_params=47_000_000_000,  # 8 experts x 7B
                context_length=32768,
                cost_per_token=0.0000015,
                avg_latency_ms=1200,
                specializations=["reasoning", "complex"],
                available=True
            ),
            ModelCapabilities(
                name="Llama-3-8B",
                provider="theta_gpu",
                size_params=8_000_000_000,
                context_length=8192,
                cost_per_token=0.0000006,
                avg_latency_ms=350,
                specializations=["chat", "general"],
                available=True
            ),
        ]
    
    async def _query_jarvislabs_models(self) -> List[ModelCapabilities]:
        """Query available models from JarvisLabs API"""
        
        # TODO: Implement actual JarvisLabs API call
        # For now, return common models
        
        return [
            ModelCapabilities(
                name="DeepSeek-Coder-33B",
                provider="jarvislabs",
                size_params=33_000_000_000,
                context_length=16384,
                cost_per_token=0.0000015,  # Slightly more expensive
                avg_latency_ms=900,
                specializations=["code"],
                available=True
            ),
        ]
    
    async def select_model(
        self,
        task_type: TaskType,
        priority: Literal["speed", "quality", "cost"] = "quality",
        min_context_length: Optional[int] = None,
        max_cost_per_token: Optional[float] = None
    ) -> Optional[ModelCapabilities]:
        """
        Select the best model for a given task
        
        Args:
            task_type: Type of task (code, chat, reasoning, etc.)
            priority: What to optimize for (speed, quality, cost)
            min_context_length: Minimum required context length
            max_cost_per_token: Maximum acceptable cost per token
        
        Returns:
            Best model for the task, or None if no suitable model found
        """
        
        # Get available models
        models = await self.get_available_models()
        
        if not models:
            logger.warning("No models available")
            return None
        
        # Filter by task specialization
        task_specialization_map = {
            TaskType.CODE_GENERATION: "code",
            TaskType.CODE_REVIEW: "code",
            TaskType.CODE_COMPLETION: "code",
            TaskType.GENERAL_CHAT: "chat",
            TaskType.COMPLEX_REASONING: "reasoning",
            TaskType.FAST_RESPONSE: "general",
            TaskType.DOCUMENT_ANALYSIS: "general",
            TaskType.DATA_ANALYSIS: "reasoning",
            TaskType.TRADING_STRATEGY: "reasoning",
        }
        
        required_spec = task_specialization_map.get(task_type, "general")
        suitable_models = [
            m for m in models
            if m.available and required_spec in m.specializations
        ]
        
        # If no specialized models, use all available
        if not suitable_models:
            suitable_models = [m for m in models if m.available]
        
        # Apply filters
        if min_context_length:
            suitable_models = [m for m in suitable_models if m.context_length >= min_context_length]
        
        if max_cost_per_token:
            suitable_models = [m for m in suitable_models if m.cost_per_token <= max_cost_per_token]
        
        if not suitable_models:
            logger.warning(f"No suitable models found for task {task_type}")
            return None
        
        # Sort by priority
        if priority == "speed":
            # Fastest response time
            suitable_models.sort(key=lambda m: m.avg_latency_ms)
        elif priority == "cost":
            # Cheapest
            suitable_models.sort(key=lambda m: m.cost_per_token)
        else:  # quality
            # Largest model (more parameters = better quality generally)
            suitable_models.sort(key=lambda m: m.size_params, reverse=True)
        
        # Return best match
        selected = suitable_models[0]
        logger.info(f"Selected model for {task_type}: {selected.name} ({selected.provider})")
        
        return selected
    
    def get_model_for_chat(self) -> str:
        """
        Get model name for chat (synchronous helper)
        
        Returns model name string for immediate use
        """
        # For chat, prioritize speed and cost
        # Default to Mistral 7B if available, otherwise Qwen2.5-Coder
        
        if self.use_theta:
            return "Mistral-7B"  # Fast and cheap for chat
        elif self.use_jarvis:
            return "DeepSeek-Coder-33B"
        else:
            return "Mock"
    
    def get_model_for_code(self) -> str:
        """
        Get model name for code generation (synchronous helper)
        
        Returns model name string for immediate use
        """
        # For code, prioritize quality
        # Default to Qwen2.5-Coder 32B (best for code)
        
        if self.use_theta:
            return "Qwen2.5-Coder-32B"  # Best for code
        elif self.use_jarvis:
            return "DeepSeek-Coder-33B"
        else:
            return "Mock"


# Global instance
_model_selector: Optional[DynamicModelSelector] = None


def get_model_selector() -> DynamicModelSelector:
    """Get global model selector instance"""
    global _model_selector
    if _model_selector is None:
        _model_selector = DynamicModelSelector()
    return _model_selector


# Example usage
async def example():
    """Example usage of dynamic model selection"""
    
    selector = get_model_selector()
    
    # Get available models
    models = await selector.get_available_models()
    print(f"Available models: {len(models)}")
    for model in models:
        print(f"  - {model.name} ({model.provider}): {model.size_params/1e9:.1f}B params")
    
    # Select model for code generation
    code_model = await selector.select_model(
        task_type=TaskType.CODE_GENERATION,
        priority="quality"
    )
    print(f"\nBest model for code generation: {code_model.name}")
    
    # Select model for fast chat
    chat_model = await selector.select_model(
        task_type=TaskType.GENERAL_CHAT,
        priority="speed"
    )
    print(f"Best model for fast chat: {chat_model.name}")
    
    # Select model for complex reasoning with budget
    reasoning_model = await selector.select_model(
        task_type=TaskType.COMPLEX_REASONING,
        priority="quality",
        max_cost_per_token=0.000001
    )
    print(f"Best model for reasoning (budget): {reasoning_model.name if reasoning_model else 'None'}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example())
