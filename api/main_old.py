"""
Apollo API Server - Main entry point

Provides analysis endpoints for Atlas to call during data ingestion.
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

from agents import EmailAgent, LedgerAgent, GitHubAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Apollo AI System",
    description="All-in-one AI system with 42+ agents, Agentic RAG, and Theta GPU integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize all agents
from agents import AGENT_REGISTRY, get_agent, list_agents
from agents import NutritionAgent, HealthAgent, TravelAgent

# Initialize Meta-Orchestrator
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agentic.orchestrator.meta_orchestrator import MetaOrchestrator

meta_orchestrator = MetaOrchestrator(AGENT_REGISTRY)

logger.info("🚀 Apollo AI System initialized")
logger.info(f"  🤖 {len(AGENT_REGISTRY)} agents loaded")
logger.info("  🧠 Meta-Orchestrator ready")


# ============================================================================
# Request/Response Models
# ============================================================================

class ParsedEmail(BaseModel):
    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: str
    has_attachments: bool = False


class ParsedTransaction(BaseModel):
    amount: float
    date: str
    description: str
    account: str


class CodeFile(BaseModel):
    path: str
    content: str
    language: str


class ParsedDocument(BaseModel):
    title: str
    content: str
    document_type: str


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Apollo AI System",
        "agents": ["EmailAgent", "LedgerAgent", "GitHubAgent", "...39 more"],
        "version": "1.0.0"
    }


# ============================================================================
# Analysis Endpoints (for Atlas ingestion)
# ============================================================================

@app.post("/analyze/email")
async def analyze_email(email: ParsedEmail) -> Dict[str, Any]:
    """
    Analyze email with EmailAgent
    
    Returns: EmailIntelligence
    """
    try:
        logger.info(f"📧 Analyzing email: {email.subject}")
        
        intelligence = await email_agent.analyze(email.dict())
        
        logger.info(f"  ✅ Analysis complete - Urgency: {intelligence['urgency']}")
        
        return intelligence
        
    except Exception as e:
        logger.error(f"❌ Email analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/transaction")
async def analyze_transaction(transaction: ParsedTransaction) -> Dict[str, Any]:
    """
    Analyze transaction with LedgerAgent
    
    Returns: TransactionIntelligence
    """
    try:
        logger.info(f"💰 Analyzing transaction: {transaction.description}")
        
        intelligence = await ledger_agent.analyze(transaction.dict())
        
        logger.info(f"  ✅ Analysis complete - Category: {intelligence['category']}")
        
        return intelligence
        
    except Exception as e:
        logger.error(f"❌ Transaction analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/code")
async def analyze_code(code: CodeFile) -> Dict[str, Any]:
    """
    Analyze code with GitHubAgent
    
    Returns: CodeIntelligence
    """
    try:
        logger.info(f"💻 Analyzing code: {code.path}")
        
        intelligence = await github_agent.analyze(code.dict())
        
        logger.info(f"  ✅ Analysis complete - Complexity: {intelligence['complexity']}")
        
        return intelligence
        
    except Exception as e:
        logger.error(f"❌ Code analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/document")
async def analyze_document(document: ParsedDocument) -> Dict[str, Any]:
    """
    Analyze document with KnowledgeAgent
    
    Returns: DocumentIntelligence
    """
    try:
        logger.info(f"📄 Analyzing document: {document.title}")
        
        # Placeholder - KnowledgeAgent to be implemented
        intelligence = {
            "summary": f"Summary of {document.title}",
            "entities": [],
            "topics": [],
            "sentiment": "neutral",
            "key_dates": []
        }
        
        logger.info(f"  ✅ Analysis complete")
        
        return intelligence
        
    except Exception as e:
        logger.error(f"❌ Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Query Endpoints (for user queries)
# ============================================================================

@app.post("/query")
async def query(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle natural language query using Meta-Orchestrator
    
    The Meta-Orchestrator will:
    1. Analyze the query
    2. Select appropriate agents
    3. Coordinate execution
    4. Combine results
    """
    try:
        query_text = request.get("query", "")
        user_id = request.get("user_id", "")
        entity_id = request.get("entity_id", "")
        context = request.get("context", {})
        
        logger.info(f"🔍 Query from {user_id}: {query_text}")
        
        # Use Meta-Orchestrator
        response = await meta_orchestrator.process_query(
            query=query_text,
            context={**context, "user_id": user_id, "entity_id": entity_id},
            user_id=user_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/{agent_name}")
async def analyze_with_agent(agent_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze data with a specific agent
    
    Universal endpoint for all 42 agents
    """
    try:
        logger.info(f"🤖 Analyzing with {agent_name}")
        
        # Get agent
        agent = get_agent(agent_name)
        
        # Analyze
        result = await agent.analyze(data)
        
        return {
            "agent": agent_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Agent Management
# ============================================================================

@app.get("/agents")
async def get_agents_list() -> Dict[str, Any]:
    """List all available agents by category"""
    agents_by_category = list_agents()
    
    # Flatten into list with metadata
    all_agents = []
    for category, agent_names in agents_by_category.items():
        for agent_name in agent_names:
            all_agents.append({
                "name": agent_name,
                "category": category,
                "status": "active",
                "endpoint": f"/analyze/{agent_name}"
            })
    
    return {
        "total": len(all_agents),
        "agents": all_agents,
        "by_category": agents_by_category
    }


@app.get("/orchestrator/stats")
async def get_orchestrator_stats() -> Dict[str, Any]:
    """Get Meta-Orchestrator statistics"""
    return meta_orchestrator.get_stats()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8002"))
    
    logger.info(f"🚀 Starting Apollo API Server on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
