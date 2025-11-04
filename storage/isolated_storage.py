"""
Isolated Storage Manager - Multi-tenant storage with privacy isolation

Handles storage for:
1. Atlas (Personal, Individual, Team, Organizational)
2. Delt (Individual, Team)
3. Akashic (always Personal)

Privacy levels:
- Personal: Only user
- Private: User + explicit shares
- Org Private: Team only
- Org Public: Organization
- Public: Everyone
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import logging

from config.model_config import (
    PrivacySchema, AppContext, AtlasTier, DeltTier,
    TrainingDataIsolation, ModelAccessControl,
    ModelIsolationStrategy
)

logger = logging.getLogger(__name__)


class IsolatedStorageManager:
    """
    Manages storage with proper isolation based on privacy settings
    
    Storage Structure on Filecoin:
    /atlas/
        /personal/{user_id}/{agent_type}/
            /models/
            /training_data/
        /team/{org_id}/{team_id}/{agent_type}/
            /models/
            /training_data/
        /org/{org_id}/{agent_type}/
            /models/
            /training_data/
        /public/{agent_type}/
            /models/
            /training_data/
    
    /delt/
        /individual/{user_id}/{agent_type}/
        /team/{org_id}/{team_id}/{agent_type}/
    
    /akashic/
        /personal/{user_id}/{agent_type}/
    """
    
    def __init__(self, filecoin_client, web3_storage_token: str):
        """
        Initialize isolated storage manager
        
        Args:
            filecoin_client: FilecoinClient instance
            web3_storage_token: Web3.Storage API token
        """
        self.filecoin = filecoin_client
        self.token = web3_storage_token
        self.cache_dir = Path("./cache/isolated_storage")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # Training Data Storage with Isolation
    # ========================================================================
    
    async def store_training_data(
        self,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        interactions: List[Dict[str, Any]],
        privacy: PrivacySchema,
        atlas_tier: Optional[AtlasTier] = None,
        delt_tier: Optional[DeltTier] = None
    ) -> Dict[str, Any]:
        """
        Store training data with proper isolation
        
        Returns:
            {
                "cid": "Qm...",
                "path": "atlas/personal/user123/finance/",
                "privacy": "personal",
                "can_share": false
            }
        """
        
        # Get storage path based on privacy and tier
        storage_path = self._get_storage_path(
            user_id, org_id, team_id, app_context, agent_type,
            privacy, atlas_tier, delt_tier
        )
        
        # Check if data can be stored at this privacy level
        isolation = ModelIsolationStrategy._determine_isolation(
            atlas_tier or AtlasTier.PERSONAL,
            privacy,
            app_context,
            delt_tier
        )
        
        # Create training data file
        training_data = {
            "user_id": user_id,
            "org_id": org_id,
            "team_id": team_id,
            "app_context": app_context.value,
            "agent_type": agent_type,
            "privacy": privacy.value,
            "isolation_level": isolation["level"],
            "interactions": interactions,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # Save to temp file
        temp_file = self.cache_dir / f"training_{user_id}_{agent_type}_{datetime.now().timestamp()}.jsonl"
        with open(temp_file, 'w') as f:
            for interaction in interactions:
                f.write(json.dumps(interaction) + '\n')
        
        # Upload to Filecoin
        cid = await self.filecoin.upload_training_data(
            user_id=user_id,
            data_type=f"{storage_path}/training_data",
            data=interactions,
            version="latest"
        )
        
        # Store metadata
        metadata = {
            "cid": cid,
            "path": storage_path,
            "privacy": privacy.value,
            "isolation_level": isolation["level"],
            "can_share": isolation["can_share"],
            "interaction_count": len(interactions),
            "created_at": datetime.now().isoformat()
        }
        
        await self._store_metadata(
            f"{storage_path}/training_data",
            metadata
        )
        
        # Cleanup
        temp_file.unlink()
        
        logger.info(f"✅ Stored training data: {storage_path} (CID: {cid})")
        
        return metadata
    
    async def retrieve_training_data(
        self,
        requesting_user_id: str,
        requesting_org_id: Optional[str],
        target_user_id: str,
        target_org_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        privacy: PrivacySchema
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve training data with access control
        
        Returns:
            Training data if user has access, None otherwise
        """
        
        # Check access
        storage_path = self._get_storage_path(
            target_user_id, target_org_id, None, app_context, agent_type,
            privacy, None, None
        )
        
        metadata = await self._get_metadata(f"{storage_path}/training_data")
        if not metadata:
            logger.warning(f"Training data not found: {storage_path}")
            return None
        
        # Verify access
        can_access = ModelAccessControl.can_access_model(
            requesting_user_id=requesting_user_id,
            requesting_org_id=requesting_org_id,
            model_owner_id=target_user_id,
            model_org_id=target_org_id,
            model_isolation=metadata["isolation_level"],
            model_privacy=privacy
        )
        
        if not can_access:
            logger.warning(f"Access denied: {requesting_user_id} cannot access {storage_path}")
            return None
        
        # Download from Filecoin
        cid = metadata["cid"]
        data = await self.filecoin.download_training_data(
            user_id=target_user_id,
            data_type=f"{storage_path}/training_data",
            version="latest"
        )
        
        logger.info(f"✅ Retrieved training data: {storage_path}")
        return data
    
    # ========================================================================
    # Model Storage with Isolation
    # ========================================================================
    
    async def store_model(
        self,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        model_path: str,
        base_model: str,
        privacy: PrivacySchema,
        training_metadata: Dict[str, Any],
        atlas_tier: Optional[AtlasTier] = None,
        delt_tier: Optional[DeltTier] = None
    ) -> Dict[str, Any]:
        """
        Store fine-tuned model with proper isolation
        
        Returns:
            {
                "cid": "Qm...",
                "path": "atlas/personal/user123/finance/models/",
                "privacy": "personal",
                "can_share": false,
                "model_id": "atlas:finance:user123"
            }
        """
        
        # Get storage path
        storage_path = self._get_storage_path(
            user_id, org_id, team_id, app_context, agent_type,
            privacy, atlas_tier, delt_tier
        )
        
        # Get isolation level
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
        
        # Upload model to Filecoin
        cid = await self.filecoin.upload_fine_tuned_model(
            user_id=user_id,
            model_name=f"{storage_path}/models/{agent_type}",
            model_path=model_path,
            base_model=base_model,
            training_metadata=training_metadata
        )
        
        # Store metadata
        metadata = {
            "cid": cid,
            "path": storage_path,
            "model_id": model_id,
            "base_model": base_model,
            "privacy": privacy.value,
            "isolation_level": isolation["level"],
            "can_share": isolation["can_share"],
            "training_metadata": training_metadata,
            "created_at": datetime.now().isoformat()
        }
        
        await self._store_metadata(
            f"{storage_path}/models/{agent_type}",
            metadata
        )
        
        logger.info(f"✅ Stored model: {model_id} (CID: {cid})")
        
        return metadata
    
    async def retrieve_model(
        self,
        requesting_user_id: str,
        requesting_org_id: Optional[str],
        target_user_id: str,
        target_org_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        privacy: PrivacySchema
    ) -> Optional[str]:
        """
        Retrieve model with access control
        
        Returns:
            Local path to model if user has access, None otherwise
        """
        
        # Get storage path
        storage_path = self._get_storage_path(
            target_user_id, target_org_id, None, app_context, agent_type,
            privacy, None, None
        )
        
        # Get metadata
        metadata = await self._get_metadata(f"{storage_path}/models/{agent_type}")
        if not metadata:
            logger.warning(f"Model not found: {storage_path}")
            return None
        
        # Check access
        can_access = ModelAccessControl.can_access_model(
            requesting_user_id=requesting_user_id,
            requesting_org_id=requesting_org_id,
            model_owner_id=target_user_id,
            model_org_id=target_org_id,
            model_isolation=metadata["isolation_level"],
            model_privacy=privacy
        )
        
        if not can_access:
            logger.warning(f"Access denied: {requesting_user_id} cannot access {storage_path}")
            return None
        
        # Download model
        model_path = await self.filecoin.download_fine_tuned_model(
            user_id=target_user_id,
            model_name=f"{storage_path}/models/{agent_type}"
        )
        
        logger.info(f"✅ Retrieved model: {storage_path}")
        return model_path
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _get_storage_path(
        self,
        user_id: str,
        org_id: Optional[str],
        team_id: Optional[str],
        app_context: AppContext,
        agent_type: str,
        privacy: PrivacySchema,
        atlas_tier: Optional[AtlasTier],
        delt_tier: Optional[DeltTier]
    ) -> str:
        """
        Build storage path based on isolation level
        
        Examples:
        - atlas/personal/user123/finance
        - atlas/team/org456/team789/finance
        - delt/individual/user123/trading
        - akashic/personal/user123/development
        """
        
        app = app_context.value
        
        # Determine isolation level
        if app_context == AppContext.AKASHIC:
            # Akashic is always personal
            return f"{app}/personal/{user_id}/{agent_type}"
        
        elif app_context == AppContext.DELT:
            if delt_tier == DeltTier.INDIVIDUAL:
                return f"{app}/individual/{user_id}/{agent_type}"
            elif delt_tier == DeltTier.TEAM:
                return f"{app}/team/{org_id}/{team_id or 'default'}/{agent_type}"
        
        elif app_context == AppContext.ATLAS:
            if privacy in [PrivacySchema.PERSONAL, PrivacySchema.PRIVATE]:
                return f"{app}/personal/{user_id}/{agent_type}"
            elif privacy == PrivacySchema.ORG_PRIVATE:
                return f"{app}/team/{org_id}/{team_id or 'default'}/{agent_type}"
            elif privacy == PrivacySchema.ORG_PUBLIC:
                return f"{app}/org/{org_id}/{agent_type}"
            elif privacy == PrivacySchema.PUBLIC:
                return f"{app}/public/{agent_type}"
        
        # Default: personal
        return f"{app}/personal/{user_id}/{agent_type}"
    
    async def _store_metadata(self, key: str, metadata: Dict[str, Any]):
        """Store metadata locally (would be PostgreSQL in production)"""
        metadata_dir = self.cache_dir / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_file = metadata_dir / f"{key.replace('/', '_')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    async def _get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata from local storage"""
        metadata_dir = self.cache_dir / "metadata"
        metadata_file = metadata_dir / f"{key.replace('/', '_')}.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    # ========================================================================
    # Sharing & Access Management
    # ========================================================================
    
    async def share_model(
        self,
        owner_user_id: str,
        owner_org_id: Optional[str],
        target_user_id: str,
        app_context: AppContext,
        agent_type: str,
        permission: str = "read"
    ) -> bool:
        """
        Share model with another user
        
        Args:
            owner_user_id: Model owner
            owner_org_id: Owner's organization
            target_user_id: User to share with
            app_context: Application context
            agent_type: Agent type
            permission: "read" or "write"
        
        Returns:
            True if shared successfully
        """
        
        # Get model metadata
        storage_path = self._get_storage_path(
            owner_user_id, owner_org_id, None, app_context, agent_type,
            PrivacySchema.PRIVATE, None, None
        )
        
        metadata = await self._get_metadata(f"{storage_path}/models/{agent_type}")
        if not metadata:
            logger.error(f"Model not found: {storage_path}")
            return False
        
        # Check if model can be shared
        if not metadata.get("can_share", False):
            logger.error(f"Model cannot be shared: {storage_path}")
            return False
        
        # Add to shared list
        if "shared_with" not in metadata:
            metadata["shared_with"] = []
        
        metadata["shared_with"].append({
            "user_id": target_user_id,
            "permission": permission,
            "shared_at": datetime.now().isoformat()
        })
        
        # Update metadata
        await self._store_metadata(f"{storage_path}/models/{agent_type}", metadata)
        
        logger.info(f"✅ Shared model {storage_path} with {target_user_id}")
        return True
    
    async def list_accessible_models(
        self,
        user_id: str,
        org_id: Optional[str],
        app_context: AppContext
    ) -> List[Dict[str, Any]]:
        """
        List all models accessible to user
        
        Returns:
            List of model metadata
        """
        
        accessible_models = []
        metadata_dir = self.cache_dir / "metadata"
        
        if not metadata_dir.exists():
            return []
        
        for metadata_file in metadata_dir.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check if user can access
            can_access = ModelAccessControl.can_access_model(
                requesting_user_id=user_id,
                requesting_org_id=org_id,
                model_owner_id=metadata.get("user_id", ""),
                model_org_id=metadata.get("org_id"),
                model_isolation=metadata.get("isolation_level", "personal"),
                model_privacy=PrivacySchema(metadata.get("privacy", "personal"))
            )
            
            if can_access:
                accessible_models.append(metadata)
        
        return accessible_models


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import asyncio
    from .filecoin_client import FilecoinClient
    
    async def main():
        # Initialize
        filecoin = FilecoinClient(api_token="your_token")
        storage = IsolatedStorageManager(filecoin, "your_token")
        
        # Example 1: Store personal training data (Atlas Personal)
        await storage.store_training_data(
            user_id="user123",
            org_id=None,
            team_id=None,
            app_context=AppContext.ATLAS,
            agent_type="finance",
            interactions=[{"query": "...", "response": "..."}],
            privacy=PrivacySchema.PERSONAL,
            atlas_tier=AtlasTier.PERSONAL
        )
        
        # Example 2: Store team model (Delt Team)
        await storage.store_model(
            user_id="user456",
            org_id="org789",
            team_id="team123",
            app_context=AppContext.DELT,
            agent_type="trading",
            model_path="/path/to/model.gguf",
            base_model="deepseek-coder-6.7b",
            privacy=PrivacySchema.ORG_PRIVATE,
            training_metadata={"epochs": 3, "loss": 0.05},
            delt_tier=DeltTier.TEAM
        )
        
        print("✅ Examples complete!")
    
    asyncio.run(main())
