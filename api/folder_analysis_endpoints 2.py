"""
Folder Analysis API Endpoints

Endpoints for comprehensive folder/repo analysis using Theta RAG + DeepSeek
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from pathlib import Path

from agents.analysis.folder_analyzer import FolderAnalyzerAgent, FolderAnalysis

router = APIRouter(prefix="/api/folder", tags=["folder-analysis"])


class FolderAnalysisRequest(BaseModel):
    folder_path: str
    entity_id: str
    deep_analysis: bool = True
    save_results: bool = True
    output_dir: Optional[str] = None


class FolderAnalysisResponse(BaseModel):
    status: str
    analysis_id: str
    folder_path: str
    
    # Summary
    total_files: int
    total_functions: int
    quality_score: float
    technical_debt_score: float
    
    # Counts
    unused_count: int
    unnecessary_count: int
    duplicates_count: int
    suggestions_count: int
    
    # Documents
    current_state_doc: str
    future_state_doc: str
    consolidated_docs: str
    
    # Issues
    unused_functionality: List[Dict[str, Any]]
    unnecessary_files: List[Dict[str, Any]]
    duplicate_features: List[Dict[str, Any]]
    
    # Suggestions
    restructuring_suggestions: List[Dict[str, Any]]
    
    # Output
    output_files: Optional[List[str]] = None


@router.post("/analyze", response_model=FolderAnalysisResponse)
async def analyze_folder(request: FolderAnalysisRequest):
    """
    Comprehensive folder/repo analysis
    
    This endpoint:
    1. Indexes the folder with Theta RAG
    2. Analyzes current state functionality
    3. Consolidates all MD documentation
    4. Generates current state + future state documents
    5. Identifies unused functionality
    6. Finds unnecessary files
    7. Detects duplicate features
    8. Suggests repo restructuring
    
    All using Theta RAG + DeepSeek models.
    """
    
    try:
        # Validate folder exists
        if not Path(request.folder_path).exists():
            raise HTTPException(status_code=404, detail=f"Folder not found: {request.folder_path}")
        
        # Create analyzer
        analyzer = FolderAnalyzerAgent()
        
        # Run analysis
        analysis = await analyzer.analyze_folder(
            folder_path=request.folder_path,
            entity_id=request.entity_id,
            deep_analysis=request.deep_analysis
        )
        
        # Save results if requested
        output_files = None
        if request.save_results:
            output_dir = request.output_dir or f"{request.folder_path}/analysis_output"
            await analyzer.save_analysis(analysis, output_dir)
            output_files = [
                f"{output_dir}/analysis_summary.json",
                f"{output_dir}/CURRENT_STATE.md",
                f"{output_dir}/FUTURE_STATE.md",
                f"{output_dir}/CONSOLIDATED_DOCS.md",
                f"{output_dir}/ISSUES_REPORT.md",
                f"{output_dir}/RESTRUCTURING_PLAN.md"
            ]
        
        return FolderAnalysisResponse(
            status="success",
            analysis_id=f"analysis_{request.entity_id}_{analysis.analyzed_at}",
            folder_path=analysis.folder_path,
            total_files=analysis.total_files,
            total_functions=analysis.total_functions,
            quality_score=analysis.code_quality_score,
            technical_debt_score=analysis.technical_debt_score,
            unused_count=len(analysis.unused_functionality),
            unnecessary_count=len(analysis.unnecessary_files),
            duplicates_count=len(analysis.duplicate_features),
            suggestions_count=len(analysis.restructuring_suggestions),
            current_state_doc=analysis.current_state_doc,
            future_state_doc=analysis.future_state_doc,
            consolidated_docs=analysis.consolidated_docs,
            unused_functionality=analysis.unused_functionality,
            unnecessary_files=analysis.unnecessary_files,
            duplicate_features=analysis.duplicate_features,
            restructuring_suggestions=analysis.restructuring_suggestions,
            output_files=output_files
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/quick")
async def quick_analyze(request: FolderAnalysisRequest):
    """
    Quick folder analysis (faster, less detailed)
    
    Skips deep analysis for faster results.
    Good for initial assessment.
    """
    
    request.deep_analysis = False
    return await analyze_folder(request)


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get previously saved analysis results"""
    
    # TODO: Implement analysis retrieval from storage
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/consolidate-docs")
async def consolidate_docs_only(request: FolderAnalysisRequest):
    """
    Only consolidate markdown documentation
    
    Faster endpoint if you just want docs consolidated.
    """
    
    try:
        analyzer = FolderAnalyzerAgent()
        
        # Index folder
        chatbot_id = await analyzer._index_folder(request.folder_path, request.entity_id)
        
        # Consolidate docs
        consolidated = await analyzer._consolidate_docs(request.folder_path, chatbot_id)
        
        # Save if requested
        if request.save_results:
            output_dir = request.output_dir or f"{request.folder_path}/analysis_output"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            with open(f"{output_dir}/CONSOLIDATED_DOCS.md", 'w') as f:
                f.write(consolidated)
        
        return {
            "status": "success",
            "consolidated_docs": consolidated,
            "output_file": f"{output_dir}/CONSOLIDATED_DOCS.md" if request.save_results else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/identify-issues")
async def identify_issues_only(request: FolderAnalysisRequest):
    """
    Only identify issues (unused, unnecessary, duplicates)
    
    Faster endpoint if you just want issue detection.
    """
    
    try:
        analyzer = FolderAnalyzerAgent()
        
        # Index folder
        chatbot_id = await analyzer._index_folder(request.folder_path, request.entity_id)
        
        # Map functionality
        functionality_map = await analyzer._map_functionality(request.folder_path, chatbot_id)
        
        # Identify issues
        unused, unnecessary, duplicates = await analyzer._identify_issues(
            request.folder_path, chatbot_id, functionality_map
        )
        
        return {
            "status": "success",
            "unused_functionality": unused,
            "unnecessary_files": unnecessary,
            "duplicate_features": duplicates,
            "unused_count": len(unused),
            "unnecessary_count": len(unnecessary),
            "duplicates_count": len(duplicates)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-restructuring")
async def suggest_restructuring_only(request: FolderAnalysisRequest):
    """
    Only generate restructuring suggestions
    
    Faster endpoint if you just want restructuring advice.
    """
    
    try:
        analyzer = FolderAnalyzerAgent()
        
        # Index folder
        chatbot_id = await analyzer._index_folder(request.folder_path, request.entity_id)
        
        # Analyze current state
        current_state = await analyzer._analyze_current_state(request.folder_path, chatbot_id)
        
        # Map functionality
        functionality_map = await analyzer._map_functionality(request.folder_path, chatbot_id)
        
        # Identify issues
        unused, unnecessary, duplicates = await analyzer._identify_issues(
            request.folder_path, chatbot_id, functionality_map
        )
        
        # Generate suggestions
        suggestions = await analyzer._suggest_restructuring(
            request.folder_path, chatbot_id, current_state, unused, unnecessary, duplicates
        )
        
        return {
            "status": "success",
            "restructuring_suggestions": suggestions,
            "suggestions_count": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
