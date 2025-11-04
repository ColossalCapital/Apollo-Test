"""
iMessage Connector Agent - Local iMessage Database Integration

Maintains local iMessage database access for privacy-preserving message analysis.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class IMessageConnectorAgent(Layer1Agent):
    """iMessage connector - local database access"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.db_path = "~/Library/Messages/chat.db"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="imessage_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="iMessage connector - local database access for privacy-preserving analysis",
            capabilities=[
                "message_extraction",
                "attachment_extraction",
                "contact_extraction",
                "link_extraction",
                "location_extraction",
                "privacy_preserving"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process iMessage connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'iMessage',
                    'auth_guide': {
                        'type': 'Local Database Access',
                        'location': '~/Library/Messages/chat.db',
                        'required': ['Full Disk Access permission'],
                        'privacy': 'All processing local, never sent to cloud'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'iMessage',
                    'sync_modes': {
                        'pull': 'Read messages from local database',
                        'real_time': 'Monitor database changes',
                        'privacy': 'All processing happens locally'
                    },
                    'entities': {
                        'messages': 'Read all text messages',
                        'attachments': 'Extract images, videos, files',
                        'contacts': 'Extract phone numbers, names',
                        'links': 'Extract shared URLs',
                        'locations': 'Extract shared locations',
                        'confirmation_codes': 'Extract 2FA codes'
                    },
                    'privacy': {
                        'local_only': True,
                        'no_cloud_sync': True,
                        'encrypted_storage': True,
                        'user_controlled': True
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'iMessage',
                    'message': 'iMessage connector for privacy-preserving message analysis'
                },
                metadata={'agent': self.metadata.name}
            )
