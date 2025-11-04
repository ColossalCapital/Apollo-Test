"""
Meta-Orchestrator API Endpoints

FastAPI endpoints for visual workflow construction and execution.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel

from orchestrator.meta_orchestrator import (
    get_meta_orchestrator, NodeType, VisualWorkflow
)
from orchestrator.workflow_templates import load_all_templates

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CreateWorkflowRequest(BaseModel):
    name: str
    description: str = ""


class AddNodeRequest(BaseModel):
    workflow_id: str
    node_type: str  # NodeType enum value
    name: str
    agent_name: Optional[str] = None
    config: Optional[Dict] = None
    position: Optional[Dict] = None


class ConnectNodesRequest(BaseModel):
    workflow_id: str
    from_node_id: str
    to_node_id: str
    condition: Optional[str] = None
    label: Optional[str] = None


class ExecuteVisualWorkflowRequest(BaseModel):
    workflow_id: str
    trigger_data: Dict
    user_id: str


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    nodes: int
    connections: int
    version: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/workflows/create", response_model=WorkflowResponse)
async def create_workflow(request: CreateWorkflowRequest):
    """
    Create a new visual workflow
    
    Example:
        POST /orchestrator/workflows/create
        {
            "name": "My Custom Workflow",
            "description": "Custom workflow for my use case"
        }
    """
    
    orchestrator = get_meta_orchestrator()
    
    workflow = orchestrator.create_workflow(
        name=request.name,
        description=request.description
    )
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        nodes=len(workflow.nodes),
        connections=len(workflow.connections),
        version=workflow.version
    )


@router.post("/workflows/{workflow_id}/nodes")
async def add_node(workflow_id: str, request: AddNodeRequest):
    """
    Add a node to workflow
    
    Example:
        POST /orchestrator/workflows/{id}/nodes
        {
            "workflow_id": "workflow_123",
            "node_type": "agent",
            "name": "Parse Email",
            "agent_name": "EmailParserAgent",
            "config": {
                "input_mapping": {"email": "trigger.email"}
            },
            "position": {"x": 100, "y": 100}
        }
    """
    
    orchestrator = get_meta_orchestrator()
    
    workflow = orchestrator.workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        node_type = NodeType(request.node_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid node type: {request.node_type}")
    
    node = orchestrator.add_node(
        workflow,
        node_type,
        request.name,
        agent_name=request.agent_name,
        config=request.config,
        position=request.position
    )
    
    return {
        "success": True,
        "node_id": node.id,
        "node_name": node.name
    }


@router.post("/workflows/{workflow_id}/connections")
async def connect_nodes(workflow_id: str, request: ConnectNodesRequest):
    """
    Connect two nodes in workflow
    
    Example:
        POST /orchestrator/workflows/{id}/connections
        {
            "workflow_id": "workflow_123",
            "from_node_id": "node_0",
            "to_node_id": "node_1",
            "condition": "output.success == true",
            "label": "success"
        }
    """
    
    orchestrator = get_meta_orchestrator()
    
    workflow = orchestrator.workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Find nodes
    from_node = next((n for n in workflow.nodes if n.id == request.from_node_id), None)
    to_node = next((n for n in workflow.nodes if n.id == request.to_node_id), None)
    
    if not from_node or not to_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    orchestrator.connect(
        workflow,
        from_node,
        to_node,
        condition=request.condition,
        label=request.label
    )
    
    return {
        "success": True,
        "from": from_node.name,
        "to": to_node.name
    }


@router.post("/workflows/{workflow_id}/execute")
async def execute_visual_workflow(workflow_id: str, request: ExecuteVisualWorkflowRequest):
    """
    Execute a visual workflow
    
    Example:
        POST /orchestrator/workflows/{id}/execute
        {
            "workflow_id": "workflow_123",
            "trigger_data": {
                "email": {...}
            },
            "user_id": "user_123"
        }
    """
    
    orchestrator = get_meta_orchestrator()
    
    workflow = orchestrator.workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    result = await orchestrator.execute(
        workflow,
        request.trigger_data,
        request.user_id
    )
    
    return result


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows():
    """
    List all visual workflows
    
    Example:
        GET /orchestrator/workflows
    """
    
    orchestrator = get_meta_orchestrator()
    workflows = orchestrator.list_workflows()
    
    return [WorkflowResponse(**w) for w in workflows]


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """
    Get workflow details
    
    Example:
        GET /orchestrator/workflows/{id}
    """
    
    orchestrator = get_meta_orchestrator()
    
    workflow = orchestrator.workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "nodes": [
            {
                "id": n.id,
                "type": n.type.value,
                "name": n.name,
                "agent_name": n.agent_name,
                "config": n.config,
                "position": n.position,
                "status": n.status.value
            }
            for n in workflow.nodes
        ],
        "connections": [
            {
                "from_node": c.from_node,
                "to_node": c.to_node,
                "condition": c.condition,
                "label": c.label
            }
            for c in workflow.connections
        ],
        "version": workflow.version
    }


@router.get("/workflows/{workflow_id}/export")
async def export_workflow(workflow_id: str):
    """
    Export workflow as JSON
    
    Example:
        GET /orchestrator/workflows/{id}/export
    """
    
    orchestrator = get_meta_orchestrator()
    
    workflow = orchestrator.workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_json = orchestrator.save_workflow(workflow)
    
    return {
        "workflow_json": workflow_json
    }


@router.post("/workflows/import")
async def import_workflow(workflow_json: str):
    """
    Import workflow from JSON
    
    Example:
        POST /orchestrator/workflows/import
        {
            "workflow_json": "{...}"
        }
    """
    
    orchestrator = get_meta_orchestrator()
    
    try:
        workflow = orchestrator.load_workflow(workflow_json)
        
        return {
            "success": True,
            "workflow_id": workflow.id,
            "workflow_name": workflow.name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.get("/templates")
async def list_templates():
    """
    List available workflow templates
    
    Example:
        GET /orchestrator/templates
    """
    
    orchestrator = get_meta_orchestrator()
    templates = load_all_templates(orchestrator)
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "nodes": len(t.nodes),
            "connections": len(t.connections)
        }
        for t in templates
    ]


@router.get("/node-types")
async def list_node_types():
    """
    List available node types
    
    Example:
        GET /orchestrator/node-types
    """
    
    return {
        "node_types": [
            {
                "value": nt.value,
                "name": nt.name,
                "description": _get_node_type_description(nt)
            }
            for nt in NodeType
        ]
    }


def _get_node_type_description(node_type: NodeType) -> str:
    """Get description for node type"""
    descriptions = {
        NodeType.AGENT: "Execute an AI agent",
        NodeType.TRIGGER: "Workflow trigger point",
        NodeType.CONDITION: "Conditional branching",
        NodeType.LOOP: "Loop over items",
        NodeType.PARALLEL: "Parallel execution",
        NodeType.MERGE: "Merge parallel branches",
        NodeType.TRANSFORM: "Transform data",
        NodeType.DELAY: "Wait/delay execution",
        NodeType.WEBHOOK: "HTTP webhook",
        NodeType.ERROR_HANDLER: "Handle errors"
    }
    return descriptions.get(node_type, "")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    orchestrator = get_meta_orchestrator()
    
    return {
        "status": "healthy",
        "workflows": len(orchestrator.workflows),
        "agents": len(orchestrator.agents)
    }
