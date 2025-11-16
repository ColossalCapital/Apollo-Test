"""
Smart Wiki - Tier 2 LLM-Powered Analysis

Combines static knowledge with LLM intelligence for personalized insights
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
import httpx
import json as json_lib


class WikiAgent(BaseAgent):
    """wiki and documentation generation with LLM-powered analysis"""
    
    def __init__(self):
        super().__init__(name="WikiAgent", model="phi-3-medium")
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze with hybrid intelligence (static + LLM)
        
        Args:
            data: Analysis request data
                - quick_mode: bool (optional) - Return static knowledge only
                - ... (agent-specific fields)
        
        Returns:
            Analysis result with static knowledge and/or LLM insights
        """
        
        # Step 1: Get static knowledge (always fast)
        static_knowledge = self.get_static_knowledge(data)
        
        # Step 2: Quick mode? Return static only
        if data.get('quick_mode'):
            return {
                "mode": "static",
                "knowledge": static_knowledge,
                "response_time_ms": 5
            }
        
        # Step 3: LLM analysis if detailed data provided
        if self._should_use_llm(data):
            try:
                llm_analysis = await self.analyze_with_llm(data, static_knowledge)
                
                return {
                    "mode": "llm_powered",
                    "static_knowledge": static_knowledge,
                    "llm_analysis": llm_analysis,
                    "confidence": llm_analysis.get("confidence", 0.8),
                    "response_time_ms": 2000
                }
            except Exception as e:
                # LLM failed, fallback to static
                return {
                    "mode": "static_fallback",
                    "knowledge": static_knowledge,
                    "error": str(e),
                    "response_time_ms": 10
                }
        
        # Step 4: No detailed data, return static
        return {
            "mode": "static",
            "knowledge": static_knowledge,
            "response_time_ms": 5
        }
    
    def get_static_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tier 1: Static knowledge (fast, deterministic)
        
        This is the original agent's knowledge - documentation and rules
        """
        # TODO: Import and use original agent's knowledge
        return {
            "agent": "Wiki",
            "description": "wiki and documentation generation",
            "capabilities": ['wiki generation', 'documentation', 'knowledge organization']
        }
    
    def _should_use_llm(self, data: Dict[str, Any]) -> bool:
        """Determine if LLM analysis is appropriate"""
        # Use LLM if user provided specific data to analyze
        return any(key in data for key in ['codebase', 'project', 'documentation'])
    
    async def analyze_with_llm(self, data: Dict[str, Any], static_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tier 2: LLM-powered analysis (smart, custom recommendations)
        
        This is where the magic happens - LLM analyzes user's specific data!
        """
        
        # Build prompt with user's data
        prompt = f"""You are a wiki and documentation generation expert. Analyze this specific situation:

USER DATA:
{json_lib.dumps(data, indent=2)}

STATIC KNOWLEDGE:
{json_lib.dumps(static_knowledge, indent=2)}

TASK:
Provide detailed, actionable analysis tailored to this specific situation.

Consider:
1. What documentation is needed?
2. How should it be organized?
3. What examples are helpful?
4. What is missing?

Format response as JSON:
{{
    "documentation": "...",
    "structure": [...],
    "examples": [...],
    "confidence": 0.85
}}

JSON Response:"""
        
        try:
            # Call llama.cpp server
            response = await self.client.post(
                f"{self.llm_url}/completion",
                json={
                    "prompt": prompt,
                    "temperature": 0.3,
                    "n_predict": 600,
                    "stop": ["\n\n"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["content"].strip()
                
                # Parse JSON response
                try:
                    if "{" in content:
                        json_start = content.index("{")
                        json_end = content.rindex("}") + 1
                        json_str = content[json_start:json_end]
                        return json_lib.loads(json_str)
                except json_lib.JSONDecodeError:
                    pass
                
                return {
                    "reasoning": content,
                    "confidence": 0.5
                }
            
            return {
                "reasoning": "LLM unavailable",
                "confidence": 0.1
            }
            
        except Exception as e:
            return {
                "reasoning": f"Error: {str(e)}",
                "confidence": 0.1
            }
