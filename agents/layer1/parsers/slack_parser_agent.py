"""
Slack Parser Agent - LLM-Powered Slack Message Parsing

Layer 1 Data Extraction agent that uses LLM to parse raw Slack API
responses into structured communication data.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class SlackParserAgent(Layer1Agent):
    """
    Slack Parser - LLM-powered Slack message parsing
    
    Takes raw Slack API responses and extracts:
    - Message content and context
    - User mentions and reactions
    - Thread conversations
    - Action items and decisions
    - Team sentiment
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="slack_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Slack message and conversation parsing",
            capabilities=["message_parsing", "thread_analysis", "action_item_extraction", "sentiment_analysis"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw Slack API response
        
        Args:
            raw_data: Raw Slack API response (message, thread, etc.)
            
        Returns:
            AgentResult with structured communication data
        """
        
        data_type = raw_data.get('type', 'message')
        
        if data_type == 'message':
            return await self._parse_message(raw_data)
        elif data_type == 'thread':
            return await self._parse_thread(raw_data)
        elif data_type == 'channel':
            return await self._parse_channel(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_message(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Slack message with LLM"""
        
        prompt = f"""You are an expert at parsing Slack messages. Extract structured information from this message.

RAW SLACK MESSAGE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Message text and formatted content
2. Sender (user ID, name if available)
3. Channel information
4. Timestamp
5. Mentions (@users, @channels)
6. Reactions and emoji
7. Attachments or files
8. Intent (question, announcement, decision, action item, etc.)
9. Action items (tasks mentioned)
10. Urgency level
11. Sentiment (positive, neutral, negative)
12. Key topics discussed

Return as JSON:
{{
    "message_id": "...",
    "text": "...",
    "formatted_text": "...",
    "sender": {{
        "user_id": "U123456",
        "name": "John Smith"
    }},
    "channel": {{
        "id": "C123456",
        "name": "general"
    }},
    "timestamp": "2025-10-29T21:00:00Z",
    "mentions": {{
        "users": ["U234567", "U345678"],
        "channels": ["C234567"],
        "everyone": false
    }},
    "reactions": [
        {{"emoji": "thumbsup", "count": 3}}
    ],
    "attachments": [],
    "intent": "action_item",
    "action_items": [
        "Review the Q4 budget by Friday",
        "Schedule meeting with design team"
    ],
    "urgency": "medium",
    "sentiment": "neutral",
    "topics": ["budget", "Q4", "design meeting"],
    "is_thread_parent": false,
    "thread_ts": null
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_message_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'message'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_thread(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Slack thread conversation with LLM"""
        
        prompt = f"""Analyze this Slack thread conversation and extract key information.

RAW THREAD DATA:
{json.dumps(raw_data, indent=2)}

ANALYZE:
1. Thread topic/subject
2. Participants
3. Key decisions made
4. Action items assigned
5. Unresolved questions
6. Consensus or disagreements
7. Next steps
8. Overall sentiment

Return as JSON with these fields.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_thread_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'thread'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_channel(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Slack channel information"""
        pass
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic Slack data parsing"""
        pass
    
    async def _store_message_in_kg(self, message_data: Dict[str, Any]):
        """Store parsed message in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="slack_message",
            data=message_data
        )
        
        # Create action items as tasks
        for action_item in message_data.get('action_items', []):
            await self.kg_client.create_entity(
                entity_type="task",
                data={'description': action_item, 'source': 'slack'}
            )
    
    async def _store_thread_in_kg(self, thread_data: Dict[str, Any]):
        """Store parsed thread in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="slack_thread",
            data=thread_data
        )
