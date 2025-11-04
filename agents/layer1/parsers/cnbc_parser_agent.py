"""
CNBC Parser Agent - LLM-Powered CNBC News Parsing

Layer 1 Data Extraction agent that uses LLM to parse CNBC news
articles and extract structured market intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class CNBCParserAgent(Layer1Agent):
    """
    CNBC Parser - LLM-powered market news parsing
    
    Takes raw CNBC news articles and extracts:
    - Headline and summary
    - Stock picks and recommendations
    - Analyst opinions
    - Trading strategies
    - Market sentiment
    - Price targets
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="cnbc_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered CNBC news parsing with trading signals",
            capabilities=["news_parsing", "stock_picks", "analyst_opinions", "trading_signals"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw CNBC news article
        
        Args:
            raw_data: Raw CNBC news article
            
        Returns:
            AgentResult with structured news data and trading signals
        """
        
        return await self._parse_article(raw_data)
    
    async def _parse_article(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse CNBC article with LLM"""
        
        prompt = f"""You are an expert at parsing CNBC market news. Extract structured information from this article.

RAW CNBC ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary
2. Publication date and time
3. Author/analyst
4. Article category (markets, investing, earnings, analysis)
5. Stock picks and recommendations (buy/sell/hold)
6. Price targets and timeframes
7. Analyst opinions and ratings
8. Trading strategies mentioned
9. Market sentiment
10. Key catalysts
11. Risk factors
12. Actionable insights

Return as JSON:
{{
    "article_id": "...",
    "headline": "...",
    "summary": "...",
    "published_at": "2025-10-29T22:00:00Z",
    "author": "Jim Cramer",
    "category": "stock_picks",
    "stock_picks": [
        {{
            "symbol": "AAPL",
            "recommendation": "buy",
            "price_target": 195.00,
            "timeframe": "6_months",
            "reasoning": "Strong iPhone sales, AI momentum"
        }}
    ],
    "analyst_opinions": [
        {{
            "analyst": "Morgan Stanley",
            "rating": "overweight",
            "action": "upgrade"
        }}
    ],
    "trading_strategies": [
        "Buy on dips below $180",
        "Set stop loss at $175"
    ],
    "sentiment": {{
        "overall": "bullish",
        "score": 0.80,
        "confidence": 0.85
    }},
    "catalysts": [
        "Q4 earnings beat expected",
        "New product launch in Q1"
    ],
    "risks": [
        "Regulatory concerns",
        "Supply chain issues"
    ],
    "actionable_insights": [
        "Consider accumulating on weakness",
        "Watch for breakout above $190"
    ],
    "urgency": "important",
    "source": "CNBC"
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
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_article_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'cnbc'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_article_in_kg(self, article_data: Dict[str, Any]):
        """Store parsed article in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="news_article",
            data=article_data
        )
        
        # Create trading signal entities
        for pick in article_data.get('stock_picks', []):
            await self.kg_client.create_entity(
                entity_type="trading_signal",
                data={
                    'symbol': pick['symbol'],
                    'recommendation': pick['recommendation'],
                    'price_target': pick['price_target'],
                    'source': 'cnbc',
                    'article_id': article_data['article_id']
                }
            )
