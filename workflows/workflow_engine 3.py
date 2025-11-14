"""
Apollo Workflow Engine

Chain agents together to create autonomous workflows.

Features:
- Multi-step agent chains
- Input/output mapping between steps
- Conditional execution
- Error handling & rollback
- Workflow templates
- Success tracking
"""

import logging
from typing import List, Dict, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class WorkflowStep:
    """
    Single step in a workflow
    
    Example:
        step = WorkflowStep(
            agent_name="CalendarAgent",
            input_mapping={"user_id": "trigger.user_id"},
            output_mapping={"availability": "my_availability"},
            condition=lambda state: state.get("needs_meeting")
        )
    """
    agent_name: str
    input_mapping: Dict[str, str]  # Map workflow vars to agent inputs
    output_mapping: Dict[str, str]  # Map agent outputs to workflow vars
    condition: Optional[Callable[[Dict], bool]] = None  # Optional condition
    error_handler: Optional[str] = None  # Error handling agent
    rollback_handler: Optional[Callable] = None  # Rollback function
    timeout_seconds: int = 30


@dataclass
class Workflow:
    """
    Complete workflow definition
    
    Example:
        workflow = Workflow(
            id="meeting_scheduling",
            name="Schedule Meeting from Email",
            trigger={"type": "email", "intent": "schedule_meeting"},
            steps=[step1, step2, step3],
            variables={"default_duration": 60}
        )
    """
    id: str
    name: str
    description: str = ""
    trigger: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    
    # Statistics
    success_count: int = 0
    failure_count: int = 0
    total_executions: int = 0
    average_duration_seconds: float = 0.0
    
    # Configuration
    max_retries: int = 3
    retry_delay_seconds: int = 5
    enable_rollback: bool = True


@dataclass
class WorkflowExecution:
    """Track a single workflow execution"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    state: Dict[str, Any]
    results: List[Dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    rollback_performed: bool = False


class WorkflowEngine:
    """
    Execute and manage workflows
    
    Usage:
        engine = WorkflowEngine()
        
        # Register agents
        engine.register_agent("CalendarAgent", calendar_agent)
        engine.register_agent("EmailAgent", email_agent)
        
        # Register workflow
        engine.register_workflow(meeting_workflow)
        
        # Execute workflow
        result = await engine.execute_workflow(
            workflow_id="meeting_scheduling",
            trigger_data={"email": email_data},
            user_id="user_123"
        )
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.agents: Dict[str, Any] = {}
        self.executions: List[WorkflowExecution] = []
        
    # ========================================================================
    # WORKFLOW REGISTRATION
    # ========================================================================
    
    def register_workflow(self, workflow: Workflow):
        """Register a workflow template"""
        self.workflows[workflow.id] = workflow
        logger.info(f"✅ Registered workflow: {workflow.name}")
        
    def register_agent(self, agent_name: str, agent: Any):
        """Register an agent for use in workflows"""
        self.agents[agent_name] = agent
        logger.info(f"✅ Registered agent: {agent_name}")
        
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
        
    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================
    
    async def execute_workflow(
        self,
        workflow_id: str,
        trigger_data: Dict[str, Any],
        user_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Args:
            workflow_id: ID of workflow to execute
            trigger_data: Data that triggered the workflow
            user_id: User executing the workflow
            org_id: Optional organization ID
            
        Returns:
            {
                'success': bool,
                'execution_id': str,
                'results': List[Dict],
                'final_state': Dict,
                'duration_seconds': float
            }
        """
        
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {
                'success': False,
                'error': f"Workflow not found: {workflow_id}"
            }
            
        # Create execution record
        execution = WorkflowExecution(
            execution_id=f"exec_{datetime.now().timestamp()}",
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            state={
                "trigger": trigger_data,
                "user_id": user_id,
                "org_id": org_id,
                **workflow.variables
            },
            results=[],
            started_at=datetime.now()
        )
        
        self.executions.append(execution)
        
        logger.info(f"🚀 Executing workflow: {workflow.name}")
        logger.info(f"   Execution ID: {execution.execution_id}")
        
        try:
            # Execute each step
            for i, step in enumerate(workflow.steps):
                logger.info(f"   Step {i+1}/{len(workflow.steps)}: {step.agent_name}")
                
                # Check condition
                if step.condition and not step.condition(execution.state):
                    logger.info(f"   ⏭️  Skipping (condition not met)")
                    continue
                
                # Execute step with retries
                step_result = await self._execute_step_with_retry(
                    step,
                    execution.state,
                    workflow.max_retries,
                    workflow.retry_delay_seconds
                )
                
                if not step_result['success']:
                    # Step failed
                    execution.status = WorkflowStatus.FAILED
                    execution.error = step_result.get('error')
                    
                    # Attempt rollback if enabled
                    if workflow.enable_rollback:
                        await self._rollback_workflow(execution)
                    
                    workflow.failure_count += 1
                    workflow.total_executions += 1
                    
                    return {
                        'success': False,
                        'execution_id': execution.execution_id,
                        'error': step_result.get('error'),
                        'failed_step': step.agent_name,
                        'results': execution.results
                    }
                
                # Store result
                execution.results.append({
                    'step': step.agent_name,
                    'result': step_result['result'],
                    'success': True
                })
                
                # Update state with outputs
                execution.state.update(
                    self._map_outputs(step.output_mapping, step_result['result'])
                )
            
            # Workflow completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            
            duration = (execution.completed_at - execution.started_at).total_seconds()
            
            # Update statistics
            workflow.success_count += 1
            workflow.total_executions += 1
            workflow.average_duration_seconds = (
                (workflow.average_duration_seconds * (workflow.total_executions - 1) + duration)
                / workflow.total_executions
            )
            
            logger.info(f"✅ Workflow completed: {workflow.name}")
            logger.info(f"   Duration: {duration:.2f}s")
            
            return {
                'success': True,
                'execution_id': execution.execution_id,
                'workflow_id': workflow_id,
                'results': execution.results,
                'final_state': execution.state,
                'duration_seconds': duration
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            
            if workflow.enable_rollback:
                await self._rollback_workflow(execution)
            
            workflow.failure_count += 1
            workflow.total_executions += 1
            
            return {
                'success': False,
                'execution_id': execution.execution_id,
                'error': str(e),
                'results': execution.results
            }
    
    async def _execute_step_with_retry(
        self,
        step: WorkflowStep,
        state: Dict[str, Any],
        max_retries: int,
        retry_delay: int
    ) -> Dict[str, Any]:
        """Execute a step with retry logic"""
        
        for attempt in range(max_retries):
            try:
                # Map inputs
                agent_input = self._map_inputs(step.input_mapping, state)
                
                # Get agent
                agent = self.agents.get(step.agent_name)
                if not agent:
                    return {
                        'success': False,
                        'error': f"Agent not found: {step.agent_name}"
                    }
                
                # Execute agent with timeout
                result = await asyncio.wait_for(
                    agent.execute(agent_input),
                    timeout=step.timeout_seconds
                )
                
                return {
                    'success': True,
                    'result': result
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"⏱️  Step timeout (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    return {
                        'success': False,
                        'error': f"Step timed out after {max_retries} attempts"
                    }
                    
            except Exception as e:
                logger.warning(f"⚠️  Step error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    # Try error handler if available
                    if step.error_handler:
                        return await self._handle_step_error(step, state, e)
                    
                    return {
                        'success': False,
                        'error': str(e)
                    }
    
    async def _handle_step_error(
        self,
        step: WorkflowStep,
        state: Dict[str, Any],
        error: Exception
    ) -> Dict[str, Any]:
        """Handle step error with error handler agent"""
        
        try:
            error_agent = self.agents.get(step.error_handler)
            if error_agent:
                result = await error_agent.execute({
                    'error': str(error),
                    'step': step.agent_name,
                    'state': state
                })
                return {
                    'success': True,
                    'result': result,
                    'error_handled': True
                }
        except Exception as e:
            logger.error(f"Error handler failed: {e}")
        
        return {
            'success': False,
            'error': str(error)
        }
    
    async def _rollback_workflow(self, execution: WorkflowExecution):
        """Rollback a failed workflow"""
        
        logger.info(f"🔄 Rolling back workflow: {execution.workflow_id}")
        
        workflow = self.workflows.get(execution.workflow_id)
        if not workflow:
            return
        
        # Execute rollback handlers in reverse order
        for i, step in enumerate(reversed(workflow.steps)):
            if step.rollback_handler:
                try:
                    await step.rollback_handler(execution.state)
                    logger.info(f"   ✅ Rolled back: {step.agent_name}")
                except Exception as e:
                    logger.error(f"   ❌ Rollback failed for {step.agent_name}: {e}")
        
        execution.status = WorkflowStatus.ROLLED_BACK
        execution.rollback_performed = True
    
    def _map_inputs(
        self,
        mapping: Dict[str, str],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map workflow state to agent inputs"""
        
        result = {}
        for agent_key, state_path in mapping.items():
            # Support nested paths like "trigger.email.from"
            value = state
            for part in state_path.split('.'):
                value = value.get(part, {})
            result[agent_key] = value
        
        return result
    
    def _map_outputs(
        self,
        mapping: Dict[str, str],
        agent_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map agent outputs to workflow state"""
        
        result = {}
        for state_key, agent_key in mapping.items():
            if agent_key in agent_output:
                result[state_key] = agent_output[agent_key]
        
        return result
    
    # ========================================================================
    # WORKFLOW MANAGEMENT
    # ========================================================================
    
    def get_workflow_statistics(self, workflow_id: str) -> Dict[str, Any]:
        """Get statistics for a workflow"""
        
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {'error': 'Workflow not found'}
        
        success_rate = (
            workflow.success_count / workflow.total_executions
            if workflow.total_executions > 0
            else 0.0
        )
        
        return {
            'workflow_id': workflow_id,
            'name': workflow.name,
            'total_executions': workflow.total_executions,
            'success_count': workflow.success_count,
            'failure_count': workflow.failure_count,
            'success_rate': success_rate,
            'average_duration_seconds': workflow.average_duration_seconds
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all registered workflows"""
        
        return [
            {
                'id': w.id,
                'name': w.name,
                'description': w.description,
                'steps': len(w.steps),
                'success_rate': (
                    w.success_count / w.total_executions
                    if w.total_executions > 0
                    else 0.0
                )
            }
            for w in self.workflows.values()
        ]
    
    def get_recent_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent workflow executions"""
        
        executions = self.executions
        
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        
        # Sort by started_at descending
        executions = sorted(executions, key=lambda e: e.started_at, reverse=True)
        
        return [
            {
                'execution_id': e.execution_id,
                'workflow_id': e.workflow_id,
                'status': e.status.value,
                'started_at': e.started_at.isoformat(),
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                'duration_seconds': (
                    (e.completed_at - e.started_at).total_seconds()
                    if e.completed_at
                    else None
                ),
                'error': e.error,
                'rollback_performed': e.rollback_performed
            }
            for e in executions[:limit]
        ]


# Global instance
_workflow_engine = WorkflowEngine()


def get_workflow_engine() -> WorkflowEngine:
    """Get global workflow engine"""
    return _workflow_engine
