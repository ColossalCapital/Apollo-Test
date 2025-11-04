"""
Code Intelligence API - Akashic IDE Integration
Apollo handles all AI-powered code intelligence

Endpoints:
- POST /code/complete - AI code completion (DeepSeek Coder)
- POST /code/validate - Code validation and error detection
- POST /code/review - Code review with suggestions
- POST /code/index-codebase - Index codebase into RAG (Learning Mode)
- POST /code/connect-project - Connect project for development (Development Mode)
- POST /code/analyze-project - Analyze project and generate plan
- GET /code/project/{project_id}/files - Get file tree
- GET /code/file/{file_id} - Get file contents
- PUT /code/file/{file_id} - Update file
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os

from agents import AGENT_REGISTRY
from agents.development import CodeReviewAgent, GitHubAgent
from config.model_config import AppContext, PrivacySchema
from learning.deepseek_coder import DeepSeekCoder, DeepSeekConfig
from learning.codebase_rag import CodebaseRAG

logger = logging.getLogger(__name__)

# Lazy-load DeepSeek Coder (don't initialize at module load time)
deepseek_config = DeepSeekConfig.from_env()
_deepseek_instance = None

def get_deepseek() -> DeepSeekCoder:
    """Lazy-load DeepSeek Coder instance"""
    global _deepseek_instance
    if _deepseek_instance is None:
        _deepseek_instance = DeepSeekCoder(
            model_size=deepseek_config.model_size,
            device=deepseek_config.device,
            use_theta=deepseek_config.use_theta
        )
    return _deepseek_instance

# Initialize CodebaseRAG
codebase_rag = CodebaseRAG()

router = APIRouter(prefix="/code", tags=["code"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CodeCompleteRequest(BaseModel):
    """AI Code Completion Request"""
    code: str = Field(..., description="Code to complete")
    position: int = Field(..., description="Cursor position")
    language: str = Field(..., description="Programming language")
    context: str = Field(..., description="Context: atlas, delt, or generic")
    user_id: str = Field(..., description="User ID")
    codebase_id: Optional[str] = Field(None, description="Connected codebase ID")
    codebase_connected: bool = Field(False, description="Is codebase connected")
    # DeepSeek settings
    use_theta_gpu: bool = Field(False, description="Use Theta GPU for inference")
    model_size: str = Field("1.3b", description="Model size: 1.3b, 6.7b, or 33b")


class CodeCompleteResponse(BaseModel):
    """AI Code Completion Response"""
    suggestions: List[str] = Field(..., description="Code suggestions")
    confidence: float = Field(..., description="Confidence score 0-1")
    model_used: str = Field(..., description="Model used for completion")


class CodeValidateRequest(BaseModel):
    """Code Validation Request"""
    code: str = Field(..., description="Code to validate")
    language: str = Field(..., description="Programming language")
    context: str = Field(..., description="Context: atlas, delt, or generic")
    user_id: str = Field(..., description="User ID")


class CodeError(BaseModel):
    """Code Error"""
    line: int
    column: int
    message: str
    severity: str  # "error" | "warning"


class CodeWarning(BaseModel):
    """Code Warning"""
    line: int
    column: int
    message: str


class CodeValidateResponse(BaseModel):
    """Code Validation Response"""
    errors: List[CodeError] = Field(default_factory=list)
    warnings: List[CodeWarning] = Field(default_factory=list)
    score: float = Field(..., description="Code quality score 0-100")


class CodeReviewRequest(BaseModel):
    """Code Review Request"""
    code: str = Field(..., description="Code to review")
    language: str = Field(..., description="Programming language")
    context: str = Field(..., description="Context")
    user_id: str = Field(..., description="User ID")


class CodeReviewIssue(BaseModel):
    """Code Review Issue"""
    line: int
    severity: str  # "error" | "warning" | "info"
    message: str
    suggestion: str


class CodeReviewResponse(BaseModel):
    """Code Review Response"""
    issues: List[CodeReviewIssue] = Field(default_factory=list)
    score: float = Field(..., description="Code quality score 0-100")
    summary: str = Field(..., description="Review summary")


class LearnOptions(BaseModel):
    """Learning Options"""
    patterns: bool = True
    conventions: bool = True
    apis: bool = True
    best_practices: bool = True


class IndexCodebaseRequest(BaseModel):
    """Index Codebase Request (Learning Mode)"""
    source: str = Field(..., description="github, gitlab, or local")
    repo: str = Field(..., description="Repository URL or path")
    branch: str = Field(default="main", description="Branch name")
    user_id: str = Field(..., description="User ID")
    learn: LearnOptions = Field(default_factory=LearnOptions)
    mode: str = Field(default="learning", description="learning or development")


class IndexCodebaseResponse(BaseModel):
    """Index Codebase Response"""
    files_indexed: int
    patterns_learned: int
    embeddings_created: int
    knowledge_base_id: str


class ConnectProjectRequest(BaseModel):
    """Connect Project Request (Development Mode)"""
    source: str = Field(..., description="github, gitlab, or local")
    repo: str = Field(..., description="Repository URL or path")
    branch: str = Field(default="main")
    user_id: str = Field(..., description="User ID")
    access: str = Field(default="read-write")
    mode: str = Field(default="development")


class ConnectProjectResponse(BaseModel):
    """Connect Project Response"""
    project_id: str
    files: int
    languages: List[str]
    ai_ready: bool


class AnalyzeOptions(BaseModel):
    """Project Analysis Options"""
    architecture: bool = True
    dependencies: bool = True
    issues: bool = True
    opportunities: bool = True


class AnalyzeProjectRequest(BaseModel):
    """Analyze Project Request"""
    project_id: str = Field(..., description="Project ID")
    user_id: str = Field(..., description="User ID")
    analyze: AnalyzeOptions = Field(default_factory=AnalyzeOptions)


class ArchitectureInfo(BaseModel):
    """Architecture Information"""
    arch_type: str
    components: List[str]
    dependencies: List[str]


class ProjectTask(BaseModel):
    """Project Task"""
    title: str
    description: str
    priority: str  # "high" | "medium" | "low"
    estimated_hours: float


class ProjectPhase(BaseModel):
    """Project Phase"""
    name: str
    tasks: List[ProjectTask]


class ProjectPlan(BaseModel):
    """Project Plan"""
    phases: List[ProjectPhase]


class ProjectIssue(BaseModel):
    """Project Issue"""
    issue_type: str
    severity: str
    description: str
    file: str
    line: int


class ProjectOpportunity(BaseModel):
    """Project Opportunity"""
    opportunity_type: str
    description: str
    impact: str


class AnalyzeProjectResponse(BaseModel):
    """Analyze Project Response"""
    architecture: ArchitectureInfo
    project_plan: ProjectPlan
    issues: List[ProjectIssue]
    opportunities: List[ProjectOpportunity]


class FileNode(BaseModel):
    """File Tree Node"""
    path: str
    node_type: str  # "file" | "directory"
    size: int
    language: Optional[str] = None


class FileTreeResponse(BaseModel):
    """File Tree Response"""
    tree: List[FileNode]


class FileContentResponse(BaseModel):
    """File Content Response"""
    path: str
    content: str
    language: str
    last_modified: str


class UpdateFileRequest(BaseModel):
    """Update File Request"""
    content: str
    commit_message: str
    user_id: str


class UpdateFileResponse(BaseModel):
    """Update File Response"""
    success: bool
    commit_hash: str


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/complete", response_model=CodeCompleteResponse)
async def code_complete(request: CodeCompleteRequest):
    """
    AI Code Completion using DeepSeek Coder
    
    Provides intelligent code suggestions based on:
    - Current code context
    - Programming language
    - Connected codebase (if available)
    - Learned patterns from Knowledge Base
    """
    logger.info(f"Code completion request: {request.language} at position {request.position}")
    
    try:
        # Get codebase context if available
        codebase_context = None
        if request.codebase_connected and request.codebase_id:
            # Query CodebaseRAG for relevant snippets
            try:
                # Extract context around cursor
                context_window = request.code[max(0, request.position-200):request.position]
                
                # Search for similar code
                snippets = await codebase_rag.query_codebase(
                    query=context_window,
                    codebase_id=request.codebase_id,
                    user_id=request.user_id,
                    limit=3
                )
                
                codebase_context = [s.content[:200] for s in snippets]
                logger.info(f"Found {len(snippets)} relevant code snippets from codebase")
            except Exception as e:
                logger.warning(f"Failed to get codebase context: {e}")
        
        # Create DeepSeek instance with user's GPU preference
        user_deepseek = DeepSeekCoder(
            model_size=request.model_size,
            device=deepseek_config.device,
            use_theta=request.use_theta_gpu
        )
        
        # Generate completions with DeepSeek
        suggestions = await user_deepseek.complete_code(
            code=request.code,
            position=request.position,
            language=request.language,
            max_tokens=50,
            temperature=0.2,
            codebase_context=codebase_context
        )
        
        # Calculate confidence based on context availability and model
        base_confidence = 0.75
        if codebase_context:
            base_confidence += 0.1
        if request.model_size == '33b':
            base_confidence += 0.1
        
        confidence = min(base_confidence, 0.95)
        
        return CodeCompleteResponse(
            suggestions=suggestions,
            confidence=confidence,
            model_used=f"deepseek-coder-{request.model_size}" + 
                      (" (Theta GPU)" if request.use_theta_gpu else " (Local)")
        )
        
    except Exception as e:
        logger.error(f"Code completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=CodeValidateResponse)
async def code_validate(request: CodeValidateRequest):
    """
    Code Validation and Error Detection
    
    Analyzes code for:
    - Syntax errors
    - Type errors
    - Style violations
    - Best practice violations
    """
    logger.info(f"Code validation request: {request.language}")
    
    try:
        # Validate code with DeepSeek
        validation_result = await get_deepseek().validate_code(
            code=request.code,
            language=request.language
        )
        
        return CodeValidateResponse(
            errors=validation_result.get("errors", []),
            warnings=validation_result.get("warnings", []),
            score=validation_result.get("score", 100.0)
        )
        
    except Exception as e:
        logger.error(f"Code validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review", response_model=CodeReviewResponse)
async def code_review(request: CodeReviewRequest):
    """
    AI Code Review
    
    Uses CodeReviewAgent to provide:
    - Code quality analysis
    - Security issues
    - Performance suggestions
    - Best practice recommendations
    """
    logger.info(f"Code review request: {request.language}")
    
    try:
        # Use CodeReviewAgent
        agent = AGENT_REGISTRY.get("code_review")()
        
        result = await agent.analyze({
            "code": request.code,
            "language": request.language,
            "context": request.context,
        })
        
        return CodeReviewResponse(
            issues=result.get("issues", []),
            score=result.get("score", 0.0),
            summary=result.get("summary", "")
        )
        
    except Exception as e:
        logger.error(f"Code review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index-codebase", response_model=IndexCodebaseResponse)
async def index_codebase(request: IndexCodebaseRequest):
    """
    Index Codebase into RAG (Learning Mode)
    
    Indexes external codebase to learn:
    - Code patterns
    - Naming conventions
    - API usage
    - Best practices
    
    Stored in Qdrant with privacy isolation
    """
    logger.info(f"Indexing codebase: {request.repo} (mode: {request.mode})")
    
    try:
        # TODO: Implement CodebaseRAG
        # For now, return mock response
        
        knowledge_base_id = f"kb_{request.user_id}_{datetime.now().timestamp()}"
        
        return IndexCodebaseResponse(
            files_indexed=150,
            patterns_learned=45,
            embeddings_created=1500,
            knowledge_base_id=knowledge_base_id
        )
        
    except Exception as e:
        logger.error(f"Codebase indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect-project", response_model=ConnectProjectResponse)
async def connect_project(request: ConnectProjectRequest):
    """
    Connect Project (Development Mode)
    
    Connects user's project for AI-assisted development:
    - Clones repository
    - Indexes for AI context
    - Enables read-write access
    - Provides AI suggestions
    """
    logger.info(f"Connecting project: {request.repo}")
    
    try:
        # TODO: Implement project connection
        # For now, return mock response
        
        project_id = f"proj_{request.user_id}_{datetime.now().timestamp()}"
        
        return ConnectProjectResponse(
            project_id=project_id,
            files=250,
            languages=["python", "javascript", "rust"],
            ai_ready=True
        )
        
    except Exception as e:
        logger.error(f"Project connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-project", response_model=AnalyzeProjectResponse)
async def analyze_project(request: AnalyzeProjectRequest):
    """
    Analyze Project & Generate Plan
    
    AI-powered project analysis:
    - Identifies architecture
    - Analyzes dependencies
    - Finds issues
    - Generates project plan with tasks
    """
    logger.info(f"Analyzing project: {request.project_id}")
    
    try:
        # TODO: Implement project analysis
        # For now, return mock response
        
        return AnalyzeProjectResponse(
            architecture=ArchitectureInfo(
                arch_type="Microservices",
                components=["API", "Frontend", "Database"],
                dependencies=["FastAPI", "React", "PostgreSQL"]
            ),
            project_plan=ProjectPlan(
                phases=[
                    ProjectPhase(
                        name="Phase 1: Foundation",
                        tasks=[
                            ProjectTask(
                                title="Set up database schema",
                                description="Design and implement PostgreSQL schema",
                                priority="high",
                                estimated_hours=8.0
                            ),
                            ProjectTask(
                                title="Create API endpoints",
                                description="Build REST API with FastAPI",
                                priority="high",
                                estimated_hours=16.0
                            )
                        ]
                    )
                ]
            ),
            issues=[],
            opportunities=[]
        )
        
    except Exception as e:
        logger.error(f"Project analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}/files", response_model=FileTreeResponse)
async def get_file_tree(project_id: str):
    """Get project file tree"""
    logger.info(f"Getting file tree for project: {project_id}")
    
    try:
        # TODO: Implement file tree retrieval
        return FileTreeResponse(tree=[])
        
    except Exception as e:
        logger.error(f"File tree error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_id}", response_model=FileContentResponse)
async def get_file(file_id: str):
    """Get file contents"""
    logger.info(f"Getting file: {file_id}")
    
    try:
        # TODO: Implement file retrieval
        return FileContentResponse(
            path="",
            content="",
            language="",
            last_modified=""
        )
        
    except Exception as e:
        logger.error(f"File retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/file/{file_id}", response_model=UpdateFileResponse)
async def update_file(file_id: str, request: UpdateFileRequest):
    """Update file contents"""
    logger.info(f"Updating file: {file_id}")
    
    try:
        # TODO: Implement file update
        return UpdateFileResponse(
            success=True,
            commit_hash="abc123"
        )
        
    except Exception as e:
        logger.error(f"File update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
