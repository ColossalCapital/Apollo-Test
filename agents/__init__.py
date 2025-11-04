"""
Apollo Agents - 7-Layer Agent Architecture

All agents inherit from layer-specific base classes:
- Layer 1: Data Extraction (Primitive)
- Layer 2: Entity Recognition (Basic Intelligence)
- Layer 3: Domain Experts (Specialists)
- Layer 4: Workflow Orchestration (Coordinators)
- Layer 5: Meta-Orchestration (Strategic)
- Layer 6: Autonomous Agents (Self-Directed)
- Layer 7: Swarm Intelligence (Collective)

Total: 147 agents with comprehensive metadata
"""

# New 5-layer architecture
from .base import (
    Layer1Agent, Layer2Agent, Layer3Agent, Layer4Agent, Layer5Agent,
    AgentLayer, AgentMetadata, AgentResult as NewAgentResult,
    Entity, Relationship, Trigger, WorkflowResult,
    get_agent_layer, validate_agent_chain
)
from .registry import AgentRegistry, get_registry
from .factory import AgentFactory, get_factory, create_agent, create_workflow

# Legacy base agent (for backwards compatibility)
from .base_agent import BaseAgent, AgentResult

# Infrastructure (4 agents)
from .infrastructure.connection_monitor_agent import ConnectionMonitorAgent
from .infrastructure.rate_limit_manager_agent import RateLimitManagerAgent
from .infrastructure.api_version_monitor_agent import APIVersionMonitorAgent
from .infrastructure.webhook_manager_agent import WebhookManagerAgent

# Connectors - Brokerages (4 agents)
from .connectors.brokerages.ib_connector_agent import IBConnectorAgent
from .connectors.brokerages.td_connector_agent import TDConnectorAgent
from .connectors.brokerages.schwab_connector_agent import SchwabConnectorAgent
from .connectors.brokerages.alpaca_connector_agent import AlpacaConnectorAgent

# Connectors - Exchanges (3 agents)
from .connectors.exchanges.binance_connector_agent import BinanceConnectorAgent
from .connectors.exchanges.coinbase_connector_agent import CoinbaseConnectorAgent
from .connectors.exchanges.kraken_connector_agent import KrakenConnectorAgent

# Connectors - Financial (5 agents)
from .connectors.financial.quickbooks_connector_agent import QuickBooksConnectorAgent
from .connectors.financial.plaid_connector_agent import PlaidConnectorAgent
from .connectors.financial.stripe_connector_agent import StripeConnectorAgent
from .connectors.financial.investor_profiles_connector_agent import InvestorProfilesConnectorAgent
from .connectors.financial.news_sentiment_connector_agent import NewsSentimentConnectorAgent

# Connectors - Communication (3 agents)
from .connectors.communication.gmail_connector_agent import GmailConnectorAgent
from .connectors.communication.gcal_connector_agent import GCalConnectorAgent
from .connectors.communication.slack_connector_agent import SlackConnectorAgent

# Connectors - Productivity (4 agents)
from .connectors.productivity.github_connector_agent import GitHubConnectorAgent
from .connectors.productivity.notion_connector_agent import NotionConnectorAgent
from .connectors.productivity.gdrive_connector_agent import GDriveConnectorAgent
from .connectors.productivity.spotify_connector_agent import SpotifyConnectorAgent

# Connectors - Market Data (24 agents)
from .connectors.market_data.alphavantage_connector_agent import AlphavantageConnectorAgent
from .connectors.market_data.polygon_connector_agent import PolygonConnectorAgent
from .connectors.market_data.finnhub_connector_agent import FinnhubConnectorAgent
from .connectors.market_data.twelvedata_connector_agent import TwelvedataConnectorAgent
from .connectors.market_data.databento_connector_agent import DatabentoConnectorAgent
from .connectors.market_data.tradier_connector_agent import TradierConnectorAgent
from .connectors.market_data.binanceus_connector_agent import BinanceusConnectorAgent
from .connectors.market_data.gemini_connector_agent import GeminiConnectorAgent
from .connectors.market_data.bitfinex_connector_agent import BitfinexConnectorAgent
from .connectors.market_data.bitstamp_connector_agent import BitstampConnectorAgent
from .connectors.market_data.bitget_connector_agent import BitgetConnectorAgent
from .connectors.market_data.bithumb_connector_agent import BithumbConnectorAgent
from .connectors.market_data.bybit_connector_agent import BybitConnectorAgent
from .connectors.market_data.deribit_connector_agent import DeribitConnectorAgent
from .connectors.market_data.ftx_connector_agent import FtxConnectorAgent
from .connectors.market_data.ftxus_connector_agent import FtxusConnectorAgent
from .connectors.market_data.gateio_connector_agent import GateioConnectorAgent
from .connectors.market_data.huobi_connector_agent import HuobiConnectorAgent
from .connectors.market_data.kucoin_connector_agent import KucoinConnectorAgent
from .connectors.market_data.okx_connector_agent import OkxConnectorAgent
from .connectors.market_data.phemex_connector_agent import PhemexConnectorAgent
from .connectors.market_data.upbit_connector_agent import UpbitConnectorAgent
from .connectors.market_data.collectors_connector_agent import CollectorsConnectorAgent
from .connectors.market_data.dex_collector_connector_agent import DEXCollectorConnectorAgent

# Communication (5 agents)
from .communication.email_agent import EmailAgent
from .communication.calendar_agent import CalendarAgent
from .communication.contact_agent import ContactAgent
from .communication.slack_agent import SlackAgent
from .communication.teams_agent import TeamsAgent

# Development (4 agents)
from .development import GitHubAgent, CodeReviewAgent, DeploymentAgent, APIAgent

# Documents (9 agents)
from .documents.document_agent import DocumentAgent
from .documents.knowledge_agent import KnowledgeAgent
from .documents.wiki_agent import WikiAgent
from .documents.research_agent import ResearchAgent
from .documents.translation_agent import TranslationAgent
from .documents.drive_agent import DriveAgent
from .documents.notion_agent import NotionAgent
from .documents.ocr_agent import OCRAgent
from .documents.pdf_agent import PDFAgent

# Finance (20 agents)
from .finance.ledger_agent import LedgerAgent
from .finance.tax_agent import TaxAgent
from .finance.invoice_agent import InvoiceAgent
from .finance.budget_agent import BudgetAgent
from .finance.trading_agent import TradingAgent
from .finance.forex_agent import ForexAgent
from .finance.stocks_agent import StocksAgent
from .finance.broker_agent import BrokerAgent
from .finance.broker_alpaca_agent import AlpacaBrokerAgent
from .finance.broker_ib_agent import IBBrokerAgent
from .finance.broker_schwab_agent import SchwabBrokerAgent
from .finance.broker_td_agent import TDBrokerAgent
from .finance.exchange_agent import ExchangeAgent
from .finance.strategy_agent import FinanceStrategyAgent
from .finance.portfolio_agent import PortfolioAgent
from .finance.options_agent import OptionsAgent
from .finance.futures_agent import FuturesAgent
from .finance.arbitrage_agent import ArbitrageAgent
from .finance.sentiment_agent import SentimentAgent
from .finance.backtest_agent import BacktestAgent

# Legal (4 agents)
from .legal.legal_agent import LegalAgent
from .legal.contract_agent import ContractAgent
from .legal.compliance_agent import ComplianceAgent
from .legal.ip_agent import IPAgent

# Business (12 agents)
from .business.grant_agent import GrantScraperAgent
from .business.sales_agent import SalesAgent
from .business.marketing_agent import MarketingAgent
from .business.hr_agent import HRAgent
from .business.project_agent import ProjectAgent
from .business.strategy_agent import BusinessStrategyAgent
from .business.travel_agent import TravelAgent
from .business.charity_agent import CharityAgent
from .business.analytics_agent import AnalyticsAgent
from .business.crm_agent import CRMAgent
from .business.operations_agent import OperationsAgent

# Health (2 agents)
from .health.nutrition_agent import NutritionAgent
from .health.health_agent import HealthAgent

# Insurance (3 agents)
from .insurance.insurance_agent import InsuranceAgent
from .insurance.claims_agent import ClaimsAgent
from .insurance.risk_agent import RiskAgent

# Media (6 agents)
from .media.vision_agent import VisionAgent
from .media.audio_agent import AudioAgent
from .media.video_agent import VideoAgent
from .media.music_agent import MusicAgent
from .media.content_agent import ContentAgent
from .media.image_agent import ImageAgent

# Analytics (9 agents)
from .analytics.data_agent import DataAgent
from .analytics.text_agent import TextAgent
from .analytics.schema_agent import SchemaAgent
from .analytics.router_agent import RouterAgent
from .analytics.materialize_agent import MaterializeAgent
from .analytics.forecast_agent import ForecastAgent
from .analytics.metrics_agent import MetricsAgent
from .analytics.ml_agent import MLAgent
from .analytics.report_agent import ReportAgent

# Modern (3 agents)
from .modern.slang_agent import SlangAgent
from .modern.meme_agent import MemeAgent
from .modern.social_agent import SocialAgent

# Web (4 agents)
from .web.scraper_agent import ScraperAgent
from .web.integration_agent import IntegrationAgent
from .web.seo_agent import SEOAgent
from .web.web_agent import WebAgent

# Web3 (5 agents)
from .web3.crypto_agent import CryptoAgent
from .web3.nft_agent import NFTAgent
from .web3.auction_agent import AuctionAgent
from .web3.blockchain_agent import BlockchainAgent
from .web3.defi_agent import DeFiAgent

# Core (1 agent)
from .core.core_agent import CoreAgent

# Knowledge (2 agents)
from .knowledge.learning_agent import LearningAgent
from .knowledge.knowledge_base_agent import KnowledgeBaseAgent

# Platform (1 agent)
from .universal_vault_agent import UniversalVaultAgent


__all__ = [
    # New 5-layer architecture
    "Layer1Agent",
    "Layer2Agent",
    "Layer3Agent",
    "Layer4Agent",
    "Layer5Agent",
    "AgentLayer",
    "AgentMetadata",
    "NewAgentResult",
    "Entity",
    "Relationship",
    "Trigger",
    "WorkflowResult",
    "get_agent_layer",
    "validate_agent_chain",
    "AgentRegistry",
    "get_registry",
    "AgentFactory",
    "get_factory",
    "create_agent",
    "create_workflow",
    
    # Legacy base (backwards compatibility)
    "BaseAgent",
    "AgentResult",
    
    # Infrastructure
    "ConnectionMonitorAgent",
    "RateLimitManagerAgent",
    "APIVersionMonitorAgent",
    "WebhookManagerAgent",
    
    # Connectors - Brokerages
    "IBConnectorAgent",
    "TDConnectorAgent",
    "SchwabConnectorAgent",
    "AlpacaConnectorAgent",
    
    # Connectors - Exchanges
    "BinanceConnectorAgent",
    "CoinbaseConnectorAgent",
    "KrakenConnectorAgent",
    
    # Connectors - Financial
    "QuickBooksConnectorAgent",
    "PlaidConnectorAgent",
    "StripeConnectorAgent",
    "InvestorProfilesConnectorAgent",
    "NewsSentimentConnectorAgent",
    
    # Connectors - Communication
    "GmailConnectorAgent",
    "GCalConnectorAgent",
    "SlackConnectorAgent",
    
    # Connectors - Productivity
    "GitHubConnectorAgent",
    "NotionConnectorAgent",
    "GDriveConnectorAgent",
    "SpotifyConnectorAgent",
    
    # Connectors - Market Data
    "AlphavantageConnectorAgent",
    "PolygonConnectorAgent",
    "FinnhubConnectorAgent",
    "TwelvedataConnectorAgent",
    "DatabentoConnectorAgent",
    "TradierConnectorAgent",
    "BinanceusConnectorAgent",
    "GeminiConnectorAgent",
    "BitfinexConnectorAgent",
    "BitstampConnectorAgent",
    "BitgetConnectorAgent",
    "BithumbConnectorAgent",
    "BybitConnectorAgent",
    "DeribitConnectorAgent",
    "FtxConnectorAgent",
    "FtxusConnectorAgent",
    "GateioConnectorAgent",
    "HuobiConnectorAgent",
    "KucoinConnectorAgent",
    "OkxConnectorAgent",
    "PhemexConnectorAgent",
    "UpbitConnectorAgent",
    "CollectorsConnectorAgent",
    "DEXCollectorConnectorAgent",
    
    # Communication
    "EmailAgent",
    "CalendarAgent",
    "ContactAgent",
    "SlackAgent",
    "TeamsAgent",
    
    # Development
    "GitHubAgent",
    "CodeReviewAgent",
    "DeploymentAgent",
    "APIAgent",
    
    # Documents
    "DocumentAgent",
    "KnowledgeAgent",
    "WikiAgent",
    "ResearchAgent",
    "TranslationAgent",
    "DriveAgent",
    "NotionAgent",
    "OCRAgent",
    "PDFAgent",
    
    # Finance
    "LedgerAgent",
    "TaxAgent",
    "InvoiceAgent",
    "BudgetAgent",
    "TradingAgent",
    "ForexAgent",
    "StocksAgent",
    "BrokerAgent",
    "AlpacaBrokerAgent",
    "IBBrokerAgent",
    "SchwabBrokerAgent",
    "TDBrokerAgent",
    "ExchangeAgent",
    "FinanceStrategyAgent",
    "PortfolioAgent",
    "OptionsAgent",
    "FuturesAgent",
    "ArbitrageAgent",
    "SentimentAgent",
    "BacktestAgent",
    
    # Legal
    "LegalAgent",
    "ContractAgent",
    "ComplianceAgent",
    "IPAgent",
    
    # Business
    "GrantScraperAgent",
    "SalesAgent",
    "MarketingAgent",
    "HRAgent",
    "ProjectAgent",
    "BusinessStrategyAgent",
    "TravelAgent",
    "CharityAgent",
    "AnalyticsAgent",
    "CRMAgent",
    "OperationsAgent",
    
    # Health
    "NutritionAgent",
    "HealthAgent",
    
    # Insurance
    "InsuranceAgent",
    "RiskAgent",
    "ClaimsAgent",
    
    # Media
    "VisionAgent",
    "AudioAgent",
    "VideoAgent",
    "MusicAgent",
    "ContentAgent",
    "ImageAgent",
    
    # Analytics
    "DataAgent",
    "TextAgent",
    "SchemaAgent",
    "RouterAgent",
    "MaterializeAgent",
    "ForecastAgent",
    "MetricsAgent",
    "MLAgent",
    "ReportAgent",
    
    # Modern
    "SlangAgent",
    "MemeAgent",
    "SocialAgent",
    
    # Web
    "ScraperAgent",
    "IntegrationAgent",
    "SEOAgent",
    "WebAgent",
    
    # Web3
    "CryptoAgent",
    "NFTAgent",
    "AuctionAgent",
    "BlockchainAgent",
    "DeFiAgent",
    
    # Core
    "CoreAgent",
    
    # Knowledge
    "LearningAgent",
    "KnowledgeBaseAgent",
    
    # Platform
    "UniversalVaultAgent",
]


# Agent registry for easy lookup
AGENT_REGISTRY = {
    # Infrastructure
    "connection_monitor": ConnectionMonitorAgent,
    "rate_limit_manager": RateLimitManagerAgent,
    "api_version_monitor": APIVersionMonitorAgent,
    "webhook_manager": WebhookManagerAgent,
    
    # Connectors - Brokerages
    "ib_connector": IBConnectorAgent,
    "td_connector": TDConnectorAgent,
    "schwab_connector": SchwabConnectorAgent,
    "alpaca_connector": AlpacaConnectorAgent,
    
    # Connectors - Exchanges
    "binance_connector": BinanceConnectorAgent,
    "coinbase_connector": CoinbaseConnectorAgent,
    "kraken_connector": KrakenConnectorAgent,
    
    # Connectors - Financial
    "quickbooks_connector": QuickBooksConnectorAgent,
    "plaid_connector": PlaidConnectorAgent,
    "stripe_connector": StripeConnectorAgent,
    "investor_profiles_connector": InvestorProfilesConnectorAgent,
    "news_sentiment_connector": NewsSentimentConnectorAgent,
    
    # Connectors - Communication
    "gmail_connector": GmailConnectorAgent,
    "gcal_connector": GCalConnectorAgent,
    "slack_connector": SlackConnectorAgent,
    
    # Connectors - Productivity
    "github_connector": GitHubConnectorAgent,
    "notion_connector": NotionConnectorAgent,
    "gdrive_connector": GDriveConnectorAgent,
    "spotify_connector": SpotifyConnectorAgent,
    
    # Connectors - Market Data
    "alphavantage_connector": AlphavantageConnectorAgent,
    "polygon_connector": PolygonConnectorAgent,
    "finnhub_connector": FinnhubConnectorAgent,
    "twelvedata_connector": TwelvedataConnectorAgent,
    "databento_connector": DatabentoConnectorAgent,
    "tradier_connector": TradierConnectorAgent,
    "binanceus_connector": BinanceusConnectorAgent,
    "gemini_connector": GeminiConnectorAgent,
    "bitfinex_connector": BitfinexConnectorAgent,
    "bitstamp_connector": BitstampConnectorAgent,
    "bitget_connector": BitgetConnectorAgent,
    "bithumb_connector": BithumbConnectorAgent,
    "bybit_connector": BybitConnectorAgent,
    "deribit_connector": DeribitConnectorAgent,
    "ftx_connector": FtxConnectorAgent,
    "ftxus_connector": FtxusConnectorAgent,
    "gateio_connector": GateioConnectorAgent,
    "huobi_connector": HuobiConnectorAgent,
    "kucoin_connector": KucoinConnectorAgent,
    "okx_connector": OkxConnectorAgent,
    "phemex_connector": PhemexConnectorAgent,
    "upbit_connector": UpbitConnectorAgent,
    "collectors_connector": CollectorsConnectorAgent,
    "dex_collector_connector": DEXCollectorConnectorAgent,
    
    # Communication
    "email": EmailAgent,
    "calendar": CalendarAgent,
    "contact": ContactAgent,
    "slack": SlackAgent,
    "teams": TeamsAgent,
    
    # Development
    "github": GitHubAgent,
    "code_review": CodeReviewAgent,
    "deployment": DeploymentAgent,
    "api": APIAgent,
    
    # Documents
    "document": DocumentAgent,
    "knowledge": KnowledgeAgent,
    "wiki": WikiAgent,
    "research": ResearchAgent,
    "translation": TranslationAgent,
    "drive": DriveAgent,
    "notion": NotionAgent,
    "ocr": OCRAgent,
    "pdf": PDFAgent,
    
    # Finance
    "ledger": LedgerAgent,
    "tax": TaxAgent,
    "invoice": InvoiceAgent,
    "budget": BudgetAgent,
    "trading": TradingAgent,
    "forex": ForexAgent,
    "stocks": StocksAgent,
    "broker": BrokerAgent,
    "broker_alpaca": AlpacaBrokerAgent,
    "broker_ib": IBBrokerAgent,
    "broker_schwab": SchwabBrokerAgent,
    "broker_td": TDBrokerAgent,
    "exchange": ExchangeAgent,
    "finance_strategy": FinanceStrategyAgent,
    "portfolio": PortfolioAgent,
    "options": OptionsAgent,
    "futures": FuturesAgent,
    "arbitrage": ArbitrageAgent,
    "sentiment": SentimentAgent,
    "backtest": BacktestAgent,
    
    # Legal
    "legal": LegalAgent,
    "contract": ContractAgent,
    "compliance": ComplianceAgent,
    "ip": IPAgent,
    
    # Business
    "grant": GrantScraperAgent,
    "sales": SalesAgent,
    "marketing": MarketingAgent,
    "hr": HRAgent,
    "project": ProjectAgent,
    "strategy": BusinessStrategyAgent,
    "travel": TravelAgent,
    "charity": CharityAgent,
    "analytics": AnalyticsAgent,
    "crm": CRMAgent,
    "operations": OperationsAgent,
    
    # Health
    "nutrition": NutritionAgent,
    "health": HealthAgent,
    
    # Insurance
    "insurance": InsuranceAgent,
    "risk": RiskAgent,
    "claims": ClaimsAgent,
    
    # Media
    "vision": VisionAgent,
    "audio": AudioAgent,
    "video": VideoAgent,
    "music": MusicAgent,
    "content": ContentAgent,
    "image": ImageAgent,
    
    # Analytics
    "data": DataAgent,
    "text": TextAgent,
    "schema": SchemaAgent,
    "router": RouterAgent,
    "materialize": MaterializeAgent,
    "forecast": ForecastAgent,
    "metrics": MetricsAgent,
    "ml": MLAgent,
    "report": ReportAgent,
    
    # Modern
    "slang": SlangAgent,
    "meme": MemeAgent,
    "social": SocialAgent,
    
    # Web
    "scraper": ScraperAgent,
    "integration": IntegrationAgent,
    "seo": SEOAgent,
    "web": WebAgent,
    
    # Web3
    "crypto": CryptoAgent,
    "nft": NFTAgent,
    "auction": AuctionAgent,
    "blockchain": BlockchainAgent,
    "defi": DeFiAgent,
    
    # Core
    "core": CoreAgent,
    
    # Knowledge
    "learning": LearningAgent,
    "knowledge_base": KnowledgeBaseAgent,
    
    # Platform
    "universal_vault": UniversalVaultAgent,
}


# Agent aliases - maps frontend agent IDs to backend agents
AGENT_ALIASES = {
    # Broker aliases -> generic broker agent
    'broker_ib': 'broker',
    'broker_td': 'broker',
    'broker_schwab': 'broker',
    'broker_alpaca': 'broker',
    
    # Exchange aliases -> generic exchange agent
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
    """
    Get an agent instance by name, with alias support.
    
    Frontend agent IDs are automatically mapped to backend agents via AGENT_ALIASES.
    For example: 'broker_ib' -> 'broker', 'exchange_binance' -> 'exchange'
    """
    # Resolve alias if it exists
    resolved_name = AGENT_ALIASES.get(agent_name, agent_name)
    
    agent_class = AGENT_REGISTRY.get(resolved_name)
    if not agent_class:
        raise ValueError(f"Unknown agent: {agent_name} (resolved to: {resolved_name})")
    return agent_class()


def list_agents() -> dict:
    """List all available agents by category"""
    return {
        "infrastructure": ["connection_monitor", "rate_limit_manager", "api_version_monitor", "webhook_manager"],
        "connectors": [
            # Brokerages
            "ib_connector", "td_connector", "schwab_connector", "alpaca_connector",
            # Exchanges
            "binance_connector", "coinbase_connector", "kraken_connector",
            # Data Sources
            "quickbooks_connector", "plaid_connector", "stripe_connector",
            "gmail_connector", "gcal_connector", "slack_connector",
            "github_connector", "notion_connector", "gdrive_connector", "spotify_connector"
        ],
        "communication": ["email", "calendar", "contact", "slack"],
        "development": ["github", "code_review", "deployment", "api"],
        "documents": ["document", "knowledge", "wiki", "research", "translation"],
        "finance": ["ledger", "tax", "invoice", "budget", "trading", "forex", "stocks", "broker", "exchange", "finance_strategy", "portfolio", "options", "futures", "arbitrage", "sentiment", "backtest"],
        "legal": ["legal", "contract", "compliance", "ip"],
        "business": ["grant", "sales", "marketing", "hr", "project", "strategy", "travel", "charity"],
        "health": ["nutrition", "health"],
        "insurance": ["insurance", "risk"],
        "media": ["vision", "audio", "video", "music"],
        "analytics": ["data", "text", "schema", "router", "materialize"],
        "modern": ["slang", "meme", "social"],
        "web": ["scraper", "integration"],
        "web3": ["crypto", "nft", "auction"],
        "platform": ["universal_vault"],
    }


# ============================================================================
# NEW REGISTRY HELPERS FOR 147 AGENTS
# ============================================================================

def get_agent_by_name(agent_name: str):
    """Get agent instance by name"""
    try:
        return get_agent(agent_name)
    except ValueError:
        return None


def get_all_agents():
    """Get all agent instances"""
    agents = []
    for agent_name in AGENT_REGISTRY.keys():
        try:
            agents.append(get_agent(agent_name))
        except:
            pass
    return agents


def get_agents_by_filter(
    app_context: str = None,
    entity_type: str = None,
    category: str = None,
    requires_subscription: list = None,
    search: str = None
):
    """
    Filter agents by metadata
    
    Args:
        app_context: Filter by app context (atlas, delt, akashic, all)
        entity_type: Filter by entity type (personal, business, trading_firm, universal)
        category: Filter by category (communication, finance, etc.)
        requires_subscription: Filter by subscription requirements
        search: Search in name, description, capabilities
    
    Returns:
        List of matching agents
    """
    all_agents = get_all_agents()
    filtered = []
    
    for agent in all_agents:
        if not hasattr(agent, 'metadata'):
            continue
        
        metadata = agent.metadata
        
        # Filter by app context
        if app_context and hasattr(metadata, 'app_contexts'):
            if metadata.app_contexts:
                contexts = [ctx.value for ctx in metadata.app_contexts]
                if app_context not in contexts and 'all' not in contexts:
                    continue
        
        # Filter by entity type
        if entity_type and hasattr(metadata, 'entity_types'):
            if metadata.entity_types:
                types = [et.value for et in metadata.entity_types]
                if entity_type not in types and 'universal' not in types:
                    continue
        
        # Filter by category
        if category and hasattr(metadata, 'category'):
            if metadata.category and metadata.category.value != category:
                continue
        
        # Filter by subscription
        if requires_subscription and hasattr(metadata, 'requires_subscription'):
            if metadata.requires_subscription:
                if not any(sub in metadata.requires_subscription for sub in requires_subscription):
                    continue
        
        # Search filter
        if search:
            search_lower = search.lower()
            searchable = [
                metadata.name.lower(),
                metadata.description.lower(),
                ' '.join(metadata.capabilities).lower()
            ]
            if not any(search_lower in s for s in searchable):
                continue
        
        filtered.append(agent)
    
    return filtered
