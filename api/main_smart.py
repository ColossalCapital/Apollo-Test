"""
Apollo API Server with Smart Agents (Tier 2 LLM-Powered)

Provides both static and LLM-powered analysis endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import smart agents
from agents.finance.strategy_agent_smart import SmartStrategyAgent
from agents.finance.portfolio_agent_smart import SmartPortfolioAgent
from agents.finance.sentiment_agent_smart import SmartSentimentAgent
from agents.finance.backtest_agent_smart import SmartBacktestAgent

# Import regular agents
from agents import AGENT_REGISTRY, get_agent, list_agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Apollo AI System (Smart Agents)",
    description="AI system with 61 agents + Tier 2 LLM-powered intelligence",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize smart agents
smart_strategy_agent = SmartStrategyAgent()
smart_portfolio_agent = SmartPortfolioAgent()
smart_sentiment_agent = SmartSentimentAgent()
smart_backtest_agent = SmartBacktestAgent()

logger.info("🚀 Apollo AI System (Smart Agents) initialized")
logger.info(f"  🤖 {len(AGENT_REGISTRY)} regular agents loaded")
logger.info(f"  🧠 4 smart agents (LLM-powered) loaded")
logger.info(f"  ⚡ Tier 2 intelligence enabled")


# ============================================================================
# Request/Response Models
# ============================================================================

class QueryRequest(BaseModel):
    query: str
    user_id: str
    entity_id: str
    context: Optional[str] = None  # "atlas", "delt", "akashic"


class AnalyzeRequest(BaseModel):
    data: Dict[str, Any]


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Apollo AI System (Smart Agents)",
        "version": "2.0.0",
        "agents": {
            "regular": len(AGENT_REGISTRY),
            "smart": 4,
            "total": len(AGENT_REGISTRY) + 4
        },
        "tier2_enabled": True
    }


@app.get("/agents")
async def get_agents_list():
    """List all available agents"""
    regular_agents = list_agents()
    smart_agents = {
        "smart": ["strategy_smart", "portfolio_smart", "sentiment_smart", "backtest_smart"]
    }
    
    return {
        "regular_agents": regular_agents,
        "smart_agents": smart_agents,
        "total": len(AGENT_REGISTRY) + 4
    }


# ============================================================================
# Smart Agent Endpoints (Tier 2 LLM-Powered)
# ============================================================================

@app.post("/analyze/strategy_smart")
async def analyze_strategy_smart(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze trading strategy with LLM intelligence
    
    Request body:
    {
        "data": {
            "type": "turtle_trading",
            "asset": "BTC",
            "price_data": {
                "current_price": 45000,
                "20_day_high": 44500,
                "atr": 2500
            },
            "quick_mode": false
        }
    }
    
    Returns:
    - mode: "static" | "llm_powered" | "static_fallback"
    - static_knowledge: {...}
    - llm_analysis: {...} (if LLM available)
    - recommendation: "BUY" | "SELL" | "HOLD"
    - confidence: 0.0-1.0
    """
    try:
        logger.info(f"🧠 Smart Strategy Analysis: {request.data.get('type', 'unknown')}")
        
        result = await smart_strategy_agent.analyze(request.data)
        
        logger.info(f"  ✅ Mode: {result['mode']}")
        if result['mode'] == 'llm_powered':
            logger.info(f"  📊 Recommendation: {result.get('recommendation', 'N/A')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Smart strategy analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/portfolio_smart")
async def analyze_portfolio_smart(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Optimize portfolio with LLM intelligence
    
    Request body:
    {
        "data": {
            "type": "optimize",
            "portfolio": {
                "BTC": 0.4,
                "ETH": 0.3,
                "STOCKS": 0.2,
                "BONDS": 0.1
            },
            "user_profile": {
                "risk_tolerance": "moderate",
                "investment_horizon": "medium",
                "goals": ["growth", "preservation"]
            }
        }
    }
    
    Returns:
    - optimized_portfolio: {...}
    - expected_return: float
    - sharpe_ratio: float
    - reasoning: str
    """
    try:
        logger.info(f"🧠 Smart Portfolio Analysis: {request.data.get('type', 'optimize')}")
        
        result = await smart_portfolio_agent.analyze(request.data)
        
        logger.info(f"  ✅ Mode: {result['mode']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Smart portfolio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/sentiment_smart")
async def analyze_sentiment_smart(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze market sentiment with LLM intelligence
    
    Request body:
    {
        "data": {
            "asset": "BTC",
            "news_headlines": [
                "Bitcoin breaks $45,000",
                "Institutional adoption grows"
            ],
            "social_data": {
                "twitter_sentiment": 0.75,
                "reddit_mentions": 2500
            }
        }
    }
    
    Returns:
    - overall_sentiment: "BULLISH" | "BEARISH" | "NEUTRAL"
    - trading_signal: "BUY" | "SELL" | "HOLD"
    - key_factors: [...]
    - confidence: 0.0-1.0
    """
    try:
        logger.info(f"🧠 Smart Sentiment Analysis: {request.data.get('asset', 'unknown')}")
        
        result = await smart_sentiment_agent.analyze(request.data)
        
        logger.info(f"  ✅ Mode: {result['mode']}")
        if result['mode'] == 'llm_powered':
            logger.info(f"  📊 Sentiment: {result.get('sentiment', 'N/A')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Smart sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/backtest_smart")
async def analyze_backtest_smart(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze backtest results with LLM intelligence
    
    Request body:
    {
        "data": {
            "backtest_results": {
                "total_return": 0.45,
                "sharpe_ratio": 1.2,
                "max_drawdown": 0.18,
                "win_rate": 0.58
            },
            "strategy_params": {
                "entry": "20-day high",
                "exit": "10-day low"
            }
        }
    }
    
    Returns:
    - overall_assessment: "EXCELLENT" | "GOOD" | "POOR"
    - strengths: [...]
    - weaknesses: [...]
    - improvement_suggestions: [...]
    """
    try:
        logger.info(f"🧠 Smart Backtest Analysis")
        
        result = await smart_backtest_agent.analyze(request.data)
        
        logger.info(f"  ✅ Mode: {result['mode']}")
        if result['mode'] == 'llm_powered':
            logger.info(f"  📊 Assessment: {result.get('assessment', 'N/A')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Smart backtest analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Universal Agent Endpoint
# ============================================================================

@app.post("/analyze/{agent_name}")
async def analyze_with_agent(agent_name: str, request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Universal endpoint for any agent
    
    Supports both regular and smart agents
    """
    try:
        # Check if it's a smart agent
        if agent_name == "strategy_smart":
            return await analyze_strategy_smart(request)
        elif agent_name == "portfolio_smart":
            return await analyze_portfolio_smart(request)
        elif agent_name == "sentiment_smart":
            return await analyze_sentiment_smart(request)
        elif agent_name == "backtest_smart":
            return await analyze_backtest_smart(request)
        
        # Regular agent
        if agent_name not in AGENT_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        logger.info(f"🤖 Analyzing with {agent_name}")
        
        agent = get_agent(agent_name)
        result = await agent.analyze(request.data)
        
        logger.info(f"  ✅ Analysis complete")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Natural Language Query Endpoint
# ============================================================================

@app.post("/query")
async def query_apollo(request: QueryRequest) -> Dict[str, Any]:
    """
    Natural language query to Apollo
    
    Uses Meta-Orchestrator to route to appropriate agent(s)
    """
    try:
        logger.info(f"💬 Query: {request.query[:50]}...")
        
        # TODO: Implement Meta-Orchestrator routing
        # For now, return placeholder
        
        return {
            "answer": f"Received query: {request.query}",
            "sources": [],
            "suggestions": [
                "Try asking about specific trading strategies",
                "Ask for portfolio optimization",
                "Request market sentiment analysis"
            ],
            "confidence": 0.5
        }
        
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 80)
    logger.info("🚀 Starting Apollo AI System (Smart Agents)")
    logger.info("=" * 80)
    logger.info(f"  📍 URL: http://localhost:8002")
    logger.info(f"  📚 Docs: http://localhost:8002/docs")
    logger.info(f"  🤖 Agents: {len(AGENT_REGISTRY) + 4}")
    logger.info(f"  🧠 Tier 2 LLM: Enabled")
    logger.info("=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
