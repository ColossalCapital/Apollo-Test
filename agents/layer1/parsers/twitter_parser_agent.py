"""
Twitter Parser Agent - LLM-Powered Twitter Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse Twitter data
and extract social intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class TwitterParserAgent(Layer1Agent):
    """
    Twitter Parser - LLM-powered Twitter parsing
    
    Takes Twitter data and extracts:
    - Tweet content and themes
    - Social engagement patterns
    - Influencer relationships
    - Trending topics
    - Sentiment and tone
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="twitter_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Twitter parsing for social intelligence",
            capabilities=[
                "tweet_analysis",
                "engagement_tracking",
                "influencer_mapping",
                "trend_detection",
                "sentiment_analysis"
            ],
            dependencies=["twitter_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL, EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from Twitter"""
        
        prompt = f"""You are an expert at analyzing Twitter data. Extract structured information from this Twitter data.

TWITTER DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Tweet themes and topics
2. Engagement metrics (likes, retweets, replies)
3. Influencer relationships and mentions
4. Trending topics and hashtags
5. Sentiment and emotional tone
6. Thread analysis and narratives
7. Bookmarked content insights
8. Network analysis (who you engage with)
9. Content performance patterns
10. Audience insights

Return as JSON with detailed Twitter analysis and social intelligence.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_twitter_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'twitter'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_twitter_in_kg(self, twitter_data: Dict[str, Any]):
        """Store parsed Twitter data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="twitter_analysis",
            data=twitter_data,
            graph_type="social"
        )
