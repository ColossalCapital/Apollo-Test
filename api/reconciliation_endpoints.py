"""
AI-Guided Reconciliation API Endpoints

Provides intelligent reconciliation between current codebase state and project plans.
Uses Apollo AI to guide users through complex decisions with natural language.

Example Use Case:
- Multiple deployment implementations (Docker Compose, Juju, Podman)
- AI asks clarifying questions about path forward
- User responds in natural language
- AI generates appropriate Linear/Jira tickets
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
import logging
from datetime import datetime

from services.dynamic_model_selector import get_model_selector, TaskType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reconciliation", tags=["reconciliation"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ReconciliationContext(BaseModel):
    """Context for reconciliation session"""
    codebase_path: str
    entity_id: str
    session_id: Optional[str] = None
    current_state: Optional[Dict[str, Any]] = None
    project_plans: Optional[Dict[str, Any]] = None
    conflicts: Optional[List[Dict[str, Any]]] = None


class ReconciliationMessage(BaseModel):
    """Message in reconciliation chat"""
    session_id: str
    message: str
    entity_id: str
    context: Optional[Dict[str, Any]] = None


class ReconciliationResponse(BaseModel):
    """AI response in reconciliation"""
    session_id: str
    message: str
    suggestions: Optional[List[Dict[str, Any]]] = None
    questions: Optional[List[str]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    confidence: float
    needs_clarification: bool


class ReconciliationDecision(BaseModel):
    """User decision from reconciliation"""
    session_id: str
    decision_type: Literal["keep", "remove", "merge", "custom"]
    target: str  # File path, implementation, etc.
    reasoning: str
    create_tickets: bool = True


class TicketGeneration(BaseModel):
    """Generated tickets from reconciliation"""
    session_id: str
    tickets: List[Dict[str, Any]]
    implementation_plan: str


# ============================================================================
# In-Memory Session Storage (TODO: Move to Redis/PostgreSQL)
# ============================================================================

reconciliation_sessions: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Reconciliation Endpoints
# ============================================================================

@router.post("/start", response_model=ReconciliationResponse)
async def start_reconciliation(context: ReconciliationContext):
    """
    Start AI-guided reconciliation session
    
    Analyzes current state vs project plans and identifies conflicts
    """
    
    try:
        # Generate session ID
        session_id = f"recon_{context.entity_id}_{datetime.now().timestamp()}"
        
        # Store session context
        reconciliation_sessions[session_id] = {
            "context": context.dict(),
            "messages": [],
            "decisions": [],
            "started_at": datetime.now().isoformat()
        }
        
        # Analyze conflicts using AI
        selector = get_model_selector()
        
        # Build analysis prompt
        prompt = f"""You are Apollo, an AI assistant helping reconcile codebase state with project plans.

**Current Situation:**
Codebase: {context.codebase_path}

**Detected Issues:**
{_format_conflicts(context.conflicts) if context.conflicts else 'Analyzing...'}

**Your Task:**
1. Identify the main conflicts or inconsistencies
2. Ask clarifying questions about the path forward
3. Help the user make informed decisions
4. Generate appropriate implementation tickets

Start by asking what the user wants to prioritize or clarify."""

        # Get AI response (mock for now - will use Theta GPU)
        ai_message = await _get_ai_guidance(prompt, session_id)
        
        # Store AI message
        reconciliation_sessions[session_id]["messages"].append({
            "role": "assistant",
            "content": ai_message,
            "timestamp": datetime.now().isoformat()
        })
        
        return ReconciliationResponse(
            session_id=session_id,
            message=ai_message,
            questions=[
                "What is the target deployment environment? (local dev, staging, production)",
                "Which implementation should be the primary path forward?",
                "Should we deprecate old implementations or keep them for compatibility?"
            ],
            confidence=0.8,
            needs_clarification=True
        )
    
    except Exception as e:
        logger.error(f"Failed to start reconciliation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ReconciliationResponse)
async def reconciliation_chat(message: ReconciliationMessage):
    """
    Chat with AI during reconciliation
    
    User provides clarifications, AI guides decisions
    """
    
    try:
        # Get session
        session = reconciliation_sessions.get(message.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store user message
        session["messages"].append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build conversation context
        conversation = _build_conversation_context(session)
        
        # Get AI response
        prompt = f"""Continue the reconciliation conversation.

**Conversation History:**
{conversation}

**User's Latest Message:**
{message.message}

**Your Task:**
1. Acknowledge the user's input
2. Provide specific recommendations based on their clarification
3. Ask follow-up questions if needed
4. Suggest concrete actions (tickets to create, files to remove, etc.)

Be specific and actionable."""

        ai_message = await _get_ai_guidance(prompt, message.session_id)
        
        # Store AI message
        session["messages"].append({
            "role": "assistant",
            "content": ai_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract suggestions and actions from AI response
        suggestions = _extract_suggestions(ai_message)
        actions = _extract_actions(ai_message)
        
        return ReconciliationResponse(
            session_id=message.session_id,
            message=ai_message,
            suggestions=suggestions,
            actions=actions,
            confidence=0.85,
            needs_clarification=len(actions) == 0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reconciliation chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decide", response_model=Dict[str, Any])
async def make_decision(decision: ReconciliationDecision):
    """
    User makes a decision during reconciliation
    
    Records the decision and updates session state
    """
    
    try:
        # Get session
        session = reconciliation_sessions.get(decision.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store decision
        session["decisions"].append({
            "decision_type": decision.decision_type,
            "target": decision.target,
            "reasoning": decision.reasoning,
            "create_tickets": decision.create_tickets,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate confirmation message
        confirmation = f"""✅ Decision recorded:
- Action: {decision.decision_type.upper()}
- Target: {decision.target}
- Reasoning: {decision.reasoning}
{'- Will create implementation tickets' if decision.create_tickets else ''}

What would you like to decide next?"""
        
        session["messages"].append({
            "role": "assistant",
            "content": confirmation,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "recorded",
            "session_id": decision.session_id,
            "decisions_count": len(session["decisions"]),
            "message": confirmation
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Decision recording error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-tickets", response_model=TicketGeneration)
async def generate_tickets(session_id: str):
    """
    Generate Linear/Jira tickets from reconciliation decisions
    
    Creates implementation plan and tickets based on all decisions made
    """
    
    try:
        # Get session
        session = reconciliation_sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Build implementation plan from decisions
        decisions = session.get("decisions", [])
        
        if not decisions:
            raise HTTPException(status_code=400, detail="No decisions made yet")
        
        # Generate tickets using AI
        prompt = f"""Generate implementation tickets based on these reconciliation decisions:

**Decisions Made:**
{_format_decisions(decisions)}

**Context:**
{session['context']}

**Your Task:**
Create a structured implementation plan with:
1. Epic/milestone for the overall reconciliation
2. Individual tickets for each decision
3. Dependencies between tickets
4. Estimated effort
5. Priority

Format as Linear/Jira tickets."""

        ai_response = await _get_ai_guidance(prompt, session_id)
        
        # Parse tickets from AI response
        tickets = _parse_tickets_from_response(ai_response, decisions)
        
        # Store tickets in session
        session["tickets"] = tickets
        session["completed_at"] = datetime.now().isoformat()
        
        return TicketGeneration(
            session_id=session_id,
            tickets=tickets,
            implementation_plan=ai_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ticket generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get reconciliation session details"""
    
    session = reconciliation_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End reconciliation session"""
    
    if session_id in reconciliation_sessions:
        del reconciliation_sessions[session_id]
        return {"status": "ended", "session_id": session_id}
    
    raise HTTPException(status_code=404, detail="Session not found")


# ============================================================================
# Helper Functions
# ============================================================================

def _format_conflicts(conflicts: List[Dict[str, Any]]) -> str:
    """Format conflicts for AI prompt"""
    if not conflicts:
        return "No conflicts detected"
    
    formatted = []
    for conflict in conflicts:
        formatted.append(f"- {conflict.get('type', 'Unknown')}: {conflict.get('description', '')}")
    
    return "\n".join(formatted)


def _build_conversation_context(session: Dict[str, Any]) -> str:
    """Build conversation context from session messages"""
    messages = session.get("messages", [])
    
    formatted = []
    for msg in messages[-10:]:  # Last 10 messages
        role = "User" if msg["role"] == "user" else "Apollo"
        formatted.append(f"{role}: {msg['content']}")
    
    return "\n\n".join(formatted)


def _format_decisions(decisions: List[Dict[str, Any]]) -> str:
    """Format decisions for AI prompt"""
    formatted = []
    for i, decision in enumerate(decisions, 1):
        formatted.append(f"{i}. {decision['decision_type'].upper()}: {decision['target']}")
        formatted.append(f"   Reasoning: {decision['reasoning']}")
    
    return "\n".join(formatted)


async def _get_ai_guidance(prompt: str, session_id: str) -> str:
    """
    Get AI guidance using Theta GPU
    
    TODO: Implement actual Theta GPU API call
    For now, returns intelligent mock responses
    """
    
    # Mock response for now - will use Theta GPU
    if "start by asking" in prompt.lower():
        return """I've analyzed your codebase and found multiple deployment implementations:

**Current Implementations:**
1. **Docker Compose** - Used for local development
2. **Juju Charms** - Planned for production deployment
3. **Podman** - Legacy implementation (appears unused)

**Questions to clarify the path forward:**

1. **Primary Deployment Target:** What environment are you optimizing for?
   - Local development only?
   - Production deployment?
   - Both with different configs?

2. **Podman Status:** The Podman files appear unused. Should we:
   - Archive them for reference?
   - Remove them completely?
   - Keep them for specific use cases?

3. **Docker Compose vs Juju:** How do you want to handle the transition?
   - Keep Docker Compose for local dev, Juju for production?
   - Gradually migrate everything to Juju?
   - Maintain both long-term?

Let me know your priorities and I'll help create a clear implementation plan!"""
    
    elif "docker" in prompt.lower() and "local" in prompt.lower():
        return """Great! So the path forward is:

**Primary Strategy:** Docker Compose for local dev, Juju for production

**Recommended Actions:**

1. **Archive Podman** (Low Priority)
   - Move Podman files to `/archive/podman/`
   - Document why they were deprecated
   - Keep for reference but remove from active codebase

2. **Standardize Docker Compose** (High Priority)
   - Create `docker-compose.dev.yml` for local development
   - Ensure it works on resource-constrained machines
   - Document which services can run locally vs need remote

3. **Prepare Juju Migration** (Medium Priority)
   - Create Juju charms in parallel
   - Test in staging environment
   - Document deployment process

4. **Update Documentation** (High Priority)
   - Clear README for local setup (Docker Compose)
   - Separate docs for production deployment (Juju)
   - Migration guide for team members

**Should I create Linear/Jira tickets for these actions?**"""
    
    else:
        return """Based on your input, here's what I recommend:

**Next Steps:**
1. Review the suggested actions
2. Make any adjustments needed
3. I'll generate implementation tickets

Would you like me to proceed with ticket generation, or do you want to clarify anything else?"""


def _extract_suggestions(ai_message: str) -> List[Dict[str, Any]]:
    """Extract actionable suggestions from AI message"""
    # Simple extraction - in production, use NLP
    suggestions = []
    
    if "archive" in ai_message.lower():
        suggestions.append({
            "action": "archive",
            "target": "Podman files",
            "priority": "low"
        })
    
    if "standardize" in ai_message.lower():
        suggestions.append({
            "action": "standardize",
            "target": "Docker Compose",
            "priority": "high"
        })
    
    return suggestions


def _extract_actions(ai_message: str) -> List[Dict[str, Any]]:
    """Extract concrete actions from AI message"""
    actions = []
    
    # Simple extraction - in production, use NLP
    if "create" in ai_message.lower() and "ticket" in ai_message.lower():
        actions.append({
            "type": "create_tickets",
            "description": "Generate implementation tickets"
        })
    
    return actions


def _parse_tickets_from_response(ai_response: str, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse tickets from AI response"""
    # In production, use NLP to extract structured tickets
    # For now, create tickets based on decisions
    
    tickets = []
    
    for i, decision in enumerate(decisions, 1):
        ticket = {
            "title": f"{decision['decision_type'].title()}: {decision['target']}",
            "description": decision['reasoning'],
            "type": "task",
            "priority": "medium",
            "labels": ["reconciliation", "infrastructure"],
            "estimate": 3  # story points
        }
        tickets.append(ticket)
    
    return tickets


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def reconciliation_health():
    """Check reconciliation service health"""
    return {
        "status": "healthy",
        "active_sessions": len(reconciliation_sessions),
        "features": [
            "AI-guided reconciliation",
            "Natural language clarification",
            "Automatic ticket generation",
            "Context-aware suggestions"
        ]
    }
