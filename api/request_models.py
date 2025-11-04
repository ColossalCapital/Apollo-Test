"""
Apollo API Request/Response Models

Every API call must specify:
1. User/Org/Team context
2. App context (Atlas/Delt/Akashic)
3. Privacy level
4. Agent type
5. Tier information

This ensures proper model routing and privacy isolation.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


# ============================================================================
# Enums (match config/model_config.py)
# ============================================================================

class AppContextEnum(str, Enum):
    """Which application is making the request"""
    ATLAS = "atlas"
    DELT = "delt"
    AKASHIC = "akashic"


class PrivacySchemaEnum(str, Enum):
    """Data and model privacy level"""
    PUBLIC = "public"
    ORG_PUBLIC = "org_public"
    ORG_PRIVATE = "org_private"
    PRIVATE = "private"
    PERSONAL = "personal"


class AtlasTierEnum(str, Enum):
    """Atlas subscription tier"""
    PERSONAL = "personal"
    INDIVIDUAL = "individual"
    TEAM = "team"
    ORGANIZATIONAL = "organizational"


class DeltTierEnum(str, Enum):
    """Delt subscription tier"""
    INDIVIDUAL = "individual"
    TEAM = "team"


# ============================================================================
# Request Context (Required for ALL API calls)
# ============================================================================

class RequestContext(BaseModel):
    """
    Context required for every Apollo API call
    
    This determines:
    - Which model to use
    - Where the model is stored
    - Privacy enforcement
    - Access control
    """
    
    # User/Org/Team identification
    user_id: str = Field(..., description="User ID making the request")
    org_id: Optional[str] = Field(None, description="Organization ID (if applicable)")
    team_id: Optional[str] = Field(None, description="Team ID (if applicable)")
    
    # Application context
    app_context: AppContextEnum = Field(..., description="Which app is calling (Atlas/Delt/Akashic)")
    
    # Privacy level
    privacy: PrivacySchemaEnum = Field(
        PrivacySchemaEnum.PERSONAL,
        description="Privacy level for this request"
    )
    
    # Tier information
    atlas_tier: Optional[AtlasTierEnum] = Field(None, description="Atlas subscription tier")
    delt_tier: Optional[DeltTierEnum] = Field(None, description="Delt subscription tier")
    
    # Process information
    process_name: Optional[str] = Field(None, description="Name of process/feature making request")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "org_id": "org456",
                "team_id": "team789",
                "app_context": "delt",
                "privacy": "org_private",
                "delt_tier": "team",
                "process_name": "trading_dashboard",
                "session_id": "sess_abc123"
            }
        }


# ============================================================================
# Agent Analysis Request
# ============================================================================

class AgentAnalysisRequest(BaseModel):
    """
    Request for agent analysis
    
    Example:
    {
        "context": {...},
        "agent_type": "finance",
        "query": {
            "type": "strategy",
            "asset": "BTC",
            "price_data": {...}
        },
        "quick_mode": false
    }
    """
    
    # Request context (REQUIRED)
    context: RequestContext = Field(..., description="Request context with user/app/privacy info")
    
    # Agent information
    agent_type: str = Field(..., description="Type of agent (finance, communication, etc.)")
    
    # Query data
    query: Dict[str, Any] = Field(..., description="Query data for the agent")
    
    # Options
    quick_mode: bool = Field(False, description="Return static knowledge only (fast)")
    use_personalized: bool = Field(True, description="Use personalized model if available")
    log_interaction: bool = Field(True, description="Log this interaction for training")
    
    class Config:
        schema_extra = {
            "example": {
                "context": {
                    "user_id": "user123",
                    "org_id": None,
                    "team_id": None,
                    "app_context": "delt",
                    "privacy": "personal",
                    "delt_tier": "individual",
                    "process_name": "trading_strategy_analysis"
                },
                "agent_type": "finance",
                "query": {
                    "type": "turtle_trading",
                    "asset": "BTC",
                    "price_data": {
                        "current_price": 45000,
                        "20_day_high": 44500,
                        "atr": 2500
                    }
                },
                "quick_mode": False,
                "use_personalized": True,
                "log_interaction": True
            }
        }


# ============================================================================
# Agent Analysis Response
# ============================================================================

class ModelInfo(BaseModel):
    """Information about the model used"""
    model_type: str = Field(..., description="base | user_finetuned | team_finetuned | org_finetuned")
    model_path: str = Field(..., description="Path to model (local:// or filecoin://)")
    base_model: str = Field(..., description="Base model name")
    isolation_level: str = Field(..., description="personal | team | org | public")
    can_train: bool = Field(..., description="Whether this model can be trained")
    can_share: bool = Field(..., description="Whether this model can be shared")


class AgentAnalysisResponse(BaseModel):
    """
    Response from agent analysis
    
    Includes:
    - Analysis result
    - Model information
    - Performance metrics
    - Training eligibility
    """
    
    # Analysis result
    mode: str = Field(..., description="static | llm_powered | static_fallback")
    result: Dict[str, Any] = Field(..., description="Analysis result")
    
    # Model information
    model_info: ModelInfo = Field(..., description="Information about model used")
    
    # Performance metrics
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    
    # Training information
    interaction_logged: bool = Field(..., description="Whether interaction was logged")
    interactions_until_training: Optional[int] = Field(None, description="Interactions needed before training")
    
    # Session tracking
    request_id: str = Field(..., description="Unique request ID")
    
    class Config:
        schema_extra = {
            "example": {
                "mode": "llm_powered",
                "result": {
                    "recommendation": "BUY",
                    "reasoning": "BTC broke above 20-day high",
                    "position_size": 0.4,
                    "stop_loss": 42500,
                    "confidence": 0.85
                },
                "model_info": {
                    "model_type": "user_finetuned",
                    "model_path": "filecoin://QmXXX...",
                    "base_model": "deepseek-coder-6.7b",
                    "isolation_level": "personal",
                    "can_train": True,
                    "can_share": False
                },
                "response_time_ms": 2500,
                "confidence": 0.85,
                "interaction_logged": True,
                "interactions_until_training": 45,
                "request_id": "req_abc123"
            }
        }


# ============================================================================
# Training Request
# ============================================================================

class TrainingRequest(BaseModel):
    """
    Request to trigger model training
    
    Training depends on:
    - App context (Atlas/Delt/Akashic)
    - Privacy level (determines isolation)
    - Team level (for group training)
    - Storage location (Filecoin path)
    """
    
    # Request context
    context: RequestContext = Field(..., description="Request context")
    
    # Agent to train
    agent_type: str = Field(..., description="Type of agent to train")
    
    # Training options
    force_training: bool = Field(False, description="Force training even if not enough interactions")
    training_method: str = Field("lora", description="lora | qlora | full")
    
    # Custom hyperparameters (optional)
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Custom training config")
    
    class Config:
        schema_extra = {
            "example": {
                "context": {
                    "user_id": "user123",
                    "org_id": "org456",
                    "team_id": "team789",
                    "app_context": "delt",
                    "privacy": "org_private",
                    "delt_tier": "team"
                },
                "agent_type": "finance",
                "force_training": False,
                "training_method": "lora",
                "hyperparameters": {
                    "learning_rate": 2e-5,
                    "epochs": 3
                }
            }
        }


class TrainingResponse(BaseModel):
    """Response from training request"""
    
    # Job information
    job_id: str = Field(..., description="Training job ID")
    model_id: str = Field(..., description="Model identifier")
    
    # Cost & time estimates
    estimated_cost_tfuel: float = Field(..., description="Estimated cost in TFUEL")
    estimated_cost_usd: float = Field(..., description="Estimated cost in USD")
    estimated_time_hours: float = Field(..., description="Estimated training time")
    
    # Infrastructure
    gpu_type: str = Field(..., description="GPU type (RTX3090/RTX4090/A100)")
    storage_path: str = Field(..., description="Filecoin storage path")
    
    # Status
    status_url: str = Field(..., description="URL to check job status")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "theta_job_123",
                "model_id": "delt:finance:org456:team:team789",
                "estimated_cost_tfuel": 0.5,
                "estimated_cost_usd": 0.50,
                "estimated_time_hours": 2.0,
                "gpu_type": "RTX3090",
                "storage_path": "delt/team/org456/team789/finance/",
                "status_url": "https://api.thetaedgecloud.com/v1/jobs/theta_job_123/status"
            }
        }


# ============================================================================
# Feedback Request (for continuous learning)
# ============================================================================

class FeedbackRequest(BaseModel):
    """
    Submit feedback on agent response
    
    Used for continuous learning
    """
    
    # Request context
    context: RequestContext = Field(..., description="Request context")
    
    # Request to rate
    request_id: str = Field(..., description="Request ID from original response")
    agent_type: str = Field(..., description="Agent type")
    
    # Feedback
    rating: float = Field(..., ge=0.0, le=1.0, description="Rating (0.0-1.0)")
    feedback_text: Optional[str] = Field(None, description="Optional text feedback")
    
    # What happened
    action_taken: Optional[str] = Field(None, description="What action user took")
    outcome: Optional[str] = Field(None, description="What was the outcome")
    
    class Config:
        schema_extra = {
            "example": {
                "context": {
                    "user_id": "user123",
                    "app_context": "delt",
                    "privacy": "personal"
                },
                "request_id": "req_abc123",
                "agent_type": "finance",
                "rating": 0.9,
                "feedback_text": "Great recommendation!",
                "action_taken": "bought_btc",
                "outcome": "profit"
            }
        }


# ============================================================================
# Model Info Request
# ============================================================================

class ModelInfoRequest(BaseModel):
    """Request information about available models"""
    
    context: RequestContext = Field(..., description="Request context")
    agent_type: Optional[str] = Field(None, description="Filter by agent type")
    
    class Config:
        schema_extra = {
            "example": {
                "context": {
                    "user_id": "user123",
                    "org_id": "org456",
                    "app_context": "delt",
                    "privacy": "org_private",
                    "delt_tier": "team"
                },
                "agent_type": "finance"
            }
        }


class ModelInfoResponse(BaseModel):
    """Response with model information"""
    
    # Available models
    available_models: List[ModelInfo] = Field(..., description="Models user can access")
    
    # Current model
    current_model: Optional[ModelInfo] = Field(None, description="Currently active model")
    
    # Training status
    training_in_progress: bool = Field(..., description="Whether training is in progress")
    training_job_id: Optional[str] = Field(None, description="Active training job ID")
    
    # Statistics
    total_interactions: int = Field(..., description="Total interactions logged")
    interactions_until_training: int = Field(..., description="Interactions until next training")
    
    class Config:
        schema_extra = {
            "example": {
                "available_models": [
                    {
                        "model_type": "base",
                        "model_path": "local://models/deepseek-coder-6.7b",
                        "base_model": "deepseek-coder-6.7b",
                        "isolation_level": "personal",
                        "can_train": True,
                        "can_share": False
                    },
                    {
                        "model_type": "user_finetuned",
                        "model_path": "filecoin://QmXXX...",
                        "base_model": "deepseek-coder-6.7b",
                        "isolation_level": "personal",
                        "can_train": True,
                        "can_share": False
                    }
                ],
                "current_model": {
                    "model_type": "user_finetuned",
                    "model_path": "filecoin://QmXXX...",
                    "base_model": "deepseek-coder-6.7b",
                    "isolation_level": "personal",
                    "can_train": True,
                    "can_share": False
                },
                "training_in_progress": False,
                "training_job_id": None,
                "total_interactions": 87,
                "interactions_until_training": 13
            }
        }


# ============================================================================
# Example Usage in API Calls
# ============================================================================

"""
Example 1: Atlas Personal user queries finance agent

POST /api/v1/analyze

{
    "context": {
        "user_id": "user123",
        "org_id": null,
        "team_id": null,
        "app_context": "atlas",
        "privacy": "personal",
        "atlas_tier": "personal",
        "process_name": "financial_planning"
    },
    "agent_type": "finance",
    "query": {
        "type": "portfolio_optimization",
        "assets": ["BTC", "ETH", "STOCKS"],
        "risk_tolerance": "moderate"
    },
    "quick_mode": false,
    "use_personalized": true,
    "log_interaction": true
}

Response:
- Routes to: atlas/personal/user123/finance/
- Uses: Personal model (if exists) or base model
- Logs interaction for future training
- Returns personalized recommendation
"""

"""
Example 2: Delt Team user queries trading agent

POST /api/v1/analyze

{
    "context": {
        "user_id": "user456",
        "org_id": "org789",
        "team_id": "team123",
        "app_context": "delt",
        "privacy": "org_private",
        "delt_tier": "team",
        "process_name": "live_trading"
    },
    "agent_type": "finance",
    "query": {
        "type": "turtle_trading",
        "asset": "BTC",
        "price_data": {...}
    },
    "quick_mode": false,
    "use_personalized": true,
    "log_interaction": true
}

Response:
- Routes to: delt/team/org789/team123/finance/
- Uses: Team model (shared by all team members)
- Logs interaction to team training data
- Returns team-optimized recommendation
"""

# ============================================================================
# Health Check Response
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    agents_loaded: int = Field(..., description="Number of agents loaded")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "agents_loaded": 69
            }
        }


"""
Example 3: Akashic code analysis (always personal)

POST /api/v1/analyze

{
    "context": {
        "user_id": "user789",
        "org_id": "org123",
        "team_id": null,
        "app_context": "akashic",
        "privacy": "personal",  # Always personal for code
        "atlas_tier": "organizational",
        "process_name": "code_review"
    },
    "agent_type": "development",
    "query": {
        "code": "...",
        "language": "python",
        "action": "review"
    },
    "quick_mode": false,
    "use_personalized": true,
    "log_interaction": true
}

Response:
- Routes to: akashic/personal/user789/development/
- Uses: Personal code model (NEVER shared for security)
- Logs to personal training data only
- Returns personalized code suggestions
"""
