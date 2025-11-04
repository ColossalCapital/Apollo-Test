"""
Topic Recognition Agent - LLM-Powered Topic Identification

Layer 2 Entity Recognition agent that uses LLM to identify and categorize
topics from parsed data.
"""

from typing import Dict, Any, List
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class TopicRecognitionAgent(Layer2Agent):
    """
    Topic Recognition - LLM-powered topic identification
    
    Takes parsed data and identifies:
    - Main topics and themes
    - Sub-topics and categories
    - Topic relationships
    - Trending topics
    - Topic sentiment
    - Topic importance
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="topic_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered topic identification and categorization",
            capabilities=["topic_extraction", "theme_analysis", "topic_relationships", "trending_detection"],
            dependencies=["gmail_parser", "slack_parser", "document_parser"]
        )
    
    async def analyze(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """
        Identify topics from parsed data
        
        Args:
            parsed_data: Parsed data from Layer 1 agents
            
        Returns:
            AgentResult with identified topics and relationships
        """
        
        prompt = f"""You are an expert at identifying topics and themes. Analyze this data and extract all relevant topics.

PARSED DATA:
{json.dumps(parsed_data, indent=2)}

IDENTIFY:
1. Main topics (3-5 primary themes)
2. Sub-topics (related concepts)
3. Topic categories (business, technical, personal, etc.)
4. Topic relationships (which topics are related)
5. Topic importance (high, medium, low)
6. Topic sentiment (positive, neutral, negative)
7. Trending indicators (is this topic gaining attention?)
8. Keywords associated with each topic

Return as JSON:
{{
    "main_topics": [
        {{
            "topic": "artificial_intelligence",
            "category": "technology",
            "importance": "high",
            "sentiment": "positive",
            "confidence": 0.92,
            "keywords": ["AI", "machine learning", "neural networks"],
            "sub_topics": ["llm", "computer_vision", "nlp"]
        }},
        {{
            "topic": "quarterly_earnings",
            "category": "business",
            "importance": "high",
            "sentiment": "neutral",
            "confidence": 0.88,
            "keywords": ["Q4", "revenue", "profit"],
            "sub_topics": ["revenue_growth", "cost_reduction"]
        }}
    ],
    "topic_relationships": [
        {{
            "from": "artificial_intelligence",
            "to": "quarterly_earnings",
            "relationship": "impacts",
            "strength": 0.75
        }}
    ],
    "trending": [
        {{
            "topic": "artificial_intelligence",
            "trend_score": 0.85,
            "velocity": "increasing"
        }}
    ],
    "context": "Technology earnings discussion"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            topic_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_topics_in_kg(topic_data)
            
            return AgentResult(
                success=True,
                data=topic_data,
                metadata={'agent': self.metadata.name, 'layer': 'recognition'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_topics_in_kg(self, topic_data: Dict[str, Any]):
        """Store identified topics in knowledge graph"""
        if not self.kg_client:
            return
        
        # Create topic entities
        for topic in topic_data.get('main_topics', []):
            await self.kg_client.create_entity(
                entity_type="topic",
                data=topic
            )
        
        # Create topic relationships
        for rel in topic_data.get('topic_relationships', []):
            await self.kg_client.create_relationship(
                from_entity=rel['from'],
                to_entity=rel['to'],
                relationship_type=rel['relationship'],
                properties={'strength': rel['strength']}
            )
