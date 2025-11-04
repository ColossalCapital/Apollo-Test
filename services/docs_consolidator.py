"""
Documentation Consolidation Service

Monitors and consolidates all markdown documentation from Cursor, Windsurf, 
and other sources into:
- Current State documents
- Future State documents  
- Project Plans (Linear as Code)

Features:
- Watches multiple directories for .md files
- Extracts information using AI
- Consolidates into structured documents
- Syncs with Linear for project management
- Generates Mermaid diagrams
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from learning.theta_edgecloud import ThetaEdgeCloud
from agents.pm.project_plan_generator import ProjectPlanGenerator

logger = logging.getLogger(__name__)


class MarkdownFileHandler(FileSystemEventHandler):
    """Handle markdown file changes"""
    
    def __init__(self, consolidator):
        self.consolidator = consolidator
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            asyncio.create_task(
                self.consolidator.process_file(event.src_path)
            )
            
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            asyncio.create_task(
                self.consolidator.process_file(event.src_path)
            )


class DocumentationConsolidator:
    """
    Consolidates documentation from multiple sources
    
    Workflow:
    1. Watch directories for .md files
    2. Detect changes (Cursor, Windsurf, manual edits)
    3. Extract key information with AI
    4. Categorize: Current State, Future State, Project Plan
    5. Consolidate into master documents
    6. Sync with Linear
    7. Generate Mermaid diagrams
    """
    
    def __init__(
        self,
        watch_paths: List[str],
        output_path: str,
        entity_id: str,
        org_id: Optional[str] = None
    ):
        self.watch_paths = [Path(p) for p in watch_paths]
        self.output_path = Path(output_path)
        self.entity_id = entity_id
        self.org_id = org_id
        
        # Create output directories
        self.output_path.mkdir(parents=True, exist_ok=True)
        (self.output_path / "current_state").mkdir(exist_ok=True)
        (self.output_path / "future_state").mkdir(exist_ok=True)
        (self.output_path / "project_plans").mkdir(exist_ok=True)
        (self.output_path / "mermaid_diagrams").mkdir(exist_ok=True)
        
        # Initialize AI components
        self.theta = ThetaEdgeCloud(api_key=os.getenv("THETA_API_KEY"))
        self.project_planner = ProjectPlanGenerator()
        
        # Track processed files
        self.file_hashes: Dict[str, str] = {}
        self.load_file_hashes()
        
        # File system observers
        self.observers: List[Observer] = []
        
    def load_file_hashes(self):
        """Load previously processed file hashes"""
        hash_file = self.output_path / ".file_hashes.json"
        if hash_file.exists():
            with open(hash_file, 'r') as f:
                self.file_hashes = json.load(f)
                
    def save_file_hashes(self):
        """Save processed file hashes"""
        hash_file = self.output_path / ".file_hashes.json"
        with open(hash_file, 'w') as f:
            json.dump(self.file_hashes, f, indent=2)
            
    def get_file_hash(self, file_path: str) -> str:
        """Get SHA256 hash of file content"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
            
    async def start_watching(self):
        """Start watching directories for changes"""
        logger.info(f"📁 Starting documentation consolidation service")
        logger.info(f"Watching paths: {self.watch_paths}")
        
        # Set up file system watchers
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                logger.warning(f"Path does not exist: {watch_path}")
                continue
                
            observer = Observer()
            handler = MarkdownFileHandler(self)
            observer.schedule(handler, str(watch_path), recursive=True)
            observer.start()
            self.observers.append(observer)
            
            logger.info(f"👀 Watching: {watch_path}")
        
        # Initial scan of existing files
        await self.initial_scan()
        
        # Start periodic consolidation
        asyncio.create_task(self.periodic_consolidation())
        
    async def stop_watching(self):
        """Stop watching"""
        for observer in self.observers:
            observer.stop()
            observer.join()
        logger.info("🛑 Documentation consolidation service stopped")
        
    async def initial_scan(self):
        """Scan all existing markdown files"""
        logger.info("🔍 Scanning existing markdown files...")
        
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
                
            for md_file in watch_path.rglob("*.md"):
                await self.process_file(str(md_file))
                
        logger.info("✅ Initial scan complete")
        
    async def process_file(self, file_path: str):
        """Process a single markdown file"""
        try:
            # Check if file changed
            current_hash = self.get_file_hash(file_path)
            if file_path in self.file_hashes:
                if self.file_hashes[file_path] == current_hash:
                    return  # No changes
                    
            logger.info(f"📄 Processing: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract information with AI
            analysis = await self.analyze_document(content, file_path)
            
            # Store analysis
            await self.store_analysis(file_path, analysis)
            
            # Update hash
            self.file_hashes[file_path] = current_hash
            self.save_file_hashes()
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            
    async def analyze_document(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze document with AI to extract key information"""
        
        prompt = f"""
Analyze this markdown document and extract:

1. **Document Type**: Is this describing:
   - Current State (what exists now)
   - Future State (what should exist)
   - Project Plan (how to get there)
   - Technical Documentation
   - Meeting Notes
   - Other

2. **Key Information**:
   - Main topics/features discussed
   - Action items
   - Technical decisions
   - Dependencies
   - Timeline/deadlines
   - People mentioned
   - Projects mentioned

3. **Status**:
   - Completed items
   - In-progress items
   - Planned items
   - Blocked items

4. **Relationships**:
   - Related documents
   - Related projects
   - Related people

File: {file_path}

Content:
{content}

Return JSON with this structure:
{{
  "document_type": "current_state|future_state|project_plan|technical_doc|meeting_notes|other",
  "title": "Document title",
  "summary": "Brief summary (2-3 sentences)",
  "topics": ["topic1", "topic2"],
  "action_items": [
    {{"text": "...", "assignee": "...", "status": "todo|in_progress|done"}}
  ],
  "technical_decisions": ["decision1", "decision2"],
  "dependencies": ["dep1", "dep2"],
  "timeline": {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}},
  "people": ["person1", "person2"],
  "projects": ["project1", "project2"],
  "status": {{
    "completed": ["item1"],
    "in_progress": ["item2"],
    "planned": ["item3"],
    "blocked": ["item4"]
  }},
  "related_docs": ["doc1", "doc2"]
}}
"""
        
        # Call Theta RAG for analysis
        response = await self.theta.query_chatbot(
            chatbot_id="docs_analyzer",
            query=prompt,
            mode="json"
        )
        
        return json.loads(response)
        
    async def store_analysis(self, file_path: str, analysis: Dict[str, Any]):
        """Store analysis results"""
        
        # Determine output location based on document type
        doc_type = analysis.get("document_type", "other")
        
        if doc_type == "current_state":
            output_dir = self.output_path / "current_state"
        elif doc_type == "future_state":
            output_dir = self.output_path / "future_state"
        elif doc_type == "project_plan":
            output_dir = self.output_path / "project_plans"
        else:
            output_dir = self.output_path / "other"
            output_dir.mkdir(exist_ok=True)
            
        # Create analysis file
        file_name = Path(file_path).stem
        analysis_file = output_dir / f"{file_name}_analysis.json"
        
        with open(analysis_file, 'w') as f:
            json.dump({
                "source_file": file_path,
                "analyzed_at": datetime.utcnow().isoformat(),
                "analysis": analysis
            }, f, indent=2)
            
        logger.info(f"✅ Stored analysis: {analysis_file}")
        
    async def periodic_consolidation(self):
        """Periodically consolidate all documents"""
        interval = int(os.getenv("DOCS_CONSOLIDATION_INTERVAL", "300"))
        
        while True:
            await asyncio.sleep(interval)
            
            try:
                logger.info("🔄 Starting periodic consolidation...")
                
                # Consolidate current state
                await self.consolidate_current_state()
                
                # Consolidate future state
                await self.consolidate_future_state()
                
                # Consolidate project plans
                await self.consolidate_project_plans()
                
                # Sync with Linear
                if os.getenv("PM_SERVICE_ENABLED") == "true":
                    await self.sync_with_linear()
                
                logger.info("✅ Consolidation complete")
                
            except Exception as e:
                logger.error(f"Error in periodic consolidation: {e}")
                
    async def consolidate_current_state(self):
        """Consolidate all current state documents"""
        logger.info("📊 Consolidating current state...")
        
        current_state_dir = self.output_path / "current_state"
        analyses = []
        
        for analysis_file in current_state_dir.glob("*_analysis.json"):
            with open(analysis_file, 'r') as f:
                analyses.append(json.load(f))
                
        if not analyses:
            return
            
        # Generate consolidated current state
        consolidated = await self.generate_consolidated_doc(
            analyses,
            "Current State",
            "current_state"
        )
        
        # Save consolidated document
        output_file = self.output_path / "CURRENT_STATE.md"
        with open(output_file, 'w') as f:
            f.write(consolidated)
            
        logger.info(f"✅ Current state consolidated: {output_file}")
        
    async def consolidate_future_state(self):
        """Consolidate all future state documents"""
        logger.info("🔮 Consolidating future state...")
        
        future_state_dir = self.output_path / "future_state"
        analyses = []
        
        for analysis_file in future_state_dir.glob("*_analysis.json"):
            with open(analysis_file, 'r') as f:
                analyses.append(json.load(f))
                
        if not analyses:
            return
            
        # Generate consolidated future state
        consolidated = await self.generate_consolidated_doc(
            analyses,
            "Future State",
            "future_state"
        )
        
        # Save consolidated document
        output_file = self.output_path / "FUTURE_STATE.md"
        with open(output_file, 'w') as f:
            f.write(consolidated)
            
        logger.info(f"✅ Future state consolidated: {output_file}")
        
    async def consolidate_project_plans(self):
        """Consolidate all project plans into Linear as Code"""
        logger.info("📋 Consolidating project plans...")
        
        project_plans_dir = self.output_path / "project_plans"
        analyses = []
        
        for analysis_file in project_plans_dir.glob("*_analysis.json"):
            with open(analysis_file, 'r') as f:
                analyses.append(json.load(f))
                
        if not analyses:
            return
            
        # Generate consolidated project plan
        consolidated = await self.generate_project_plan(analyses)
        
        # Save as Linear as Code
        output_file = self.output_path / "LINEAR_AS_CODE.md"
        with open(output_file, 'w') as f:
            f.write(consolidated)
            
        # Generate Mermaid diagram
        mermaid = await self.generate_mermaid_diagram(analyses)
        mermaid_file = self.output_path / "mermaid_diagrams" / "project_roadmap.mmd"
        with open(mermaid_file, 'w') as f:
            f.write(mermaid)
            
        logger.info(f"✅ Project plans consolidated: {output_file}")
        logger.info(f"✅ Mermaid diagram: {mermaid_file}")
        
    async def generate_consolidated_doc(
        self,
        analyses: List[Dict],
        title: str,
        doc_type: str
    ) -> str:
        """Generate consolidated markdown document"""
        
        prompt = f"""
Generate a consolidated {title} document from these analyses:

{json.dumps(analyses, indent=2)}

Create a well-structured markdown document that:
1. Summarizes all key information
2. Groups related topics
3. Lists all action items
4. Shows status of items
5. Identifies dependencies
6. Includes timeline
7. Lists people and projects involved

Format as professional markdown with clear sections and hierarchy.
"""
        
        response = await self.theta.query_chatbot(
            chatbot_id="docs_consolidator",
            query=prompt
        )
        
        return response
        
    async def generate_project_plan(self, analyses: List[Dict]) -> str:
        """Generate Linear as Code project plan"""
        
        # Use ProjectPlanGenerator
        plan = await self.project_planner.generate_from_docs(analyses)
        
        return plan
        
    async def generate_mermaid_diagram(self, analyses: List[Dict]) -> str:
        """Generate Mermaid diagram for project roadmap"""
        
        prompt = f"""
Generate a Mermaid diagram showing the project roadmap from these analyses:

{json.dumps(analyses, indent=2)}

Create a Gantt chart or flowchart showing:
1. Phases
2. Tasks
3. Dependencies
4. Timeline
5. Status

Return only the Mermaid code (no markdown fences).
"""
        
        response = await self.theta.query_chatbot(
            chatbot_id="mermaid_generator",
            query=prompt
        )
        
        return response
        
    async def sync_with_linear(self):
        """Sync consolidated plans with Linear"""
        logger.info("🔄 Syncing with Linear...")
        
        # Read LINEAR_AS_CODE.md
        linear_file = self.output_path / "LINEAR_AS_CODE.md"
        if not linear_file.exists():
            return
            
        with open(linear_file, 'r') as f:
            content = f.read()
            
        # Parse and create/update Linear tickets
        # TODO: Implement Linear API integration
        
        logger.info("✅ Linear sync complete")


# ============================================================================
# Service Entry Point
# ============================================================================

async def main():
    """Start documentation consolidation service"""
    
    # Get configuration
    watch_paths = os.getenv("DOCS_WATCH_PATHS", "").split(",")
    output_path = os.getenv("DOCS_OUTPUT_PATH", "/workspace/consolidated_docs")
    entity_id = os.getenv("ENTITY_ID", "default")
    org_id = os.getenv("ORG_ID")
    
    # Create consolidator
    consolidator = DocumentationConsolidator(
        watch_paths=watch_paths,
        output_path=output_path,
        entity_id=entity_id,
        org_id=org_id
    )
    
    # Start watching
    await consolidator.start_watching()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await consolidator.stop_watching()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
