"""
Project Manager Agent - LLM-Powered Project Management Workflow

Layer 4 Workflow Orchestration agent that uses LLM to coordinate
project management workflows.
"""

from typing import Dict, Any, List
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ProjectManagerAgent(Layer4Agent):
    """
    Project Manager - LLM-powered project management orchestration
    
    Coordinates project workflows:
    1. Project planning and breakdown
    2. Task creation and assignment
    3. Progress tracking
    4. Deadline management
    5. Resource allocation
    6. Status reporting
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="project_manager",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="LLM-powered project management workflow orchestration",
            capabilities=["project_planning", "task_management", "progress_tracking", "resource_allocation"],
            dependencies=[]
        )
    
    async def orchestrate(self, trigger: Dict[str, Any]) -> AgentResult:
        """
        Orchestrate project management workflow
        
        Args:
            trigger: {
                "type": "new_project" | "update_progress" | "generate_report",
                "project": {...},
                "context": {...}
            }
            
        Returns:
            AgentResult with workflow execution results
        """
        
        trigger_type = trigger.get('type', 'new_project')
        
        if trigger_type == 'new_project':
            return await self._plan_new_project(trigger)
        elif trigger_type == 'update_progress':
            return await self._update_progress(trigger)
        elif trigger_type == 'generate_report':
            return await self._generate_report(trigger)
        else:
            return await self._generic_workflow(trigger)
    
    async def _plan_new_project(self, trigger: Dict[str, Any]) -> AgentResult:
        """Plan a new project with LLM"""
        
        prompt = f"""You are a project manager. Plan this new project.

PROJECT REQUEST:
{json.dumps(trigger, indent=2)}

CREATE A PROJECT PLAN:
1. Break down into phases
2. Identify key milestones
3. Create task list with dependencies
4. Estimate timeline
5. Identify required resources
6. Assess risks

Return as JSON:
{{
    "project": {{
        "name": "...",
        "description": "...",
        "timeline": "3 months",
        "budget": 50000
    }},
    "phases": [
        {{
            "name": "Phase 1: Planning",
            "duration": "2 weeks",
            "tasks": [
                {{
                    "id": "task_001",
                    "title": "Requirements gathering",
                    "assignee": "PM",
                    "duration": "1 week",
                    "dependencies": [],
                    "priority": "high"
                }}
            ]
        }}
    ],
    "milestones": [
        {{"date": "2025-12-01", "name": "Phase 1 complete"}}
    ],
    "resources": [
        {{"role": "Developer", "count": 2, "duration": "3 months"}},
        {{"role": "Designer", "count": 1, "duration": "1 month"}}
    ],
    "risks": [
        {{"risk": "Scope creep", "mitigation": "Weekly scope reviews"}}
    ],
    "estimated_completion": "2026-02-01"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            project_plan = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Execute the plan
            execution_results = await self._execute_project_plan(project_plan)
            
            return AgentResult(
                success=True,
                data={
                    'project_plan': project_plan,
                    'execution_results': execution_results
                },
                metadata={'agent': self.metadata.name, 'type': 'new_project'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _execute_project_plan(self, project_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the project plan"""
        
        results = []
        
        # Create project
        project_result = await self._create_project(project_plan.get('project', {}))
        results.append({'action': 'create_project', 'result': project_result})
        
        # Create tasks
        for phase in project_plan.get('phases', []):
            for task in phase.get('tasks', []):
                task_result = await self._create_task(task)
                results.append({'action': 'create_task', 'result': task_result})
        
        # Set milestones
        for milestone in project_plan.get('milestones', []):
            milestone_result = await self._create_milestone(milestone)
            results.append({'action': 'create_milestone', 'result': milestone_result})
        
        return results
    
    async def _create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create project in project management system"""
        # TODO: Integrate with Linear/Jira
        return {'success': True, 'project_id': 'proj_123'}
    
    async def _create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task in project management system"""
        # TODO: Integrate with Linear/Jira
        return {'success': True, 'task_id': task_data.get('id')}
    
    async def _create_milestone(self, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create milestone"""
        # TODO: Integrate with project management system
        return {'success': True, 'milestone_id': 'milestone_123'}
    
    async def _update_progress(self, trigger: Dict[str, Any]) -> AgentResult:
        """Update project progress"""
        pass
    
    async def _generate_report(self, trigger: Dict[str, Any]) -> AgentResult:
        """Generate project status report"""
        pass
    
    async def _generic_workflow(self, trigger: Dict[str, Any]) -> AgentResult:
        """Generic project workflow"""
        pass
