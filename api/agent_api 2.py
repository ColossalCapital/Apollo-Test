"""
Apollo Agent API - Core agent execution endpoints

Provides REST API for executing all 147 agents with comprehensive metadata support.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from enum import Enum
import httpx
import json

# Import agent registry
from ..agents import get_agent_by_name, list_agents, get_agents_by_filter

app = FastAPI(title="Apollo Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to Atlas/Delt/Akashic domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AppContext(str, Enum):
    ATLAS = "atlas"
    DELT = "delt"
    AKASHIC = "akashic"
    ALL = "all"


class EntityType(str, Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    TRADING_FIRM = "trading_firm"
    UNIVERSAL = "universal"


class AgentExecuteRequest(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]
    user_id: str
    org_id: Optional[str] = None
    team_id: Optional[str] = None
    app_context: AppContext
    entity_type: EntityType
    privacy_level: str = "private"


class AgentExecuteResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    execution_time_ms: float
    agent_name: str
    agent_version: str


class AgentListRequest(BaseModel):
    app_context: Optional[AppContext] = None
    entity_type: Optional[EntityType] = None
    category: Optional[str] = None
    requires_subscription: Optional[List[str]] = None
    search: Optional[str] = None


class AgentMetadataResponse(BaseModel):
    name: str
    layer: str
    version: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    entity_types: List[str]
    app_contexts: List[str]
    requires_subscription: List[str]
    byok_enabled: bool
    wtf_purchasable: bool
    estimated_cost_per_call: Optional[float]
    avg_response_time_ms: Optional[int]
    category: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    documentation_url: Optional[str]
    example_use_cases: List[str]


# ============================================================================
# CORE AGENT ENDPOINTS
# ============================================================================

@app.post("/agents/execute", response_model=AgentExecuteResponse)
async def execute_agent(request: AgentExecuteRequest):
    """
    Execute any agent by name
    
    This is the primary endpoint for running agents. It handles:
    - Agent lookup and validation
    - Permission checking
    - Input validation
    - Execution
    - Result formatting
    """
    
    try:
        # Get agent
        agent = get_agent_by_name(request.agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")
        
        # Check permissions
        metadata = agent.metadata
        
        # Check app context
        if request.app_context.value not in [ctx.value for ctx in metadata.app_contexts]:
            if AppContext.ALL not in metadata.app_contexts:
                raise HTTPException(
                    status_code=403,
                    detail=f"Agent not available in {request.app_context.value} context"
                )
        
        # Check entity type
        if request.entity_type.value not in [et.value for et in metadata.entity_types]:
            if EntityType.UNIVERSAL not in metadata.entity_types:
                raise HTTPException(
                    status_code=403,
                    detail=f"Agent not available for {request.entity_type.value} entity type"
                )
        
        # Execute agent
        import time
        start_time = time.time()
        
        # Route to appropriate execution method based on layer
        if hasattr(agent, 'extract'):
            result = await agent.extract(request.input_data)
        elif hasattr(agent, 'recognize'):
            result = await agent.recognize(request.input_data)
        elif hasattr(agent, 'analyze'):
            result = await agent.analyze(request.input_data)
        elif hasattr(agent, 'orchestrate'):
            result = await agent.orchestrate(request.input_data)
        elif hasattr(agent, 'optimize'):
            result = await agent.optimize(request.input_data)
        elif hasattr(agent, 'execute_autonomous_cycle'):
            result = await agent.execute_autonomous_cycle()
        elif hasattr(agent, 'execute_swarm'):
            result = await agent.execute_swarm(request.input_data)
        elif hasattr(agent, 'connect'):
            result = await agent.connect(request.input_data)
        else:
            raise HTTPException(status_code=500, detail="Agent has no executable method")
        
        execution_time = (time.time() - start_time) * 1000
        
        return AgentExecuteResponse(
            success=result.success,
            data=result.data,
            metadata=result.metadata,
            execution_time_ms=execution_time,
            agent_name=metadata.name,
            agent_version=metadata.version
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/batch", response_model=List[AgentExecuteResponse])
async def execute_agents_batch(requests: List[AgentExecuteRequest]):
    """
    Execute multiple agents in parallel
    
    Useful for workflows that need multiple agents to run simultaneously.
    """
    
    import asyncio
    
    async def execute_single(req: AgentExecuteRequest):
        try:
            return await execute_agent(req)
        except Exception as e:
            return AgentExecuteResponse(
                success=False,
                data={},
                metadata={"error": str(e)},
                execution_time_ms=0,
                agent_name=req.agent_name,
                agent_version="unknown"
            )
    
    results = await asyncio.gather(*[execute_single(req) for req in requests])
    return results


@app.post("/agents/list", response_model=List[AgentMetadataResponse])
async def list_agents_filtered(request: AgentListRequest):
    """
    List agents with filtering
    
    Supports filtering by:
    - App context (atlas, delt, akashic)
    - Entity type (personal, business, trading_firm, universal)
    - Category (communication, finance, health, etc.)
    - Subscription requirements
    - Search query
    """
    
    filters = {}
    
    if request.app_context:
        filters['app_context'] = request.app_context.value
    
    if request.entity_type:
        filters['entity_type'] = request.entity_type.value
    
    if request.category:
        filters['category'] = request.category
    
    if request.requires_subscription:
        filters['requires_subscription'] = request.requires_subscription
    
    if request.search:
        filters['search'] = request.search
    
    agents = get_agents_by_filter(**filters)
    
    return [
        AgentMetadataResponse(
            name=agent.metadata.name,
            layer=agent.metadata.layer.name,
            version=agent.metadata.version,
            description=agent.metadata.description,
            capabilities=agent.metadata.capabilities,
            dependencies=agent.metadata.dependencies or [],
            entity_types=[et.value for et in agent.metadata.entity_types] if agent.metadata.entity_types else [],
            app_contexts=[ac.value for ac in agent.metadata.app_contexts] if agent.metadata.app_contexts else [],
            requires_subscription=agent.metadata.requires_subscription or [],
            byok_enabled=agent.metadata.byok_enabled,
            wtf_purchasable=agent.metadata.wtf_purchasable,
            estimated_cost_per_call=agent.metadata.estimated_cost_per_call,
            avg_response_time_ms=agent.metadata.avg_response_time_ms,
            category=agent.metadata.category.value if agent.metadata.category else None,
            icon=agent.metadata.icon,
            color=agent.metadata.color,
            documentation_url=agent.metadata.documentation_url,
            example_use_cases=agent.metadata.example_use_cases or []
        )
        for agent in agents
    ]


@app.get("/agents/{agent_name}/metadata", response_model=AgentMetadataResponse)
async def get_agent_metadata(agent_name: str):
    """Get detailed metadata for a specific agent"""
    
    agent = get_agent_by_name(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    metadata = agent.metadata
    
    return AgentMetadataResponse(
        name=metadata.name,
        layer=metadata.layer.name,
        version=metadata.version,
        description=metadata.description,
        capabilities=metadata.capabilities,
        dependencies=metadata.dependencies or [],
        entity_types=[et.value for et in metadata.entity_types] if metadata.entity_types else [],
        app_contexts=[ac.value for ac in metadata.app_contexts] if metadata.app_contexts else [],
        requires_subscription=metadata.requires_subscription or [],
        byok_enabled=metadata.byok_enabled,
        wtf_purchasable=metadata.wtf_purchasable,
        estimated_cost_per_call=metadata.estimated_cost_per_call,
        avg_response_time_ms=metadata.avg_response_time_ms,
        category=metadata.category.value if metadata.category else None,
        icon=metadata.icon,
        color=metadata.color,
        documentation_url=metadata.documentation_url,
        example_use_cases=metadata.example_use_cases or []
    )


@app.get("/agents/{agent_name}/health")
async def check_agent_health(agent_name: str):
    """Check health status of an agent"""
    
    agent = get_agent_by_name(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    # Basic health check
    return {
        "status": "healthy",
        "agent": agent_name,
        "version": agent.metadata.version,
        "uptime": "unknown",  # Would track actual uptime
        "last_execution": "unknown",  # Would track last execution
        "error_rate": 0.0  # Would track actual error rate
    }


@app.post("/agents/{agent_name}/train")
async def trigger_agent_training(agent_name: str, user_id: str, org_id: Optional[str] = None):
    """
    Trigger training for an agent
    
    Only works for agents that support continuous learning.
    """
    
    agent = get_agent_by_name(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    if not agent.metadata.supports_continuous_learning:
        raise HTTPException(
            status_code=400,
            detail=f"Agent '{agent_name}' does not support continuous learning"
        )
    
    # Trigger training job
    # In production, this would:
    # 1. Collect training data from Filecoin
    # 2. Submit job to Theta GPU
    # 3. Return job ID for tracking
    
    return {
        "status": "training_started",
        "agent": agent_name,
        "user_id": user_id,
        "org_id": org_id,
        "estimated_cost_wtf": agent.metadata.training_cost_wtf,
        "estimated_time_minutes": 120,
        "job_id": "placeholder_job_id"
    }


@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "service": "apollo-agent-api",
        "version": "1.0.0",
        "total_agents": len(list_agents())
    }


# ============================================================================
# AGENT REGISTRY HELPER
# ============================================================================

@app.get("/agents/stats")
async def get_agent_stats():
    """Get statistics about available agents"""
    
    all_agents = list_agents()
    
    stats = {
        "total_agents": len(all_agents),
        "by_layer": {},
        "by_category": {},
        "by_app_context": {},
        "by_entity_type": {},
        "learning_enabled": 0,
        "byok_enabled": 0,
        "wtf_purchasable": 0
    }
    
    for agent in all_agents:
        metadata = agent.metadata
        
        # By layer
        layer = metadata.layer.name
        stats["by_layer"][layer] = stats["by_layer"].get(layer, 0) + 1
        
        # By category
        if metadata.category:
            cat = metadata.category.value
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        
        # By app context
        if metadata.app_contexts:
            for ctx in metadata.app_contexts:
                stats["by_app_context"][ctx.value] = stats["by_app_context"].get(ctx.value, 0) + 1
        
        # By entity type
        if metadata.entity_types:
            for et in metadata.entity_types:
                stats["by_entity_type"][et.value] = stats["by_entity_type"].get(et.value, 0) + 1
        
        # Features
        if metadata.supports_continuous_learning:
            stats["learning_enabled"] += 1
        if metadata.byok_enabled:
            stats["byok_enabled"] += 1
        if metadata.wtf_purchasable:
            stats["wtf_purchasable"] += 1
    
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
