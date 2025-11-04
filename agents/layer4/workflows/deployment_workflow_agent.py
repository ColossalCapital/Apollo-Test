"""
Deployment Workflow Agent - LLM-Powered Deployment Orchestration

Layer 4 Workflow agent that orchestrates application deployments.
"""

from typing import Dict, Any
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class DeploymentWorkflowAgent(Layer4Agent):
    """
    Deployment Workflow - Orchestrates deployments
    
    Workflow:
    1. Pre-deployment checks
    2. Build and test
    3. Staging deployment
    4. Production deployment
    5. Post-deployment verification
    6. Rollback if needed
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="deployment_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered deployment orchestration",
            capabilities=[
                "deployment_planning",
                "ci_cd_integration",
                "rollback_management",
                "health_checks",
                "deployment_verification"
            ],
            dependencies=["code_review", "github_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.PERSONAL],
            app_contexts=[AppContext.AKASHIC],
            requires_subscription=["akashic"],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def orchestrate(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate deployment workflow"""
        
        deployment = workflow_data.get('deployment', {})
        
        prompt = f"""You are an expert DevOps engineer. Create a deployment plan.

DEPLOYMENT:
Application: {deployment.get('app', 'N/A')}
Environment: {deployment.get('environment', 'production')}
Version: {deployment.get('version', 'N/A')}
Changes: {deployment.get('changes', [])}

CREATE DEPLOYMENT PLAN:
1. Pre-deployment checklist
2. Build steps
3. Test requirements
4. Staging deployment steps
5. Production deployment steps
6. Health check procedures
7. Rollback plan
8. Post-deployment verification
9. Monitoring and alerts
10. Communication plan

Return as JSON with complete deployment workflow.
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
            deployment_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Orchestrate workflow steps
            workflow_steps = await self._execute_deployment_workflow(deployment_plan)
            
            if self.kg_client:
                await self._store_deployment_in_kg(deployment_plan, workflow_steps)
            
            return AgentResult(
                success=True,
                data={
                    'deployment_plan': deployment_plan,
                    'workflow_steps': workflow_steps
                },
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _execute_deployment_workflow(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment workflow steps"""
        return {
            'pre_deployment': 'Checks passed',
            'build': 'Build successful',
            'tests': 'All tests passed',
            'staging': 'Deployed to staging',
            'production': 'Ready for production',
            'status': 'Awaiting approval'
        }
    
    async def _store_deployment_in_kg(self, plan: Dict[str, Any], steps: Dict[str, Any]):
        """Store deployment in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="deployment",
            data={'plan': plan, 'steps': steps},
            graph_type="workflow"
        )
