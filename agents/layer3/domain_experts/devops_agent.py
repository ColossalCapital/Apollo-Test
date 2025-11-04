"""
DevOps Agent - LLM-Powered DevOps and Infrastructure

Layer 3 Domain Expert agent that provides DevOps and infrastructure expertise.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class DevOpsAgent(Layer3Agent):
    """
    DevOps Agent - LLM-powered DevOps and infrastructure
    
    Provides:
    - Infrastructure as Code
    - CI/CD pipeline optimization
    - Container orchestration
    - Monitoring and alerting
    - Security best practices
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="devops",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered DevOps and infrastructure expertise",
            capabilities=[
                "infrastructure_as_code",
                "cicd_optimization",
                "container_orchestration",
                "monitoring_setup",
                "security_hardening"
            ],
            dependencies=["knowledge_graph", "architecture", "security"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.PERSONAL],
            app_contexts=[AppContext.AKASHIC],
            requires_subscription=["akashic"],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Provide DevOps recommendations"""
        
        infrastructure = domain_data.get('infrastructure', {})
        
        prompt = f"""You are an expert DevOps engineer. Analyze this infrastructure and provide recommendations.

INFRASTRUCTURE:
{json.dumps(infrastructure, indent=2)}

ANALYZE:
1. Infrastructure as Code (Terraform, CloudFormation, Pulumi)
2. CI/CD pipeline optimization
3. Container strategy (Docker, Kubernetes)
4. Deployment strategies (blue-green, canary, rolling)
5. Monitoring and observability (Prometheus, Grafana, Datadog)
6. Logging and tracing (ELK, Jaeger)
7. Security hardening (secrets management, network policies)
8. Backup and disaster recovery
9. Cost optimization
10. Scalability improvements
11. High availability setup
12. Performance tuning

Return as JSON with detailed DevOps recommendations and implementation steps.
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
            recommendations = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_devops_in_kg(recommendations)
            
            return AgentResult(
                success=True,
                data=recommendations,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_devops_in_kg(self, devops: Dict[str, Any]):
        """Store DevOps recommendations in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="devops_recommendations",
            data=devops,
            graph_type="technical"
        )
