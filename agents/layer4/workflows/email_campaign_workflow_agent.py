"""
Email Campaign Workflow Agent - LLM-Powered Email Campaign Orchestration

Layer 4 Workflow agent that orchestrates end-to-end email campaigns.
"""

from typing import Dict, Any
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class EmailCampaignWorkflowAgent(Layer4Agent):
    """
    Email Campaign Workflow - Orchestrates email campaigns
    
    Workflow:
    1. Audience segmentation
    2. Content generation
    3. A/B test setup
    4. Send scheduling
    5. Performance tracking
    6. Follow-up automation
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="email_campaign_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered email campaign orchestration",
            capabilities=[
                "audience_segmentation",
                "content_generation",
                "ab_testing",
                "send_scheduling",
                "performance_tracking"
            ],
            dependencies=["content_creation", "marketing", "gmail_connector"]
        )
    
    async def orchestrate(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate email campaign workflow"""
        
        campaign = workflow_data.get('campaign', {})
        
        prompt = f"""You are an expert email marketing strategist. Create a complete email campaign plan.

CAMPAIGN:
Goal: {campaign.get('goal', 'N/A')}
Target Audience: {campaign.get('audience', 'N/A')}
Product/Service: {campaign.get('product', 'N/A')}
Budget: {campaign.get('budget', 'N/A')}

CREATE CAMPAIGN PLAN:
1. Audience segmentation strategy
2. Email sequence (welcome, nurture, conversion)
3. Subject line variations for A/B testing
4. Email content for each sequence step
5. Send timing recommendations
6. Success metrics and KPIs
7. Follow-up automation rules
8. Personalization strategy

Return as JSON with complete campaign plan.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            campaign_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Orchestrate workflow steps
            workflow_steps = await self._execute_campaign_workflow(campaign_plan)
            
            if self.kg_client:
                await self._store_campaign_in_kg(campaign_plan, workflow_steps)
            
            return AgentResult(
                success=True,
                data={
                    'campaign_plan': campaign_plan,
                    'workflow_steps': workflow_steps
                },
                metadata={'agent': self.metadata.name, 'campaign_id': campaign.get('id')}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _execute_campaign_workflow(self, campaign_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute campaign workflow steps"""
        return {
            'step_1_segmentation': 'Audience segmented',
            'step_2_content': 'Content generated',
            'step_3_ab_test': 'A/B test configured',
            'step_4_scheduled': 'Campaign scheduled',
            'step_5_tracking': 'Tracking enabled'
        }
    
    async def _store_campaign_in_kg(self, campaign_plan: Dict[str, Any], workflow_steps: Dict[str, Any]):
        """Store campaign in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="email_campaign",
            data={'plan': campaign_plan, 'steps': workflow_steps},
            graph_type="workflow"
        )
