"""
Sentiment Recognition Agent - LLM-Powered Sentiment Analysis

Layer 2 Entity Recognition agent that analyzes sentiment and emotional tone.
"""

from typing import Dict, Any
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class SentimentRecognitionAgent(Layer2Agent):
    """
    Sentiment Recognition - Analyzes sentiment and emotion
    
    Detects:
    - Overall sentiment (positive, negative, neutral)
    - Emotional tone
    - Urgency level
    - Confidence level
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="sentiment_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered sentiment and emotion analysis",
            capabilities=["sentiment_analysis", "emotion_detection", "urgency_detection"],
            dependencies=["document_parser"],
            
            # Metadata for filtering
            entity_types=[EntityType.UNIVERSAL],
            app_contexts=[AppContext.ATLAS, AppContext.DELT, AppContext.AKASHIC],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def recognize(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """Analyze sentiment from parsed data"""
        
        text = parsed_data.get('text', '')
        
        prompt = f"""Analyze the sentiment and emotional tone of this text.

TEXT:
{text}

Analyze:
1. Overall sentiment (positive, negative, neutral) with confidence score
2. Emotional tone (happy, angry, sad, excited, worried, etc.)
3. Urgency level (low, medium, high, critical)
4. Confidence level (uncertain, moderate, confident, very confident)
5. Key phrases that indicate sentiment
6. Sentiment shifts (if any)

Return as JSON with detailed sentiment analysis.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1500
                }
            )
            
            llm_response = response.json()
            sentiment = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_sentiment_in_kg(sentiment)
            
            return AgentResult(
                success=True,
                data=sentiment,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_sentiment_in_kg(self, sentiment: Dict[str, Any]):
        """Store sentiment analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="sentiment",
            data=sentiment,
            graph_type="semantic"
        )
