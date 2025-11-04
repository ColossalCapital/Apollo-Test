"""
Learning System API Endpoints

FastAPI endpoints for workflow learning and suggestions.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel

from learning.workflow_learner import get_workflow_learner

router = APIRouter(prefix="/learning", tags=["learning"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ObserveActionRequest(BaseModel):
    user_id: str
    action_type: str
    trigger: Dict
    steps: List[Dict]
    outcome: str  # approved, rejected, modified
    org_id: Optional[str] = None
    context: Optional[Dict] = None


class ObserveActionResponse(BaseModel):
    success: bool
    message: str
    pattern_detected: bool
    pattern_id: Optional[str] = None
    observations: Optional[int] = None


class SuggestWorkflowRequest(BaseModel):
    trigger: Dict
    user_id: str


class SuggestWorkflowResponse(BaseModel):
    has_suggestion: bool
    workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    observations: Optional[int] = None
    success_rate: Optional[float] = None


class LearnFromGraphRequest(BaseModel):
    graph_id: str
    user_id: str


class LearningStatistics(BaseModel):
    total_observations: int
    total_patterns: int
    total_workflows: int
    kg_patterns: int
    average_success_rate: float
    patterns_above_threshold: int


class LearnedWorkflow(BaseModel):
    workflow_id: str
    name: str
    description: str
    steps: int
    pattern_id: str
    observations: int
    success_rate: float


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/observe", response_model=ObserveActionResponse)
async def observe_action(request: ObserveActionRequest):
    """
    Observe a user action for learning
    
    Example:
        POST /learning/observe
        {
            "user_id": "user_123",
            "action_type": "schedule_meeting",
            "trigger": {
                "type": "email",
                "intent": "schedule_meeting",
                "email": {...}
            },
            "steps": [
                {"agent": "CalendarAgent", "input": {...}, "output": {...}},
                {"agent": "EmailAgent", "input": {...}, "output": {...}}
            ],
            "outcome": "approved"
        }
    """
    
    learner = get_workflow_learner()
    
    await learner.observe_action(
        user_id=request.user_id,
        action_type=request.action_type,
        trigger=request.trigger,
        steps=request.steps,
        outcome=request.outcome,
        org_id=request.org_id,
        context=request.context
    )
    
    # Check if pattern was detected
    pattern_key = learner._create_pattern_key(request.trigger, request.steps)
    pattern = learner.patterns.get(pattern_key)
    
    if pattern:
        return ObserveActionResponse(
            success=True,
            message="Action observed and pattern updated",
            pattern_detected=True,
            pattern_id=pattern.pattern_id,
            observations=pattern.observations
        )
    
    return ObserveActionResponse(
        success=True,
        message="Action observed",
        pattern_detected=False
    )


@router.post("/suggest", response_model=SuggestWorkflowResponse)
async def suggest_workflow(request: SuggestWorkflowRequest):
    """
    Suggest a workflow for a trigger
    
    Example:
        POST /learning/suggest
        {
            "trigger": {
                "type": "email",
                "intent": "schedule_meeting"
            },
            "user_id": "user_123"
        }
        
    Response:
        {
            "has_suggestion": true,
            "workflow_id": "learned_email_schedule_meeting_...",
            "workflow_name": "Learned: Email Meeting Request",
            "confidence": 0.92,
            "reason": "Learned from 5 similar actions",
            "observations": 5,
            "success_rate": 0.95
        }
    """
    
    learner = get_workflow_learner()
    
    suggestion = await learner.suggest_workflow(
        trigger=request.trigger,
        user_id=request.user_id
    )
    
    if suggestion:
        return SuggestWorkflowResponse(
            has_suggestion=True,
            **suggestion
        )
    
    return SuggestWorkflowResponse(
        has_suggestion=False
    )


@router.post("/learn-from-graph")
async def learn_from_knowledge_graph(request: LearnFromGraphRequest):
    """
    Learn patterns from knowledge graph
    
    Example:
        POST /learning/learn-from-graph
        {
            "graph_id": "business",
            "user_id": "user_123"
        }
    """
    
    learner = get_workflow_learner()
    
    # TODO: Get knowledge graph from Atlas
    # For now, use mock
    knowledge_graph = None
    
    await learner.learn_from_knowledge_graph(
        graph_id=request.graph_id,
        knowledge_graph=knowledge_graph
    )
    
    return {
        "success": True,
        "message": f"Learned patterns from graph: {request.graph_id}",
        "kg_patterns": len(learner.kg_patterns)
    }


@router.get("/statistics", response_model=LearningStatistics)
async def get_learning_statistics():
    """
    Get learning system statistics
    
    Example:
        GET /learning/statistics
    """
    
    learner = get_workflow_learner()
    stats = learner.get_learning_statistics()
    
    return LearningStatistics(**stats)


@router.get("/workflows", response_model=List[LearnedWorkflow])
async def list_learned_workflows():
    """
    List all learned workflows
    
    Example:
        GET /learning/workflows
    """
    
    learner = get_workflow_learner()
    workflows = learner.list_learned_workflows()
    
    return [LearnedWorkflow(**w) for w in workflows]


@router.get("/patterns")
async def list_patterns():
    """
    List all detected patterns
    
    Example:
        GET /learning/patterns
    """
    
    learner = get_workflow_learner()
    
    patterns = [
        {
            'pattern_id': p.pattern_id,
            'pattern_type': p.pattern_type.value,
            'trigger': p.trigger,
            'action_sequence': p.action_sequence,
            'observations': p.observations,
            'success_rate': p.success_rate,
            'first_seen': p.first_seen.isoformat(),
            'last_seen': p.last_seen.isoformat()
        }
        for p in learner.patterns.values()
    ]
    
    return {
        'total_patterns': len(patterns),
        'patterns': patterns
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    learner = get_workflow_learner()
    stats = learner.get_learning_statistics()
    
    return {
        "status": "healthy",
        "observations": stats['total_observations'],
        "patterns": stats['total_patterns'],
        "workflows": stats['total_workflows']
    }
