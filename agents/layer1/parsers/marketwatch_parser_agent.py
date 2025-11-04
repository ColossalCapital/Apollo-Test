"""
MarketWatch Parser Agent - LLM-Powered MarketWatch News Parsing

Layer 1 Data Extraction agent that uses LLM to parse MarketWatch news
and extract market sentiment intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class MarketWatchParserAgent(Layer1Agent):
    """
    MarketWatch Parser - LLM-powered market sentiment parsing
    
    Takes raw MarketWatch articles and extracts:
    - Market sentiment indicators
    - Stock recommendations
    - Sector rotation signals
    - Fear/greed indicators
    - Trading volume analysis
    - Technical levels
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="marketwatch_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered MarketWatch parsing with sentiment analysis",
            capabilities=["sentiment_parsing", "stock_recommendations", "technical_analysis", "volume_analysis"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from raw MarketWatch article"""
        
        prompt = f"""You are an expert at analyzing market sentiment. Extract structured information from this MarketWatch article.

RAW MARKETWATCH ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary
2. Overall market sentiment (fear, greed, neutral)
3. Sector sentiment (which sectors bullish/bearish)
4. Stock mentions with sentiment
5. Technical levels (support, resistance)
6. Volume analysis
7. Fear/greed indicators
8. Contrarian signals
9. Institutional activity
10. Retail sentiment
11. Trading recommendations

Return as JSON:
{{
    "article_id": "...",
    "headline": "...",
    "summary": "...",
    "published_at": "2025-10-29T23:00:00Z",
    "market_sentiment": {{
        "overall": "cautiously_bullish",
        "fear_greed_index": 65,
        "sentiment_score": 0.35,
        "confidence": 0.80
    }},
    "sector_sentiment": [
        {{"sector": "technology", "sentiment": "bullish", "score": 0.75}},
        {{"sector": "energy", "sentiment": "bearish", "score": -0.45}},
        {{"sector": "financials", "sentiment": "neutral", "score": 0.05}}
    ],
    "stock_mentions": [
        {{
            "ticker": "AAPL",
            "sentiment": "bullish",
            "price": 180.50,
            "target": 200.00,
            "support": 175.00,
            "resistance": 185.00,
            "recommendation": "buy"
        }}
    ],
    "technical_analysis": {{
        "sp500": {{
            "current": 4500,
            "support": 4450,
            "resistance": 4550,
            "trend": "uptrend",
            "momentum": "positive"
        }}
    }},
    "volume_analysis": {{
        "overall_volume": "above_average",
        "buying_pressure": "strong",
        "selling_pressure": "weak",
        "institutional_flow": "accumulation"
    }},
    "contrarian_signals": [
        "Extreme optimism in tech",
        "Retail FOMO building"
    ],
    "trading_recommendations": [
        "Take profits in extended names",
        "Look for pullback entries",
        "Maintain core positions"
    ],
    "source": "marketwatch"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_sentiment_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'marketwatch'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_sentiment_in_kg(self, sentiment_data: Dict[str, Any]):
        """Store parsed sentiment in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="market_sentiment",
            data=sentiment_data
        )
