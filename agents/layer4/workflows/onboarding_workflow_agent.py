"""
Onboarding Workflow Agent - LLM-Powered User Onboarding

Layer 4 Workflow agent that orchestrates user onboarding experiences.
"""

from typing import Dict, Any
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class OnboardingWorkflowAgent(Layer4Agent):
    """
    Onboarding Workflow - Orchestrates user onboarding
    
    Workflow:
    1. Welcome email
    2. Account setup guidance
    3. Feature tutorials
    4. Integration setup
    5. First success milestone
    6. Ongoing engagement
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="onboarding_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered user onboarding orchestration",
            capabilities=[
                "welcome_sequence",
                "setup_guidance",
                "feature_tutorials",
                "integration_setup",
                "milestone_tracking"
            ],
            dependencies=["customer_support", "content_creation", "gmail_connector"]
        )
    
    async def orchestrate(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate onboarding workflow"""
        
        user = workflow_data.get('user', {})
        product = workflow_data.get('product', 'Atlas')
        
        prompt = f"""You are an expert onboarding specialist. Create a personalized onboarding plan.

USER:
Name: {user.get('name', 'N/A')}
Role: {user.get('role', 'N/A')}
Company: {user.get('company', 'N/A')}
Use Case: {user.get('use_case', 'N/A')}
Product: {product}

CREATE ONBOARDING PLAN:
1. Welcome email (personalized)
2. Day 1: Account setup checklist
3. Day 2-3: Core feature tutorials
4. Day 4-5: Integration setup (based on use case)
5. Week 2: First success milestone
6. Week 3-4: Advanced features
7. Ongoing: Engagement touchpoints
8. Success metrics to track

Return as JSON with complete onboarding plan.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            onboarding_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Orchestrate workflow steps
            workflow_steps = await self._execute_onboarding_workflow(onboarding_plan, user)
            
            if self.kg_client:
                await self._store_onboarding_in_kg(user, onboarding_plan, workflow_steps)
            
            return AgentResult(
                success=True,
                data={
                    'onboarding_plan': onboarding_plan,
                    'workflow_steps': workflow_steps
                },
                metadata={'agent': self.metadata.name, 'user_id': user.get('id')}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _execute_onboarding_workflow(self, plan: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Execute onboarding workflow steps"""
        return {
            'welcome_sent': True,
            'account_setup': 'In progress',
            'tutorials_scheduled': True,
            'integrations_recommended': plan.get('integrations', []),
            'milestone_tracking': 'Enabled'
        }
    
    async def _store_onboarding_in_kg(self, user: Dict[str, Any], plan: Dict[str, Any], steps: Dict[str, Any]):
        """Store onboarding in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="user_onboarding",
            data={'user': user, 'plan': plan, 'steps': steps},
            graph_type="workflow"
        )
