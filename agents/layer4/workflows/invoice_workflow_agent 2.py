"""
Invoice Workflow Agent - LLM-Powered Invoice Processing Orchestration

Layer 4 Workflow Orchestration agent that uses LLM to coordinate
multi-step invoice processing workflows.
"""

from typing import Dict, Any, List
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class InvoiceWorkflowAgent(Layer4Agent):
    """
    Invoice Workflow Orchestrator - LLM-powered multi-step invoice processing
    
    Coordinates multiple agents to process invoices end-to-end:
    1. Parse invoice (Layer 1)
    2. Recognize vendor (Layer 2)
    3. Analyze financial impact (Layer 3)
    4. Execute workflow (create task, schedule payment, update systems)
    5. Send notifications
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="invoice_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered invoice processing workflow orchestration",
            capabilities=["invoice_processing", "payment_scheduling", "multi_step_workflow", "task_creation"],
            dependencies=["quickbooks_parser", "person_recognition", "financial_analyst"]
        )
    
    async def orchestrate(self, trigger: Dict[str, Any]) -> AgentResult:
        """
        Orchestrate invoice processing workflow
        
        Args:
            trigger: {
                "type": "invoice_received",
                "raw_invoice": {...},  # Raw QuickBooks data
                "context": {...}
            }
            
        Returns:
            AgentResult with workflow execution results
        """
        
        # Step 1: Decide workflow based on invoice
        workflow_plan = await self._plan_workflow(trigger)
        
        # Step 2: Execute workflow
        results = await self._execute_workflow(workflow_plan)
        
        return AgentResult(
            success=True,
            data={
                "workflow_plan": workflow_plan,
                "execution_results": results,
                "status": "completed"
            },
            metadata={'agent': self.metadata.name}
        )
    
    async def _plan_workflow(self, trigger: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to plan the workflow"""
        
        prompt = f"""You are an invoice processing workflow orchestrator. Plan the workflow for this invoice.

INVOICE DATA:
{json.dumps(trigger, indent=2)}

PLAN the workflow:
1. What agents should be called? (parser, recognition, analyst)
2. What actions should be taken? (create task, schedule payment, update QuickBooks, send notification)
3. What's the priority? (urgent, high, medium, low)
4. Any special handling? (approval required, auto-pay, etc.)

Consider:
- Invoice amount (auto-approve if < $1000?)
- Vendor history (trusted vendor?)
- Due date (urgent if < 7 days?)
- Cash flow impact

Return as JSON:
{{
    "steps": [
        {{"step": 1, "agent": "quickbooks_parser", "action": "parse_invoice"}},
        {{"step": 2, "agent": "person_recognition", "action": "recognize_vendor"}},
        {{"step": 3, "agent": "financial_analyst", "action": "analyze_impact"}},
        {{"step": 4, "action": "create_task", "params": {{}}}},
        {{"step": 5, "action": "schedule_payment", "params": {{}}}},
        {{"step": 6, "action": "update_quickbooks", "params": {{}}}},
        {{"step": 7, "action": "send_notification", "params": {{}}}}
    ],
    "priority": "high",
    "auto_approve": false,
    "requires_review": true,
    "estimated_time": "5 minutes"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1500
                }
            )
            
            llm_response = response.json()
            workflow_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            return workflow_plan
            
        except Exception as e:
            # Fallback to default workflow
            return {
                "steps": [
                    {"step": 1, "action": "create_task", "params": {"title": "Review invoice"}},
                    {"step": 2, "action": "send_notification", "params": {"message": "New invoice received"}}
                ],
                "priority": "medium",
                "auto_approve": False
            }
    
    async def _execute_workflow(self, workflow_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the workflow steps"""
        
        results = []
        
        for step in workflow_plan.get('steps', []):
            step_result = await self._execute_step(step)
            results.append({
                "step": step['step'],
                "action": step.get('action'),
                "result": step_result,
                "status": "completed" if step_result.get('success') else "failed"
            })
        
        return results
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        action = step.get('action')
        
        if action == "create_task":
            return await self._create_task(step.get('params', {}))
        elif action == "schedule_payment":
            return await self._schedule_payment(step.get('params', {}))
        elif action == "update_quickbooks":
            return await self._update_quickbooks(step.get('params', {}))
        elif action == "send_notification":
            return await self._send_notification(step.get('params', {}))
        else:
            # Call another agent
            agent_name = step.get('agent')
            return await self._call_agent(agent_name, step.get('params', {}))
    
    async def _create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task in task management system"""
        # TODO: Integrate with task management system
        return {"success": True, "task_id": "task_123"}
    
    async def _schedule_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule payment"""
        # TODO: Integrate with payment system
        return {"success": True, "payment_id": "pay_123"}
    
    async def _update_quickbooks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update QuickBooks"""
        # TODO: Integrate with QuickBooks API
        return {"success": True}
    
    async def _send_notification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification"""
        # TODO: Integrate with notification system
        return {"success": True}
    
    async def _call_agent(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call another agent"""
        # TODO: Use agent factory to call other agents
        return {"success": True, "agent": agent_name}
