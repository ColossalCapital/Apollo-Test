"""
Encryption Module - Zero-Knowledge Client-Side Encryption

Implements AES-256-GCM encryption with key derivation for multi-tenant isolation.
Data is encrypted BEFORE uploading to Filecoin, ensuring privacy.

Key Hierarchy:
    Master Key (stored in Universal Vault)
        ↓
    Org Key = HKDF(master, org_id)
        ↓
    User Key = HKDF(org_key, user_id)
        ↓
    File Key = HKDF(user_key, file_id)
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import os
import secrets
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
import base64
import json


@dataclass
class EncryptedData:
    """Encrypted data with metadata"""
    ciphertext: bytes
    nonce: bytes
    key_id: str
    algorithm: str = "AES-256-GCM"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for storage"""
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(self.nonce).decode('utf-8'),
            "key_id": self.key_id,
            "algorithm": self.algorithm
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'EncryptedData':
        """Create from dictionary"""
        return cls(
            ciphertext=base64.b64decode(data["ciphertext"]),
            nonce=base64.b64decode(data["nonce"]),
            key_id=data["key_id"],
            algorithm=data.get("algorithm", "AES-256-GCM")
        )


class EncryptionManager:
    """
    Manages encryption keys and operations
    
    Features:
    - AES-256-GCM authenticated encryption
    - HKDF key derivation for isolation
    - Zero-knowledge architecture
    - Key rotation support
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption manager
        
        Args:
            master_key: Master encryption key (32 bytes). If None, generates new key.
        """
        if master_key is None:
            # Generate new master key (should be stored in Universal Vault)
            self.master_key = AESGCM.generate_key(bit_length=256)
        else:
            if len(master_key) != 32:
                raise ValueError("Master key must be 32 bytes")
            self.master_key = master_key
        
        self.backend = default_backend()
    
    def derive_key(
        self,
        context: str,
        salt: Optional[bytes] = None,
        parent_key: Optional[bytes] = None
    ) -> bytes:
        """
        Derive a key using HKDF
        
        Args:
            context: Context string (e.g., "org_123", "user_456")
            salt: Optional salt (generated if not provided)
            parent_key: Parent key to derive from (uses master_key if not provided)
        
        Returns:
            Derived 32-byte key
        """
        if salt is None:
            salt = context.encode('utf-8')
        
        if parent_key is None:
            parent_key = self.master_key
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=context.encode('utf-8'),
            backend=self.backend
        )
        
        return hkdf.derive(parent_key)
    
    def get_org_key(self, org_id: str) -> bytes:
        """Derive organization-specific key"""
        return self.derive_key(f"org_{org_id}")
    
    def get_user_key(self, org_id: str, user_id: str) -> bytes:
        """Derive user-specific key"""
        org_key = self.get_org_key(org_id)
        return self.derive_key(f"user_{user_id}", parent_key=org_key)
    
    def get_file_key(self, org_id: str, user_id: str, file_id: str) -> bytes:
        """Derive file-specific key"""
        user_key = self.get_user_key(org_id, user_id)
        return self.derive_key(f"file_{file_id}", parent_key=user_key)
    
    def encrypt(
        self,
        plaintext: bytes,
        org_id: str,
        user_id: str,
        file_id: Optional[str] = None,
        associated_data: Optional[bytes] = None
    ) -> EncryptedData:
        """
        Encrypt data with AES-256-GCM
        
        Args:
            plaintext: Data to encrypt
            org_id: Organization ID
            user_id: User ID
            file_id: Optional file ID (generates random if not provided)
            associated_data: Optional authenticated but unencrypted data
        
        Returns:
            EncryptedData object
        """
        # Generate file_id if not provided
        if file_id is None:
            file_id = secrets.token_hex(16)
        
        # Derive encryption key
        encryption_key = self.get_file_key(org_id, user_id, file_id)
        
        # Generate random nonce (96 bits for GCM)
        nonce = os.urandom(12)
        
        # Create cipher
        aesgcm = AESGCM(encryption_key)
        
        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        
        # Create key_id for reference
        key_id = f"{org_id}:{user_id}:{file_id}"
        
        return EncryptedData(
            ciphertext=ciphertext,
            nonce=nonce,
            key_id=key_id
        )
    
    def decrypt(
        self,
        encrypted_data: EncryptedData,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt data with AES-256-GCM
        
        Args:
            encrypted_data: EncryptedData object
            associated_data: Optional authenticated data (must match encryption)
        
        Returns:
            Decrypted plaintext
        
        Raises:
            cryptography.exceptions.InvalidTag: If authentication fails
        """
        # Parse key_id
        org_id, user_id, file_id = encrypted_data.key_id.split(':')
        
        # Derive decryption key
        decryption_key = self.get_file_key(org_id, user_id, file_id)
        
        # Create cipher
        aesgcm = AESGCM(decryption_key)
        
        # Decrypt
        plaintext = aesgcm.decrypt(
            encrypted_data.nonce,
            encrypted_data.ciphertext,
            associated_data
        )
        
        return plaintext
    
    def encrypt_metadata(
        self,
        metadata: Dict[str, Any],
        org_id: str,
        user_id: str
    ) -> str:
        """
        Encrypt metadata (filename, tags, etc.)
        
        Args:
            metadata: Dictionary of metadata
            org_id: Organization ID
            user_id: User ID
        
        Returns:
            Base64-encoded encrypted metadata
        """
        # Serialize metadata
        plaintext = json.dumps(metadata).encode('utf-8')
        
        # Encrypt
        encrypted = self.encrypt(plaintext, org_id, user_id, file_id="metadata")
        
        # Return as base64 string
        return base64.b64encode(
            json.dumps(encrypted.to_dict()).encode('utf-8')
        ).decode('utf-8')
    
    def decrypt_metadata(
        self,
        encrypted_metadata: str
    ) -> Dict[str, Any]:
        """
        Decrypt metadata
        
        Args:
            encrypted_metadata: Base64-encoded encrypted metadata
        
        Returns:
            Decrypted metadata dictionary
        """
        # Decode
        encrypted_dict = json.loads(
            base64.b64decode(encrypted_metadata).decode('utf-8')
        )
        
        # Create EncryptedData object
        encrypted = EncryptedData.from_dict(encrypted_dict)
        
        # Decrypt
        plaintext = self.decrypt(encrypted)
        
        # Deserialize
        return json.loads(plaintext.decode('utf-8'))
    
    def rotate_key(
        self,
        old_encrypted: EncryptedData,
        new_file_id: str
    ) -> EncryptedData:
        """
        Rotate encryption key (re-encrypt with new key)
        
        Args:
            old_encrypted: Old encrypted data
            new_file_id: New file ID for key derivation
        
        Returns:
            Re-encrypted data with new key
        """
        # Decrypt with old key
        plaintext = self.decrypt(old_encrypted)
        
        # Parse old key_id
        org_id, user_id, _ = old_encrypted.key_id.split(':')
        
        # Encrypt with new key
        return self.encrypt(plaintext, org_id, user_id, file_id=new_file_id)


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager(master_key: Optional[bytes] = None) -> EncryptionManager:
    """
    Get global encryption manager instance
    
    Args:
        master_key: Master key (only used on first call)
    
    Returns:
        EncryptionManager instance
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager(master_key)
    return _encryption_manager


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = EncryptionManager()
    
    # Encrypt some data
    plaintext = b"This is sensitive user data!"
    encrypted = manager.encrypt(
        plaintext,
        org_id="org_123",
        user_id="user_456"
    )
    
    print("Encrypted:")
    print(f"  Key ID: {encrypted.key_id}")
    print(f"  Ciphertext: {encrypted.ciphertext[:20]}...")
    print(f"  Nonce: {encrypted.nonce.hex()}")
    
    # Decrypt
    decrypted = manager.decrypt(encrypted)
    print(f"\nDecrypted: {decrypted.decode('utf-8')}")
    
    # Encrypt metadata
    metadata = {"filename": "document.pdf", "size": 1024, "tags": ["important"]}
    encrypted_meta = manager.encrypt_metadata(metadata, "org_123", "user_456")
    print(f"\nEncrypted metadata: {encrypted_meta[:50]}...")
    
    # Decrypt metadata
    decrypted_meta = manager.decrypt_metadata(encrypted_meta)
    print(f"Decrypted metadata: {decrypted_meta}")
