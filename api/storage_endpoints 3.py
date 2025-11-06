"""
Storage API Endpoints - Encrypted File Upload/Download

Provides REST API for:
- Encrypted file uploads to Filecoin
- Encrypted file downloads from Filecoin
- File metadata management
- BYOK credential management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import io
from storage.encrypted_storage import get_encrypted_storage, StoredFile
from security.vault_integration import get_vault_client, ProviderType
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/storage", tags=["storage"])


# Request/Response Models
class UploadRequest(BaseModel):
    """File upload request"""
    user_id: str = Field(..., description="User ID")
    org_id: str = Field(..., description="Organization ID")
    filename: str = Field(..., description="Original filename")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class UploadResponse(BaseModel):
    """File upload response"""
    file_id: str
    cid: str
    size_bytes: int
    content_hash: str
    encrypted: bool = True
    message: str = "File uploaded and encrypted successfully"


class FileMetadata(BaseModel):
    """File metadata response"""
    file_id: str
    cid: str
    size_bytes: int
    content_hash: str
    filename: str
    user_id: str
    org_id: str
    encrypted: bool = True


class BYOKCredentials(BaseModel):
    """BYOK credentials for provider"""
    provider: str = Field(..., description="Provider name (filecoin, theta, jarvislabs)")
    api_key: str
    api_secret: Optional[str] = None
    endpoint: Optional[str] = None
    wallet: Optional[str] = None


class BYOKResponse(BaseModel):
    """BYOK credentials storage response"""
    success: bool
    message: str
    provider: str


# Dependency to get storage
async def get_storage():
    """Get encrypted storage instance"""
    return get_encrypted_storage()


# Dependency to get vault client
async def get_vault():
    """Get vault client instance"""
    return get_vault_client()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Header(...),
    org_id: str = Header(...),
    metadata: Optional[str] = Header(None),
    storage = Depends(get_storage)
):
    """
    Upload and encrypt file to Filecoin
    
    Flow:
    1. Receive file from client
    2. Get credentials from Universal Vault
    3. Encrypt file with user-specific key
    4. Upload encrypted blob to Filecoin
    5. Return file metadata
    
    Headers:
    - user_id: User identifier
    - org_id: Organization identifier
    - metadata: Optional JSON metadata
    
    Returns:
    - file_id: Unique file identifier
    - cid: Filecoin Content ID
    - size_bytes: Original file size
    - content_hash: SHA-256 hash
    """
    try:
        logger.info(f"Upload request: user={user_id}, org={org_id}, file={file.filename}")
        
        # Read file content
        file_data = await file.read()
        
        # Parse metadata if provided
        import json
        file_metadata = json.loads(metadata) if metadata else None
        
        # Upload with encryption
        stored = await storage.upload_file(
            file_data=file_data,
            filename=file.filename,
            user_id=user_id,
            org_id=org_id,
            metadata=file_metadata
        )
        
        logger.info(f"Upload successful: file_id={stored.file_id}, cid={stored.cid}")
        
        return UploadResponse(
            file_id=stored.file_id,
            cid=stored.cid,
            size_bytes=stored.size_bytes,
            content_hash=stored.content_hash
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    user_id: str = Header(...),
    org_id: str = Header(...),
    storage = Depends(get_storage)
):
    """
    Download and decrypt file from Filecoin
    
    Flow:
    1. Retrieve file metadata from database
    2. Get credentials from Universal Vault
    3. Download encrypted blob from Filecoin
    4. Decrypt with user-specific key
    5. Verify content integrity
    6. Return decrypted file
    
    Args:
    - file_id: File identifier
    
    Headers:
    - user_id: User identifier
    - org_id: Organization identifier
    
    Returns:
    - Decrypted file content
    """
    try:
        logger.info(f"Download request: file_id={file_id}, user={user_id}, org={org_id}")
        
        # TODO: Retrieve StoredFile from PostgreSQL
        # For now, this is a placeholder
        # stored = await db.get_stored_file(file_id, user_id, org_id)
        
        raise HTTPException(
            status_code=501,
            detail="Download endpoint requires PostgreSQL integration (coming soon)"
        )
        
        # Download and decrypt
        # decrypted_data = await storage.download_file(stored)
        # filename = await storage.get_filename(stored)
        
        # Return as streaming response
        # return StreamingResponse(
        #     io.BytesIO(decrypted_data),
        #     media_type="application/octet-stream",
        #     headers={"Content-Disposition": f"attachment; filename={filename}"}
        # )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/metadata/{file_id}", response_model=FileMetadata)
async def get_file_metadata(
    file_id: str,
    user_id: str = Header(...),
    org_id: str = Header(...),
    storage = Depends(get_storage)
):
    """
    Get file metadata
    
    Args:
    - file_id: File identifier
    
    Headers:
    - user_id: User identifier
    - org_id: Organization identifier
    
    Returns:
    - File metadata (filename, size, hash, etc.)
    """
    try:
        logger.info(f"Metadata request: file_id={file_id}, user={user_id}, org={org_id}")
        
        # TODO: Retrieve from PostgreSQL
        raise HTTPException(
            status_code=501,
            detail="Metadata endpoint requires PostgreSQL integration (coming soon)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metadata retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metadata retrieval failed: {str(e)}")


@router.post("/byok/credentials", response_model=BYOKResponse)
async def store_byok_credentials(
    credentials: BYOKCredentials,
    user_id: str = Header(...),
    vault = Depends(get_vault)
):
    """
    Store user's BYOK credentials
    
    Allows enterprise users to provide their own provider credentials.
    Credentials are stored encrypted in Universal Vault.
    
    Body:
    - provider: Provider name (filecoin, theta, jarvislabs)
    - api_key: Provider API key
    - api_secret: Optional API secret
    - endpoint: Optional custom endpoint
    - wallet: Optional wallet address (Theta)
    
    Headers:
    - user_id: User identifier
    
    Returns:
    - Success status
    """
    try:
        logger.info(f"BYOK credentials: user={user_id}, provider={credentials.provider}")
        
        # Map provider string to ProviderType
        provider_map = {
            "filecoin": ProviderType.FILECOIN,
            "theta": ProviderType.THETA,
            "jarvislabs": ProviderType.JARVISLABS
        }
        
        if credentials.provider not in provider_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {credentials.provider}"
            )
        
        provider_type = provider_map[credentials.provider]
        
        # Store credentials in vault with user-specific key
        cred_dict = {
            "api_key": credentials.api_key,
        }
        if credentials.api_secret:
            cred_dict["api_secret"] = credentials.api_secret
        if credentials.endpoint:
            cred_dict["endpoint"] = credentials.endpoint
        if credentials.wallet:
            cred_dict["wallet"] = credentials.wallet
        
        # Store with BYOK prefix and user_id
        prefix = f"providers.byok.{provider_type.value}.user_{user_id}"
        for key, value in cred_dict.items():
            await vault.store_system_secret(f"{prefix}.{key}", value)
        
        logger.info(f"BYOK credentials stored: user={user_id}, provider={credentials.provider}")
        
        return BYOKResponse(
            success=True,
            message=f"BYOK credentials stored for {credentials.provider}",
            provider=credentials.provider
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BYOK storage failed: {e}")
        raise HTTPException(status_code=500, detail=f"BYOK storage failed: {str(e)}")


@router.delete("/byok/credentials/{provider}")
async def delete_byok_credentials(
    provider: str,
    user_id: str = Header(...),
    vault = Depends(get_vault)
):
    """
    Delete user's BYOK credentials
    
    Args:
    - provider: Provider name (filecoin, theta, jarvislabs)
    
    Headers:
    - user_id: User identifier
    
    Returns:
    - Success status
    """
    try:
        logger.info(f"Delete BYOK credentials: user={user_id}, provider={provider}")
        
        # TODO: Implement credential deletion in Universal Vault
        raise HTTPException(
            status_code=501,
            detail="BYOK deletion requires Universal Vault delete endpoint (coming soon)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BYOK deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"BYOK deletion failed: {str(e)}")


@router.get("/providers/status")
async def get_provider_status(
    user_id: str = Header(...),
    org_id: str = Header(...),
    vault = Depends(get_vault)
):
    """
    Get status of all providers
    
    Shows which providers are available (shared or BYOK)
    
    Headers:
    - user_id: User identifier
    - org_id: Organization identifier
    
    Returns:
    - Provider status for each provider
    """
    try:
        logger.info(f"Provider status: user={user_id}, org={org_id}")
        
        status = {}
        
        for provider in [ProviderType.FILECOIN, ProviderType.THETA, ProviderType.JARVISLABS]:
            creds = await vault.get_provider_credentials(
                provider,
                user_id=user_id,
                org_id=org_id
            )
            
            if creds:
                status[provider.value] = {
                    "available": True,
                    "mode": creds.mode.value,
                    "namespace": creds.namespace,
                    "endpoint": creds.endpoint
                }
            else:
                status[provider.value] = {
                    "available": False,
                    "mode": None,
                    "namespace": None,
                    "endpoint": None
                }
        
        return status
        
    except Exception as e:
        logger.error(f"Provider status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Provider status failed: {str(e)}")


@router.get("/health")
async def storage_health():
    """
    Health check for storage system
    
    Returns:
    - System status
    """
    return {
        "status": "healthy",
        "encryption": "enabled",
        "providers": ["filecoin", "theta", "jarvislabs"],
        "features": ["encryption", "byok", "multi-tenant"]
    }
