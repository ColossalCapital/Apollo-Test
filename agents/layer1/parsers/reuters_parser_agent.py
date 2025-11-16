"""
Reuters Parser Agent - LLM-Powered Reuters News Parsing

Layer 1 Data Extraction agent that uses LLM to parse Reuters news
articles and extract structured global news intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ReutersParserAgent(Layer1Agent):
    """
    Reuters Parser - LLM-powered global news parsing
    
    Takes raw Reuters news articles and extracts:
    - Headline and summary
    - Geographic focus
    - Affected markets/sectors
    - Sentiment and impact
    - Key entities and events
    - Geopolitical implications
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="reuters_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Reuters news parsing with geopolitical analysis",
            capabilities=["news_parsing", "geopolitical_analysis", "market_impact", "entity_extraction"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw Reuters news article
        
        Args:
            raw_data: Raw Reuters news article
            
        Returns:
            AgentResult with structured news data
        """
        
        return await self._parse_article(raw_data)
    
    async def _parse_article(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Reuters article with LLM"""
        
        prompt = f"""You are an expert global news analyst. Extract structured information from this Reuters article.

RAW REUTERS ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary
2. Publication date and time
3. Author(s) and location
4. Article category (politics, business, markets, world, etc.)
5. Geographic focus (countries, regions)
6. Affected markets/sectors
7. Key entities (governments, companies, leaders)
8. Geopolitical implications
9. Market sentiment and impact
10. Key facts and developments
11. Related events/context
12. Urgency level

Return as JSON:
{{
    "article_id": "...",
    "headline": "...",
    "summary": "...",
    "published_at": "2025-10-29T22:00:00Z",
    "author": ["Jane Smith"],
    "location": "Washington",
    "category": "politics",
    "geographic_focus": [
        {{"country": "USA", "region": "North America"}},
        {{"country": "China", "region": "Asia"}}
    ],
    "affected_markets": [
        {{"market": "US_equities", "impact": "negative"}},
        {{"market": "commodities", "impact": "positive"}}
    ],
    "entities": [
        {{"name": "Federal Reserve", "type": "institution", "role": "primary"}},
        {{"name": "Jerome Powell", "type": "person", "role": "fed_chair"}}
    ],
    "geopolitical_implications": [
        "Trade tensions escalating",
        "Potential policy shifts"
    ],
    "sentiment": {{
        "overall": "bearish",
        "score": -0.45,
        "confidence": 0.80,
        "reasoning": "Policy uncertainty, trade concerns"
    }},
    "market_impact": "high",
    "key_facts": [
        "Fed signals rate hold",
        "Trade deficit widens 8%"
    ],
    "related_events": ["G20_summit", "trade_negotiations"],
    "urgency": "breaking",
    "source": "Reuters"
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
                metadata={'agent': self.metadata.name, 'source': 'reuters'}
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
        
        # Create geopolitical event entities
        for event in article_data.get('related_events', []):
            await self.kg_client.create_entity(
                entity_type="geopolitical_event",
                data={'event_name': event, 'article_id': article_data['article_id']}
            )
