# 🎯 Agent Filtering - Refined Architecture

**Multi-dimensional filtering: Entity Type + App Context**

---

## 🤔 The Problem You Identified

**Scenario:**
- User: Jacob Leonard (Personal entity)
- Uses: Atlas (personal management) + Delt (personal investing)
- Problem: Trading agents would show in Atlas UI even though they're only relevant in Delt

**Current approach would show:**
```
Atlas Personal Dashboard:
- ✅ Gmail, Calendar, Health, Spotify (correct)
- ❌ Trading agents (wrong! These are for Delt, not Atlas)
```

**What we actually want:**
```
Atlas Personal Dashboard:
- ✅ Gmail, Calendar, Health, Spotify
- ❌ Trading agents (hidden - only show in Delt)

Delt Personal Dashboard:
- ✅ Trading agents, market data, portfolio
- ❌ Health, travel, shopping (hidden - only show in Atlas)
```

---

## ✅ Solution: Multi-Dimensional Filtering

### **Filter by BOTH entity_type AND app_context:**

```python
class AgentMetadata:
    # Dimension 1: Who can use this? (Entity Type)
    entity_types: List[EntityType]  # [PERSONAL, BUSINESS, TRADING_FIRM, UNIVERSAL]
    
    # Dimension 2: Where can they use it? (App Context)
    app_contexts: List[AppContext]  # [ATLAS, DELT, AKASHIC, ALL]
    
    # Dimension 3: What tier do they need?
    tier_requirements: Dict[str, str]  # {"atlas": "free", "delt": "trader"}
    
    # Dimension 4: What integrations are required?
    required_integrations: List[str]  # ["plaid", "alpaca"]
```

---

## 📋 Corrected Agent Categorization

### **Personal + Atlas (Personal Management):**

```python
AppleHealthConnectorAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]  # Only in Atlas
    tier_requirements: {"atlas": "free"}
    # Shows in: Atlas Personal
    # Hides in: Delt Personal

StravaConnectorAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]  # Only in Atlas
    tier_requirements: {"atlas": "free"}
    # Shows in: Atlas Personal
    # Hides in: Delt Personal

GoogleMapsConnectorAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]  # Only in Atlas
    tier_requirements: {"atlas": "free"}
    # Shows in: Atlas Personal
    # Hides in: Delt Personal

ShoppingParserAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]  # Only in Atlas
    tier_requirements: {"atlas": "free"}
    # Shows in: Atlas Personal
    # Hides in: Delt Personal
```

### **Personal + Delt (Personal Investing):**

```python
AlpacaConnectorAgent:
    entity_types: [PERSONAL, TRADING_FIRM]  # Both can use
    app_contexts: [DELT]  # Only in Delt
    tier_requirements: {"delt": "trader"}
    # Shows in: Delt Personal, Delt Trading Firm
    # Hides in: Atlas Personal, Atlas Business

TradingStrategyAgent:
    entity_types: [PERSONAL, TRADING_FIRM]  # Both can use
    app_contexts: [DELT]  # Only in Delt
    tier_requirements: {"delt": "trader"}
    # Shows in: Delt Personal, Delt Trading Firm
    # Hides in: Atlas Personal, Atlas Business

PortfolioAgent:
    entity_types: [PERSONAL, TRADING_FIRM]  # Both can use
    app_contexts: [DELT]  # Only in Delt
    tier_requirements: {"delt": "trader"}
    # Shows in: Delt Personal, Delt Trading Firm
    # Hides in: Atlas Personal, Atlas Business

BinanceConnectorAgent:
    entity_types: [PERSONAL, TRADING_FIRM]  # Both can use
    app_contexts: [DELT]  # Only in Delt
    tier_requirements: {"delt": "trader"}
    # Shows in: Delt Personal, Delt Trading Firm
    # Hides in: Atlas Personal, Atlas Business
```

### **Universal (All Apps):**

```python
GmailParserAgent:
    entity_types: [UNIVERSAL]
    app_contexts: [ALL]  # Shows everywhere
    tier_requirements: {"atlas": "free", "delt": "free", "akashic": "free"}
    # Shows in: Atlas Personal, Atlas Business, Delt Personal, Delt Trading, Akashic

GCalConnectorAgent:
    entity_types: [UNIVERSAL]
    app_contexts: [ALL]  # Shows everywhere
    tier_requirements: {"atlas": "free", "delt": "free", "akashic": "free"}
    # Shows in: All contexts

SlackParserAgent:
    entity_types: [UNIVERSAL]
    app_contexts: [ALL]  # Shows everywhere
    tier_requirements: {"atlas": "free", "delt": "free", "akashic": "free"}
    # Shows in: All contexts
```

### **Business + Atlas (Business Management):**

```python
QuickBooksConnectorAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]  # Only in Atlas
    tier_requirements: {"atlas": "business"}
    # Shows in: Atlas Business
    # Hides in: Atlas Personal, Delt

HRAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]  # Only in Atlas
    tier_requirements: {"atlas": "business"}
    # Shows in: Atlas Business
    # Hides in: Atlas Personal, Delt

MarketingAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]  # Only in Atlas
    tier_requirements: {"atlas": "business"}
    # Shows in: Atlas Business
    # Hides in: Atlas Personal, Delt
```

### **Cross-App Agents (Development):**

```python
GitHubConnectorAgent:
    entity_types: [PERSONAL, BUSINESS]
    app_contexts: [ATLAS, AKASHIC]  # Both Atlas and Akashic
    tier_requirements: {"atlas": "free", "akashic": "free"}
    # Shows in: Atlas Personal, Atlas Business, Akashic
    # Hides in: Delt

CodeReviewAgent:
    entity_types: [PERSONAL, BUSINESS]
    app_contexts: [AKASHIC]  # Only in Akashic
    tier_requirements: {"akashic": "free"}
    # Shows in: Akashic
    # Hides in: Atlas, Delt

CodeGenerationAgent:
    entity_types: [PERSONAL, BUSINESS]
    app_contexts: [AKASHIC]  # Only in Akashic
    tier_requirements: {"akashic": "free"}
    # Shows in: Akashic
    # Hides in: Atlas, Delt
```

---

## 🎬 Corrected Real-World Scenarios

### **Scenario 1: Personal User with Atlas + Delt**

**User:** Jacob Leonard  
**Entity Type:** PERSONAL  
**Apps:** Atlas + Delt  
**Tiers:** Atlas Pro + Delt Trader  

**Atlas Personal Dashboard (20 agents):**
- ✅ Universal: Gmail, Calendar, Slack
- ✅ Personal + Atlas: Apple Health, Strava, Spotify, Google Maps, Uber, Airbnb, Amazon
- ✅ Cross-app: GitHub (for personal projects)
- ❌ Trading: All hidden (only show in Delt)
- ❌ Business: All hidden (not a business entity)

**Delt Personal Dashboard (35 agents):**
- ✅ Universal: Gmail, Calendar, Slack
- ✅ Personal + Delt: All trading agents, exchanges, brokerages, market data
- ✅ Trading: Portfolio, Strategy, Options, Futures, Arbitrage
- ❌ Health/Travel: All hidden (only show in Atlas)
- ❌ Business: All hidden (not a business entity)

### **Scenario 2: Business Entity (Atlas Only)**

**Entity:** Atlas LLC  
**Entity Type:** BUSINESS  
**Apps:** Atlas  
**Tier:** Business  

**Atlas Business Dashboard (30 agents):**
- ✅ Universal: Gmail, Calendar, Slack
- ✅ Business + Atlas: QuickBooks, HR, Marketing, Sales, Jira, GitHub
- ✅ Workflows: Invoice, Hiring, Compliance, Email Campaign
- ❌ Personal: All hidden (not a personal entity)
- ❌ Trading: All hidden (not using Delt)

### **Scenario 3: Trading Firm (Delt Only)**

**Entity:** AckwardRootsInc  
**Entity Type:** TRADING_FIRM  
**Apps:** Delt  
**Tier:** Enterprise  

**Delt Trading Firm Dashboard (50 agents):**
- ✅ Universal: Gmail, Calendar, Slack
- ✅ Trading Firm + Delt: All 27 exchanges, 4 brokerages, market data
- ✅ Trading: Portfolio, Strategy, Options, Futures, Arbitrage, Sentiment
- ✅ News: Bloomberg, Reuters (for trading insights)
- ❌ Personal: All hidden (not a personal entity)
- ❌ Business: HR, Marketing hidden (not using Atlas)

### **Scenario 4: Power User (Personal + Business, Atlas + Delt)**

**Entities:** Jacob Leonard (Personal) + Atlas LLC (Business)  
**Apps:** Atlas + Delt  
**Tiers:** All tiers  

**UI with Entity + App Switcher:**
```
Current Context: [Jacob Leonard (Personal) ▼] in [Atlas ▼]

Entity Selector:
├── Jacob Leonard (Personal)
│   ├── Atlas → Shows personal + Atlas agents (20)
│   └── Delt → Shows personal + Delt agents (35)
└── Atlas LLC (Business)
    └── Atlas → Shows business + Atlas agents (30)
```

**Jacob Leonard (Personal) in Atlas:**
- Health, travel, shopping, personal management
- NO trading agents (those are in Delt)

**Jacob Leonard (Personal) in Delt:**
- Trading, portfolio, market data
- NO health/travel agents (those are in Atlas)

**Atlas LLC (Business) in Atlas:**
- QuickBooks, HR, marketing, business management
- NO personal or trading agents

---

## 🔄 Updated Filtering Logic

```python
class MetaOrchestrator:
    def get_available_agents(
        self,
        entity_id: str,
        entity_type: EntityType,
        app_context: AppContext,  # NEW: Which app are they using?
        tier: str,
        active_integrations: List[str]
    ) -> List[Agent]:
        
        available_agents = []
        
        for agent in self.all_agents:
            # 1. Check entity type
            if not self._matches_entity_type(agent, entity_type):
                continue
            
            # 2. Check app context (NEW!)
            if not self._matches_app_context(agent, app_context):
                continue
            
            # 3. Check tier requirement
            if not self._meets_tier_requirement(agent, app_context, tier):
                continue
            
            # 4. Check required integrations
            if not self._has_required_integrations(agent, active_integrations):
                continue
            
            available_agents.append(agent)
        
        return available_agents
    
    def _matches_app_context(self, agent: Agent, app_context: AppContext) -> bool:
        """NEW: Filter by app context"""
        return (
            AppContext.ALL in agent.metadata.app_contexts or
            app_context in agent.metadata.app_contexts
        )
```

---

## 📊 Agent Distribution by Entity + App

### **Personal + Atlas (20 agents):**
- Communication: Gmail, Calendar, iMessage, Telegram, Slack
- Health: Apple Health, Strava, Nike Run Club, MyFitnessPal
- Media: Spotify, YouTube
- Travel: Google Maps, Uber, Airbnb
- Shopping: Amazon, Subscriptions
- Storage: Google Drive, Dropbox, iCloud
- Social: Twitter, LinkedIn

### **Personal + Delt (35 agents):**
- Communication: Gmail, Calendar, Slack
- Trading: All exchanges, brokerages, market data
- Portfolio: Strategy, Options, Futures, Arbitrage
- News: Bloomberg, Reuters, CNBC (for trading)

### **Business + Atlas (30 agents):**
- Communication: Gmail, Calendar, Slack
- Finance: QuickBooks, Stripe, Plaid, TurboTax
- PM Tools: Jira, Linear, GitHub Projects
- Business: HR, Marketing, Sales, Customer Support
- Workflows: Invoice, Hiring, Compliance

### **Trading Firm + Delt (50 agents):**
- Communication: Gmail, Calendar, Slack
- Trading: All exchanges, brokerages, market data
- Portfolio: Strategy, Options, Futures, Arbitrage
- News: All financial news sources
- Finance: QuickBooks (for accounting)

### **Universal (All Contexts) (10 agents):**
- Gmail, Calendar, Slack, GitHub
- Document, Audio, Image, Video parsers
- Entity recognition agents
- Meta-orchestrator

---

## 🎯 Key Insight

**Two-dimensional filtering:**
1. **Entity Type** (Who): Personal, Business, Trading Firm
2. **App Context** (Where): Atlas, Delt, Akashic

**Result:**
- Personal user in Atlas: Sees health/travel agents, NOT trading agents
- Personal user in Delt: Sees trading agents, NOT health/travel agents
- Business in Atlas: Sees business agents, NOT personal or trading agents

**This solves your exact concern - trading agents only show in Delt, not in Atlas!** ✅

---

**Status:** Architecture refined with app context filtering  
**Created:** October 30, 2025  
**Owner:** Apollo AI System
