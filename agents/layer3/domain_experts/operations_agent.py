"""
Operations Agent - LLM-Powered Operations Management

Layer 3 Domain Expert agent that optimizes operations and processes.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class OperationsAgent(Layer3Agent):
    """
    Operations Agent - LLM-powered operations optimization
    
    Provides:
    - Process optimization
    - Workflow analysis
    - Resource allocation
    - Efficiency improvements
    - Cost reduction strategies
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="operations",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered operations and process optimization",
            capabilities=[
                "process_optimization",
                "workflow_analysis",
                "resource_allocation",
                "efficiency_improvements",
                "cost_reduction"
            ],
            dependencies=["knowledge_graph"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Analyze operations and provide optimization recommendations"""
        
        operation = domain_data.get('operation', {})
        
        prompt = f"""You are an expert operations manager. Analyze this operation and provide optimization recommendations.

OPERATION:
Process: {operation.get('process', 'N/A')}
Current State: {operation.get('current_state', 'N/A')}
Pain Points: {operation.get('pain_points', [])}
Goals: {operation.get('goals', [])}

ANALYZE:
1. Current process efficiency
2. Bottlenecks and constraints
3. Resource utilization
4. Cost analysis
5. Optimization opportunities
6. Automation potential
7. Recommended improvements
8. Implementation roadmap
9. Expected ROI

Return as JSON with detailed operations analysis and recommendations.
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
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_operations_in_kg(analysis)
            
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
    
    async def _store_operations_in_kg(self, analysis: Dict[str, Any]):
        """Store operations analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="operations_analysis",
            data=analysis,
            graph_type="business"
        )
