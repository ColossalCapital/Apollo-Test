"""
Travel Parser Agent - LLM-Powered Travel Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse travel data
from multiple sources (Google Maps, Uber, Airbnb).
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class TravelParserAgent(Layer1Agent):
    """
    Travel Parser - LLM-powered travel data parsing
    
    Takes travel data and extracts:
    - Trip itineraries
    - Location patterns
    - Travel expenses
    - Frequent destinations
    - Travel preferences
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="travel_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered travel data parsing",
            capabilities=[
                "itinerary_extraction",
                "location_analysis",
                "expense_tracking",
                "pattern_detection",
                "preference_learning"
            ],
            dependencies=[
                "google_maps_connector",
                "uber_connector",
                "airbnb_connector"
            ]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from travel sources"""
        
        prompt = f"""You are an expert at analyzing travel data. Extract structured information from this data.

TRAVEL DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Trip summary (dates, destinations, purpose)
2. Itinerary details (flights, hotels, activities)
3. Location patterns (frequent places, commute routes)
4. Travel expenses (transportation, lodging, meals)
5. Business vs personal travel classification
6. Travel preferences (airlines, hotels, neighborhoods)
7. Expense categorization for tax purposes
8. Travel timeline and history
9. Recommendations for future trips
10. Cost optimization opportunities

Return as JSON with detailed travel analysis.
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
                await self._store_travel_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'travel'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_travel_in_kg(self, travel_data: Dict[str, Any]):
        """Store parsed travel data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="travel",
            data=travel_data,
            graph_type="personal"
        )
