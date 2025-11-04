"""
Docs Consolidator Service - Watches for .md files and consolidates them

Monitors codebase for .md files created by Cursor/Windsurf and:
- Consolidates them into .akashic/docs/
- Removes them from codebase directories
- Maintains single source of truth
"""

import os
import shutil
from pathlib import Path
from typing import List, Set
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logger = logging.getLogger(__name__)


class DocsConsolidatorService:
    """Watches for .md files and consolidates them"""
    
    def __init__(self, repo_path: str, entity_id: str, auto_remove: bool = True):
        self.repo_path = Path(repo_path)
        self.entity_id = entity_id
        self.auto_remove = auto_remove
        self.observer = None
        self.is_running = False
        
        # Output directory
        self.docs_dir = self.repo_path / ".akashic" / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files: Set[str] = set()
        
    async def start_monitoring(self):
        """Start monitoring for .md files"""
        logger.info(f"📝 Starting Docs Consolidator for {self.repo_path}")
        self.is_running = True
        
        # Initial scan
        await self._scan_for_md_files()
        
        # Start file watcher
        event_handler = MarkdownFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.repo_path), recursive=True)
        self.observer.start()
        
        logger.info(f"✅ Docs Consolidator started - watching for *.md files")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("🛑 Docs Consolidator stopped")
        
    async def _scan_for_md_files(self):
        """Scan for existing .md files"""
        logger.info("📊 Scanning for .md files...")
        
        md_files = list(self.repo_path.rglob("*.md"))
        consolidated_count = 0
        
        for md_file in md_files:
            if self._should_process(md_file):
                await self._consolidate_file(md_file)
                consolidated_count += 1
                
        logger.info(f"✅ Consolidated {consolidated_count} .md files")
        
        # Generate consolidated docs
        await self._generate_consolidated_docs()
        
    def _should_process(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Don't process files already in .akashic
        if '.akashic' in str(file_path):
            return False
            
        # Don't process README.md in root
        if file_path.name == 'README.md' and file_path.parent == self.repo_path:
            return False
            
        # Don't process if already processed
        if str(file_path) in self.processed_files:
            return False
            
        # Ignore common directories
        ignore_dirs = [
            'node_modules',
            '.git',
            '.venv',
            'venv',
            '__pycache__',
        ]
        
        return not any(ignore_dir in str(file_path) for ignore_dir in ignore_dirs)
        
    async def _consolidate_file(self, md_file: Path):
        """Consolidate a single .md file"""
        try:
            logger.info(f"📄 Consolidating: {md_file.name}")
            
            # Read content
            content = md_file.read_text(encoding='utf-8')
            
            # Determine category based on filename/content
            category = self._categorize_doc(md_file.name, content)
            
            # Create category directory
            category_dir = self.docs_dir / category
            category_dir.mkdir(exist_ok=True)
            
            # Copy to .akashic/docs/
            dest_path = category_dir / md_file.name
            
            # Add metadata header
            metadata = f"""---
source: {md_file.relative_to(self.repo_path)}
consolidated: {datetime.now().isoformat()}
category: {category}
---

"""
            dest_path.write_text(metadata + content, encoding='utf-8')
            
            # Mark as processed
            self.processed_files.add(str(md_file))
            
            # Remove from codebase if auto_remove is enabled
            if self.auto_remove:
                md_file.unlink()
                logger.info(f"🗑️  Removed {md_file.name} from codebase")
            else:
                logger.info(f"✅ Consolidated {md_file.name} (original kept)")
                
        except Exception as e:
            logger.error(f"Failed to consolidate {md_file}: {e}")
            
    def _categorize_doc(self, filename: str, content: str) -> str:
        """Categorize documentation based on filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Check filename patterns
        if any(word in filename_lower for word in ['api', 'endpoint', 'route']):
            return 'api'
        elif any(word in filename_lower for word in ['design', 'architecture', 'system']):
            return 'architecture'
        elif any(word in filename_lower for word in ['guide', 'tutorial', 'howto', 'how-to']):
            return 'guides'
        elif any(word in filename_lower for word in ['spec', 'requirement', 'feature']):
            return 'specifications'
        elif any(word in filename_lower for word in ['plan', 'roadmap', 'todo']):
            return 'planning'
        elif any(word in filename_lower for word in ['changelog', 'release', 'version']):
            return 'releases'
            
        # Check content patterns
        if '## API' in content or '### Endpoint' in content:
            return 'api'
        elif '## Architecture' in content or 'diagram' in content_lower:
            return 'architecture'
        elif '## Installation' in content or '## Setup' in content:
            return 'guides'
            
        return 'general'
        
    async def _generate_consolidated_docs(self):
        """Generate PROJECT_DOCS.md with all consolidated docs"""
        project_docs = f"""# Project Documentation
Generated: {datetime.now().isoformat()}

This documentation has been automatically consolidated from various .md files throughout the codebase.

## Categories

"""
        
        # List all categories
        categories = [d for d in self.docs_dir.iterdir() if d.is_dir()]
        
        for category in sorted(categories):
            docs = list(category.glob("*.md"))
            if docs:
                project_docs += f"\n### {category.name.title()} ({len(docs)} files)\n\n"
                for doc in sorted(docs):
                    project_docs += f"- [{doc.name}]({category.name}/{doc.name})\n"
                    
        # Add index of all docs
        project_docs += "\n## All Documentation Files\n\n"
        all_docs = list(self.docs_dir.rglob("*.md"))
        for doc in sorted(all_docs):
            rel_path = doc.relative_to(self.docs_dir)
            project_docs += f"- [{doc.name}]({rel_path})\n"
            
        # Write PROJECT_DOCS.md
        (self.docs_dir / "PROJECT_DOCS.md").write_text(project_docs)
        logger.info(f"📝 Generated PROJECT_DOCS.md with {len(all_docs)} files")
        
    async def on_file_created(self, file_path: str):
        """Handle new .md file creation"""
        if not self.is_running:
            return
            
        path = Path(file_path)
        if path.suffix == '.md' and self._should_process(path):
            logger.info(f"📄 New .md file detected: {path.name}")
            await self._consolidate_file(path)
            await self._generate_consolidated_docs()


class MarkdownFileHandler(FileSystemEventHandler):
    """Handle markdown file system events"""
    
    def __init__(self, consolidator: DocsConsolidatorService):
        self.consolidator = consolidator
        
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            import asyncio
            asyncio.create_task(self.consolidator.on_file_created(event.src_path))
