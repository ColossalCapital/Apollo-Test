"""
Smart Portfolio Agent - Tier 2 LLM-Powered Portfolio Optimization

Combines static knowledge with LLM intelligence for personalized portfolio advice
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
import httpx
import json as json_lib


class PortfolioAgent(BaseAgent):
    """Portfolio Agent with LLM-powered personalized optimization"""
    
    def __init__(self):
        super().__init__(name="PortfolioAgent", model="phi-3-medium")
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze portfolio with hybrid intelligence
        
        Args:
            data: {
                "type": "optimize" | "rebalance" | "risk",
                "portfolio": {"BTC": 0.4, "ETH": 0.3, ...},
                "quick_mode": bool (optional),
                "user_profile": {
                    "risk_tolerance": "conservative" | "moderate" | "aggressive",
                    "investment_horizon": "short" | "medium" | "long",
                    "goals": ["growth", "income", "preservation"]
                }
            }
        """
        
        # Step 1: Get static knowledge
        static_knowledge = self.get_static_knowledge(data)
        
        # Step 2: Quick mode? Return static only
        if data.get('quick_mode'):
            return {
                "mode": "static",
                "knowledge": static_knowledge
            }
        
        # Step 3: LLM analysis if user profile provided
        if "user_profile" in data or "portfolio" in data:
            try:
                llm_analysis = await self.analyze_with_llm(data, static_knowledge)
                
                return {
                    "mode": "llm_powered",
                    "static_knowledge": static_knowledge,
                    "llm_analysis": llm_analysis,
                    "optimized_portfolio": llm_analysis.get("optimized_allocation"),
                    "confidence": llm_analysis.get("confidence", 0.8)
                }
            except Exception as e:
                return {
                    "mode": "static_fallback",
                    "knowledge": static_knowledge,
                    "error": str(e)
                }
        
        return {
            "mode": "static",
            "knowledge": static_knowledge
        }
    
    def get_static_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tier 1: Static portfolio optimization knowledge"""
        
        analysis_type = data.get("type", "optimize")
        
        if analysis_type == "optimize":
            return {
                "optimization_methods": {
                    "mean_variance": "Markowitz Modern Portfolio Theory",
                    "max_sharpe": "Maximize risk-adjusted returns",
                    "min_volatility": "Minimize portfolio volatility",
                    "risk_parity": "Equal risk contribution from each asset"
                },
                "example": {
                    "current": {"BTC": 0.40, "ETH": 0.30, "STOCKS": 0.20, "BONDS": 0.10},
                    "optimized": {"BTC": 0.35, "ETH": 0.25, "STOCKS": 0.25, "BONDS": 0.15},
                    "improvement": "Sharpe ratio: 0.71 → 0.93 (+31%)"
                }
            }
        
        elif analysis_type == "risk":
            return {
                "risk_metrics": {
                    "var_95": "Value at Risk (95% confidence)",
                    "cvar_95": "Conditional VaR (expected loss beyond VaR)",
                    "beta": "Volatility vs market",
                    "max_drawdown": "Largest peak-to-trough decline"
                }
            }
        
        return {"type": analysis_type}
    
    async def analyze_with_llm(self, data: Dict[str, Any], static_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Tier 2: LLM-powered personalized portfolio optimization"""
        
        # Extract user data
        portfolio = data.get('portfolio', {})
        user_profile = data.get('user_profile', {})
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        horizon = user_profile.get('investment_horizon', 'medium')
        goals = user_profile.get('goals', ['growth'])
        
        # Build prompt
        prompt = f"""You are a portfolio optimization expert. Analyze this portfolio and provide personalized advice.

CURRENT PORTFOLIO:
{json_lib.dumps(portfolio, indent=2)}

USER PROFILE:
- Risk Tolerance: {risk_tolerance}
- Investment Horizon: {horizon}
- Goals: {', '.join(goals)}

STATIC KNOWLEDGE:
{json_lib.dumps(static_knowledge, indent=2)}

TASK:
Provide a personalized portfolio optimization that matches this user's profile.

Consider:
1. Is the current allocation appropriate for their risk tolerance?
2. What adjustments would better match their goals?
3. What is the expected return and risk of the optimized portfolio?
4. What specific actions should they take?

Format response as JSON:
{{
    "optimized_allocation": {{
        "BTC": 0.35,
        "ETH": 0.25,
        "STOCKS": 0.25,
        "BONDS": 0.15
    }},
    "expected_return": 0.28,
    "expected_volatility": 0.30,
    "sharpe_ratio": 0.93,
    "reasoning": "detailed explanation tailored to user's profile",
    "action_items": [
        "Reduce BTC by 5% (too risky for moderate profile)",
        "Increase bonds by 5% (better stability)"
    ],
    "confidence": 0.85
}}

JSON Response:"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/completion",
                json={
                    "prompt": prompt,
                    "temperature": 0.3,
                    "n_predict": 700,
                    "stop": ["\n\n"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["content"].strip()
                
                # Parse JSON
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
