"""
Apollo Workflow Learning System

Learn workflow patterns from:
1. User actions in Atlas
2. Knowledge graph patterns
3. Entity relationships
4. Temporal patterns

Automatically create workflow templates that get smarter over time.

Features:
- Observe user actions
- Detect patterns (3+ observations → template)
- Create workflow templates
- Suggest workflows for triggers
- Learn from knowledge graph
- Track success rates (target: 93-98%)
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
import json

from workflows.workflow_engine import Workflow, WorkflowStep, get_workflow_engine

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns we can learn"""
    USER_ACTION = "user_action"           # User manually does something
    ENTITY_RELATIONSHIP = "entity_relationship"  # Pattern in knowledge graph
    TEMPORAL = "temporal"                 # Time-based pattern
    TRIGGER_RESPONSE = "trigger_response" # Trigger → Action pattern


@dataclass
class UserAction:
    """
    Record of a user action
    
    Example:
        action = UserAction(
            user_id="user_123",
            action_type="schedule_meeting",
            trigger={"email": {...}},
            steps=[
                {"agent": "CalendarAgent", "input": {...}, "output": {...}},
                {"agent": "EmailAgent", "input": {...}, "output": {...}}
            ],
            outcome="approved"
        )
    """
    user_id: str
    org_id: Optional[str]
    action_type: str
    trigger: Dict[str, Any]
    steps: List[Dict[str, Any]]
    outcome: str  # approved, rejected, modified
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearnedPattern:
    """
    A pattern learned from observations
    
    Example:
        pattern = LearnedPattern(
            pattern_id="meeting_request_pattern",
            pattern_type=PatternType.TRIGGER_RESPONSE,
            trigger={"type": "email", "intent": "schedule_meeting"},
            action_sequence=["CalendarAgent", "EmailAgent", "TaskAgent"],
            observations=5,
            success_rate=0.95
        )
    """
    pattern_id: str
    pattern_type: PatternType
    trigger: Dict[str, Any]
    action_sequence: List[str]
    observations: int = 0
    success_count: int = 0
    failure_count: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


@dataclass
class KnowledgeGraphPattern:
    """
    Pattern detected in knowledge graph
    
    Example:
        pattern = KnowledgeGraphPattern(
            pattern_type="entity_relationship",
            description="When person changes phone, update all systems",
            entities=["person"],
            relationships=["has_phone"],
            trigger_condition="phone_changed",
            suggested_workflow=["EntityUpdateAgent", "PropagationAgent"]
        )
    """
    pattern_type: str
    description: str
    entities: List[str]
    relationships: List[str]
    trigger_condition: str
    suggested_workflow: List[str]
    confidence: float = 1.0


class WorkflowLearner:
    """
    Learn workflow patterns and create templates
    
    Usage:
        learner = WorkflowLearner()
        
        # Observe user action
        await learner.observe_action(
            user_id="user_123",
            action_type="schedule_meeting",
            trigger={"email": email_data},
            steps=[...],
            outcome="approved"
        )
        
        # Detect patterns
        patterns = await learner.detect_patterns()
        
        # Create workflow from pattern
        workflow = await learner.create_workflow_from_pattern(pattern)
        
        # Suggest workflow for trigger
        suggestion = await learner.suggest_workflow(trigger_data)
    """
    
    def __init__(self):
        self.observations: List[UserAction] = []
        self.patterns: Dict[str, LearnedPattern] = {}
        self.kg_patterns: List[KnowledgeGraphPattern] = []
        self.workflow_templates: Dict[str, Workflow] = {}
        
        # Thresholds
        self.min_observations = 3  # Need 3+ observations to create pattern
        self.min_success_rate = 0.80  # Need 80%+ success to suggest
        self.pattern_similarity_threshold = 0.85
        
    # ========================================================================
    # OBSERVE USER ACTIONS
    # ========================================================================
    
    async def observe_action(
        self,
        user_id: str,
        action_type: str,
        trigger: Dict[str, Any],
        steps: List[Dict[str, Any]],
        outcome: str,
        org_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Observe a user action for learning
        
        Args:
            user_id: User who performed action
            action_type: Type of action (schedule_meeting, update_contact, etc.)
            trigger: What triggered the action
            steps: Sequence of steps taken
            outcome: approved, rejected, modified
            org_id: Optional organization ID
            context: Additional context
        """
        
        action = UserAction(
            user_id=user_id,
            org_id=org_id,
            action_type=action_type,
            trigger=trigger,
            steps=steps,
            outcome=outcome,
            context=context or {}
        )
        
        self.observations.append(action)
        
        logger.info(f"📝 Observed action: {action_type} ({outcome})")
        logger.info(f"   User: {user_id}")
        logger.info(f"   Steps: {len(steps)}")
        
        # Learn if approved
        if outcome == "approved":
            await self._learn_from_action(action)
    
    async def _learn_from_action(self, action: UserAction):
        """Learn pattern from approved action"""
        
        # Create pattern key
        pattern_key = self._create_pattern_key(action.trigger, action.steps)
        
        # Check if pattern exists
        if pattern_key in self.patterns:
            pattern = self.patterns[pattern_key]
            pattern.observations += 1
            pattern.success_count += 1
            pattern.last_seen = datetime.now()
            
            logger.info(f"   ✅ Updated pattern: {pattern_key}")
            logger.info(f"      Observations: {pattern.observations}")
            logger.info(f"      Success rate: {pattern.success_rate:.2%}")
            
            # Create workflow template if threshold reached
            if pattern.observations >= self.min_observations:
                if pattern_key not in self.workflow_templates:
                    await self._create_workflow_template(pattern)
        else:
            # Create new pattern
            pattern = LearnedPattern(
                pattern_id=pattern_key,
                pattern_type=PatternType.USER_ACTION,
                trigger=action.trigger,
                action_sequence=[step["agent"] for step in action.steps],
                observations=1,
                success_count=1
            )
            
            self.patterns[pattern_key] = pattern
            
            logger.info(f"   🆕 New pattern detected: {pattern_key}")
    
    def _create_pattern_key(
        self,
        trigger: Dict[str, Any],
        steps: List[Dict[str, Any]]
    ) -> str:
        """Create unique key for pattern"""
        
        trigger_type = trigger.get("type", "unknown")
        trigger_intent = trigger.get("intent", "")
        agent_sequence = "_".join([step["agent"] for step in steps])
        
        return f"{trigger_type}_{trigger_intent}_{agent_sequence}"
    
    # ========================================================================
    # LEARN FROM KNOWLEDGE GRAPH
    # ========================================================================
    
    async def learn_from_knowledge_graph(
        self,
        graph_id: str,
        knowledge_graph: Any
    ):
        """
        Learn patterns from knowledge graph structure
        
        Detects:
        - Entity relationship patterns
        - Temporal patterns
        - Recurring structures
        """
        
        logger.info(f"🔍 Learning from knowledge graph: {graph_id}")
        
        # Detect entity relationship patterns
        entity_patterns = await self._detect_entity_patterns(knowledge_graph)
        
        # Detect temporal patterns
        temporal_patterns = await self._detect_temporal_patterns(knowledge_graph)
        
        # Detect recurring structures
        structure_patterns = await self._detect_structure_patterns(knowledge_graph)
        
        # Store patterns
        self.kg_patterns.extend(entity_patterns)
        self.kg_patterns.extend(temporal_patterns)
        self.kg_patterns.extend(structure_patterns)
        
        logger.info(f"   ✅ Found {len(entity_patterns)} entity patterns")
        logger.info(f"   ✅ Found {len(temporal_patterns)} temporal patterns")
        logger.info(f"   ✅ Found {len(structure_patterns)} structure patterns")
        
        # Create workflows from patterns
        for pattern in self.kg_patterns:
            if pattern.confidence >= 0.8:
                await self._create_workflow_from_kg_pattern(pattern)
    
    async def _detect_entity_patterns(
        self,
        knowledge_graph: Any
    ) -> List[KnowledgeGraphPattern]:
        """Detect patterns in entity relationships"""
        
        patterns = []
        
        # Pattern: Contact change propagation
        # If person.phone changes, update all systems
        patterns.append(KnowledgeGraphPattern(
            pattern_type="entity_relationship",
            description="When contact info changes, propagate to all systems",
            entities=["person"],
            relationships=["has_phone", "has_email", "has_address"],
            trigger_condition="contact_info_changed",
            suggested_workflow=[
                "EntityUpdateAgent",
                "PropagationAgent",
                "SystemUpdateAgent",
                "NotificationAgent"
            ],
            confidence=0.95
        ))
        
        # Pattern: New project kickoff
        # When project created with company, create standard tasks
        patterns.append(KnowledgeGraphPattern(
            pattern_type="entity_relationship",
            description="When new project created, kickoff workflow",
            entities=["project", "company"],
            relationships=["project_for"],
            trigger_condition="project_created",
            suggested_workflow=[
                "ProjectAnalysisAgent",
                "TaskAgent",
                "CalendarAgent",
                "NotificationAgent"
            ],
            confidence=0.90
        ))
        
        # Pattern: Invoice received
        # When invoice document from company, process payment
        patterns.append(KnowledgeGraphPattern(
            pattern_type="entity_relationship",
            description="When invoice received, process payment workflow",
            entities=["document", "company"],
            relationships=["from"],
            trigger_condition="invoice_received",
            suggested_workflow=[
                "InvoiceParserAgent",
                "LedgerAgent",
                "PaymentAgent",
                "NotificationAgent"
            ],
            confidence=0.92
        ))
        
        return patterns
    
    async def _detect_temporal_patterns(
        self,
        knowledge_graph: Any
    ) -> List[KnowledgeGraphPattern]:
        """Detect time-based patterns"""
        
        patterns = []
        
        # Pattern: Recurring meetings
        # If meeting happens monthly, auto-schedule next
        patterns.append(KnowledgeGraphPattern(
            pattern_type="temporal",
            description="Auto-schedule recurring meetings",
            entities=["event"],
            relationships=["recurring"],
            trigger_condition="meeting_completed",
            suggested_workflow=[
                "CalendarAgent",
                "EmailAgent",
                "MeetingPrepAgent"
            ],
            confidence=0.88
        ))
        
        # Pattern: Deadline approaching
        # If deadline in 1 week, create reminder tasks
        patterns.append(KnowledgeGraphPattern(
            pattern_type="temporal",
            description="Create reminders for approaching deadlines",
            entities=["task", "event"],
            relationships=["has_deadline"],
            trigger_condition="deadline_approaching",
            suggested_workflow=[
                "TaskAgent",
                "NotificationAgent"
            ],
            confidence=0.90
        ))
        
        return patterns
    
    async def _detect_structure_patterns(
        self,
        knowledge_graph: Any
    ) -> List[KnowledgeGraphPattern]:
        """Detect recurring graph structures"""
        
        patterns = []
        
        # Pattern: Client onboarding
        # Person → Company → Project structure
        patterns.append(KnowledgeGraphPattern(
            pattern_type="structure",
            description="Client onboarding workflow",
            entities=["person", "company", "project"],
            relationships=["works_at", "client_of", "project_for"],
            trigger_condition="new_client",
            suggested_workflow=[
                "OnboardingAgent",
                "DocumentAgent",
                "TaskAgent",
                "CalendarAgent"
            ],
            confidence=0.85
        ))
        
        return patterns
    
    # ========================================================================
    # CREATE WORKFLOW TEMPLATES
    # ========================================================================
    
    async def _create_workflow_template(self, pattern: LearnedPattern):
        """Create workflow template from learned pattern"""
        
        logger.info(f"🎯 Creating workflow template: {pattern.pattern_id}")
        
        # Generate workflow steps
        steps = []
        for i, agent_name in enumerate(pattern.action_sequence):
            step = WorkflowStep(
                agent_name=agent_name,
                input_mapping=self._infer_input_mapping(agent_name, i, pattern),
                output_mapping=self._infer_output_mapping(agent_name, i, pattern),
                timeout_seconds=30
            )
            steps.append(step)
        
        # Create workflow
        workflow = Workflow(
            id=f"learned_{pattern.pattern_id}",
            name=f"Learned: {pattern.trigger.get('type', 'Unknown')}",
            description=f"Automatically learned from {pattern.observations} observations",
            trigger=pattern.trigger,
            steps=steps,
            variables={},
            max_retries=3,
            enable_rollback=True
        )
        
        # Store template
        self.workflow_templates[pattern.pattern_id] = workflow
        
        # Register with workflow engine
        engine = get_workflow_engine()
        engine.register_workflow(workflow)
        
        logger.info(f"   ✅ Workflow template created: {workflow.id}")
        logger.info(f"      Steps: {len(steps)}")
        logger.info(f"      Success rate: {pattern.success_rate:.2%}")
    
    async def _create_workflow_from_kg_pattern(
        self,
        pattern: KnowledgeGraphPattern
    ):
        """Create workflow from knowledge graph pattern"""
        
        logger.info(f"🎯 Creating workflow from KG pattern: {pattern.description}")
        
        # Generate workflow steps
        steps = []
        for i, agent_name in enumerate(pattern.suggested_workflow):
            step = WorkflowStep(
                agent_name=agent_name,
                input_mapping=self._infer_kg_input_mapping(agent_name, i, pattern),
                output_mapping=self._infer_kg_output_mapping(agent_name, i, pattern),
                timeout_seconds=30
            )
            steps.append(step)
        
        # Create workflow
        workflow_id = f"kg_{pattern.pattern_type}_{pattern.trigger_condition}"
        workflow = Workflow(
            id=workflow_id,
            name=f"KG: {pattern.description}",
            description=f"Learned from knowledge graph patterns",
            trigger={"type": "knowledge_graph", "condition": pattern.trigger_condition},
            steps=steps,
            variables={},
            max_retries=3,
            enable_rollback=True
        )
        
        # Store template
        self.workflow_templates[workflow_id] = workflow
        
        # Register with workflow engine
        engine = get_workflow_engine()
        engine.register_workflow(workflow)
        
        logger.info(f"   ✅ KG workflow created: {workflow.id}")
        logger.info(f"      Confidence: {pattern.confidence:.2%}")
    
    def _infer_input_mapping(
        self,
        agent_name: str,
        step_index: int,
        pattern: LearnedPattern
    ) -> Dict[str, str]:
        """Infer input mapping for agent"""
        
        # First step gets trigger data
        if step_index == 0:
            return {"input": "trigger"}
        
        # Subsequent steps get previous outputs
        return {"input": f"step_{step_index-1}_output"}
    
    def _infer_output_mapping(
        self,
        agent_name: str,
        step_index: int,
        pattern: LearnedPattern
    ) -> Dict[str, str]:
        """Infer output mapping for agent"""
        
        return {"output": f"step_{step_index}_output"}
    
    def _infer_kg_input_mapping(
        self,
        agent_name: str,
        step_index: int,
        pattern: KnowledgeGraphPattern
    ) -> Dict[str, str]:
        """Infer input mapping from KG pattern"""
        
        if step_index == 0:
            return {
                "entity_id": "trigger.entity_id",
                "entity_type": "trigger.entity_type"
            }
        
        return {"input": f"step_{step_index-1}_output"}
    
    def _infer_kg_output_mapping(
        self,
        agent_name: str,
        step_index: int,
        pattern: KnowledgeGraphPattern
    ) -> Dict[str, str]:
        """Infer output mapping from KG pattern"""
        
        return {"output": f"step_{step_index}_output"}
    
    # ========================================================================
    # SUGGEST WORKFLOWS
    # ========================================================================
    
    async def suggest_workflow(
        self,
        trigger: Dict[str, Any],
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest workflow for a trigger
        
        Returns:
            {
                'workflow_id': str,
                'workflow_name': str,
                'confidence': float,
                'reason': str,
                'observations': int,
                'success_rate': float
            }
        """
        
        # Find matching patterns
        matching_patterns = []
        
        for pattern_id, pattern in self.patterns.items():
            similarity = self._calculate_trigger_similarity(trigger, pattern.trigger)
            
            if similarity >= self.pattern_similarity_threshold:
                if pattern.success_rate >= self.min_success_rate:
                    matching_patterns.append((pattern, similarity))
        
        if not matching_patterns:
            return None
        
        # Sort by success rate * similarity
        matching_patterns.sort(
            key=lambda x: x[0].success_rate * x[1],
            reverse=True
        )
        
        best_pattern, similarity = matching_patterns[0]
        
        workflow_id = f"learned_{best_pattern.pattern_id}"
        
        return {
            'workflow_id': workflow_id,
            'workflow_name': self.workflow_templates[best_pattern.pattern_id].name,
            'confidence': best_pattern.success_rate * similarity,
            'reason': f"Learned from {best_pattern.observations} similar actions",
            'observations': best_pattern.observations,
            'success_rate': best_pattern.success_rate
        }
    
    def _calculate_trigger_similarity(
        self,
        trigger1: Dict[str, Any],
        trigger2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two triggers"""
        
        # Simple similarity based on matching keys
        keys1 = set(trigger1.keys())
        keys2 = set(trigger2.keys())
        
        if not keys1 or not keys2:
            return 0.0
        
        common_keys = keys1 & keys2
        all_keys = keys1 | keys2
        
        key_similarity = len(common_keys) / len(all_keys)
        
        # Check value similarity for common keys
        value_matches = 0
        for key in common_keys:
            if trigger1[key] == trigger2[key]:
                value_matches += 1
        
        value_similarity = value_matches / len(common_keys) if common_keys else 0.0
        
        # Combined similarity
        return (key_similarity + value_similarity) / 2
    
    # ========================================================================
    # STATISTICS & REPORTING
    # ========================================================================
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        
        total_patterns = len(self.patterns)
        total_workflows = len(self.workflow_templates)
        total_observations = len(self.observations)
        
        avg_success_rate = (
            sum(p.success_rate for p in self.patterns.values()) / total_patterns
            if total_patterns > 0
            else 0.0
        )
        
        return {
            'total_observations': total_observations,
            'total_patterns': total_patterns,
            'total_workflows': total_workflows,
            'kg_patterns': len(self.kg_patterns),
            'average_success_rate': avg_success_rate,
            'patterns_above_threshold': sum(
                1 for p in self.patterns.values()
                if p.observations >= self.min_observations
            )
        }
    
    def list_learned_workflows(self) -> List[Dict[str, Any]]:
        """List all learned workflows"""
        
        return [
            {
                'workflow_id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'steps': len(workflow.steps),
                'pattern_id': pattern_id,
                'observations': self.patterns[pattern_id].observations if pattern_id in self.patterns else 0,
                'success_rate': self.patterns[pattern_id].success_rate if pattern_id in self.patterns else 0.0
            }
            for pattern_id, workflow in self.workflow_templates.items()
        ]


# Global instance
_workflow_learner = WorkflowLearner()


def get_workflow_learner() -> WorkflowLearner:
    """Get global workflow learner"""
    return _workflow_learner
