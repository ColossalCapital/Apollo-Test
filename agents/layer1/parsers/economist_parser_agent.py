"""
Economist Parser Agent - LLM-Powered Economist News Parsing

Layer 1 Data Extraction agent that uses LLM to parse The Economist articles
and extract structured global intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class EconomistParserAgent(Layer1Agent):
    """
    Economist Parser - LLM-powered global politics and economics parsing
    
    Takes raw Economist articles and extracts:
    - Global political analysis
    - Economic policy insights
    - Geopolitical implications
    - Long-term trends
    - Data-driven analysis
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="economist_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Economist parsing with global intelligence",
            capabilities=["news_parsing", "political_analysis", "economic_analysis", "trend_detection"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from raw Economist article"""
        
        prompt = f"""You are an expert geopolitical and economic analyst. Extract structured information from this Economist article.

RAW ECONOMIST ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary
2. Article category (politics, economics, business, technology, science)
3. Geographic focus (countries, regions)
4. Key themes and topics
5. Political analysis
6. Economic implications
7. Geopolitical context
8. Long-term trends
9. Data and statistics mentioned
10. Expert opinions
11. Policy recommendations
12. Historical context
13. Future predictions

Return as JSON:
{{
    "article_id": "...",
    "headline": "...",
    "summary": "...",
    "published_at": "2025-10-29T23:00:00Z",
    "category": "global_politics",
    "geographic_focus": [
        {{"country": "China", "region": "Asia", "importance": "primary"}},
        {{"country": "United States", "region": "North America", "importance": "secondary"}}
    ],
    "themes": [
        "us_china_relations",
        "trade_policy",
        "technology_competition"
    ],
    "political_analysis": {{
        "key_players": ["Xi Jinping", "Joe Biden"],
        "power_dynamics": "Shifting balance in Asia-Pacific",
        "policy_changes": ["Export controls on semiconductors"],
        "implications": "Increased tech decoupling"
    }},
    "economic_implications": {{
        "affected_sectors": ["technology", "manufacturing", "finance"],
        "market_impact": "negative_short_term",
        "gdp_impact": -0.5,
        "trade_impact": "Supply chain disruption"
    }},
    "geopolitical_context": {{
        "alliances": ["US-Japan-South Korea", "China-Russia"],
        "tensions": ["Taiwan Strait", "South China Sea"],
        "cooperation_areas": ["Climate change", "Pandemic response"]
    }},
    "long_term_trends": [
        "Multipolar world order",
        "Technology bifurcation",
        "Regional trade blocs"
    ],
    "data_statistics": [
        {{"metric": "China GDP growth", "value": 5.2, "period": "2024"}},
        {{"metric": "US-China trade", "value": 690000000000, "period": "2023"}}
    ],
    "expert_opinions": [
        {{
            "expert": "Henry Kissinger",
            "affiliation": "Former US Secretary of State",
            "opinion": "Managed competition necessary",
            "credibility": "high"
        }}
    ],
    "policy_recommendations": [
        "Establish guardrails for competition",
        "Maintain diplomatic channels",
        "Focus on mutual interests"
    ],
    "historical_context": "Similar to US-Soviet Cold War but with economic interdependence",
    "predictions": [
        {{
            "prediction": "Continued tech decoupling",
            "timeframe": "5-10 years",
            "confidence": 0.75
        }}
    ],
    "source": "economist"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_article_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'economist'}
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
