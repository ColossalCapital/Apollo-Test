"""
Theta EdgeCloud Integration - Complete Implementation

Features:
1. RAG Chatbot Service (Agentic AI)
2. Persistent Storage Volumes
3. Model API Deployment
4. GPU Cluster Training
5. Programmatic Management

Replaces:
- Qdrant (use Theta RAG instead)
- Manual model downloads (use Theta Model APIs)
- Ephemeral storage (use Persistent Volumes)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import asyncio
import os

logger = logging.getLogger(__name__)


class ThetaEdgeCloud:
    """
    Complete Theta EdgeCloud integration
    
    Features:
    - Agentic RAG chatbots for knowledge retrieval
    - Persistent storage for training data/models
    - Model deployment as APIs
    - GPU cluster training
    - Programmatic deployment management
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.thetaedgecloud.com/v1"
    ):
        self.api_key = api_key or os.getenv("THETA_API_KEY")
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=300.0,  # 5 minutes for long operations
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        logger.info("🚀 Theta EdgeCloud initialized")
    
    # ========================================================================
    # 1. AGENTIC RAG CHATBOT (Replaces Qdrant)
    # ========================================================================
    
    async def create_rag_chatbot(
        self,
        name: str,
        documents: List[str],
        description: str = None,
        model: str = "mistral-7b-instruct-v0.2",
        embedding_model: str = "bge-large-en-v1.5"
    ) -> str:
        """
        Create RAG chatbot on Theta EdgeCloud
        
        This replaces our Qdrant setup with Theta's managed RAG service.
        
        Args:
            name: Chatbot name (e.g., "apollo_rag_user123")
            documents: List of documents/text to index
            description: Chatbot description
            model: LLM model to use
            embedding_model: Embedding model for vectors
        
        Returns:
            Chatbot ID
        """
        
        logger.info(f"🤖 Creating RAG chatbot: {name}")
        
        response = await self.client.post(
            f"{self.base_url}/rag/chatbots",
            json={
                "name": name,
                "description": description or f"RAG chatbot for {name}",
                "documents": documents,
                "model": model,
                "embedding_model": embedding_model,
                "settings": {
                    "chunk_size": 512,
                    "chunk_overlap": 50,
                    "top_k": 5,
                    "temperature": 0.7
                }
            }
        )
        
        result = response.json()
        chatbot_id = result["chatbot_id"]
        
        logger.info(f"✅ RAG chatbot created: {chatbot_id}")
        
        return chatbot_id
    
    async def update_rag_knowledge(
        self,
        chatbot_id: str,
        new_documents: List[str]
    ):
        """
        Update RAG chatbot's knowledge base
        
        Add new documents to existing chatbot
        """
        
        logger.info(f"📚 Updating knowledge base for {chatbot_id}")
        
        await self.client.post(
            f"{self.base_url}/rag/chatbots/{chatbot_id}/documents",
            json={"documents": new_documents}
        )
        
        logger.info(f"✅ Knowledge base updated")
    
    async def query_rag(
        self,
        chatbot_id: str,
        query: str,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query RAG chatbot
        
        This replaces Qdrant vector search + LLM generation
        
        Args:
            chatbot_id: Chatbot ID
            query: User query
            include_sources: Include source documents
        
        Returns:
            Response with answer and sources
        """
        
        response = await self.client.post(
            f"{self.base_url}/rag/chatbots/{chatbot_id}/query",
            json={
                "query": query,
                "include_sources": include_sources
            }
        )
        
        return response.json()
    
    async def create_codebase_rag(
        self,
        name: str,
        repo_url: str = None,
        local_path: str = None,
        file_patterns: List[str] = None
    ) -> str:
        """
        Create RAG chatbot for codebase analysis
        
        This enables agentic AI to understand and query codebases!
        
        Args:
            name: Chatbot name
            repo_url: Git repository URL
            local_path: Local codebase path
            file_patterns: File patterns to include (e.g., ["*.py", "*.ts"])
        
        Returns:
            Chatbot ID
        """
        
        logger.info(f"💻 Creating codebase RAG: {name}")
        
        # Read codebase files
        if local_path:
            documents = await self._read_codebase(local_path, file_patterns)
        elif repo_url:
            # Clone and read
            documents = await self._clone_and_read_repo(repo_url, file_patterns)
        else:
            raise ValueError("Must provide repo_url or local_path")
        
        # Create RAG chatbot with code-specific settings
        chatbot_id = await self.create_rag_chatbot(
            name=name,
            documents=documents,
            description=f"Codebase RAG for {name}",
            model="deepseek-coder-6.7b",  # Better for code
            embedding_model="bge-large-en-v1.5"
        )
        
        logger.info(f"✅ Codebase RAG created: {chatbot_id}")
        
        return chatbot_id
    
    # ========================================================================
    # 2. PERSISTENT STORAGE (Replaces Ephemeral Storage)
    # ========================================================================
    
    async def create_volume(
        self,
        name: str,
        size_gb: int = 100,
        region: str = "us-west-2"
    ) -> str:
        """
        Create persistent volume on Theta
        
        Data persists between GPU node restarts
        
        Args:
            name: Volume name
            size_gb: Size in GB
            region: Region
        
        Returns:
            Volume ID
        """
        
        logger.info(f"💾 Creating persistent volume: {name} ({size_gb}GB)")
        
        response = await self.client.post(
            f"{self.base_url}/volumes",
            json={
                "name": name,
                "size_gb": size_gb,
                "region": region
            }
        )
        
        result = response.json()
        volume_id = result["volume_id"]
        
        logger.info(f"✅ Volume created: {volume_id}")
        
        return volume_id
    
    async def attach_volume(
        self,
        volume_id: str,
        gpu_node_id: str,
        mount_path: str = "/data"
    ):
        """
        Attach volume to GPU node
        
        Args:
            volume_id: Volume ID
            gpu_node_id: GPU node ID
            mount_path: Mount path on node
        """
        
        logger.info(f"🔗 Attaching volume {volume_id} to {gpu_node_id}")
        
        await self.client.post(
            f"{self.base_url}/volumes/{volume_id}/attach",
            json={
                "gpu_node_id": gpu_node_id,
                "mount_path": mount_path
            }
        )
        
        logger.info(f"✅ Volume attached at {mount_path}")
    
    async def write_to_volume(
        self,
        volume_id: str,
        path: str,
        data: bytes
    ):
        """
        Write data to persistent volume
        
        Args:
            volume_id: Volume ID
            path: Path on volume
            data: Data to write
        """
        
        await self.client.post(
            f"{self.base_url}/volumes/{volume_id}/files",
            files={"file": (path, data)}
        )
    
    # ========================================================================
    # 3. MODEL API DEPLOYMENT (Replaces Manual Serving)
    # ========================================================================
    
    async def deploy_model_api(
        self,
        model_id: str,
        model_path: str,
        instance_type: str = "T4",
        auto_scaling: Dict = None
    ) -> str:
        """
        Deploy model as API on Theta
        
        No need to download models - Theta hosts them!
        
        Args:
            model_id: Model identifier
            model_path: Path to model (on volume or Filecoin)
            instance_type: GPU instance type
            auto_scaling: Auto-scaling config
        
        Returns:
            API endpoint URL
        """
        
        logger.info(f"🚀 Deploying model API: {model_id}")
        
        response = await self.client.post(
            f"{self.base_url}/model-deployments",
            json={
                "model_id": model_id,
                "model_path": model_path,
                "instance_type": instance_type,
                "auto_scaling": auto_scaling or {
                    "min_instances": 1,
                    "max_instances": 10,
                    "target_qps": 100
                },
                "framework": "llama.cpp",  # For GGUF models
                "runtime_config": {
                    "context_length": 4096,
                    "batch_size": 512
                }
            }
        )
        
        result = response.json()
        api_endpoint = result["api_endpoint"]
        
        logger.info(f"✅ Model API deployed: {api_endpoint}")
        
        return api_endpoint
    
    async def query_model_api(
        self,
        api_endpoint: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Query deployed model API
        
        Args:
            api_endpoint: Model API endpoint
            prompt: Prompt
            temperature: Temperature
            max_tokens: Max tokens
        
        Returns:
            Generated text
        """
        
        response = await self.client.post(
            api_endpoint,
            json={
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        
        return response.json()["output"]
    
    # ========================================================================
    # 4. GPU TRAINING (Enhanced)
    # ========================================================================
    
    async def create_training_job(
        self,
        model_id: str,
        base_model: str,
        training_data_path: str,  # On persistent volume
        hyperparameters: Dict,
        instance_type: str = "A100-40GB",
        num_gpus: int = 1
    ) -> str:
        """
        Create training job on Theta GPU
        
        Args:
            model_id: Model identifier
            base_model: Base model to fine-tune
            training_data_path: Path to training data (on volume)
            hyperparameters: Training hyperparameters
            instance_type: GPU instance type
            num_gpus: Number of GPUs (for clusters)
        
        Returns:
            Job ID
        """
        
        logger.info(f"🎓 Creating training job: {model_id}")
        
        # Create GPU node/cluster
        if num_gpus > 1:
            # GPU cluster for faster training
            node_config = {
                "type": "cluster",
                "num_nodes": num_gpus,
                "instance_type": instance_type,
                "distributed_strategy": "ddp"
            }
        else:
            # Single GPU
            node_config = {
                "type": "single",
                "instance_type": instance_type
            }
        
        response = await self.client.post(
            f"{self.base_url}/training-jobs",
            json={
                "model_id": model_id,
                "base_model": base_model,
                "training_data_path": training_data_path,
                "hyperparameters": hyperparameters,
                "node_config": node_config,
                "framework": "pytorch",
                "training_script": "train.py",
                "output_path": f"/volumes/models/{model_id}/"
            }
        )
        
        result = response.json()
        job_id = result["job_id"]
        
        logger.info(f"✅ Training job created: {job_id}")
        
        return job_id
    
    async def monitor_training(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Monitor training job status
        
        Returns:
            Job status and metrics
        """
        
        response = await self.client.get(
            f"{self.base_url}/training-jobs/{job_id}"
        )
        
        return response.json()
    
    async def wait_for_training(
        self,
        job_id: str,
        poll_interval: int = 30
    ) -> Dict[str, Any]:
        """
        Wait for training to complete
        
        Args:
            job_id: Job ID
            poll_interval: Polling interval in seconds
        
        Returns:
            Final job status
        """
        
        logger.info(f"⏳ Waiting for training job {job_id}...")
        
        while True:
            status = await self.monitor_training(job_id)
            
            if status["state"] == "completed":
                logger.info(f"✅ Training completed!")
                return status
            elif status["state"] == "failed":
                logger.error(f"❌ Training failed: {status['error']}")
                raise RuntimeError(f"Training failed: {status['error']}")
            
            logger.info(f"  Status: {status['state']} - {status.get('progress', 0)}%")
            await asyncio.sleep(poll_interval)
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _read_codebase(
        self,
        path: str,
        file_patterns: List[str] = None
    ) -> List[str]:
        """Read codebase files"""
        import os
        import fnmatch
        
        documents = []
        patterns = file_patterns or ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx"]
        
        for root, dirs, files in os.walk(path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in [
                'node_modules', '.git', '__pycache__', 'venv', 'dist', 'build'
            ]]
            
            for file in files:
                if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            documents.append(f"File: {file_path}\n\n{content}")
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
        
        logger.info(f"📁 Read {len(documents)} files from codebase")
        
        return documents
    
    async def _clone_and_read_repo(
        self,
        repo_url: str,
        file_patterns: List[str] = None
    ) -> List[str]:
        """Clone git repo and read files"""
        import tempfile
        import subprocess
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clone repo
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, tmpdir],
                check=True
            )
            
            # Read files
            return await self._read_codebase(tmpdir, file_patterns)


# ============================================================================
# Convenience Functions
# ============================================================================

async def create_user_rag_chatbot(
    theta: ThetaEdgeCloud,
    user_id: str,
    documents: List[str]
) -> str:
    """Create RAG chatbot for user's documents"""
    
    return await theta.create_rag_chatbot(
        name=f"apollo_rag_{user_id}",
        documents=documents,
        description=f"Personal RAG chatbot for user {user_id}"
    )


async def create_user_volume(
    theta: ThetaEdgeCloud,
    user_id: str,
    size_gb: int = 100
) -> str:
    """Create persistent volume for user"""
    
    return await theta.create_volume(
        name=f"apollo_user_{user_id}",
        size_gb=size_gb
    )


async def deploy_user_model(
    theta: ThetaEdgeCloud,
    user_id: str,
    model_path: str
) -> str:
    """Deploy user's trained model as API"""
    
    return await theta.deploy_model_api(
        model_id=f"apollo_model_{user_id}",
        model_path=model_path,
        instance_type="T4",  # Cheaper for inference
        auto_scaling={
            "min_instances": 1,
            "max_instances": 5,
            "target_qps": 50
        }
    )
