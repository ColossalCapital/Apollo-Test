"""
Politico Parser Agent - LLM-Powered Political News Parsing

Layer 1 Data Extraction agent that uses LLM to parse Politico articles
and extract political intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class PoliticoParserAgent(Layer1Agent):
    """
    Politico Parser - LLM-powered political news parsing
    
    Takes raw Politico articles and extracts:
    - Political analysis and implications
    - Legislative tracking
    - Election coverage and polling
    - Policy impact analysis
    - Congressional dynamics
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="politico_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Politico parsing with political intelligence",
            capabilities=["news_parsing", "political_analysis", "legislative_tracking", "election_coverage"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from raw Politico article"""
        
        prompt = f"""You are an expert political analyst. Extract structured information from this Politico article.

RAW POLITICO ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary
2. Article category (congress, white_house, campaigns, policy, states)
3. Key political figures mentioned
4. Legislative items (bills, votes, committees)
5. Political parties and positions
6. Policy implications
7. Election relevance (if applicable)
8. Polling data (if mentioned)
9. Congressional dynamics
10. Stakeholder analysis
11. Timeline and deadlines
12. Potential outcomes

Return as JSON with detailed political analysis.
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
                metadata={'agent': self.metadata.name, 'source': 'politico'}
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
