"""
Smart Strategy Agent - Tier 2 LLM-Powered Analysis

Combines static knowledge (Tier 1) with LLM intelligence (Tier 2)
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
import httpx
import json as json_lib

class FinanceStrategyAgent(BaseAgent):
    """
    Strategy Agent with 3-Tier Intelligence:
    - Tier 1: Static knowledge (fast, < 10ms)
    - Tier 2: LLM analysis (smart, 1-3 seconds)
    - Tier 3: Personalized (future)
    """
    
    def __init__(self):
        super().__init__(name="StrategyAgent", model="phi-3-medium")
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trading strategy with hybrid intelligence
        
        Args:
            data: {
                "type": "turtle_trading" | "cycle_detection" | etc.,
                "quick_mode": bool (optional, returns static only),
                "asset": str (optional, for LLM analysis),
                "price_data": dict (optional, for LLM analysis)
            }
            
        Returns:
            Analysis with static knowledge and/or LLM insights
        """
        
        # Step 1: Always get static knowledge (fast fallback)
        static_knowledge = self.get_static_knowledge(data)
        
        # Step 2: Quick mode? Return static only
        if data.get('quick_mode'):
            return {
                "mode": "static",
                "knowledge": static_knowledge,
                "response_time_ms": 5
            }
        
        # Step 3: LLM analysis if user provided specific data
        if "price_data" in data or "asset" in data:
            try:
                llm_analysis = await self.analyze_with_llm(data, static_knowledge)
                
                return {
                    "mode": "llm_powered",
                    "static_knowledge": static_knowledge,
                    "llm_analysis": llm_analysis,
                    "recommendation": llm_analysis.get("recommendation"),
                    "confidence": llm_analysis.get("confidence", 0.8),
                    "response_time_ms": 2000
                }
            except Exception as e:
                # LLM failed, return static knowledge
                return {
                    "mode": "static_fallback",
                    "knowledge": static_knowledge,
                    "error": str(e),
                    "response_time_ms": 10
                }
        
        # Step 4: No specific data, return static knowledge
        return {
            "mode": "static",
            "knowledge": static_knowledge,
            "response_time_ms": 5
        }
    
    def get_static_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tier 1: Static knowledge (fast, deterministic)
        
        This is the same as the original StrategyAgent - just documentation
        """
        strategy_type = data.get("type", "turtle_trading")
        
        if strategy_type == "turtle_trading":
            return {
                "strategy": "Turtle Trading",
                "system": "Original Turtle Trading by Richard Dennis",
                "rules": {
                    "entry": "20-day high breakout (System 1) or 55-day high (System 2)",
                    "exit": "10-day low (System 1) or 20-day low (System 2)",
                    "position_sizing": "N-based: Risk 1% of capital per trade, where N = ATR",
                    "stop_loss": "2 ATR below entry price",
                    "pyramiding": "Add up to 4 units, 0.5 ATR apart"
                },
                "example": {
                    "entry_price": 100,
                    "atr": 2.5,
                    "position_size": "Capital * 0.01 / (2 * ATR)",
                    "stop_loss": 95  # 100 - (2 * 2.5)
                }
            }
        
        elif strategy_type == "cycle_detection":
            return {
                "strategy": "Cycle Detection",
                "methods": [
                    "Fourier Transform (frequency analysis)",
                    "Hurst Exponent (trend vs mean reversion)",
                    "Autocorrelation (cyclical patterns)"
                ],
                "market_phases": {
                    "accumulation": "Buy signal",
                    "markup": "Hold/add",
                    "distribution": "Prepare to sell",
                    "markdown": "Sell/short"
                }
            }
        
        return {"strategy": strategy_type, "info": "No static knowledge available"}
    
    async def analyze_with_llm(self, data: Dict[str, Any], static_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tier 2: LLM-powered analysis (smart, custom recommendations)
        
        This is where the magic happens - LLM analyzes YOUR specific data!
        """
        
        # Extract user's data
        asset = data.get('asset', 'Unknown')
        price_data = data.get('price_data', {})
        current_price = price_data.get('current_price', 0)
        twenty_day_high = price_data.get('20_day_high', 0)
        atr = price_data.get('atr', 0)
        
        # Build prompt with context
        prompt = f"""You are a Turtle Trading expert analyzing a specific trading opportunity.

ASSET: {asset}
CURRENT PRICE: ${current_price:,.2f}
20-DAY HIGH: ${twenty_day_high:,.2f}
ATR (N): ${atr:,.2f}

STATIC KNOWLEDGE:
{json_lib.dumps(static_knowledge, indent=2)}

TASK:
Analyze this specific situation and provide actionable trading advice.

Answer these questions:
1. Should we enter a position NOW? (Yes/No and detailed reasoning)
2. What is the optimal position size? (in units, based on 1% risk per ATR)
3. What is the exact stop loss price? (2 ATR below entry)
4. What are the specific risks for THIS asset right now?
5. What is the expected holding period?
6. What is your confidence level? (0.0 to 1.0)

IMPORTANT: Format your response as valid JSON:
{{
    "recommendation": "BUY" or "SELL" or "HOLD",
    "reasoning": "detailed explanation",
    "position_size": 0.4,
    "stop_loss": 42500.00,
    "risks": ["risk 1", "risk 2"],
    "holding_period": "10-15 days",
    "confidence": 0.85
}}

JSON Response:"""
        
        try:
            # Call llama.cpp server
            response = await self.client.post(
                f"{self.llm_url}/completion",
                json={
                    "prompt": prompt,
                    "temperature": 0.3,  # Lower = more deterministic
                    "n_predict": 600,
                    "stop": ["\n\n", "```"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["content"].strip()
                
                # Parse JSON response
                try:
                    # Try to extract JSON from response
                    if "{" in content:
                        json_start = content.index("{")
                        json_end = content.rindex("}") + 1
                        json_str = content[json_start:json_end]
                        analysis = json_lib.loads(json_str)
                        return analysis
                    else:
                        # No JSON found, return text response
                        return {
                            "recommendation": "HOLD",
                            "reasoning": content,
                            "confidence": 0.5
                        }
                except json_lib.JSONDecodeError as e:
                    # JSON parsing failed, return text
                    return {
                        "recommendation": "HOLD",
                        "reasoning": f"LLM response (non-JSON): {content}",
                        "confidence": 0.4
                    }
            else:
                # LLM API error
                return {
                    "recommendation": "HOLD",
                    "reasoning": f"LLM API error: {response.status_code}",
                    "confidence": 0.1
                }
                
        except Exception as e:
            # Connection error or other exception
            return {
                "recommendation": "HOLD",
                "reasoning": f"LLM unavailable: {str(e)}",
                "confidence": 0.1
            }
    
    async def analyze_turtle_trading(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method for Turtle Trading analysis"""
        data["type"] = "turtle_trading"
        return await self.analyze(data)
    
    async def analyze_cycle_detection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method for Cycle Detection analysis"""
        data["type"] = "cycle_detection"
        return await self.analyze(data)
