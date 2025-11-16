"""
Meme Parser Agent - LLM-Powered Meme and Cultural Reference Analysis

Layer 1 Data Extraction agent that uses LLM to parse memes, cultural references,
and internet culture from text, images, and multimedia content.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class MemeParserAgent(Layer1Agent):
    """
    Meme Parser - LLM-powered meme and cultural reference analysis
    
    Takes content and extracts:
    - Meme references and formats
    - Cultural context and origins
    - Viral trends and popularity
    - Humor patterns and styles
    - Community-specific memes
    - Cross-platform meme evolution
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="meme_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered meme and cultural reference analysis",
            capabilities=["meme_detection", "cultural_analysis", "trend_tracking", "humor_analysis"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured meme data from content
        
        Args:
            raw_data: Content with potential meme references
            
        Returns:
            AgentResult with structured meme data
        """
        
        return await self._parse_meme_content(raw_data)
    
    async def _parse_meme_content(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse meme content with LLM"""
        
        prompt = f"""You are an expert in internet culture and memes. Analyze this content and extract all meme references and cultural context.

CONTENT:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Meme references (identify all memes mentioned or referenced)
2. Meme format/template (if applicable)
3. Origin and history
4. Cultural context and meaning
5. Popularity and virality
6. Platform associations (TikTok, Twitter, Reddit, etc.)
7. Community context (which communities use this meme)
8. Humor style (ironic, absurdist, wholesome, dark, etc.)
9. Evolution and variations
10. Cross-references to other memes

Return as JSON:
{{
    "content_id": "post_123",
    "content_text": "just vibin with these kernels 🌽🎵 #kernt",
    "meme_references": [
        {{
            "meme_name": "Country Girls Make Do",
            "meme_type": "phrase_meme",
            "origin": {{
                "platform": "Tumblr",
                "year": 2012,
                "original_context": "Rural improvisation joke",
                "creator": "Anonymous"
            }},
            "meaning": {{
                "surface": "Rural people improvise with available resources",
                "deeper": "Sexual innuendo about improvised objects",
                "cultural_significance": "Became iconic LGBTQ+ humor"
            }},
            "popularity": {{
                "peak_year": 2019,
                "current_status": "classic",
                "virality_score": 0.85,
                "longevity": "evergreen"
            }},
            "platforms": [
                {{"platform": "Tumblr", "usage": "origin"}},
                {{"platform": "Twitter", "usage": "mainstream"}},
                {{"platform": "TikTok", "usage": "revival"}}
            ],
            "communities": ["LGBTQ+", "rural_culture", "meme_culture"],
            "humor_style": "sexual_innuendo",
            "variations": [
                "Country boys make do",
                "City girls make do",
                "Programmers make do"
            ],
            "related_memes": ["improvise_adapt_overcome", "modern_problems_require_modern_solutions"]
        }},
        {{
            "meme_name": "Vibing",
            "meme_type": "slang_term",
            "origin": {{
                "platform": "Twitter",
                "year": 2018,
                "original_context": "Relaxed enjoyment",
                "evolution": "From AAVE to mainstream"
            }},
            "meaning": {{
                "surface": "Relaxing and enjoying the moment",
                "deeper": "Mindful presence and contentment",
                "cultural_significance": "Gen Z emotional expression"
            }},
            "popularity": {{
                "peak_year": 2020,
                "current_status": "mainstream",
                "virality_score": 0.95,
                "longevity": "ongoing"
            }},
            "platforms": [
                {{"platform": "Twitter", "usage": "origin"}},
                {{"platform": "TikTok", "usage": "dominant"}},
                {{"platform": "Instagram", "usage": "mainstream"}}
            ],
            "communities": ["gen_z", "music_culture", "chill_culture"],
            "humor_style": "wholesome",
            "variations": ["vibe check", "vibes", "good vibes only"],
            "related_memes": ["no_thoughts_head_empty", "living_my_best_life"]
        }}
    ],
    "meme_format": {{
        "format_name": "text_with_emoji",
        "structure": "casual_statement + emoji + hashtag",
        "typical_usage": "social_media_post",
        "effectiveness": "high"
    }},
    "cultural_analysis": {{
        "primary_culture": "internet_culture",
        "subcultures": ["LGBTQ+", "gen_z", "music_lovers"],
        "generational_appeal": "millennials_and_gen_z",
        "geographic_spread": "global",
        "language_barriers": "low"
    }},
    "humor_analysis": {{
        "primary_style": "layered_humor",
        "techniques": ["innuendo", "wordplay", "cultural_reference"],
        "sophistication": "high",
        "accessibility": "medium",
        "offensiveness": "low"
    }},
    "virality_potential": {{
        "shareability": 0.80,
        "relatability": 0.75,
        "novelty": 0.60,
        "emotional_impact": 0.70,
        "overall_score": 0.71
    }},
    "cross_references": {{
        "music_references": ["EDM", "chill_music"],
        "slang_terms": ["kernt", "vibin"],
        "emoji_usage": ["🌽", "🎵"],
        "hashtags": ["#kernt"]
    }},
    "graph_routing": {{
        "primary_graphs": ["memes", "slang", "humor"],
        "secondary_graphs": ["music", "community", "firstperson"]
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
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_meme_data_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'meme'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_meme_data_in_kg(self, meme_data: Dict[str, Any]):
        """Store parsed meme data in knowledge graphs"""
        if not self.kg_client:
            return
        
        # Memes Graph (primary)
        for meme_ref in meme_data.get('meme_references', []):
            await self.kg_client.create_entity(
                entity_type="meme",
                data=meme_ref,
                graph_type="memes"
            )
        
        # Slang Graph (cross-references)
        for slang_term in meme_data.get('cross_references', {}).get('slang_terms', []):
            await self.kg_client.create_entity(
                entity_type="slang_term",
                data={'term': slang_term, 'source': 'meme_context'},
                graph_type="slang"
            )
        
        # Humor Graph
        await self.kg_client.create_entity(
            entity_type="humor_analysis",
            data=meme_data.get('humor_analysis'),
            graph_type="humor"
        )
        
        # Community Graph
        for community in meme_data.get('cultural_analysis', {}).get('subcultures', []):
            await self.kg_client.create_entity(
                entity_type="community",
                data={'name': community, 'context': 'meme_culture'},
                graph_type="community"
            )
