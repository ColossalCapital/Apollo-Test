"""
Akashic File Watcher with Multi-Project Support
Monitors multiple .akashic projects and updates analysis
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
from pathlib import Path

from .multi_project_detector import MultiProjectDetector


class AkashicFileWatcher(FileSystemEventHandler):
    """Watches multiple .akashic projects for file changes"""
    
    def __init__(self, root_path: str, detector: MultiProjectDetector):
        self.root_path = root_path
        self.detector = detector
        self.projects = detector.projects
        self.observers: Dict[str, Observer] = {}
        self.change_queue = asyncio.Queue()
    
    def start_watching(self):
        """Start watching all detected projects"""
        
        print(f"\n👁️  Starting File Watcher for {len(self.projects)} projects...")
        
        for project_path, project_info in self.projects.items():
            observer = Observer()
            observer.schedule(self, project_path, recursive=True)
            observer.start()
            
            self.observers[project_path] = observer
            
            print(f"  ✅ Watching: {project_info['name']} ({project_info['type']})")
        
        print(f"\n🔄 File Watcher active. Monitoring for changes...\n")
    
    def stop_watching(self):
        """Stop all observers"""
        for observer in self.observers.values():
            observer.stop()
            observer.join()
        
        print("🛑 File Watcher stopped")
    
    def on_modified(self, event):
        """File was modified"""
        if event.is_directory or self._should_ignore(event.src_path):
            return
        
        asyncio.create_task(self._handle_event(event, 'modified'))
    
    def on_created(self, event):
        """File was created"""
        if event.is_directory or self._should_ignore(event.src_path):
            return
        
        asyncio.create_task(self._handle_event(event, 'created'))
    
    def on_deleted(self, event):
        """File was deleted"""
        if event.is_directory or self._should_ignore(event.src_path):
            return
        
        asyncio.create_task(self._handle_event(event, 'deleted'))
    
    def _should_ignore(self, file_path: str) -> bool:
        """Check if file should be ignored"""
        
        # Ignore patterns
        ignore_patterns = [
            '.git',
            '__pycache__',
            'node_modules',
            '.DS_Store',
            '*.pyc',
            '*.swp',
            '*.tmp',
            '.akashic'  # Don't watch .akashic changes (avoid loops)
        ]
        
        for pattern in ignore_patterns:
            if pattern in file_path:
                return True
        
        return False
    
    async def _handle_event(self, event, event_type: str):
        """Handle file system event"""
        
        file_path = event.src_path
        
        # Find which project this file belongs to
        project = self.detector.get_project_for_file(file_path)
        
        if not project:
            return
        
        print(f"📝 [{event_type.upper()}] {os.path.basename(file_path)}")
        print(f"   Project: {project['name']}")
        
        # Process the change
        await self.handle_file_change(file_path, project, event_type)
    
    async def handle_file_change(self, file_path: str, project: dict, event_type: str):
        """Process file change for specific project"""
        
        # 1. Analyze the change
        analysis = await self.analyze_change(file_path, project, event_type)
        
        # 2. Update project's .akashic/analysis/
        await self.update_analysis(project, analysis)
        
        # 3. If this affects parent projects, update them too
        if project['parent']:
            await self.update_parent_project(project['parent'], analysis)
        
        # 4. If this is a root project, update master plan
        if project['type'] == 'root':
            await self.update_master_plan(project, analysis)
    
    async def analyze_change(self, file_path: str, project: dict, event_type: str) -> dict:
        """Analyze what changed in the file"""
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'relative_path': os.path.relpath(file_path, project['path']),
            'event_type': event_type,
            'project': project['name'],
            'file_type': Path(file_path).suffix,
            'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        
        # Analyze file content if it exists
        if os.path.exists(file_path) and event_type != 'deleted':
            try:
                # Count lines
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    analysis['lines'] = len(lines)
                    
                    # Detect TODOs, FIXMEs
                    todos = [i for i, line in enumerate(lines, 1) if 'TODO' in line or 'FIXME' in line]
                    if todos:
                        analysis['todos'] = todos
                    
                    # Detect imports (for dependency tracking)
                    if file_path.endswith('.py'):
                        imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
                        if imports:
                            analysis['imports'] = imports[:10]  # First 10
            except Exception as e:
                analysis['error'] = str(e)
        
        return analysis
    
    async def update_analysis(self, project: dict, analysis: dict):
        """Update project's .akashic/analysis/ with change info"""
        
        akashic_path = project['akashic_path']
        analysis_dir = os.path.join(akashic_path, 'analysis')
        
        # Ensure directory exists
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Update changes.log
        changes_log_path = os.path.join(analysis_dir, 'changes.log')
        
        log_entry = {
            'timestamp': analysis['timestamp'],
            'file': analysis['relative_path'],
            'event': analysis['event_type'],
            'lines': analysis.get('lines', 0)
        }
        
        # Append to log
        with open(changes_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Update files.json
        await self.update_files_inventory(project, analysis)
        
        print(f"   ✅ Updated analysis for {project['name']}")
    
    async def update_files_inventory(self, project: dict, analysis: dict):
        """Update files.json with current file inventory"""
        
        files_json_path = os.path.join(project['akashic_path'], 'analysis', 'files.json')
        
        # Load existing inventory
        if os.path.exists(files_json_path):
            with open(files_json_path, 'r') as f:
                inventory = json.load(f)
        else:
            inventory = {
                'project': project['name'],
                'last_updated': datetime.now().isoformat(),
                'total_files': 0,
                'by_type': {},
                'files': {}
            }
        
        # Update file entry
        rel_path = analysis['relative_path']
        
        if analysis['event_type'] == 'deleted':
            # Remove from inventory
            if rel_path in inventory['files']:
                del inventory['files'][rel_path]
        else:
            # Add or update
            inventory['files'][rel_path] = {
                'path': rel_path,
                'type': analysis['file_type'],
                'size': analysis['size'],
                'lines': analysis.get('lines', 0),
                'last_modified': analysis['timestamp'],
                'todos': len(analysis.get('todos', []))
            }
        
        # Recalculate stats
        inventory['total_files'] = len(inventory['files'])
        inventory['last_updated'] = datetime.now().isoformat()
        
        # Count by type
        by_type = {}
        for file_info in inventory['files'].values():
            file_type = file_info['type'] or 'unknown'
            by_type[file_type] = by_type.get(file_type, 0) + 1
        
        inventory['by_type'] = by_type
        
        # Save
        with open(files_json_path, 'w') as f:
            json.dump(inventory, f, indent=2)
    
    async def update_parent_project(self, parent_path: str, analysis: dict):
        """Update parent project with child project changes"""
        
        if parent_path not in self.projects:
            return
        
        parent_project = self.projects[parent_path]
        parent_analysis_dir = os.path.join(parent_project['akashic_path'], 'analysis')
        
        os.makedirs(parent_analysis_dir, exist_ok=True)
        
        # Log child project changes
        child_changes_path = os.path.join(parent_analysis_dir, 'child_project_changes.log')
        
        log_entry = {
            'timestamp': analysis['timestamp'],
            'child_project': analysis['project'],
            'file': analysis['relative_path'],
            'event': analysis['event_type']
        }
        
        with open(child_changes_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"   ↗️  Updated parent: {parent_project['name']}")
    
    async def update_master_plan(self, project: dict, analysis: dict):
        """Update master plan with changes"""
        
        master_plan_path = os.path.join(project['akashic_path'], 'pm', 'master_plan.json')
        
        # This will be implemented in Phase 2 (Project Plan Generator)
        # For now, just log that we would update it
        print(f"   📊 Would update master plan (Phase 2)")


# Example usage
async def main():
    import sys
    
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = os.getcwd()
    
    # Detect projects
    detector = MultiProjectDetector(root_path)
    projects = detector.scan_for_projects()
    
    if not projects:
        print("❌ No .akashic projects found")
        return
    
    # Create missing directories
    detector.create_missing_akashic_dirs()
    
    # Start file watcher
    watcher = AkashicFileWatcher(root_path, detector)
    watcher.start_watching()
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping file watcher...")
        watcher.stop_watching()


if __name__ == "__main__":
    asyncio.run(main())
