"""
YouTube Parser Agent - LLM-Powered YouTube Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse YouTube data
and extract video intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class YouTubeParserAgent(Layer1Agent):
    """
    YouTube Parser - LLM-powered video streaming data parsing
    
    Takes YouTube API data and extracts:
    - Watch patterns and interests
    - Content preferences
    - Educational vs entertainment balance
    - Creator relationships
    - Learning pathways
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="youtube_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered YouTube data parsing with content intelligence",
            capabilities=["watch_analysis", "interest_profiling", "creator_analysis", "learning_pathways"],
            dependencies=["youtube_connector"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from YouTube API response"""
        
        prompt = f"""You are an expert content analyst. Extract structured information from this YouTube data.

YOUTUBE DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Watch history and patterns
2. Content categories and interests
3. Favorite creators and channels
4. Educational vs entertainment balance
5. Video length preferences
6. Watch completion rates
7. Engagement patterns (likes, comments, shares)
8. Learning pathways (tutorial sequences)
9. Trending topics in watch history
10. Social connections (shared interests)

Return as JSON:
{{
    "user_id": "youtube_user_123",
    "watch_history": [
        {{
            "video_id": "abc123",
            "title": "How to Build a Trading Bot",
            "channel": "Tech Education",
            "category": "education",
            "duration_seconds": 1800,
            "watched_at": "2025-10-29T20:00:00Z",
            "watch_percentage": 0.95,
            "engagement": ["liked", "saved"]
        }}
    ],
    "content_interests": [
        {{
            "category": "technology",
            "subcategories": ["programming", "AI", "trading"],
            "watch_time_hours": 150,
            "video_count": 300,
            "growth_trend": "increasing"
        }},
        {{
            "category": "education",
            "subcategories": ["finance", "business", "science"],
            "watch_time_hours": 100,
            "video_count": 200,
            "growth_trend": "stable"
        }}
    ],
    "favorite_creators": [
        {{
            "channel": "Tech Education",
            "subscriber_since": "2023-01-15",
            "videos_watched": 50,
            "avg_watch_percentage": 0.85,
            "notification_level": "all",
            "content_type": "educational"
        }}
    ],
    "content_balance": {{
        "educational": 0.60,
        "entertainment": 0.25,
        "news": 0.10,
        "music": 0.05
    }},
    "watch_patterns": {{
        "avg_video_length": 900,
        "preferred_length": "10-20 minutes",
        "completion_rate": 0.75,
        "peak_hours": ["7am-9am", "9pm-11pm"],
        "binge_watching": true,
        "playlist_usage": "frequent"
    }},
    "engagement_profile": {{
        "like_rate": 0.30,
        "comment_rate": 0.05,
        "share_rate": 0.10,
        "save_rate": 0.20,
        "engagement_style": "passive_consumer"
    }},
    "learning_pathways": [
        {{
            "topic": "Python Programming",
            "videos_watched": 25,
            "progression": "beginner → intermediate",
            "completion": 0.80,
            "next_steps": ["Advanced Python", "Django Framework"]
        }},
        {{
            "topic": "Trading Strategies",
            "videos_watched": 40,
            "progression": "basics → advanced",
            "completion": 0.60,
            "next_steps": ["Options Trading", "Algorithmic Trading"]
        }}
    ],
    "trending_topics": [
        {{"topic": "AI and Machine Learning", "video_count": 30, "recent_surge": true}},
        {{"topic": "Cryptocurrency", "video_count": 20, "recent_surge": false}}
    ],
    "social_connections": {{
        "shared_interests": ["technology", "finance"],
        "collaborative_playlists": 3,
        "recommended_by_friends": 0.15
    }},
    "graph_routing": {{
        "primary_graphs": ["personal", "technical"],
        "secondary_graphs": ["social", "temporal"]
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
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_youtube_data_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'youtube'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_youtube_data_in_kg(self, youtube_data: Dict[str, Any]):
        """Store parsed YouTube data in knowledge graphs"""
        if not self.kg_client:
            return
        
        # Personal Graph (interests and learning)
        await self.kg_client.create_entity(
            entity_type="content_interests",
            data=youtube_data.get('content_interests'),
            graph_type="personal"
        )
        
        # Technical Graph (learning pathways)
        for pathway in youtube_data.get('learning_pathways', []):
            await self.kg_client.create_entity(
                entity_type="learning_pathway",
                data=pathway,
                graph_type="technical"
            )
        
        # Social Graph (creators and connections)
        for creator in youtube_data.get('favorite_creators', []):
            await self.kg_client.create_entity(
                entity_type="content_creator",
                data=creator,
                graph_type="social"
            )
        
        # Temporal Graph (watch patterns)
        await self.kg_client.create_entity(
            entity_type="watch_patterns",
            data=youtube_data.get('watch_patterns'),
            graph_type="temporal"
        )
