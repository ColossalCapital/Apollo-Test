"""
Performance Agent - LLM-Powered Performance Optimization

Layer 3 Domain Expert agent that optimizes application performance.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class PerformanceAgent(Layer3Agent):
    """
    Performance Agent - LLM-powered performance optimization
    
    Provides:
    - Performance analysis
    - Bottleneck identification
    - Optimization recommendations
    - Load testing strategies
    - Caching strategies
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="performance",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered performance analysis and optimization",
            capabilities=[
                "performance_analysis",
                "bottleneck_detection",
                "optimization_recommendations",
                "load_testing",
                "caching_strategies"
            ],
            dependencies=["knowledge_graph", "code_review"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.PERSONAL],
            app_contexts=[AppContext.AKASHIC],
            requires_subscription=["akashic"],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Analyze performance and provide optimization recommendations"""
        
        performance_data = domain_data.get('performance', {})
        
        prompt = f"""You are an expert performance engineer. Analyze this application's performance.

PERFORMANCE DATA:
Application: {performance_data.get('app', 'N/A')}
Metrics: {performance_data.get('metrics', {})}
Issues: {performance_data.get('issues', [])}
Load: {performance_data.get('load', 'N/A')}

ANALYZE:
1. Performance bottlenecks
2. Database query optimization
3. API response time improvements
4. Caching strategies (Redis, CDN)
5. Code-level optimizations
6. Infrastructure scaling recommendations
7. Load testing strategy
8. Monitoring and alerting setup
9. Performance budget recommendations
10. Quick wins vs long-term improvements

Return as JSON with detailed performance analysis and optimization plan.
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
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_performance_in_kg(analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_performance_in_kg(self, analysis: Dict[str, Any]):
        """Store performance analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="performance_analysis",
            data=analysis,
            graph_type="technical"
        )
