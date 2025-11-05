# 🧠 Apollo Query Routing - Complex Multi-Agent Queries

**How Apollo handles generic natural language queries**

---

## 🎯 **The Challenge:**

**User Query:**
> "Show me my email usage and spending over the last 3 months while outside of the united states?"

**This requires:**
1. ✅ Email data (Email Agent)
2. ✅ Spending data (Ledger Agent)
3. ✅ Location data (from email metadata or calendar)
4. ✅ Time filtering (last 3 months)
5. ✅ Data aggregation (combine results)
6. ✅ Visualization (charts/graphs)

---

## 🔄 **How Apollo Handles This:**

### **Step 1: Atlas Sends Generic Query**

```python
# Atlas doesn't know which agents to use
# Just sends the natural language query

response = await apollo_client.query(
    user_id="user123",
    org_id="company456",
    app_context="atlas",
    atlas_tier="personal",
    privacy="personal",
    query="Show me my email usage and spending over the last 3 months while outside of the united states?",
    context={
        "source": "chat_interface",
        "timestamp": "2024-10-27T11:48:00Z"
    }
)
```

---

### **Step 2: Meta-Orchestrator Analyzes Query**

```python
# Meta-Orchestrator is the "brain" that routes queries
class MetaOrchestrator:
    async def process_query(self, query: str, context: AgentContext):
        # 1. Analyze intent with LLM
        intent = await self.analyze_intent(query, context)
        
        # Intent analysis result:
        {
            "type": "multi_data_query",
            "complexity": "complex",
            "requires_multiple_agents": True,
            "entities": ["email", "spending", "location"],
            "time_range": "last_3_months",
            "filters": ["location != 'united_states'"],
            "output_format": "visualization"
        }
        
        # 2. Select agents based on intent
        agents = self.select_agents(intent, query)
        # Result: ["email", "ledger", "data"]
        
        # 3. Build execution plan
        plan = self.build_execution_plan(agents, intent)
        
        # Execution plan:
        {
            "steps": [
                {
                    "step": 1,
                    "agent": "email",
                    "action": "fetch_emails",
                    "params": {
                        "time_range": "last_3_months",
                        "include_metadata": True
                    }
                },
                {
                    "step": 2,
                    "agent": "ledger",
                    "action": "fetch_transactions",
                    "params": {
                        "time_range": "last_3_months",
                        "categories": ["all"]
                    }
                },
                {
                    "step": 3,
                    "agent": "data",
                    "action": "filter_by_location",
                    "params": {
                        "location_filter": "outside_us",
                        "data_sources": ["emails", "transactions"]
                    }
                },
                {
                    "step": 4,
                    "agent": "data",
                    "action": "aggregate_and_visualize",
                    "params": {
                        "metrics": ["email_count", "spending_total"],
                        "group_by": "month"
                    }
                }
            ]
        }
        
        # 4. Execute plan
        results = await self.execute_plan(plan, context)
        
        # 5. Combine results
        final_result = self.combine_results(results, intent)
        
        return final_result
```

---

### **Step 3: Meta-Orchestrator Executes Multi-Agent Workflow**

```python
# Execute each step in the plan

# Step 1: Email Agent
email_result = await email_agent.analyze(
    data={
        "action": "fetch_emails",
        "time_range": "last_3_months",
        "include_metadata": True
    },
    context=agent_context
)

# Email Agent returns:
{
    "emails": [
        {
            "id": "email_1",
            "date": "2024-08-15",
            "location": "london",  # From IP metadata
            "count": 1
        },
        {
            "id": "email_2",
            "date": "2024-09-20",
            "location": "paris",
            "count": 1
        },
        # ... more emails
    ],
    "total_emails": 150,
    "locations": ["london", "paris", "tokyo", "new_york"]
}

# Step 2: Ledger Agent
ledger_result = await ledger_agent.analyze(
    data={
        "action": "fetch_transactions",
        "time_range": "last_3_months"
    },
    context=agent_context
)

# Ledger Agent returns:
{
    "transactions": [
        {
            "id": "txn_1",
            "date": "2024-08-15",
            "amount": 45.50,
            "category": "food",
            "location": "london"  # From merchant data
        },
        {
            "id": "txn_2",
            "date": "2024-09-20",
            "amount": 120.00,
            "category": "hotel",
            "location": "paris"
        },
        # ... more transactions
    ],
    "total_spending": 5432.50
}

# Step 3: Data Agent (Filter)
filtered_result = await data_agent.analyze(
    data={
        "action": "filter_by_location",
        "emails": email_result["emails"],
        "transactions": ledger_result["transactions"],
        "location_filter": "outside_us"
    },
    context=agent_context
)

# Data Agent returns:
{
    "filtered_emails": [
        # Only emails from outside US
        {"date": "2024-08-15", "location": "london"},
        {"date": "2024-09-20", "location": "paris"},
        # ...
    ],
    "filtered_transactions": [
        # Only transactions from outside US
        {"date": "2024-08-15", "amount": 45.50, "location": "london"},
        {"date": "2024-09-20", "amount": 120.00, "location": "paris"},
        # ...
    ],
    "total_emails_outside_us": 87,
    "total_spending_outside_us": 3245.75
}

# Step 4: Data Agent (Aggregate & Visualize)
final_result = await data_agent.analyze(
    data={
        "action": "aggregate_and_visualize",
        "filtered_data": filtered_result,
        "metrics": ["email_count", "spending_total"],
        "group_by": "month"
    },
    context=agent_context
)
```

---

### **Step 4: Meta-Orchestrator Returns Combined Result**

```json
{
    "answer": "Over the last 3 months while outside the United States, you sent 87 emails and spent $3,245.75.",
    
    "summary": {
        "total_emails": 87,
        "total_spending": 3245.75,
        "time_range": "2024-07-27 to 2024-10-27",
        "locations": ["London", "Paris", "Tokyo"],
        "top_spending_category": "Hotels ($1,234.50)"
    },
    
    "breakdown_by_month": [
        {
            "month": "August 2024",
            "emails": 32,
            "spending": 1234.50,
            "locations": ["London", "Paris"]
        },
        {
            "month": "September 2024",
            "emails": 28,
            "spending": 987.25,
            "locations": ["Tokyo"]
        },
        {
            "month": "October 2024",
            "emails": 27,
            "spending": 1024.00,
            "locations": ["London"]
        }
    ],
    
    "visualization": {
        "type": "combined_chart",
        "charts": [
            {
                "type": "bar",
                "title": "Email Usage by Month",
                "data": [
                    {"month": "Aug", "value": 32},
                    {"month": "Sep", "value": 28},
                    {"month": "Oct", "value": 27}
                ]
            },
            {
                "type": "bar",
                "title": "Spending by Month",
                "data": [
                    {"month": "Aug", "value": 1234.50},
                    {"month": "Sep", "value": 987.25},
                    {"month": "Oct", "value": 1024.00}
                ]
            },
            {
                "type": "pie",
                "title": "Spending by Category",
                "data": [
                    {"category": "Hotels", "value": 1234.50},
                    {"category": "Food", "value": 876.25},
                    {"category": "Transport", "value": 1135.00}
                ]
            }
        ]
    },
    
    "insights": [
        "Your email usage decreased by 15% from August to October",
        "You spent the most in August ($1,234.50)",
        "Hotels were your biggest expense (38% of total)",
        "You visited 3 countries in the last 3 months"
    ],
    
    "agents_used": ["email", "ledger", "data"],
    "execution_time_ms": 1234,
    "confidence": 0.92
}
```

---

## 🧠 **Meta-Orchestrator Intelligence:**

### **How It Understands Complex Queries:**

```python
class MetaOrchestrator:
    async def analyze_intent(self, query: str, context: AgentContext):
        """Use LLM to understand query intent"""
        
        # Build prompt for LLM
        prompt = f"""
        Analyze this user query and extract:
        1. What data sources are needed?
        2. What time range?
        3. What filters?
        4. What output format?
        
        Query: "{query}"
        
        Available agents:
        - email: Email data and analysis
        - ledger: Financial transactions
        - calendar: Calendar events and location
        - data: Data processing and visualization
        - ... (all 62 agents)
        
        Return JSON with:
        {{
            "data_sources": [...],
            "agents_needed": [...],
            "time_range": "...",
            "filters": [...],
            "output_format": "..."
        }}
        """
        
        # Query LLM (using context-aware model)
        response = await self.query_llm(prompt, context)
        
        # Parse LLM response
        intent = json.loads(response)
        
        return intent
```

---

## 🎯 **Example Queries & Agent Routing:**

### **Query 1: "What did I spend on food last month?"**

**Intent Analysis:**
```json
{
    "data_sources": ["transactions"],
    "agents_needed": ["ledger"],
    "time_range": "last_month",
    "filters": ["category=food"],
    "output_format": "summary"
}
```

**Execution:**
```python
# Single agent workflow
result = await ledger_agent.analyze({
    "action": "get_spending",
    "time_range": "last_month",
    "category": "food"
})
```

---

### **Query 2: "Show me emails from my boss about the Q4 project"**

**Intent Analysis:**
```json
{
    "data_sources": ["emails"],
    "agents_needed": ["email", "contact"],
    "filters": ["sender=boss", "topic=Q4_project"],
    "output_format": "list"
}
```

**Execution:**
```python
# Step 1: Get boss's email
boss = await contact_agent.analyze({"query": "boss"})

# Step 2: Filter emails
emails = await email_agent.analyze({
    "action": "search",
    "sender": boss.email,
    "keywords": ["Q4", "project"]
})
```

---

### **Query 3: "Compare my portfolio performance to S&P 500"**

**Intent Analysis:**
```json
{
    "data_sources": ["portfolio", "market_data"],
    "agents_needed": ["portfolio", "stocks", "data"],
    "comparison": "sp500",
    "output_format": "chart"
}
```

**Execution:**
```python
# Step 1: Get portfolio performance
portfolio = await portfolio_agent.analyze({"action": "get_performance"})

# Step 2: Get S&P 500 performance
sp500 = await stocks_agent.analyze({"symbol": "SPY", "action": "get_performance"})

# Step 3: Compare and visualize
comparison = await data_agent.analyze({
    "action": "compare",
    "data1": portfolio,
    "data2": sp500,
    "visualization": "line_chart"
})
```

---

### **Query 4: "Create a trading bot that buys BTC when RSI < 30"**

**Intent Analysis:**
```json
{
    "action": "code_generation",
    "agents_needed": ["development", "strategy"],
    "context": "trading_bot",
    "requirements": ["RSI indicator", "buy signal", "BTC"],
    "output_format": "code"
}
```

**Execution:**
```python
# Step 1: Generate bot code
code = await development_agent.analyze({
    "action": "generate_code",
    "description": "Trading bot: buy BTC when RSI < 30",
    "language": "python",
    "context": "trading_bot"
})

# Step 2: Validate strategy
validation = await strategy_agent.analyze({
    "action": "validate_strategy",
    "code": code,
    "symbol": "BTC"
})

# Step 3: Backtest
backtest = await backtest_agent.analyze({
    "action": "backtest",
    "code": code,
    "period": "2020-2024"
})
```

---

## 🚀 **API Endpoint for Complex Queries:**

```python
@app.post("/v3/query")
async def query_endpoint(request: NaturalLanguageQuery):
    """
    Handle complex natural language queries
    
    This endpoint:
    1. Accepts generic queries
    2. Uses Meta-Orchestrator to route
    3. Executes multi-agent workflows
    4. Returns combined results
    """
    
    # Build context
    agent_context = AgentContext(
        app_context=request.context.app_context,
        user_id=request.context.user_id,
        org_id=request.context.org_id,
        atlas_tier=request.context.atlas_tier,
        privacy=request.context.privacy,
        # ... full context
    )
    
    # Meta-Orchestrator processes query
    result = await meta_orchestrator.process_query(
        query=request.query,
        context=agent_context
    )
    
    return result
```

---

## 💡 **Key Insights:**

### **1. Meta-Orchestrator is the Brain**
- Analyzes natural language queries
- Selects appropriate agents
- Builds execution plans
- Coordinates multi-agent workflows

### **2. Context-Aware Routing**
- Uses user's tier, privacy, org
- Loads appropriate models
- Respects data boundaries

### **3. Multi-Agent Coordination**
- Can use multiple agents in sequence
- Passes data between agents
- Aggregates results

### **4. Intelligent Query Understanding**
- LLM-powered intent analysis
- Extracts entities, time ranges, filters
- Determines output format

---

## 🎯 **Summary:**

**YES, Apollo can handle generic queries!**

1. ✅ **Atlas sends generic query** → "Show me my email usage and spending..."
2. ✅ **Meta-Orchestrator analyzes** → Determines needs email + ledger + data agents
3. ✅ **Builds execution plan** → Multi-step workflow
4. ✅ **Executes agents** → Each agent does its part
5. ✅ **Combines results** → Aggregates and visualizes
6. ✅ **Returns answer** → Complete response with insights

**The API call is context-aware, AND Apollo interprets the message to route to correct agents!**

---

**Created:** October 27, 2025  
**Version:** 1.0.0  
**Status:** ARCHITECTURE CLARIFICATION
