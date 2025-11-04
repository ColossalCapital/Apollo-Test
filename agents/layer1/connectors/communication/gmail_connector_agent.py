"""
Gmail Connector Agent - Gmail-specific API guidance and support
"""

from typing import Dict, Any
from ....base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class GmailConnectorAgent(Layer1Agent):
    """Gmail platform-specific connector for email management"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="gmail_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Gmail API, email sync, and message management",
            capabilities=["gmail_api", "email_sync", "label_management", "search", "send_email"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract data from Gmail API"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Gmail',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'scopes': ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send'],
                        'flow': 'Google OAuth 2.0 consent screen'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'messages':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Gmail',
                    'message_guide': {
                        'list': 'GET /gmail/v1/users/me/messages',
                        'get': 'GET /gmail/v1/users/me/messages/{id}',
                        'send': 'POST /gmail/v1/users/me/messages/send',
                        'format': 'Base64url encoded MIME message'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Gmail',
                    'message': 'I can help with Gmail API, email sync, and message management.'
                },
                metadata={'agent': self.metadata.name}
            )
