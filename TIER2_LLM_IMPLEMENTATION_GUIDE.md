# 🚀 Tier 2: LLM-Powered Analysis - Implementation Guide

## **Overview**

This guide shows you how to upgrade Apollo agents from **static knowledge** (Tier 1) to **LLM-powered analysis** (Tier 2).

---

## **Step 1: Complete the LLM Client**

The LLM client file at `Apollo/llm/llm_client.py` needs to be completed. Here's the full implementation:

```python
"""
LLM Client - Interface to local LLM models (llama.cpp)
"""

import httpx
import json
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for local LLM inference via llama.cpp server"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate(
        self,
        prompt: str,
        model: str = "phi-3-medium",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """Generate text using LLM"""
        try:
            full_prompt = self._build_prompt(prompt, system_prompt, model)
            
            response = await self.client.post(
                f"{self.base_url}/completion",
                json={
                    "prompt": full_prompt,
                    "temperature": temperature,
                    "n_predict": max_tokens,
                    "stop": stop or [],
                }
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"LLM API error: {response.status_code}")
            
            result = response.json()
            return result["content"].strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def _build_prompt(self, prompt: str, system_prompt: Optional[str], model: str) -> str:
        """Build prompt with proper formatting for each model"""
        
        if model == "phi-3-medium":
            # Phi-3 format
            if system_prompt:
                return f"<|system|>\n{system_prompt}<|end|>\n
