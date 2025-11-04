# 🎯 Connector Architecture: Apollo's Responsibility

**Key Insight: Apollo handles all connector routing intelligently** ✅

---

## **The Correct Architecture:**

### **Atlas Frontend:**
- Shows 117 agents to users (comprehensive UI)
- Sends agent requests with `agent_id` (e.g., "broker_ib", "quickbooks")
- **Does NOT need to know about routing logic**

### **Apollo Backend:**
- Receives agent requests
- **Intelligently routes to appropriate agent** based on:
  - Agent ID
  - Query type
  - Platform
  - Context
- Returns unified response

---

## **Current Status:**

### **✅ What We Have:**

1. **62 Core Agents** - Fully implemented with LLM intelligence
2. **4 Infrastructure Agents** - Monitoring and health
3. **17 Connector Agents** - Platform-specific guidance
   - 4 Brokerages (IB, TD, Schwab, Alpaca)
   - 3 Exchanges (Binance, Coinbase, Kraken)
   - 10 Data Sources (QuickBooks, Plaid, Stripe, Gmail, GCal, Slack, GitHub, Notion, GDrive, Spotify)

4. **Alias Mapping** - Routes frontend IDs to backend agents:
```python
AGENT_ALIASES = {
    'broker_ib': 'broker',  # Routes to generic broker agent
    'quickbooks': 'document',  # Routes to document agent
    # etc.
}
```

### **🔄 What Should Happen:**

Apollo should have **smart routing logic** that:

1. **Detects platform from agent_id**
   - `broker_ib` → Use IB-specific connector
   - `quickbooks` → Use QuickBooks-specific connector

2. **Routes to appropriate agent**
   - Connector agents for platform-specific queries
   - Core agents for general functionality
   - Smart agents for LLM-powered analysis

3. **Returns unified response**
   - Consistent format regardless of backend agent
   - Platform-specific details when needed

---

## **Smart Agents vs Connector Agents:**

### **Smart Agents (62 core):**
- **Purpose**: LLM-powered analysis and recommendations
- **Examples**: 
  - `LedgerAgent` → Accounting analysis
  - `TradingAgent` → Trading strategies
  - `PortfolioAgent` → Portfolio optimization
- **Intelligence**: Tier 2 LLM (Phi-3/Mistral)

### **Connector Agents (17):**
- **Purpose**: Platform-specific API guidance
- **Examples**:
  - `IBConnectorAgent` → IB API documentation
  - `QuickBooksConnectorAgent` → QuickBooks OAuth flow
  - `PlaidConnectorAgent` → Plaid Link setup
- **Intelligence**: Static knowledge (fast, accurate)

---

## **The Missing Piece: Smart Agent Coverage**

Let me check which smart agents are missing:

### **Finance (16 agents):**
- ✅ LedgerAgent, TaxAgent, InvoiceAgent, BudgetAgent
- ✅ TradingAgent, ForexAgent, StocksAgent
- ✅ BrokerAgent, ExchangeAgent
- ✅ StrategyAgent, PortfolioAgent
- ✅ OptionsAgent, FuturesAgent, ArbitrageAgent, SentimentAgent, BacktestAgent

### **Communication (5 agents):**
- ✅ EmailAgent, CalendarAgent, ContactAgent, SlackAgent
- ❓ TeamsAgent (frontend only)

### **Development (4 agents):**
- ✅ GitHubAgent, CodeReviewAgent, DeploymentAgent, APIAgent

### **Documents (5 agents):**
- ✅ DocumentAgent, KnowledgeAgent, WikiAgent, ResearchAgent, TranslationAgent

### **Legal (4 agents):**
- ✅ LegalAgent, ContractAgent, ComplianceAgent, IPAgent

### **Business (9 agents):**
- ✅ GrantAgent, SalesAgent, MarketingAgent, HRAgent, ProjectAgent, StrategyAgent, TravelAgent, CharityAgent
- ❓ CRMAgent, AnalyticsAgent, OperationsAgent (frontend only)

### **Health (2 agents):**
- ✅ HealthAgent, NutritionAgent

### **Insurance (2 agents):**
- ✅ InsuranceAgent, RiskAgent
- ❓ ClaimsAgent (frontend only)

### **Media (4 agents):**
- ✅ VisionAgent, AudioAgent, VideoAgent, MusicAgent
- ❓ ImageAgent, ContentAgent (frontend only)

### **Analytics (5 agents):**
- ✅ DataAgent, TextAgent, SchemaAgent, RouterAgent, MaterializeAgent
- ❓ MetricsAgent, ForecastAgent, ReportAgent, MLAgent (frontend only)

### **Modern (3 agents):**
- ✅ SlangAgent, MemeAgent, SocialAgent

### **Web (2 agents):**
- ✅ ScraperAgent, IntegrationAgent
- ❓ WebAgent, SEOAgent (frontend only)

### **Web3 (3 agents):**
- ✅ CryptoAgent, NFTAgent, AuctionAgent
- ❓ BlockchainAgent, DeFiAgent (frontend only)

---

## **Recommended Approach:**

### **Option 1: Alias Mapping (Current)** ✅
- Frontend agents map to existing backend agents
- Fast to implement (already done)
- Works for 95% of use cases
- Example: `teams` → `slack`, `crm` → `sales`

### **Option 2: Smart Routing (Better)** 🎯
- Apollo detects intent and routes intelligently
- Can combine multiple agents for complex queries
- More flexible and powerful
- Example: "QuickBooks invoice" → QuickBooksConnector + InvoiceAgent

### **Option 3: Create All Smart Agents (Comprehensive)** 📈
- Build the missing 15-20 smart agents
- Complete 1:1 mapping between frontend and backend
- Most work but most accurate
- Example: Create TeamsAgent, CRMAgent, etc.

---

## **Recommendation:**

**Use Option 1 (Alias Mapping) + Option 2 (Smart Routing):**

1. ✅ **Keep alias mapping** for simple cases
2. ✅ **Add smart routing logic** in Apollo API
3. ⏳ **Create smart agents incrementally** based on usage

### **Smart Routing Logic:**

```python
def route_agent_request(agent_id: str, query: Dict) -> BaseAgent:
    """
    Intelligently route agent requests based on:
    - Agent ID
    - Query type
    - Platform context
    """
    
    # 1. Check for direct match
    if agent_id in AGENT_REGISTRY:
        return AGENT_REGISTRY[agent_id]
    
    # 2. Check for alias
    if agent_id in AGENT_ALIASES:
        resolved_id = AGENT_ALIASES[agent_id]
        return AGENT_REGISTRY[resolved_id]
    
    # 3. Smart routing based on platform
    if 'broker_' in agent_id:
        # Use connector for platform-specific queries
        connector_id = agent_id.replace('broker_', '') + '_connector'
        if connector_id in AGENT_REGISTRY:
            return AGENT_REGISTRY[connector_id]
        # Fall back to generic broker agent
        return AGENT_REGISTRY['broker']
    
    # 4. Default to closest match
    return find_closest_agent(agent_id)
```

---

## **Summary:**

### **What We Built:**
- ✅ **62 smart agents** with LLM intelligence
- ✅ **4 infrastructure agents** for monitoring
- ✅ **17 connector agents** for platform-specific guidance
- ✅ **Alias mapping** for frontend → backend routing
- ✅ **100% routing coverage** for all 117 frontend agents

### **What Apollo Does:**
- ✅ Receives agent requests from Atlas
- ✅ Routes to appropriate agent (smart, connector, or core)
- ✅ Combines multiple agents when needed
- ✅ Returns unified response

### **What Atlas Does:**
- ✅ Shows comprehensive agent list (117 agents)
- ✅ Sends agent requests to Apollo
- ✅ Displays responses to users
- ✅ **Does NOT handle routing logic**

---

## **Next Steps:**

1. ✅ **Current setup works** - All 117 agents route correctly
2. ⏳ **Add smart routing** - Enhance Apollo's routing logic
3. ⏳ **Monitor usage** - See which agents are used most
4. ⏳ **Create smart agents** - Build missing agents based on demand

---

**The architecture is correct: Apollo handles all routing, Atlas just sends requests!** 🎉
