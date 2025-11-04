# Apollo Agent Categorization Guide

**Total Agents: 133**

This document provides the complete categorization of all Apollo agents to improve Meta-Orchestrator routing and agent selection.

---

## 🏗️ Infrastructure (4 agents)
*System monitoring and management*

- `connection_monitor` - Monitor API connections and health
- `rate_limit_manager` - Manage API rate limits
- `api_version_monitor` - Track API version compatibility
- `webhook_manager` - Manage webhook subscriptions

---

## 🔌 Connectors (43 agents)

### Brokerages (4 agents)
*Trading platform integrations*

- `ib_connector` - Interactive Brokers
- `td_connector` - TD Ameritrade
- `schwab_connector` - Charles Schwab
- `alpaca_connector` - Alpaca Markets

### Exchanges (3 agents)
*Major crypto exchanges*

- `binance_connector` - Binance
- `coinbase_connector` - Coinbase
- `kraken_connector` - Kraken

### Market Data (24 agents)
*Real-time and historical market data*

- `alphavantage_connector` - Alpha Vantage (stocks, forex, crypto)
- `polygon_connector` - Polygon.io (stocks, options, forex)
- `finnhub_connector` - Finnhub (stocks, forex, crypto)
- `twelvedata_connector` - Twelve Data (stocks, forex, crypto)
- `databento_connector` - Databento (institutional data)
- `tradier_connector` - Tradier (stocks, options)
- `binanceus_connector` - Binance US
- `gemini_connector` - Gemini
- `bitfinex_connector` - Bitfinex
- `bitstamp_connector` - Bitstamp
- `bitget_connector` - Bitget
- `bithumb_connector` - Bithumb
- `bybit_connector` - Bybit
- `deribit_connector` - Deribit (derivatives)
- `ftx_connector` - FTX (historical)
- `ftxus_connector` - FTX US (historical)
- `gateio_connector` - Gate.io
- `huobi_connector` - Huobi
- `kucoin_connector` - KuCoin
- `okx_connector` - OKX
- `phemex_connector` - Phemex
- `upbit_connector` - Upbit
- `collectors_connector` - Multi-source aggregator
- `dex_collector_connector` - DEX data aggregator

### Financial Services (5 agents)
*Financial data and services*

- `quickbooks_connector` - QuickBooks accounting
- `plaid_connector` - Plaid bank connections
- `stripe_connector` - Stripe payments
- `investor_profiles_connector` - Investor profile data
- `news_sentiment_connector` - Financial news sentiment

### Communication (3 agents)
*Email, calendar, messaging*

- `gmail_connector` - Gmail integration
- `gcal_connector` - Google Calendar
- `slack_connector` - Slack workspace

### Productivity (4 agents)
*Documents, code, storage*

- `github_connector` - GitHub repositories
- `notion_connector` - Notion workspace
- `gdrive_connector` - Google Drive
- `spotify_connector` - Spotify (for media/audio)

---

## 💬 Communication (5 agents)
*Direct communication tools*

- `email` - Email composition and management
- `calendar` - Calendar scheduling
- `contact` - Contact management
- `slack` - Slack messaging
- `teams` - Microsoft Teams

---

## 💻 Development (4 agents)
*Software development tools*

- `github` - GitHub operations (repos, PRs, issues)
- `code_review` - Code review and analysis
- `deployment` - Deployment automation
- `api` - API design and testing

---

## 📄 Documents (9 agents)
*Document processing and management*

- `document` - General document processing
- `knowledge` - Knowledge base management
- `wiki` - Wiki creation and management
- `research` - Research and citation
- `translation` - Document translation
- `drive` - Cloud storage management
- `notion` - Notion document operations
- `ocr` - Optical character recognition
- `pdf` - PDF processing and generation

---

## 💰 Finance (16 agents)
*Financial analysis and trading*

- `ledger` - Accounting and bookkeeping
- `tax` - Tax calculation and filing
- `invoice` - Invoice generation
- `budget` - Budget planning and tracking
- `trading` - Trading execution
- `forex` - Foreign exchange
- `stocks` - Stock analysis
- `broker` - Brokerage operations
- `exchange` - Exchange operations
- `finance_strategy` - Financial strategy
- `portfolio` - Portfolio management
- `options` - Options trading
- `futures` - Futures trading
- `arbitrage` - Arbitrage opportunities
- `sentiment` - Market sentiment analysis
- `backtest` - Strategy backtesting

---

## ⚖️ Legal (4 agents)
*Legal and compliance*

- `legal` - General legal assistance
- `contract` - Contract review and generation
- `compliance` - Regulatory compliance
- `ip` - Intellectual property

---

## 🏢 Business (12 agents)
*Business operations*

- `grant` - Grant discovery and applications
- `sales` - Sales automation
- `marketing` - Marketing campaigns
- `hr` - Human resources
- `project` - Project management
- `strategy` - Business strategy
- `travel` - Travel booking and management
- `charity` - Charitable giving
- `analytics` - Business analytics
- `business_strategy` - Strategic planning
- `crm` - Customer relationship management
- `operations` - Operations management

---

## 🏥 Health (2 agents)
*Health and wellness*

- `nutrition` - Nutrition tracking and advice
- `health` - General health management

---

## 🛡️ Insurance (3 agents)
*Insurance management*

- `insurance` - Insurance policy management
- `risk` - Risk assessment
- `claims` - Claims processing

---

## 🎬 Media (6 agents)
*Media processing*

- `vision` - Image analysis
- `audio` - Audio processing
- `video` - Video processing
- `music` - Music management
- `content` - Content creation
- `image` - Image editing and generation

---

## 📊 Analytics (9 agents)
*Data analysis and insights*

- `data` - Data processing
- `text` - Text analysis
- `schema` - Schema design
- `router` - Data routing
- `materialize` - Data materialization
- `forecast` - Forecasting
- `metrics` - Metrics tracking
- `ml` - Machine learning
- `report` - Report generation

---

## 🎭 Modern (3 agents)
*Modern communication styles*

- `slang` - Slang translation
- `meme` - Meme generation
- `social` - Social media management

---

## 🌐 Web (4 agents)
*Web operations*

- `scraper` - Web scraping
- `integration` - Web integrations
- `seo` - SEO optimization
- `web` - General web operations

---

## ⛓️ Web3 (5 agents)
*Blockchain and crypto*

- `crypto` - Cryptocurrency operations
- `nft` - NFT management
- `auction` - NFT auctions
- `blockchain` - Blockchain interactions
- `defi` - DeFi protocols

---

## 🧠 Core (1 agent)
*Central orchestration*

- `core` - Core routing and orchestration

---

## 📚 Knowledge (2 agents)
*Learning and knowledge management*

- `learning` - Continuous learning
- `knowledge_base` - Knowledge base operations

---

## 🔧 Platform (1 agent)
*Platform services*

- `universal_vault` - Universal Vault integration

---

## Meta-Orchestrator Routing Guidelines

### Query Intent → Agent Category Mapping

**Financial Queries:**
- Trading, stocks, portfolio → `Finance` agents
- Market data, prices → `Connectors - Market Data`
- Accounting, invoices → `Finance` (ledger, invoice, tax)
- Banking, payments → `Connectors - Financial` (plaid, stripe)

**Business Queries:**
- CRM, sales, marketing → `Business` agents
- HR, hiring, payroll → `Business` (hr)
- Project management → `Business` (project)
- Strategy, planning → `Business` (strategy, business_strategy)

**Communication Queries:**
- Email → `Communication` (email) or `Connectors - Communication` (gmail_connector)
- Calendar, scheduling → `Communication` (calendar) or `Connectors - Communication` (gcal_connector)
- Messaging → `Communication` (slack, teams)

**Development Queries:**
- Code review, GitHub → `Development` agents
- API design → `Development` (api)
- Deployment → `Development` (deployment)

**Document Queries:**
- PDF, OCR → `Documents` (pdf, ocr)
- Knowledge base → `Documents` (knowledge) or `Knowledge` (knowledge_base)
- Translation → `Documents` (translation)

**Data & Analytics:**
- Data analysis → `Analytics` (data, ml)
- Forecasting → `Analytics` (forecast)
- Reporting → `Analytics` (report)

**Web3 & Crypto:**
- Cryptocurrency → `Web3` (crypto) or `Connectors - Market Data` (crypto exchanges)
- NFTs → `Web3` (nft, auction)
- DeFi → `Web3` (defi)

### Multi-Agent Workflows

**Complex queries may require multiple agents:**

1. **"Analyze my portfolio and send me a report"**
   - `portfolio` (Finance) → analyze holdings
   - `report` (Analytics) → generate report
   - `email` (Communication) → send report

2. **"Find grant opportunities and update my CRM"**
   - `grant` (Business) → find grants
   - `crm` (Business) → update records

3. **"Get market sentiment and execute trades"**
   - `news_sentiment_connector` (Connectors - Financial) → get sentiment
   - `sentiment` (Finance) → analyze sentiment
   - `trading` (Finance) → execute trades

4. **"Review this contract and file it"**
   - `contract` (Legal) → review contract
   - `document` (Documents) → process and file

---

## Agent Selection Priority

When multiple agents can handle a query:

1. **Specificity** - More specific agents first (e.g., `options` over `trading`)
2. **Connectors** - Use connectors for data retrieval, agents for processing
3. **Workflow** - Core/router agents for complex multi-step tasks
4. **Context** - Consider user's app context (Atlas, Delt, Akashic)

---

*Last Updated: October 28, 2025*
*Total Agents: 133*
