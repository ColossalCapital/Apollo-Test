# 🏗️ Apollo Agent Architecture - 5 Layers

## 🎯 Overview

Apollo uses a **5-layer agent architecture** where each layer builds on the previous one, creating a force multiplier effect:

```
Layer 1 (10x) → Layer 2 (100x) → Layer 3 (1,000x) → Layer 4 (10,000x) → Layer 5 (100,000x)
```

Each layer has specific responsibilities and standard interfaces.

---

## 📚 Layer Definitions

### **Layer 1: Data Extraction (Primitive)**

**Purpose:** Convert unstructured → structured data

**Base Class:** `Layer1Agent`

**Characteristics:**
- ✅ No decision-making
- ✅ Pure extraction/transformation
- ✅ Fast (< 1 second)
- ✅ Stateless

**Examples:**
- EmailParser
- DocumentParser
- ImageParser
- AudioParser
- VideoParser
- WebScraper
- CSVParser

**Interface:**
```python
from agents.base import Layer1Agent, AgentResult

class EmailParserAgent(Layer1Agent):
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="email_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Parse emails into structured data",
            capabilities=["email", "mime", "attachments"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Any) -> AgentResult:
        # Parse email
        email = parse_email(raw_data)
        
        return AgentResult(
            success=True,
            data={
                "from": email.sender,
                "subject": email.subject,
                "body": email.body,
                "attachments": email.attachments
            },
            confidence=1.0,
            metadata={"format": "email"}
        )
```

---

### **Layer 2: Entity Recognition (Basic Intelligence)**

**Purpose:** Identify entities and relationships from structured data

**Base Class:** `Layer2Agent`

**Characteristics:**
- ✅ Uses NLP/ML models
- ✅ Identifies patterns
- ✅ Creates graph nodes
- ✅ Light decision-making (classification)

**Examples:**
- PersonRecognition
- CompanyRecognition
- LocationRecognition
- DateTimeRecognition
- MoneyRecognition
- TopicRecognition
- SentimentAgent
- IntentAgent

**Interface:**
```python
from agents.base import Layer2Agent, AgentResult, Entity, Relationship

class PersonRecognitionAgent(Layer2Agent):
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="person_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="Recognize people and their attributes",
            capabilities=["person", "contact", "role"],
            dependencies=[]
        )
    
    async def recognize(self, structured_data: Dict[str, Any]) -> AgentResult:
        # Use NLP to extract people
        people = extract_people(structured_data["text"])
        
        entities = []
        for person in people:
            entities.append(Entity(
                id=generate_id(),
                name=person.name,
                type="person",
                properties={"email": person.email, "role": person.role},
                confidence=0.9,
                source="email_parser",
                graph="business"
            ))
        
        return AgentResult(
            success=True,
            data={"entities": entities},
            confidence=0.9,
            metadata={"model": "spacy"}
        )
```

---

### **Layer 3: Domain Experts (Specialists)**

**Purpose:** Deep domain knowledge and analysis

**Base Class:** `Layer3Agent`

**Characteristics:**
- ✅ Domain-specific expertise
- ✅ Complex analysis
- ✅ Uses knowledge graph for context
- ✅ Can call Layer 1 & 2 agents

**Examples:**
- FinancialAnalyst
- LegalAgent
- CodeReviewAgent
- ResearchAgent
- MarketingAgent
- HRAgent

**Interface:**
```python
from agents.base import Layer3Agent, AgentResult, Entity

class FinancialAnalystAgent(Layer3Agent):
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="financial_analyst",
            layer=AgentLayer.LAYER_3_DOMAIN,
            version="1.0.0",
            description="Analyze financial data and provide insights",
            capabilities=["financial_analysis", "valuation", "forecasting"],
            dependencies=[]
        )
    
    async def analyze(
        self,
        entities: List[Entity],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        # Get context from knowledge graph
        company = entities[0]
        kg_context = await self.get_context_from_kg(company)
        
        # Perform analysis
        analysis = {
            "valuation": calculate_valuation(company, kg_context),
            "recommendation": "BUY",
            "confidence": 0.85
        }
        
        return AgentResult(
            success=True,
            data=analysis,
            confidence=0.85,
            metadata={"method": "DCF"}
        )
```

---

### **Layer 4: Workflow Orchestration (Coordinators)**

**Purpose:** Multi-step workflows coordinating multiple agents

**Base Class:** `Layer4Agent`

**Characteristics:**
- ✅ Query knowledge graph for context
- ✅ Discover workflow patterns
- ✅ Coordinate Layer 1-3 agents
- ✅ Complex decisions
- ✅ Learn from execution

**Examples:**
- MeetingOrchestrator
- EmailCampaign
- CustomerSupport
- InvestorRelations
- ProjectManager
- HiringAgent

**Interface:**
```python
from agents.base import Layer4Agent, Trigger, WorkflowResult

class MeetingOrchestratorAgent(Layer4Agent):
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="meeting_orchestrator",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="Handle meeting requests end-to-end",
            capabilities=["meeting", "calendar", "email", "prep_doc"],
            dependencies=["email_parser", "calendar", "research", "document"]
        )
    
    async def orchestrate(self, trigger: Trigger) -> WorkflowResult:
        workflow_id = generate_workflow_id()
        steps_completed = []
        
        # Step 1: Parse email
        email_data = await self.execute_step("email_parser", trigger.data)
        steps_completed.append("parse_email")
        
        # Step 2: Check calendar
        availability = await self.execute_step("calendar", email_data)
        steps_completed.append("check_calendar")
        
        # Step 3: Research attendees
        research = await self.execute_step("research", email_data)
        steps_completed.append("research_attendees")
        
        # Step 4: Send confirmation
        confirmation = await self.execute_step("email", {
            "to": email_data["from"],
            "subject": "Meeting confirmed",
            "body": f"Meeting scheduled for {availability['time']}"
        })
        steps_completed.append("send_confirmation")
        
        # Learn from execution
        await self.learn_from_execution(workflow_id, success=True)
        
        return WorkflowResult(
            workflow_id=workflow_id,
            success=True,
            steps_completed=steps_completed,
            outputs={"meeting_time": availability['time']},
            execution_time_ms=1500
        )
```

---

### **Layer 5: Meta-Orchestration (Strategic)**

**Purpose:** High-level strategy, learning, optimization

**Base Class:** `Layer5Agent`

**Characteristics:**
- ✅ Analyze all agent performance
- ✅ Optimize workflows
- ✅ Create new workflow patterns
- ✅ Strategic decision-making
- ✅ Cross-domain coordination

**Examples:**
- MetaOrchestrator
- WorkflowOptimizer
- AgentPerformance
- Strategy
- Learning
- ResourceAllocation

**Interface:**
```python
from agents.base import Layer5Agent, SystemState, Optimization

class WorkflowOptimizerAgent(Layer5Agent):
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="workflow_optimizer",
            layer=AgentLayer.LAYER_5_META,
            version="1.0.0",
            description="Optimize workflows across the system",
            capabilities=["optimization", "performance_analysis"],
            dependencies=[]
        )
    
    async def optimize(self, system_state: SystemState) -> Optimization:
        # Analyze agent performance
        performance = await self.analyze_agent_performance()
        
        # Find bottlenecks
        bottlenecks = find_bottlenecks(performance)
        
        # Generate optimization
        return Optimization(
            type="workflow_optimization",
            description="Reduce meeting workflow time by 30%",
            impact=0.3,
            actions=[
                "Parallelize research and calendar check",
                "Cache frequent attendee info",
                "Pre-generate email templates"
            ],
            priority=8
        )
```

---

## 🏭 Using the Agent Factory

### **Basic Usage:**

```python
from agents import get_factory, get_registry
from knowledge_graph import get_knowledge_graph

# Get knowledge graph client
kg = await get_knowledge_graph()

# Create factory
factory = get_factory(kg_client=kg)

# Create agents
email_parser = factory.create("email_parser")
person_recognition = factory.create("person_recognition")
financial_analyst = factory.create("financial_analyst")
meeting_orchestrator = factory.create("meeting_orchestrator")

# Or use layer-specific methods
email_parser = factory.create_layer1_agent("email_parser")
workflow = factory.create_layer4_agent("meeting_orchestrator")
```

### **Creating Workflows with Dependencies:**

```python
# Create workflow with all dependencies resolved
workflow = factory.create_workflow("meeting_orchestrator")

# All dependencies are automatically registered:
# - email_parser
# - calendar
# - research
# - document

# Execute workflow
trigger = Trigger(
    id="trigger-001",
    type="meeting_request",
    data={"email": raw_email},
    timestamp=datetime.now()
)

result = await workflow.orchestrate(trigger)
print(f"Completed steps: {result.steps_completed}")
```

### **Creating Agent Chains:**

```python
# Create a chain of agents
chain = factory.create_agent_chain([
    "email_parser",      # Layer 1
    "person_recognition", # Layer 2
    "financial_analyst"   # Layer 3
])

# Execute chain
raw_email = get_email()
parsed = await chain[0].extract(raw_email)
entities = await chain[1].recognize(parsed.data)
analysis = await chain[2].analyze(entities.data["entities"])
```

---

## 📋 Agent Registry

### **Viewing Registered Agents:**

```python
from agents import get_registry

registry = get_registry()

# Print all agents
registry.print_registry()

# Get stats
stats = registry.get_stats()
print(f"Total agents: {stats['total_agents']}")
print(f"Layer 4 agents: {stats['layer_4_agents']}")

# List agents by layer
layer4_agents = registry.list_agents_by_layer(AgentLayer.LAYER_4_WORKFLOW)
for entry in layer4_agents:
    print(f"{entry.name}: {entry.description}")

# Find agents by capability
meeting_agents = registry.find_agents_by_capability("meeting")
```

### **Registering New Agents:**

```python
from agents import get_registry, AgentLayer

registry = get_registry()

# Register a new agent
registry.register(
    name="my_custom_agent",
    layer=AgentLayer.LAYER_3_DOMAIN,
    agent_class=MyCustomAgent,
    description="My custom domain expert",
    capabilities=["custom_analysis"],
    dependencies=["email_parser"],
    enabled=True
)
```

---

## 🎯 Best Practices

### **1. Layer Separation:**
- ✅ Keep layers separate
- ✅ Don't skip layers
- ✅ Use `validate_agent_chain()` to verify chains

### **2. Dependency Injection:**
- ✅ Use factory for agent creation
- ✅ Inject knowledge graph client for Layer 3-5
- ✅ Register dependencies for Layer 4 agents

### **3. Error Handling:**
- ✅ Return `AgentResult` with success=False on errors
- ✅ Include error messages in `errors` list
- ✅ Set appropriate confidence levels

### **4. Learning:**
- ✅ Layer 4 agents should call `learn_from_execution()`
- ✅ Track success rates in knowledge graph
- ✅ Update workflow patterns based on results

### **5. Performance:**
- ✅ Cache agent instances (factory does this by default)
- ✅ Use async/await for all agent methods
- ✅ Parallelize independent steps in workflows

---

## 📊 Migration Guide

### **Migrating Legacy Agents:**

**Old way (BaseAgent):**
```python
from agents import BaseAgent

class MyAgent(BaseAgent):
    async def process(self, data):
        # Process data
        return result
```

**New way (Layer-specific):**
```python
from agents.base import Layer3Agent, AgentResult

class MyAgent(Layer3Agent):
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="my_agent",
            layer=AgentLayer.LAYER_3_DOMAIN,
            version="1.0.0",
            description="My domain expert agent",
            capabilities=["analysis"],
            dependencies=[]
        )
    
    async def analyze(self, entities, context=None) -> AgentResult:
        # Analyze entities
        return AgentResult(
            success=True,
            data=result,
            confidence=0.9,
            metadata={}
        )
```

---

## 🚀 Summary

**5-Layer Architecture Benefits:**
- ✅ Clear separation of concerns
- ✅ Standard interfaces
- ✅ Easy to test
- ✅ Dependency injection
- ✅ Force multiplier effect
- ✅ Scalable and maintainable

**Files:**
- `agents/base.py` - Base classes for all 5 layers
- `agents/registry.py` - Central agent registry
- `agents/factory.py` - Agent factory with DI
- `agents/__init__.py` - Exports and backwards compatibility

**Ready for local iteration!** 🎉
