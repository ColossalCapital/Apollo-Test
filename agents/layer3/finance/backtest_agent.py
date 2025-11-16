"""
Smart Backtest Agent - Tier 2 LLM-Powered Backtest Analysis

Analyzes backtest results and suggests improvements with LLM intelligence
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
import httpx
import json as json_lib


class BacktestAgent(BaseAgent):
    """Backtest Agent with LLM-powered result analysis and optimization suggestions"""
    
    def __init__(self):
        super().__init__(name="BacktestAgent", model="phi-3-medium")
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze backtest results with hybrid intelligence
        
        Args:
            data: {
                "type": "analyze_results" | "suggest_improvements",
                "backtest_results": {
                    "total_return": 0.45,
                    "sharpe_ratio": 1.2,
                    "max_drawdown": 0.18,
                    "win_rate": 0.58,
                    ...
                },
                "strategy_params": {...},
                "quick_mode": bool (optional)
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
        
        # Step 3: LLM analysis if backtest results provided
        if "backtest_results" in data:
            try:
                llm_analysis = await self.analyze_with_llm(data, static_knowledge)
                
                return {
                    "mode": "llm_powered",
                    "static_knowledge": static_knowledge,
                    "llm_analysis": llm_analysis,
                    "assessment": llm_analysis.get("overall_assessment"),
                    "suggestions": llm_analysis.get("improvement_suggestions"),
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
        """Tier 1: Static backtest analysis knowledge"""
        
        return {
            "performance_metrics": {
                "sharpe_ratio": {
                    "< 1.0": "Poor",
                    "1.0 - 2.0": "Good",
                    "> 2.0": "Excellent"
                },
                "max_drawdown": {
                    "< 10%": "Excellent",
                    "10-20%": "Good",
                    "> 20%": "High risk"
                },
                "win_rate": {
                    "< 40%": "Needs improvement",
                    "40-60%": "Acceptable",
                    "> 60%": "Strong"
                }
            },
            "common_issues": [
                "Overfitting (too many parameters)",
                "Lookahead bias (using future data)",
                "Survivorship bias (only surviving stocks)",
                "Ignoring transaction costs"
            ]
        }
    
    async def analyze_with_llm(self, data: Dict[str, Any], static_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Tier 2: LLM-powered backtest analysis and suggestions"""
        
        # Extract data
        results = data.get('backtest_results', {})
        strategy_params = data.get('strategy_params', {})
        
        prompt = f"""You are a quantitative trading expert. Analyze these backtest results and suggest improvements.

BACKTEST RESULTS:
{json_lib.dumps(results, indent=2)}

STRATEGY PARAMETERS:
{json_lib.dumps(strategy_params, indent=2)}

STATIC KNOWLEDGE:
{json_lib.dumps(static_knowledge, indent=2)}

TASK:
Provide a comprehensive analysis of these backtest results and suggest specific improvements.

Consider:
1. How good are these results? (excellent/good/poor)
2. What are the strengths of this strategy?
3. What are the weaknesses?
4. What specific parameter changes would improve performance?
5. Are there signs of overfitting?
6. What is the risk-adjusted return quality?

Format response as JSON:
{{
    "overall_assessment": "EXCELLENT" or "GOOD" or "POOR",
    "grade": "A" or "B" or "C" or "D" or "F",
    "strengths": [
        "High Sharpe ratio (1.2)",
        "Acceptable win rate (58%)"
    ],
    "weaknesses": [
        "High max drawdown (18%)",
        "Low profit factor"
    ],
    "improvement_suggestions": [
        "Reduce position size to lower drawdown",
        "Add volatility filter to avoid choppy markets",
        "Optimize stop loss (try 1.5 ATR instead of 2 ATR)"
    ],
    "overfitting_risk": "LOW" or "MEDIUM" or "HIGH",
    "recommended_next_steps": [
        "Run walk-forward analysis",
        "Test on different time periods"
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
                    "n_predict": 800,
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
                    "overall_assessment": "UNKNOWN",
                    "reasoning": content,
                    "confidence": 0.5
                }
            
            return {
                "overall_assessment": "UNKNOWN",
                "reasoning": "LLM unavailable",
                "confidence": 0.1
            }
            
        except Exception as e:
            return {
                "overall_assessment": "UNKNOWN",
                "reasoning": f"Error: {str(e)}",
                "confidence": 0.1
            }
