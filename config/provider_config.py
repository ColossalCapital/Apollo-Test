"""
Provider Configuration - BYOK + Multi-tenant Support

Users can either:
1. Bring Your Own Key (BYOK) - Use their own Filecoin/Theta/JarvisLabs accounts
2. Use shared infrastructure - We provide multi-tenant isolated access

Priority: BYOK > Shared > Disabled
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
import os


class ProviderMode(str, Enum):
    """Provider access mode"""
    BYOK = "byok"  # User provides their own keys
    SHARED = "shared"  # Use our shared multi-tenant infrastructure
    DISABLED = "disabled"  # Provider not available


class FilecoinConfig(BaseModel):
    """Filecoin storage configuration"""
    mode: ProviderMode = Field(default=ProviderMode.DISABLED)
    
    # BYOK settings
    user_api_key: Optional[str] = None
    user_api_secret: Optional[str] = None
    user_endpoint: Optional[str] = None
    
    # Shared settings (our infrastructure)
    shared_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("FILECOIN_API_KEY"))
    shared_api_secret: Optional[str] = Field(default_factory=lambda: os.getenv("FILECOIN_API_SECRET"))
    shared_endpoint: str = "https://api.web3.storage"
    
    # Multi-tenant isolation
    isolation_prefix: str = "colossalcapital"  # Our root namespace
    user_isolation: bool = True  # Isolate by user_id
    org_isolation: bool = True  # Isolate by org_id
    
    def get_active_config(self, user_id: str, org_id: str) -> Dict[str, Any]:
        """Get active configuration based on mode"""
        if self.mode == ProviderMode.BYOK and self.user_api_key:
            return {
                "api_key": self.user_api_key,
                "api_secret": self.user_api_secret,
                "endpoint": self.user_endpoint or self.shared_endpoint,
                "namespace": f"user_{user_id}",  # User's own namespace
                "mode": "byok"
            }
        elif self.mode == ProviderMode.SHARED and self.shared_api_key:
            # Multi-tenant: our account, isolated by user/org
            namespace = f"{self.isolation_prefix}"
            if self.org_isolation:
                namespace += f"/org_{org_id}"
            if self.user_isolation:
                namespace += f"/user_{user_id}"
            
            return {
                "api_key": self.shared_api_key,
                "api_secret": self.shared_api_secret,
                "endpoint": self.shared_endpoint,
                "namespace": namespace,
                "mode": "shared"
            }
        else:
            return {"mode": "disabled"}


class ThetaConfig(BaseModel):
    """Theta GPU training configuration"""
    mode: ProviderMode = Field(default=ProviderMode.DISABLED)
    
    # BYOK settings
    user_api_key: Optional[str] = None
    user_wallet_address: Optional[str] = None
    
    # Shared settings (our infrastructure)
    shared_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("THETA_API_KEY"))
    shared_wallet: Optional[str] = Field(default_factory=lambda: os.getenv("THETA_WALLET"))
    shared_endpoint: str = "https://api.thetaedgecloud.com"
    
    # Multi-tenant isolation
    isolation_prefix: str = "colossalcapital"
    user_isolation: bool = True
    org_isolation: bool = True
    
    # Resource limits (shared mode only)
    max_gpu_hours_per_user: int = 10  # Per month
    max_concurrent_jobs: int = 2
    
    def get_active_config(self, user_id: str, org_id: str) -> Dict[str, Any]:
        """Get active configuration based on mode"""
        if self.mode == ProviderMode.BYOK and self.user_api_key:
            return {
                "api_key": self.user_api_key,
                "wallet": self.user_wallet_address,
                "endpoint": self.shared_endpoint,
                "namespace": f"user_{user_id}",
                "mode": "byok",
                "limits": None  # No limits for BYOK
            }
        elif self.mode == ProviderMode.SHARED and self.shared_api_key:
            namespace = f"{self.isolation_prefix}"
            if self.org_isolation:
                namespace += f"/org_{org_id}"
            if self.user_isolation:
                namespace += f"/user_{user_id}"
            
            return {
                "api_key": self.shared_api_key,
                "wallet": self.shared_wallet,
                "endpoint": self.shared_endpoint,
                "namespace": namespace,
                "mode": "shared",
                "limits": {
                    "max_gpu_hours": self.max_gpu_hours_per_user,
                    "max_concurrent": self.max_concurrent_jobs
                }
            }
        else:
            return {"mode": "disabled"}


class JarvisLabsConfig(BaseModel):
    """JarvisLabs GPU training configuration"""
    mode: ProviderMode = Field(default=ProviderMode.DISABLED)
    
    # BYOK settings
    user_api_key: Optional[str] = None
    
    # Shared settings (our infrastructure)
    shared_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("JARVISLABS_API_KEY"))
    shared_endpoint: str = "https://api.jarvislabs.ai"
    
    # Multi-tenant isolation
    isolation_prefix: str = "colossalcapital"
    user_isolation: bool = True
    org_isolation: bool = True
    
    # Resource limits (shared mode only)
    max_gpu_hours_per_user: int = 10
    max_concurrent_jobs: int = 2
    
    def get_active_config(self, user_id: str, org_id: str) -> Dict[str, Any]:
        """Get active configuration based on mode"""
        if self.mode == ProviderMode.BYOK and self.user_api_key:
            return {
                "api_key": self.user_api_key,
                "endpoint": self.shared_endpoint,
                "namespace": f"user_{user_id}",
                "mode": "byok",
                "limits": None
            }
        elif self.mode == ProviderMode.SHARED and self.shared_api_key:
            namespace = f"{self.isolation_prefix}"
            if self.org_isolation:
                namespace += f"/org_{org_id}"
            if self.user_isolation:
                namespace += f"/user_{user_id}"
            
            return {
                "api_key": self.shared_api_key,
                "endpoint": self.shared_endpoint,
                "namespace": namespace,
                "mode": "shared",
                "limits": {
                    "max_gpu_hours": self.max_gpu_hours_per_user,
                    "max_concurrent": self.max_concurrent_jobs
                }
            }
        else:
            return {"mode": "disabled"}


class ProviderSettings(BaseModel):
    """Complete provider settings"""
    filecoin: FilecoinConfig = Field(default_factory=FilecoinConfig)
    theta: ThetaConfig = Field(default_factory=ThetaConfig)
    jarvislabs: JarvisLabsConfig = Field(default_factory=JarvisLabsConfig)
    
    # Global settings
    allow_byok: bool = True  # Allow users to bring their own keys
    default_mode: ProviderMode = ProviderMode.SHARED  # Default to shared
    
    def get_provider_config(
        self,
        provider: Literal["filecoin", "theta", "jarvislabs"],
        user_id: str,
        org_id: str,
        user_keys: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get provider configuration with BYOK support
        
        Args:
            provider: Provider name
            user_id: User ID for isolation
            org_id: Organization ID for isolation
            user_keys: Optional user-provided keys (BYOK)
        
        Returns:
            Active configuration for the provider
        """
        config_map = {
            "filecoin": self.filecoin,
            "theta": self.theta,
            "jarvislabs": self.jarvislabs
        }
        
        provider_config = config_map[provider]
        
        # If user provides keys and BYOK is allowed, use BYOK mode
        if self.allow_byok and user_keys:
            # Temporarily override with user keys
            if provider == "filecoin":
                provider_config.user_api_key = user_keys.get("api_key")
                provider_config.user_api_secret = user_keys.get("api_secret")
                provider_config.user_endpoint = user_keys.get("endpoint")
                provider_config.mode = ProviderMode.BYOK
            elif provider in ["theta", "jarvislabs"]:
                provider_config.user_api_key = user_keys.get("api_key")
                if provider == "theta":
                    provider_config.user_wallet_address = user_keys.get("wallet")
                provider_config.mode = ProviderMode.BYOK
        
        return provider_config.get_active_config(user_id, org_id)


# Global settings instance
provider_settings = ProviderSettings()


def get_filecoin_config(user_id: str, org_id: str, user_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Get Filecoin configuration"""
    return provider_settings.get_provider_config("filecoin", user_id, org_id, user_keys)


def get_theta_config(user_id: str, org_id: str, user_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Get Theta configuration"""
    return provider_settings.get_provider_config("theta", user_id, org_id, user_keys)


def get_jarvislabs_config(user_id: str, org_id: str, user_keys: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Get JarvisLabs configuration"""
    return provider_settings.get_provider_config("jarvislabs", user_id, org_id, user_keys)


# Example usage
if __name__ == "__main__":
    # Shared mode (default)
    config = get_filecoin_config("user123", "org456")
    print("Shared mode:", config)
    
    # BYOK mode
    user_keys = {
        "api_key": "user_provided_key",
        "api_secret": "user_provided_secret"
    }
    config = get_filecoin_config("user123", "org456", user_keys)
    print("BYOK mode:", config)
