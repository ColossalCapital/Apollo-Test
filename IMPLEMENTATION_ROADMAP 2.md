# 🗺️ Apollo Clean Architecture - Implementation Roadmap

## 📊 Current Status

**Physical Migration: 100% ✅**
- ✅ All 140 agents copied to layer directories
- ✅ 7 new project-specific agents created
- ✅ Layer __init__.py files created
- ✅ Architecture documented

**Code Updates: 0% ⏳**
- ⏳ Agent inheritance updates
- ⏳ Import updates
- ⏳ Registry registration
- ⏳ Atlas integration

---

## 🎯 Implementation Plan (5-6 hours total)

### **Phase 1: Update Agent Inheritance (2-3 hours)**

**Goal:** Update all agents to inherit from layer-specific base classes

**Approach:** Start with new agents, then migrate existing ones gradually

#### **Step 1.1: Update New Agents First (30 min)**

These are the 7 agents we just created - easiest to update:

**File: `agents/layer3/trading/trading_strategy_agent.py`**
```python
# BEFORE
from ..base_agent import BaseAgent, AgentResult

class TradingStrategyAgent(BaseAgent):
    async def process(self, data: dict) -> AgentResult:
        ...

# AFTER
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer

class TradingStrategyAgent(Layer3Agent):
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="trading_strategy",
            layer=AgentLayer.LAYER_3_DOMAIN,
            version="1.0.0",
            description="Algorithmic trading strategy analysis",
            capabilities=["trading", "strategy", "backtest", "optimization"],
            dependencies=[]
        )
    
    async def analyze(self, entities, context=None) -> AgentResult:
        # Rename process() to analyze()
        # Keep same logic
        ...
```

**Repeat for:**
- EntityGovernanceAgent
- InvestorRelationsAgent
- KnowledgeGraphAgent
- WorkflowPatternAgent
- DataPipelineAgent
- SecurityComplianceAgent

#### **Step 1.2: Create Migration Script (1 hour)**

**File: `scripts/migrate_agents.py`**
```python
#!/usr/bin/env python3
"""
Script to help migrate agents to new base classes
"""

import os
import re
from pathlib import Path

LAYER_MAPPINGS = {
    1: {
        "base_class": "Layer1Agent",
        "method": "extract",
        "old_method": "process"
    },
    2: {
        "base_class": "Layer2Agent",
        "method": "recognize",
        "old_method": "process"
    },
    3: {
        "base_class": "Layer3Agent",
        "method": "analyze",
        "old_method": "process"
    },
    4: {
        "base_class": "Layer4Agent",
        "method": "orchestrate",
        "old_method": "process"
    },
    5: {
        "base_class": "Layer5Agent",
        "method": "optimize",
        "old_method": "process"
    }
}

def migrate_agent(file_path: Path, layer: int):
    """Migrate a single agent file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    mapping = LAYER_MAPPINGS[layer]
    
    # Update import
    content = content.replace(
        "from ..base_agent import BaseAgent",
        f"from ...base import {mapping['base_class']}, AgentResult, AgentMetadata, AgentLayer"
    )
    
    # Update class inheritance
    content = re.sub(
        r"class (\w+)\(BaseAgent\):",
        rf"class \1({mapping['base_class']}):",
        content
    )
    
    # Add _get_metadata method (placeholder)
    # User will need to fill this in
    
    # Rename process() to layer-specific method
    content = content.replace(
        f"async def {mapping['old_method']}(",
        f"async def {mapping['method']}("
    )
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Migrated: {file_path}")

def main():
    """Migrate all agents"""
    
    base_path = Path(__file__).parent.parent / "agents"
    
    # Layer 1
    for file in (base_path / "layer1" / "connectors").rglob("*_agent.py"):
        migrate_agent(file, 1)
    
    # Layer 2
    for file in (base_path / "layer2").rglob("*_agent.py"):
        migrate_agent(file, 2)
    
    # Layer 3
    for file in (base_path / "layer3").rglob("*_agent.py"):
        migrate_agent(file, 3)
    
    # Layer 4
    for file in (base_path / "layer4").rglob("*_agent.py"):
        migrate_agent(file, 4)
    
    # Layer 5
    for file in (base_path / "layer5").rglob("*_agent.py"):
        migrate_agent(file, 5)

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
cd Apollo
python scripts/migrate_agents.py
```

#### **Step 1.3: Manual Review & Fix (1-2 hours)**

After running the script:
1. Review each migrated agent
2. Add proper `_get_metadata()` implementation
3. Fix any import issues
4. Test each agent

---

### **Phase 2: Update Registry (1 hour)**

**Goal:** Register all 140 agents in the central registry

#### **Step 2.1: Create Registry Population Script (30 min)**

**File: `scripts/populate_registry.py`**
```python
#!/usr/bin/env python3
"""
Populate registry with all agents
"""

from pathlib import Path
import importlib

def discover_agents(layer_path: Path, layer_num: int):
    """Discover all agents in a layer"""
    
    agents = []
    
    for file in layer_path.rglob("*_agent.py"):
        if file.name == "__init__.py":
            continue
        
        # Get module path
        rel_path = file.relative_to(layer_path.parent.parent)
        module_path = str(rel_path).replace("/", ".").replace(".py", "")
        
        # Import module
        try:
            module = importlib.import_module(module_path)
            
            # Find agent class
            for name in dir(module):
                if name.endswith("Agent") and not name.startswith("_"):
                    agent_class = getattr(module, name)
                    agents.append({
                        "name": name.replace("Agent", "").lower(),
                        "class": agent_class,
                        "module": module_path
                    })
        except Exception as e:
            print(f"⚠️  Failed to import {module_path}: {e}")
    
    return agents

def generate_registry_code():
    """Generate registry registration code"""
    
    base_path = Path(__file__).parent.parent / "agents"
    
    code = []
    
    # Layer 1
    code.append("# Layer 1: Data Extraction Agents")
    agents = discover_agents(base_path / "layer1", 1)
    for agent in agents:
        code.append(f"""
self.register(
    name="{agent['name']}",
    layer=AgentLayer.LAYER_1_EXTRACTION,
    agent_class={agent['class'].__name__},
    description="TODO: Add description",
    capabilities=["TODO"],
    dependencies=[]
)
""")
    
    # Repeat for layers 2-5...
    
    print("\n".join(code))

if __name__ == "__main__":
    generate_registry_code()
```

#### **Step 2.2: Update Registry Manually (30 min)**

Copy generated code into `agents/registry.py` and fill in:
- Descriptions
- Capabilities
- Dependencies

---

### **Phase 3: Update Atlas Integration (1 hour)**

**Goal:** Update Atlas Rust backend to use new factory

#### **Step 3.1: Update Apollo Client (30 min)**

**File: `Atlas/backend/src/services/apollo_client.rs`**

```rust
// BEFORE
pub async fn call_agent(&self, agent_name: &str, data: Value) -> Result<Value> {
    let url = format!("{}/agent/{}", self.base_url, agent_name);
    // ...
}

// AFTER
pub async fn call_agent_by_layer(
    &self, 
    layer: u8, 
    agent_name: &str, 
    data: Value
) -> Result<Value> {
    let url = format!("{}/layer{}/{}", self.base_url, layer, agent_name);
    
    let response = self.client
        .post(&url)
        .json(&data)
        .send()
        .await?;
    
    Ok(response.json().await?)
}

// Convenience methods
pub async fn extract_data(&self, connector: &str, data: Value) -> Result<Value> {
    self.call_agent_by_layer(1, connector, data).await
}

pub async fn recognize_entities(&self, agent: &str, data: Value) -> Result<Value> {
    self.call_agent_by_layer(2, agent, data).await
}

pub async fn analyze_domain(&self, expert: &str, entities: Value) -> Result<Value> {
    self.call_agent_by_layer(3, expert, entities).await
}

pub async fn execute_workflow(&self, workflow: &str, trigger: Value) -> Result<Value> {
    self.call_agent_by_layer(4, workflow, trigger).await
}
```

#### **Step 3.2: Update Apollo API Routes (30 min)**

**File: `Apollo/api/main.py`**

```python
from fastapi import FastAPI
from agents import get_factory

app = FastAPI()
factory = None

@app.on_event("startup")
async def startup():
    global factory
    kg = await get_knowledge_graph()
    factory = get_factory(kg_client=kg)

# Layer-specific endpoints
@app.post("/layer1/{agent_name}")
async def layer1_endpoint(agent_name: str, data: dict):
    agent = factory.create_layer1_agent(agent_name)
    result = await agent.extract(data)
    return result

@app.post("/layer2/{agent_name}")
async def layer2_endpoint(agent_name: str, data: dict):
    agent = factory.create_layer2_agent(agent_name)
    result = await agent.recognize(data)
    return result

@app.post("/layer3/{agent_name}")
async def layer3_endpoint(agent_name: str, data: dict):
    agent = factory.create_layer3_agent(agent_name)
    result = await agent.analyze(data.get("entities"), data.get("context"))
    return result

@app.post("/layer4/{workflow_name}")
async def layer4_endpoint(workflow_name: str, trigger: dict):
    workflow = factory.create_workflow(workflow_name)
    result = await workflow.orchestrate(trigger)
    return result

@app.post("/layer5/{agent_name}")
async def layer5_endpoint(agent_name: str, system_state: dict):
    agent = factory.create_layer5_agent(agent_name)
    result = await agent.optimize(system_state)
    return result
```

---

### **Phase 4: Testing & Cleanup (1 hour)**

#### **Step 4.1: Create Tests (30 min)**

**File: `tests/test_architecture.py`**

```python
import pytest
from agents import get_factory, get_registry

@pytest.mark.asyncio
async def test_registry():
    """Test registry has all agents"""
    registry = get_registry()
    stats = registry.get_stats()
    
    assert stats['layer_1_agents'] == 43
    assert stats['layer_2_agents'] == 12
    assert stats['layer_3_agents'] == 69
    assert stats['layer_4_agents'] == 14
    assert stats['layer_5_agents'] == 2
    assert stats['total_agents'] == 140

@pytest.mark.asyncio
async def test_factory():
    """Test factory can create agents"""
    factory = get_factory()
    
    # Test Layer 1
    agent = factory.create("gmail_connector")
    assert agent is not None
    
    # Test Layer 3
    agent = factory.create("trading_strategy")
    assert agent is not None
    
    # Test Layer 4
    workflow = factory.create_workflow("meeting_orchestrator")
    assert workflow is not None

@pytest.mark.asyncio
async def test_agent_chain():
    """Test agent chaining"""
    factory = get_factory()
    
    chain = factory.create_agent_chain([
        "gmail_connector",
        "person_recognition",
        "trading_strategy"
    ])
    
    assert len(chain) == 3
```

#### **Step 4.2: Cleanup (30 min)**

1. Remove old agent directories (once migration is verified)
2. Update all documentation
3. Create migration changelog
4. Update README

---

## 📋 Execution Checklist

### **Day 1: Agent Migration (3 hours)**
- [ ] Update 7 new agents manually (30 min)
- [ ] Create migration script (1 hour)
- [ ] Run migration script (5 min)
- [ ] Review and fix migrated agents (1.5 hours)

### **Day 2: Registry & Integration (2 hours)**
- [ ] Create registry population script (30 min)
- [ ] Update registry with all agents (30 min)
- [ ] Update Atlas Rust client (30 min)
- [ ] Update Apollo API routes (30 min)

### **Day 3: Testing & Cleanup (1 hour)**
- [ ] Create tests (30 min)
- [ ] Run tests and fix issues (20 min)
- [ ] Cleanup old directories (10 min)

---

## 🎯 Success Criteria

**When complete, you should be able to:**

```python
from agents import get_factory

factory = get_factory(kg_client=kg)

# Create any agent
agent = factory.create("trading_strategy")

# Execute agent
result = await agent.analyze(entities, context)

# Create workflow
workflow = factory.create_workflow("meeting_orchestrator")
result = await workflow.orchestrate(trigger)
```

**And from Atlas:**

```rust
let apollo = ApolloClient::new("http://localhost:8002");

// Call Layer 3 agent
let result = apollo.analyze_domain("trading_strategy", entities).await?;

// Execute workflow
let result = apollo.execute_workflow("meeting_orchestrator", trigger).await?;
```

---

## 📈 Progress Tracking

**Current: 66% Complete**
- ✅ Architecture design (100%)
- ✅ Physical migration (100%)
- ⏳ Code updates (0%)

**Target: 100% Complete**
- ✅ Architecture design (100%)
- ✅ Physical migration (100%)
- ✅ Code updates (100%)

---

## 🚀 Ready to Execute!

**The roadmap is complete. You can now execute this plan over 3 days to finish the clean architecture migration!** 🎯✨
