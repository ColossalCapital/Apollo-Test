"""
SEO Agent - LLM-Powered Search Engine Optimization

Layer 3 Domain Expert agent that provides SEO analysis and recommendations.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class SEOAgent(Layer3Agent):
    """
    SEO Agent - LLM-powered search engine optimization
    
    Provides:
    - Keyword research
    - On-page SEO analysis
    - Content optimization
    - Technical SEO audit
    - Competitor analysis
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="seo",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered SEO analysis and optimization",
            capabilities=[
                "keyword_research",
                "on_page_seo",
                "content_optimization",
                "technical_seo",
                "competitor_analysis"
            ],
            dependencies=["knowledge_graph", "content_creation"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Provide SEO analysis and recommendations"""
        
        content = domain_data.get('content', {})
        
        prompt = f"""You are an expert SEO specialist. Analyze this content and provide SEO recommendations.

CONTENT:
Title: {content.get('title', 'N/A')}
URL: {content.get('url', 'N/A')}
Content: {content.get('body', 'N/A')}
Target Keywords: {content.get('keywords', [])}

ANALYZE:
1. Keyword optimization (density, placement, LSI keywords)
2. Title tag and meta description recommendations
3. Header structure (H1, H2, H3) optimization
4. Content quality and readability
5. Internal linking opportunities
6. Image optimization (alt text, file names)
7. URL structure recommendations
8. Schema markup suggestions
9. Mobile optimization
10. Page speed considerations
11. Competitor keyword gaps
12. Content improvement suggestions

Return as JSON with detailed SEO analysis and actionable recommendations.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            seo_analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_seo_in_kg(seo_analysis)
            
            return AgentResult(
                success=True,
                data=seo_analysis,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_seo_in_kg(self, seo: Dict[str, Any]):
        """Store SEO analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="seo_analysis",
            data=seo,
            graph_type="business"
        )
