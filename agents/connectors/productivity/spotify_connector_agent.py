"""
Spotify Connector Agent - Spotify-specific API guidance and support
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent


class SpotifyConnectorAgent(BaseAgent):
    """Spotify platform-specific connector for music data"""
    
    def __init__(self):
        super().__init__(
            name="Spotify Connector",
            description="Spotify API, listening history, and playlist management",
            capabilities=["Spotify API", "Listening History", "Playlist Management", "Track Analysis", "Recommendations"]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Spotify-specific queries"""
        query_type = data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return {
                'status': 'success',
                'platform': 'Spotify',
                'auth_guide': {
                    'type': 'OAuth 2.0',
                    'flows': ['Authorization Code', 'Client Credentials', 'Implicit Grant'],
                    'scopes': ['user-read-private', 'user-read-email', 'playlist-modify-public', 'user-top-read']
                }
            }
        elif query_type == 'playlists':
            return {
                'status': 'success',
                'platform': 'Spotify',
                'playlist_guide': {
                    'get_user_playlists': 'GET /v1/me/playlists',
                    'create': 'POST /v1/users/{user_id}/playlists',
                    'add_tracks': 'POST /v1/playlists/{playlist_id}/tracks',
                    'remove_tracks': 'DELETE /v1/playlists/{playlist_id}/tracks'
                }
            }
        else:
            return {
                'status': 'success',
                'platform': 'Spotify',
                'message': 'I can help with Spotify API, listening history, and playlist management.'
            }
