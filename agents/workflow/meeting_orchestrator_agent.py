"""
Meeting Orchestrator Agent

Intelligent workflow agent that:
1. Reads knowledge graph for context
2. Discovers workflow patterns
3. Executes multi-step workflows
4. Coordinates with other agents

Example: Meeting request from investor
- Parse email (EmailAgent)
- Query knowledge graph (find investor info, past meetings, projects)
- Check calendar (CalendarAgent)
- Find optimal time
- Research investor background (ResearchAgent)
- Create meeting prep doc (DocumentAgent)
- Send confirmation email (EmailAgent)
- Add to Atlas UI with all context
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from knowledge_graph import get_knowledge_graph, WorkflowPattern
from agents.communication.email_agent import EmailAgent
from agents.communication.calendar_agent import CalendarAgent
from agents.documents.document_agent import DocumentAgent
from agents.research.research_agent import ResearchAgent

logger = logging.getLogger(__name__)


@dataclass
class MeetingRequest:
    """Parsed meeting request"""
    from_email: str
    from_name: str
    subject: str
    body: str
    requested_topic: str
    urgency: str  # low, medium, high
    investor_interest: bool
    parsed_at: datetime


@dataclass
class MeetingWorkflow:
    """Complete meeting workflow execution plan"""
    request: MeetingRequest
    context: Dict[str, Any]  # From knowledge graph
    steps: List[str]
    optimal_time: Optional[datetime]
    prep_doc_path: Optional[str]
    confirmation_sent: bool
    atlas_task_id: Optional[str]


class MeetingOrchestratorAgent:
    """
    Intelligent Meeting Orchestrator
    
    Uses knowledge graph to:
    - Understand who is requesting the meeting
    - Find past interactions and context
    - Determine importance and priority
    - Execute appropriate workflow
    - Coordinate multiple agents
    
    Usage:
        agent = MeetingOrchestratorAgent()
        result = await agent.handle_meeting_request(email_data)
    """
    
    def __init__(self):
        self.kg = None  # Will be initialized async
        self.email_agent = EmailAgent()
        self.calendar_agent = CalendarAgent()
        self.document_agent = DocumentAgent()
        self.research_agent = ResearchAgent()
    
    async def initialize(self):
        """Initialize async components"""
        self.kg = await get_knowledge_graph()
        logger.info("✅ MeetingOrchestratorAgent initialized")
    
    async def handle_meeting_request(
        self,
        email_data: Dict[str, Any]
    ) -> MeetingWorkflow:
        """
        Main entry point - handle complete meeting request workflow
        
        Args:
            email_data: Raw email data from Kafka
            
        Returns:
            MeetingWorkflow with complete execution results
        """
        logger.info(f"📧 Handling meeting request from {email_data.get('from')}")
        
        # Step 1: Parse email to extract meeting request
        meeting_request = await self._parse_meeting_request(email_data)
        
        # Step 2: Query knowledge graph for context
        context = await self._get_context_from_knowledge_graph(meeting_request)
        
        # Step 3: Discover or create workflow pattern
        workflow_pattern = await self._discover_workflow(meeting_request, context)
        
        # Step 4: Execute workflow steps
        workflow = await self._execute_workflow(
            meeting_request,
            context,
            workflow_pattern
        )
        
        # Step 5: Learn from execution
        await self._learn_from_execution(workflow_pattern, workflow)
        
        return workflow
    
    async def _parse_meeting_request(
        self,
        email_data: Dict[str, Any]
    ) -> MeetingRequest:
        """Parse email to extract meeting request details"""
        # Use EmailAgent to parse
        parsed = await self.email_agent.parse(email_data)
        
        # Extract meeting-specific info
        return MeetingRequest(
            from_email=email_data.get("from", ""),
            from_name=parsed.get("sender_name", ""),
            subject=email_data.get("subject", ""),
            body=email_data.get("body", ""),
            requested_topic=parsed.get("topic", ""),
            urgency=parsed.get("urgency", "medium"),
            investor_interest=self._detect_investor_interest(parsed),
            parsed_at=datetime.now()
        )
    
    def _detect_investor_interest(self, parsed_email: Dict[str, Any]) -> bool:
        """Detect if email is from potential investor"""
        keywords = ["invest", "funding", "capital", "partnership", "opportunity"]
        body_lower = parsed_email.get("body", "").lower()
        return any(keyword in body_lower for keyword in keywords)
    
    async def _get_context_from_knowledge_graph(
        self,
        request: MeetingRequest
    ) -> Dict[str, Any]:
        """
        Query knowledge graph for all relevant context
        
        Queries:
        1. Find person in graph (business + personal)
        2. Find past interactions
        3. Find related projects
        4. Find investor profile (if applicable)
        5. Find common connections
        """
        context = {
            "person": None,
            "past_meetings": [],
            "related_projects": [],
            "investor_profile": None,
            "common_connections": [],
            "importance_score": 0.5
        }
        
        # Find person in business graph
        person = await self.kg.find_entity(request.from_name, graph="business")
        if person:
            context["person"] = person
            
            # Get full context around this person
            person_context = await self.kg.find_entity_context(
                request.from_name,
                max_depth=3,
                graph="business"
            )
            
            # Extract related entities
            for entity in person_context.get("related_entities", []):
                if entity.type == "meeting":
                    context["past_meetings"].append(entity)
                elif entity.type == "project":
                    context["related_projects"].append(entity)
                elif entity.type == "investor_profile":
                    context["investor_profile"] = entity
            
            # Calculate importance score
            context["importance_score"] = self._calculate_importance(
                person,
                context["past_meetings"],
                context["investor_profile"]
            )
        
        logger.info(f"📊 Context: {len(context['past_meetings'])} past meetings, "
                   f"importance: {context['importance_score']:.2f}")
        
        return context
    
    def _calculate_importance(
        self,
        person: Any,
        past_meetings: List[Any],
        investor_profile: Any
    ) -> float:
        """Calculate importance score (0-1)"""
        score = 0.5  # Base score
        
        # Boost for investor
        if investor_profile:
            score += 0.3
        
        # Boost for past meetings (relationship strength)
        if len(past_meetings) > 0:
            score += min(0.2, len(past_meetings) * 0.05)
        
        # Boost for person properties
        if person and person.properties.get("vip"):
            score += 0.2
        
        return min(1.0, score)
    
    async def _discover_workflow(
        self,
        request: MeetingRequest,
        context: Dict[str, Any]
    ) -> WorkflowPattern:
        """
        Discover appropriate workflow pattern from knowledge graph
        
        Looks for patterns like:
        - "meeting request from investor"
        - "high priority meeting request"
        - "meeting request with past relationship"
        """
        # Build trigger description
        trigger_parts = ["meeting request"]
        
        if request.investor_interest:
            trigger_parts.append("investor")
        
        if request.urgency == "high":
            trigger_parts.append("high priority")
        
        if len(context.get("past_meetings", [])) > 0:
            trigger_parts.append("existing relationship")
        
        trigger = " ".join(trigger_parts)
        
        # Try to find existing workflow
        workflow = await self.kg.discover_workflow(trigger)
        
        if workflow:
            logger.info(f"✅ Found workflow: {workflow.name} "
                       f"(success rate: {workflow.success_rate:.2%})")
            return workflow
        
        # Create new workflow if none found
        logger.info(f"🆕 Creating new workflow for: {trigger}")
        steps = self._generate_workflow_steps(request, context)
        
        workflow_id = await self.kg.create_workflow_pattern(
            name=f"Meeting Request: {trigger}",
            trigger=trigger,
            steps=steps,
            initial_success_rate=0.7
        )
        
        return WorkflowPattern(
            id=workflow_id,
            name=f"Meeting Request: {trigger}",
            trigger=trigger,
            steps=steps,
            success_rate=0.7,
            usage_count=0
        )
    
    def _generate_workflow_steps(
        self,
        request: MeetingRequest,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate workflow steps based on context"""
        steps = [
            "parse_meeting_request",
            "query_knowledge_graph",
            "check_calendar_availability"
        ]
        
        # Add research step for investors or new contacts
        if request.investor_interest or not context.get("person"):
            steps.append("research_background")
        
        # Add prep doc for important meetings
        if context.get("importance_score", 0) > 0.7:
            steps.append("create_meeting_prep_doc")
        
        steps.extend([
            "propose_meeting_time",
            "send_confirmation_email",
            "create_atlas_task",
            "add_to_calendar"
        ])
        
        return steps
    
    async def _execute_workflow(
        self,
        request: MeetingRequest,
        context: Dict[str, Any],
        workflow_pattern: WorkflowPattern
    ) -> MeetingWorkflow:
        """Execute all workflow steps"""
        logger.info(f"🚀 Executing workflow: {workflow_pattern.name}")
        logger.info(f"📋 Steps: {', '.join(workflow_pattern.steps)}")
        
        workflow = MeetingWorkflow(
            request=request,
            context=context,
            steps=workflow_pattern.steps,
            optimal_time=None,
            prep_doc_path=None,
            confirmation_sent=False,
            atlas_task_id=None
        )
        
        for step in workflow_pattern.steps:
            logger.info(f"  ▶️  {step}")
            
            if step == "check_calendar_availability":
                workflow.optimal_time = await self._find_optimal_time(request, context)
            
            elif step == "research_background":
                research = await self._research_background(request, context)
                context["research"] = research
            
            elif step == "create_meeting_prep_doc":
                workflow.prep_doc_path = await self._create_prep_doc(request, context)
            
            elif step == "send_confirmation_email":
                workflow.confirmation_sent = await self._send_confirmation(
                    request,
                    workflow.optimal_time,
                    workflow.prep_doc_path
                )
            
            elif step == "create_atlas_task":
                workflow.atlas_task_id = await self._create_atlas_task(
                    request,
                    context,
                    workflow
                )
        
        logger.info(f"✅ Workflow complete!")
        return workflow
    
    async def _find_optimal_time(
        self,
        request: MeetingRequest,
        context: Dict[str, Any]
    ) -> datetime:
        """Find optimal meeting time using CalendarAgent"""
        # Get available slots for next 2 weeks
        start = datetime.now()
        end = start + timedelta(days=14)
        
        available_slots = await self.calendar_agent.find_available_slots(
            start_date=start,
            end_date=end,
            duration_minutes=60
        )
        
        # Prefer afternoon slots for investor meetings
        if request.investor_interest:
            afternoon_slots = [
                slot for slot in available_slots
                if 14 <= slot.hour <= 16
            ]
            if afternoon_slots:
                return afternoon_slots[0]
        
        # Return first available
        return available_slots[0] if available_slots else start + timedelta(days=1)
    
    async def _research_background(
        self,
        request: MeetingRequest,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Research person's background using ResearchAgent"""
        return await self.research_agent.research_person(
            name=request.from_name,
            email=request.from_email,
            context=context
        )
    
    async def _create_prep_doc(
        self,
        request: MeetingRequest,
        context: Dict[str, Any]
    ) -> str:
        """Create meeting preparation document"""
        doc_content = f"""
# Meeting Preparation: {request.from_name}

## Meeting Details
- **Topic:** {request.requested_topic}
- **Requested by:** {request.from_name} ({request.from_email})
- **Urgency:** {request.urgency}
- **Investor Interest:** {'Yes' if request.investor_interest else 'No'}

## Context
- **Past Meetings:** {len(context.get('past_meetings', []))}
- **Related Projects:** {', '.join([p.name for p in context.get('related_projects', [])])}
- **Importance Score:** {context.get('importance_score', 0):.2f}

## Background Research
{context.get('research', {}).get('summary', 'No research available')}

## Talking Points
{self._generate_talking_points(request, context)}

## Action Items
- [ ] Review past meeting notes
- [ ] Prepare project updates
- [ ] Gather relevant documents
"""
        
        doc_path = await self.document_agent.create_document(
            title=f"Meeting Prep: {request.from_name}",
            content=doc_content,
            doc_type="meeting_prep"
        )
        
        logger.info(f"📄 Created prep doc: {doc_path}")
        return doc_path
    
    def _generate_talking_points(
        self,
        request: MeetingRequest,
        context: Dict[str, Any]
    ) -> str:
        """Generate talking points based on context"""
        points = []
        
        if request.investor_interest:
            points.append("- Discuss investment opportunity and terms")
            points.append("- Share company vision and roadmap")
            points.append("- Review financial projections")
        
        if context.get("related_projects"):
            points.append(f"- Update on {context['related_projects'][0].name}")
        
        if context.get("past_meetings"):
            points.append("- Follow up on previous discussion points")
        
        return "\n".join(points) if points else "- Discuss meeting topic"
    
    async def _send_confirmation(
        self,
        request: MeetingRequest,
        meeting_time: datetime,
        prep_doc_path: Optional[str]
    ) -> bool:
        """Send meeting confirmation email"""
        email_body = f"""
Hi {request.from_name},

Thank you for reaching out regarding {request.requested_topic}.

I'd be happy to meet. How about {meeting_time.strftime('%A, %B %d at %I:%M %p')}?

I've prepared some materials for our discussion and look forward to speaking with you.

Best regards
"""
        
        sent = await self.email_agent.send_email(
            to=request.from_email,
            subject=f"Re: {request.subject}",
            body=email_body
        )
        
        logger.info(f"📧 Confirmation email {'sent' if sent else 'failed'}")
        return sent
    
    async def _create_atlas_task(
        self,
        request: MeetingRequest,
        context: Dict[str, Any],
        workflow: MeetingWorkflow
    ) -> str:
        """Create task in Atlas UI with all context"""
        # This would call Atlas API to create a task
        # For now, return a mock task ID
        task_id = f"task-{datetime.now().timestamp()}"
        
        logger.info(f"✅ Created Atlas task: {task_id}")
        return task_id
    
    async def _learn_from_execution(
        self,
        workflow_pattern: WorkflowPattern,
        workflow: MeetingWorkflow
    ):
        """Update knowledge graph with execution results"""
        # Determine success
        success = (
            workflow.optimal_time is not None and
            workflow.confirmation_sent and
            workflow.atlas_task_id is not None
        )
        
        # Update workflow pattern success rate
        await self.kg.learn_workflow_success(workflow_pattern.id, success)
        
        logger.info(f"📊 Workflow learning: {'success' if success else 'failure'}")
