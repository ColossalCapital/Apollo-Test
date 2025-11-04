"""
iMessage Parser Agent - LLM-Powered iMessage Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse iMessage data
and extract conversation intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class IMessageParserAgent(Layer1Agent):
    """
    iMessage Parser - LLM-powered iMessage parsing
    
    Takes iMessage data and extracts:
    - Conversation context and sentiment
    - Shared links and media
    - Contact information
    - Location data
    - Confirmation codes
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="imessage_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered iMessage parsing with privacy preservation",
            capabilities=[
                "conversation_analysis",
                "link_extraction",
                "contact_extraction",
                "location_extraction",
                "confirmation_code_detection"
            ],
            dependencies=["imessage_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from iMessage"""
        
        prompt = f"""You are an expert at analyzing text messages. Extract structured information from this iMessage data.

IMESSAGE DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Conversation context and topics
2. Shared links and URLs
3. Contact information (phone numbers, emails)
4. Location data (addresses, coordinates)
5. Confirmation codes (2FA, verification)
6. Dates and times mentioned
7. Action items and commitments
8. Sentiment and tone
9. Important information to remember
10. Privacy-sensitive data (flag for user review)

Return as JSON with detailed iMessage analysis while respecting privacy.
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
                await self._store_imessage_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'imessage'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_imessage_in_kg(self, imessage_data: Dict[str, Any]):
        """Store parsed iMessage data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="imessage_conversation",
            data=imessage_data,
            graph_type="personal"
        )
