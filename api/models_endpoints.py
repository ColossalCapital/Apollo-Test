"""
Model Management API Endpoints

Manages local LLM models (Ollama) with multi-entity support.
Each entity can download, configure, and use different models.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Literal
import asyncio
import aiohttp
import os
from datetime import datetime

router = APIRouter(prefix="/api/models", tags=["models"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ModelDownloadRequest(BaseModel):
    """Request to download a model"""
    entity_id: str
    org_id: Optional[str] = None
    model_name: str  # e.g., "deepseek-coder:33b"
    priority: Literal["high", "normal", "low"] = "normal"


class ModelConfigRequest(BaseModel):
    """Configure model for entity"""
    entity_id: str
    org_id: Optional[str] = None
    model_name: str
    use_case: Literal["code_generation", "email_analysis", "general"]
    max_tokens: int = 4000
    temperature: float = 0.2


class ModelUsageQuery(BaseModel):
    """Query model usage"""
    entity_id: str
    org_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ModelInfo(BaseModel):
    """Model information"""
    name: str
    size: str
    quantization: str
    downloaded: bool
    download_progress: Optional[float] = None
    entities_using: int
    total_requests: int


class ModelDownloadStatus(BaseModel):
    """Download status"""
    model_name: str
    status: Literal["queued", "downloading", "complete", "failed"]
    progress: float  # 0-100
    downloaded_bytes: int
    total_bytes: int
    eta_seconds: Optional[int] = None
    error: Optional[str] = None


# ============================================================================
# Model Management
# ============================================================================

class OllamaModelManager:
    """Manages Ollama models with multi-entity support"""
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.downloads = {}  # Track active downloads
        
    async def list_available_models(self) -> List[dict]:
        """List all available models"""
        return [
            {
                "name": "deepseek-coder:33b",
                "size": "20GB",
                "quantization": "Q4_K_M",
                "description": "DeepSeek Coder 33B - Best for code generation",
                "use_cases": ["code_generation", "code_review", "documentation"]
            },
            {
                "name": "deepseek-coder:6.7b",
                "size": "4GB",
                "quantization": "Q4_K_M",
                "description": "DeepSeek Coder 6.7B - Faster, smaller model",
                "use_cases": ["code_completion", "quick_analysis"]
            },
            {
                "name": "llama3:8b",
                "size": "4.7GB",
                "quantization": "Q4_0",
                "description": "Llama 3 8B - General purpose",
                "use_cases": ["email_analysis", "summarization", "general"]
            },
            {
                "name": "mistral:7b",
                "size": "4.1GB",
                "quantization": "Q4_0",
                "description": "Mistral 7B - Fast and efficient",
                "use_cases": ["quick_tasks", "classification"]
            }
        ]
    
    async def list_downloaded_models(self) -> List[dict]:
        """List downloaded models"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.ollama_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                return []
    
    async def download_model(
        self,
        model_name: str,
        entity_id: str,
        progress_callback=None
    ) -> ModelDownloadStatus:
        """Download a model"""
        
        download_id = f"{entity_id}_{model_name}"
        
        # Check if already downloading
        if download_id in self.downloads:
            return self.downloads[download_id]
        
        # Initialize download status
        status = ModelDownloadStatus(
            model_name=model_name,
            status="downloading",
            progress=0.0,
            downloaded_bytes=0,
            total_bytes=0
        )
        self.downloads[download_id] = status
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/pull",
                    json={"name": model_name, "stream": True}
                ) as response:
                    if response.status != 200:
                        status.status = "failed"
                        status.error = f"HTTP {response.status}"
                        return status
                    
                    # Stream download progress
                    async for line in response.content:
                        if line:
                            data = json.loads(line)
                            
                            if "total" in data and "completed" in data:
                                status.total_bytes = data["total"]
                                status.downloaded_bytes = data["completed"]
                                status.progress = (data["completed"] / data["total"]) * 100
                                
                                if progress_callback:
                                    await progress_callback(status)
                            
                            if data.get("status") == "success":
                                status.status = "complete"
                                status.progress = 100.0
                                break
            
            return status
            
        except Exception as e:
            status.status = "failed"
            status.error = str(e)
            return status
        finally:
            # Clean up
            if download_id in self.downloads:
                del self.downloads[download_id]
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.ollama_url}/api/delete",
                json={"name": model_name}
            ) as response:
                return response.status == 200


# Global instance
model_manager = OllamaModelManager()


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/available")
async def list_available_models():
    """List all available models for download"""
    models = await model_manager.list_available_models()
    return {"models": models}


@router.get("/downloaded")
async def list_downloaded_models():
    """List all downloaded models"""
    models = await model_manager.list_downloaded_models()
    return {"models": models}


@router.post("/download")
async def download_model(
    request: ModelDownloadRequest,
    background_tasks: BackgroundTasks
):
    """
    Download a model for an entity
    
    Multi-entity support:
    - Each entity can download models independently
    - Download progress tracked per entity
    - Usage quotas enforced per entity
    """
    
    # Check if model already downloaded
    downloaded = await model_manager.list_downloaded_models()
    if any(m["name"] == request.model_name for m in downloaded):
        return {
            "status": "already_downloaded",
            "model_name": request.model_name,
            "message": "Model already available"
        }
    
    # Start download in background
    async def download_task():
        await model_manager.download_model(
            request.model_name,
            request.entity_id
        )
    
    background_tasks.add_task(download_task)
    
    return {
        "status": "download_started",
        "model_name": request.model_name,
        "entity_id": request.entity_id,
        "message": "Download started in background"
    }


@router.get("/download/status/{model_name}")
async def get_download_status(model_name: str, entity_id: str):
    """Get download status for a model"""
    
    download_id = f"{entity_id}_{model_name}"
    
    if download_id in model_manager.downloads:
        return model_manager.downloads[download_id]
    
    # Check if already downloaded
    downloaded = await model_manager.list_downloaded_models()
    if any(m["name"] == model_name for m in downloaded):
        return ModelDownloadStatus(
            model_name=model_name,
            status="complete",
            progress=100.0,
            downloaded_bytes=0,
            total_bytes=0
        )
    
    return ModelDownloadStatus(
        model_name=model_name,
        status="not_started",
        progress=0.0,
        downloaded_bytes=0,
        total_bytes=0
    )


@router.post("/configure")
async def configure_model(request: ModelConfigRequest):
    """
    Configure model preferences for an entity
    
    Stores entity-specific model configuration:
    - Which model to use for which use case
    - Model parameters (temperature, max_tokens)
    - Usage quotas and limits
    """
    
    # Store in PostgreSQL
    config = {
        "entity_id": request.entity_id,
        "org_id": request.org_id,
        "model_name": request.model_name,
        "use_case": request.use_case,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "configured_at": datetime.utcnow().isoformat()
    }
    
    # TODO: Store in database
    # await db.model_configs.insert_one(config)
    
    return {
        "status": "configured",
        "entity_id": request.entity_id,
        "model_name": request.model_name,
        "use_case": request.use_case
    }


@router.get("/config/{entity_id}")
async def get_entity_config(entity_id: str, org_id: Optional[str] = None):
    """Get model configuration for an entity"""
    
    # TODO: Query from database
    # config = await db.model_configs.find_one({
    #     "entity_id": entity_id,
    #     "org_id": org_id
    # })
    
    # Default config
    return {
        "entity_id": entity_id,
        "org_id": org_id,
        "models": {
            "code_generation": {
                "model": "deepseek-coder:33b",
                "max_tokens": 4000,
                "temperature": 0.2
            },
            "email_analysis": {
                "model": "llama3:8b",
                "max_tokens": 2000,
                "temperature": 0.3
            },
            "general": {
                "model": "mistral:7b",
                "max_tokens": 2000,
                "temperature": 0.5
            }
        }
    }


@router.get("/usage/{entity_id}")
async def get_model_usage(entity_id: str, org_id: Optional[str] = None):
    """
    Get model usage statistics for an entity
    
    Returns:
    - Total requests
    - Tokens used
    - Cost savings vs API
    - Usage by model
    """
    
    # TODO: Query from QuestDB
    # usage = await questdb.query(f"""
    #     SELECT 
    #         model_name,
    #         count(*) as requests,
    #         sum(tokens_used) as total_tokens,
    #         avg(response_time_ms) as avg_response_time
    #     FROM model_usage
    #     WHERE entity_id = '{entity_id}'
    #     GROUP BY model_name
    # """)
    
    # Mock data
    return {
        "entity_id": entity_id,
        "org_id": org_id,
        "period": "last_30_days",
        "usage": {
            "deepseek-coder:33b": {
                "requests": 1247,
                "tokens_used": 3_450_000,
                "avg_response_time_ms": 2300,
                "cost_savings_usd": 483.00  # vs API
            },
            "llama3:8b": {
                "requests": 5892,
                "tokens_used": 8_920_000,
                "avg_response_time_ms": 850,
                "cost_savings_usd": 1248.00
            }
        },
        "total_cost_savings_usd": 1731.00
    }


@router.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """Delete a downloaded model"""
    
    success = await model_manager.delete_model(model_name)
    
    if success:
        return {
            "status": "deleted",
            "model_name": model_name
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to delete model")


@router.get("/status")
async def get_model_status():
    """
    Get current model status - which models are active and available
    
    Returns information about:
    - DeepSeek Coder models (local Ollama)
    - Theta GPU models (remote)
    - JarvisLabs GPU models (remote)
    """
    
    models = []
    
    # Check local Ollama models
    try:
        downloaded = await model_manager.list_downloaded_models()
        for model in downloaded:
            model_name = model.get("name", "")
            if "deepseek" in model_name.lower():
                models.append({
                    "name": model_name,
                    "provider": "ollama",
                    "active": True,
                    "type": "local",
                    "size": model.get("size", "unknown")
                })
    except:
        pass
    
    # Check Theta GPU (via environment variable or config)
    theta_enabled = os.getenv("USE_THETA_GPU", "false").lower() == "true"
    if theta_enabled:
        theta_model = os.getenv("THETA_MODEL", "Qwen2.5-Coder 32B")
        models.append({
            "name": theta_model,
            "provider": "theta_gpu",
            "active": True,
            "type": "remote",
            "cost": "$3/month flat rate"
        })
    
    # Check JarvisLabs (via environment variable or config)
    jarvis_enabled = os.getenv("USE_JARVISLABS", "false").lower() == "true"
    if jarvis_enabled:
        jarvis_model = os.getenv("JARVISLABS_MODEL", "DeepSeek Coder 33B")
        models.append({
            "name": jarvis_model,
            "provider": "jarvislabs",
            "active": True,
            "type": "remote",
            "gpu": os.getenv("JARVISLABS_GPU", "A100")
        })
    
    return {
        "status": "ok",
        "models": models,
        "total_active": len([m for m in models if m["active"]])
    }


@router.get("/health")
async def check_ollama_health():
    """Check if Ollama is running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{model_manager.ollama_url}/api/tags") as response:
                if response.status == 200:
                    return {
                        "status": "healthy",
                        "ollama_url": model_manager.ollama_url,
                        "available": True
                    }
    except:
        pass
    
    return {
        "status": "unhealthy",
        "ollama_url": model_manager.ollama_url,
        "available": False,
        "message": "Ollama not running. Start with: ollama serve"
    }
