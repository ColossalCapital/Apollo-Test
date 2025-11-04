"""
Notion Parser Agent - LLM-Powered Notion Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse Notion data
and extract knowledge and documentation intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class NotionParserAgent(Layer1Agent):
    """
    Notion Parser - LLM-powered Notion parsing
    
    Takes Notion data and extracts:
    - Documentation structure
    - Knowledge organization
    - Project information
    - Task and todo items
    - Database relationships
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="notion_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Notion parsing for knowledge management",
            capabilities=[
                "documentation_analysis",
                "knowledge_extraction",
                "project_parsing",
                "task_extraction",
                "database_relationship_mapping"
            ],
            dependencies=["notion_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL, EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS, AppContext.AKASHIC],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from Notion"""
        
        prompt = f"""You are an expert at analyzing Notion workspaces. Extract structured information from this Notion data.

NOTION DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Documentation structure and hierarchy
2. Knowledge topics and categories
3. Project information and status
4. Tasks and todo items
5. Database relationships and connections
6. Key insights and learnings
7. Meeting notes and decisions
8. Process documentation
9. Templates and workflows
10. Cross-page references and links

Return as JSON with detailed Notion workspace analysis.
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
                await self._store_notion_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'notion'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_notion_in_kg(self, notion_data: Dict[str, Any]):
        """Store parsed Notion data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="notion_workspace",
            data=notion_data,
            graph_type="business"
        )
