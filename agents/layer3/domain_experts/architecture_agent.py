"""
Architecture Agent - LLM-Powered Software Architecture

Layer 3 Domain Expert agent that provides software architecture guidance.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class ArchitectureAgent(Layer3Agent):
    """
    Architecture Agent - LLM-powered software architecture expertise
    
    Provides:
    - System architecture design
    - Scalability recommendations
    - Technology stack selection
    - Microservices design
    - Database architecture
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="architecture",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered software architecture and system design",
            capabilities=[
                "system_design",
                "scalability_planning",
                "tech_stack_selection",
                "microservices_design",
                "database_architecture"
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
        """Provide architecture recommendations"""
        
        system = domain_data.get('system', {})
        
        prompt = f"""You are an expert software architect. Design a system architecture.

REQUIREMENTS:
System: {system.get('name', 'N/A')}
Scale: {system.get('scale', 'N/A')}
Requirements: {system.get('requirements', [])}
Constraints: {system.get('constraints', [])}

DESIGN:
1. High-level architecture diagram (components)
2. Technology stack recommendations
3. Database architecture (SQL, NoSQL, caching)
4. API design (REST, GraphQL, gRPC)
5. Scalability strategy (horizontal, vertical)
6. Security architecture
7. Deployment architecture (containers, serverless)
8. Monitoring and observability
9. Cost optimization strategies
10. Migration path (if applicable)

Return as JSON with detailed architecture design.
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
            architecture = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_architecture_in_kg(architecture)
            
            return AgentResult(
                success=True,
                data=architecture,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_architecture_in_kg(self, architecture: Dict[str, Any]):
        """Store architecture design in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="architecture_design",
            data=architecture,
            graph_type="technical"
        )
