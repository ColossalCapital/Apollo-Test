"""
Spotify Parser Agent - LLM-Powered Spotify Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse Spotify data
and extract music intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class SpotifyParserAgent(Layer1Agent):
    """
    Spotify Parser - LLM-powered music streaming data parsing
    
    Takes Spotify API data and extracts:
    - Listening patterns and habits
    - Music taste profile
    - Mood-based playlists
    - Discovery patterns
    - Social music connections
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="spotify_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Spotify data parsing with music intelligence",
            capabilities=["listening_analysis", "taste_profiling", "mood_detection", "recommendation_analysis"],
            dependencies=["spotify_connector"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from Spotify API response"""
        
        prompt = f"""You are an expert music analyst. Extract structured information from this Spotify data.

SPOTIFY DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Listening history and patterns
2. Top tracks and artists
3. Music taste profile
4. Genre preferences
5. Mood patterns (when do they listen to what)
6. Discovery behavior (new vs familiar)
7. Playlist organization
8. Audio feature preferences (tempo, energy, valence)
9. Listening contexts (work, exercise, relax)
10. Social connections (shared artists, collaborative playlists)

Return as JSON:
{{
    "user_id": "spotify_user_123",
    "listening_history": [
        {{
            "track": "Country Girls Make Do",
            "artist": "DJ Kernels",
            "played_at": "2025-10-29T22:00:00Z",
            "context": "working",
            "duration_ms": 240000
        }}
    ],
    "top_tracks": [
        {{
            "track": "Song Title",
            "artist": "Artist Name",
            "play_count": 150,
            "first_played": "2025-01-01",
            "last_played": "2025-10-29"
        }}
    ],
    "top_artists": [
        {{
            "artist": "Artist Name",
            "genres": ["EDM", "house"],
            "play_count": 500,
            "discovery_date": "2024-06-15"
        }}
    ],
    "music_taste_profile": {{
        "primary_genres": ["EDM", "indie", "hip-hop"],
        "mood_preferences": ["energetic", "chill", "melancholic"],
        "era_preferences": ["2010s", "2020s"],
        "discovery_openness": 0.75,
        "mainstream_vs_indie": 0.60
    }},
    "audio_preferences": {{
        "avg_tempo": 125,
        "avg_energy": 0.75,
        "avg_valence": 0.65,
        "avg_danceability": 0.80,
        "preferred_key": "C major",
        "preferred_mode": "major"
    }},
    "listening_patterns": {{
        "peak_hours": ["9am-11am", "8pm-11pm"],
        "weekday_vs_weekend": {{
            "weekday": "focus_music",
            "weekend": "party_music"
        }},
        "seasonal_trends": "summer: upbeat, winter: melancholic"
    }},
    "contexts": [
        {{
            "context": "working",
            "genres": ["lo-fi", "ambient"],
            "tempo_range": [80, 110],
            "frequency": "daily"
        }},
        {{
            "context": "exercising",
            "genres": ["EDM", "hip-hop"],
            "tempo_range": [120, 140],
            "frequency": "3x/week"
        }}
    ],
    "discovery_behavior": {{
        "new_artist_rate": "5 per month",
        "playlist_vs_album": "70% playlists",
        "algorithm_vs_manual": "60% algorithm",
        "social_discovery": "20% from friends"
    }},
    "playlists": [
        {{
            "name": "Focus Flow",
            "track_count": 150,
            "avg_tempo": 95,
            "purpose": "working",
            "update_frequency": "weekly"
        }}
    ],
    "graph_routing": {{
        "primary_graphs": ["music", "personal"],
        "secondary_graphs": ["temporal", "social"]
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_spotify_data_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'spotify'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_spotify_data_in_kg(self, spotify_data: Dict[str, Any]):
        """Store parsed Spotify data in knowledge graphs"""
        if not self.kg_client:
            return
        
        # Music Graph
        for track in spotify_data.get('top_tracks', []):
            await self.kg_client.create_entity(
                entity_type="track",
                data=track,
                graph_type="music"
            )
        
        # Personal Graph (listening history)
        await self.kg_client.create_entity(
            entity_type="music_taste_profile",
            data=spotify_data.get('music_taste_profile'),
            graph_type="personal"
        )
        
        # Temporal Graph (listening patterns)
        await self.kg_client.create_entity(
            entity_type="listening_patterns",
            data=spotify_data.get('listening_patterns'),
            graph_type="temporal"
        )
