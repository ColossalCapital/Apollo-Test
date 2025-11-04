"""
Video Parser Agent - LLM-Powered Video Analysis

Layer 1 Data Extraction agent that uses LLM to parse videos
and extract multimedia intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class VideoParserAgent(Layer1Agent):
    """
    Video Parser - LLM-powered video analysis
    
    Takes videos and extracts:
    - Scene analysis and transitions
    - Audio transcription
    - Visual elements and objects
    - People and actions
    - Mood and tone
    - Content type and category
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=180.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="video_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered video analysis with multimedia intelligence",
            capabilities=["scene_analysis", "transcription", "action_recognition", "content_classification"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from video"""
        
        prompt = f"""You are an expert at analyzing videos. Extract comprehensive information from this video.

VIDEO DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Video metadata (duration, resolution, format)
2. Scene breakdown and transitions
3. Audio transcription and dialogue
4. Visual elements and objects
5. People, faces, and actions
6. Mood, tone, and atmosphere
7. Content type and category
8. Key moments and highlights
9. Educational vs entertainment value
10. Engagement potential

Return as JSON with detailed video analysis.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-vision",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_video_data_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'video'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_video_data_in_kg(self, video_data: Dict[str, Any]):
        """Store parsed video data in knowledge graphs"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="video",
            data=video_data
        )
