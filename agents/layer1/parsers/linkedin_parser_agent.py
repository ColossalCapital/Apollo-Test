"""
LinkedIn Parser Agent - LLM-Powered LinkedIn Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse LinkedIn data
and extract professional network intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class LinkedInParserAgent(Layer1Agent):
    """
    LinkedIn Parser - LLM-powered LinkedIn parsing
    
    Takes LinkedIn data and extracts:
    - Professional network analysis
    - Connection insights
    - Job and career patterns
    - Content engagement
    - Industry trends
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="linkedin_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered LinkedIn parsing for professional network intelligence",
            capabilities=[
                "network_analysis",
                "connection_insights",
                "career_tracking",
                "content_engagement",
                "industry_trends"
            ],
            dependencies=["linkedin_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL, EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from LinkedIn"""
        
        prompt = f"""You are an expert at analyzing LinkedIn data. Extract structured information from this LinkedIn data.

LINKEDIN DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Professional network structure
2. Connection insights (who, when, how)
3. Job opportunities and applications
4. Career progression patterns
5. Content engagement (posts, articles, comments)
6. Industry trends and topics
7. Skill endorsements and recommendations
8. Company follows and interests
9. Messaging patterns and relationships
10. Professional development opportunities

Return as JSON with detailed LinkedIn analysis and professional insights.
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
            
            if self.kg_client:
                await self._store_linkedin_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'linkedin'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_linkedin_in_kg(self, linkedin_data: Dict[str, Any]):
        """Store parsed LinkedIn data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="linkedin_analysis",
            data=linkedin_data,
            graph_type="social"
        )
