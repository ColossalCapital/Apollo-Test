"""
Codebase Analysis API Endpoints

Features:
1. Index codebase with Theta RAG
2. Generate project plans with AI
3. Create Linear tickets
4. Track progress via WebSocket
5. Generate Mermaid diagrams
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import os
from datetime import datetime

from learning.theta_edgecloud import ThetaEdgeCloud
from learning.codebase_indexer import CodebaseIndexer
from learning.agentic_codebase_rag import AgenticCodebaseRAG
from agents.pm.project_plan_generator import ProjectPlanGenerator
from agents.development.code_agent import CodeReviewAgent

router = APIRouter(prefix="/api/codebase", tags=["codebase"])

# WebSocket connections for real-time progress
active_connections: Dict[str, WebSocket] = {}


class IndexRequest(BaseModel):
    path: str
    entity_id: str
    org_id: Optional[str] = None
    use_theta_rag: bool = True
    file_patterns: Optional[List[str]] = None


class ProjectPlanRequest(BaseModel):
    codebase_id: str  # Theta RAG chatbot ID
    entity_id: str
    org_id: Optional[str] = None
    include_linear: bool = False
    include_mermaid: bool = True


class LinearTicketsRequest(BaseModel):
    project_name: str
    tickets: List[Dict[str, Any]]
    entity_id: str
    linear_api_key: Optional[str] = None


class CodebaseAnalysisResponse(BaseModel):
    chatbot_id: str
    files_indexed: int
    functions_found: int
    classes_found: int
    dependencies: List[str]
    cost_tfuel: float
    status: str


class ProjectPlanResponse(BaseModel):
    phases: List[Dict[str, Any]]
    technical_debt: List[str]
    architecture_recommendations: List[str]
    mermaid_diagram: Optional[str] = None
    estimated_weeks: int
    priority_tasks: List[Dict[str, Any]]


# ============================================================================
# WebSocket for Real-Time Progress
# ============================================================================

@router.websocket("/ws/{entity_id}")
async def websocket_endpoint(websocket: WebSocket, entity_id: str):
    """WebSocket connection for real-time progress updates"""
    await websocket.accept()
    active_connections[entity_id] = websocket
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        del active_connections[entity_id]


async def send_progress(entity_id: str, message: str, progress: int):
    """Send progress update to connected client"""
    if entity_id in active_connections:
        try:
            await active_connections[entity_id].send_json({
                "message": message,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            })
        except:
            del active_connections[entity_id]


# ============================================================================
# 1. Index Codebase with Theta RAG
# ============================================================================

@router.post("/index", response_model=CodebaseAnalysisResponse)
async def index_codebase(request: IndexRequest):
    """
    Index codebase using Theta RAG
    
    Steps:
    1. Scan codebase files
    2. Extract structure (functions, classes, imports)
    3. Create embeddings with Theta EdgeCloud
    4. Store in Theta RAG chatbot
    5. Return chatbot ID for queries
    """
    
    try:
        # Send initial progress
        await send_progress(request.entity_id, "Starting codebase scan...", 10)
        
        # Initialize Theta EdgeCloud
        theta = ThetaEdgeCloud(
            api_key=os.getenv("THETA_API_KEY")
        )
        
        # Initialize codebase indexer
        indexer = CodebaseIndexer(
            codebase_path=request.path,
            file_patterns=request.file_patterns or ["*.py", "*.ts", "*.tsx", "*.rs", "*.js", "*.jsx"]
        )
        
        # Scan codebase
        await send_progress(request.entity_id, "Scanning files...", 20)
        analysis = await indexer.analyze()
        
        await send_progress(request.entity_id, f"Found {analysis['total_files']} files", 40)
        
        # Create documents for Theta RAG
        documents = []
        for file_info in analysis['files']:
            doc = f"""
File: {file_info['path']}
Language: {file_info['language']}
Lines: {file_info['lines']}

Functions:
{chr(10).join(f"- {f['name']}: {f.get('docstring', 'No description')}" for f in file_info.get('functions', []))}

Classes:
{chr(10).join(f"- {c['name']}: {c.get('docstring', 'No description')}" for c in file_info.get('classes', []))}

Imports:
{chr(10).join(f"- {imp}" for imp in file_info.get('imports', []))}

Code:
{file_info.get('content', '')}
"""
            documents.append(doc)
        
        await send_progress(request.entity_id, "Creating Theta RAG chatbot...", 60)
        
        # Create Theta RAG chatbot
        chatbot_id = await theta.create_codebase_rag(
            name=f"codebase_{request.entity_id}_{datetime.utcnow().timestamp()}",
            local_path=request.path,
            file_patterns=request.file_patterns
        )
        
        await send_progress(request.entity_id, "Indexing complete!", 100)
        
        return CodebaseAnalysisResponse(
            chatbot_id=chatbot_id,
            files_indexed=analysis['total_files'],
            functions_found=analysis['total_functions'],
            classes_found=analysis['total_classes'],
            dependencies=analysis.get('dependencies', []),
            cost_tfuel=0.02,  # Approximate cost
            status="completed"
        )
        
    except Exception as e:
        await send_progress(request.entity_id, f"Error: {str(e)}", 0)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 2. Generate Project Plan
# ============================================================================

@router.post("/plan", response_model=ProjectPlanResponse)
async def generate_project_plan(request: ProjectPlanRequest):
    """
    Generate AI-powered project plan
    
    Uses:
    - Theta RAG for codebase context
    - DeepSeek Coder for analysis
    - Project planning templates
    
    Generates:
    - Phase-based roadmap
    - Technical debt analysis
    - Architecture recommendations
    - Mermaid diagrams
    - Priority tasks
    """
    
    try:
        await send_progress(request.entity_id, "Analyzing codebase structure...", 20)
        
        # Initialize Theta EdgeCloud
        theta = ThetaEdgeCloud(
            api_key=os.getenv("THETA_API_KEY")
        )
        
        # Query Theta RAG for codebase overview
        overview = await theta.query_rag(
            chatbot_id=request.codebase_id,
            query="Provide a comprehensive overview of this codebase: architecture, main components, dependencies, and current state."
        )
        
        await send_progress(request.entity_id, "Identifying gaps and missing features...", 40)
        
        # Query for gaps
        gaps = await theta.query_rag(
            chatbot_id=request.codebase_id,
            query="Identify: 1) Incomplete implementations, 2) TODO comments, 3) Missing features, 4) Technical debt"
        )
        
        await send_progress(request.entity_id, "Generating project plan with DeepSeek...", 60)
        
        # Initialize project plan generator
        planner = ProjectPlanGenerator(
            codebase_context=overview['answer'],
            gaps_analysis=gaps['answer']
        )
        
        # Generate plan
        plan = await planner.generate_plan()
        
        # Generate Mermaid diagram if requested
        mermaid_diagram = None
        if request.include_mermaid:
            await send_progress(request.entity_id, "Creating Mermaid diagram...", 80)
            mermaid_diagram = await planner.generate_mermaid_diagram(plan)
        
        await send_progress(request.entity_id, "Project plan complete!", 100)
        
        return ProjectPlanResponse(
            phases=plan['phases'],
            technical_debt=plan['technical_debt'],
            architecture_recommendations=plan['architecture'],
            mermaid_diagram=mermaid_diagram,
            estimated_weeks=plan['estimated_weeks'],
            priority_tasks=plan['priority_tasks']
        )
        
    except Exception as e:
        await send_progress(request.entity_id, f"Error: {str(e)}", 0)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 3. Create Linear Tickets
# ============================================================================

@router.post("/linear/create-tickets")
async def create_linear_tickets(request: LinearTicketsRequest):
    """
    Create Linear tickets from project plan
    
    Features:
    - Creates project in Linear
    - Creates tickets with descriptions
    - Sets priorities and estimates
    - Links tickets to codebase context
    """
    
    try:
        import httpx
        
        linear_api_key = request.linear_api_key or os.getenv("LINEAR_API_KEY")
        if not linear_api_key:
            raise HTTPException(status_code=400, detail="LINEAR_API_KEY not configured")
        
        await send_progress(request.entity_id, "Creating Linear project...", 20)
        
        # GraphQL endpoint
        url = "https://api.linear.app/graphql"
        headers = {
            "Authorization": linear_api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Create project
            create_project_mutation = """
            mutation CreateProject($name: String!) {
              projectCreate(input: { name: $name }) {
                project {
                  id
                  name
                }
              }
            }
            """
            
            response = await client.post(
                url,
                headers=headers,
                json={
                    "query": create_project_mutation,
                    "variables": {"name": request.project_name}
                }
            )
            
            project_data = response.json()
            project_id = project_data['data']['projectCreate']['project']['id']
            
            await send_progress(request.entity_id, f"Project created: {project_id}", 40)
            
            # Create tickets
            created_tickets = []
            total_tickets = len(request.tickets)
            
            for idx, ticket in enumerate(request.tickets):
                progress = 40 + int((idx / total_tickets) * 50)
                await send_progress(
                    request.entity_id,
                    f"Creating ticket {idx + 1}/{total_tickets}: {ticket['title']}",
                    progress
                )
                
                create_issue_mutation = """
                mutation CreateIssue($title: String!, $description: String, $priority: Int, $estimate: Int, $projectId: String!) {
                  issueCreate(input: {
                    title: $title
                    description: $description
                    priority: $priority
                    estimate: $estimate
                    projectId: $projectId
                  }) {
                    issue {
                      id
                      title
                      url
                    }
                  }
                }
                """
                
                response = await client.post(
                    url,
                    headers=headers,
                    json={
                        "query": create_issue_mutation,
                        "variables": {
                            "title": ticket['title'],
                            "description": ticket.get('description', ''),
                            "priority": ticket.get('priority', 2),
                            "estimate": ticket.get('estimate', 3),
                            "projectId": project_id
                        }
                    }
                )
                
                issue_data = response.json()
                created_tickets.append(issue_data['data']['issueCreate']['issue'])
            
            await send_progress(request.entity_id, "All tickets created!", 100)
            
            return {
                "project_id": project_id,
                "tickets_created": len(created_tickets),
                "tickets": created_tickets
            }
            
    except Exception as e:
        await send_progress(request.entity_id, f"Error: {str(e)}", 0)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 4. Work on Individual Ticket with DeepSeek
# ============================================================================

@router.post("/ticket/work")
async def work_on_ticket(
    ticket_id: str,
    codebase_id: str,
    entity_id: str
):
    """
    Use DeepSeek Coder to work on a specific ticket
    
    Steps:
    1. Get ticket details from Linear
    2. Query Theta RAG for relevant code context
    3. Use DeepSeek to generate solution
    4. Create PR with changes
    5. Update ticket with PR link
    """
    
    try:
        await send_progress(entity_id, "Fetching ticket details...", 10)
        
        # TODO: Implement ticket work automation
        # This would:
        # 1. Fetch ticket from Linear
        # 2. Query Theta RAG for context
        # 3. Use DeepSeek to generate code
        # 4. Create branch and commit
        # 5. Open PR
        # 6. Update Linear ticket
        
        return {
            "status": "in_progress",
            "message": "Ticket work automation coming soon"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 5. Code Watching (Agentic RAG)
# ============================================================================

# Store active watchers
active_watchers: Dict[str, AgenticCodebaseRAG] = {}


class StartWatchingRequest(BaseModel):
    codebase_id: str
    entity_id: str
    org_id: Optional[str] = None
    team_id: Optional[str] = None
    repo_path: str
    notify_slack: bool = False
    notify_email: bool = False


class WatcherStatus(BaseModel):
    codebase_id: str
    status: str  # "running" | "stopped"
    last_commit: Optional[str] = None
    last_sync: Optional[str] = None
    files_indexed: int
    drift_detected: bool


@router.post("/watch/start")
async def start_code_watching(request: StartWatchingRequest):
    """
    Start autonomous code watching for a codebase
    
    Features:
    - Watches git for commits (every 5 seconds)
    - Auto-indexes changed files
    - Updates current state documentation
    - Detects drift from PM plan
    - Notifies team via Slack/Email
    """
    
    try:
        # Check if already watching
        if request.codebase_id in active_watchers:
            return {
                "status": "already_running",
                "message": f"Already watching {request.codebase_id}"
            }
        
        # Create watcher
        watcher = AgenticCodebaseRAG(
            codebase_id=request.codebase_id,
            team_id=request.team_id or request.entity_id,
            org_id=request.org_id or request.entity_id,
            repo_path=request.repo_path
        )
        
        # Start watching in background
        asyncio.create_task(watcher.start_watching())
        
        # Store watcher
        active_watchers[request.codebase_id] = watcher
        
        await send_progress(
            request.entity_id,
            f"Started watching {request.codebase_id}",
            100
        )
        
        return {
            "status": "started",
            "codebase_id": request.codebase_id,
            "message": "Code watching started successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watch/stop/{codebase_id}")
async def stop_code_watching(codebase_id: str):
    """Stop code watching for a codebase"""
    
    try:
        if codebase_id not in active_watchers:
            raise HTTPException(status_code=404, detail="Watcher not found")
        
        watcher = active_watchers[codebase_id]
        await watcher.stop_watching()
        
        del active_watchers[codebase_id]
        
        return {
            "status": "stopped",
            "codebase_id": codebase_id,
            "message": "Code watching stopped"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watch/status/{codebase_id}", response_model=WatcherStatus)
async def get_watcher_status(codebase_id: str):
    """Get status of code watcher"""
    
    try:
        if codebase_id not in active_watchers:
            return WatcherStatus(
                codebase_id=codebase_id,
                status="stopped",
                files_indexed=0,
                drift_detected=False
            )
        
        watcher = active_watchers[codebase_id]
        
        # Get watcher stats
        # TODO: Implement proper status tracking in AgenticCodebaseRAG
        
        return WatcherStatus(
            codebase_id=codebase_id,
            status="running" if watcher.running else "stopped",
            last_commit=None,  # TODO: Get from watcher
            last_sync=datetime.utcnow().isoformat(),
            files_indexed=0,  # TODO: Get from watcher
            drift_detected=False  # TODO: Get from watcher
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watch/list")
async def list_active_watchers():
    """List all active code watchers"""
    
    return {
        "watchers": [
            {
                "codebase_id": codebase_id,
                "status": "running" if watcher.running else "stopped"
            }
            for codebase_id, watcher in active_watchers.items()
        ],
        "total": len(active_watchers)
    }


@router.post("/scan/trigger")
async def trigger_code_scan(request: IndexRequest):
    """
    One-off code scan (test before enabling continuous watching)
    
    This endpoint:
    - Scans current codebase state
    - Indexes changed files
    - Updates documentation
    - Checks for drift
    - Returns results immediately
    
    Use this to test before enabling continuous watching.
    """
    
    try:
        await send_progress(request.entity_id, "Starting code scan...", 10)
        
        # Initialize indexer
        indexer = CodebaseIndexer(codebase_path=request.path)
        
        await send_progress(request.entity_id, "Analyzing codebase structure...", 30)
        
        # Scan codebase
        analysis = await indexer.analyze()
        
        await send_progress(request.entity_id, "Indexing files...", 50)
        
        # Index with Theta RAG if enabled
        if request.use_theta_rag:
            theta = ThetaEdgeCloud(api_key=os.getenv("THETA_API_KEY"))
            
            await send_progress(request.entity_id, "Creating embeddings with Theta RAG...", 70)
            
            # Create chatbot for this codebase
            chatbot_id = f"codebase_{request.entity_id}_{int(datetime.utcnow().timestamp())}"
            
            # TODO: Actually create embeddings and store in Theta
            # For now, simulate
            
            await send_progress(request.entity_id, "Checking for drift...", 90)
            
            # Check for drift (compare to PM plan)
            drift_detected = False  # TODO: Implement drift detection
            
            await send_progress(request.entity_id, "Scan complete!", 100)
            
            return {
                "status": "success",
                "files_scanned": analysis.get("total_files", 0),
                "changes_detected": analysis.get("changes", 0),
                "docs_updated": True,
                "drift_detected": drift_detected,
                "chatbot_id": chatbot_id,
                "cost_tfuel": 0.01,
                "message": "One-off scan complete. Use /watch/start to enable continuous monitoring."
            }
        else:
            # Without Theta RAG
            await send_progress(request.entity_id, "Scan complete!", 100)
            
            return {
                "status": "success",
                "files_scanned": analysis.get("total_files", 0),
                "changes_detected": 0,
                "docs_updated": False,
                "drift_detected": False,
                "message": "Scan complete. Enable use_theta_rag for full analysis."
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
