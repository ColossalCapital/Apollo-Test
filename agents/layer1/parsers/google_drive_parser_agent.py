"""
Google Drive Parser Agent - LLM-Powered Google Drive Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse Google Drive data
and extract document intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class GoogleDriveParserAgent(Layer1Agent):
    """
    Google Drive Parser - LLM-powered Google Drive parsing
    
    Takes Google Drive data and extracts:
    - Document content and structure
    - File organization patterns
    - Collaboration insights
    - Version history analysis
    - Sharing permissions
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="google_drive_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Google Drive parsing for document intelligence",
            capabilities=[
                "document_analysis",
                "file_organization",
                "collaboration_insights",
                "version_tracking",
                "permission_analysis"
            ],
            dependencies=["google_drive_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL, EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from Google Drive"""
        
        prompt = f"""You are an expert at analyzing Google Drive data. Extract structured information from this Google Drive data.

GOOGLE DRIVE DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Document content summaries
2. File organization and folder structure
3. Collaboration patterns (who works with whom)
4. Version history and change patterns
5. Sharing permissions and access control
6. Document types and categories
7. Important documents and priorities
8. Duplicate files and cleanup opportunities
9. Storage usage patterns
10. Cross-document references

Return as JSON with detailed Google Drive analysis.
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
                await self._store_drive_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'google_drive'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_drive_in_kg(self, drive_data: Dict[str, Any]):
        """Store parsed Google Drive data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="google_drive_analysis",
            data=drive_data,
            graph_type="business"
        )
