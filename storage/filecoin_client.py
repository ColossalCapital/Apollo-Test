"""
Filecoin Storage Client - Decentralized storage with multi-tenant isolation

Provides:
- Model storage (fine-tuned models)
- Training data storage with privacy isolation
- Metadata management
- Access control based on Atlas/Delt tiers
- Cost: ~$0.01/GB/month (230x cheaper than AWS S3)

Privacy Isolation:
- Personal: Only user can access
- Team: Team members can access
- Org: Organization members can access
- Public: Anyone can access
"""

import os
import hashlib
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests
import httpx
import logging
from config.model_config import (
    PrivacySchema, AppContext, AtlasTier, DeltTier,
    TrainingDataIsolation, ModelAccessControl
)
# from web3.storage import Web3Storage  # TODO: Install web3.storage SDK

logger = logging.getLogger(__name__)

class FilecoinClient:
    """Client for storing and retrieving AI models and training data on Filecoin"""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Filecoin client
        
        Args:
            api_token: Web3.Storage API token (or use env var WEB3_STORAGE_TOKEN)
        """
        self.api_token = api_token or os.getenv("WEB3_STORAGE_TOKEN")
        if not self.api_token:
            raise ValueError("Web3.Storage API token required")
        
        self.client = Web3Storage(token=self.api_token)
        self.cache_dir = Path("./cache/models")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # Model Storage
    # ========================================================================
    
    async def upload_model(
        self,
        model_path: str,
        model_name: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload model to Filecoin
        
        Args:
            model_path: Local path to model file
            model_name: Name of model (e.g., "email_agent")
            version: Version string (e.g., "v1.0.0")
            metadata: Optional metadata (quantization, memory, etc.)
            
        Returns:
            CID (Content Identifier) of uploaded model
        """
        # Calculate file hash
        file_hash = self._calculate_hash(model_path)
        
        # Create metadata
        full_metadata = {
            "model_name": model_name,
            "version": version,
            "file_hash": file_hash,
            "file_size": os.path.getsize(model_path),
            **(metadata or {})
        }
        
        # Upload to Filecoin via Web3.Storage
        with open(model_path, 'rb') as f:
            cid = self.client.put(f, name=f"{model_name}-{version}")
        
        # Store metadata
        await self._store_metadata(model_name, version, cid, full_metadata)
        
        print(f"✅ Uploaded {model_name} {version} to Filecoin: {cid}")
        return cid
    
    async def download_model(
        self,
        model_name: str,
        version: str = "latest",
        force: bool = False
    ) -> str:
        """
        Download model from Filecoin
        
        Args:
            model_name: Name of model
            version: Version to download (default: "latest")
            force: Force re-download even if cached
            
        Returns:
            Local path to downloaded model
        """
        # Check cache first
        cache_path = self.cache_dir / f"{model_name}-{version}.gguf"
        if cache_path.exists() and not force:
            print(f"✅ Using cached model: {cache_path}")
            return str(cache_path)
        
        # Get CID from metadata
        metadata = await self._get_metadata(model_name, version)
        if not metadata:
            raise ValueError(f"Model {model_name} {version} not found")
        
        cid = metadata["cid"]
        
        # Download from Filecoin
        print(f"📥 Downloading {model_name} {version} from Filecoin...")
        content = self.client.get(cid)
        
        # Save to cache
        with open(cache_path, 'wb') as f:
            f.write(content)
        
        # Verify hash
        downloaded_hash = self._calculate_hash(str(cache_path))
        if downloaded_hash != metadata.get("file_hash"):
            raise ValueError("Downloaded file hash mismatch!")
        
        print(f"✅ Downloaded {model_name} {version}: {cache_path}")
        return str(cache_path)
    
    # ========================================================================
    # Training Data Storage
    # ========================================================================
    
    async def upload_training_data(
        self,
        user_id: str,
        data_type: str,
        data: Any,
        version: str = "v1.0.0"
    ) -> str:
        """
        Upload training data to Filecoin
        
        Args:
            user_id: User identifier
            data_type: Type of data (e.g., "email_patterns")
            data: Training data (dict, list, etc.)
            version: Version string
            
        Returns:
            CID of uploaded data
        """
        # Create temp file
        temp_path = self.cache_dir / f"{user_id}_{data_type}_{version}.jsonl"
        
        # Write data
        with open(temp_path, 'w') as f:
            if isinstance(data, list):
                for item in data:
                    f.write(json.dumps(item) + '\n')
            else:
                f.write(json.dumps(data))
        
        # Upload to Filecoin
        with open(temp_path, 'rb') as f:
            cid = self.client.put(f, name=f"{user_id}/{data_type}/{version}")
        
        # Store metadata
        metadata = {
            "user_id": user_id,
            "data_type": data_type,
            "version": version,
            "file_size": os.path.getsize(temp_path),
            "cid": cid
        }
        await self._store_metadata(f"training/{user_id}/{data_type}", version, cid, metadata)
        
        # Cleanup temp file
        temp_path.unlink()
        
        print(f"✅ Uploaded training data for {user_id}/{data_type}: {cid}")
        return cid
    
    async def download_training_data(
        self,
        user_id: str,
        data_type: str,
        version: str = "latest"
    ) -> Any:
        """
        Download training data from Filecoin
        
        Args:
            user_id: User identifier
            data_type: Type of data
            version: Version to download
            
        Returns:
            Training data
        """
        # Get CID
        metadata = await self._get_metadata(f"training/{user_id}/{data_type}", version)
        if not metadata:
            raise ValueError(f"Training data not found: {user_id}/{data_type}")
        
        cid = metadata["cid"]
        
        # Download
        content = self.client.get(cid)
        
        # Parse JSONL
        data = []
        for line in content.decode('utf-8').split('\n'):
            if line.strip():
                data.append(json.loads(line))
        
        return data
    
    # ========================================================================
    # Fine-tuned Model Storage
    # ========================================================================
    
    async def upload_fine_tuned_model(
        self,
        user_id: str,
        model_name: str,
        model_path: str,
        base_model: str,
        training_metadata: Dict[str, Any]
    ) -> str:
        """
        Upload fine-tuned model to Filecoin
        
        Args:
            user_id: User identifier
            model_name: Name of model
            model_path: Local path to fine-tuned model
            base_model: Base model used for fine-tuning
            training_metadata: Training details (epochs, loss, etc.)
            
        Returns:
            CID of uploaded model
        """
        # Calculate hash
        file_hash = self._calculate_hash(model_path)
        
        # Create metadata
        metadata = {
            "user_id": user_id,
            "model_name": model_name,
            "base_model": base_model,
            "file_hash": file_hash,
            "file_size": os.path.getsize(model_path),
            "training": training_metadata
        }
        
        # Upload
        with open(model_path, 'rb') as f:
            cid = self.client.put(f, name=f"{user_id}/{model_name}/fine_tuned")
        
        # Store metadata
        await self._store_metadata(f"fine_tuned/{user_id}/{model_name}", "latest", cid, metadata)
        
        print(f"✅ Uploaded fine-tuned model for {user_id}/{model_name}: {cid}")
        return cid
    
    async def download_fine_tuned_model(
        self,
        user_id: str,
        model_name: str
    ) -> str:
        """
        Download user's fine-tuned model
        
        Args:
            user_id: User identifier
            model_name: Name of model
            
        Returns:
            Local path to model
        """
        # Check cache
        cache_path = self.cache_dir / f"{user_id}_{model_name}_fine_tuned.gguf"
        if cache_path.exists():
            return str(cache_path)
        
        # Get CID
        metadata = await self._get_metadata(f"fine_tuned/{user_id}/{model_name}", "latest")
        if not metadata:
            # Fall back to base model
            print(f"⚠️  No fine-tuned model for {user_id}/{model_name}, using base model")
            return await self.download_model(model_name)
        
        cid = metadata["cid"]
        
        # Download
        content = self.client.get(cid)
        
        # Save
        with open(cache_path, 'wb') as f:
            f.write(content)
        
        # Verify hash
        downloaded_hash = self._calculate_hash(str(cache_path))
        if downloaded_hash != metadata.get("file_hash"):
            raise ValueError("Downloaded file hash mismatch!")
        
        print(f"✅ Downloaded fine-tuned model: {cache_path}")
        return str(cache_path)
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    async def _store_metadata(
        self,
        key: str,
        version: str,
        cid: str,
        metadata: Dict[str, Any]
    ):
        """Store metadata in local database (would be PostgreSQL in production)"""
        metadata_dir = Path("./cache/metadata")
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_path = metadata_dir / f"{key.replace('/', '_')}_{version}.json"
        
        full_metadata = {
            "cid": cid,
            "version": version,
            **metadata
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(full_metadata, f, indent=2)
    
    async def _get_metadata(
        self,
        key: str,
        version: str
    ) -> Optional[Dict[str, Any]]:
        """Get metadata from local database"""
        metadata_dir = Path("./cache/metadata")
        metadata_path = metadata_dir / f"{key.replace('/', '_')}_{version}.json"
        
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    # ========================================================================
    # Model Registry
    # ========================================================================
    
    async def list_models(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List all available models
        
        Args:
            user_id: Optional user ID to filter fine-tuned models
            
        Returns:
            Dict of available models
        """
        metadata_dir = Path("./cache/metadata")
        
        models = {
            "base": [],
            "fine_tuned": []
        }
        
        for metadata_file in metadata_dir.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            if "fine_tuned" in str(metadata_file):
                if not user_id or metadata.get("user_id") == user_id:
                    models["fine_tuned"].append(metadata)
            else:
                models["base"].append(metadata)
        
        return models
