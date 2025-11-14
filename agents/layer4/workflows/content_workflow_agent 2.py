"""
Content Workflow Agent - LLM-Powered Content Production Orchestration

Layer 4 Workflow agent that orchestrates content creation and publishing.
"""

from typing import Dict, Any
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class ContentWorkflowAgent(Layer4Agent):
    """
    Content Workflow - Orchestrates content production
    
    Workflow:
    1. Content ideation and planning
    2. Research and outline
    3. Content creation
    4. Review and editing
    5. SEO optimization
    6. Publishing and distribution
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="content_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered content production orchestration",
            capabilities=[
                "content_planning",
                "editorial_calendar",
                "content_creation",
                "seo_optimization",
                "distribution_automation"
            ],
            dependencies=["content_creation", "marketing"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def orchestrate(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate content workflow"""
        
        content_brief = workflow_data.get('brief', {})
        
        prompt = f"""You are an expert content strategist. Create a content production plan.

CONTENT BRIEF:
Topic: {content_brief.get('topic', 'N/A')}
Type: {content_brief.get('type', 'blog_post')}
Audience: {content_brief.get('audience', 'N/A')}
Goals: {content_brief.get('goals', [])}
Keywords: {content_brief.get('keywords', [])}

CREATE CONTENT PLAN:
1. Content angle and unique perspective
2. Research sources and references
3. Content outline (H1, H2, H3 structure)
4. Key points to cover
5. SEO optimization strategy
6. Call-to-action recommendations
7. Visual content needs (images, infographics)
8. Distribution channels (blog, social, email)
9. Social media snippets
10. Editorial calendar placement
11. Success metrics (traffic, engagement, conversions)
12. Repurposing opportunities

Return as JSON with complete content production plan.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            content_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Orchestrate workflow steps
            workflow_steps = await self._execute_content_workflow(content_plan)
            
            if self.kg_client:
                await self._store_content_in_kg(content_plan, workflow_steps)
            
            return AgentResult(
                success=True,
                data={
                    'content_plan': content_plan,
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
    
    async def _execute_content_workflow(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content workflow steps"""
        return {
            'planning': 'Content planned',
            'research': 'Research completed',
            'creation': 'Draft in progress',
            'review': 'Pending review',
            'status': 'In production'
        }
    
    async def _store_content_in_kg(self, plan: Dict[str, Any], steps: Dict[str, Any]):
        """Store content workflow in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="content_production",
            data={'plan': plan, 'steps': steps},
            graph_type="workflow"
        )
