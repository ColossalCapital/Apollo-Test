"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Akashic Intelligence API Endpoints
Provides intelligence for Akashic IDE when loading codebases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from services.akashic_intelligence_orchestrator import AkashicIntelligenceOrchestrator
from services.functionality_mapper import FunctionalityMapper
from services.docs_consolidator_service import DocsConsolidatorService
from services.pm_sync_service import PMSyncService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/akashic", tags=["akashic-intelligence"])

# Store active orchestrators and services
active_orchestrators: Dict[str, AkashicIntelligenceOrchestrator] = {}
active_functionality_mappers: Dict[str, FunctionalityMapper] = {}
active_docs_consolidators: Dict[str, DocsConsolidatorService] = {}
active_pm_syncs: Dict[str, PMSyncService] = {}


# ============================================================================
# Request/Response Models
# ============================================================================

class AnalyzeRepositoryRequest(BaseModel):
    """Request to analyze a repository"""
    entity_id: str
    org_id: Optional[str] = None
    repo_path: str
    options: Optional[Dict[str, bool]] = None
    linear_api_key: Optional[str] = None


class AnalyzeRepositoryResponse(BaseModel):
    """Response from repository analysis"""
    status: str
    repo_path: str
    started_at: str
    completed_at: Optional[str] = None
    phases: Dict[str, Any]
    monitoring: Optional[Dict[str, str]] = None


class DashboardDataResponse(BaseModel):
    """Dashboard data for Akashic IDE"""
    hot_files: List[Dict]
    cold_files: List[Dict]
    planned_features: List[Dict]
    documentation_files: List[str]
    temperature_distribution: Dict[str, int]


class FileMetricsResponse(BaseModel):
    """Metrics for a specific file"""
    path: str
    temperature: str
    edit_count: int
    last_edited: Optional[str]
    is_planned_feature: bool
    can_delete: bool
    delete_reason: str


class RestructuringSuggestionsResponse(BaseModel):
    """Restructuring suggestions"""
    safe_to_delete: List[Dict]
    protected_files: List[Dict]
    move_suggestions: List[Dict]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/analyze", response_model=AnalyzeRepositoryResponse)
async def analyze_repository(
    request: AnalyzeRepositoryRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a repository and provide comprehensive intelligence
    
    This triggers:
    1. Code Watcher - File usage tracking
    2. Docs Consolidator - Documentation merging
    3. PM Automation - Project plan generation
    4. Knowledge Graph - Relationship building
    5. Codebase RAG - Semantic indexing
    """
    try:
        logger.info(f"🧠 Analyzing repository: {request.repo_path}")
        
        # Create orchestrator
        orchestrator = AkashicIntelligenceOrchestrator(
            entity_id=request.entity_id,
            org_id=request.org_id,
            linear_api_key=request.linear_api_key
        )
        
        # Store for later access
        active_orchestrators[request.entity_id] = orchestrator
        
        # Run analysis
        results = await orchestrator.analyze_repository(
            repo_path=request.repo_path,
            options=request.options
        )
        
        return AnalyzeRepositoryResponse(
            status="completed",
            repo_path=request.repo_path,
            started_at=results['started_at'],
            completed_at=results.get('completed_at'),
            phases=results['phases'],
            monitoring=results.get('monitoring')
        )
    
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}", exc_info=True)
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/progress/{entity_id}")
async def get_analysis_progress(entity_id: str):
    """
    Get real-time analysis progress
    
    Returns:
    - step: Current step (Scan, Index, Analyze, Plan, Complete)
    - phase: Current phase name
    - percentage: Progress percentage (0-100)
    - details: Additional details about current phase
    """
    try:
        if entity_id not in active_orchestrators:
            return {
                'step': '',
                'phase': '',
                'percentage': 0,
                'details': 'No active analysis'
            }
        
        orchestrator = active_orchestrators[entity_id]
        return orchestrator.get_progress()
    
    except Exception as e:
        logger.error(f"❌ Progress check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{entity_id}", response_model=DashboardDataResponse)
async def get_dashboard_data(entity_id: str):
    """
    Get dashboard data for Akashic IDE
    
    Returns:
    - Hot files (recently edited)
    - Cold files (candidates for cleanup)
    - Planned features (protected from deletion)
    - Documentation files
    - Temperature distribution
    """
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        data = orchestrator.get_dashboard_data()
        
        return DashboardDataResponse(**data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dashboard data failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file-metrics/{entity_id}")
async def get_file_metrics(entity_id: str, file_path: str):
    """
    Get metrics for a specific file
    
    Returns:
    - Temperature (hot/warm/cool/cold)
    - Edit count and frequency
    - Whether it's a planned feature
    - Whether it can be safely deleted
    """
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        metrics = orchestrator.code_watcher.get_file_metrics(file_path)
        if not metrics:
            raise HTTPException(status_code=404, detail="File not found in metrics")
        
        can_delete, reason = orchestrator.code_watcher.can_delete_file(file_path)
        
        return FileMetricsResponse(
            path=file_path,
            temperature=metrics['temperature'],
            edit_count=metrics['edit_count'],
            last_edited=metrics.get('last_edited'),
            is_planned_feature=metrics['is_planned_feature'],
            can_delete=can_delete,
            delete_reason=reason
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ File metrics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-files/{entity_id}")
async def get_hot_files(entity_id: str, limit: int = 20):
    """Get hottest files (most recently edited)"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        hot_files = orchestrator.code_watcher.get_hot_files(limit=limit)
        return {"hot_files": hot_files}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Hot files failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cold-files/{entity_id}")
async def get_cold_files(entity_id: str, limit: int = 20):
    """Get coldest files (candidates for cleanup)"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        cold_files = orchestrator.code_watcher.get_cold_files(limit=limit)
        return {"cold_files": cold_files}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Cold files failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/planned-features/{entity_id}")
async def get_planned_features(entity_id: str):
    """Get files marked as planned features (PROTECTED from deletion)"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        planned = orchestrator.code_watcher.get_planned_features()
        return {"planned_features": planned}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Planned features failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/restructuring-suggestions/{entity_id}", response_model=RestructuringSuggestionsResponse)
async def get_restructuring_suggestions(entity_id: str):
    """
    Get intelligent restructuring suggestions
    
    Returns:
    - Files safe to delete
    - Files protected from deletion (planned features)
    - Suggestions for moving/reorganizing files
    """
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        # Generate suggestions
        analysis_results = {'phases': {}}  # Would come from stored results
        suggestions = await orchestrator._generate_restructuring_suggestions(analysis_results)
        
        return RestructuringSuggestionsResponse(**suggestions)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Restructuring suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-monitoring/{entity_id}")
async def stop_monitoring(entity_id: str):
    """Stop file monitoring for this entity"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        orchestrator.stop_monitoring()
        
        # Remove from active
        del active_orchestrators[entity_id]
        
        return {"status": "stopped", "entity_id": entity_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Stop monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-file-open/{entity_id}")
async def record_file_open(entity_id: str, file_path: str):
    """Record that a file was opened (for view duration tracking)"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        orchestrator.code_watcher._record_open(file_path)
        return {"status": "recorded", "file_path": file_path}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Record open failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-file-close/{entity_id}")
async def record_file_close(entity_id: str, file_path: str):
    """Record that a file was closed (for view duration tracking)"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        orchestrator.code_watcher._record_close(file_path)
        return {"status": "recorded", "file_path": file_path}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Record close failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-file-run/{entity_id}")
async def record_file_run(entity_id: str, file_path: str):
    """Record that a file was executed"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        if not orchestrator.code_watcher:
            raise HTTPException(status_code=400, detail="Code watcher not active")
        
        orchestrator.code_watcher._record_run(file_path)
        return {"status": "recorded", "file_path": file_path}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Record run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Continuous Monitoring Endpoints
# ============================================================================

@router.post("/monitoring/docs-consolidator/start/{entity_id}")
async def start_docs_consolidator(entity_id: str, repo_path: str):
    """
    Start Docs Consolidator - watches *.md files and consolidates to .akashic/docs/
    
    Monitors codebase for .md files created by Cursor/Windsurf and:
    - Consolidates them into .akashic/docs/
    - Removes them from codebase directories
    - Maintains single source of truth
    """
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        # Check if already running
        if entity_id in active_docs_consolidators:
            return {
                "status": "running",
                "entity_id": entity_id,
                "watching": "*.md files",
                "output": f"{repo_path}/.akashic/docs/"
            }
        
        # Start docs consolidator service
        consolidator = DocsConsolidatorService(repo_path, entity_id, auto_remove=True)
        await consolidator.start_monitoring()
        active_docs_consolidators[entity_id] = consolidator
        
        return {
            "status": "started",
            "entity_id": entity_id,
            "watching": "*.md files",
            "output": f"{repo_path}/.akashic/docs/"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Start docs consolidator failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/docs-consolidator/stop/{entity_id}")
async def stop_docs_consolidator(entity_id: str):
    """Stop Docs Consolidator"""
    try:
        if entity_id not in active_docs_consolidators:
            raise HTTPException(status_code=404, detail="Docs consolidator not running for this entity")
        
        # Stop docs consolidator service
        consolidator = active_docs_consolidators[entity_id]
        consolidator.stop_monitoring()
        del active_docs_consolidators[entity_id]
        
        return {"status": "stopped", "entity_id": entity_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Stop docs consolidator failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/functionality-mapper/start/{entity_id}")
async def start_functionality_mapper(entity_id: str, repo_path: str, similarity_threshold: float = 0.7):
    """
    Start Functionality Mapper - maps code organization and detects overlapping functionality
    
    Analyzes codebase structure and:
    - Maps how functionality is implemented across directories
    - Detects agents/modules with overlapping functionality
    - Identifies organizational issues (e.g., similar agents in different dirs)
    - Creates reorganization plans in .akashic/restructuring/
    - Generates Cursor/Windsurf prompts for reorganization
    
    Example: Detects authentication agents in /agents/auth/ and /services/auth/
    and creates a plan to consolidate them.
    """
    try:
        # Check if already running
        if entity_id in active_functionality_mappers:
            return {
                "status": "running",
                "entity_id": entity_id,
                "similarity_threshold": similarity_threshold,
                "watching": "Code organization & functionality",
                "output": f"{repo_path}/.akashic/restructuring/"
            }
        
        # Start functionality mapper service
        mapper = FunctionalityMapper(repo_path, entity_id, similarity_threshold)
        await mapper.start_monitoring()
        active_functionality_mappers[entity_id] = mapper
        
        return {
            "status": "started",
            "entity_id": entity_id,
            "similarity_threshold": similarity_threshold,
            "watching": "Code organization & functionality",
            "output": f"{repo_path}/.akashic/restructuring/"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Start functionality mapper failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/functionality-mapper/stop/{entity_id}")
async def stop_functionality_mapper(entity_id: str):
    """Stop Functionality Mapper"""
    try:
        if entity_id not in active_functionality_mappers:
            raise HTTPException(status_code=404, detail="Functionality mapper not running for this entity")
        
        # Stop functionality mapper service
        mapper = active_functionality_mappers[entity_id]
        mapper.stop_monitoring()
        del active_functionality_mappers[entity_id]
        
        return {"status": "stopped", "entity_id": entity_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Stop functionality mapper failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/pm-sync/start/{entity_id}")
async def start_pm_sync(entity_id: str, repo_path: str, pm_config: dict = None):
    """
    Start PM Sync - continuous project management syncing
    
    Syncs with multiple PM tools:
    - Linear: Tickets, sprints, issues
    - Jira: Issues, epics, sprints
    - GitHub: Issues, PRs, projects
    - Bitbucket: PRs, issues
    
    Monitors code changes and:
    - Updates ticket status based on commits
    - Creates tickets for detected issues
    - Syncs bidirectionally
    - Stores in .akashic/pm/{tool}/
    """
    try:
        # Check if already running
        if entity_id in active_pm_syncs:
            return {
                "status": "running",
                "entity_id": entity_id,
                "watching": "Code changes & PM tools",
                "tools": ["linear", "jira", "github", "bitbucket"],
                "output": f"{repo_path}/.akashic/pm/"
            }
        
        # Start PM sync service
        pm_sync = PMSyncService(repo_path, entity_id, pm_config)
        await pm_sync.start_monitoring()
        active_pm_syncs[entity_id] = pm_sync
        
        return {
            "status": "started",
            "entity_id": entity_id,
            "watching": "Code changes & PM tools",
            "tools": ["linear", "jira", "github", "bitbucket"],
            "output": f"{repo_path}/.akashic/pm/"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Start PM sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/pm-sync/stop/{entity_id}")
async def stop_pm_sync(entity_id: str):
    """Stop PM Sync"""
    try:
        if entity_id not in active_pm_syncs:
            raise HTTPException(status_code=404, detail="PM sync not running for this entity")
        
        # Stop PM sync service
        pm_sync = active_pm_syncs[entity_id]
        pm_sync.stop_monitoring()
        del active_pm_syncs[entity_id]
        
        return {"status": "stopped", "entity_id": entity_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Stop PM sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/status/{entity_id}")
async def get_monitoring_status(entity_id: str):
    """Get status of all continuous monitoring services"""
    try:
        if entity_id not in active_orchestrators:
            raise HTTPException(status_code=404, detail="No active analysis for this entity")
        
        orchestrator = active_orchestrators[entity_id]
        
        return {
            "entity_id": entity_id,
            "file_watcher": {
                "active": orchestrator.code_watcher is not None,
                "watching": "All files",
                "output": ".akashic/analysis/"
            },
            "docs_consolidator": {
                "active": entity_id in active_docs_consolidators,
                "watching": "*.md files",
                "output": ".akashic/docs/"
            },
            "functionality_mapper": {
                "active": entity_id in active_functionality_mappers,
                "watching": "Code organization & functionality",
                "output": ".akashic/restructuring/"
            },
            "pm_sync": {
                "active": entity_id in active_pm_syncs,
                "watching": "PM tools (Linear, Jira, GitHub, Bitbucket)",
                "output": ".akashic/pm/"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get monitoring status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Cleanup & Archive Endpoint
# ============================================================================

class CleanupRequest(BaseModel):
    """Request to cleanup and archive scattered docs"""
    entity_id: str
    repo_path: str


class CleanupResponse(BaseModel):
    """Response from cleanup operation"""
    success: bool
    archived_count: int
    skipped_count: int
    archive_location: str
    manifest_path: str
    files: List[Dict[str, str]]


@router.post("/cleanup-and-archive", response_model=CleanupResponse)
async def cleanup_and_archive_docs(request: CleanupRequest):
    """
    Clean up project by archiving scattered documentation
    
    This should be run AFTER the first analysis to:
    1. Move all scattered .md/.txt/.rst files to .akashic/archive/original/
    2. Keep only README, LICENSE, CHANGELOG in root
    3. Keep .akashic/ folder with organized outputs
    4. Clean up the codebase
    
    The archived files maintain their directory structure and a manifest
    is created for reference.
    """
    try:
        logger.info(f"🧹 Cleanup requested for: {request.repo_path}")
        
        # Get or create orchestrator
        if request.entity_id not in active_orchestrators:
            orchestrator = AkashicIntelligenceOrchestrator(
                entity_id=request.entity_id,
                org_id=None,
                linear_api_key=None
            )
            active_orchestrators[request.entity_id] = orchestrator
        else:
            orchestrator = active_orchestrators[request.entity_id]
        
        # Run cleanup
        result = await orchestrator.cleanup_and_archive_docs(request.repo_path)
        
        return CleanupResponse(**result)
    
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CheckDirectoryRequest(BaseModel):
    """Request to check if .akashic directory exists"""
    repo_path: str


class CheckDirectoryResponse(BaseModel):
    """Response for directory check"""
    exists: bool
    repo_path: str


@router.post("/check-directory", response_model=CheckDirectoryResponse)
async def check_akashic_directory(request: CheckDirectoryRequest):
    """
    Check if .akashic directory exists in the repository
    
    Used by IDE to detect if user deleted the .akashic directory
    """
    try:
        from pathlib import Path
        
        akashic_path = Path(request.repo_path) / ".akashic"
        exists = akashic_path.exists() and akashic_path.is_dir()
        
        return CheckDirectoryResponse(
            exists=exists,
            repo_path=request.repo_path
        )
    
    except Exception as e:
        logger.error(f"❌ Directory check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
