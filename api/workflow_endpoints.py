"""
Workflow API Endpoints

FastAPI endpoints for workflow management and execution.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel

from workflows.workflow_engine import get_workflow_engine
from workflows.templates.meeting_scheduling import create_meeting_scheduling_workflow
from workflows.templates.entity_setup import create_entity_setup_workflow
from workflows.templates.contact_update import create_contact_update_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    trigger_data: Dict
    user_id: str
    org_id: Optional[str] = None


class ExecuteWorkflowResponse(BaseModel):
    success: bool
    execution_id: str
    workflow_id: str
    results: List[Dict]
    final_state: Optional[Dict] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


class WorkflowInfo(BaseModel):
    id: str
    name: str
    description: str
    steps: int
    success_rate: float


class WorkflowStatistics(BaseModel):
    workflow_id: str
    name: str
    total_executions: int
    success_count: int
    failure_count: int
    success_rate: float
    average_duration_seconds: float


class ExecutionInfo(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    started_at: str
    completed_at: Optional[str]
    duration_seconds: Optional[float]
    error: Optional[str]
    rollback_performed: bool


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/execute", response_model=ExecuteWorkflowResponse)
async def execute_workflow(request: ExecuteWorkflowRequest):
    """
    Execute a workflow
    
    Example:
        POST /workflows/execute
        {
            "workflow_id": "meeting_scheduling",
            "trigger_data": {
                "email": {
                    "from": "john@example.com",
                    "subject": "Meeting next week?",
                    "body": "Can we meet Tuesday or Thursday?"
                }
            },
            "user_id": "user_123"
        }
    """
    
    engine = get_workflow_engine()
    
    result = await engine.execute_workflow(
        workflow_id=request.workflow_id,
        trigger_data=request.trigger_data,
        user_id=request.user_id,
        org_id=request.org_id
    )
    
    return ExecuteWorkflowResponse(**result)


@router.get("/list", response_model=List[WorkflowInfo])
async def list_workflows():
    """
    List all available workflows
    
    Returns:
        [
            {
                "id": "meeting_scheduling",
                "name": "Schedule Meeting from Email",
                "description": "...",
                "steps": 7,
                "success_rate": 0.95
            }
        ]
    """
    
    engine = get_workflow_engine()
    workflows = engine.list_workflows()
    
    return [WorkflowInfo(**w) for w in workflows]


@router.get("/{workflow_id}/statistics", response_model=WorkflowStatistics)
async def get_workflow_statistics(workflow_id: str):
    """
    Get statistics for a specific workflow
    
    Example:
        GET /workflows/meeting_scheduling/statistics
    """
    
    engine = get_workflow_engine()
    stats = engine.get_workflow_statistics(workflow_id)
    
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    
    return WorkflowStatistics(**stats)


@router.get("/executions", response_model=List[ExecutionInfo])
async def get_recent_executions(
    workflow_id: Optional[str] = None,
    limit: int = 10
):
    """
    Get recent workflow executions
    
    Example:
        GET /workflows/executions?workflow_id=meeting_scheduling&limit=10
    """
    
    engine = get_workflow_engine()
    executions = engine.get_recent_executions(workflow_id, limit)
    
    return [ExecutionInfo(**e) for e in executions]


@router.post("/initialize")
async def initialize_workflows():
    """
    Initialize all workflow templates
    
    This should be called on startup to register all workflows.
    """
    
    engine = get_workflow_engine()
    
    # Register workflow templates
    workflows = [
        create_meeting_scheduling_workflow(),
        create_entity_setup_workflow(),
        create_contact_update_workflow()
    ]
    
    for workflow in workflows:
        engine.register_workflow(workflow)
    
    return {
        "success": True,
        "workflows_registered": len(workflows),
        "workflows": [w.name for w in workflows]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    engine = get_workflow_engine()
    
    return {
        "status": "healthy",
        "workflows_registered": len(engine.workflows),
        "agents_registered": len(engine.agents),
        "total_executions": sum(w.total_executions for w in engine.workflows.values())
    }


# ============================================================================
# STARTUP
# ============================================================================

async def startup_workflows():
    """Initialize workflows on startup"""
    await initialize_workflows()
