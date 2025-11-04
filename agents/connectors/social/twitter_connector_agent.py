"""
Twitter/X Connector Agent - Twitter API Integration

Maintains Twitter API connector for tweets, bookmarks, and social data.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class TwitterConnectorAgent(Layer1Agent):
    """Twitter/X API connector"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/twitter"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="twitter_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Twitter/X connector - tweets, bookmarks, social graph",
            capabilities=[
                "tweet_sync",
                "bookmark_extraction",
                "thread_parsing",
                "link_extraction",
                "social_graph"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Twitter connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Twitter/X',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'endpoints': ['Twitter API v2'],
                        'required': ['API Key', 'API Secret', 'Bearer Token'],
                        'scopes': ['tweet.read', 'users.read', 'bookmark.read']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Twitter/X',
                    'sync_modes': {
                        'pull': 'Fetch tweets and bookmarks',
                        'streaming': 'Real-time tweet stream'
                    },
                    'entities': {
                        'tweets': 'Your tweets and timeline',
                        'bookmarks': 'Saved tweets',
                        'threads': 'Tweet threads',
                        'links': 'Shared URLs',
                        'followers': 'Social connections',
                        'lists': 'Twitter lists'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Twitter/X',
                    'message': 'Twitter connector for social media'
                },
                metadata={'agent': self.metadata.name}
            )
