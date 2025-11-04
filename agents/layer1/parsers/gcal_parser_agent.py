"""
Google Calendar Parser Agent - LLM-Powered Calendar Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse Google Calendar data
and extract scheduling intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class GCalParserAgent(Layer1Agent):
    """
    Google Calendar Parser - LLM-powered calendar parsing
    
    Takes Google Calendar data and extracts:
    - Meeting patterns and frequency
    - Time allocation by category
    - Scheduling conflicts
    - Productivity insights
    - Relationship mapping
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="gcal_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Google Calendar parsing for scheduling intelligence",
            capabilities=[
                "meeting_analysis",
                "time_allocation",
                "conflict_detection",
                "productivity_insights",
                "relationship_mapping"
            ],
            dependencies=["gcal_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.UNIVERSAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from Google Calendar"""
        
        prompt = f"""You are an expert at analyzing calendar data. Extract structured information from this Google Calendar data.

CALENDAR DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Meeting patterns (frequency, duration, types)
2. Time allocation by category (meetings, focus time, personal)
3. Recurring events and commitments
4. Scheduling conflicts and double-bookings
5. Meeting attendees and relationship mapping
6. Productivity insights (meeting-heavy days, focus time)
7. Travel time and commute patterns
8. Important deadlines and milestones
9. Work-life balance indicators
10. Optimization opportunities

Return as JSON with detailed calendar analysis and productivity insights.
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
                await self._store_calendar_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'google_calendar'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_calendar_in_kg(self, calendar_data: Dict[str, Any]):
        """Store parsed calendar data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="calendar_analysis",
            data=calendar_data,
            graph_type="temporal"
        )
