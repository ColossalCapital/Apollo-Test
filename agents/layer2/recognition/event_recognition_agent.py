"""
Event Recognition Agent - LLM-Powered Event Detection

Layer 2 Entity Recognition agent that uses LLM to identify and categorize
events from parsed data.
"""

from typing import Dict, Any
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class EventRecognitionAgent(Layer2Agent):
    """
    Event Recognition - LLM-powered event detection
    
    Takes parsed data and identifies:
    - Calendar events (meetings, deadlines)
    - Business events (launches, acquisitions)
    - Market events (earnings, announcements)
    - Personal events (birthdays, milestones)
    - Event relationships and dependencies
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="event_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered event detection and categorization",
            capabilities=["event_extraction", "event_categorization", "deadline_detection", "milestone_tracking"],
            dependencies=["gmail_parser", "slack_parser", "document_parser"]
        )
    
    async def analyze(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """
        Identify events from parsed data
        
        Args:
            parsed_data: Parsed data from Layer 1 agents
            
        Returns:
            AgentResult with identified events
        """
        
        prompt = f"""You are an expert at identifying events. Analyze this data and extract all events, deadlines, and milestones.

PARSED DATA:
{json.dumps(parsed_data, indent=2)}

IDENTIFY:
1. All events mentioned (meetings, launches, deadlines, etc.)
2. Event type (meeting, deadline, launch, announcement, etc.)
3. Event date and time (if specified)
4. Event participants/stakeholders
5. Event location (physical or virtual)
6. Event importance (critical, high, medium, low)
7. Event dependencies (what must happen before/after)
8. Action items related to event

Return as JSON:
{{
    "events": [
        {{
            "event_id": "evt_001",
            "title": "Q4 Board Meeting",
            "type": "meeting",
            "date": "2025-11-15",
            "time": "14:00:00",
            "timezone": "UTC",
            "participants": ["John Smith", "Jane Doe", "Board Members"],
            "location": "Conference Room A",
            "importance": "critical",
            "description": "Quarterly board meeting to review financials",
            "action_items": [
                "Prepare financial reports",
                "Create presentation deck"
            ],
            "dependencies": [
                {{"event": "Q4 close", "type": "must_complete_before"}}
            ]
        }},
        {{
            "event_id": "evt_002",
            "title": "Product Launch",
            "type": "launch",
            "date": "2025-12-01",
            "time": "09:00:00",
            "timezone": "UTC",
            "participants": ["Marketing Team", "Product Team"],
            "location": "virtual",
            "importance": "high",
            "description": "Launch new AI features",
            "action_items": [
                "Finalize marketing materials",
                "Test production deployment"
            ],
            "dependencies": []
        }}
    ],
    "deadlines": [
        {{
            "deadline_id": "dl_001",
            "title": "Tax Filing Deadline",
            "date": "2025-11-30",
            "importance": "critical",
            "related_to": "Q4 financials"
        }}
    ],
    "milestones": [
        {{
            "milestone_id": "ms_001",
            "title": "Reached 1M Users",
            "date": "2025-10-29",
            "importance": "high",
            "celebration": true
        }}
    ]
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            event_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_events_in_kg(event_data)
            
            return AgentResult(
                success=True,
                data=event_data,
                metadata={'agent': self.metadata.name, 'layer': 'recognition'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_events_in_kg(self, event_data: Dict[str, Any]):
        """Store identified events in knowledge graph"""
        if not self.kg_client:
            return
        
        # Create event entities
        for event in event_data.get('events', []):
            await self.kg_client.create_entity(
                entity_type="event",
                data=event
            )
        
        # Create deadline entities
        for deadline in event_data.get('deadlines', []):
            await self.kg_client.create_entity(
                entity_type="deadline",
                data=deadline
            )
        
        # Create milestone entities
        for milestone in event_data.get('milestones', []):
            await self.kg_client.create_entity(
                entity_type="milestone",
                data=milestone
            )
