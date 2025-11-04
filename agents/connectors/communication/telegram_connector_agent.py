"""
Telegram Connector Agent - Telegram API Integration

Maintains Telegram API connector for messages, channels, and bots.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class TelegramConnectorAgent(Layer1Agent):
    """Telegram API connector"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/telegram"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="telegram_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Telegram connector - messages, channels, bots",
            capabilities=[
                "message_sync",
                "channel_sync",
                "bot_interaction",
                "media_download",
                "link_extraction"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Telegram connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Telegram',
                    'auth_guide': {
                        'type': 'API Token + Phone Number',
                        'endpoints': ['Telegram Bot API', 'MTProto API'],
                        'required': ['API ID', 'API Hash', 'Phone Number'],
                        'scopes': ['messages', 'channels', 'media']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Telegram',
                    'sync_modes': {
                        'pull': 'Fetch messages and media',
                        'real_time': 'Real-time message updates',
                        'bot_mode': 'Bot interactions and commands'
                    },
                    'entities': {
                        'messages': 'Personal and group messages',
                        'channels': 'Channel subscriptions and posts',
                        'media': 'Photos, videos, documents',
                        'bots': 'Bot interactions and commands',
                        'links': 'Shared URLs and previews'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Telegram',
                    'message': 'Telegram connector for messages and channels'
                },
                metadata={'agent': self.metadata.name}
            )
