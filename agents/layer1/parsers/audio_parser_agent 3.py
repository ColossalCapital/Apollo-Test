"""
Audio Parser Agent - LLM-Powered Audio Analysis

Layer 1 Data Extraction agent that uses LLM to parse audio files
and extract structured music intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class AudioParserAgent(Layer1Agent):
    """
    Audio Parser - LLM-powered audio and music analysis
    
    Takes audio files and extracts:
    - Song metadata (title, artist, album)
    - Audio features (tempo, key, genre)
    - Lyrics and themes
    - Mood and emotion
    - Cultural references
    - Meme connections
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="audio_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered audio and music analysis with cultural intelligence",
            capabilities=["audio_analysis", "lyrics_parsing", "mood_detection", "meme_recognition"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from audio file
        
        Args:
            raw_data: Audio file data with metadata and features
            
        Returns:
            AgentResult with structured music data
        """
        
        return await self._parse_audio(raw_data)
    
    async def _parse_audio(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse audio file with LLM"""
        
        prompt = f"""You are an expert musicologist and cultural analyst. Analyze this audio file and extract comprehensive information.

AUDIO DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Song metadata (title, artist, album, year)
2. Genre and subgenre
3. Audio features (tempo, key, time signature)
4. Lyrics (if available)
5. Themes and topics
6. Mood and emotion
7. Cultural references
8. Meme connections
9. Slang or unique vocabulary
10. Story or narrative (if present)
11. Similar songs/artists
12. Target audience

Return as JSON:
{{
    "song_metadata": {{
        "title": "Country Girls Make Do",
        "artist": "DJ Kernels",
        "album": "Provocative Beats Vol. 1",
        "year": 2024,
        "duration_seconds": 240,
        "explicit": true
    }},
    "genre": {{
        "primary": "EDM",
        "subgenres": ["house", "electro"],
        "influences": ["dubstep", "trap"]
    }},
    "audio_features": {{
        "tempo_bpm": 128,
        "key": "A minor",
        "time_signature": "4/4",
        "energy": 0.92,
        "danceability": 0.88,
        "valence": 0.65,
        "loudness_db": -5.2,
        "spectral_centroid": 2500,
        "beat_strength": 0.85
    }},
    "lyrics": {{
        "has_lyrics": true,
        "language": "english",
        "explicit": true,
        "themes": ["rural_life", "improvisation", "sexual_innuendo"],
        "key_phrases": ["country girls make do", "kernels in the field"]
    }},
    "mood_emotion": {{
        "primary_mood": "provocative",
        "secondary_moods": ["playful", "energetic"],
        "emotional_arc": "building_tension",
        "intensity": 0.85
    }},
    "cultural_references": [
        {{
            "reference": "country girls make do",
            "type": "meme",
            "origin": "Tumblr 2012",
            "meaning": "rural improvisation with sexual connotation",
            "popularity": "high"
        }},
        {{
            "reference": "kernels",
            "type": "wordplay",
            "meanings": ["corn kernels", "math kernel", "slang: turnt"],
            "context": "triple entendre"
        }}
    ],
    "slang_vocabulary": [
        {{
            "term": "make do",
            "meaning": "improvise with available resources",
            "connotation": "sexual",
            "usage": "common"
        }}
    ],
    "narrative": {{
        "has_story": false,
        "narrative_type": "vibe-based",
        "story_arc": null
    }},
    "similar_songs": [
        {{"title": "Old Town Road", "artist": "Lil Nas X", "similarity": 0.65}},
        {{"title": "Horses", "artist": "Lil Nas X", "similarity": 0.60}}
    ],
    "target_audience": {{
        "age_range": "18-35",
        "demographics": ["EDM fans", "meme culture", "LGBTQ+"],
        "contexts": ["clubs", "festivals", "parties"]
    }},
    "graph_routing": {{
        "primary_graphs": ["music", "memes"],
        "secondary_graphs": ["slang", "personal"],
        "optional_graphs": ["narrative", "humor"]
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_audio_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'audio'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_audio_in_kg(self, audio_data: Dict[str, Any]):
        """Store parsed audio in knowledge graphs"""
        if not self.kg_client:
            return
        
        # Route to multiple graphs based on graph_routing
        routing = audio_data.get('graph_routing', {})
        
        # Music Graph (primary)
        if 'music' in routing.get('primary_graphs', []):
            await self.kg_client.create_entity(
                entity_type="song",
                data=audio_data,
                graph_type="music"
            )
        
        # Memes Graph (if meme references)
        if 'memes' in routing.get('primary_graphs', []):
            for ref in audio_data.get('cultural_references', []):
                if ref['type'] == 'meme':
                    await self.kg_client.create_entity(
                        entity_type="meme_reference",
                        data=ref,
                        graph_type="memes"
                    )
        
        # Slang Graph (if slang vocabulary)
        if 'slang' in routing.get('secondary_graphs', []):
            for term in audio_data.get('slang_vocabulary', []):
                await self.kg_client.create_entity(
                    entity_type="slang_term",
                    data=term,
                    graph_type="slang"
                )
        
        # Personal Graph (listening history)
        if 'personal' in routing.get('secondary_graphs', []):
            await self.kg_client.create_entity(
                entity_type="listening_event",
                data={
                    'song': audio_data['song_metadata']['title'],
                    'listened_at': raw_data.get('listened_at'),
                    'context': raw_data.get('context')
                },
                graph_type="personal"
            )
