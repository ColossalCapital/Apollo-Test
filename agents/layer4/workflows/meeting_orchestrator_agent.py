"""
Meeting Orchestrator Agent - LLM-Powered Meeting Workflow Orchestration

Layer 4 Workflow Orchestration agent that uses LLM to coordinate
multi-step meeting scheduling and preparation workflows.
"""

from typing import Dict, Any, List
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class MeetingOrchestratorAgent(Layer4Agent):
    """
    Meeting Orchestrator - LLM-powered meeting workflow coordination
    
    Coordinates multiple agents for meeting workflows:
    1. Parse meeting request (Layer 1)
    2. Recognize participants (Layer 2)
    3. Analyze context and importance (Layer 3)
    4. Find available times
    5. Schedule meeting
    6. Create prep document
    7. Send invitations
    8. Create follow-up tasks
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="meeting_orchestrator",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered meeting scheduling and preparation workflow",
            capabilities=["meeting_scheduling", "calendar_management", "prep_documents", "multi_step_workflow"],
            dependencies=["gmail_parser", "person_recognition"]
        )
    
    async def orchestrate(self, trigger: Dict[str, Any]) -> AgentResult:
        """
        Orchestrate meeting workflow
        
        Args:
            trigger: {
                "type": "meeting_request",
                "email": {...},  # Parsed email with meeting request
                "context": {...}
            }
            
        Returns:
            AgentResult with workflow execution results
        """
        
        # Plan the workflow
        workflow_plan = await self._plan_meeting_workflow(trigger)
        
        # Execute workflow
        results = await self._execute_workflow(workflow_plan)
        
        return AgentResult(
            success=True,
            data={
                "workflow_plan": workflow_plan,
                "execution_results": results,
                "meeting_scheduled": True
            },
            metadata={'agent': self.metadata.name}
        )
    
    async def _plan_meeting_workflow(self, trigger: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to plan meeting workflow"""
        
        prompt = f"""You are a meeting orchestration expert. Plan the workflow for this meeting request.

MEETING REQUEST:
{json.dumps(trigger, indent=2)}

PLAN the workflow:
1. Who are the participants?
2. What's the meeting about?
3. How important/urgent is it?
4. What preparation is needed?
5. What follow-up actions?

Create a workflow with these steps:
- Parse meeting request
- Recognize participants
- Find available times
- Schedule meeting
- Create prep document
- Send calendar invitations
- Create follow-up tasks

Return as JSON:
{{
    "meeting": {{
        "title": "...",
        "participants": [...],
        "duration": 60,
        "importance": "high|medium|low",
        "urgency": "urgent|normal"
    }},
    "steps": [
        {{"step": 1, "action": "find_available_times", "params": {{}}}},
        {{"step": 2, "action": "schedule_meeting", "params": {{}}}},
        {{"step": 3, "action": "create_prep_doc", "params": {{}}}},
        {{"step": 4, "action": "send_invitations", "params": {{}}}},
        {{"step": 5, "action": "create_tasks", "params": {{}}}}
    ],
    "prep_needed": true,
    "estimated_time": "3 minutes"
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
            return json.loads(llm_response['choices'][0]['message']['content'])
            
        except Exception as e:
            return {
                "meeting": {"title": "Meeting", "duration": 60},
                "steps": [{"step": 1, "action": "schedule_meeting"}]
            }
    
    async def _execute_workflow(self, workflow_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute meeting workflow steps"""
        
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
        
        if action == "find_available_times":
            return await self._find_available_times(step.get('params', {}))
        elif action == "schedule_meeting":
            return await self._schedule_meeting(step.get('params', {}))
        elif action == "create_prep_doc":
            return await self._create_prep_doc(step.get('params', {}))
        elif action == "send_invitations":
            return await self._send_invitations(step.get('params', {}))
        elif action == "create_tasks":
            return await self._create_tasks(step.get('params', {}))
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    async def _find_available_times(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find available times in calendars"""
        # TODO: Integrate with calendar API
        return {"success": True, "available_times": ["2025-11-01 14:00", "2025-11-01 15:00"]}
    
    async def _schedule_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule the meeting"""
        # TODO: Integrate with calendar API
        return {"success": True, "meeting_id": "meet_123"}
    
    async def _create_prep_doc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create meeting prep document"""
        # TODO: Integrate with document system
        return {"success": True, "doc_id": "doc_123"}
    
    async def _send_invitations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send calendar invitations"""
        # TODO: Integrate with email/calendar
        return {"success": True, "sent": 3}
    
    async def _create_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create follow-up tasks"""
        # TODO: Integrate with task management
        return {"success": True, "tasks_created": 2}
