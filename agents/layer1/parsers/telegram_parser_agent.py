"""
Telegram Parser Agent - LLM-Powered Telegram Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse Telegram data
and extract channel and conversation intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class TelegramParserAgent(Layer1Agent):
    """
    Telegram Parser - LLM-powered Telegram parsing
    
    Takes Telegram data and extracts:
    - Channel content and topics
    - Bot interactions
    - Group conversations
    - Shared media and links
    - Community insights
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="telegram_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Telegram parsing for channels and conversations",
            capabilities=[
                "channel_analysis",
                "bot_interaction_parsing",
                "group_conversation_analysis",
                "media_extraction",
                "community_insights"
            ],
            dependencies=["telegram_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL, EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from Telegram"""
        
        prompt = f"""You are an expert at analyzing Telegram data. Extract structured information from this Telegram data.

TELEGRAM DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Channel topics and themes
2. Bot commands and interactions
3. Group conversation dynamics
4. Shared links and media
5. Community sentiment and trends
6. Key influencers and active members
7. Important announcements
8. Technical discussions (if applicable)
9. Action items and decisions
10. Cross-channel connections

Return as JSON with detailed Telegram analysis.
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
                await self._store_telegram_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'telegram'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_telegram_in_kg(self, telegram_data: Dict[str, Any]):
        """Store parsed Telegram data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="telegram_content",
            data=telegram_data,
            graph_type="community"
        )
