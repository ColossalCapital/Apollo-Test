# 🧠 Apollo Context-Aware Architecture

## **Overview**

Apollo is **context-aware** - it adapts its behavior based on:
- **App Context** (Atlas, Delt, Akashic, etc.)
- **User Context** (personal vs business entity)
- **Task Context** (coding, trading, document analysis, etc.)
- **Data Context** (what data is available)

---

## **🎯 Context Types**

### **1. App Context**
```python
class AppContext:
    app_name: str           # "atlas", "delt", "akashic", "wtf"
    app_version: str        # "1.0.0"
    environment: str        # "development", "production"
    capabilities: List[str] # What this app can do
```

### **2. User Context**
```python
class UserContext:
    user_id: str           # "user_123"
    entity_id: str         # "entity_456" (optional)
    tenant_type: str       # "personal", "business", "trading"
    role: str              # "owner", "admin", "member", "viewer"
    permissions: List[str] # ["read", "write", "admin"]
```

### **3. Task Context**
```python
class TaskContext:
    task_type: str         # "code", "trade", "document", "email"
    domain: str            # "development", "finance", "legal"
    language: str          # "python", "rust", "typescript" (for code)
    framework: str         # "react", "django", "actix" (for code)
    data_sources: List[str] # ["materialize", "postgres", "filecoin"]
```

### **4. Data Context**
```python
class DataContext:
    available_data: List[str]  # What data is accessible
    real_time: bool            # Is real-time data available?
    historical: bool           # Is historical data available?
    permissions: Dict[str, str] # Data access permissions
```

---

## **🏗️ Context-Aware Agent Selection**

### **Example 1: Delt App (Trading)**
```python
# User in Delt app asks: "Should I buy BTC?"

context = {
    "app": "delt",
    "user_id": "user_123",
    "entity_id": "trading_entity_456",
    "task_type": "trading_decision",
    "domain": "finance",
    "data_sources": ["materialize", "binance_api"]
}

# Meta-Orchestrator selects:
agents = [
    "TradingAgent",      # Market analysis
    "CryptoAgent",       # BTC-specific analysis
    "RiskAgent",         # Risk assessment
    "MaterializeAgent"   # Real-time price data
]

# Result: Comprehensive trading recommendation
```

### **Example 2: Akashic Code Editor (Development)**
```python
# User in Akashic asks: "Complete this function"

context = {
    "app": "akashic",
    "user_id": "user_123",
    "task_type": "code_completion",
    "domain": "development",
    "language": "rust",
    "framework": "actix",
    "file_path": "/src/main.rs",
    "cursor_position": 150
}

# Meta-Orchestrator selects:
agents = [
    "CodeAssistantAgent",  # DeepSeek for code generation
    "GitHubAgent",         # Check similar code in repos
    "DocumentAgent"        # Check documentation
]

# Result: Context-aware code completion
```

### **Example 3: Akashic + Materialize Query**
```python
# User in Akashic asks: "Show me real-time BTC trades"

context = {
    "app": "akashic",
    "user_id": "user_123",
    "task_type": "data_query",
    "domain": "finance",
    "data_sources": ["materialize"],
    "real_time": True
}

# Meta-Orchestrator selects:
agents = [
    "MaterializeAgent",  # Query real-time stream
    "DataAgent",         # Format results
    "CodeAssistantAgent" # Generate visualization code
]

# Result: Real-time data + visualization code
```

### **Example 4: Atlas Business (Project Management)**
```python
# User in Atlas (business entity) asks: "Summarize Q4 projects"

context = {
    "app": "atlas",
    "user_id": "user_123",
    "entity_id": "acme_corp",
    "task_type": "project_summary",
    "domain": "business",
    "data_sources": ["postgres", "github", "calendar"]
}

# Meta-Orchestrator selects:
agents = [
    "ProjectAgent",      # Project analysis
    "GitHubAgent",       # Code commits
    "CalendarAgent",     # Meetings
    "DocumentAgent"      # Project docs
]

# Result: Comprehensive Q4 project summary
```

---

## **🎯 Context-Aware Model Selection**

### **Different Models for Different Contexts:**

```python
# Delt (Trading)
if context.app == "delt":
    models = {
        "trading": "mistral-7b",      # Fast, accurate
        "risk": "phi-3-medium",       # Risk analysis
        "tax": "phi-3-medium"         # Tax calculations
    }

# Akashic (Code Editor)
elif context.app == "akashic":
    models = {
        "code": "deepseek-6.7b",      # Best for code
        "docs": "phi-3-medium",       # Documentation
        "data": "phi-3-mini"          # Data queries
    }

# Atlas (Personal/Business)
elif context.app == "atlas":
    if context.entity_id:
        # Business entity
        models = {
            "legal": "phi-3-medium",   # Contracts
            "finance": "phi-3-medium", # Financials
            "email": "mistral-7b"      # Communication
        }
    else:
        # Personal
        models = {
            "email": "mistral-7b",     # Personal email
            "calendar": "phi-3-mini",  # Scheduling
            "health": "phi-3-mini"     # Health tracking
        }
```

---

## **🚀 Implementation**

### **Context Manager**
```python
# Apollo/context/context_manager.py

class ContextManager:
    """Manages context for Apollo queries"""
    
    def __init__(self):
        self.contexts = {}
    
    def create_context(
        self,
        app: str,
        user_id: str,
        entity_id: str = None,
        task_type: str = None,
        **kwargs
    ) -> Context:
        """Create context for query"""
        
        # App-specific context
        app_context = self.get_app_context(app)
        
        # User-specific context
        user_context = self.get_user_context(user_id, entity_id)
        
        # Task-specific context
        task_context = self.get_task_context(task_type, **kwargs)
        
        # Combine contexts
        return Context(
            app=app_context,
            user=user_context,
            task=task_context,
            data=self.get_data_context(user_id, entity_id)
        )
    
    def get_app_context(self, app: str) -> AppContext:
        """Get app-specific context"""
        
        if app == "delt":
            return AppContext(
                app_name="delt",
                capabilities=[
                    "trading",
                    "market_analysis",
                    "risk_management",
                    "tax_reporting",
                    "portfolio_tracking"
                ],
                data_sources=["materialize", "binance", "coinbase"],
                real_time=True
            )
        
        elif app == "akashic":
            return AppContext(
                app_name="akashic",
                capabilities=[
                    "code_completion",
                    "code_review",
                    "refactoring",
                    "documentation",
                    "data_queries",
                    "project_management"
                ],
                data_sources=["materialize", "github", "postgres"],
                real_time=True
            )
        
        elif app == "atlas":
            return AppContext(
                app_name="atlas",
                capabilities=[
                    "email_management",
                    "calendar_optimization",
                    "document_analysis",
                    "project_management",
                    "financial_tracking",
                    "health_tracking"
                ],
                data_sources=["gmail", "calendar", "drive", "postgres"],
                real_time=False
            )
        
        else:
            return AppContext(app_name=app, capabilities=[])
    
    def get_agent_recommendations(
        self,
        query: str,
        context: Context
    ) -> List[str]:
        """Recommend agents based on context"""
        
        agents = []
        
        # App-specific agents
        if context.app.app_name == "delt":
            agents.extend([
                "TradingAgent",
                "CryptoAgent",
                "RiskAgent"
            ])
        
        elif context.app.app_name == "akashic":
            agents.extend([
                "CodeAssistantAgent",
                "GitHubAgent",
                "MaterializeAgent"
            ])
        
        elif context.app.app_name == "atlas":
            if context.user.entity_id:
                # Business
                agents.extend([
                    "ProjectAgent",
                    "LegalAgent",
                    "ComplianceAgent"
                ])
            else:
                # Personal
                agents.extend([
                    "EmailAgent",
                    "CalendarAgent",
                    "HealthAgent"
                ])
        
        # Task-specific agents
        if context.task.task_type == "code":
            agents.append("CodeAssistantAgent")
        elif context.task.task_type == "trading":
            agents.append("TradingAgent")
        elif context.task.task_type == "data_query":
            agents.append("MaterializeAgent")
        
        return list(set(agents))  # Remove duplicates
```

### **Enhanced Meta-Orchestrator**
```python
# Apollo/agentic/orchestrator/meta_orchestrator.py

class MetaOrchestrator:
    """Context-aware Meta-Orchestrator"""
    
    def __init__(self, agent_registry, context_manager):
        self.agent_registry = agent_registry
        self.context_manager = context_manager
    
    async def process_query(
        self,
        query: str,
        app: str,
        user_id: str,
        entity_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Process query with context awareness"""
        
        # Create context
        context = self.context_manager.create_context(
            app=app,
            user_id=user_id,
            entity_id=entity_id,
            **kwargs
        )
        
        # Get recommended agents
        recommended_agents = self.context_manager.get_agent_recommendations(
            query, context
        )
        
        # Analyze query with context
        selected_agents = await self.analyze_query_with_context(
            query, context, recommended_agents
        )
        
        # Execute agents
        results = await self.execute_agents(
            selected_agents, query, context
        )
        
        # Combine results with context awareness
        final_result = await self.combine_results_with_context(
            results, context
        )
        
        return final_result
```

---

## **📊 Agent Count Update**

### **New Agents Added:**
```
Finance (7):
- LedgerAgent
- TaxAgent
- InvoiceAgent
- BudgetAgent
- TradingAgent ⭐ NEW
- ForexAgent ⭐ NEW
- StocksAgent ⭐ NEW

Web3 (4):
- CryptoAgent ⭐ NEW
- NFTAgent ⭐ NEW
- AuctionAgent ⭐ NEW
- (DeFiAgent - future)

Business (8):
- SalesAgent
- MarketingAgent
- HRAgent
- GrantAgent
- ProjectAgent
- StrategyAgent
- TravelAgent
- CharityAgent ⭐ NEW

Analytics (5):
- DataAgent
- TextAgent
- SchemaAgent
- RouterAgent
- MaterializeAgent ⭐ NEW

Total: 52 Agents! 🎉
```

---

## **🎯 Context-Aware Examples**

### **Example 1: Delt Trading**
```typescript
// User in Delt app
const apollo = new ApolloService({
  url: 'http://localhost:8002',
  context: {
    app: 'delt',
    userId: 'user_123',
    entityId: 'trading_entity',
    capabilities: ['trading', 'risk', 'tax']
  }
});

// Query: "Should I buy BTC?"
const result = await apollo.query("Should I buy BTC?");

// Apollo knows:
// - This is a trading query (app: delt)
// - Use TradingAgent, CryptoAgent, RiskAgent
// - Query Materialize for real-time data
// - Consider user's risk profile
// - Return trading recommendation
```

### **Example 2: Akashic Code Completion**
```typescript
// User in Akashic code editor
const apollo = new ApolloCodeService({
  url: 'http://localhost:8002',
  context: {
    app: 'akashic',
    userId: 'user_123',
    language: 'rust',
    framework: 'actix',
    filePath: '/src/main.rs'
  }
});

// User types: "async fn handle_request"
const completion = await apollo.completeCode({
  code: "async fn handle_request",
  cursor: 23,
  language: "rust"
});

// Apollo knows:
// - This is code completion (app: akashic)
// - Use DeepSeek-6.7B (best for code)
// - Context: Rust + Actix framework
// - Check user's codebase for patterns
// - Return context-aware completion
```

### **Example 3: Akashic Data Query**
```typescript
// User in Akashic asks: "Show me BTC trades"
const result = await apollo.query("Show me BTC trades");

// Apollo knows:
// - This is a data query (app: akashic)
// - Use MaterializeAgent (real-time data)
// - Query: SELECT * FROM trades WHERE symbol = 'BTC'
// - Also use CodeAssistantAgent to generate viz code
// - Return: data + visualization code
```

### **Example 4: Atlas Business Project Management**
```typescript
// User in Atlas (business entity)
const apollo = new ApolloService({
  url: 'http://localhost:8002',
  context: {
    app: 'atlas',
    userId: 'user_123',
    entityId: 'acme_corp',
    role: 'ceo'
  }
});

// Query: "Summarize Q4 projects"
const result = await apollo.query("Summarize Q4 projects");

// Apollo knows:
// - This is business context (entity: acme_corp)
// - Use ProjectAgent, GitHubAgent, CalendarAgent
// - Access business data (not personal)
// - Return comprehensive project summary
```

---

## **🚀 Summary**

**Apollo is now context-aware!**

✅ **52 Agents** (added 7 new agents)
✅ **App-aware** (Delt, Akashic, Atlas, WTF)
✅ **User-aware** (personal vs business)
✅ **Task-aware** (code, trade, document, etc.)
✅ **Data-aware** (Materialize, GitHub, etc.)

**Each app gets the right agents with the right models for the right tasks!** 🎯
