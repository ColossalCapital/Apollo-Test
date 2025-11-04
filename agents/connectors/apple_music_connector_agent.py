"""
Apple Music Connector Agent - Apple Music API Integration

Connector agent that integrates with Apple Music API for music streaming data.
"""

from typing import Dict, Any
from ..base import ConnectorAgent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx


class AppleMusicConnectorAgent(ConnectorAgent):
    """
    Apple Music Connector - Music streaming integration
    
    Provides:
    - Listening history
    - Playlists
    - Library management
    - Music recommendations
    - Artist following
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.api_url = "https://api.music.apple.com/v1"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="apple_music_connector",
            layer=AgentLayer.CONNECTOR,
            version="1.0.0",
            description="Apple Music API integration for music streaming data",
            capabilities=[
                "listening_history",
                "playlist_management",
                "library_sync",
                "music_recommendations",
                "artist_following"
            ],
            dependencies=[],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=True,
            wtf_purchasable=False,
            required_credentials=["developer_token", "user_token"]
        )
    
    async def connect(self, credentials: Dict[str, str]) -> AgentResult:
        """Connect to Apple Music API"""
        
        developer_token = credentials.get('developer_token')
        user_token = credentials.get('user_token')
        
        try:
            # Test connection
            response = await self.client.get(
                f"{self.api_url}/me/library/playlists",
                headers={
                    "Authorization": f"Bearer {developer_token}",
                    "Music-User-Token": user_token
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return AgentResult(
                    success=True,
                    data={"status": "connected", "playlists": len(data.get('data', []))},
                    metadata={'agent': self.metadata.name}
                )
            else:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'error': 'Authentication failed'}
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def fetch_recent_plays(self, developer_token: str, user_token: str, limit: int = 50) -> AgentResult:
        """Fetch recently played tracks"""
        
        try:
            response = await self.client.get(
                f"{self.api_url}/me/recent/played/tracks",
                headers={
                    "Authorization": f"Bearer {developer_token}",
                    "Music-User-Token": user_token
                },
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                tracks = response.json()
                return AgentResult(
                    success=True,
                    data=tracks,
                    metadata={'agent': self.metadata.name, 'count': len(tracks.get('data', []))}
                )
            else:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'error': 'Failed to fetch tracks'}
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
