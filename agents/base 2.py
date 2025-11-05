"""
Apollo Agent Base Classes

Defines standard interfaces for all 5 layers of agents.
Each layer has specific responsibilities and contracts.

Layer 1: Data Extraction (Primitive)
Layer 2: Entity Recognition (Basic Intelligence)
Layer 3: Domain Experts (Specialists)
Layer 4: Workflow Orchestration (Coordinators)
Layer 5: Meta-Orchestration (Strategic)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# ============================================================================
# COMMON DATA STRUCTURES
# ============================================================================

class AgentLayer(Enum):
    """Agent layer classification"""
    LAYER_1_EXTRACTION = 1
    LAYER_2_RECOGNITION = 2
    LAYER_3_DOMAIN_EXPERT = 3
    LAYER_4_WORKFLOW = 4
    LAYER_5_META = 5
    CONNECTOR = 6


class EntityType(Enum):
    """Entity type for agent visibility"""
    PERSONAL = "personal"
    BUSINESS = "business"
    TRADING_FIRM = "trading_firm"
    UNIVERSAL = "universal"


class AppContext(Enum):
    """Application context for agent usage"""
    ATLAS = "atlas"
    DELT = "delt"
    AKASHIC = "akashic"
    ALL = "all"


class PrivacyLevel(Enum):
    """Privacy level for data handling"""
    PERSONAL = "personal"  # Only user can access
    PRIVATE = "private"  # User + explicit shares
    ORG_PRIVATE = "org_private"  # Organization members only
    ORG_PUBLIC = "org_public"  # Organization + public profile
    PUBLIC = "public"  # Fully public


class AgentCategory(Enum):
    """Agent category for organization"""
    COMMUNICATION = "communication"
    FINANCE = "finance"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    SOCIAL = "social"
    TRAVEL = "travel"
    SHOPPING = "shopping"
    MEDIA = "media"
    DEVELOPMENT = "development"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    SALES = "sales"
    HR = "hr"
    LEGAL = "legal"
    OPERATIONS = "operations"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    KNOWLEDGE = "knowledge"
    WORKFLOW = "workflow"
    META = "meta"


class ConfidenceLevel(Enum):
    """Confidence levels for agent outputs"""
    VERY_LOW = 0.0
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9
    CERTAIN = 1.0


@dataclass
class AgentMetadata:
    """Comprehensive metadata about an agent"""
    # Core Identity
    name: str
    layer: AgentLayer
    version: str
    description: str
    capabilities: List[str]
    dependencies: List[str] = None
    
    # Filtering & Visibility
    entity_types: List[EntityType] = None
    app_contexts: List[AppContext] = None
    requires_subscription: List[str] = None  # ["delt", "akashic"]
    
    # Authentication & Access
    byok_enabled: bool = False  # Bring Your Own Keys
    wtf_purchasable: bool = False  # Purchasable with WTF coin
    required_credentials: List[str] = None  # ["api_key", "secret_key"]
    wtf_price_monthly: Optional[int] = None  # WTF coins per month
    
    # Resource Usage
    estimated_tokens_per_call: Optional[int] = None  # LLM token usage
    estimated_cost_per_call: Optional[float] = None  # USD cost
    rate_limit: Optional[str] = None  # "100/hour", "1000/day"
    
    # Performance
    avg_response_time_ms: Optional[int] = None  # Average response time
    requires_gpu: bool = False  # Needs GPU for processing
    can_run_offline: bool = False  # Works without internet
    
    # Data & Privacy
    data_retention_days: Optional[int] = None  # How long data is kept
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE  # Default privacy
    pii_handling: bool = False  # Handles personally identifiable information
    gdpr_compliant: bool = True  # GDPR compliance
    
    # Integration Details
    api_version: Optional[str] = None  # "v2", "2024-01"
    webhook_support: bool = False  # Supports webhooks
    real_time_sync: bool = False  # Real-time vs batch sync
    sync_frequency: Optional[str] = None  # "hourly", "daily", "real-time"
    
    # Business Logic
    free_tier_limit: Optional[int] = None  # Free tier usage limit
    pro_tier_limit: Optional[int] = None  # Pro tier usage limit
    enterprise_only: bool = False  # Only for enterprise customers
    beta: bool = False  # Still in beta
    
    # Learning & Training
    supports_continuous_learning: bool = False  # Can train on user data
    training_cost_wtf: Optional[int] = None  # WTF cost to train model
    training_frequency: Optional[str] = None  # "after_100_interactions"
    model_storage_location: Optional[str] = None  # "filecoin", "theta"
    
    # UI/UX
    has_ui_component: bool = False  # Has dedicated UI in Atlas
    icon: Optional[str] = None  # Icon name or URL
    color: Optional[str] = None  # Brand color (#hex)
    category: Optional[AgentCategory] = None  # COMMUNICATION, FINANCE, etc.
    
    # Monitoring & Alerts
    health_check_endpoint: Optional[str] = None  # Health check URL
    alert_on_failure: bool = False  # Send alerts if agent fails
    fallback_agent: Optional[str] = None  # Fallback if this agent fails
    
    # Documentation
    documentation_url: Optional[str] = None  # Link to docs
    example_use_cases: List[str] = None  # Example scenarios
    setup_guide_url: Optional[str] = None  # Setup instructions


@dataclass
class AgentResult:
    """Standard result from any agent"""
    success: bool
    data: Any
    confidence: float
    metadata: Dict[str, Any]
    errors: List[str] = None
    warnings: List[str] = None
    execution_time_ms: float = 0.0


@dataclass
class Entity:
    """Entity extracted from data"""
    id: str
    name: str
    type: str  # person, company, project, etc.
    properties: Dict[str, Any]
    confidence: float
    source: str
    graph: str  # which knowledge graph


@dataclass
class Relationship:
    """Relationship between entities"""
    id: str
    from_entity_id: str
    to_entity_id: str
    type: str  # works_at, invested_in, etc.
    properties: Dict[str, Any]
    confidence: float
    source: str


@dataclass
class Trigger:
    """Trigger for workflow execution"""
    id: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 1-10, 10 = highest


@dataclass
class WorkflowResult:
    """Result from workflow execution"""
    workflow_id: str
    success: bool
    steps_completed: List[str]
    outputs: Dict[str, Any]
    errors: List[str] = None
    execution_time_ms: float = 0.0


@dataclass
class SystemState:
    """Current state of the system"""
    active_workflows: int
    agent_performance: Dict[str, float]
    resource_usage: Dict[str, float]
    error_rate: float
    timestamp: datetime


@dataclass
class Optimization:
    """System optimization recommendation"""
    type: str
    description: str
    impact: float  # 0-1
    actions: List[str]
    priority: int


# ============================================================================
# LAYER 1: DATA EXTRACTION AGENTS (Primitive)
# ============================================================================

class Layer1Agent(ABC):
    """
    Base class for Layer 1 Data Extraction Agents
    
    Purpose: Convert unstructured data → structured data
    Characteristics:
    - No decision-making
    - Pure extraction/transformation
    - Fast (< 1 second)
    - Stateless
    
    Examples: EmailParser, DocumentParser, ImageParser
    """
    
    def __init__(self):
        self.metadata = self._get_metadata()
    
    @abstractmethod
    def _get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass
    
    @abstractmethod
    async def extract(self, raw_data: Any) -> AgentResult:
        """
        Extract structured data from raw input
        
        Args:
            raw_data: Unstructured input (email, document, image, etc.)
            
        Returns:
            AgentResult with structured data
            
        Example:
            raw_email = {"from": "...", "body": "..."}
            result = await agent.extract(raw_email)
            # result.data = {"sender": "...", "subject": "...", "entities": [...]}
        """
        pass
    
    def validate_input(self, raw_data: Any) -> Tuple[bool, Optional[str]]:
        """Validate input data format"""
        return True, None
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported input formats"""
        return []


# ============================================================================
# LAYER 2: ENTITY RECOGNITION AGENTS (Basic Intelligence)
# ============================================================================

class Layer2Agent(ABC):
    """
    Base class for Layer 2 Entity Recognition Agents
    
    Purpose: Identify entities and relationships from structured data
    Characteristics:
    - Uses NLP/ML models
    - Identifies patterns
    - Creates graph nodes
    - Light decision-making (classification)
    
    Examples: PersonRecognition, CompanyRecognition, SentimentAgent
    """
    
    def __init__(self):
        self.metadata = self._get_metadata()
        self.model = None  # Will be loaded by subclass
    
    @abstractmethod
    def _get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass
    
    @abstractmethod
    async def recognize(self, structured_data: Dict[str, Any]) -> AgentResult:
        """
        Recognize entities and relationships from structured data
        
        Args:
            structured_data: Output from Layer 1 agent
            
        Returns:
            AgentResult with entities and relationships
            
        Example:
            data = {"text": "Jacob works at Company X"}
            result = await agent.recognize(data)
            # result.data = {
            #   "entities": [Entity(name="Jacob", type="person"), ...],
            #   "relationships": [Relationship(type="works_at"), ...]
            # }
        """
        pass
    
    async def load_model(self):
        """Load ML model (if needed)"""
        pass
    
    def get_entity_types(self) -> List[str]:
        """Return list of entity types this agent can recognize"""
        return []


# ============================================================================
# LAYER 3: DOMAIN EXPERT AGENTS (Specialists)
# ============================================================================

class Layer3Agent(ABC):
    """
    Base class for Layer 3 Domain Expert Agents
    
    Purpose: Deep domain knowledge and analysis
    Characteristics:
    - Domain-specific expertise
    - Complex analysis
    - Uses knowledge graph for context
    - Can call Layer 1 & 2 agents
    
    Examples: FinancialAnalyst, LegalAgent, CodeReviewAgent
    """
    
    def __init__(self, kg_client=None):
        self.metadata = self._get_metadata()
        self.kg = kg_client  # Knowledge graph client
        self.layer1_agents = {}
        self.layer2_agents = {}
    
    @abstractmethod
    def _get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass
    
    @abstractmethod
    async def analyze(
        self,
        entities: List[Entity],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Perform domain-specific analysis
        
        Args:
            entities: List of entities from Layer 2
            context: Optional context from knowledge graph
            
        Returns:
            AgentResult with domain-specific insights
            
        Example:
            entities = [Entity(type="company", name="ACME Inc")]
            result = await financial_agent.analyze(entities)
            # result.data = {
            #   "analysis": "Company is undervalued",
            #   "metrics": {...},
            #   "recommendations": [...]
            # }
        """
        pass
    
    async def get_context_from_kg(self, entity: Entity) -> Dict[str, Any]:
        """Get context from knowledge graph"""
        if not self.kg:
            return {}
        return await self.kg.find_entity_context(entity.name, max_depth=3)
    
    def register_layer1_agent(self, name: str, agent: Layer1Agent):
        """Register Layer 1 agent for use"""
        self.layer1_agents[name] = agent
    
    def register_layer2_agent(self, name: str, agent: Layer2Agent):
        """Register Layer 2 agent for use"""
        self.layer2_agents[name] = agent


# ============================================================================
# LAYER 4: WORKFLOW ORCHESTRATION AGENTS (Coordinators)
# ============================================================================

class Layer4Agent(ABC):
    """
    Base class for Layer 4 Workflow Orchestration Agents
    
    Purpose: Multi-step workflows coordinating multiple agents
    Characteristics:
    - Query knowledge graph for context
    - Discover workflow patterns
    - Coordinate Layer 1-3 agents
    - Complex decisions
    - Learn from execution
    
    Examples: MeetingOrchestrator, ProjectManager, SalesProcess
    """
    
    def __init__(self, kg_client=None):
        self.metadata = self._get_metadata()
        self.kg = kg_client
        self.agents = {}  # Registry of available agents
    
    @abstractmethod
    def _get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass
    
    @abstractmethod
    async def orchestrate(self, trigger: Trigger) -> WorkflowResult:
        """
        Execute multi-step workflow
        
        Args:
            trigger: Event that triggered the workflow
            
        Returns:
            WorkflowResult with execution details
            
        Example:
            trigger = Trigger(type="meeting_request", data={...})
            result = await orchestrator.orchestrate(trigger)
            # result.steps_completed = [
            #   "parse_email", "check_calendar", "send_confirmation"
            # ]
        """
        pass
    
    async def discover_workflow_pattern(self, trigger: Trigger) -> Optional[Any]:
        """Discover workflow pattern from knowledge graph"""
        if not self.kg:
            return None
        return await self.kg.discover_workflow(trigger.type)
    
    async def learn_from_execution(self, workflow_id: str, success: bool):
        """Update workflow pattern based on execution result"""
        if not self.kg:
            return
        await self.kg.learn_workflow_success(workflow_id, success)
    
    def register_agent(self, name: str, agent: Any):
        """Register agent for use in workflows"""
        self.agents[name] = agent
    
    async def execute_step(self, step_name: str, input_data: Any) -> Any:
        """Execute a single workflow step"""
        if step_name not in self.agents:
            raise ValueError(f"Agent '{step_name}' not registered")
        
        agent = self.agents[step_name]
        
        # Route to appropriate method based on agent layer
        if isinstance(agent, Layer1Agent):
            return await agent.extract(input_data)
        elif isinstance(agent, Layer2Agent):
            return await agent.recognize(input_data)
        elif isinstance(agent, Layer3Agent):
            return await agent.analyze(input_data)
        else:
            raise ValueError(f"Unknown agent type for '{step_name}'")


# ============================================================================
# LAYER 5: META-ORCHESTRATION AGENTS (Strategic)
# ============================================================================

class Layer5Agent(ABC):
    """
    Base class for Layer 5 Meta-Orchestration Agents
    
    Purpose: High-level strategy, learning, optimization
    Characteristics:
    - Analyze all agent performance
    - Optimize workflows
    - Create new workflow patterns
    - Strategic decision-making
    - Cross-domain coordination
    
    Examples: MetaOrchestrator, WorkflowOptimizer, LearningAgent
    """
    
    def __init__(self, kg_client=None):
        self.metadata = self._get_metadata()
        self.kg = kg_client
        self.system_metrics = {}
    
    @abstractmethod
    def _get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass
    
    @abstractmethod
    async def optimize(self, system_state: SystemState) -> Optimization:
        """
        Perform system-wide optimization
        
        Args:
            system_state: Current state of the system
            
        Returns:
            Optimization recommendations
            
        Example:
            state = SystemState(active_workflows=10, error_rate=0.05)
            result = await optimizer.optimize(state)
            # result.actions = [
            #   "Scale down workflow X",
            #   "Increase timeout for agent Y"
            # ]
        """
        pass
    
    async def analyze_agent_performance(self) -> Dict[str, float]:
        """Analyze performance of all agents"""
        # Query knowledge graph for agent metrics
        return {}
    
    async def create_workflow_pattern(
        self,
        name: str,
        trigger: str,
        steps: List[str]
    ) -> str:
        """Create new workflow pattern in knowledge graph"""
        if not self.kg:
            return ""
        return await self.kg.create_workflow_pattern(name, trigger, steps)
    
    async def optimize_workflow(self, workflow_id: str) -> List[str]:
        """Optimize existing workflow"""
        return []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_agent_layer(agent: Any) -> AgentLayer:
    """Get the layer of an agent"""
    if isinstance(agent, Layer1Agent):
        return AgentLayer.LAYER_1_EXTRACTION
    elif isinstance(agent, Layer2Agent):
        return AgentLayer.LAYER_2_RECOGNITION
    elif isinstance(agent, Layer3Agent):
        return AgentLayer.LAYER_3_DOMAIN
    elif isinstance(agent, Layer4Agent):
        return AgentLayer.LAYER_4_WORKFLOW
    elif isinstance(agent, Layer5Agent):
        return AgentLayer.LAYER_5_META
    else:
        raise ValueError(f"Unknown agent type: {type(agent)}")


def validate_agent_chain(agents: List[Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that agents can be chained together
    
    Rules:
    - Layer 1 → Layer 2 ✅
    - Layer 2 → Layer 3 ✅
    - Layer 3 → Layer 4 ✅
    - Layer 4 → Layer 5 ✅
    - Cannot skip layers ❌
    """
    if not agents:
        return False, "Empty agent chain"
    
    prev_layer = None
    for agent in agents:
        current_layer = get_agent_layer(agent)
        
        if prev_layer and current_layer.value != prev_layer.value + 1:
            return False, f"Cannot chain {prev_layer} → {current_layer}"
        
        prev_layer = current_layer
    
    return True, None
