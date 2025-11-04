# 🗺️ Agent Layer Mapping - All 133 Agents

## 📊 Layer Distribution

**Layer 1: Data Extraction (43 agents)** - All connectors
**Layer 2: Entity Recognition (12 agents)** - Analytics + Modern
**Layer 3: Domain Experts (62 agents)** - Finance, Business, Legal, etc.
**Layer 4: Workflow Orchestration (14 agents)** - Communication, Development, Web
**Layer 5: Meta-Orchestration (2 agents)** - Knowledge, Core

---

## 🔵 Layer 1: Data Extraction (43 agents)

**Purpose:** Extract data from external sources → structured format

### **Connectors - Brokerages (4)**
1. `IBConnectorAgent` - Interactive Brokers
2. `TDConnectorAgent` - TD Ameritrade
3. `SchwabConnectorAgent` - Charles Schwab
4. `AlpacaConnectorAgent` - Alpaca

### **Connectors - Exchanges (3)**
5. `BinanceConnectorAgent` - Binance
6. `CoinbaseConnectorAgent` - Coinbase
7. `KrakenConnectorAgent` - Kraken

### **Connectors - Financial (5)**
8. `QuickBooksConnectorAgent` - QuickBooks
9. `PlaidConnectorAgent` - Plaid
10. `StripeConnectorAgent` - Stripe
11. `InvestorProfilesConnectorAgent` - Investor data
12. `NewsSentimentConnectorAgent` - News feeds

### **Connectors - Communication (3)**
13. `GmailConnectorAgent` - Gmail
14. `GCalConnectorAgent` - Google Calendar
15. `SlackConnectorAgent` - Slack

### **Connectors - Productivity (4)**
16. `GitHubConnectorAgent` - GitHub
17. `NotionConnectorAgent` - Notion
18. `GDriveConnectorAgent` - Google Drive
19. `SpotifyConnectorAgent` - Spotify

### **Connectors - Market Data (24)**
20. `AlphavantageConnectorAgent`
21. `PolygonConnectorAgent`
22. `FinnhubConnectorAgent`
23. `TwelvedataConnectorAgent`
24. `DatabentoConnectorAgent`
25. `TradierConnectorAgent`
26. `BinanceusConnectorAgent`
27. `GeminiConnectorAgent`
28. `BitfinexConnectorAgent`
29. `BitstampConnectorAgent`
30. `BitgetConnectorAgent`
31. `BithumbConnectorAgent`
32. `BybitConnectorAgent`
33. `DeribitConnectorAgent`
34. `FtxConnectorAgent`
35. `FtxusConnectorAgent`
36. `GateioConnectorAgent`
37. `HuobiConnectorAgent`
38. `KucoinConnectorAgent`
39. `OkxConnectorAgent`
40. `PhemexConnectorAgent`
41. `UpbitConnectorAgent`
42. `CollectorsConnectorAgent`
43. `DEXCollectorConnectorAgent`

**All inherit from:** `Layer1Agent`
**Method:** `async def extract(self, raw_data) -> AgentResult`

---

## 🟢 Layer 2: Entity Recognition (12 agents)

**Purpose:** Identify entities, patterns, and relationships from structured data

### **Analytics (9)**
1. `DataAgent` - Extract data entities
2. `TextAgent` - Extract text entities (NER)
3. `SchemaAgent` - Recognize schema patterns
4. `RouterAgent` - Route classification
5. `MaterializeAgent` - Materialized view patterns
6. `ForecastAgent` - Pattern recognition for forecasting
7. `MetricsAgent` - Metric extraction
8. `MLAgent` - ML pattern recognition
9. `ReportAgent` - Report entity extraction

### **Modern (3)**
10. `SlangAgent` - Slang recognition
11. `MemeAgent` - Meme recognition
12. `SocialAgent` - Social entity recognition

**All inherit from:** `Layer2Agent`
**Method:** `async def recognize(self, structured_data) -> AgentResult`

---

## 🟡 Layer 3: Domain Experts (62 agents)

**Purpose:** Domain-specific analysis and expertise

### **Finance (20)**
1. `LedgerAgent` - Accounting analysis
2. `TaxAgent` - Tax analysis
3. `InvoiceAgent` - Invoice analysis
4. `BudgetAgent` - Budget analysis
5. `TradingAgent` - Trading analysis
6. `ForexAgent` - Forex analysis
7. `StocksAgent` - Stock analysis
8. `BrokerAgent` - Broker analysis
9. `AlpacaBrokerAgent` - Alpaca-specific
10. `IBBrokerAgent` - IB-specific
11. `SchwabBrokerAgent` - Schwab-specific
12. `TDBrokerAgent` - TD-specific
13. `ExchangeAgent` - Exchange analysis
14. `FinanceStrategyAgent` - Strategy analysis
15. `PortfolioAgent` - Portfolio analysis
16. `OptionsAgent` - Options analysis
17. `FuturesAgent` - Futures analysis
18. `ArbitrageAgent` - Arbitrage analysis
19. `SentimentAgent` - Sentiment analysis
20. `BacktestAgent` - Backtest analysis

### **Business (12)**
21. `GrantScraperAgent` - Grant research
22. `SalesAgent` - Sales analysis
23. `MarketingAgent` - Marketing analysis
24. `HRAgent` - HR analysis
25. `ProjectAgent` - Project analysis
26. `BusinessStrategyAgent` - Strategy analysis
27. `TravelAgent` - Travel analysis
28. `CharityAgent` - Charity analysis
29. `AnalyticsAgent` - Business analytics
30. `CRMAgent` - CRM analysis
31. `OperationsAgent` - Operations analysis
32. `ResearchAgent` - Research analysis ✅ Already exists!

### **Legal (4)**
33. `LegalAgent` - Legal analysis
34. `ContractAgent` - Contract analysis
35. `ComplianceAgent` - Compliance analysis
36. `IPAgent` - IP analysis

### **Documents (9)**
37. `DocumentAgent` - Document analysis
38. `KnowledgeAgent` - Knowledge extraction
39. `WikiAgent` - Wiki analysis
40. `TranslationAgent` - Translation
41. `DriveAgent` - Drive file analysis
42. `NotionAgent` - Notion analysis
43. `OCRAgent` - OCR analysis
44. `PDFAgent` - PDF analysis

### **Media (6)**
45. `VisionAgent` - Image analysis
46. `AudioAgent` - Audio analysis
47. `VideoAgent` - Video analysis
48. `MusicAgent` - Music analysis
49. `ContentAgent` - Content analysis
50. `ImageAgent` - Image analysis

### **Health (2)**
51. `NutritionAgent` - Nutrition analysis
52. `HealthAgent` - Health analysis

### **Insurance (3)**
53. `InsuranceAgent` - Insurance analysis
54. `RiskAgent` - Risk analysis
55. `ClaimsAgent` - Claims analysis

### **Web3 (5)**
56. `CryptoAgent` - Crypto analysis
57. `NFTAgent` - NFT analysis
58. `AuctionAgent` - Auction analysis
59. `BlockchainAgent` - Blockchain analysis
60. `DeFiAgent` - DeFi analysis

### **PM (1)**
61. `TicketRefinementAgent` - Ticket analysis

**All inherit from:** `Layer3Agent`
**Method:** `async def analyze(self, entities, context) -> AgentResult`

---

## 🟠 Layer 4: Workflow Orchestration (14 agents)

**Purpose:** Multi-step workflows coordinating multiple agents

### **Communication (5)**
1. `EmailAgent` - Email workflows
2. `CalendarAgent` - Calendar workflows
3. `ContactAgent` - Contact workflows
4. `SlackAgent` - Slack workflows
5. `TeamsAgent` - Teams workflows

### **Development (4)**
6. `GitHubAgent` - GitHub workflows
7. `CodeReviewAgent` - Code review workflows
8. `DeploymentAgent` - Deployment workflows
9. `APIAgent` - API workflows

### **Web (4)**
10. `ScraperAgent` - Scraping workflows
11. `IntegrationAgent` - Integration workflows
12. `SEOAgent` - SEO workflows
13. `WebAgent` - Web workflows

### **Workflow (1)**
14. `MeetingOrchestratorAgent` - Meeting workflows ✅ Already exists!

**All inherit from:** `Layer4Agent`
**Method:** `async def orchestrate(self, trigger) -> WorkflowResult`

---

## 🔴 Layer 5: Meta-Orchestration (2 agents)

**Purpose:** System-wide optimization and learning

### **Knowledge (2)**
1. `LearningAgent` - System learning
2. `KnowledgeBaseAgent` - Knowledge management

### **Core (1)**
3. `CoreAgent` - Meta-orchestration

**All inherit from:** `Layer5Agent`
**Method:** `async def optimize(self, system_state) -> Optimization`

---

## 🏗️ Infrastructure Agents (4 - Special)

**These are support agents, not in the main layers:**

1. `ConnectionMonitorAgent` - Monitor connections
2. `RateLimitManagerAgent` - Rate limiting
3. `APIVersionMonitorAgent` - API versioning
4. `WebhookManagerAgent` - Webhook management

**Keep in:** `agents/infrastructure/`

---

## 🔐 Platform Agents (1 - Special)

1. `UniversalVaultAgent` - Credential management

**Keep in:** `agents/` (root level)

---

## 📊 Summary

**Total: 133 agents**
- Layer 1: 43 agents (Data Extraction)
- Layer 2: 12 agents (Entity Recognition)
- Layer 3: 62 agents (Domain Experts)
- Layer 4: 14 agents (Workflow Orchestration)
- Layer 5: 2 agents (Meta-Orchestration)
- Infrastructure: 4 agents (Support)
- Platform: 1 agent (Vault)

---

## 🎯 Migration Priority

**Phase 1: Critical Agents (Week 1-2)**
1. `GmailConnectorAgent` → Layer 1
2. `QuickBooksConnectorAgent` → Layer 1
3. `PlaidConnectorAgent` → Layer 1
4. `TextAgent` → Layer 2
5. `ResearchAgent` → Layer 3 ✅
6. `MeetingOrchestratorAgent` → Layer 4 ✅

**Phase 2: High Priority (Week 3-4)**
7. All financial connectors → Layer 1
8. All analytics agents → Layer 2
9. All finance domain agents → Layer 3
10. All communication workflows → Layer 4

**Phase 3: Medium Priority (Week 5-6)**
11. All remaining connectors → Layer 1
12. All business domain agents → Layer 3
13. All development workflows → Layer 4

**Phase 4: Low Priority (Week 7-8)**
14. All remaining agents
15. Infrastructure agents (keep as-is)
16. Platform agents (keep as-is)

---

## 🔄 Backwards Compatibility

**All existing agents still work!**
- Legacy agents inherit from `BaseAgent`
- New agents inherit from `Layer1Agent`, `Layer2Agent`, etc.
- Factory supports both
- Registry supports both
- Gradual migration over time

**No breaking changes!** 🎉
