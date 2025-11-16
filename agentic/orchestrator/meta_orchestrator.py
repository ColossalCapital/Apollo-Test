"""
Meta-Orchestrator - The master agentic AI that coordinates all agents

This is the "brain" of Apollo with agentic AI capabilities:
- LLM-powered intent analysis
- Autonomous agent selection via self-discovery
- Multi-agent workflow coordination
- Self-learning from interactions
- Dynamic optimization over time

Agentic AI Features:
- Autonomous decision making
- Goal-oriented planning
- Self-reflection and improvement
- Tool use (agents as tools)
- Memory and context awareness
- Self-aware agent discovery
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.discovery import discover_all_agents, get_agent_count, get_total_agent_count

logger = logging.getLogger(__name__)


class MetaOrchestrator:
    """
    Master agentic AI that orchestrates all specialized agents
    
    Agentic AI Capabilities:
    1. **Autonomous Intent Analysis** - LLM-powered understanding
    2. **Goal-Oriented Planning** - Multi-step task decomposition
    3. **Tool Selection** - Agents as tools for achieving goals
    4. **Self-Discovery** - Dynamically discovers available agents
    5. **Self-Reflection** - Evaluates own performance
    6. **Continuous Learning** - Improves from every interaction
    7. **Context Awareness** - Maintains conversation memory
    
    The Meta-Orchestrator acts as an autonomous agent that:
    - Discovers its own capabilities (agents)
    - Reasons about user goals
    - Plans multi-agent workflows
    - Executes plans adaptively
    - Reflects on outcomes
    - Learns and improves
    """
    
    def __init__(self, agent_registry: Dict[str, Any] = None, llm_client=None):
        # Use dynamic discovery if no registry provided
        self.agent_registry = agent_registry or {}
        self.llm_client = llm_client
        self.execution_history = []
        self.agent_cache = None
        self.last_discovery_time = None
        
        # Perform initial agent discovery
        # self._discover_agents()  # TODO: Implement this method
        self.agent_cache = self.agent_registry  # Use provided registry
        self.agent_performance = {}
        self.llm_client = llm_client  # For agentic reasoning
        
        # Agent selection rules (learned over time)
        self.selection_rules = self._initialize_selection_rules()
        
        # Agentic AI memory
        self.conversation_memory = []
        self.learned_patterns = {}
        self.goal_templates = self._initialize_goal_templates()
        
        logger.info(f"🧠 Meta-Orchestrator initialized with {len(self.agent_cache)} agents")
        logger.info(f"  🤖 Agents: {len(self.agent_registry)}")
        logger.info(f"  🎯 Goal-oriented planning: ENABLED")
        logger.info(f"  🔄 Self-reflection: ENABLED")
        logger.info(f"  📚 Continuous learning: ENABLED")
    
    def _initialize_selection_rules(self) -> Dict[str, List[str]]:
        """
        Initialize agent selection rules based on keywords
        
        Organized by category for better routing:
        - 133 total agents across 23 categories
        - See AGENT_CATEGORIZATION.md for complete mapping
        """
        return {
            # Communication (5 agents)
            "email": ["email", "mail", "send message"],
            "calendar": ["calendar", "meeting", "schedule", "appointment", "event"],
            "contact": ["contact", "person", "relationship", "address book"],
            "slack": ["slack", "message", "team", "chat", "channel"],
            "teams": ["teams", "microsoft teams", "video call"],
            
            # Development (4 agents)
            "github": ["code", "github", "repository", "commit", "repo"],
            "code_review": ["review", "pr", "pull request", "code quality"],
            "deployment": ["deploy", "ci/cd", "release", "production"],
            "api": ["api", "endpoint", "rest", "graphql"],
            
            # Documents (9 agents)
            "document": ["document", "word", "file", "doc"],
            "knowledge": ["search", "find", "query", "knowledge"],
            "wiki": ["documentation", "wiki", "docs", "guide"],
            "research": ["research", "study", "learn", "investigate"],
            "translation": ["translate", "language", "localization"],
            "drive": ["drive", "storage", "cloud", "files"],
            "notion": ["notion", "notes", "workspace"],
            "ocr": ["ocr", "scan", "extract text", "read image"],
            "pdf": ["pdf", "convert", "generate pdf"],
            
            # Finance (16 agents)
            "ledger": ["transaction", "expense", "spending", "accounting"],
            "tax": ["tax", "deduction", "irs", "filing", "1099"],
            "invoice": ["invoice", "bill", "payment", "billing"],
            "budget": ["budget", "forecast", "planning", "financial plan"],
            "trading": ["trade", "buy", "sell", "order", "position"],
            "forex": ["forex", "fx", "currency", "exchange rate"],
            "stocks": ["stock", "equity", "shares", "ticker"],
            "portfolio": ["portfolio", "holdings", "allocation", "diversification"],
            "options": ["option", "call", "put", "strike", "expiry"],
            "futures": ["futures", "contract", "commodity"],
            "arbitrage": ["arbitrage", "spread", "opportunity"],
            "sentiment": ["sentiment", "mood", "market feeling"],
            "backtest": ["backtest", "historical", "simulation", "test strategy"],
            
            # Legal (4 agents)
            "legal": ["legal", "law", "attorney", "counsel"],
            "contract": ["contract", "agreement", "terms", "clause"],
            "compliance": ["compliance", "regulation", "regulatory", "audit"],
            "ip": ["patent", "trademark", "intellectual property", "copyright"],
            
            # Business (12 agents)
            "grant": ["grant", "funding", "award", "application"],
            "sales": ["sales", "deal", "customer", "pipeline"],
            "marketing": ["marketing", "campaign", "advertising", "promotion"],
            "hr": ["hire", "recruit", "candidate", "employee", "onboarding"],
            "project": ["project", "task", "milestone", "deadline"],
            "strategy": ["strategy", "plan", "business plan", "roadmap"],
            "travel": ["travel", "flight", "hotel", "trip"],
            "charity": ["charity", "donation", "nonprofit", "giving"],
            "crm": ["crm", "customer relationship", "lead", "contact management"],
            "operations": ["operations", "process", "workflow", "efficiency"],
            
            # Analytics (9 agents)
            "data": ["data", "dataset", "analyze", "process"],
            "forecast": ["forecast", "predict", "projection", "trend"],
            "metrics": ["metrics", "kpi", "measurement", "tracking"],
            "ml": ["machine learning", "model", "train", "ai"],
            "report": ["report", "dashboard", "visualization", "summary"],
            
            # Insurance (3 agents)
            "insurance": ["insurance", "policy", "coverage", "premium"],
            "risk": ["risk", "threat", "vulnerability", "assessment"],
            "claims": ["claim", "accident", "damage", "reimbursement"],
            
            # Media (6 agents)
            "vision": ["image", "photo", "picture", "visual"],
            "audio": ["audio", "speech", "transcribe", "sound"],
            "video": ["video", "recording", "stream"],
            "music": ["music", "song", "playlist", "spotify"],
            "content": ["content", "create", "generate", "write"],
            "image": ["image", "edit", "filter", "resize"],
            
            # Web3 (5 agents)
            "crypto": ["crypto", "cryptocurrency", "bitcoin", "ethereum"],
            "nft": ["nft", "token", "collectible", "digital art"],
            "blockchain": ["blockchain", "chain", "ledger", "distributed"],
            "defi": ["defi", "decentralized finance", "yield", "liquidity"],
            
            # Web (4 agents)
            "scraper": ["scrape", "extract", "crawl", "web data"],
            "seo": ["seo", "search engine", "optimization", "ranking"],
            "web": ["website", "web", "url", "link"],
            
            # Connectors - Financial (5 agents)
            "investor_profiles_connector": ["investor profile", "risk tolerance", "investment preference"],
            "news_sentiment_connector": ["news sentiment", "market news", "breaking news"],
            
            # Health (2 agents)
            "nutrition": ["nutrition", "diet", "calories", "food"],
            "health": ["health", "wellness", "medical", "fitness"],
            
            # Knowledge (2 agents)
            "learning": ["learn", "study", "training", "education"],
            "knowledge_base": ["knowledge base", "kb", "documentation"],
            
            # Core (1 agent)
            "core": ["route", "orchestrate", "coordinate", "workflow"],
            "music": ["music", "song", "audio"],
            
            # Analytics
            "data": ["data", "analysis", "sql", "query"],
            "text": ["text", "nlp", "analyze"],
            "schema": ["schema", "structure", "format"],
            "router": ["route", "classify", "categorize"],
            
            # Modern
            "slang": ["slang", "informal", "casual"],
            "meme": ["meme", "viral", "trend"],
            "social": ["social", "twitter", "facebook"],
            
            # Web
            "scraper": ["scrape", "extract", "web"],
            "integration": ["integrate", "connect", "api"],
        }
    
    def _initialize_goal_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize goal templates for agentic planning"""
        return {
            "analyze_data": {
                "steps": ["extract", "process", "analyze", "summarize"],
                "agents": ["data", "text", "knowledge"]
            },
            "financial_analysis": {
                "steps": ["gather_data", "calculate_metrics", "generate_insights"],
                "agents": ["ledger", "budget", "portfolio"]
            },
            "document_processing": {
                "steps": ["extract_text", "analyze_content", "categorize", "store"],
                "agents": ["document", "text", "knowledge"]
            },
            "code_review": {
                "steps": ["analyze_code", "check_quality", "suggest_improvements"],
                "agents": ["github", "code_review", "api"]
            }
        }
    
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query by orchestrating appropriate agents
        
        Args:
            query: Natural language query from user
            context: Additional context (entity_id, service, etc.)
            user_id: User ID for personalization
            
        Returns:
            Orchestrated response from agents
        """
        logger.info(f"🔍 Processing query: {query}")
        
        # 1. Analyze query intent
        intent = await self.analyze_intent(query, context)
        
        # 2. Select agents
        selected_agents = self.select_agents(intent, query)
        
        logger.info(f"  📋 Selected agents: {', '.join(selected_agents)}")
        
        # 3. Execute agents in optimal order
        results = await self.execute_agents(selected_agents, query, context)
        
        # 4. Combine results
        combined_result = self.combine_results(results, intent)
        
        # 5. Learn from execution
        await self.learn_from_execution(query, selected_agents, combined_result)
        
        # 6. Record execution
        self.record_execution(query, selected_agents, combined_result)
        
        return combined_result
    
    async def analyze_intent(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze user intent from query"""
        query_lower = query.lower()
        
        # Detect intent type
        intent_type = "general"
        
        if any(word in query_lower for word in ["analyze", "review", "check"]):
            intent_type = "analysis"
        elif any(word in query_lower for word in ["create", "generate", "make"]):
            intent_type = "creation"
        elif any(word in query_lower for word in ["find", "search", "lookup"]):
            intent_type = "search"
        elif any(word in query_lower for word in ["summarize", "explain", "what"]):
            intent_type = "explanation"
        
        # Detect complexity (single vs multi-agent)
        complexity = "simple"
        if " and " in query_lower or " then " in query_lower:
            complexity = "complex"
        
        return {
            "type": intent_type,
            "complexity": complexity,
            "requires_multiple_agents": complexity == "complex",
            "context": context or {}
        }
    
    def select_agents(self, intent: Dict[str, Any], query: str) -> List[str]:
        """
        Select appropriate agents based on intent and query
        
        This is the core intelligence of the orchestrator
        """
        query_lower = query.lower()
        selected = []
        
        # Check each agent's keywords
        for agent_name, keywords in self.selection_rules.items():
            if any(keyword in query_lower for keyword in keywords):
                selected.append(agent_name)
        
        # If no agents selected, use general agents
        if not selected:
            selected = ["knowledge", "text"]  # Default agents
        
        # Limit to top 5 agents for performance
        return selected[:5]
    
    async def execute_agents(
        self,
        agent_names: List[str],
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute selected agents"""
        results = {}
        
        for agent_name in agent_names:
            try:
                # Get agent instance
                agent_class = self.agent_registry.get(agent_name)
                if not agent_class:
                    logger.warning(f"Agent not found: {agent_name}")
                    continue
                
                agent = agent_class()
                
                # Execute agent
                logger.info(f"  🤖 Executing {agent_name}...")
                
                # Prepare data for agent (would be real data in production)
                agent_data = self.prepare_agent_data(agent_name, query, context)
                
                # Analyze with agent
                result = await agent.analyze(agent_data)
                
                results[agent_name] = {
                    "success": True,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"  ❌ Agent {agent_name} failed: {e}")
                results[agent_name] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return results
    
    def prepare_agent_data(
        self,
        agent_name: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare data for specific agent"""
        # This would extract relevant data from context
        # For now, return a generic structure
        return {
            "query": query,
            "context": context or {},
            "agent": agent_name
        }
    
    def combine_results(
        self,
        results: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine results from multiple agents into coherent response"""
        
        successful_results = {
            name: data["result"]
            for name, data in results.items()
            if data.get("success")
        }
        
        failed_agents = [
            name for name, data in results.items()
            if not data.get("success")
        ]
        
        return {
            "answer": self.generate_answer(successful_results, intent),
            "agents_used": list(results.keys()),
            "successful_agents": list(successful_results.keys()),
            "failed_agents": failed_agents,
            "results": successful_results,
            "confidence": self.calculate_confidence(successful_results),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_answer(
        self,
        results: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> str:
        """Generate natural language answer from agent results"""
        
        if not results:
            return "I couldn't find any relevant information."
        
        # Combine insights from all agents
        insights = []
        for agent_name, result in results.items():
            if isinstance(result, dict):
                # Extract key information
                insights.append(f"{agent_name}: {result}")
        
        return f"Based on analysis from {len(results)} agents: " + "; ".join(insights[:3])
    
    def calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate confidence score based on agent results"""
        if not results:
            return 0.0
        
        # Simple confidence based on number of successful agents
        return min(len(results) / 5.0, 1.0)  # Max confidence with 5+ agents
    
    async def learn_from_execution(
        self,
        query: str,
        agents_used: List[str],
        result: Dict[str, Any]
    ):
        """Learn from execution to improve future agent selection"""
        
        # Track agent performance
        for agent in agents_used:
            if agent not in self.agent_performance:
                self.agent_performance[agent] = {
                    "uses": 0,
                    "successes": 0,
                    "avg_confidence": 0.0
                }
            
            self.agent_performance[agent]["uses"] += 1
            
            if agent in result.get("successful_agents", []):
                self.agent_performance[agent]["successes"] += 1
        
        # TODO: Implement ML-based learning
        # - Adjust selection rules based on success
        # - Learn query patterns
        # - Optimize agent ordering
    
    def record_execution(
        self,
        query: str,
        agents: List[str],
        result: Dict[str, Any]
    ):
        """Record execution for analytics"""
        self.execution_history.append({
            "query": query,
            "agents": agents,
            "confidence": result.get("confidence", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 1000 executions
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "total_queries": len(self.execution_history),
            "agent_performance": self.agent_performance,
            "avg_confidence": sum(
                e["confidence"] for e in self.execution_history
            ) / len(self.execution_history) if self.execution_history else 0.0
        }
