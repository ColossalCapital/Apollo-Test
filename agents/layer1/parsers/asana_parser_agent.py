"""
Asana Parser Agent - LLM-Powered Asana Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse Asana data
and extract cross-functional project intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class AsanaParserAgent(Layer1Agent):
    """
    Asana Parser - LLM-powered Asana parsing
    
    Takes Asana data and extracts:
    - Cross-functional project insights
    - Team collaboration patterns
    - Goal and portfolio tracking
    - Resource allocation
    - Campaign and initiative progress
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="asana_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Asana parsing with cross-functional intelligence",
            capabilities=["project_parsing", "team_collaboration", "goal_tracking", "resource_allocation"],
            dependencies=["asana_connector"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from Asana"""
        
        prompt = f"""You are an expert at analyzing cross-functional projects. Extract structured information from this Asana data.

ASANA DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Project and portfolio structure
2. Task dependencies and relationships
3. Team collaboration patterns
4. Goal progress and metrics
5. Resource allocation
6. Timeline and milestone tracking
7. Custom field usage
8. Cross-functional workflows
9. Bottlenecks and blockers
10. Campaign effectiveness

Return as JSON with detailed Asana analysis including cross-functional insights, team collaboration patterns, and goal tracking.
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
                await self._store_asana_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'asana'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_asana_in_kg(self, asana_data: Dict[str, Any]):
        """Store parsed Asana data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="asana_project",
            data=asana_data,
            graph_type="business"
        )
