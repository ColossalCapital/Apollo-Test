"""
Design Agent - LLM-Powered Design and UX

Layer 3 Domain Expert agent that provides design and UX recommendations.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class DesignAgent(Layer3Agent):
    """
    Design Agent - LLM-powered design and UX expertise
    
    Provides:
    - UI/UX design recommendations
    - Brand identity guidance
    - Visual design critique
    - Accessibility improvements
    - Design system creation
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="design",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered design and UX expertise",
            capabilities=[
                "ui_design",
                "ux_design",
                "brand_identity",
                "accessibility",
                "design_systems"
            ],
            dependencies=["knowledge_graph"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS, AppContext.AKASHIC],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Provide design recommendations"""
        
        design_request = domain_data.get('request', {})
        
        prompt = f"""You are an expert UI/UX designer. Provide design recommendations.

REQUEST:
Type: {design_request.get('type', 'general')}
Context: {design_request.get('context', 'N/A')}
Target Audience: {design_request.get('audience', 'general')}
Platform: {design_request.get('platform', 'web')}

PROVIDE:
1. Design recommendations
2. Color palette suggestions
3. Typography recommendations
4. Layout and spacing guidelines
5. Accessibility considerations (WCAG compliance)
6. User flow improvements
7. Visual hierarchy suggestions
8. Design system components needed

Return as JSON with detailed design guidance.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.6,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            design_recommendations = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_design_in_kg(design_recommendations)
            
            return AgentResult(
                success=True,
                data=design_recommendations,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_design_in_kg(self, design: Dict[str, Any]):
        """Store design recommendations in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="design_recommendation",
            data=design,
            graph_type="technical"
        )
