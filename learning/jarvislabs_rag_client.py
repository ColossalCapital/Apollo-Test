"""
JarvisLabs RAG Client - Fallback GPU Provider

Provides vector storage and GPU inference as a fallback to Theta.

Features:
- Qdrant on JarvisLabs GPU instances
- GPU inference for DeepSeek models
- Automatic failover from Theta
- Cost-effective alternative ($1.50/job vs $1 Theta)
"""

import os
import logging
import aiohttp
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class JarvisLabsRAGClient:
    """
    JarvisLabs RAG Client - Fallback to Theta
    
    Provides:
    - Vector storage (Qdrant on JarvisLabs)
    - GPU inference
    - Automatic failover
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://api.jarvislabs.ai/v1"
    ):
        """
        Initialize JarvisLabs RAG client
        
        Args:
            api_key: JarvisLabs API key (or from JARVISLABS_API_KEY env)
            endpoint: JarvisLabs API endpoint
        """
        self.api_key = api_key or os.getenv("JARVISLABS_API_KEY")
        self.endpoint = endpoint
        
        if not self.api_key:
            logger.warning("JARVISLABS_API_KEY not set - JarvisLabs will not work")
        
        logger.info(f"JarvisLabsRAGClient initialized: {endpoint}")
    
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int = 384,
        distance: str = "cosine"
    ) -> Dict[str, Any]:
        """Create a RAG collection on JarvisLabs"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/rag/collections",
                json={
                    "name": collection_name,
                    "vector_size": vector_size,
                    "distance": distance
                },
                headers=self._headers()
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Failed to create collection: {error}")
                
                result = await resp.json()
                logger.info(f"Created JarvisLabs RAG collection: {collection_name}")
                return result
    
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.endpoint}/rag/collections/{collection_name}",
                    headers=self._headers()
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Error checking collection: {e}")
            return False
    
    async def upsert_vectors(
        self,
        collection_name: str,
        points: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Store vectors in JarvisLabs RAG"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/rag/collections/{collection_name}/points",
                json={"points": points},
                headers=self._headers()
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Failed to upsert vectors: {error}")
                
                result = await resp.json()
                logger.info(f"Upserted {len(points)} vectors to JarvisLabs RAG")
                return result
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Semantic search in JarvisLabs RAG"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/rag/collections/{collection_name}/search",
                json={
                    "vector": query_vector,
                    "limit": limit,
                    "filter": filters,
                    "score_threshold": score_threshold
                },
                headers=self._headers()
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Search failed: {error}")
                
                result = await resp.json()
                return result.get("results", [])
    
    async def delete_points(
        self,
        collection_name: str,
        point_ids: List[str]
    ) -> Dict[str, Any]:
        """Delete points from collection"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/rag/collections/{collection_name}/points/delete",
                json={"ids": point_ids},
                headers=self._headers()
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Failed to delete points: {error}")
                
                result = await resp.json()
                logger.info(f"Deleted {len(point_ids)} points from JarvisLabs RAG")
                return result
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers with auth"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
