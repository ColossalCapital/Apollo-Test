# 🎯 Agent Filtering - Final Architecture

**Atlas as Master Control Plane for All Apps**

---

## 🏗️ The Real Architecture

### **Atlas = Master Control Plane**
- **Atlas UI** controls what data/agents user has access to across ALL apps
- **Delt** shows all available data (no filtering by subscription)
- **Akashic** shows all available data (no filtering by subscription)
- **Subscription/Access Control** happens in Atlas, not in individual apps

### **Key Insight:**
> "Atlas is the UI that controls what data the user has access to in Akashic and therefore in Delt on an investor level"

---

## 🎬 How It Actually Works

### **Scenario 1: User Signs Up for Delt**

**User:** Jacob Leonard  
**Subscription:** Atlas Pro + Delt Trader  

**What Happens:**
1. User subscribes to Delt in Atlas
2. **Trading agents appear in Atlas UI** (not in Delt!)
3. Atlas shows: "You now have access to trading agents"
4. User can configure trading agents in Atlas
5. Delt shows ALL available data (no subscription filtering)

**Atlas Dashboard (with Delt subscription):**
```
Personal Agents:
├── Health & Fitness (4 agents)
├── Travel (3 agents)
├── Shopping (2 agents)
└── Trading (35 agents) ← NEW! Appeared after Delt subscription
    ├── Exchanges (27 agents)
    ├── Brokerages (4 agents)
    └── Trading Strategies (4 agents)
```

**Delt Dashboard:**
```
Shows: ALL available market data
- No subscription filtering
- No agent filtering
- Just pure data access
```

---

## 🔑 BYOK (Bring Your Own Keys) Process

### **How Connector Agents Appear:**

**Option 1: User Subscribes to Delt**
1. User subscribes to Delt in Atlas
2. Trading agents appear in Atlas UI
3. Atlas prompts: "Connect your Alpaca account?"
4. User provides API keys in Atlas
5. Connector is configured
6. Data flows to Delt

**Option 2: User Does BYOK in Akashic**
1. User opens Akashic IDE
2. User writes trading strategy: `import alpaca`
3. Akashic detects: "You need Alpaca connector"
4. **Agent appears in Atlas UI** asking for keys
5. User provides API keys in Atlas
6. Connector is configured
7. Data flows to Akashic (and Delt if subscribed)

**Option 3: User Pays with WTF Coin**
1. User opens Akashic IDE
2. User wants premium data stream (e.g., Level 2 market data)
3. Akashic shows: "Pay 100 WTF/month for Polygon Level 2 data"
4. User pays with WTF coin
5. **Agent appears in Atlas UI** (already configured)
6. Data stream is enabled
7. Data flows to Akashic and Delt

---

## 📊 Agent Visibility Logic (Corrected)

### **Atlas UI (Master Control):**

```python
def get_visible_agents_in_atlas(user: User) -> List[Agent]:
    """
    Atlas shows agents based on:
    1. Entity type (personal vs business)
    2. Active subscriptions (Delt, Akashic)
    3. Connected integrations (BYOK)
    4. WTF coin purchases
    """
    visible_agents = []
    
    # 1. Always show universal agents
    visible_agents += get_universal_agents()
    
    # 2. Show agents for entity type
    if user.entity_type == PERSONAL:
        visible_agents += get_personal_agents()
    elif user.entity_type == BUSINESS:
        visible_agents += get_business_agents()
    
    # 3. Show agents for active subscriptions
    if user.has_subscription("delt"):
        visible_agents += get_trading_agents()  # Trading agents appear!
    
    if user.has_subscription("akashic"):
        visible_agents += get_code_agents()  # Code agents appear!
    
    # 4. Show agents for BYOK integrations
    for integration in user.byok_integrations:
        visible_agents += get_agents_for_integration(integration)
    
    # 5. Show agents for WTF coin purchases
    for data_stream in user.wtf_purchases:
        visible_agents += get_agents_for_data_stream(data_stream)
    
    return visible_agents
```

### **Delt UI (No Filtering):**

```python
def get_visible_data_in_delt(user: User) -> List[DataStream]:
    """
    Delt shows ALL available data.
    No subscription filtering.
    No agent filtering.
    """
    return get_all_market_data()  # Everything!
```

### **Akashic IDE (No Filtering):**

```python
def get_visible_data_in_akashic(user: User) -> List[DataStream]:
    """
    Akashic shows ALL available data.
    No subscription filtering.
    No agent filtering.
    
    BUT: Creating strategies with that data requires:
    - Connector agents (configured in Atlas)
    - OR WTF coin payment for data streams
    """
    return get_all_data_sources()  # Everything!
```

---

## 🎭 Real-World Examples

### **Example 1: Personal User, No Delt Subscription**

**User:** Jacob Leonard  
**Subscriptions:** Atlas Pro (no Delt)  
**Entity:** Personal  

**Atlas Dashboard:**
```
Available Agents (20):
├── Universal (5): Gmail, Calendar, Slack, GitHub, Document Parser
├── Personal (15): Health, Travel, Shopping, Media, Social
└── Trading (0): ❌ No trading agents (no Delt subscription)
```

**Delt:** Not accessible (no subscription)  
**Akashic:** Not accessible (no subscription)

---

### **Example 2: Personal User, Subscribes to Delt**

**User:** Jacob Leonard  
**Subscriptions:** Atlas Pro + Delt Trader  
**Entity:** Personal  

**Atlas Dashboard:**
```
Available Agents (55):
├── Universal (5): Gmail, Calendar, Slack, GitHub, Document Parser
├── Personal (15): Health, Travel, Shopping, Media, Social
└── Trading (35): ← NEW! Appeared after Delt subscription
    ├── Exchanges (27): Binance, Coinbase, Kraken, etc.
    ├── Brokerages (4): Alpaca, Interactive Brokers, TD, Schwab
    ├── Market Data (10): Polygon, Finnhub, AlphaVantage, etc.
    └── Trading Strategies (4): Portfolio, Options, Futures, Arbitrage

Status: "Not configured - Click to add API keys"
```

**Delt Dashboard:**
```
Market Data:
├── Stocks: ALL available (S&P 500, NASDAQ, etc.)
├── Crypto: ALL available (BTC, ETH, etc.)
├── Forex: ALL available
└── Commodities: ALL available

Note: No subscription filtering, shows everything
```

**Akashic:** Not accessible (no subscription)

---

### **Example 3: User Does BYOK in Akashic**

**User:** Jacob Leonard  
**Subscriptions:** Atlas Pro + Delt Trader + Akashic Pro  
**Action:** Writes trading strategy in Akashic  

**Akashic IDE:**
```python
# User writes this code:
from alpaca import AlpacaClient

client = AlpacaClient()  # Needs API keys!
```

**What Happens:**
1. Akashic detects: "You need Alpaca connector"
2. **Alpaca agent appears in Atlas UI** with prompt:
   ```
   🔑 Alpaca Connector Required
   
   Your Akashic strategy needs Alpaca API access.
   
   [Add API Keys] [Learn More]
   ```
3. User clicks "Add API Keys" in Atlas
4. User provides: API Key, Secret Key
5. Atlas configures AlpacaConnectorAgent
6. Akashic strategy can now run
7. Data flows to Delt automatically

**Atlas Dashboard (after BYOK):**
```
Trading Agents (35):
├── Alpaca Connector ✅ CONFIGURED
│   Status: Connected
│   Last sync: 2 minutes ago
│   [View Settings] [Disconnect]
├── Binance Connector ⚙️ NOT CONFIGURED
│   [Add API Keys]
└── ... (other agents)
```

---

### **Example 4: User Pays with WTF Coin**

**User:** Jacob Leonard  
**Subscriptions:** Atlas Pro + Akashic Pro  
**Action:** Wants premium data in Akashic  

**Akashic IDE:**
```python
# User wants Level 2 market data
from polygon import PolygonClient

client = PolygonClient(level2=True)  # Premium data!
```

**What Happens:**
1. Akashic shows: "Level 2 data requires premium subscription"
2. Akashic offers: "Pay 100 WTF/month for Polygon Level 2"
3. User pays with WTF coin
4. **Polygon Premium agent appears in Atlas UI** (already configured)
5. Data stream is enabled
6. Akashic strategy can now access Level 2 data
7. If user also has Delt, data appears there too

**Atlas Dashboard (after WTF payment):**
```
Market Data Agents:
├── Polygon Basic ✅ FREE (included with Delt)
├── Polygon Level 2 ✅ PREMIUM (100 WTF/month)
│   Status: Active
│   Renewal: Dec 1, 2025
│   [Manage Subscription]
└── ... (other agents)
```

---

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         ATLAS UI                            │
│                   (Master Control Plane)                    │
│                                                             │
│  Shows agents based on:                                     │
│  1. Entity type (personal/business)                         │
│  2. Active subscriptions (Delt, Akashic)                    │
│  3. BYOK integrations (user-provided keys)                  │
│  4. WTF coin purchases (premium data)                       │
│                                                             │
│  User configures agents here:                               │
│  - Add API keys (BYOK)                                      │
│  - Enable/disable agents                                    │
│  - Manage subscriptions                                     │
│  - Pay with WTF coin                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Controls access to:
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│     DELT     │    │   AKASHIC    │    │    APOLLO    │
│              │    │              │    │              │
│ Shows: ALL   │    │ Shows: ALL   │    │ Executes:    │
│ market data  │    │ data sources │    │ Configured   │
│              │    │              │    │ agents only  │
│ No filtering │    │ No filtering │    │              │
│ by sub level │    │ by sub level │    │ Based on     │
│              │    │              │    │ Atlas config │
│ Pure data    │    │ Pure IDE     │    │              │
│ visualization│    │ experience   │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 📋 Agent Metadata (Updated)

```python
class AgentMetadata:
    name: str
    layer: AgentLayer
    version: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    
    # Visibility in Atlas UI
    entity_types: List[EntityType]  # Who can see this?
    requires_subscription: List[str]  # ["delt", "akashic"]
    byok_enabled: bool  # Can user bring their own keys?
    wtf_purchasable: bool  # Can user pay with WTF coin?
    
    # Configuration
    required_credentials: List[str]  # ["api_key", "secret_key"]
    wtf_price_monthly: Optional[int]  # WTF coins per month
```

### **Example Agent Configurations:**

```python
AlpacaConnectorAgent:
    entity_types: [PERSONAL, TRADING_FIRM]
    requires_subscription: ["delt"]  # Appears when user subscribes to Delt
    byok_enabled: True  # User can provide their own keys
    wtf_purchasable: False  # Not available for WTF purchase
    required_credentials: ["api_key", "secret_key"]
    # Visibility: Shows in Atlas after Delt subscription OR Akashic BYOK

PolygonLevel2Agent:
    entity_types: [PERSONAL, TRADING_FIRM]
    requires_subscription: ["delt", "akashic"]
    byok_enabled: False  # Must pay with WTF
    wtf_purchasable: True  # Available for WTF purchase
    wtf_price_monthly: 100  # 100 WTF/month
    # Visibility: Shows in Atlas after WTF payment

AppleHealthConnectorAgent:
    entity_types: [PERSONAL]
    requires_subscription: []  # Always available for personal users
    byok_enabled: False  # Uses HealthKit, no keys needed
    wtf_purchasable: False
    # Visibility: Always shows in Atlas for personal users
```

---

## 🎯 Key Principles

### **1. Atlas = Single Source of Truth**
- All agent configuration happens in Atlas
- All subscription management happens in Atlas
- All BYOK happens in Atlas
- All WTF purchases happen in Atlas

### **2. Delt = Pure Data Visualization**
- Shows ALL available market data
- No subscription filtering
- No agent configuration
- Just charts, analysis, and trading

### **3. Akashic = Pure IDE Experience**
- Shows ALL available data sources
- No subscription filtering
- No agent configuration (happens in Atlas)
- Just code, strategies, and backtesting

### **4. Apollo = Execution Engine**
- Executes only configured agents
- Respects Atlas configuration
- No UI for agent management
- Pure backend execution

---

## 🚀 User Journey Examples

### **Journey 1: New User → Delt Subscriber**

1. User signs up for Atlas (personal)
2. Atlas shows: 20 personal agents (health, travel, shopping)
3. User subscribes to Delt
4. **35 trading agents appear in Atlas UI**
5. Atlas prompts: "Connect your Alpaca account to start trading"
6. User adds Alpaca API keys in Atlas
7. Alpaca connector is configured
8. User opens Delt → Sees ALL market data
9. User can now trade with Alpaca through Delt

### **Journey 2: Developer → Akashic BYOK**

1. User signs up for Atlas + Akashic
2. User writes trading strategy in Akashic
3. Strategy imports: `from binance import BinanceClient`
4. Akashic detects: "Binance connector needed"
5. **Binance agent appears in Atlas UI**
6. User adds Binance API keys in Atlas
7. Binance connector is configured
8. Strategy can now run in Akashic
9. If user also has Delt, Binance data appears there too

### **Journey 3: Power User → WTF Premium Data**

1. User has Atlas + Delt + Akashic
2. User wants Level 2 market data for strategies
3. Akashic shows: "Pay 100 WTF/month for Polygon Level 2"
4. User pays with WTF coin
5. **Polygon Level 2 agent appears in Atlas UI** (configured)
6. Premium data stream is enabled
7. Data flows to both Akashic and Delt
8. User can now build strategies with Level 2 data

---

## 📊 Summary Table

| Location | Shows Agents? | Filters by Subscription? | Configuration? |
|----------|---------------|-------------------------|----------------|
| **Atlas** | ✅ YES | ✅ YES | ✅ YES (master control) |
| **Delt** | ❌ NO | ❌ NO | ❌ NO (pure data) |
| **Akashic** | ❌ NO | ❌ NO | ❌ NO (pure IDE) |
| **Apollo** | ❌ NO | N/A | ❌ NO (execution only) |

---

**Status:** Final architecture with Atlas as master control plane  
**Created:** October 30, 2025  
**Owner:** Apollo AI System
