"""
Hierarchical Model Training System

Trains models in layers based on organizational structure:
- Org-wide knowledge (policies, templates, standards)
- Role-based knowledge (job-specific patterns)
- Team knowledge (team communication patterns)
- Personal knowledge (individual style)

Flexible hierarchy based on organization structure:
- Traditional: Org → Department → Team → Individual
- Flat: Org → Role → Team → Individual
- Custom: Any hierarchy defined by organization
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class OrganizationStructure(Enum):
    """Types of organizational structures"""
    TRADITIONAL = "traditional"  # Org → Dept → Team → Individual
    FLAT = "flat"                # Org → Role → Team → Individual
    MATRIX = "matrix"            # Org → Role + Team → Individual
    CUSTOM = "custom"            # User-defined hierarchy


class ModelLayer(Enum):
    """Layers in model hierarchy"""
    BASE = "base"                # Base LLM (e.g., Mistral-7B)
    ORG = "org"                  # Organization-wide
    DEPARTMENT = "department"    # Department-level
    ROLE = "role"                # Role-based
    TEAM = "team"                # Team-level
    PERSONAL = "personal"        # Individual


class HierarchicalTrainer:
    """
    Trains models hierarchically based on organizational structure
    
    Key Features:
    - Flexible hierarchy (traditional, flat, matrix, custom)
    - Incremental training (each layer builds on previous)
    - Model lineage tracking
    - Automatic parent model selection
    - Training data aggregation
    """
    
    def __init__(
        self,
        unified_trainer,
        storage_manager,
        default_structure: OrganizationStructure = OrganizationStructure.FLAT
    ):
        self.trainer = unified_trainer
        self.storage = storage_manager
        self.default_structure = default_structure
        
        # Track model lineage
        self.model_lineage = {}
        
        logger.info("🏗️  Hierarchical Trainer initialized")
        logger.info(f"  Default structure: {default_structure.value}")
    
    # ========================================================================
    # Main Training Methods
    # ========================================================================
    
    async def train_personal_model(
        self,
        user_id: str,
        org_id: str,
        agent_type: str,
        app_context: str = "atlas",
        team_id: Optional[str] = None,
        role: Optional[str] = None,
        department: Optional[str] = None,
        org_structure: Optional[OrganizationStructure] = None
    ) -> Dict[str, Any]:
        """
        Train personal model with organizational context
        
        This is the main entry point for hierarchical training.
        Automatically trains parent models if they don't exist.
        
        Args:
            user_id: User ID
            org_id: Organization ID
            agent_type: Agent type (email, calendar, etc.)
            app_context: Application context (atlas, delt, etc.)
            team_id: Team ID (optional)
            role: User's role (optional, e.g., "sales_rep", "engineer")
            department: Department (optional, e.g., "sales", "engineering")
            org_structure: Organization structure type
        
        Returns:
            Training result with model lineage
        """
        
        logger.info(f"🏗️  Starting hierarchical training")
        logger.info(f"  User: {user_id}")
        logger.info(f"  Org: {org_id}")
        logger.info(f"  Agent: {agent_type}")
        logger.info(f"  Context: {app_context}")
        
        structure = org_structure or self.default_structure
        
        # Build training hierarchy based on org structure
        hierarchy = self._build_hierarchy(
            structure=structure,
            user_id=user_id,
            org_id=org_id,
            team_id=team_id,
            role=role,
            department=department,
            agent_type=agent_type,
            app_context=app_context
        )
        
        logger.info(f"  Hierarchy: {' → '.join([h['layer'].value for h in hierarchy])}")
        
        # Train each layer in sequence
        current_base = None
        trained_models = []
        
        for layer_config in hierarchy:
            layer = layer_config["layer"]
            model_id = layer_config["model_id"]
            
            logger.info(f"  Training {layer.value} layer: {model_id}")
            
            # Check if model already exists
            if await self._model_exists(model_id):
                logger.info(f"    ✓ Model exists, skipping")
                current_base = model_id
                trained_models.append({
                    "layer": layer.value,
                    "model_id": model_id,
                    "status": "exists"
                })
                continue
            
            # Get training data for this layer
            training_data = await self._get_training_data(layer_config)
            
            if not training_data or len(training_data) < 10:
                logger.warning(f"    ⚠️  Insufficient data ({len(training_data) if training_data else 0} interactions), skipping")
                continue
            
            # Train model
            result = await self._train_layer(
                model_id=model_id,
                base_model=current_base or "mistral-7b-instruct-v0.2",
                training_data=training_data,
                layer=layer
            )
            
            # Update base for next layer
            current_base = model_id
            
            trained_models.append({
                "layer": layer.value,
                "model_id": model_id,
                "status": "trained",
                "interactions": len(training_data),
                "result": result
            })
        
        # Store model lineage
        personal_model_id = hierarchy[-1]["model_id"]
        lineage = [h["model_id"] for h in hierarchy]
        
        await self._store_lineage(personal_model_id, lineage)
        
        logger.info(f"✅ Hierarchical training complete")
        logger.info(f"  Final model: {personal_model_id}")
        logger.info(f"  Lineage: {' → '.join(lineage)}")
        
        return {
            "personal_model_id": personal_model_id,
            "lineage": lineage,
            "trained_models": trained_models,
            "structure": structure.value
        }
    
    # ========================================================================
    # Hierarchy Building
    # ========================================================================
    
    def _build_hierarchy(
        self,
        structure: OrganizationStructure,
        user_id: str,
        org_id: str,
        agent_type: str,
        app_context: str,
        team_id: Optional[str] = None,
        role: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Build training hierarchy based on organizational structure
        
        Returns list of layers to train, in order
        """
        
        if structure == OrganizationStructure.TRADITIONAL:
            return self._build_traditional_hierarchy(
                user_id, org_id, agent_type, app_context, team_id, department
            )
        
        elif structure == OrganizationStructure.FLAT:
            return self._build_flat_hierarchy(
                user_id, org_id, agent_type, app_context, team_id, role
            )
        
        elif structure == OrganizationStructure.MATRIX:
            return self._build_matrix_hierarchy(
                user_id, org_id, agent_type, app_context, team_id, role
            )
        
        else:  # CUSTOM
            return self._build_custom_hierarchy(
                user_id, org_id, agent_type, app_context, team_id, role, department
            )
    
    def _build_traditional_hierarchy(
        self,
        user_id: str,
        org_id: str,
        agent_type: str,
        app_context: str,
        team_id: Optional[str],
        department: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Traditional hierarchy: Org → Department → Team → Individual
        
        Example: BigCorp → Sales Dept → West Coast Team → John
        """
        
        hierarchy = [
            {
                "layer": ModelLayer.ORG,
                "model_id": f"{app_context}:{agent_type}:{org_id}:org",
                "org_id": org_id,
                "scope": "org"
            }
        ]
        
        if department:
            hierarchy.append({
                "layer": ModelLayer.DEPARTMENT,
                "model_id": f"{app_context}:{agent_type}:{org_id}:dept:{department}",
                "org_id": org_id,
                "department": department,
                "scope": "department"
            })
        
        if team_id:
            hierarchy.append({
                "layer": ModelLayer.TEAM,
                "model_id": f"{app_context}:{agent_type}:{org_id}:team:{team_id}",
                "org_id": org_id,
                "team_id": team_id,
                "scope": "team"
            })
        
        hierarchy.append({
            "layer": ModelLayer.PERSONAL,
            "model_id": f"{app_context}:{agent_type}:{user_id}",
            "user_id": user_id,
            "scope": "personal"
        })
        
        return hierarchy
    
    def _build_flat_hierarchy(
        self,
        user_id: str,
        org_id: str,
        agent_type: str,
        app_context: str,
        team_id: Optional[str],
        role: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Flat hierarchy: Org → Role → Team → Individual
        
        Example: Startup → Engineer → Backend Team → Sarah
        
        In flat orgs, role is more important than department
        """
        
        hierarchy = [
            {
                "layer": ModelLayer.ORG,
                "model_id": f"{app_context}:{agent_type}:{org_id}:org",
                "org_id": org_id,
                "scope": "org"
            }
        ]
        
        if role:
            hierarchy.append({
                "layer": ModelLayer.ROLE,
                "model_id": f"{app_context}:{agent_type}:{org_id}:role:{role}",
                "org_id": org_id,
                "role": role,
                "scope": "role"
            })
        
        if team_id:
            hierarchy.append({
                "layer": ModelLayer.TEAM,
                "model_id": f"{app_context}:{agent_type}:{org_id}:team:{team_id}",
                "org_id": org_id,
                "team_id": team_id,
                "scope": "team"
            })
        
        hierarchy.append({
            "layer": ModelLayer.PERSONAL,
            "model_id": f"{app_context}:{agent_type}:{user_id}",
            "user_id": user_id,
            "scope": "personal"
        })
        
        return hierarchy
    
    def _build_matrix_hierarchy(
        self,
        user_id: str,
        org_id: str,
        agent_type: str,
        app_context: str,
        team_id: Optional[str],
        role: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Matrix hierarchy: Org → (Role + Team) → Individual
        
        Example: Company → (Product Manager + Mobile Team) → Alex
        
        In matrix orgs, employees have both role and team context
        """
        
        hierarchy = [
            {
                "layer": ModelLayer.ORG,
                "model_id": f"{app_context}:{agent_type}:{org_id}:org",
                "org_id": org_id,
                "scope": "org"
            }
        ]
        
        # Both role and team at same level
        if role:
            hierarchy.append({
                "layer": ModelLayer.ROLE,
                "model_id": f"{app_context}:{agent_type}:{org_id}:role:{role}",
                "org_id": org_id,
                "role": role,
                "scope": "role"
            })
        
        if team_id:
            # Matrix: combine role + team
            if role:
                model_id = f"{app_context}:{agent_type}:{org_id}:matrix:{role}:{team_id}"
            else:
                model_id = f"{app_context}:{agent_type}:{org_id}:team:{team_id}"
            
            hierarchy.append({
                "layer": ModelLayer.TEAM,
                "model_id": model_id,
                "org_id": org_id,
                "team_id": team_id,
                "role": role,
                "scope": "team"
            })
        
        hierarchy.append({
            "layer": ModelLayer.PERSONAL,
            "model_id": f"{app_context}:{agent_type}:{user_id}",
            "user_id": user_id,
            "scope": "personal"
        })
        
        return hierarchy
    
    def _build_custom_hierarchy(
        self,
        user_id: str,
        org_id: str,
        agent_type: str,
        app_context: str,
        team_id: Optional[str],
        role: Optional[str],
        department: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Custom hierarchy: Organization defines their own structure
        
        For now, use all available layers
        """
        
        hierarchy = [
            {
                "layer": ModelLayer.ORG,
                "model_id": f"{app_context}:{agent_type}:{org_id}:org",
                "org_id": org_id,
                "scope": "org"
            }
        ]
        
        if department:
            hierarchy.append({
                "layer": ModelLayer.DEPARTMENT,
                "model_id": f"{app_context}:{agent_type}:{org_id}:dept:{department}",
                "org_id": org_id,
                "department": department,
                "scope": "department"
            })
        
        if role:
            hierarchy.append({
                "layer": ModelLayer.ROLE,
                "model_id": f"{app_context}:{agent_type}:{org_id}:role:{role}",
                "org_id": org_id,
                "role": role,
                "scope": "role"
            })
        
        if team_id:
            hierarchy.append({
                "layer": ModelLayer.TEAM,
                "model_id": f"{app_context}:{agent_type}:{org_id}:team:{team_id}",
                "org_id": org_id,
                "team_id": team_id,
                "scope": "team"
            })
        
        hierarchy.append({
            "layer": ModelLayer.PERSONAL,
            "model_id": f"{app_context}:{agent_type}:{user_id}",
            "user_id": user_id,
            "scope": "personal"
        })
        
        return hierarchy
    
    # ========================================================================
    # Training Data Collection
    # ========================================================================
    
    async def _get_training_data(self, layer_config: Dict[str, Any]) -> List[Dict]:
        """Get training data for a specific layer"""
        
        layer = layer_config["layer"]
        scope = layer_config["scope"]
        
        # Implementation: Fetch interactions from storage based on scope
        # For now, return empty list (implement later)
        
        logger.info(f"    Fetching {scope} training data...")
        
        return []  # Placeholder
    
    # ========================================================================
    # Model Training
    # ========================================================================
    
    async def _train_layer(
        self,
        model_id: str,
        base_model: str,
        training_data: List[Dict],
        layer: ModelLayer
    ) -> Dict[str, Any]:
        """Train a single layer"""
        
        logger.info(f"    Training {layer.value} model...")
        logger.info(f"      Base: {base_model}")
        logger.info(f"      Data: {len(training_data)} interactions")
        
        # Submit training job
        result = await self.trainer.submit_training(
            model_id=model_id,
            base_model=base_model,
            training_data=training_data,
            hyperparameters={
                "epochs": 3,
                "learning_rate": 2e-5,
                "batch_size": 4
            }
        )
        
        return result
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _model_exists(self, model_id: str) -> bool:
        """Check if model already exists"""
        # Implementation: Check storage for model
        return False  # Placeholder
    
    async def _store_lineage(self, model_id: str, lineage: List[str]):
        """Store model lineage for tracking"""
        self.model_lineage[model_id] = {
            "lineage": lineage,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Also store in persistent storage
        await self.storage.store_metadata(model_id, {
            "lineage": lineage,
            "created_at": datetime.utcnow().isoformat()
        })
    
    async def get_model_lineage(self, model_id: str) -> List[str]:
        """Get lineage for a model"""
        if model_id in self.model_lineage:
            return self.model_lineage[model_id]["lineage"]
        
        # Fetch from storage
        metadata = await self.storage.get_metadata(model_id)
        return metadata.get("lineage", [model_id])
