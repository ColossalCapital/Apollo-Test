"""
ClickUp Parser Agent - LLM-Powered ClickUp Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse ClickUp data
and extract all-in-one project intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ClickUpParserAgent(Layer1Agent):
    """
    ClickUp Parser - LLM-powered ClickUp parsing
    
    Takes ClickUp data and extracts:
    - All-in-one project insights
    - Time tracking and productivity
    - Goal and OKR progress
    - Documentation and knowledge
    - Automation effectiveness
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="clickup_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered ClickUp parsing with all-in-one intelligence",
            capabilities=["project_parsing", "time_tracking", "goal_tracking", "doc_analysis", "automation_analysis"],
            dependencies=["clickup_connector"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from ClickUp"""
        
        prompt = f"""You are an expert at analyzing all-in-one project management. Extract structured information from this ClickUp data.

CLICKUP DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Workspace and space structure
2. Task hierarchy and relationships
3. Time tracking and productivity metrics
4. Goal and OKR progress
5. Documentation and knowledge base
6. Custom field usage and insights
7. Automation rules and effectiveness
8. Dashboard metrics
9. Team workload and capacity
10. Integration points

Return as JSON with detailed ClickUp analysis including time tracking, goal progress, documentation insights, and automation effectiveness.
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
                await self._store_clickup_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'clickup'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_clickup_in_kg(self, clickup_data: Dict[str, Any]):
        """Store parsed ClickUp data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="clickup_project",
            data=clickup_data,
            graph_type="business"
        )
