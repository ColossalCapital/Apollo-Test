# Agent Mapping Strategy: Atlas UI ↔ Apollo Backend

**Critical for AI Agent Routing** ✅

---

## **Current Status:**

- **Atlas Frontend**: 117 agents (72 core + 45 specialized)
- **Apollo Backend**: 73 agents (62 core + 4 infrastructure + 7 connectors)
- **Gap**: 44 agents in frontend without backend implementation

---

## **Mapping Strategy:**

### **1. Direct 1:1 Mapping (62 agents)** ✅

These agents have exact matches between frontend and backend:

**Finance (16):**
- ledger, tax, invoice, budget, trading, forex, stocks, options, futures, arbitrage, sentiment, backtest, portfolio
- **Backend has**: broker, exchange (generic)
- **Frontend has**: broker_ib, broker_td, broker_schwab, broker_alpaca, exchange_binance, exchange_coinbase, exchange_kraken

**Communication (4):**
- email, calendar, contact, slack ✅

**Development (4):**
- github, api ✅
- **Backend has**: codereview, deployment
- **Frontend has**: code, devops

**Documents (5):**
- **Backend has**: document, knowledge, research, translation, wiki ✅
- **Frontend has**: document, pdf, ocr, notion, drive

**Legal (4):**
- legal, contract, compliance, ip ✅

**Business (8):**
- grant, sales, marketing, hr, project ✅
- **Backend has**: strategy, travel, charity
- **Frontend has**: crm, analytics, business_strategy, operations

**Health (2):**
- health, nutrition ✅

**Insurance (2):**
- **Backend has**: insurance, risk ✅
- **Frontend has**: insurance, claims

**Media (4):**
- audio, video ✅
- **Backend has**: vision, music
- **Frontend has**: image, content

**Analytics (5):**
- data ✅
- **Backend has**: text, schema, router, materialize
- **Frontend has**: metrics, forecast, report, ml

**Modern (3):**
- slang, meme, social ✅

**Web (2):**
- **Backend has**: scraper, integration ✅
- **Frontend has**: web, seo

**Web3 (3):**
- nft ✅
- **Backend has**: crypto, auction
- **Frontend has**: blockchain, defi

---

## **2. Routing Strategy:**

### **Option A: Alias Mapping (Recommended)** ✅

Create an alias map in Apollo that routes frontend agent IDs to backend agents:

```python
AGENT_ALIASES = {
    # Frontend ID -> Backend Agent
    'broker_ib': 'broker',
    'broker_td': 'broker',
    'broker_schwab': 'broker',
    'broker_alpaca': 'broker',
    'exchange_binance': 'exchange',
    'exchange_coinbase': 'exchange',
    'exchange_kraken': 'exchange',
    'code': 'codereview',
    'devops': 'deployment',
    'pdf': 'document',
    'ocr': 'document',
    'notion': 'document',
    'drive': 'document',
    'crm': 'sales',
    'analytics': 'data',
    'business_strategy': 'strategy',
    'operations': 'project',
    'claims': 'insurance',
    'image': 'vision',
    'content': 'text',
    'metrics': 'data',
    'forecast': 'data',
    'report': 'data',
    'ml': 'data',
    'router': 'router',  # Core router agent
    'web': 'scraper',
    'seo': 'scraper',
    'blockchain': 'crypto',
    'defi': 'crypto',
    'teams': 'slack',  # Similar functionality
}
```

### **Option B: Create Missing Agents** ⏳

Build the 44 missing agents in Apollo backend. This is more work but provides:
- Better separation of concerns
- More specialized responses
- Easier to maintain

### **Option C: Hybrid Approach (Best)** ✅

1. **Use aliases for similar agents** (broker_ib → broker)
2. **Create new agents for unique functionality** (pdf, ocr, seo, etc.)
3. **Connector agents route to specialized implementations**

---

## **3. Implementation Plan:**

### **Phase 1: Add Alias Routing (Immediate)** ✅

```python
# In Apollo/agents/__init__.py

AGENT_ALIASES = {
    # Broker aliases -> generic broker
    'broker_ib': 'broker',
    'broker_td': 'broker',
    'broker_schwab': 'broker',
    'broker_alpaca': 'broker',
    
    # Exchange aliases -> generic exchange
    'exchange_binance': 'exchange',
    'exchange_coinbase': 'exchange',
    'exchange_kraken': 'exchange',
    
    # Development aliases
    'code': 'codereview',
    'devops': 'deployment',
    
    # Document aliases
    'pdf': 'document',
    'ocr': 'document',
    'notion': 'document',
    'drive': 'document',
    
    # Business aliases
    'crm': 'sales',
    'analytics': 'data',
    'business_strategy': 'strategy',
    'operations': 'project',
    
    # Insurance aliases
    'claims': 'insurance',
    
    # Media aliases
    'image': 'vision',
    'content': 'text',
    
    # Analytics aliases
    'metrics': 'data',
    'forecast': 'data',
    'report': 'data',
    'ml': 'data',
    
    # Web aliases
    'web': 'scraper',
    'seo': 'scraper',
    
    # Web3 aliases
    'blockchain': 'crypto',
    'defi': 'crypto',
    
    # Communication aliases
    'teams': 'slack',
}

def get_agent(agent_name: str) -> BaseAgent:
    """Get an agent instance by name, with alias support"""
    # Check for alias first
    resolved_name = AGENT_ALIASES.get(agent_name, agent_name)
    
    agent_class = AGENT_REGISTRY.get(resolved_name)
    if not agent_class:
        raise ValueError(f"Unknown agent: {agent_name} (resolved to: {resolved_name})")
    return agent_class()
```

### **Phase 2: Connector Routing (Already Done)** ✅

The connector agents (ib_connector, td_connector, etc.) provide platform-specific guidance and route to the appropriate backend agent.

### **Phase 3: Market Data Connectors (Future)** ⏳

The 24 market data connectors in the frontend can:
1. Route to existing agents (exchange, data)
2. Provide platform-specific documentation
3. Be implemented as needed

---

## **4. Routing Flow:**

```
User selects agent in Atlas UI
    ↓
Frontend sends request with agent_id (e.g., "broker_ib")
    ↓
Apollo receives request
    ↓
Check AGENT_ALIASES for mapping
    ↓
If alias exists: Use mapped agent (e.g., "broker")
If no alias: Use agent_id directly
    ↓
Get agent from AGENT_REGISTRY
    ↓
Process request and return response
```

---

## **5. Benefits of This Approach:**

### **Alias Mapping:**
- ✅ Immediate solution
- ✅ No new code needed
- ✅ Maintains frontend flexibility
- ✅ Backend stays focused

### **Specialized Connectors:**
- ✅ Platform-specific guidance
- ✅ Better user experience
- ✅ Can be added incrementally

### **Hybrid:**
- ✅ Best of both worlds
- ✅ Scalable
- ✅ Maintainable

---

## **6. Testing Strategy:**

```python
# Test alias resolution
assert get_agent('broker_ib').name == 'Broker Agent'
assert get_agent('broker_td').name == 'Broker Agent'
assert get_agent('exchange_binance').name == 'Exchange Agent'

# Test direct agents
assert get_agent('ledger').name == 'Ledger Agent'
assert get_agent('email').name == 'Email Agent'

# Test connectors
assert get_agent('ib_connector').name == 'IB Connector'
```

---

## **7. Documentation for Frontend:**

Update `apollo_client.rs` to document the mapping:

```rust
// Agent IDs that map to backend agents:
// - broker_ib, broker_td, broker_schwab, broker_alpaca -> broker
// - exchange_binance, exchange_coinbase, exchange_kraken -> exchange
// - code -> codereview
// - devops -> deployment
// etc.
```

---

## **8. Next Steps:**

1. ✅ **Add AGENT_ALIASES to Apollo** (5 minutes)
2. ✅ **Update get_agent() function** (5 minutes)
3. ✅ **Test alias resolution** (10 minutes)
4. ⏳ **Document mapping in Atlas** (10 minutes)
5. ⏳ **Add remaining connector agents** (as needed)

---

## **Recommendation:**

**Implement Phase 1 (Alias Routing) immediately.** This ensures all 117 frontend agents can route to appropriate backend agents without building 44 new agents. The connector agents already provide platform-specific guidance, so the alias system handles the rest.

**Total time: ~30 minutes to implement and test** ✅

This maintains the separation between:
- **Atlas**: User-facing agent list (comprehensive)
- **Apollo**: Processing agents (focused)
- **Routing**: Intelligent mapping between them

---

**Ready to implement?** Let me know and I'll add the alias mapping to Apollo!
