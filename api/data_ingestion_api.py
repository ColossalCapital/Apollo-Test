"""
Apollo Data Ingestion API

Receives raw data from connectors, parses it, and sends to Atlas knowledge graph.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from enum import Enum
import httpx
import uuid

# Import agents
from ..agents import get_agent_by_name

app = FastAPI(title="Apollo Data Ingestion API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class DataSource(str, Enum):
    QUICKBOOKS = "quickbooks"
    GMAIL = "gmail"
    SLACK = "slack"
    GITHUB = "github"
    STRIPE = "stripe"
    CUSTOM = "custom"


class IngestionRequest(BaseModel):
    source: DataSource
    entity_id: str
    data_type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class IngestionResponse(BaseModel):
    success: bool
    job_id: str
    status: str
    message: str


class ParsedData(BaseModel):
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]


class IngestionStatus(BaseModel):
    job_id: str
    status: str  # "pending", "parsing", "analyzing", "sending", "complete", "failed"
    progress: float  # 0.0 to 1.0
    parsed_data: Optional[ParsedData] = None
    error: Optional[str] = None


# In-memory job tracking (in production, use Redis)
jobs: Dict[str, IngestionStatus] = {}


# ============================================================================
# DATA INGESTION ENDPOINTS
# ============================================================================

@app.post("/data/ingest", response_model=IngestionResponse)
async def ingest_data(
    request: IngestionRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest raw data from connectors
    
    Flow:
    1. Receive raw data
    2. Route to appropriate parser (Layer 1)
    3. Extract entities (Layer 2)
    4. Analyze with experts (Layer 3)
    5. Send to Atlas knowledge graph
    """
    
    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = IngestionStatus(
        job_id=job_id,
        status="pending",
        progress=0.0
    )
    
    # Process in background
    background_tasks.add_task(
        process_ingestion,
        job_id,
        request
    )
    
    return IngestionResponse(
        success=True,
        job_id=job_id,
        status="pending",
        message=f"Ingestion job {job_id} started"
    )


@app.get("/data/status/{job_id}", response_model=IngestionStatus)
async def get_ingestion_status(job_id: str):
    """Get status of ingestion job"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@app.post("/data/parse")
async def parse_data(request: IngestionRequest):
    """
    Parse data synchronously (for testing)
    """
    
    try:
        # Step 1: Parse with Layer 1 agent
        parsed = await parse_with_layer1(request.source, request.data)
        
        # Step 2: Extract entities with Layer 2
        entities = await extract_entities(parsed)
        
        # Step 3: Analyze with Layer 3
        insights = await analyze_with_experts(request.source, entities)
        
        return {
            "success": True,
            "parsed_data": {
                "entities": entities.get("entities", []),
                "relationships": entities.get("relationships", []),
                "events": entities.get("events", []),
                "insights": insights
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BACKGROUND PROCESSING
# ============================================================================

async def process_ingestion(job_id: str, request: IngestionRequest):
    """Process ingestion in background"""
    
    try:
        # Update status: parsing
        jobs[job_id].status = "parsing"
        jobs[job_id].progress = 0.2
        
        # Step 1: Parse with Layer 1 agent
        parsed = await parse_with_layer1(request.source, request.data)
        
        # Update status: extracting entities
        jobs[job_id].status = "extracting"
        jobs[job_id].progress = 0.4
        
        # Step 2: Extract entities with Layer 2
        entities = await extract_entities(parsed)
        
        # Update status: analyzing
        jobs[job_id].status = "analyzing"
        jobs[job_id].progress = 0.6
        
        # Step 3: Analyze with Layer 3
        insights = await analyze_with_experts(request.source, entities)
        
        # Update status: sending to Atlas
        jobs[job_id].status = "sending"
        jobs[job_id].progress = 0.8
        
        # Step 4: Send to Atlas knowledge graph
        await send_to_atlas(
            request.entity_id,
            entities.get("entities", []),
            entities.get("relationships", []),
            entities.get("events", []),
            insights
        )
        
        # Update status: complete
        jobs[job_id].status = "complete"
        jobs[job_id].progress = 1.0
        jobs[job_id].parsed_data = ParsedData(
            entities=entities.get("entities", []),
            relationships=entities.get("relationships", []),
            events=entities.get("events", []),
            insights=insights
        )
        
    except Exception as e:
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(e)


# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

async def parse_with_layer1(source: DataSource, data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse data with Layer 1 parser agent"""
    
    # Map source to parser agent
    parser_map = {
        DataSource.QUICKBOOKS: "quickbooks_parser",
        DataSource.GMAIL: "gmail_parser",
        DataSource.SLACK: "slack_parser",
        DataSource.GITHUB: "github_parser",
        DataSource.STRIPE: "stripe_parser",
    }
    
    parser_name = parser_map.get(source, "document_parser")
    parser = get_agent_by_name(parser_name)
    
    if not parser:
        raise Exception(f"Parser not found for source: {source}")
    
    # Execute parser
    result = await parser.extract(data)
    
    if not result.success:
        raise Exception(f"Parsing failed: {result.metadata.get('error')}")
    
    return result.data


async def extract_entities(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract entities with Layer 2 agent"""
    
    entity_recognizer = get_agent_by_name("entity_recognition")
    
    if not entity_recognizer:
        raise Exception("Entity recognizer not found")
    
    result = await entity_recognizer.recognize(parsed_data)
    
    if not result.success:
        raise Exception(f"Entity extraction failed: {result.metadata.get('error')}")
    
    return result.data


async def analyze_with_experts(source: DataSource, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze with Layer 3 domain experts"""
    
    # Map source to expert agent
    expert_map = {
        DataSource.QUICKBOOKS: "financial_expert",
        DataSource.GMAIL: "communication_expert",
        DataSource.SLACK: "communication_expert",
        DataSource.GITHUB: "development_expert",
        DataSource.STRIPE: "financial_expert",
    }
    
    expert_name = expert_map.get(source, "business_expert")
    expert = get_agent_by_name(expert_name)
    
    if not expert:
        return []
    
    result = await expert.analyze(entities)
    
    if not result.success:
        return []
    
    return result.data.get("insights", [])


async def send_to_atlas(
    entity_id: str,
    entities: List[Dict[str, Any]],
    relationships: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    insights: List[Dict[str, Any]]
):
    """Send parsed data to Atlas knowledge graph"""
    
    atlas_url = "http://atlas:8000"  # In production, use env var
    
    payload = {
        "entity_id": entity_id,
        "entities": entities,
        "relationships": relationships,
        "events": events,
        "insights": insights
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{atlas_url}/api/knowledge-graph/ingest",
            json=payload,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Atlas ingestion failed: {response.status_code}")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "service": "apollo-data-ingestion-api",
        "version": "1.0.0",
        "active_jobs": len([j for j in jobs.values() if j.status not in ["complete", "failed"]])
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
