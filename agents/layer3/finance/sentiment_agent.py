"""
Smart Sentiment Agent - Tier 2 LLM-Powered Sentiment Analysis

Analyzes news, social media, and market data with LLM intelligence
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent
import httpx
import json as json_lib


class SentimentAgent(BaseAgent):
    """Sentiment Agent with LLM-powered news and social analysis"""
    
    def __init__(self):
        super().__init__(name="SentimentAgent", model="phi-3-medium")
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market sentiment with hybrid intelligence
        
        Args:
            data: {
                "type": "news" | "social" | "fear_greed",
                "asset": "BTC" | "ETH" | "AAPL",
                "news_headlines": [...] (optional),
                "social_data": {...} (optional),
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
        
        # Step 3: LLM analysis if news/social data provided
        if "news_headlines" in data or "social_data" in data:
            try:
                llm_analysis = await self.analyze_with_llm(data, static_knowledge)
                
                return {
                    "mode": "llm_powered",
                    "static_knowledge": static_knowledge,
                    "llm_analysis": llm_analysis,
                    "sentiment": llm_analysis.get("overall_sentiment"),
                    "signal": llm_analysis.get("trading_signal"),
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
        """Tier 1: Static sentiment analysis knowledge"""
        
        return {
            "sentiment_sources": [
                "News sentiment (FinBERT NLP)",
                "Social media (Twitter, Reddit, StockTwits)",
                "Fear & Greed Index",
                "On-chain metrics (crypto)",
                "Options sentiment (put/call ratio)"
            ],
            "sentiment_scale": {
                "very_bullish": "> 0.7",
                "bullish": "0.3 to 0.7",
                "neutral": "-0.3 to 0.3",
                "bearish": "-0.7 to -0.3",
                "very_bearish": "< -0.7"
            },
            "contrarian_signals": {
                "extreme_bullish": "Potential top (> 90% bullish)",
                "extreme_bearish": "Potential bottom (> 90% bearish)"
            }
        }
    
    async def analyze_with_llm(self, data: Dict[str, Any], static_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Tier 2: LLM-powered sentiment analysis"""
        
        # Extract data
        asset = data.get('asset', 'Unknown')
        news_headlines = data.get('news_headlines', [])
        social_data = data.get('social_data', {})
        
        # Build prompt
        news_text = "\n".join([f"- {headline}" for headline in news_headlines[:10]]) if news_headlines else "No news data"
        social_text = json_lib.dumps(social_data, indent=2) if social_data else "No social data"
        
        prompt = f"""You are a market sentiment analyst. Analyze sentiment for {asset} based on this data:

RECENT NEWS HEADLINES:
{news_text}

SOCIAL MEDIA DATA:
{social_text}

STATIC KNOWLEDGE:
{json_lib.dumps(static_knowledge, indent=2)}

TASK:
Analyze the overall market sentiment and provide a trading signal.

Consider:
1. What is the dominant sentiment from news? (bullish/bearish/neutral)
2. What is the social media sentiment? (bullish/bearish/neutral)
3. Are there any contrarian signals? (extreme sentiment)
4. What is the recommended trading action?
5. What are the key factors driving sentiment?

Format response as JSON:
{{
    "overall_sentiment": "BULLISH" or "BEARISH" or "NEUTRAL",
    "sentiment_score": 0.75,
    "news_sentiment": "BULLISH",
    "social_sentiment": "BULLISH",
    "trading_signal": "BUY" or "SELL" or "HOLD",
    "key_factors": [
        "Positive earnings report",
        "Strong social media buzz"
    ],
    "contrarian_warning": false,
    "reasoning": "detailed explanation",
    "confidence": 0.85
}}

JSON Response:"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/completion",
                json={
                    "prompt": prompt,
                    "temperature": 0.4,
                    "n_predict": 600,
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
                    "overall_sentiment": "NEUTRAL",
                    "reasoning": content,
                    "confidence": 0.5
                }
            
            return {
                "overall_sentiment": "NEUTRAL",
                "reasoning": "LLM unavailable",
                "confidence": 0.1
            }
            
        except Exception as e:
            return {
                "overall_sentiment": "NEUTRAL",
                "reasoning": f"Error: {str(e)}",
                "confidence": 0.1
            }
