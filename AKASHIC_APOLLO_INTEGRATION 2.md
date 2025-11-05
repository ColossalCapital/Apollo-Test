# 🎯 Akashic + Apollo Integration

## **Overview**

Akashic is a universal code editor that embeds in multiple apps:
- **Atlas** (personal/business project management)
- **Delt** (trading platform)
- **Standalone** (general development)

Apollo adapts based on **where Akashic is embedded** and **what the user is doing**.

---

## **🏗️ Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Akashic Code Editor                       │
│  (Universal - same editor everywhere)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Apollo Context Router                      │
│  (Detects: app, project type, file type, user query)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Apollo        │  │ Apollo        │  │ Apollo        │
│ (Atlas Mode)  │  │ (Delt Mode)   │  │ (Standalone)  │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

## **🎯 Mode 1: Akashic in Atlas (Project Management)**

### **Context:**
```typescript
{
  app: "atlas",
  editor: "akashic",
  project_type: "business_app",
  entity_id: "acme_corp",
  language: "rust",
  framework: "actix"
}
```

### **Available Agents:**
```
Core Agents:
✅ CodeAssistantAgent (DeepSeek-6.7B) - Code completion
✅ AgenticRAG - Codebase understanding
✅ GitHubAgent - Repo management
✅ DocumentAgent - Documentation
✅ ProjectAgent - Project management

Business Agents (because entity_id exists):
✅ LegalAgent - Contract templates
✅ ComplianceAgent - Code compliance
✅ HRAgent - Team management

Data Agents:
✅ MaterializeAgent - Query project data
✅ DataAgent - Data analysis
```

### **Example Queries:**

**Code Completion:**
```typescript
// User types in Akashic (Atlas)
async fn handle_request(req: HttpRequest) -> Result<HttpResponse> {
    // Apollo suggests (DeepSeek):
    let user_id = req.match_info().get("user_id").unwrap();
    let entity_id = req.match_info().get("entity_id").unwrap();
    
    // Check permissions
    if !has_permission(user_id, entity_id).await? {
        return Ok(HttpResponse::Forbidden().finish());
    }
    
    // Continue...
}
```

**Natural Language Query:**
```typescript
// User asks in Akashic (Atlas): "Show me all API endpoints"
const result = await apollo.query("Show me all API endpoints", {
  app: "atlas",
  editor: "akashic",
  project_path: "/Users/leonard/Atlas"
});

// Apollo uses:
// - AgenticRAG: Scan codebase for routes
// - CodeAssistantAgent: Parse route definitions
// - DocumentAgent: Generate API docs

// Returns:
{
  endpoints: [
    { method: "GET", path: "/api/users", handler: "get_users" },
    { method: "POST", path: "/api/entities", handler: "create_entity" },
    // ...
  ],
  documentation: "# API Endpoints\n..."
}
```

**Project Management Query:**
```typescript
// User asks: "What tasks are due this week?"
const result = await apollo.query("What tasks are due this week?", {
  app: "atlas",
  editor: "akashic",
  entity_id: "acme_corp"
});

// Apollo uses:
// - ProjectAgent: Query project tasks
// - CalendarAgent: Check deadlines
// - GitHubAgent: Check open issues

// Returns:
{
  tasks: [
    { name: "Implement auth", due: "2025-10-28", status: "in_progress" },
    { name: "Write tests", due: "2025-10-29", status: "pending" }
  ]
}
```

---

## **🎯 Mode 2: Akashic in Delt (Trading Platform)**

### **Context:**
```typescript
{
  app: "delt",
  editor: "akashic",
  project_type: "trading_bot",
  entity_id: "trading_entity",
  language: "python",
  framework: "fastapi"
}
```

### **Available Agents:**
```
Core Agents:
✅ CodeAssistantAgent (DeepSeek-6.7B) - Code completion
✅ AgenticRAG - Codebase understanding
✅ GitHubAgent - Repo management

Finance Agents:
✅ TradingAgent - Trading logic
✅ CryptoAgent - Crypto analysis
✅ StocksAgent - Stock analysis
✅ ForexAgent - Forex analysis
✅ RiskAgent - Risk management
✅ TaxAgent - Tax calculations

Data Agents:
✅ MaterializeAgent - Real-time market data
✅ DataAgent - Data analysis
✅ SchemaAgent - Data schemas

Integration Agents (NEW!):
✅ BrokerAgent - Broker integrations
✅ ExchangeAgent - Exchange APIs
```

### **Example Queries:**

**Code Completion (Trading Bot):**
```python
# User types in Akashic (Delt)
async def execute_trade(symbol: str, quantity: float):
    # Apollo suggests (DeepSeek + TradingAgent):
    
    # Get current price from Materialize
    price = await materialize.query(
        f"SELECT price FROM market_data WHERE symbol = '{symbol}' ORDER BY timestamp DESC LIMIT 1"
    )
    
    # Check risk limits
    risk = await risk_agent.analyze({
        "symbol": symbol,
        "quantity": quantity,
        "price": price
    })
    
    if risk["risk_level"] > 0.5:
        raise Exception("Risk too high")
    
    # Execute trade
    order = await broker.place_order(symbol, quantity, price)
    
    # Log to Materialize
    await materialize.insert("trades", order)
    
    return order
```

**Natural Language Query (Market Data):**
```typescript
// User asks in Akashic (Delt): "Show me BTC trades in the last hour"
const result = await apollo.query("Show me BTC trades in the last hour", {
  app: "delt",
  editor: "akashic"
});

// Apollo uses:
// - MaterializeAgent: Query real-time stream
// - DataAgent: Format results
// - CodeAssistantAgent: Generate visualization code

// Returns:
{
  sql: "SELECT * FROM trades WHERE symbol = 'BTC' AND timestamp > NOW() - INTERVAL '1 hour'",
  data: [...],
  visualization_code: `
    import matplotlib.pyplot as plt
    
    plt.plot(data['timestamp'], data['price'])
    plt.title('BTC Trades - Last Hour')
    plt.show()
  `
}
```

**Trading Strategy Query:**
```typescript
// User asks: "Should I buy BTC right now?"
const result = await apollo.query("Should I buy BTC right now?", {
  app: "delt",
  editor: "akashic"
});

// Apollo uses:
// - TradingAgent: Market analysis
// - CryptoAgent: BTC-specific analysis
// - RiskAgent: Risk assessment
// - MaterializeAgent: Real-time price data

// Returns:
{
  recommendation: "buy",
  confidence: 0.85,
  entry_price: 51000,
  stop_loss: 50000,
  take_profit: 53000,
  reasoning: "Strong bullish momentum, low risk",
  code_snippet: `
    # Execute this trade
    await execute_trade("BTC", quantity=0.1, entry=51000, stop_loss=50000)
  `
}
```

**Broker Integration Query:**
```typescript
// User asks: "Connect to Interactive Brokers"
const result = await apollo.query("Connect to Interactive Brokers", {
  app: "delt",
  editor: "akashic"
});

// Apollo uses:
// - BrokerAgent: Generate IB connection code
// - CodeAssistantAgent: Generate boilerplate

// Returns:
{
  code: `
    from ib_insync import IB, Stock, MarketOrder
    
    # Connect to Interactive Brokers
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    # Place order
    contract = Stock('AAPL', 'SMART', 'USD')
    order = MarketOrder('BUY', 100)
    trade = ib.placeOrder(contract, order)
    
    # Wait for fill
    while not trade.isDone():
        ib.sleep(1)
    
    print(f"Order filled: {trade}")
  `,
  documentation: "# Interactive Brokers Integration\n..."
}
```

---

## **🎯 Mode 3: Akashic Standalone (General Development)**

### **Context:**
```typescript
{
  app: "akashic",
  editor: "akashic",
  project_type: "general",
  language: "typescript",
  framework: "react"
}
```

### **Available Agents:**
```
Core Agents:
✅ CodeAssistantAgent (DeepSeek-6.7B) - Code completion
✅ AgenticRAG - Codebase understanding
✅ GitHubAgent - Repo management
✅ DocumentAgent - Documentation
✅ APIAgent - API integration
```

### **Example Queries:**

**Code Completion:**
```typescript
// User types in Akashic (Standalone)
const MyComponent: React.FC = () => {
  // Apollo suggests (DeepSeek):
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/data');
      const json = await response.json();
      setData(json);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      {loading ? <Spinner /> : <DataTable data={data} />}
    </div>
  );
};
```

---

## **🔧 Implementation**

### **Akashic Apollo Service (Context-Aware)**

```typescript
// Akashic/src/services/apollo.ts

export class AkashicApolloService {
  private apolloUrl: string;
  private context: AkashicContext;
  
  constructor(context: AkashicContext) {
    this.apolloUrl = process.env.APOLLO_URL || 'http://localhost:8002';
    this.context = context;
  }
  
  /**
   * Query Apollo with Akashic context
   */
  async query(query: string, additionalContext?: any): Promise<any> {
    const fullContext = {
      ...this.context,
      ...additionalContext,
      editor: "akashic"
    };
    
    const response = await fetch(`${this.apolloUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        user_id: this.context.userId,
        entity_id: this.context.entityId,
        context: fullContext
      })
    });
    
    return await response.json();
  }
  
  /**
   * Code completion with context
   */
  async completeCode(params: {
    code: string;
    cursor: number;
    language: string;
    filePath?: string;
  }): Promise<string> {
    const response = await fetch(`${this.apolloUrl}/analyze/code_assistant`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: "completion",
        code: params.code,
        cursor: params.cursor,
        language: params.language,
        file_path: params.filePath,
        context: this.context
      })
    });
    
    const result = await response.json();
    return result.completion;
  }
  
  /**
   * Query Materialize (only available in Delt mode)
   */
  async queryMaterialize(query: string): Promise<any> {
    if (this.context.app !== "delt") {
      throw new Error("Materialize queries only available in Delt mode");
    }
    
    return await this.query(`Query Materialize: ${query}`, {
      data_source: "materialize"
    });
  }
  
  /**
   * Get trading recommendation (only available in Delt mode)
   */
  async getTradingRecommendation(symbol: string): Promise<any> {
    if (this.context.app !== "delt") {
      throw new Error("Trading queries only available in Delt mode");
    }
    
    return await this.query(`Should I buy ${symbol}?`, {
      task_type: "trading_decision"
    });
  }
  
  /**
   * Get project tasks (only available in Atlas mode)
   */
  async getProjectTasks(): Promise<any> {
    if (this.context.app !== "atlas") {
      throw new Error("Project queries only available in Atlas mode");
    }
    
    return await this.query("What tasks are due this week?", {
      task_type: "project_management"
    });
  }
}

/**
 * Create Akashic Apollo service based on context
 */
export function createAkashicApollo(context: AkashicContext): AkashicApolloService {
  return new AkashicApolloService(context);
}
```

### **Usage in Atlas:**

```typescript
// Atlas/frontend/mobile/src/screens/CodeEditor.tsx

import { createAkashicApollo } from 'akashic/services/apollo';

const CodeEditorScreen = () => {
  const apollo = createAkashicApollo({
    app: "atlas",
    userId: currentUser.id,
    entityId: currentEntity?.id,
    projectType: "business_app",
    language: "rust",
    framework: "actix"
  });
  
  // Code completion
  const handleCodeChange = async (code: string, cursor: number) => {
    const completion = await apollo.completeCode({
      code,
      cursor,
      language: "rust"
    });
    // Show completion...
  };
  
  // Natural language query
  const handleQuery = async (query: string) => {
    const result = await apollo.query(query);
    // Show result...
  };
  
  return (
    <AkashicEditor
      onCodeChange={handleCodeChange}
      onQuery={handleQuery}
    />
  );
};
```

### **Usage in Delt:**

```typescript
// Delt/lib/screens/code_editor_screen.dart

class CodeEditorScreen extends StatefulWidget {
  @override
  _CodeEditorScreenState createState() => _CodeEditorScreenState();
}

class _CodeEditorScreenState extends State<CodeEditorScreen> {
  late AkashicApolloService apollo;
  
  @override
  void initState() {
    super.initState();
    
    apollo = AkashicApolloService(
      context: AkashicContext(
        app: "delt",
        userId: currentUser.id,
        entityId: tradingEntity.id,
        projectType: "trading_bot",
        language: "python",
        framework: "fastapi",
      ),
    );
  }
  
  // Code completion
  Future<void> handleCodeChange(String code, int cursor) async {
    final completion = await apollo.completeCode(
      code: code,
      cursor: cursor,
      language: "python",
    );
    // Show completion...
  }
  
  // Trading query
  Future<void> handleTradingQuery(String symbol) async {
    final recommendation = await apollo.getTradingRecommendation(symbol);
    // Show recommendation...
  }
  
  // Materialize query
  Future<void> handleDataQuery(String query) async {
    final result = await apollo.queryMaterialize(query);
    // Show result...
  }
  
  @override
  Widget build(BuildContext context) {
    return AkashicEditor(
      onCodeChange: handleCodeChange,
      onQuery: handleTradingQuery,
    );
  }
}
```

---

## **🎯 Agent Selection Logic**

### **Apollo Context Router:**

```python
# Apollo/context/router.py

class ApolloContextRouter:
    """Routes queries to appropriate agents based on context"""
    
    def get_agents_for_context(self, context: Dict[str, Any]) -> List[str]:
        """Get available agents based on context"""
        
        agents = []
        
        # Always available in Akashic
        agents.extend([
            "CodeAssistantAgent",  # DeepSeek-6.7B
            "AgenticRAG",          # Codebase understanding
            "GitHubAgent",         # Repo management
            "DocumentAgent"        # Documentation
        ])
        
        # App-specific agents
        if context.get("app") == "atlas":
            agents.extend([
                "ProjectAgent",      # Project management
                "CalendarAgent",     # Deadlines
            ])
            
            # Business entity
            if context.get("entity_id"):
                agents.extend([
                    "LegalAgent",       # Contracts
                    "ComplianceAgent",  # Compliance
                    "HRAgent"           # Team management
                ])
        
        elif context.get("app") == "delt":
            agents.extend([
                "TradingAgent",      # Trading logic
                "CryptoAgent",       # Crypto analysis
                "StocksAgent",       # Stock analysis
                "ForexAgent",        # Forex analysis
                "RiskAgent",         # Risk management
                "TaxAgent",          # Tax calculations
                "MaterializeAgent",  # Real-time data
                "BrokerAgent",       # Broker integrations (NEW!)
                "ExchangeAgent"      # Exchange APIs (NEW!)
            ])
        
        return agents
```

---

## **📊 Summary**

**Akashic + Apollo Integration:**

✅ **Same Akashic editor** in all apps
✅ **Context-aware Apollo** adapts to app
✅ **DeepSeek-6.7B** for code completion everywhere
✅ **AgenticRAG** for codebase understanding everywhere
✅ **App-specific agents** based on context

**Atlas Mode:**
- Project management agents
- Business/legal agents (if entity)
- General development agents

**Delt Mode:**
- Finance agents (Trading, Crypto, Stocks, Forex)
- Data agents (Materialize)
- Broker/Exchange agents (NEW!)
- Risk/Tax agents

**Standalone Mode:**
- General development agents
- No app-specific agents

**This enables:**
- ✅ Same editor, different intelligence
- ✅ Context-aware suggestions
- ✅ Real-time data in Delt
- ✅ Project management in Atlas
- ✅ Universal code completion
