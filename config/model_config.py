"""
Model Configuration System - Multi-tenant isolation across apps and tiers

Handles:
1. Atlas tiers: Personal, Individual, Team, Organizational
2. Privacy schemas: Public, Org Public, Org Private, Private, Personal
3. Delt tiers: Individual, Team
4. Akashic context isolation
"""

from typing import Dict, Any, Optional
from enum import Enum


# ============================================================================
# Atlas Tiers (Data & Model Sharing)
# ============================================================================

class AtlasTier(Enum):
    """Atlas SaaS subscription tiers"""
    FREE = "free"                  # $0/mo - Try before buy, no custom ontology
    PERSONAL = "personal"          # $29/mo - 1 entity, basic integrations
    INDIVIDUAL = "individual"      # Individual tier with sharing capabilities
    TEAM = "team"                  # $99/mo - 5 entities, team collaboration
    ENTERPRISE = "enterprise"      # Custom - Unlimited entities, enterprise support


class PrivacySchema(Enum):
    """Data and model privacy levels"""
    PUBLIC = "public"                    # Anyone can access
    ORG_PUBLIC = "org_public"           # Anyone in org can access
    ORG_PRIVATE = "org_private"         # Only specific teams in org
    PRIVATE = "private"                  # Only user + explicitly shared
    PERSONAL = "personal"                # Only user, never shared


# ============================================================================
# Delt Tiers
# ============================================================================

class DeltTier(Enum):
    """Delt subscription tiers"""
    RETAIL = "retail"              # Individual retail trader
    PROFESSIONAL = "professional"  # Professional trader
    INSTITUTIONAL = "institutional"  # Hedge fund / institution
    TEAM = "team"                  # Trading team (deprecated, use PROFESSIONAL)


# ============================================================================
# Application Context
# ============================================================================

class AppContext(Enum):
    """Which application is using the model"""
    ATLAS = "atlas"                    # Personal AI assistant (standalone)
    DELT = "delt"                      # Trading platform (standalone)
    AKASHIC = "akashic"                # Code editor (standalone)
    AKASHIC_IN_ATLAS = "akashic_atlas" # Code editor within Atlas
    AKASHIC_IN_DELT = "akashic_delt"   # Code editor within Delt (for trading bots)


# ============================================================================
# Task-Specific Model Selection
# ============================================================================

AGENT_MODELS = {
    # Finance agents - Need numerical reasoning
    "finance": {
        "base_model": "deepseek-coder-33b",
        "context_size": 16384,
        "temperature": 0.2,
        "use_cases": ["trading", "portfolio", "sentiment", "backtest"],
        "inference": "theta_gpu"  # All on Theta GPU
    },
    
    # Code agents - Need code understanding (BEST MODELS)
    "development": {
        "primary": "qwen2.5-coder-32b",      # 92.7% HumanEval (matches Claude!)
        "fallback": "deepseek-coder-33b",    # 78.6% HumanEval (excellent)
        "fast": "starcoder2-15b",            # 72.6% HumanEval (quick completions)
        "context_size": 32768,
        "temperature": 0.1,
        "use_cases": ["github", "code_review", "deployment", "refactoring"],
        "inference": "theta_gpu"
    },
    
    # Code completion - Fast responses
    "code_completion": {
        "base_model": "starcoder2-15b",
        "context_size": 8192,
        "temperature": 0.0,
        "use_cases": ["autocomplete", "suggestions"],
        "inference": "theta_gpu"
    },
    
    # Communication agents - Need language understanding
    "communication": {
        "base_model": "mistral-7b-instruct-v0.2",
        "context_size": 8192,
        "temperature": 0.7,
        "use_cases": ["email", "calendar", "slack"],
        "inference": "theta_gpu"
    },
    
    # Legal/Document agents - Need long context
    "legal": {
        "base_model": "mixtral-8x7b-instruct",
        "context_size": 32768,
        "temperature": 0.3,
        "use_cases": ["legal", "contract", "compliance", "document"],
        "inference": "theta_gpu"
    },
    
    # Media agents - Need multimodal
    "media": {
        "base_model": "llava-1.6-34b",
        "context_size": 4096,
        "temperature": 0.5,
        "use_cases": ["vision", "audio", "video"]
    },
    
    # Analytics agents - Need data reasoning
    "analytics": {
        "base_model": "phi-3-medium",
        "context_size": 4096,
        "temperature": 0.4,
        "use_cases": ["data", "text", "schema"]
    },
    
    # Default for others
    "default": {
        "base_model": "phi-3-medium",
        "context_size": 4096,
        "temperature": 0.5,
        "use_cases": []
    }
}


# ============================================================================
# Model Isolation Strategy
# ============================================================================

class ModelIsolationStrategy:
    """
    Determines which model to use based on:
    - User/Organization ID
    - Atlas tier
    - Privacy schema
    - Application context (Atlas/Delt/Akashic)
    - Agent type
    """
    
    @staticmethod
    def get_model_path(
        user_id: str,
        org_id: Optional[str],
        atlas_tier: AtlasTier,
        privacy_schema: PrivacySchema,
        app_context: AppContext,
        agent_type: str,
        delt_tier: Optional[DeltTier] = None
    ) -> Dict[str, Any]:
        """
        Get the appropriate model path and configuration
        
        Returns:
            {
                "model_type": "base" | "user_finetuned" | "team_finetuned" | "org_finetuned",
                "model_path": "filecoin://Qm..." or "local://models/...",
                "base_model": "phi-3-medium",
                "can_train": bool,
                "can_share": bool,
                "isolation_level": "personal" | "team" | "org" | "public"
            }
        """
        
        # Get base model for agent type
        base_config = AGENT_MODELS.get(agent_type, AGENT_MODELS["default"])
        base_model = base_config["base_model"]
        
        # Determine isolation level
        isolation = ModelIsolationStrategy._determine_isolation(
            atlas_tier, privacy_schema, app_context, delt_tier
        )
        
        # Build model identifier
        model_id = ModelIsolationStrategy._build_model_id(
            user_id, org_id, isolation, app_context, agent_type
        )
        
        # Check if personalized model exists
        personalized_exists = ModelIsolationStrategy._check_personalized_model(model_id)
        
        if personalized_exists:
            return {
                "model_type": f"{isolation['level']}_finetuned",
                "model_path": f"filecoin://{model_id}",
                "base_model": base_model,
                "can_train": isolation["can_train"],
                "can_share": isolation["can_share"],
                "isolation_level": isolation["level"],
                "context_size": base_config["context_size"],
                "temperature": base_config["temperature"]
            }
        else:
            return {
                "model_type": "base",
                "model_path": f"local://models/{base_model}",
                "base_model": base_model,
                "can_train": isolation["can_train"],
                "can_share": isolation["can_share"],
                "isolation_level": isolation["level"],
                "context_size": base_config["context_size"],
                "temperature": base_config["temperature"]
            }
    
    @staticmethod
    def _determine_isolation(
        atlas_tier: AtlasTier,
        privacy_schema: PrivacySchema,
        app_context: AppContext,
        delt_tier: Optional[DeltTier]
    ) -> Dict[str, Any]:
        """
        Determine isolation level and permissions
        
        Isolation Levels:
        - personal: Only this user, never shared
        - team: Shared within team
        - org: Shared within organization
        - public: Shared with everyone
        """
        
        # ATLAS CONTEXT
        if app_context == AppContext.ATLAS:
            # Free tier: No training, basic access only
            if atlas_tier == AtlasTier.FREE:
                return {
                    "level": "personal",
                    "can_train": False,  # Free tier can't train
                    "can_share": False,
                    "scope": "user"
                }
            
            # Personal tier: Always personal, can train
            elif atlas_tier == AtlasTier.PERSONAL:
                return {
                    "level": "personal",
                    "can_train": True,
                    "can_share": False,
                    "scope": "user"
                }
            
            # Individual tier: Can share if privacy allows
            elif atlas_tier == AtlasTier.INDIVIDUAL:
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user"
                    }
                elif privacy_schema == PrivacySchema.PRIVATE:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": True,  # Can explicitly share
                        "scope": "user"
                    }
                else:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": True,
                        "scope": "user"
                    }
            
            # Team tier: Team collaboration
            elif atlas_tier == AtlasTier.TEAM:
                if privacy_schema in [PrivacySchema.PERSONAL, PrivacySchema.PRIVATE]:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": True,
                        "scope": "user"
                    }
                elif privacy_schema == PrivacySchema.ORG_PRIVATE:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team"
                    }
                else:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team"
                    }
            
            # Enterprise tier: Full org-level sharing
            elif atlas_tier == AtlasTier.ENTERPRISE:
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user"
                    }
                elif privacy_schema == PrivacySchema.PRIVATE:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": True,
                        "scope": "user"
                    }
                elif privacy_schema == PrivacySchema.ORG_PRIVATE:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team"
                    }
                elif privacy_schema == PrivacySchema.ORG_PUBLIC:
                    return {
                        "level": "org",
                        "can_train": True,
                        "can_share": True,
                        "scope": "org"
                    }
                else:  # PUBLIC
                    return {
                        "level": "public",
                        "can_train": True,
                        "can_share": True,
                        "scope": "public"
                    }
        
        # DELT CONTEXT
        elif app_context == AppContext.DELT:
            if delt_tier == DeltTier.RETAIL:
                # Retail traders: personal models only
                return {
                    "level": "personal",
                    "can_train": True,
                    "can_share": False,
                    "scope": "user"
                }
            elif delt_tier == DeltTier.PROFESSIONAL:
                # Professional traders: can share with team
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user"
                    }
                else:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team"
                    }
            elif delt_tier == DeltTier.INSTITUTIONAL:
                # Institutional: org-level models
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user"
                    }
                elif privacy_schema in [PrivacySchema.PRIVATE, PrivacySchema.ORG_PRIVATE]:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team"
                    }
                else:  # ORG_PUBLIC or PUBLIC
                    return {
                        "level": "org",
                        "can_train": True,
                        "can_share": True,
                        "scope": "org"
                    }
            elif delt_tier == DeltTier.TEAM:
                # Deprecated: use PROFESSIONAL instead
                return {
                    "level": "team",
                    "can_train": True,
                    "can_share": True,
                    "scope": "team"
                }
        
        # AKASHIC CONTEXT (standalone - privacy-controlled)
        elif app_context == AppContext.AKASHIC:
            # Default to personal for security, but respect privacy settings
            if privacy_schema == PrivacySchema.PERSONAL:
                return {
                    "level": "personal",
                    "can_train": True,
                    "can_share": False,
                    "scope": "user",
                    "conflict_resolution": "last_write_wins"
                }
            else:
                # Allow sharing if user explicitly chooses
                return {
                    "level": "personal",
                    "can_train": True,
                    "can_share": True,
                    "scope": "user",
                    "conflict_resolution": "last_write_wins"
                }
        
        # AKASHIC IN ATLAS (code editor within Atlas)
        elif app_context == AppContext.AKASHIC_IN_ATLAS:
            # Privacy-controlled: User chooses via privacy settings
            
            # Free/Personal tier: Always personal
            if atlas_tier in [AtlasTier.FREE, AtlasTier.PERSONAL]:
                return {
                    "level": "personal",
                    "can_train": True,
                    "can_share": False,
                    "scope": "user",
                    "parent_context": "atlas",
                    "conflict_resolution": "last_write_wins"
                }
            
            # Individual tier: Can share if privacy allows
            elif atlas_tier == AtlasTier.INDIVIDUAL:
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
                else:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": True,  # Can share explicitly
                        "scope": "user",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
            
            # Team tier: Can share at team level
            elif atlas_tier == AtlasTier.TEAM:
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
                elif privacy_schema in [PrivacySchema.PRIVATE, PrivacySchema.ORG_PRIVATE]:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
                else:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
            
            # Enterprise tier: Can share at org level
            elif atlas_tier == AtlasTier.ENTERPRISE:
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
                elif privacy_schema in [PrivacySchema.PRIVATE, PrivacySchema.ORG_PRIVATE]:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
                else:  # ORG_PUBLIC or PUBLIC
                    return {
                        "level": "org",
                        "can_train": True,
                        "can_share": True,
                        "scope": "org",
                        "parent_context": "atlas",
                        "conflict_resolution": "last_write_wins"
                    }
        
        # AKASHIC IN DELT (code editor within Delt for trading bots)
        elif app_context == AppContext.AKASHIC_IN_DELT:
            # For trading bots, code can be shared at team/org level
            # But default to personal for security
            if delt_tier == DeltTier.RETAIL:
                return {
                    "level": "personal",
                    "can_train": True,
                    "can_share": False,
                    "scope": "user",
                    "parent_context": "delt"
                }
            elif delt_tier == DeltTier.PROFESSIONAL:
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user",
                        "parent_context": "delt"
                    }
                else:
                    # Professional can share trading bot code with team
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team",
                        "parent_context": "delt"
                    }
            elif delt_tier == DeltTier.INSTITUTIONAL:
                if privacy_schema == PrivacySchema.PERSONAL:
                    return {
                        "level": "personal",
                        "can_train": True,
                        "can_share": False,
                        "scope": "user",
                        "parent_context": "delt"
                    }
                elif privacy_schema in [PrivacySchema.PRIVATE, PrivacySchema.ORG_PRIVATE]:
                    return {
                        "level": "team",
                        "can_train": True,
                        "can_share": True,
                        "scope": "team",
                        "parent_context": "delt"
                    }
                else:
                    # Institutional can share at org level
                    return {
                        "level": "org",
                        "can_train": True,
                        "can_share": True,
                        "scope": "org",
                        "parent_context": "delt"
                    }
            else:
                # Default: personal
                return {
                    "level": "personal",
                    "can_train": True,
                    "can_share": False,
                    "scope": "user",
                    "parent_context": "delt"
                }
        
        # Default: personal, isolated
        return {
            "level": "personal",
            "can_train": True,
            "can_share": False,
            "scope": "user"
        }
    
    @staticmethod
    def _build_model_id(
        user_id: str,
        org_id: Optional[str],
        isolation: Dict[str, Any],
        app_context: AppContext,
        agent_type: str
    ) -> str:
        """
        Build unique model identifier
        
        Format:
        - Personal: {app}:{agent_type}:{user_id}
        - Team: {app}:{agent_type}:{org_id}:team:{team_id}
        - Org: {app}:{agent_type}:{org_id}:org
        - Public: {app}:{agent_type}:public
        """
        
        level = isolation["level"]
        app = app_context.value
        
        if level == "personal":
            return f"{app}:{agent_type}:{user_id}"
        elif level == "team":
            # TODO: Get team_id from context
            team_id = "default_team"
            return f"{app}:{agent_type}:{org_id}:team:{team_id}"
        elif level == "org":
            return f"{app}:{agent_type}:{org_id}:org"
        elif level == "public":
            return f"{app}:{agent_type}:public"
        
        return f"{app}:{agent_type}:{user_id}"
    
    @staticmethod
    def _check_personalized_model(model_id: str) -> bool:
        """Check if personalized model exists on Filecoin"""
        # TODO: Implement Filecoin lookup
        return False


# ============================================================================
# Training Data Isolation
# ============================================================================

class TrainingDataIsolation:
    """
    Manages training data isolation based on privacy settings
    
    Rules:
    1. Personal data NEVER leaves user's control
    2. Team data shared within team only
    3. Org data shared within org only
    4. Public data can be used for public models
    """
    
    @staticmethod
    def can_use_for_training(
        data_privacy: PrivacySchema,
        model_isolation: str
    ) -> bool:
        """
        Check if data can be used for training given model isolation level
        
        Examples:
        - Personal data → Only personal models
        - Team data → Personal or team models
        - Org data → Personal, team, or org models
        - Public data → Any model
        """
        
        if data_privacy == PrivacySchema.PERSONAL:
            return model_isolation == "personal"
        
        elif data_privacy == PrivacySchema.PRIVATE:
            return model_isolation == "personal"
        
        elif data_privacy == PrivacySchema.ORG_PRIVATE:
            return model_isolation in ["personal", "team"]
        
        elif data_privacy == PrivacySchema.ORG_PUBLIC:
            return model_isolation in ["personal", "team", "org"]
        
        elif data_privacy == PrivacySchema.PUBLIC:
            return True  # Can use for any model
        
        return False
    
    @staticmethod
    def get_training_data_path(
        user_id: str,
        org_id: Optional[str],
        privacy: PrivacySchema,
        app_context: AppContext,
        agent_type: str
    ) -> str:
        """
        Get Filecoin path for training data
        
        Format: {app}/{privacy}/{org_id or user_id}/{agent_type}/
        """
        
        app = app_context.value
        privacy_level = privacy.value
        
        if privacy in [PrivacySchema.PERSONAL, PrivacySchema.PRIVATE]:
            return f"{app}/{privacy_level}/{user_id}/{agent_type}/"
        elif privacy in [PrivacySchema.ORG_PRIVATE, PrivacySchema.ORG_PUBLIC]:
            return f"{app}/{privacy_level}/{org_id}/{agent_type}/"
        else:  # PUBLIC
            return f"{app}/{privacy_level}/public/{agent_type}/"


# ============================================================================
# Model Sharing & Access Control
# ============================================================================

class ModelAccessControl:
    """
    Manages who can access which models
    """
    
    @staticmethod
    def can_access_model(
        requesting_user_id: str,
        requesting_org_id: Optional[str],
        model_owner_id: str,
        model_org_id: Optional[str],
        model_isolation: str,
        model_privacy: PrivacySchema
    ) -> bool:
        """
        Check if user can access a model
        
        Rules:
        - Personal models: Only owner
        - Team models: Anyone in same team
        - Org models: Anyone in same org
        - Public models: Anyone
        """
        
        # Owner always has access
        if requesting_user_id == model_owner_id:
            return True
        
        # Personal models: only owner
        if model_isolation == "personal":
            return False
        
        # Team models: same org required
        if model_isolation == "team":
            return requesting_org_id == model_org_id
        
        # Org models: same org required
        if model_isolation == "org":
            return requesting_org_id == model_org_id
        
        # Public models: everyone
        if model_isolation == "public":
            return True
        
        return False


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example 1: Atlas Personal user
    config = ModelIsolationStrategy.get_model_path(
        user_id="user123",
        org_id=None,
        atlas_tier=AtlasTier.PERSONAL,
        privacy_schema=PrivacySchema.PERSONAL,
        app_context=AppContext.ATLAS,
        agent_type="finance"
    )
    print("Atlas Personal:", config)
    
    # Example 2: Delt Team user
    config = ModelIsolationStrategy.get_model_path(
        user_id="user456",
        org_id="org789",
        atlas_tier=AtlasTier.TEAM,
        privacy_schema=PrivacySchema.ORG_PRIVATE,
        app_context=AppContext.DELT,
        agent_type="finance",
        delt_tier=DeltTier.TEAM
    )
    print("Delt Team:", config)
    
    # Example 3: Akashic (always personal)
    config = ModelIsolationStrategy.get_model_path(
        user_id="user789",
        org_id="org123",
        atlas_tier=AtlasTier.ORGANIZATIONAL,
        privacy_schema=PrivacySchema.ORG_PUBLIC,
        app_context=AppContext.AKASHIC,
        agent_type="development"
    )
    print("Akashic:", config)
