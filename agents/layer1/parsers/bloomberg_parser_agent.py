"""
Bloomberg Parser Agent - LLM-Powered Bloomberg News Parsing

Layer 1 Data Extraction agent that uses LLM to parse Bloomberg news
articles and extract structured financial intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class BloombergParserAgent(Layer1Agent):
    """
    Bloomberg Parser - LLM-powered financial news parsing
    
    Takes raw Bloomberg news articles and extracts:
    - Headline and summary
    - Market impact analysis
    - Affected securities
    - Sentiment (bullish/bearish/neutral)
    - Key entities (companies, people, sectors)
    - Trading signals
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="bloomberg_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Bloomberg news parsing with sentiment analysis",
            capabilities=["news_parsing", "sentiment_analysis", "market_impact", "entity_extraction"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw Bloomberg news article
        
        Args:
            raw_data: Raw Bloomberg news article
            
        Returns:
            AgentResult with structured news data and sentiment
        """
        
        return await self._parse_article(raw_data)
    
    async def _parse_article(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Bloomberg article with LLM"""
        
        prompt = f"""You are an expert financial news analyst. Extract structured information from this Bloomberg article.

RAW BLOOMBERG ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary (2-3 sentences)
2. Publication date and time
3. Author(s)
4. Article category (earnings, M&A, policy, markets, etc.)
5. Affected securities (stocks, bonds, commodities, currencies)
6. Key entities (companies, executives, institutions)
7. Market sentiment (bullish, bearish, neutral) with confidence
8. Market impact (high, medium, low)
9. Key facts and figures (prices, percentages, amounts)
10. Trading implications
11. Related topics/themes
12. Urgency level (breaking, important, routine)

Return as JSON:
{{
    "article_id": "...",
    "headline": "...",
    "summary": "...",
    "published_at": "2025-10-29T22:00:00Z",
    "author": ["John Smith", "Jane Doe"],
    "category": "earnings",
    "securities": [
        {{"symbol": "AAPL", "type": "stock", "impact": "positive"}},
        {{"symbol": "MSFT", "type": "stock", "impact": "neutral"}}
    ],
    "entities": [
        {{"name": "Apple Inc", "type": "company", "role": "primary"}},
        {{"name": "Tim Cook", "type": "person", "role": "ceo"}}
    ],
    "sentiment": {{
        "overall": "bullish",
        "score": 0.75,
        "confidence": 0.85,
        "reasoning": "Strong earnings beat, raised guidance"
    }},
    "market_impact": "high",
    "key_facts": [
        "EPS beat by 15%",
        "Revenue up 12% YoY",
        "Raised FY guidance"
    ],
    "trading_implications": [
        "Potential upside momentum",
        "Watch for profit-taking at resistance"
    ],
    "topics": ["earnings", "tech_sector", "guidance"],
    "urgency": "important",
    "source": "Bloomberg"
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
                metadata={'agent': self.metadata.name, 'source': 'bloomberg'}
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
        
        # Create news article entity
        await self.kg_client.create_entity(
            entity_type="news_article",
            data=article_data
        )
        
        # Create relationships for affected securities
        for security in article_data.get('securities', []):
            await self.kg_client.create_relationship(
                from_entity=article_data['article_id'],
                to_entity=security['symbol'],
                relationship_type='affects',
                properties={'impact': security['impact']}
            )
        
        # Create entities for companies/people mentioned
        for entity in article_data.get('entities', []):
            await self.kg_client.create_entity(
                entity_type=entity['type'],
                data=entity
            )
