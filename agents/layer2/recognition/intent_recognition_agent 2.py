"""
Intent Recognition Agent - LLM-Powered Intent Detection

Layer 2 Entity Recognition agent that uses LLM to identify user intent
and desired actions from parsed data.
"""

from typing import Dict, Any
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class IntentRecognitionAgent(Layer2Agent):
    """
    Intent Recognition - LLM-powered intent detection
    
    Takes parsed data and identifies:
    - User intent (what does the user want?)
    - Action requests (schedule, create, update, delete)
    - Questions (information requests)
    - Commands (direct instructions)
    - Sentiment behind intent
    - Urgency level
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="intent_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered user intent detection and action classification",
            capabilities=["intent_detection", "action_classification", "question_identification", "urgency_assessment"],
            dependencies=["gmail_parser", "slack_parser"]
        )
    
    async def analyze(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """
        Identify user intent from parsed data
        
        Args:
            parsed_data: Parsed data from Layer 1 agents
            
        Returns:
            AgentResult with identified intents and actions
        """
        
        prompt = f"""You are an expert at understanding user intent. Analyze this data and identify what the user wants.

PARSED DATA:
{json.dumps(parsed_data, indent=2)}

IDENTIFY:
1. Primary intent (what does the user want?)
2. Intent type (question, request, command, statement, complaint)
3. Requested actions (schedule, create, update, delete, search, etc.)
4. Required information (what data is needed?)
5. Urgency level (urgent, high, medium, low)
6. Sentiment (frustrated, neutral, happy, confused)
7. Confidence in intent interpretation
8. Alternative interpretations (if ambiguous)

Return as JSON:
{{
    "primary_intent": {{
        "intent": "schedule_meeting",
        "type": "request",
        "confidence": 0.95,
        "description": "User wants to schedule a meeting next week"
    }},
    "requested_actions": [
        {{
            "action": "schedule",
            "target": "meeting",
            "parameters": {{
                "timeframe": "next_week",
                "participants": ["John Smith", "Jane Doe"],
                "duration": "1_hour",
                "topic": "Q4 planning"
            }},
            "priority": "high"
        }},
        {{
            "action": "send",
            "target": "calendar_invite",
            "parameters": {{
                "recipients": ["john@example.com", "jane@example.com"]
            }},
            "priority": "high"
        }}
    ],
    "required_information": [
        {{
            "field": "specific_date",
            "status": "missing",
            "suggestion": "Ask user for preferred date/time"
        }},
        {{
            "field": "meeting_location",
            "status": "missing",
            "suggestion": "Ask if virtual or in-person"
        }}
    ],
    "urgency": "medium",
    "sentiment": "neutral",
    "alternative_interpretations": [
        {{
            "intent": "check_availability",
            "confidence": 0.25,
            "description": "User might just be checking if people are available"
        }}
    ],
    "follow_up_questions": [
        "What specific date and time works best?",
        "Should this be a virtual or in-person meeting?"
    ]
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            intent_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_intent_in_kg(intent_data)
            
            return AgentResult(
                success=True,
                data=intent_data,
                metadata={'agent': self.metadata.name, 'layer': 'recognition'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_intent_in_kg(self, intent_data: Dict[str, Any]):
        """Store identified intent in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="user_intent",
            data=intent_data
        )
        
        # Create action entities
        for action in intent_data.get('requested_actions', []):
            await self.kg_client.create_entity(
                entity_type="requested_action",
                data=action
            )
