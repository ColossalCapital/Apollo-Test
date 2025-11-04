# 🚀 Quick Start - Apollo Agent System

## ✅ What's Built

**Infrastructure (100% Complete):**
- ✅ Base classes for all 5 layers (`agents/base.py`)
- ✅ Central agent registry (`agents/registry.py`)
- ✅ Agent factory with DI (`agents/factory.py`)
- ✅ Backwards compatibility with legacy agents
- ✅ Comprehensive documentation

**You can now:**
- Create agents with standard interfaces
- Use factory for dependency injection
- Discover agents via registry
- Build agent chains
- Create workflows with auto-resolved dependencies

---

## 🎯 Quick Examples

### **1. Create a Simple Layer 1 Agent:**

```python
# agents/layer1/email_parser.py
from agents.base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer

class EmailParserAgent(Layer1Agent):
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="email_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Parse emails into structured data",
            capabilities=["email", "mime"],
            dependencies=[]
        )
    
    async def extract(self, raw_data):
        # Your parsing logic here
        return AgentResult(
            success=True,
            data={"from": "...", "subject": "..."},
            confidence=1.0,
            metadata={}
        )
```

### **2. Register Your Agent:**

```python
# agents/registry.py (in _load_agents method)
from .layer1.email_parser import EmailParserAgent

self.register(
    name="email_parser",
    layer=AgentLayer.LAYER_1_EXTRACTION,
    agent_class=EmailParserAgent,
    description="Parse emails into structured data",
    capabilities=["email", "mime"],
    dependencies=[]
)
```

### **3. Use the Factory:**

```python
from agents import get_factory

factory = get_factory()
email_parser = factory.create("email_parser")

result = await email_parser.extract(raw_email)
print(result.data)
```

### **4. Create a Workflow:**

```python
from agents import get_factory
from agents.base import Trigger
from datetime import datetime

factory = get_factory(kg_client=kg)

# Create workflow with dependencies
workflow = factory.create_workflow("meeting_orchestrator")

# Execute
trigger = Trigger(
    id="trigger-001",
    type="meeting_request",
    data={"email": raw_email},
    timestamp=datetime.now()
)

result = await workflow.orchestrate(trigger)
```

---

## 📁 File Structure

```
Apollo/
├── agents/
│   ├── __init__.py          ✅ Updated with new exports
│   ├── base.py              ✅ NEW: 5-layer base classes
│   ├── registry.py          ✅ NEW: Central registry
│   ├── factory.py           ✅ NEW: Agent factory
│   │
│   ├── layer1/              🔮 Create as you build
│   │   ├── email_parser.py
│   │   ├── document_parser.py
│   │   └── ...
│   │
│   ├── layer2/              🔮 Create as you build
│   │   ├── person_recognition.py
│   │   └── ...
│   │
│   ├── layer3/              🔮 Create as you build
│   │   ├── financial_analyst.py
│   │   └── ...
│   │
│   ├── layer4/
│   │   ├── meeting_orchestrator.py  ✅ Already exists!
│   │   └── ...
│   │
│   ├── layer5/              🔮 Create as you build
│   │   └── meta_orchestrator.py
│   │
│   └── [legacy agents...]   ✅ Still work!
```

---

## 🎯 Next Steps (Local Iteration)

### **Phase 1: Build Layer 1 Agents (1 week)**

**Create these agents:**
1. `EmailParserAgent` - Parse emails
2. `DocumentParserAgent` - Parse PDFs, Word docs
3. `ImageParserAgent` - Extract text from images (OCR)

**Test with real data:**
```python
# Test email parser
email_parser = factory.create("email_parser")
result = await email_parser.extract(gmail_message)
assert result.success
assert "from" in result.data
```

---

### **Phase 2: Build Layer 2 Agents (1 week)**

**Create these agents:**
1. `PersonRecognitionAgent` - Extract people
2. `CompanyRecognitionAgent` - Extract companies
3. `TopicRecognitionAgent` - Extract topics
4. `SentimentAgent` - Analyze sentiment

**Test entity extraction:**
```python
# Chain Layer 1 → Layer 2
parsed = await email_parser.extract(email)
entities = await person_recognition.recognize(parsed.data)
assert len(entities.data["entities"]) > 0
```

---

### **Phase 3: Build Layer 3 Agents (1 week)**

**Create these agents:**
1. `FinancialAnalystAgent` - Financial analysis
2. `ResearchAgent` - Background research
3. `LegalAgent` - Legal analysis

**Test with knowledge graph:**
```python
# Layer 3 uses knowledge graph
analyst = factory.create("financial_analyst")
analysis = await analyst.analyze(entities, context=kg_context)
assert analysis.confidence > 0.7
```

---

### **Phase 4: Build More Workflows (1 week)**

**Create these workflows:**
1. `InvestorRelationsAgent` - Handle investor emails
2. `ProjectManagerAgent` - Manage projects
3. `SalesProcessAgent` - Sales automation

**Test end-to-end:**
```python
# Full workflow
workflow = factory.create_workflow("investor_relations")
result = await workflow.orchestrate(trigger)
assert result.success
assert len(result.steps_completed) > 3
```

---

## 🛠️ Development Workflow

### **1. Create Agent:**
```bash
# Create new agent file
touch Apollo/agents/layer1/my_agent.py
```

### **2. Implement Interface:**
```python
from agents.base import Layer1Agent

class MyAgent(Layer1Agent):
    def _get_metadata(self): ...
    async def extract(self, raw_data): ...
```

### **3. Register:**
```python
# In agents/registry.py
self.register(name="my_agent", ...)
```

### **4. Test:**
```python
# Test your agent
factory = get_factory()
agent = factory.create("my_agent")
result = await agent.extract(test_data)
assert result.success
```

### **5. Use in Workflow:**
```python
# Register with workflow
workflow.register_agent("my_agent", agent)
await workflow.execute_step("my_agent", data)
```

---

## 📊 Testing

### **Unit Tests:**
```python
# tests/test_agents.py
import pytest
from agents import get_factory

@pytest.mark.asyncio
async def test_email_parser():
    factory = get_factory()
    agent = factory.create("email_parser")
    
    result = await agent.extract(sample_email)
    
    assert result.success
    assert result.confidence > 0.9
    assert "from" in result.data
```

### **Integration Tests:**
```python
@pytest.mark.asyncio
async def test_agent_chain():
    factory = get_factory()
    
    # Create chain
    parser = factory.create("email_parser")
    recognition = factory.create("person_recognition")
    
    # Execute chain
    parsed = await parser.extract(email)
    entities = await recognition.recognize(parsed.data)
    
    assert len(entities.data["entities"]) > 0
```

### **Workflow Tests:**
```python
@pytest.mark.asyncio
async def test_meeting_workflow(kg_client):
    factory = get_factory(kg_client=kg_client)
    workflow = factory.create_workflow("meeting_orchestrator")
    
    trigger = Trigger(
        id="test-001",
        type="meeting_request",
        data={"email": test_email},
        timestamp=datetime.now()
    )
    
    result = await workflow.orchestrate(trigger)
    
    assert result.success
    assert "parse_email" in result.steps_completed
    assert "send_confirmation" in result.steps_completed
```

---

## 🎉 Summary

**What You Have:**
- ✅ Complete 5-layer architecture
- ✅ Base classes with standard interfaces
- ✅ Central registry for discovery
- ✅ Factory with dependency injection
- ✅ Backwards compatibility
- ✅ Comprehensive documentation

**What to Build (Iteratively):**
- 🔮 Layer 1 agents (parsers)
- 🔮 Layer 2 agents (recognition)
- 🔮 Layer 3 agents (domain experts)
- 🔮 Layer 4 agents (workflows)
- 🔮 Layer 5 agents (meta-orchestration)

**Timeline:**
- Week 1: Layer 1 agents
- Week 2: Layer 2 agents
- Week 3: Layer 3 agents
- Week 4: Layer 4 workflows
- Week 5-6: Testing & refinement

**You're ready to iterate locally!** 🚀

---

## 📚 Documentation

**Read these files:**
1. `AGENT_ARCHITECTURE.md` - Complete architecture guide
2. `agents/base.py` - Base class implementations
3. `agents/registry.py` - Registry implementation
4. `agents/factory.py` - Factory implementation

**Example agents:**
- `agents/workflow/meeting_orchestrator_agent.py` - Layer 4 example
- `agents/research/research_agent.py` - Layer 3 example

**Start building!** 🎯
