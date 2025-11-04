"""
LLM Client - Interface to local LLM models (llama.cpp)

Supports:
- Phi-3 Medium (7B)
- Mistral 7B
- DeepSeek Coder 6.7B
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
        """
        Generate text using LLM
        
        Args:
            prompt: User prompt
            model: Model name (phi-3-medium, mistral-7b, deepseek-coder-6.7b)
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate
            system_prompt: System prompt (optional)
            stop: Stop sequences (optional)
            
        Returns:
            Generated text
        """
        try:
            # Build full prompt
            full_prompt = self._build_prompt(prompt, system_prompt, model)
            
            # Call llama.cpp server
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
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                raise RuntimeError(f"LLM API error: {response.status_code}")
            
            result = response.json()
            return result["content"].strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "phi-3-medium",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Chat completion (multi-turn conversation)
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Assistant's response
        """
        try:
            # Convert messages to prompt format
            prompt = self._messages_to_prompt(messages, model)
            
            # Generate
            return await self.generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
        except Exception as e:
            logger.error(f"LLM chat failed: {e}")
            raise
    
    def _build_prompt(self, prompt: str, system_prompt: Optional[str], model: str) -> str:
        """Build prompt with proper formatting for each model"""
        
        if model == "phi-3-medium":
            # Phi-3 format: <|system|>\n{system}<|end|>\n
