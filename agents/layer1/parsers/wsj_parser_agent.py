"""
WSJ Parser Agent - LLM-Powered Wall Street Journal News Parsing

Layer 1 Data Extraction agent that uses LLM to parse WSJ news
articles and extract structured market and political intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class WSJParserAgent(Layer1Agent):
    """
    WSJ Parser - LLM-powered market and political news parsing
    
    Takes raw WSJ news articles and extracts:
    - Market analysis and trends
    - Political developments
    - Economic indicators
    - Corporate news
    - Policy implications
    - Global events impact
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="wsj_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered WSJ news parsing with market and political analysis",
            capabilities=["news_parsing", "market_analysis", "political_analysis", "policy_impact"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw WSJ news article
        
        Args:
            raw_data: Raw WSJ news article
            
        Returns:
            AgentResult with structured news data
        """
        
        return await self._parse_article(raw_data)
    
    async def _parse_article(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse WSJ article with LLM"""
        
        prompt = f"""You are an expert market and political analyst. Extract structured information from this WSJ article.

RAW WSJ ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary
2. Publication date and time
3. Author(s)
4. Article category (markets, politics, business, economy, opinion)
5. Key events and developments
6. Affected markets and sectors
7. Political implications
8. Economic indicators mentioned
9. Policy changes or proposals
10. Corporate actions
11. Expert analysis and quotes
12. Market sentiment
13. Investment implications
14. Risk factors
15. Historical context

Return as JSON:
{{
    "article_id": "...",
    "headline": "...",
    "summary": "...",
    "published_at": "2025-10-29T22:45:00Z",
    "author": ["Jane Reporter", "John Analyst"],
    "category": "markets",
    "key_events": [
        "Fed signals rate pause",
        "Tech earnings beat expectations"
    ],
    "affected_markets": [
        {{
            "market": "US_equities",
            "sector": "technology",
            "impact": "positive",
            "magnitude": "high"
        }}
    ],
    "political_implications": [
        "Bipartisan support for infrastructure bill",
        "Trade tensions easing"
    ],
    "economic_indicators": [
        {{
            "indicator": "GDP_growth",
            "value": 2.8,
            "period": "Q3_2024",
            "trend": "increasing"
        }},
        {{
            "indicator": "unemployment",
            "value": 3.8,
            "period": "October_2024",
            "trend": "stable"
        }}
    ],
    "policy_changes": [
        {{
            "policy": "interest_rates",
            "change": "hold_steady",
            "rationale": "Inflation moderating",
            "effective_date": "2025-11-01"
        }}
    ],
    "corporate_actions": [
        {{
            "company": "Apple Inc",
            "action": "earnings_beat",
            "details": "EPS $1.52 vs $1.45 expected",
            "market_reaction": "positive"
        }}
    ],
    "expert_analysis": [
        {{
            "expert": "Chief Economist",
            "firm": "Goldman Sachs",
            "opinion": "Soft landing likely",
            "confidence": "high"
        }}
    ],
    "market_sentiment": {{
        "overall": "cautiously_optimistic",
        "equities": "bullish",
        "bonds": "neutral",
        "commodities": "bearish"
    }},
    "investment_implications": [
        "Favor quality growth stocks",
        "Maintain diversification",
        "Watch for policy shifts"
    ],
    "risk_factors": [
        "Geopolitical tensions",
        "Inflation persistence",
        "Credit tightening"
    ],
    "historical_context": "Similar to 1995 soft landing scenario",
    "urgency": "important",
    "source": "WSJ"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3000
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
                metadata={'agent': self.metadata.name, 'source': 'wsj'}
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
        
        # Create economic indicator entities
        for indicator in article_data.get('economic_indicators', []):
            await self.kg_client.create_entity(
                entity_type="economic_indicator",
                data=indicator
            )
        
        # Create policy change entities
        for policy in article_data.get('policy_changes', []):
            await self.kg_client.create_entity(
                entity_type="policy_change",
                data=policy
            )
