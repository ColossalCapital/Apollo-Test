"""
Location Recognition Agent - LLM-Powered Location Entity Recognition

Layer 2 Entity Recognition agent that identifies and extracts location entities.
"""

from typing import Dict, Any
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class LocationRecognitionAgent(Layer2Agent):
    """
    Location Recognition - Identifies location entities
    
    Extracts:
    - Cities, states, countries
    - Addresses and coordinates
    - Landmarks and venues
    - Geographic regions
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="location_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered location entity recognition",
            capabilities=["location_extraction", "address_parsing", "geocoding"],
            dependencies=["document_parser"],
            
            # Metadata for filtering
            entity_types=[EntityType.UNIVERSAL],
            app_contexts=[AppContext.ATLAS, AppContext.DELT, AppContext.AKASHIC],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def recognize(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """Recognize location entities from parsed data"""
        
        text = parsed_data.get('text', '')
        
        prompt = f"""Extract all location entities from this text.

TEXT:
{text}

Extract:
1. Cities (e.g., "New York", "London")
2. States/Provinces (e.g., "California", "Ontario")
3. Countries (e.g., "United States", "Canada")
4. Addresses (e.g., "123 Main St, New York, NY 10001")
5. Landmarks (e.g., "Empire State Building")
6. Regions (e.g., "Silicon Valley", "Wall Street")

Return as JSON with location entities and their types.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            locations = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_locations_in_kg(locations)
            
            return AgentResult(
                success=True,
                data=locations,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_locations_in_kg(self, locations: Dict[str, Any]):
        """Store location entities in knowledge graph"""
        if not self.kg_client:
            return
        
        for location in locations.get('locations', []):
            await self.kg_client.create_entity(
                entity_type="location",
                data=location,
                graph_type="geographic"
            )
