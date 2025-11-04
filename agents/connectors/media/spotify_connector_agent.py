"""
Spotify Connector Agent - Spotify API Integration

Maintains the Rust-based Spotify connector in AckwardRootsInc.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class SpotifyConnectorAgent(Layer1Agent):
    """Spotify API connector maintenance agent"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="spotify_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Spotify connector maintenance - keeps Rust connector up-to-date",
            capabilities=["spotify_api", "music_streaming", "playlist_management", "listening_history"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Spotify connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Spotify',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'endpoints': ['Spotify Web API'],
                        'required': ['Client ID', 'Client Secret'],
                        'scopes': [
                            'user-read-recently-played',
                            'user-top-read',
                            'user-library-read',
                            'playlist-read-private',
                            'user-read-playback-state'
                        ]
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Spotify',
                    'capabilities': {
                        'listening_history': 'Recently played tracks',
                        'top_tracks': 'User top tracks and artists',
                        'playlists': 'User playlists',
                        'saved_tracks': 'Liked songs',
                        'audio_features': 'Track audio analysis',
                        'recommendations': 'Personalized recommendations',
                        'currently_playing': 'Real-time playback'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Spotify',
                    'message': 'Spotify connector for music streaming and listening history'
                },
                metadata={'agent': self.metadata.name}
            )
