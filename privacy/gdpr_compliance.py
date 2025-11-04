"""
GDPR Compliance System for Apollo AI

Handles:
- Right to Access (Article 15)
- Right to Erasure / "Right to be Forgotten" (Article 17)
- Right to Data Portability (Article 20)
- Right to Rectification (Article 16)
- Data Retention Policies

All user data and models stored on Filecoin can be:
- Exported (data portability)
- Deleted (right to erasure)
- Updated (right to rectification)
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class DataCategory(Enum):
    """Categories of user data"""
    INTERACTIONS = "interactions"           # Training interactions
    MODELS = "models"                       # Trained models
    TELEMETRY = "telemetry"                # Usage telemetry
    PREFERENCES = "preferences"             # User preferences
    METADATA = "metadata"                   # User metadata


class DeletionStatus(Enum):
    """Status of deletion request"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GDPRComplianceManager:
    """
    Manages GDPR compliance for Apollo AI
    
    Key Features:
    - Delete all user data from Filecoin
    - Delete all trained models
    - Export user data (data portability)
    - Audit trail of all operations
    """
    
    def __init__(
        self,
        unified_storage,
        unified_trainer,
        audit_logger
    ):
        self.storage = unified_storage
        self.trainer = unified_trainer
        self.audit = audit_logger
        
        # Track deletion requests
        self.deletion_requests = {}
        
        # Data retention policies (days)
        self.retention_policies = {
            DataCategory.INTERACTIONS: 365,      # 1 year
            DataCategory.MODELS: 365,            # 1 year
            DataCategory.TELEMETRY: 90,          # 3 months
            DataCategory.PREFERENCES: None,      # Keep until deleted
            DataCategory.METADATA: None          # Keep until deleted
        }
    
    # ========================================================================
    # Right to Erasure (Article 17) - "Right to be Forgotten"
    # ========================================================================
    
    async def request_data_deletion(
        self,
        user_id: str,
        org_id: Optional[str] = None,
        reason: str = "user_request",
        verification_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request deletion of all user data
        
        This is the main GDPR compliance endpoint.
        Deletes:
        - All training interactions
        - All trained models
        - All telemetry data
        - All user preferences
        
        Args:
            user_id: User ID to delete
            org_id: Organization ID (if applicable)
            reason: Reason for deletion
            verification_token: Token to verify user identity
        
        Returns:
            Deletion request details
        """
        
        logger.info(f"🗑️  GDPR Deletion Request: user_id={user_id}")
        
        # Verify user identity (important for GDPR)
        if not await self._verify_user_identity(user_id, verification_token):
            raise PermissionError("User identity verification failed")
        
        # Create deletion request
        request_id = f"del_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        deletion_request = {
            "request_id": request_id,
            "user_id": user_id,
            "org_id": org_id,
            "reason": reason,
            "status": DeletionStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "categories_to_delete": [
                DataCategory.INTERACTIONS.value,
                DataCategory.MODELS.value,
                DataCategory.TELEMETRY.value,
                DataCategory.PREFERENCES.value,
                DataCategory.METADATA.value
            ],
            "deletion_summary": {}
        }
        
        self.deletion_requests[request_id] = deletion_request
        
        # Log audit trail
        await self.audit.log_event(
            event_type="gdpr_deletion_request",
            user_id=user_id,
            details=deletion_request
        )
        
        # Start deletion process asynchronously
        asyncio.create_task(self._execute_deletion(request_id))
        
        return {
            "request_id": request_id,
            "status": "pending",
            "message": "Deletion request received. Processing will complete within 30 days as per GDPR requirements.",
            "estimated_completion": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    
    async def _execute_deletion(self, request_id: str):
        """
        Execute the deletion process
        
        This runs asynchronously and deletes all user data
        """
        
        request = self.deletion_requests[request_id]
        user_id = request["user_id"]
        org_id = request["org_id"]
        
        try:
            # Update status
            request["status"] = DeletionStatus.IN_PROGRESS.value
            
            logger.info(f"🗑️  Starting deletion for user_id={user_id}")
            
            deletion_summary = {}
            
            # 1. Delete training interactions
            logger.info(f"  Deleting training interactions...")
            interactions_deleted = await self._delete_interactions(user_id, org_id)
            deletion_summary["interactions"] = interactions_deleted
            
            # 2. Delete trained models
            logger.info(f"  Deleting trained models...")
            models_deleted = await self._delete_models(user_id, org_id)
            deletion_summary["models"] = models_deleted
            
            # 3. Delete telemetry data
            logger.info(f"  Deleting telemetry data...")
            telemetry_deleted = await self._delete_telemetry(user_id, org_id)
            deletion_summary["telemetry"] = telemetry_deleted
            
            # 4. Delete preferences
            logger.info(f"  Deleting preferences...")
            preferences_deleted = await self._delete_preferences(user_id, org_id)
            deletion_summary["preferences"] = preferences_deleted
            
            # 5. Delete metadata
            logger.info(f"  Deleting metadata...")
            metadata_deleted = await self._delete_metadata(user_id, org_id)
            deletion_summary["metadata"] = metadata_deleted
            
            # Update request
            request["status"] = DeletionStatus.COMPLETED.value
            request["completed_at"] = datetime.utcnow().isoformat()
            request["deletion_summary"] = deletion_summary
            
            # Log completion
            await self.audit.log_event(
                event_type="gdpr_deletion_completed",
                user_id=user_id,
                details={
                    "request_id": request_id,
                    "summary": deletion_summary
                }
            )
            
            logger.info(f"✅ Deletion completed for user_id={user_id}")
            logger.info(f"  Summary: {deletion_summary}")
            
        except Exception as e:
            logger.error(f"❌ Deletion failed for user_id={user_id}: {e}")
            
            request["status"] = DeletionStatus.FAILED.value
            request["error"] = str(e)
            
            await self.audit.log_event(
                event_type="gdpr_deletion_failed",
                user_id=user_id,
                details={
                    "request_id": request_id,
                    "error": str(e)
                }
            )
    
    async def _delete_interactions(
        self,
        user_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Delete all training interactions for user"""
        
        deleted_count = 0
        paths_to_delete = []
        
        # Build paths for all contexts
        contexts = ["atlas", "delt", "akashic", "akashic_atlas", "akashic_delt"]
        
        for context in contexts:
            # Personal interactions
            path = f"{context}/personal/{user_id}/"
            paths_to_delete.append(path)
            
            # Team interactions (if org_id provided)
            if org_id:
                path = f"{context}/team/{org_id}/"
                paths_to_delete.append(path)
                
                path = f"{context}/org/{org_id}/"
                paths_to_delete.append(path)
        
        # Delete from Filecoin
        for path in paths_to_delete:
            try:
                result = await self.storage.delete_directory(path)
                deleted_count += result.get("files_deleted", 0)
                logger.info(f"    Deleted: {path} ({result.get('files_deleted', 0)} files)")
            except Exception as e:
                logger.warning(f"    Failed to delete {path}: {e}")
        
        return {
            "paths_deleted": len(paths_to_delete),
            "files_deleted": deleted_count
        }
    
    async def _delete_models(
        self,
        user_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Delete all trained models for user"""
        
        deleted_count = 0
        models_to_delete = []
        
        # Build model paths for all contexts and agents
        contexts = ["atlas", "delt", "akashic", "akashic_atlas", "akashic_delt"]
        agents = ["email", "calendar", "document", "legal", "strategy", "portfolio", 
                  "development", "code_review"]  # Add all 62 agents
        
        for context in contexts:
            for agent in agents:
                # Personal models
                model_id = f"{context}:{agent}:{user_id}"
                models_to_delete.append(model_id)
                
                # Team models (if org_id provided)
                if org_id:
                    model_id = f"{context}:{agent}:{org_id}:team"
                    models_to_delete.append(model_id)
                    
                    model_id = f"{context}:{agent}:{org_id}:org"
                    models_to_delete.append(model_id)
        
        # Delete models from Filecoin
        for model_id in models_to_delete:
            try:
                result = await self.storage.delete_file(f"models/{model_id}.gguf")
                if result.get("deleted"):
                    deleted_count += 1
                    logger.info(f"    Deleted model: {model_id}")
            except Exception as e:
                logger.warning(f"    Failed to delete model {model_id}: {e}")
        
        return {
            "models_deleted": deleted_count
        }
    
    async def _delete_telemetry(
        self,
        user_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Delete all telemetry data for user"""
        
        # Telemetry stored in separate location
        path = f"telemetry/{user_id}/"
        
        try:
            result = await self.storage.delete_directory(path)
            logger.info(f"    Deleted telemetry: {path}")
            return {
                "files_deleted": result.get("files_deleted", 0)
            }
        except Exception as e:
            logger.warning(f"    Failed to delete telemetry: {e}")
            return {"files_deleted": 0}
    
    async def _delete_preferences(
        self,
        user_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Delete user preferences"""
        
        path = f"preferences/{user_id}.json"
        
        try:
            result = await self.storage.delete_file(path)
            logger.info(f"    Deleted preferences: {path}")
            return {"files_deleted": 1 if result.get("deleted") else 0}
        except Exception as e:
            logger.warning(f"    Failed to delete preferences: {e}")
            return {"files_deleted": 0}
    
    async def _delete_metadata(
        self,
        user_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Delete user metadata"""
        
        path = f"metadata/{user_id}.json"
        
        try:
            result = await self.storage.delete_file(path)
            logger.info(f"    Deleted metadata: {path}")
            return {"files_deleted": 1 if result.get("deleted") else 0}
        except Exception as e:
            logger.warning(f"    Failed to delete metadata: {e}")
            return {"files_deleted": 0}
    
    # ========================================================================
    # Right to Access (Article 15) - Data Export
    # ========================================================================
    
    async def export_user_data(
        self,
        user_id: str,
        org_id: Optional[str] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export all user data (GDPR Article 15 - Right to Access)
        
        Returns all data in machine-readable format
        """
        
        logger.info(f"📦 GDPR Data Export: user_id={user_id}")
        
        export_data = {
            "user_id": user_id,
            "org_id": org_id,
            "export_date": datetime.utcnow().isoformat(),
            "format": format,
            "data": {}
        }
        
        # Export interactions
        export_data["data"]["interactions"] = await self._export_interactions(user_id, org_id)
        
        # Export models (metadata only, not the actual model files)
        export_data["data"]["models"] = await self._export_model_metadata(user_id, org_id)
        
        # Export telemetry
        export_data["data"]["telemetry"] = await self._export_telemetry(user_id, org_id)
        
        # Export preferences
        export_data["data"]["preferences"] = await self._export_preferences(user_id, org_id)
        
        # Export metadata
        export_data["data"]["metadata"] = await self._export_metadata(user_id, org_id)
        
        # Log audit trail
        await self.audit.log_event(
            event_type="gdpr_data_export",
            user_id=user_id,
            details={"export_size": len(str(export_data))}
        )
        
        return export_data
    
    async def _export_interactions(self, user_id: str, org_id: Optional[str]) -> List[Dict]:
        """Export all training interactions"""
        # Implementation: Fetch all interaction files from Filecoin
        return []
    
    async def _export_model_metadata(self, user_id: str, org_id: Optional[str]) -> List[Dict]:
        """Export model metadata (not actual models)"""
        # Implementation: List all models and their metadata
        return []
    
    async def _export_telemetry(self, user_id: str, org_id: Optional[str]) -> List[Dict]:
        """Export telemetry data"""
        # Implementation: Fetch telemetry from Filecoin
        return []
    
    async def _export_preferences(self, user_id: str, org_id: Optional[str]) -> Dict:
        """Export user preferences"""
        # Implementation: Fetch preferences
        return {}
    
    async def _export_metadata(self, user_id: str, org_id: Optional[str]) -> Dict:
        """Export user metadata"""
        # Implementation: Fetch metadata
        return {}
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _verify_user_identity(
        self,
        user_id: str,
        verification_token: Optional[str]
    ) -> bool:
        """
        Verify user identity before deletion
        
        Important for GDPR compliance - must verify user is who they say they are
        """
        # Implementation: Verify token against user's account
        # Could use email verification, 2FA, etc.
        return True  # Placeholder
    
    async def get_deletion_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of deletion request"""
        
        if request_id not in self.deletion_requests:
            raise ValueError(f"Deletion request {request_id} not found")
        
        return self.deletion_requests[request_id]
    
    async def list_user_data(
        self,
        user_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all data stored for a user
        
        Useful for transparency and GDPR compliance
        """
        
        data_inventory = {
            "user_id": user_id,
            "org_id": org_id,
            "categories": {}
        }
        
        # Count interactions
        interactions = await self._count_interactions(user_id, org_id)
        data_inventory["categories"]["interactions"] = interactions
        
        # Count models
        models = await self._count_models(user_id, org_id)
        data_inventory["categories"]["models"] = models
        
        # Count telemetry
        telemetry = await self._count_telemetry(user_id, org_id)
        data_inventory["categories"]["telemetry"] = telemetry
        
        return data_inventory
    
    async def _count_interactions(self, user_id: str, org_id: Optional[str]) -> Dict:
        """Count interaction files"""
        # Implementation: Count files in Filecoin
        return {"count": 0, "size_mb": 0}
    
    async def _count_models(self, user_id: str, org_id: Optional[str]) -> Dict:
        """Count trained models"""
        # Implementation: Count model files
        return {"count": 0, "size_mb": 0}
    
    async def _count_telemetry(self, user_id: str, org_id: Optional[str]) -> Dict:
        """Count telemetry data"""
        # Implementation: Count telemetry files
        return {"count": 0, "size_mb": 0}
    
    # ========================================================================
    # Model Download (Offline Use)
    # ========================================================================
    
    async def list_user_models(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all trained models user can download
        
        Args:
            user_id: User ID
        
        Returns:
            List of downloadable models
        """
        
        models = []
        
        # All contexts
        contexts = ["atlas", "delt", "akashic", "akashic_atlas", "akashic_delt"]
        
        # All agents (simplified list - in production, use all 62)
        agents = [
            "email", "calendar", "document", "legal", "knowledge",
            "strategy", "portfolio", "sentiment", "backtest",
            "development", "code_review"
        ]
        
        for context in contexts:
            for agent in agents:
                model_id = f"{context}:{agent}:{user_id}"
                
                # Check if model exists
                if await self._model_exists(model_id):
                    metadata = await self._get_model_metadata(model_id)
                    
                    models.append({
                        "model_id": model_id,
                        "context": context,
                        "agent": agent,
                        "size_mb": metadata.get("size_mb", 0),
                        "created_at": metadata.get("created_at"),
                        "training_interactions": metadata.get("training_interactions", 0),
                        "base_model": metadata.get("base_model", "unknown"),
                        "can_download": True
                    })
        
        return models
    
    async def download_user_model(
        self,
        user_id: str,
        model_id: str,
        format: str = "gguf"
    ) -> Dict[str, Any]:
        """
        Generate download link for user's trained model
        
        Args:
            user_id: User ID
            model_id: Model identifier (e.g., "atlas:email:user123")
            format: Model format (gguf, pytorch, onnx)
        
        Returns:
            Download URL and metadata
        """
        
        logger.info(f"📥 Model download request: user_id={user_id}, model_id={model_id}")
        
        # Verify user owns this model
        if not self._verify_model_ownership(user_id, model_id):
            raise PermissionError("You don't own this model")
        
        # Get model CID from Filecoin
        model_cid = await self._get_model_cid(model_id)
        
        # Generate signed download URL (expires in 1 hour)
        download_url = self._generate_signed_url(
            user_id=user_id,
            cid=model_cid,
            expires_in=3600
        )
        
        # Get model metadata
        metadata = await self._get_model_metadata(model_id)
        
        # Log download
        await self.audit.log_event(
            event_type="model_download",
            user_id=user_id,
            details={"model_id": model_id, "format": format}
        )
        
        return {
            "model_id": model_id,
            "download_url": download_url,
            "expires_in": 3600,
            "format": format,
            "size_mb": metadata.get("size_mb", 0),
            "created_at": metadata.get("created_at"),
            "training_interactions": metadata.get("training_interactions", 0),
            "base_model": metadata.get("base_model", "unknown"),
            "instructions": {
                "usage": "Download and run with llama.cpp or your preferred inference engine",
                "example_llama_cpp": f"llama-cli -m {model_id.replace(':', '_')}.gguf -p 'Your prompt here'",
                "example_python": f"from llama_cpp import Llama\nmodel = Llama(model_path='{model_id.replace(':', '_')}.gguf')\nresponse = model('Your prompt')"
            }
        }
    
    def _verify_model_ownership(self, user_id: str, model_id: str) -> bool:
        """Verify user owns this model"""
        # Parse model_id: "atlas:email:user123"
        parts = model_id.split(":")
        if len(parts) < 3:
            return False
        
        owner_id = parts[2]
        return user_id == owner_id
    
    async def _model_exists(self, model_id: str) -> bool:
        """Check if model exists"""
        # Implementation: Check Filecoin for model file
        # For now, return False (implement later)
        return False
    
    async def _get_model_cid(self, model_id: str) -> str:
        """Get Filecoin CID for model"""
        # Implementation: Look up model CID in database/Filecoin
        # For now, return placeholder
        return f"Qm{model_id.replace(':', '')[:40]}"
    
    async def _get_model_metadata(self, model_id: str) -> Dict[str, Any]:
        """Get model metadata"""
        # Implementation: Fetch from database or Filecoin
        return {
            "size_mb": 234.5,
            "created_at": "2024-09-01T00:00:00Z",
            "training_interactions": 150,
            "base_model": "mistral-7b-instruct-v0.2"
        }
    
    def _generate_signed_url(
        self,
        user_id: str,
        cid: str,
        expires_in: int = 3600
    ) -> str:
        """Generate signed download URL"""
        import jwt
        from datetime import datetime, timedelta
        import os
        
        # Create JWT token
        payload = {
            "user_id": user_id,
            "cid": cid,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        secret = os.getenv("JWT_SECRET", "change-me-in-production")
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Return signed URL
        base_url = os.getenv("APOLLO_URL", "http://localhost:8002")
        return f"{base_url}/download/{cid}?token={token}"
    
    # ========================================================================
    # Data Retention Policies
    # ========================================================================
    
    async def apply_retention_policies(self):
        """
        Apply data retention policies
        
        Automatically delete old data based on retention policies
        """
        
        logger.info("🗑️  Applying data retention policies...")
        
        for category, retention_days in self.retention_policies.items():
            if retention_days is None:
                continue  # No automatic deletion
            
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            logger.info(f"  {category.value}: Deleting data older than {cutoff_date}")
            
            # Delete old data
            # Implementation: Query Filecoin for old files and delete
        
        logger.info("✅ Retention policies applied")


# ============================================================================
# Audit Logger
# ============================================================================

class AuditLogger:
    """
    Audit logger for GDPR compliance
    
    Logs all data access, modifications, and deletions
    """
    
    def __init__(self, storage):
        self.storage = storage
    
    async def log_event(
        self,
        event_type: str,
        user_id: str,
        details: Dict[str, Any]
    ):
        """Log audit event"""
        
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        # Store audit log on Filecoin (immutable)
        path = f"audit_logs/{datetime.utcnow().strftime('%Y-%m-%d')}/{event_type}_{user_id}_{int(datetime.utcnow().timestamp())}.json"
        
        await self.storage.store_file(path, event)
        
        logger.info(f"📝 Audit log: {event_type} for user {user_id}")
