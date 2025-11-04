"""
Contacts Parser Agent - LLM-Powered Contacts Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse contacts data
and extract relationship intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class ContactsParserAgent(Layer1Agent):
    """
    Contacts Parser - LLM-powered contacts parsing
    
    Takes contacts data and extracts:
    - Relationship categorization
    - Contact enrichment
    - Network mapping
    - Communication patterns
    - Relationship strength
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="contacts_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered contacts parsing for relationship intelligence",
            capabilities=[
                "relationship_categorization",
                "contact_enrichment",
                "network_mapping",
                "communication_tracking",
                "relationship_strength"
            ],
            dependencies=[],
            
            # Metadata for filtering
            entity_types=[EntityType.UNIVERSAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from contacts"""
        
        prompt = f"""You are an expert at analyzing contact data. Extract structured information from this contacts data.

CONTACTS DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Relationship categorization (family, friend, colleague, client, etc.)
2. Contact enrichment (infer missing information)
3. Network mapping (who knows whom)
4. Communication patterns (frequency, channels)
5. Relationship strength indicators
6. Important dates (birthdays, anniversaries)
7. Professional connections (companies, roles)
8. Geographic distribution
9. Contact groups and clusters
10. Duplicate detection and merging opportunities

Return as JSON with detailed contacts analysis and relationship intelligence.
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
                await self._store_contacts_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'contacts'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_contacts_in_kg(self, contacts_data: Dict[str, Any]):
        """Store parsed contacts data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="contacts_analysis",
            data=contacts_data,
            graph_type="personal"
        )
