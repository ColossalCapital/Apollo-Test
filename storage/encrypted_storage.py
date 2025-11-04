"""
Encrypted Storage Module - Filecoin with Client-Side Encryption

Combines:
- Client-side encryption (security/encryption.py)
- Universal Vault credentials (security/vault_integration.py)
- Filecoin storage (Storacha API)

Flow:
    1. Get credentials from Universal Vault
    2. Encrypt data with user-specific key
    3. Upload encrypted blob to Filecoin
    4. Store metadata (CID, key_id) in PostgreSQL
"""

import httpx
from typing import Dict, Any, Optional, BinaryIO
from dataclasses import dataclass
import asyncio
from security.encryption import get_encryption_manager, EncryptedData
from security.vault_integration import get_vault_client, ProviderType
import hashlib
import json


@dataclass
class StoredFile:
    """Metadata for a stored file"""
    file_id: str
    cid: str  # Filecoin Content ID
    key_id: str  # Encryption key reference
    nonce: str  # Encryption nonce (hex)
    size_bytes: int
    filename_encrypted: str  # Even filename is encrypted
    content_hash: str  # SHA-256 of original content
    user_id: str
    org_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            "file_id": self.file_id,
            "cid": self.cid,
            "key_id": self.key_id,
            "nonce": self.nonce,
            "size_bytes": self.size_bytes,
            "filename_encrypted": self.filename_encrypted,
            "content_hash": self.content_hash,
            "user_id": self.user_id,
            "org_id": self.org_id
        }


class EncryptedFilecoinStorage:
    """
    Encrypted storage on Filecoin
    
    Features:
    - Client-side encryption before upload
    - Multi-tenant isolation
    - BYOK support
    - Zero-knowledge architecture
    """
    
    def __init__(self):
        """Initialize encrypted storage"""
        self.encryption_manager = get_encryption_manager()
        self.vault_client = get_vault_client()
    
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
        org_id: str,
        file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StoredFile:
        """
        Upload file with encryption
        
        Args:
            file_data: File content (bytes)
            filename: Original filename
            user_id: User ID
            org_id: Organization ID
            file_id: Optional file ID (generated if not provided)
            metadata: Optional additional metadata
        
        Returns:
            StoredFile with CID and encryption info
        
        Raises:
            Exception: If upload fails
        """
        # 1. Get Filecoin credentials from Universal Vault
        credentials = await self.vault_client.get_provider_credentials(
            ProviderType.FILECOIN,
            user_id=user_id,
            org_id=org_id
        )
        
        if not credentials:
            raise Exception("No Filecoin credentials available")
        
        # 2. Compute content hash (before encryption)
        content_hash = hashlib.sha256(file_data).hexdigest()
        
        # 3. Encrypt file data
        encrypted = self.encryption_manager.encrypt(
            file_data,
            org_id=org_id,
            user_id=user_id,
            file_id=file_id
        )
        
        # 4. Encrypt filename
        filename_encrypted = self.encryption_manager.encrypt_metadata(
            {"filename": filename, "metadata": metadata or {}},
            org_id=org_id,
            user_id=user_id
        )
        
        # 5. Upload encrypted blob to Filecoin (Storacha)
        cid = await self._upload_to_storacha(
            encrypted.ciphertext,
            credentials.api_key,
            credentials.endpoint or "https://api.storacha.network",
            credentials.namespace
        )
        
        # 6. Create StoredFile metadata
        stored_file = StoredFile(
            file_id=encrypted.key_id.split(':')[2],  # Extract file_id from key_id
            cid=cid,
            key_id=encrypted.key_id,
            nonce=encrypted.nonce.hex(),
            size_bytes=len(file_data),
            filename_encrypted=filename_encrypted,
            content_hash=content_hash,
            user_id=user_id,
            org_id=org_id
        )
        
        return stored_file
    
    async def download_file(
        self,
        stored_file: StoredFile
    ) -> bytes:
        """
        Download and decrypt file
        
        Args:
            stored_file: StoredFile metadata
        
        Returns:
            Decrypted file content
        
        Raises:
            Exception: If download or decryption fails
        """
        # 1. Get Filecoin credentials
        credentials = await self.vault_client.get_provider_credentials(
            ProviderType.FILECOIN,
            user_id=stored_file.user_id,
            org_id=stored_file.org_id
        )
        
        if not credentials:
            raise Exception("No Filecoin credentials available")
        
        # 2. Download encrypted blob from Filecoin
        encrypted_data = await self._download_from_storacha(
            stored_file.cid,
            credentials.api_key,
            credentials.endpoint or "https://api.storacha.network"
        )
        
        # 3. Reconstruct EncryptedData object
        encrypted = EncryptedData(
            ciphertext=encrypted_data,
            nonce=bytes.fromhex(stored_file.nonce),
            key_id=stored_file.key_id
        )
        
        # 4. Decrypt
        plaintext = self.encryption_manager.decrypt(encrypted)
        
        # 5. Verify content hash
        computed_hash = hashlib.sha256(plaintext).hexdigest()
        if computed_hash != stored_file.content_hash:
            raise Exception("Content hash mismatch - file may be corrupted")
        
        return plaintext
    
    async def get_filename(self, stored_file: StoredFile) -> str:
        """
        Decrypt and get original filename
        
        Args:
            stored_file: StoredFile metadata
        
        Returns:
            Original filename
        """
        metadata = self.encryption_manager.decrypt_metadata(
            stored_file.filename_encrypted
        )
        return metadata.get("filename", "unknown")
    
    async def _upload_to_storacha(
        self,
        data: bytes,
        api_key: str,
        endpoint: str,
        namespace: Optional[str] = None
    ) -> str:
        """
        Upload data to Storacha (Filecoin)
        
        Args:
            data: Data to upload (already encrypted)
            api_key: Storacha API key
            endpoint: Storacha endpoint
            namespace: Optional namespace for organization
        
        Returns:
            CID (Content Identifier)
        """
        async with httpx.AsyncClient() as client:
            # Storacha API expects multipart/form-data
            files = {"file": ("encrypted_blob", data, "application/octet-stream")}
            headers = {"Authorization": f"Bearer {api_key}"}
            
            # Add namespace if provided
            if namespace:
                headers["X-Namespace"] = namespace
            
            response = await client.post(
                f"{endpoint}/upload",
                files=files,
                headers=headers,
                timeout=300.0  # 5 minutes for large files
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Storacha returns CID in response
            return result.get("cid") or result.get("root", {}).get("cid")
    
    async def _download_from_storacha(
        self,
        cid: str,
        api_key: str,
        endpoint: str
    ) -> bytes:
        """
        Download data from Storacha (Filecoin)
        
        Args:
            cid: Content Identifier
            api_key: Storacha API key
            endpoint: Storacha endpoint
        
        Returns:
            Downloaded data (still encrypted)
        """
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key}"}
            
            # Download via IPFS gateway
            response = await client.get(
                f"https://w3s.link/ipfs/{cid}",
                headers=headers,
                timeout=300.0
            )
            
            response.raise_for_status()
            return response.content


# Global storage instance
_storage: Optional[EncryptedFilecoinStorage] = None


def get_encrypted_storage() -> EncryptedFilecoinStorage:
    """Get global encrypted storage instance"""
    global _storage
    if _storage is None:
        _storage = EncryptedFilecoinStorage()
    return _storage


# Example usage
if __name__ == "__main__":
    async def main():
        storage = EncryptedFilecoinStorage()
        
        # Upload a file
        print("Uploading encrypted file to Filecoin...")
        test_data = b"This is sensitive user data that will be encrypted!"
        
        stored = await storage.upload_file(
            file_data=test_data,
            filename="test_document.txt",
            user_id="user_123",
            org_id="org_456",
            metadata={"tags": ["test", "encrypted"]}
        )
        
        print(f"✅ Uploaded successfully!")
        print(f"   CID: {stored.cid}")
        print(f"   Key ID: {stored.key_id}")
        print(f"   Size: {stored.size_bytes} bytes")
        print(f"   Hash: {stored.content_hash}")
        
        # Download and decrypt
        print("\nDownloading and decrypting...")
        decrypted = await storage.download_file(stored)
        
        print(f"✅ Decrypted: {decrypted.decode('utf-8')}")
        
        # Get filename
        filename = await storage.get_filename(stored)
        print(f"   Filename: {filename}")
    
    asyncio.run(main())
