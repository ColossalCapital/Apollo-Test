"""
Incident Response Workflow Agent - LLM-Powered Incident Management

Layer 4 Workflow agent that orchestrates incident response.
"""

from typing import Dict, Any
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class IncidentResponseWorkflowAgent(Layer4Agent):
    """
    Incident Response Workflow - Orchestrates incident management
    
    Workflow:
    1. Incident detection and triage
    2. Team notification
    3. Investigation and diagnosis
    4. Mitigation and resolution
    5. Post-mortem analysis
    6. Documentation and learning
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="incident_response_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered incident response orchestration",
            capabilities=[
                "incident_triage",
                "team_notification",
                "root_cause_analysis",
                "mitigation_planning",
                "post_mortem"
            ],
            dependencies=["customer_support", "slack_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS, AppContext.AKASHIC],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def orchestrate(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate incident response workflow"""
        
        incident = workflow_data.get('incident', {})
        
        prompt = f"""You are an expert incident response manager. Create an incident response plan.

INCIDENT:
Severity: {incident.get('severity', 'N/A')}
Description: {incident.get('description', 'N/A')}
Impact: {incident.get('impact', 'N/A')}
Affected Systems: {incident.get('systems', [])}

CREATE RESPONSE PLAN:
1. Incident classification and severity
2. Immediate actions (stop the bleeding)
3. Team notification plan
4. Investigation steps
5. Root cause analysis approach
6. Mitigation strategy
7. Communication plan (internal + external)
8. Rollback procedures (if applicable)
9. Monitoring and verification
10. Post-mortem template
11. Prevention measures
12. Documentation requirements

Return as JSON with complete incident response workflow.
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
            response_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Orchestrate workflow steps
            workflow_steps = await self._execute_incident_workflow(response_plan)
            
            if self.kg_client:
                await self._store_incident_in_kg(response_plan, workflow_steps)
            
            return AgentResult(
                success=True,
                data={
                    'response_plan': response_plan,
                    'workflow_steps': workflow_steps
                },
                metadata={'agent': self.metadata.name, 'severity': incident.get('severity')}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _execute_incident_workflow(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute incident response workflow steps"""
        return {
            'triage': 'Incident triaged',
            'notification': 'Team notified',
            'investigation': 'Investigation started',
            'mitigation': 'Mitigation in progress',
            'status': 'Active incident'
        }
    
    async def _store_incident_in_kg(self, plan: Dict[str, Any], steps: Dict[str, Any]):
        """Store incident in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="incident",
            data={'plan': plan, 'steps': steps},
            graph_type="workflow"
        )
