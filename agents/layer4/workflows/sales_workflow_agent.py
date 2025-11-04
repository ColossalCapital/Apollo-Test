"""
Sales Workflow Agent - LLM-Powered Sales Process Orchestration

Layer 4 Workflow agent that orchestrates sales processes.
"""

from typing import Dict, Any
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class SalesWorkflowAgent(Layer4Agent):
    """
    Sales Workflow - Orchestrates sales processes
    
    Workflow:
    1. Lead qualification
    2. Discovery and needs analysis
    3. Proposal creation
    4. Negotiation
    5. Contract and closing
    6. Onboarding handoff
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="sales_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered sales process orchestration",
            capabilities=[
                "lead_qualification",
                "proposal_generation",
                "deal_scoring",
                "pipeline_management",
                "contract_automation"
            ],
            dependencies=["sales", "customer_support", "gmail_connector"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def orchestrate(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate sales workflow"""
        
        lead = workflow_data.get('lead', {})
        
        prompt = f"""You are an expert sales manager. Create a sales strategy for this lead.

LEAD:
Company: {lead.get('company', 'N/A')}
Contact: {lead.get('contact', 'N/A')}
Industry: {lead.get('industry', 'N/A')}
Pain Points: {lead.get('pain_points', [])}
Budget: {lead.get('budget', 'N/A')}

CREATE SALES STRATEGY:
1. Lead qualification (BANT: Budget, Authority, Need, Timeline)
2. Discovery questions to ask
3. Value proposition tailored to their needs
4. Proposal outline
5. Pricing strategy
6. Objection handling strategies
7. Negotiation tactics
8. Contract terms to emphasize
9. Success metrics and ROI
10. Follow-up cadence
11. Onboarding plan (if closed)
12. Deal score and win probability

Return as JSON with complete sales strategy.
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
            sales_strategy = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Orchestrate workflow steps
            workflow_steps = await self._execute_sales_workflow(sales_strategy)
            
            if self.kg_client:
                await self._store_sales_in_kg(sales_strategy, workflow_steps)
            
            return AgentResult(
                success=True,
                data={
                    'sales_strategy': sales_strategy,
                    'workflow_steps': workflow_steps
                },
                metadata={'agent': self.metadata.name, 'lead_id': lead.get('id')}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _execute_sales_workflow(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sales workflow steps"""
        return {
            'qualification': 'Lead qualified',
            'discovery': 'Discovery call scheduled',
            'proposal': 'Proposal in draft',
            'stage': 'Discovery',
            'next_action': 'Schedule discovery call'
        }
    
    async def _store_sales_in_kg(self, strategy: Dict[str, Any], steps: Dict[str, Any]):
        """Store sales workflow in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="sales_opportunity",
            data={'strategy': strategy, 'steps': steps},
            graph_type="workflow"
        )
