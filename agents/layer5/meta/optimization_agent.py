"""
Optimization Agent - LLM-Powered System Optimization

Layer 5 Meta-Orchestration agent that optimizes the entire agent system.
"""

from typing import Dict, Any
from ...base import Layer5Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class OptimizationAgent(Layer5Agent):
    """
    Optimization Agent - System-wide optimization
    
    Optimizes:
    - Agent performance and efficiency
    - Workflow orchestration
    - Resource allocation
    - Cost optimization
    - Learning system improvements
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="optimization",
            layer=AgentLayer.LAYER_5_META,
            version="1.0.0",
            description="LLM-powered system-wide optimization",
            capabilities=[
                "performance_optimization",
                "workflow_optimization",
                "resource_allocation",
                "cost_optimization",
                "learning_optimization"
            ],
            dependencies=["meta_orchestrator", "learning"],
            
            # Metadata for filtering
            entity_types=[EntityType.UNIVERSAL],
            app_contexts=[AppContext.ALL],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def optimize(self, system_data: Dict[str, Any]) -> AgentResult:
        """Optimize the entire agent system"""
        
        metrics = system_data.get('metrics', {})
        
        prompt = f"""You are an expert system optimizer. Analyze the Apollo agent system and provide optimization recommendations.

SYSTEM METRICS:
Agent Performance: {metrics.get('agent_performance', {})}
Workflow Success Rates: {metrics.get('workflow_success', {})}
Resource Usage: {metrics.get('resource_usage', {})}
Cost: {metrics.get('cost', {})}
User Satisfaction: {metrics.get('user_satisfaction', {})}

OPTIMIZE:
1. Agent performance bottlenecks
2. Workflow orchestration improvements
3. Resource allocation optimization
4. Cost reduction opportunities
5. Learning system enhancements
6. Agent selection improvements
7. Caching and efficiency gains
8. Parallel execution opportunities
9. Model selection optimization
10. Infrastructure recommendations
11. Quick wins (immediate impact)
12. Long-term strategic improvements

Return as JSON with comprehensive optimization plan.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            optimization_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_optimization_in_kg(optimization_plan)
            
            return AgentResult(
                success=True,
                data=optimization_plan,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_optimization_in_kg(self, optimization: Dict[str, Any]):
        """Store optimization plan in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="system_optimization",
            data=optimization,
            graph_type="workflow"
        )
