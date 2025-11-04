"""
QA Testing Agent - LLM-Powered Quality Assurance

Layer 3 Domain Expert agent that provides QA and testing strategies.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class QATestingAgent(Layer3Agent):
    """
    QA Testing Agent - LLM-powered quality assurance
    
    Provides:
    - Test strategy development
    - Test case generation
    - Bug analysis
    - Test automation recommendations
    - Quality metrics
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="qa_testing",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered QA and testing strategies",
            capabilities=[
                "test_strategy",
                "test_case_generation",
                "bug_analysis",
                "test_automation",
                "quality_metrics"
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
        """Provide QA and testing recommendations"""
        
        feature = domain_data.get('feature', {})
        
        prompt = f"""You are an expert QA engineer. Create a comprehensive testing strategy.

FEATURE:
Name: {feature.get('name', 'N/A')}
Description: {feature.get('description', 'N/A')}
Requirements: {feature.get('requirements', [])}
User Stories: {feature.get('user_stories', [])}

CREATE TESTING STRATEGY:
1. Test plan overview
2. Unit test cases
3. Integration test cases
4. End-to-end test cases
5. Edge cases and negative tests
6. Performance test scenarios
7. Security test cases
8. Accessibility tests
9. Test automation recommendations
10. Quality metrics and coverage goals
11. Bug severity classification
12. Regression testing strategy

Return as JSON with comprehensive testing strategy and test cases.
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
            testing_strategy = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_testing_in_kg(testing_strategy)
            
            return AgentResult(
                success=True,
                data=testing_strategy,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_testing_in_kg(self, testing: Dict[str, Any]):
        """Store testing strategy in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="testing_strategy",
            data=testing,
            graph_type="technical"
        )
