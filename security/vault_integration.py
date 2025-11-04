"""
Universal Vault Integration - Provider Credential Management

Integrates with Universal Vault (Rust service) to store and retrieve:
- Provider credentials (Filecoin, Theta, JarvisLabs)
- Encryption keys (master, org, user)
- BYOK credentials (user-provided keys)

Architecture:
    Apollo/Atlas → Universal Vault API → Encrypted Storage
"""

import httpx
import os
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass
import json
from enum import Enum


class ProviderType(str, Enum):
    """Provider types"""
    FILECOIN = "filecoin"
    THETA = "theta"
    JARVISLABS = "jarvislabs"


class CredentialMode(str, Enum):
    """Credential access mode"""
    SHARED = "shared"  # Use Apollo's shared credentials
    BYOK = "byok"      # User's own credentials


@dataclass
class ProviderCredentials:
    """Provider credentials from Universal Vault"""
    provider: ProviderType
    mode: CredentialMode
    api_key: str
    api_secret: Optional[str] = None
    endpoint: Optional[str] = None
    wallet: Optional[str] = None  # For Theta
    namespace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "provider": self.provider.value,
            "mode": self.mode.value,
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "endpoint": self.endpoint,
            "wallet": self.wallet,
            "namespace": self.namespace
        }


class UniversalVaultClient:
    """
    Client for Universal Vault API
    
    Handles:
    - Provider credential storage/retrieval
    - Encryption key management
    - BYOK credential management
    - Access control
    """
    
    def __init__(
        self,
        vault_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Universal Vault client
        
        Args:
            vault_url: Universal Vault API URL (defaults to env var)
            api_key: API key for authentication (defaults to env var)
        """
        self.vault_url = vault_url or os.getenv(
            "UNIVERSAL_VAULT_URL",
            "http://localhost:8001"
        )
        self.api_key = api_key or os.getenv("UNIVERSAL_VAULT_API_KEY")
        
        self.client = httpx.AsyncClient(
            base_url=self.vault_url,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            timeout=30.0
        )
    
    async def store_system_secret(
        self,
        key: str,
        value: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a system-level secret (provider credentials)
        
        Args:
            key: Secret key (e.g., "filecoin.api_key")
            value: Secret value
            metadata: Optional metadata
        
        Returns:
            True if successful
        """
        try:
            response = await self.client.post(
                "/api/v1/secrets/system",
                json={
                    "key": key,
                    "value": value,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error storing system secret: {e}")
            return False
    
    async def get_system_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a system-level secret
        
        Args:
            key: Secret key
        
        Returns:
            Secret value or None if not found
        """
        try:
            response = await self.client.get(f"/api/v1/secrets/system/{key}")
            response.raise_for_status()
            data = response.json()
            return data.get("value")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Error retrieving system secret: {e}")
            return None
        except Exception as e:
            print(f"Error retrieving system secret: {e}")
            return None
    
    async def store_provider_credentials(
        self,
        provider: ProviderType,
        credentials: Dict[str, str],
        mode: CredentialMode = CredentialMode.SHARED
    ) -> bool:
        """
        Store provider credentials
        
        Args:
            provider: Provider type
            credentials: Credential dictionary
            mode: Shared or BYOK
        
        Returns:
            True if successful
        """
        prefix = f"providers.{mode.value}.{provider.value}"
        
        success = True
        for key, value in credentials.items():
            if value:  # Only store non-empty values
                secret_key = f"{prefix}.{key}"
                if not await self.store_system_secret(secret_key, value):
                    success = False
        
        return success
    
    async def get_provider_credentials(
        self,
        provider: ProviderType,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> Optional[ProviderCredentials]:
        """
        Get provider credentials (BYOK or shared)
        
        Priority: BYOK (user) > Shared
        
        Args:
            provider: Provider type
            user_id: User ID (for BYOK check)
            org_id: Organization ID (for namespace)
        
        Returns:
            ProviderCredentials or None
        """
        # Check for BYOK credentials first
        if user_id:
            byok_creds = await self._get_byok_credentials(provider, user_id)
            if byok_creds:
                return byok_creds
        
        # Fall back to shared credentials
        return await self._get_shared_credentials(provider, user_id, org_id)
    
    async def _get_byok_credentials(
        self,
        provider: ProviderType,
        user_id: str
    ) -> Optional[ProviderCredentials]:
        """Get user's BYOK credentials"""
        prefix = f"providers.byok.{provider.value}.user_{user_id}"
        
        api_key = await self.get_system_secret(f"{prefix}.api_key")
        if not api_key:
            return None
        
        return ProviderCredentials(
            provider=provider,
            mode=CredentialMode.BYOK,
            api_key=api_key,
            api_secret=await self.get_system_secret(f"{prefix}.api_secret"),
            endpoint=await self.get_system_secret(f"{prefix}.endpoint"),
            wallet=await self.get_system_secret(f"{prefix}.wallet"),
            namespace=f"user_{user_id}"
        )
    
    async def _get_shared_credentials(
        self,
        provider: ProviderType,
        user_id: Optional[str],
        org_id: Optional[str]
    ) -> Optional[ProviderCredentials]:
        """Get shared credentials"""
        prefix = f"providers.shared.{provider.value}"
        
        api_key = await self.get_system_secret(f"{prefix}.api_key")
        if not api_key:
            return None
        
        # Build namespace for multi-tenant isolation
        namespace = "colossalcapital"
        if org_id:
            namespace += f"/org_{org_id}"
        if user_id:
            namespace += f"/user_{user_id}"
        
        return ProviderCredentials(
            provider=provider,
            mode=CredentialMode.SHARED,
            api_key=api_key,
            api_secret=await self.get_system_secret(f"{prefix}.api_secret"),
            endpoint=await self.get_system_secret(f"{prefix}.endpoint"),
            wallet=await self.get_system_secret(f"{prefix}.wallet"),
            namespace=namespace
        )
    
    async def store_encryption_key(
        self,
        key_type: Literal["master", "org", "user"],
        key_id: str,
        key_value: bytes
    ) -> bool:
        """
        Store encryption key
        
        Args:
            key_type: Type of key (master, org, user)
            key_id: Key identifier
            key_value: Key bytes (will be base64 encoded)
        
        Returns:
            True if successful
        """
        import base64
        secret_key = f"encryption.{key_type}.{key_id}"
        encoded_key = base64.b64encode(key_value).decode('utf-8')
        return await self.store_system_secret(secret_key, encoded_key)
    
    async def get_encryption_key(
        self,
        key_type: Literal["master", "org", "user"],
        key_id: str
    ) -> Optional[bytes]:
        """
        Retrieve encryption key
        
        Args:
            key_type: Type of key
            key_id: Key identifier
        
        Returns:
            Key bytes or None
        """
        import base64
        secret_key = f"encryption.{key_type}.{key_id}"
        encoded_key = await self.get_system_secret(secret_key)
        
        if encoded_key:
            return base64.b64decode(encoded_key)
        return None
    
    async def initialize_from_env(self) -> bool:
        """
        Initialize Universal Vault with credentials from .env
        
        Reads Apollo's .env and stores credentials in Universal Vault
        
        Returns:
            True if successful
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        success = True
        
        # Filecoin
        filecoin_key = os.getenv("FILECOIN_API_KEY")
        if filecoin_key:
            success &= await self.store_provider_credentials(
                ProviderType.FILECOIN,
                {
                    "api_key": filecoin_key,
                    "api_secret": os.getenv("FILECOIN_API_SECRET", ""),
                    "endpoint": os.getenv("FILECOIN_ENDPOINT", "https://api.storacha.network")
                }
            )
        
        # Theta
        theta_key = os.getenv("THETA_API_KEY")
        if theta_key:
            success &= await self.store_provider_credentials(
                ProviderType.THETA,
                {
                    "api_key": theta_key,
                    "wallet": os.getenv("THETA_WALLET", ""),
                    "endpoint": "https://api.thetaedgecloud.com"
                }
            )
        
        # JarvisLabs
        jarvis_key = os.getenv("JARVISLABS_API_KEY")
        if jarvis_key:
            success &= await self.store_provider_credentials(
                ProviderType.JARVISLABS,
                {
                    "api_key": jarvis_key,
                    "endpoint": "https://api.jarvislabs.ai"
                }
            )
        
        return success
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global vault client instance
_vault_client: Optional[UniversalVaultClient] = None


def get_vault_client() -> UniversalVaultClient:
    """Get global vault client instance"""
    global _vault_client
    if _vault_client is None:
        _vault_client = UniversalVaultClient()
    return _vault_client


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        vault = UniversalVaultClient()
        
        # Initialize from .env
        print("Initializing Universal Vault from .env...")
        success = await vault.initialize_from_env()
        print(f"Initialization: {'✅ Success' if success else '❌ Failed'}")
        
        # Get Filecoin credentials
        print("\nRetrieving Filecoin credentials...")
        creds = await vault.get_provider_credentials(
            ProviderType.FILECOIN,
            user_id="test_user",
            org_id="test_org"
        )
        
        if creds:
            print(f"✅ Got credentials:")
            print(f"   Mode: {creds.mode}")
            print(f"   API Key: {creds.api_key[:20]}...")
            print(f"   Namespace: {creds.namespace}")
        else:
            print("❌ No credentials found")
        
        await vault.close()
    
    asyncio.run(main())
