# 🎯 Agent Filtering Architecture

**Context-aware agent visibility based on entity type and user needs**

---

## 🎭 The Problem

**Example Scenario:**
- User manages "Atlas LLC" (business entity)
- Needs: QuickBooks, Jira, GitHub, HR, Marketing
- Doesn't need: Apple Health, Strava, Nike Run Club, MyFitnessPal

**Without filtering:** User sees all 108 agents (overwhelming, irrelevant)  
**With filtering:** User sees only 30 relevant business agents (focused, useful)

---

## 🏗️ Solution: Entity-Aware Agent Metadata

### **Agent Metadata Structure:**

```python
class AgentMetadata:
    name: str
    layer: AgentLayer
    version: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    
    # Filtering metadata
    entity_types: List[EntityType]  # Who can use this agent?
    app_contexts: List[AppContext]  # Which apps can use this?
    tier_requirements: Dict[str, str]  # What tier is required?
    required_integrations: List[str]  # What integrations are needed?

class EntityType(Enum):
    PERSONAL = "personal"  # Individual person
    BUSINESS = "business"  # Any business entity
    TRADING_FIRM = "trading_firm"  # Trading/investment firms
    UNIVERSAL = "universal"  # Everyone (email, calendar, etc.)

class AppContext(Enum):
    ATLAS = "atlas"  # Atlas (business/personal management)
    DELT = "delt"  # Delt (trading platform)
    AKASHIC = "akashic"  # Akashic (code/development)
    ALL = "all"  # All apps
```

---

## 📋 Agent Categorization Examples

### **Universal Agents (Everyone needs these):**

```python
GmailParserAgent:
    entity_types: [UNIVERSAL]
    app_contexts: [ATLAS, ALL]
    tier_requirements: {"atlas": "free"}
    # Visible to: Everyone

GCalConnectorAgent:
    entity_types: [UNIVERSAL]
    app_contexts: [ATLAS, ALL]
    tier_requirements: {"atlas": "free"}
    # Visible to: Everyone

SlackParserAgent:
    entity_types: [UNIVERSAL]
    app_contexts: [ATLAS, ALL]
    tier_requirements: {"atlas": "free"}
    # Visible to: Everyone
```

### **Personal-Only Agents (Individual users):**

```python
AppleHealthConnectorAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "free"}
    required_integrations: ["apple_health"]
    # Visible to: Personal entities only

StravaConnectorAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "free"}
    required_integrations: ["strava"]
    # Visible to: Personal entities only

NikeRunClubConnectorAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "free"}
    required_integrations: ["nike_run_club"]
    # Visible to: Personal entities only

MyFitnessPalConnectorAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "pro"}
    required_integrations: ["myfitnesspal"]
    # Visible to: Personal entities with Pro tier

HealthFitnessParserAgent:
    entity_types: [PERSONAL]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "free"}
    dependencies: ["apple_health_connector", "strava_connector"]
    # Visible to: Personal entities only
```

### **Business-Only Agents:**

```python
QuickBooksConnectorAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "business"}
    required_integrations: ["quickbooks"]
    # Visible to: Business entities only

HRAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "business"}
    # Visible to: Business entities only

MarketingAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "business"}
    # Visible to: Business entities only

SalesAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "business"}
    # Visible to: Business entities only

CustomerSupportAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "business"}
    # Visible to: Business entities only

HiringWorkflowAgent:
    entity_types: [BUSINESS]
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "business"}
    # Visible to: Business entities only
```

### **Trading Firm Agents:**

```python
AlpacaConnectorAgent:
    entity_types: [TRADING_FIRM]
    app_contexts: [DELT]
    tier_requirements: {"delt": "trader"}
    required_integrations: ["alpaca"]
    # Visible to: Trading firms only

TradingStrategyAgent:
    entity_types: [TRADING_FIRM]
    app_contexts: [DELT]
    tier_requirements: {"delt": "trader"}
    # Visible to: Trading firms only

PortfolioAgent:
    entity_types: [TRADING_FIRM, BUSINESS]  # Both can use
    app_contexts: [DELT, ATLAS]
    tier_requirements: {"delt": "trader", "atlas": "business"}
    # Visible to: Trading firms and businesses
```

### **Multi-Entity Agents (Shared):**

```python
JiraConnectorAgent:
    entity_types: [BUSINESS, PERSONAL]  # Both can use
    app_contexts: [ATLAS]
    tier_requirements: {"atlas": "pro"}
    required_integrations: ["jira"]
    # Visible to: Business entities and personal users with Jira

GitHubConnectorAgent:
    entity_types: [BUSINESS, PERSONAL]  # Both can use
    app_contexts: [ATLAS, AKASHIC]
    tier_requirements: {"atlas": "free", "akashic": "free"}
    required_integrations: ["github"]
    # Visible to: Anyone with GitHub integration

CodeReviewAgent:
    entity_types: [BUSINESS, PERSONAL]  # Both can use
    app_contexts: [AKASHIC]
    tier_requirements: {"akashic": "free"}
    # Visible to: Anyone using Akashic
```

---

## 🎬 Real-World Scenarios

### **Scenario 1: Atlas LLC (Business Entity)**

**Entity:** Atlas LLC  
**Type:** BUSINESS  
**App:** Atlas  
**Tier:** Business  
**Integrations:** QuickBooks, Jira, GitHub, Slack, Gmail

**Agents Visible (30 agents):**
- ✅ Universal: Gmail, Calendar, Slack, GitHub
- ✅ Business: QuickBooks, HR, Marketing, Sales, Customer Support
- ✅ PM Tools: Jira, Linear, GitHub Projects
- ✅ Finance: Stripe, TurboTax, Plaid
- ✅ Workflows: Invoice, Meeting, Hiring, Compliance
- ❌ Personal: Apple Health, Strava, Nike Run Club, MyFitnessPal
- ❌ Trading: Alpaca, Trading Strategy, Portfolio (unless also tagged BUSINESS)

### **Scenario 2: Personal User (Individual)**

**Entity:** Jacob Leonard (Personal)  
**Type:** PERSONAL  
**App:** Atlas  
**Tier:** Pro  
**Integrations:** Gmail, Apple Health, Spotify, Strava

**Agents Visible (40 agents):**
- ✅ Universal: Gmail, Calendar, Slack
- ✅ Personal: Apple Health, Strava, Nike Run Club, MyFitnessPal
- ✅ Media: Spotify, YouTube
- ✅ Travel: Google Maps, Uber, Airbnb
- ✅ Shopping: Amazon, Subscriptions
- ✅ Storage: Google Drive, Dropbox, iCloud
- ✅ Social: Twitter, LinkedIn
- ❌ Business: QuickBooks, HR, Marketing, Sales
- ❌ Trading: All trading agents

### **Scenario 3: AckwardRootsInc (Trading Firm)**

**Entity:** AckwardRootsInc  
**Type:** TRADING_FIRM  
**App:** Delt  
**Tier:** Trader  
**Integrations:** Alpaca, Binance, Polygon, QuickBooks

**Agents Visible (50 agents):**
- ✅ Universal: Gmail, Calendar, Slack
- ✅ Trading: All 27 exchange connectors, 4 brokerages
- ✅ Finance: Trading Strategy, Portfolio, Options, Futures, Arbitrage
- ✅ Market Data: Polygon, Finnhub, AlphaVantage
- ✅ News: Bloomberg, Reuters, CNBC, Forbes (for trading insights)
- ✅ Business: QuickBooks (for accounting)
- ❌ Personal: Apple Health, Strava, Nike Run Club
- ❌ Travel: Google Maps, Uber, Airbnb

### **Scenario 4: Power User (Personal + Business)**

**Entity 1:** Jacob Leonard (Personal)  
**Entity 2:** Atlas LLC (Business)  
**Type:** PERSONAL + BUSINESS  
**App:** Atlas  
**Tier:** Pro + Business  

**Agents Visible (70 agents):**
- ✅ Universal: All universal agents
- ✅ Personal: All personal agents (when viewing Personal entity)
- ✅ Business: All business agents (when viewing Atlas LLC entity)
- ✅ Shared: GitHub, Jira, Notion (visible in both contexts)
- ❌ Trading: Still hidden (not a trading firm)

**Entity Switcher in UI:**
```
Current Entity: [Atlas LLC ▼]
├── Jacob Leonard (Personal)
└── Atlas LLC (Business)

When switching:
- Personal → Shows fitness, travel, shopping agents
- Business → Shows HR, marketing, sales agents
```

---

## 🔄 Filtering Logic

### **Meta-Orchestrator Filtering:**

```python
class MetaOrchestrator:
    def get_available_agents(
        self,
        entity_id: str,
        entity_type: EntityType,
        app_context: AppContext,
        tier: str,
        active_integrations: List[str]
    ) -> List[Agent]:
        
        available_agents = []
        
        for agent in self.all_agents:
            # 1. Check entity type
            if not self._matches_entity_type(agent, entity_type):
                continue
            
            # 2. Check app context
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
    
    def _matches_entity_type(self, agent: Agent, entity_type: EntityType) -> bool:
        return (
            EntityType.UNIVERSAL in agent.metadata.entity_types or
            entity_type in agent.metadata.entity_types
        )
    
    def _matches_app_context(self, agent: Agent, app_context: AppContext) -> bool:
        return (
            AppContext.ALL in agent.metadata.app_contexts or
            app_context in agent.metadata.app_contexts
        )
    
    def _meets_tier_requirement(
        self,
        agent: Agent,
        app_context: AppContext,
        user_tier: str
    ) -> bool:
        required_tier = agent.metadata.tier_requirements.get(app_context.value)
        if not required_tier:
            return True  # No tier requirement
        
        tier_hierarchy = ["free", "pro", "business", "enterprise"]
        return tier_hierarchy.index(user_tier) >= tier_hierarchy.index(required_tier)
    
    def _has_required_integrations(
        self,
        agent: Agent,
        active_integrations: List[str]
    ) -> bool:
        if not agent.metadata.required_integrations:
            return True  # No integrations required
        
        return all(
            integration in active_integrations
            for integration in agent.metadata.required_integrations
        )
```

---

## 📊 Agent Distribution by Entity Type

### **Personal Entities (40 agents):**
- Communication: Gmail, Calendar, iMessage, Telegram, Slack
- Health: Apple Health, Strava, Nike Run Club, MyFitnessPal
- Media: Spotify, YouTube
- Travel: Google Maps, Uber, Airbnb
- Shopping: Amazon, Subscriptions
- Storage: Google Drive, Dropbox, iCloud
- Social: Twitter, LinkedIn
- Parsers: Health, Travel, Shopping, Media

### **Business Entities (30 agents):**
- Finance: QuickBooks, Stripe, Plaid, TurboTax
- PM Tools: Jira, Linear, GitHub Projects, Asana, ClickUp
- Development: GitHub, Code Review, Code Generation
- Business: HR, Marketing, Sales, Product, Customer Support
- Workflows: Invoice, Meeting, Hiring, Compliance, Email Campaign
- Parsers: QuickBooks, Stripe, GitHub, Slack

### **Trading Firms (50 agents):**
- Exchanges: 27 crypto exchanges
- Brokerages: 4 stock brokerages
- Market Data: 10 data providers
- Trading: Strategy, Portfolio, Options, Futures, Arbitrage
- News: 8 financial news sources
- Parsers: Market data, news, trading

### **Universal (Everyone) (15 agents):**
- Gmail, Calendar, Slack, GitHub
- Document, Audio, Image, Video parsers
- Entity recognition agents
- Meta-orchestrator, Learning agent

---

## 🎯 Benefits

✅ **Focused Experience:** Users only see relevant agents  
✅ **Reduced Cognitive Load:** 30 agents instead of 108  
✅ **Better Onboarding:** Clear what's available for their use case  
✅ **Flexible:** Same user can have multiple entities (personal + business)  
✅ **Scalable:** Easy to add new entity types  
✅ **Self-Documenting:** Agent metadata declares its applicability  

---

## 🚀 Implementation Steps

1. **Update AgentMetadata class** with new fields
2. **Tag all 108 agents** with appropriate metadata
3. **Update Meta-Orchestrator** with filtering logic
4. **Atlas Frontend:** Entity switcher + filtered agent list
5. **Documentation:** Agent catalog by entity type

---

**Result:** Business users see business agents, personal users see personal agents, power users can switch between contexts!

**Status:** Ready to implement  
**Created:** October 30, 2025  
**Owner:** Apollo AI System
