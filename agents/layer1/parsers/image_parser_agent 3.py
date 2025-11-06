"""
Image Parser Agent - LLM-Powered Image Analysis

Layer 1 Data Extraction agent that uses LLM to parse images
and extract visual intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ImageParserAgent(Layer1Agent):
    """
    Image Parser - LLM-powered image analysis
    
    Takes images and extracts:
    - Objects and scenes
    - Text (OCR)
    - Faces and emotions
    - Meme templates
    - Visual style and aesthetics
    - Context and meaning
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="image_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered image analysis with visual intelligence",
            capabilities=["object_detection", "ocr", "face_recognition", "meme_detection", "aesthetic_analysis"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from image"""
        
        prompt = f"""You are an expert at analyzing images. Extract comprehensive information from this image.

IMAGE DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Main subjects and objects
2. Scene and setting
3. Text content (OCR)
4. Faces and emotions
5. Colors and composition
6. Visual style and aesthetics
7. Meme template (if applicable)
8. Cultural references
9. Context and meaning
10. Potential uses

Return as JSON with detailed image analysis.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-vision",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_image_data_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'image'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_image_data_in_kg(self, image_data: Dict[str, Any]):
        """Store parsed image data in knowledge graphs"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="image",
            data=image_data
        )
