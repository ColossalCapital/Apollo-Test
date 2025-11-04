"""
Apollo Agent Registry

Central registry of all agents organized by layer.
Provides easy discovery and instantiation of agents.

Usage:
    from agents.registry import AgentRegistry
    
    registry = AgentRegistry()
    agent = registry.get_agent(layer=1, name="email_parser")
    agents = registry.list_agents_by_layer(layer=4)
"""

from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass
from enum import Enum

from .base import (
    Layer1Agent, Layer2Agent, Layer3Agent, Layer4Agent, Layer5Agent,
    AgentLayer, AgentMetadata
)

# Import existing agents
from .workflow.meeting_orchestrator_agent import MeetingOrchestratorAgent
from .research.research_agent import ResearchAgent


# ============================================================================
# AGENT REGISTRY DATA STRUCTURES
# ============================================================================

@dataclass
class AgentRegistryEntry:
    """Entry in the agent registry"""
    name: str
    layer: AgentLayer
    agent_class: Type[Any]
    description: str
    capabilities: List[str]
    dependencies: List[str]
    enabled: bool = True


class AgentCategory(Enum):
    """Agent categories for organization"""
    # Layer 1: Data Extraction
    PARSERS = "parsers"
    EXTRACTORS = "extractors"
    
    # Layer 2: Entity Recognition
    RECOGNITION = "recognition"
    CLASSIFICATION = "classification"
    
    # Layer 3: Domain Experts
    BUSINESS = "business"
    TECHNICAL = "technical"
    RESEARCH = "research"
    CREATIVE = "creative"
    FINANCIAL = "financial"
    LEGAL = "legal"
    
    # Layer 4: Workflow Orchestration
    COMMUNICATION = "communication"
    PROJECT_MANAGEMENT = "project_management"
    SALES = "sales"
    CUSTOMER_SUCCESS = "customer_success"
    
    # Layer 5: Meta-Orchestration
    OPTIMIZATION = "optimization"
    LEARNING = "learning"
    STRATEGY = "strategy"


# ============================================================================
# AGENT REGISTRY
# ============================================================================

class AgentRegistry:
    """
    Central registry of all Apollo agents
    
    Organizes agents by layer and provides discovery mechanisms.
    """
    
    def __init__(self):
        self._registry: Dict[AgentLayer, Dict[str, AgentRegistryEntry]] = {
            AgentLayer.LAYER_1_EXTRACTION: {},
            AgentLayer.LAYER_2_RECOGNITION: {},
            AgentLayer.LAYER_3_DOMAIN: {},
            AgentLayer.LAYER_4_WORKFLOW: {},
            AgentLayer.LAYER_5_META: {},
        }
        
        # Load all agents
        self._load_agents()
    
    def _load_agents(self):
        """Load all agents into registry"""
        
        # ====================================================================
        # LAYER 1: DATA EXTRACTION AGENTS (43 agents)
        # ====================================================================
        
        # MIGRATED CONNECTORS (3 agents) ✅
        from .layer1.connectors.communication.gmail_connector_agent import GmailConnectorAgent
        from .layer1.connectors.financial.quickbooks_connector_agent import QuickBooksConnectorAgent
        from .layer1.connectors.financial.plaid_connector_agent import PlaidConnectorAgent
        
        self.register(
            name="gmail_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            agent_class=GmailConnectorAgent,
            description="Gmail API, email sync, and message management",
            capabilities=["gmail_api", "email_sync", "label_management", "search", "send_email"],
            dependencies=[]
        )
        
        self.register(
            name="quickbooks_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            agent_class=QuickBooksConnectorAgent,
            description="QuickBooks API, invoice sync, and accounting integration",
            capabilities=["quickbooks_api", "invoice_sync", "expense_tracking", "pl_reports", "tax_categories"],
            dependencies=[]
        )
        
        self.register(
            name="plaid_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            agent_class=PlaidConnectorAgent,
            description="Plaid Link, bank connections, and transaction sync",
            capabilities=["plaid_link", "bank_connections", "transaction_sync", "balance_checks", "identity_verification"],
            dependencies=[]
        )
        
        # NOTE: Remaining connector agents will be registered here
        # They extract data from external sources
        # Current status: Using legacy BaseAgent (will migrate)
        
        # Connectors - Brokerages (4)
        # - IBConnectorAgent, TDConnectorAgent, SchwabConnectorAgent, AlpacaConnectorAgent
        
        # Connectors - Exchanges (3)
        # - BinanceConnectorAgent, CoinbaseConnectorAgent, KrakenConnectorAgent
        
        # Connectors - Financial (2 remaining)
        # - StripeConnectorAgent, InvestorProfilesConnectorAgent, NewsSentimentConnectorAgent
        
        # Connectors - Communication (2 remaining)
        # - GCalConnectorAgent, SlackConnectorAgent
        
        # Connectors - Productivity (4)
        # - GitHubConnectorAgent, NotionConnectorAgent, GDriveConnectorAgent, SpotifyConnectorAgent
        
        # Connectors - Market Data (24)
        # - All exchange connectors (Alphavantage, Polygon, Finnhub, etc.)
        
        # Total Layer 1: 43 agents (3 migrated, 40 remaining)
        
        # ====================================================================
        # LAYER 2: ENTITY RECOGNITION AGENTS (12 agents)
        # ====================================================================
        
        # NOTE: Analytics and Modern agents will be registered here
        # They recognize entities and patterns from structured data
        # Current status: Using legacy BaseAgent (will migrate)
        
        # Analytics (9)
        # - DataAgent, TextAgent, SchemaAgent, RouterAgent, MaterializeAgent
        # - ForecastAgent, MetricsAgent, MLAgent, ReportAgent
        
        # Modern (3)
        # - SlangAgent, MemeAgent, SocialAgent
        
        # Total Layer 2: 12 agents
        
        # ====================================================================
        # LAYER 3: DOMAIN EXPERT AGENTS (62 agents)
        # ====================================================================
        
        # Research Agent (already migrated)
        self.register(
            name="research",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=ResearchAgent,
            description="Research people, companies, topics",
            capabilities=["research", "background", "analysis"],
            dependencies=[]
        )
        
        # NEW PROJECT-SPECIFIC AGENTS (7 agents) ✅ MIGRATED
        from .layer3.trading.trading_strategy_agent import TradingStrategyAgent
        from .layer3.governance.entity_governance_agent import EntityGovernanceAgent
        from .layer3.investor.investor_relations_agent import InvestorRelationsAgent
        from .layer3.knowledge.knowledge_graph_agent import KnowledgeGraphAgent
        from .layer4.workflow.workflow_pattern_agent import WorkflowPatternAgent
        from .layer3.data.data_pipeline_agent import DataPipelineAgent
        from .layer3.security.security_compliance_agent import SecurityComplianceAgent
        
        self.register(
            name="trading_strategy",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=TradingStrategyAgent,
            description="Algorithmic trading strategy analysis",
            capabilities=["trading", "strategy", "backtest", "optimization", "risk_analysis"],
            dependencies=[]
        )
        
        self.register(
            name="entity_governance",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=EntityGovernanceAgent,
            description="Corporate governance and compliance",
            capabilities=["governance", "compliance", "c_corp", "s_corp", "board_meetings", "filings"],
            dependencies=[]
        )
        
        self.register(
            name="investor_relations",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=InvestorRelationsAgent,
            description="Investor communication and reporting",
            capabilities=["investor_relations", "reporting", "communication", "fundraising"],
            dependencies=[]
        )
        
        self.register(
            name="knowledge_graph",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=KnowledgeGraphAgent,
            description="Knowledge graph optimization and analysis",
            capabilities=["graph_optimization", "pattern_discovery", "cross_graph_analysis"],
            dependencies=[]
        )
        
        self.register(
            name="workflow_pattern",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=WorkflowPatternAgent,
            description="Workflow pattern discovery and optimization",
            capabilities=["pattern_discovery", "workflow_optimization", "automation"],
            dependencies=[]
        )
        
        self.register(
            name="data_pipeline",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=DataPipelineAgent,
            description="Data pipeline orchestration and monitoring",
            capabilities=["pipeline_orchestration", "data_quality", "etl_optimization"],
            dependencies=[]
        )
        
        self.register(
            name="security_compliance",
            layer=AgentLayer.LAYER_3_DOMAIN,
            agent_class=SecurityComplianceAgent,
            description="Security audit and compliance tracking",
            capabilities=["security_audit", "compliance", "vulnerability_detection"],
            dependencies=[]
        )
        
        # NOTE: Domain expert agents will be registered here
        # They provide deep domain knowledge and analysis
        # Current status: Using legacy BaseAgent (will migrate)
        
        # Finance (20)
        # - LedgerAgent, TaxAgent, InvoiceAgent, BudgetAgent, TradingAgent
        # - ForexAgent, StocksAgent, BrokerAgent, ExchangeAgent, PortfolioAgent
        # - OptionsAgent, FuturesAgent, ArbitrageAgent, SentimentAgent, BacktestAgent
        # - AlpacaBrokerAgent, IBBrokerAgent, SchwabBrokerAgent, TDBrokerAgent
        # - FinanceStrategyAgent
        
        # Business (12)
        # - GrantScraperAgent, SalesAgent, MarketingAgent, HRAgent, ProjectAgent
        # - BusinessStrategyAgent, TravelAgent, CharityAgent, AnalyticsAgent
        # - CRMAgent, OperationsAgent, ResearchAgent
        
        # Legal (4)
        # - LegalAgent, ContractAgent, ComplianceAgent, IPAgent
        
        # Documents (9)
        # - DocumentAgent, KnowledgeAgent, WikiAgent, TranslationAgent
        # - DriveAgent, NotionAgent, OCRAgent, PDFAgent
        
        # Media (6)
        # - VisionAgent, AudioAgent, VideoAgent, MusicAgent, ContentAgent, ImageAgent
        
        # Health (2)
        # - NutritionAgent, HealthAgent
        
        # Insurance (3)
        # - InsuranceAgent, RiskAgent, ClaimsAgent
        
        # Web3 (5)
        # - CryptoAgent, NFTAgent, AuctionAgent, BlockchainAgent, DeFiAgent
        
        # PM (1)
        # - TicketRefinementAgent
        
        # Total Layer 3: 62 agents
        
        # ====================================================================
        # LAYER 4: WORKFLOW ORCHESTRATION AGENTS (14 agents)
        # ====================================================================
        
        # Meeting Orchestrator (already migrated)
        self.register(
            name="meeting_orchestrator",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            agent_class=MeetingOrchestratorAgent,
            description="Handle meeting requests end-to-end",
            capabilities=["meeting", "calendar", "email", "prep_doc"],
            dependencies=["email_parser", "calendar", "research", "document"]
        )
        
        # NOTE: Workflow orchestration agents will be registered here
        # They coordinate multi-step workflows
        # Current status: Using legacy BaseAgent (will migrate)
        
        # Communication (5)
        # - EmailAgent, CalendarAgent, ContactAgent, SlackAgent, TeamsAgent
        
        # Development (4)
        # - GitHubAgent, CodeReviewAgent, DeploymentAgent, APIAgent
        
        # Web (4)
        # - ScraperAgent, IntegrationAgent, SEOAgent, WebAgent
        
        # Total Layer 4: 14 agents
        
        # ====================================================================
        # LAYER 5: META-ORCHESTRATION AGENTS (2 agents)
        # ====================================================================
        
        # NOTE: Meta-orchestration agents will be registered here
        # They provide system-wide optimization and learning
        # Current status: Using legacy BaseAgent (will migrate)
        
        # Knowledge (2)
        # - LearningAgent, KnowledgeBaseAgent
        
        # Core (1)
        # - CoreAgent
        
        # Total Layer 5: 2 agents
        
        # ====================================================================
        # TOTAL: 133 agents across 5 layers
        # ====================================================================
        # Layer 1: 43 agents (Data Extraction)
        # Layer 2: 12 agents (Entity Recognition)
        # Layer 3: 62 agents (Domain Experts)
        # Layer 4: 14 agents (Workflow Orchestration)
        # Layer 5: 2 agents (Meta-Orchestration)
        # Infrastructure: 4 agents (Support - not in layers)
        # Platform: 1 agent (Vault - not in layers)
        # ====================================================================
    
    def register(
        self,
        name: str,
        layer: AgentLayer,
        agent_class: Type[Any],
        description: str,
        capabilities: List[str],
        dependencies: List[str],
        enabled: bool = True
    ):
        """Register an agent"""
        entry = AgentRegistryEntry(
            name=name,
            layer=layer,
            agent_class=agent_class,
            description=description,
            capabilities=capabilities,
            dependencies=dependencies,
            enabled=enabled
        )
        
        self._registry[layer][name] = entry
    
    def get_agent_class(self, layer: AgentLayer, name: str) -> Optional[Type[Any]]:
        """Get agent class by layer and name"""
        entry = self._registry[layer].get(name)
        return entry.agent_class if entry and entry.enabled else None
    
    def get_agent_entry(self, layer: AgentLayer, name: str) -> Optional[AgentRegistryEntry]:
        """Get full agent registry entry"""
        return self._registry[layer].get(name)
    
    def list_agents_by_layer(self, layer: AgentLayer) -> List[AgentRegistryEntry]:
        """List all agents in a layer"""
        return [
            entry for entry in self._registry[layer].values()
            if entry.enabled
        ]
    
    def list_all_agents(self) -> List[AgentRegistryEntry]:
        """List all registered agents"""
        all_agents = []
        for layer in AgentLayer:
            all_agents.extend(self.list_agents_by_layer(layer))
        return all_agents
    
    def find_agents_by_capability(self, capability: str) -> List[AgentRegistryEntry]:
        """Find agents that have a specific capability"""
        results = []
        for layer in AgentLayer:
            for entry in self._registry[layer].values():
                if capability in entry.capabilities and entry.enabled:
                    results.append(entry)
        return results
    
    def get_agent_dependencies(self, layer: AgentLayer, name: str) -> List[str]:
        """Get dependencies for an agent"""
        entry = self._registry[layer].get(name)
        return entry.dependencies if entry else []
    
    def validate_dependencies(self, layer: AgentLayer, name: str) -> tuple[bool, List[str]]:
        """
        Validate that all dependencies are registered
        
        Returns:
            (all_valid, missing_dependencies)
        """
        entry = self._registry[layer].get(name)
        if not entry:
            return False, [f"Agent '{name}' not found"]
        
        missing = []
        for dep in entry.dependencies:
            # Check if dependency exists in any layer
            found = False
            for check_layer in AgentLayer:
                if dep in self._registry[check_layer]:
                    found = True
                    break
            if not found:
                missing.append(dep)
        
        return len(missing) == 0, missing
    
    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics"""
        return {
            "layer_1_agents": len(self._registry[AgentLayer.LAYER_1_EXTRACTION]),
            "layer_2_agents": len(self._registry[AgentLayer.LAYER_2_RECOGNITION]),
            "layer_3_agents": len(self._registry[AgentLayer.LAYER_3_DOMAIN]),
            "layer_4_agents": len(self._registry[AgentLayer.LAYER_4_WORKFLOW]),
            "layer_5_agents": len(self._registry[AgentLayer.LAYER_5_META]),
            "total_agents": sum(
                len(agents) for agents in self._registry.values()
            )
        }
    
    def print_registry(self):
        """Print formatted registry"""
        print("\n" + "="*80)
        print("APOLLO AGENT REGISTRY")
        print("="*80 + "\n")
        
        for layer in AgentLayer:
            agents = self.list_agents_by_layer(layer)
            if not agents:
                continue
            
            print(f"\n{layer.name} ({len(agents)} agents)")
            print("-" * 80)
            
            for entry in agents:
                status = "✅" if entry.enabled else "❌"
                print(f"{status} {entry.name}")
                print(f"   Description: {entry.description}")
                print(f"   Capabilities: {', '.join(entry.capabilities)}")
                if entry.dependencies:
                    print(f"   Dependencies: {', '.join(entry.dependencies)}")
                print()
        
        stats = self.get_stats()
        print("\n" + "="*80)
        print(f"TOTAL: {stats['total_agents']} agents registered")
        print("="*80 + "\n")


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_registry_instance: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get singleton registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = AgentRegistry()
    return _registry_instance


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def list_layer1_agents() -> List[str]:
    """List all Layer 1 agent names"""
    registry = get_registry()
    return [e.name for e in registry.list_agents_by_layer(AgentLayer.LAYER_1_EXTRACTION)]


def list_layer2_agents() -> List[str]:
    """List all Layer 2 agent names"""
    registry = get_registry()
    return [e.name for e in registry.list_agents_by_layer(AgentLayer.LAYER_2_RECOGNITION)]


def list_layer3_agents() -> List[str]:
    """List all Layer 3 agent names"""
    registry = get_registry()
    return [e.name for e in registry.list_agents_by_layer(AgentLayer.LAYER_3_DOMAIN)]


def list_layer4_agents() -> List[str]:
    """List all Layer 4 agent names"""
    registry = get_registry()
    return [e.name for e in registry.list_agents_by_layer(AgentLayer.LAYER_4_WORKFLOW)]


def list_layer5_agents() -> List[str]:
    """List all Layer 5 agent names"""
    registry = get_registry()
    return [e.name for e in registry.list_agents_by_layer(AgentLayer.LAYER_5_META)]


def find_agents_for_task(task_type: str) -> List[str]:
    """Find agents that can handle a task type"""
    registry = get_registry()
    agents = registry.find_agents_by_capability(task_type)
    return [e.name for e in agents]
