"""
Base Agent Class for Apollo AI System with Context Awareness

All specialized agents inherit from this base class.

Context-Aware Features:
- Tier-appropriate recommendations
- Privacy-aware responses
- Smart model routing based on context
- Training data management
- Storage location determination
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class AgentContext:
    """
    Context passed to agents for context-aware analysis
    
    This context guides:
    - Model selection (which trained model to use)
    - Storage location (where to save training data)
    - Recommendations (tier-appropriate suggestions)
    - Privacy handling (what can be shared)
    """
    
    def __init__(
        self,
        app_context: str,
        user_id: str,
        org_id: Optional[str] = None,
        team_id: Optional[str] = None,
        atlas_tier: Optional[str] = None,
        delt_tier: Optional[str] = None,
        privacy: str = "personal",
        isolation_level: str = "personal",
        can_share: bool = False,
        can_train: bool = True,
        model_path: Optional[str] = None,
        storage_path: Optional[str] = None,
        parent_context: Optional[str] = None,
        conflict_resolution: str = "last_write_wins"
    ):
        self.app_context = app_context
        self.user_id = user_id
        self.org_id = org_id
        self.team_id = team_id
        self.atlas_tier = atlas_tier
        self.delt_tier = delt_tier
        self.privacy = privacy
        self.isolation_level = isolation_level
        self.can_share = can_share
        self.can_train = can_train
        self.model_path = model_path
        self.storage_path = storage_path
        self.parent_context = parent_context
        self.conflict_resolution = conflict_resolution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging"""
        return {
            "app_context": self.app_context,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "team_id": self.team_id,
            "atlas_tier": self.atlas_tier,
            "delt_tier": self.delt_tier,
            "privacy": self.privacy,
            "isolation_level": self.isolation_level,
            "can_share": self.can_share,
            "can_train": self.can_train,
            "model_path": self.model_path,
            "storage_path": self.storage_path,
            "parent_context": self.parent_context,
            "conflict_resolution": self.conflict_resolution
        }


class BaseAgent(ABC):
    """
    Base class for all Apollo agents with context awareness
    
    Context-aware agents can:
    - Use the right trained model for the user/org/team
    - Store training data in the correct location
    - Give tier-appropriate recommendations
    - Respect privacy boundaries
    """
    
    def __init__(self, name: str, model: str = "phi-2"):
        self.name = name
        self.model = model
        self.atlas_client = None  # Will be injected
        self.llm_client = None    # Will be injected
        
    @abstractmethod
    async def analyze(self, data: Any, context: Optional[AgentContext] = None) -> Dict[str, Any]:
        """
        Analyze data and return intelligence.
        Must be implemented by each agent.
        
        Args:
            data: The data to analyze
            context: Context for context-aware analysis (tier, privacy, model path, etc.)
        
        Returns:
            Analysis result with intelligence
        """
        pass
    
    async def query_llm(
        self, 
        prompt: str, 
        agent_context: Optional[AgentContext] = None
    ) -> str:
        """
        Query the LLM with a prompt using context-aware model selection
        
        The agent_context determines:
        - Which trained model to use (personal/team/org)
        - Model path (Filecoin location)
        - Temperature and parameters
        """
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        try:
            # Build request with context
            request_data = {
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # Add context-aware model selection
            if agent_context:
                request_data["context"] = agent_context.to_dict()
                
                # Use trained model if available
                if agent_context.model_path:
                    request_data["model_path"] = agent_context.model_path
                    logger.info(f"Using trained model: {agent_context.model_path}")
            
            response = await self.llm_client.post(
                "/completion",
                json=request_data
            )
            return response.json()["content"]
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            raise
    
    async def query_atlas(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Query Atlas for data"""
        if not self.atlas_client:
            raise RuntimeError("Atlas client not initialized")
        
        try:
            response = await self.atlas_client.get(endpoint, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Atlas query failed: {e}")
            raise
    
    async def store_result(self, result: Dict[str, Any]) -> None:
        """Store analysis result back in Atlas"""
        if not self.atlas_client:
            raise RuntimeError("Atlas client not initialized")
        
        try:
            await self.atlas_client.post("/api/data/store", json=result)
        except Exception as e:
            logger.error(f"Failed to store result: {e}")
            raise
    
    def extract_text(self, data: Dict, key: str, default: str = "") -> str:
        """Safely extract text from data"""
        return str(data.get(key, default))
    
    def extract_number(self, data: Dict, key: str, default: float = 0.0) -> float:
        """Safely extract number from data"""
        try:
            return float(data.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def extract_list(self, data: Dict, key: str, default: Optional[List] = None) -> List:
        """Safely extract list from data"""
        value = data.get(key, default or [])
        return value if isinstance(value, list) else []


class AgentResult:
    """Standard result format for all agents"""
    
    def __init__(
        self,
        agent_name: str,
        data_type: str,
        intelligence: Dict[str, Any],
        confidence: float = 1.0,
        metadata: Optional[Dict] = None
    ):
        self.agent_name = agent_name
        self.data_type = data_type
        self.intelligence = intelligence
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "data_type": self.data_type,
            "intelligence": self.intelligence,
            "confidence": self.confidence,
            "metadata": self.metadata
        }
