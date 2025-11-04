"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Code Watcher Agent
Tracks file usage, edits, runs, and provides intelligence for:
- Documentation consolidation
- Repo restructuring
- Project planning
- Future-state awareness (don't delete planned features)

Integrates with:
- DocsConsolidator (services/docs_consolidator.py)
- PMAutomationService (services/pm_automation.py)
- ProjectPlanGenerator (agents/pm/project_plan_generator.py)
- KnowledgeGraphBuilder (agents/documents/knowledge_graph_builder.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import hashlib
import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

try:
    import git
except ImportError:
    git = None


@dataclass
class FileMetrics:
    """Comprehensive file metrics"""
    path: str
    
    # Edit metrics
    edit_count: int = 0
    last_edited: Optional[str] = None
    edit_frequency: float = 0.0  # edits per day
    
    # Execution metrics (for scripts)
    run_count: int = 0
    last_run: Optional[str] = None
    run_frequency: float = 0.0
    
    # Access metrics
    open_count: int = 0
    last_opened: Optional[str] = None
    total_view_duration: int = 0  # seconds
    
    # Collaboration
    editors: List[str] = field(default_factory=list)
    edit_conflicts: int = 0
    
    # Code metrics
    lines_of_code: int = 0
    complexity_score: float = 0.0
    file_size_bytes: int = 0
    
    # Dependencies
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    dependency_depth: int = 0
    
    # Business value
    criticality_score: float = 0.0
    business_impact: str = "unknown"  # high, medium, low, unknown
    
    # Future state awareness
    is_planned_feature: bool = False
    planned_for_version: Optional[str] = None
    feature_description: Optional[str] = None
    protection_reason: Optional[str] = None
    
    # Status
    status: str = "active"  # active, cold, deprecated, planned
    temperature: str = "warm"  # hot, warm, cool, cold
    days_since_edit: Optional[int] = None  # Days since last modification
    
    # Timestamps
    created_at: Optional[str] = None
    first_tracked: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class CodeWatcherAgent(FileSystemEventHandler):
    """
    Watches codebase for changes and tracks comprehensive metrics
    
    Integrates with existing Apollo agents:
    - DocsConsolidator: Provides file metrics for doc relevance
    - PMAutomation: Identifies hot files for prioritization
    - ProjectPlanGenerator: Feeds file usage into planning
    - KnowledgeGraphBuilder: Builds file relationship graph
    """
    
    def __init__(self, repo_path: str, entity_id: str = "default"):
        self.repo_path = Path(repo_path)
        self.entity_id = entity_id
        self.db_path = str(self.repo_path / ".akashic" / "analysis" / "file_metrics.json")
        self.metrics: Dict[str, FileMetrics] = {}
        self.observer = None
        
        # Git integration
        self.git_repo = None
        if git:
            try:
                self.git_repo = git.Repo(repo_path)
            except:
                pass
        
        # Load existing metrics
        self._load_metrics()
        
        # Track open files (for view duration)
        self.open_files: Dict[str, datetime] = {}
        
        # Future state markers
        self.future_markers = [
            'TODO', 'FIXME', 'FUTURE', 'PLANNED', 'ROADMAP',
            '@akashic:keep', '@akashic:planned', '@akashic:do-not-delete'
        ]
    
    def _load_metrics(self):
        """Load metrics from disk"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.metrics = {
                        path: FileMetrics(**metrics)
                        for path, metrics in data.items()
                    }
                print(f"📊 Loaded metrics for {len(self.metrics)} files")
            except Exception as e:
                print(f"⚠️  Failed to load metrics: {e}")
                self.metrics = {}
    
    def _save_metrics(self):
        """Save metrics to disk"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            data = {
                path: asdict(metrics)
                for path, metrics in self.metrics.items()
            }
            json.dump(data, f, indent=2)
    
    async def initial_scan(self) -> Dict[str, any]:
        """
        Perform initial scan of repository
        
        Returns comprehensive analysis for other agents
        """
        print(f"🔍 Starting initial scan of {self.repo_path}")
        
        results = {
            'total_files': 0,
            'hot_files': [],
            'cold_files': [],
            'planned_features': [],
            'documentation_files': [],
            'code_files': [],
            'config_files': [],
            'test_files': [],
            'temperature_distribution': {'hot': 0, 'warm': 0, 'cool': 0, 'cold': 0}
        }
        
        # Scan all files first
        for root, dirs, files in os.walk(self.repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.repo_path))
                
                if self._should_ignore(str(file_path)):
                    continue
                
                results['total_files'] += 1
                
                # Analyze file (creates metrics)
                await self._analyze_file(rel_path)
        
        # Analyze git history if available
        if self.git_repo:
            await self._analyze_git_history()
        
        # Calculate temperatures BEFORE collecting results
        self._calculate_temperatures()
        
        # Now collect results with accurate temperatures
        for rel_path, metrics in self.metrics.items():
            # Temperature distribution
            results['temperature_distribution'][metrics.temperature] += 1
            
            # Hot/Cold classification with details
            if metrics.temperature == 'hot':
                results['hot_files'].append({
                    'path': rel_path,
                    'temperature': metrics.temperature,
                    'days_since_edit': metrics.days_since_edit,
                    'edit_frequency': metrics.edit_frequency,
                    'last_edited': metrics.last_edited,
                    'edit_count': metrics.edit_count
                })
            elif metrics.temperature == 'cold':
                results['cold_files'].append({
                    'path': rel_path,
                    'temperature': metrics.temperature,
                    'days_since_edit': metrics.days_since_edit,
                    'edit_frequency': metrics.edit_frequency,
                    'last_edited': metrics.last_edited,
                    'edit_count': metrics.edit_count
                })
            
            # Planned features
            if metrics.is_planned_feature:
                results['planned_features'].append({
                    'path': rel_path,
                    'version': metrics.planned_for_version,
                    'description': metrics.feature_description
                })
            
            # File type categorization
            file = Path(rel_path).name
            if file.endswith('.md'):
                results['documentation_files'].append(rel_path)
            elif file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.rs', '.go')):
                results['code_files'].append(rel_path)
            elif file.endswith(('.json', '.yaml', '.yml', '.toml', '.env')):
                results['config_files'].append(rel_path)
            elif 'test' in file.lower() or 'spec' in file.lower():
                results['test_files'].append(rel_path)
        
        # Save metrics
        self._save_metrics()
        
        print(f"✅ Scan complete: {results['total_files']} files")
        print(f"   🔥 Hot: {results['temperature_distribution']['hot']}")
        print(f"   🌡️  Warm: {results['temperature_distribution']['warm']}")
        print(f"   ❄️  Cold: {results['temperature_distribution']['cold']}")
        print(f"   📋 Planned: {len(results['planned_features'])}")
        
        return results
    
    async def _analyze_file(self, rel_path: str):
        """Analyze a single file"""
        full_path = self.repo_path / rel_path
        
        if not full_path.exists():
            return
        
        # Get or create metrics
        if rel_path not in self.metrics:
            self.metrics[rel_path] = FileMetrics(path=rel_path)
        
        metrics = self.metrics[rel_path]
        
        # Update file stats
        stat = full_path.stat()
        metrics.file_size_bytes = stat.st_size
        metrics.created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
        
        # Count lines of code
        if full_path.suffix in ['.py', '.ts', '.tsx', '.js', '.jsx', '.rs', '.go', '.java']:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    metrics.lines_of_code = sum(1 for line in f if line.strip())
            except:
                pass
        
        # Detect future state markers
        await self._detect_future_state(rel_path, full_path)
        
        # Analyze imports/dependencies
        await self._analyze_dependencies(rel_path, full_path)
        
        metrics.last_updated = datetime.now().isoformat()
    
    async def _detect_future_state(self, rel_path: str, full_path: Path):
        """Detect if file is planned for future use"""
        metrics = self.metrics[rel_path]
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for future markers
            for marker in self.future_markers:
                if marker in content:
                    metrics.is_planned_feature = True
                    metrics.protection_reason = f"Contains {marker} marker"
                    
                    # Try to extract version
                    version_match = re.search(r'v?(\d+\.\d+)', content[content.index(marker):content.index(marker)+200])
                    if version_match:
                        metrics.planned_for_version = version_match.group(0)
                    
                    # Try to extract description
                    desc_match = re.search(r'(?:TODO|FUTURE|PLANNED):\s*(.+)', content)
                    if desc_match:
                        metrics.feature_description = desc_match.group(1).strip()[:200]
                    
                    break
        
        except:
            pass
    
    async def _analyze_dependencies(self, rel_path: str, full_path: Path):
        """Analyze file imports and dependencies"""
        metrics = self.metrics[rel_path]
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Python imports
            if full_path.suffix == '.py':
                imports = re.findall(r'from\s+([\w.]+)\s+import|import\s+([\w.]+)', content)
                metrics.imports = list(set([i[0] or i[1] for i in imports]))
            
            # TypeScript/JavaScript imports
            elif full_path.suffix in ['.ts', '.tsx', '.js', '.jsx']:
                imports = re.findall(r'from\s+[\'"](.+?)[\'"]|import\s+[\'"](.+?)[\'"]', content)
                metrics.imports = list(set([i[0] or i[1] for i in imports]))
        
        except:
            pass
    
    async def _analyze_git_history(self):
        """Analyze git history for file usage patterns"""
        if not self.git_repo:
            return
        
        try:
            # Get commits from last 6 months
            since = datetime.now() - timedelta(days=180)
            commits = list(self.git_repo.iter_commits(since=since.isoformat()))
            
            # Track file changes
            file_changes = {}
            file_authors = {}
            
            for commit in commits:
                for item in commit.stats.files:
                    if item not in file_changes:
                        file_changes[item] = 0
                        file_authors[item] = set()
                    
                    file_changes[item] += 1
                    file_authors[item].add(commit.author.name)
            
            # Update metrics
            for file_path, change_count in file_changes.items():
                if file_path in self.metrics:
                    metrics = self.metrics[file_path]
                    metrics.edit_count = change_count
                    metrics.editors = list(file_authors[file_path])
                    
                    # Calculate edit frequency (edits per day)
                    days = 180
                    metrics.edit_frequency = change_count / days
        
        except Exception as e:
            print(f"⚠️  Git analysis failed: {e}")
    
    def _calculate_temperatures(self):
        """Calculate file temperatures based on actual usage and modification times"""
        now = datetime.now()
        
        for file_path, metrics in self.metrics.items():
            # Get actual file modification time from filesystem
            full_path = Path(self.repo_path) / file_path
            days_since_edit = None
            
            try:
                if full_path.exists():
                    mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
                    days_since_edit = (now - mtime).days
                    
                    # Update last_edited if we have filesystem data
                    if not metrics.last_edited or mtime > datetime.fromisoformat(metrics.last_edited):
                        metrics.last_edited = mtime.isoformat()
            except:
                pass
            
            # If we don't have filesystem data, try to parse last_edited
            if days_since_edit is None and metrics.last_edited:
                try:
                    last_edit = datetime.fromisoformat(metrics.last_edited)
                    days_since_edit = (now - last_edit).days
                except:
                    pass
            
            # Store days since edit
            metrics.days_since_edit = days_since_edit
            
            # Default to cold if we have no data
            if days_since_edit is None:
                metrics.temperature = 'cold'
                continue
            
            # Calculate temperature based on recency
            # Hot: Edited in last 7 days
            if days_since_edit < 7:
                metrics.temperature = 'hot'
            # Warm: Edited in last 30 days
            elif days_since_edit < 30:
                metrics.temperature = 'warm'
            # Cool: Edited in last 90 days
            elif days_since_edit < 90:
                metrics.temperature = 'cool'
            # Cold: Not edited in 90+ days
            else:
                metrics.temperature = 'cold'
            
            # Override based on edit frequency (if we have git data)
            if metrics.edit_count > 0:
                # Calculate frequency: edits per day
                if metrics.last_edited:
                    try:
                        first_edit = datetime.fromisoformat(metrics.last_edited)
                        days_tracked = max((now - first_edit).days, 1)
                        frequency = metrics.edit_count / days_tracked
                        
                        # Very active files (multiple edits per day)
                        if frequency > 0.5:
                            metrics.temperature = 'hot'
                        # Active files (edit every few days)
                        elif frequency > 0.1 and metrics.temperature == 'cold':
                            metrics.temperature = 'warm'
                    except:
                        pass
            
            # Planned features should not be marked as cold (they're protected)
            if metrics.is_planned_feature and metrics.temperature == 'cold':
                metrics.temperature = 'cool'
    
    def _should_ignore_dir(self, dirname: str) -> bool:
        """Check if directory should be ignored"""
        ignore_dirs = {
            '.git', 'node_modules', '__pycache__', '.akashic',
            'target', 'build', 'dist', '.next', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'coverage'
        }
        return dirname in ignore_dirs
    
    def _should_ignore(self, path: str) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            '.DS_Store', '.pyc', '.swp', '.swo', '.log',
            'package-lock.json', 'yarn.lock', 'Cargo.lock'
        ]
        return any(pattern in path for pattern in ignore_patterns)
    
    def _get_relative_path(self, abs_path: str) -> str:
        """Get path relative to repo root"""
        return str(Path(abs_path).relative_to(self.repo_path))
    
    def _record_edit(self, rel_path: str):
        """Record file edit"""
        if rel_path not in self.metrics:
            self.metrics[rel_path] = FileMetrics(path=rel_path)
        
        metrics = self.metrics[rel_path]
        metrics.edit_count += 1
        metrics.last_edited = datetime.now().isoformat()
        metrics.last_updated = datetime.now().isoformat()
        
        self._save_metrics()
    
    def _record_open(self, rel_path: str):
        """Record file open"""
        if rel_path not in self.metrics:
            self.metrics[rel_path] = FileMetrics(path=rel_path)
        
        metrics = self.metrics[rel_path]
        metrics.open_count += 1
        metrics.last_opened = datetime.now().isoformat()
        
        # Track for view duration
        self.open_files[rel_path] = datetime.now()
    
    def _record_close(self, rel_path: str):
        """Record file close"""
        if rel_path in self.open_files:
            open_time = self.open_files[rel_path]
            duration = (datetime.now() - open_time).seconds
            
            if rel_path in self.metrics:
                self.metrics[rel_path].total_view_duration += duration
            
            del self.open_files[rel_path]
            self._save_metrics()
    
    def _record_run(self, rel_path: str):
        """Record file execution"""
        if rel_path not in self.metrics:
            self.metrics[rel_path] = FileMetrics(path=rel_path)
        
        metrics = self.metrics[rel_path]
        metrics.run_count += 1
        metrics.last_run = datetime.now().isoformat()
        metrics.last_updated = datetime.now().isoformat()
        
        self._save_metrics()
    
    # Watchdog event handlers
    def on_modified(self, event):
        """File was modified"""
        if event.is_directory or self._should_ignore(event.src_path):
            return
        
        rel_path = self._get_relative_path(event.src_path)
        self._record_edit(rel_path)
    
    def on_created(self, event):
        """File was created"""
        if event.is_directory or self._should_ignore(event.src_path):
            return
        
        rel_path = self._get_relative_path(event.src_path)
        asyncio.create_task(self._analyze_file(rel_path))
    
    def start_watching(self):
        """Start watching the repository"""
        print(f"👁️  Starting Code Watcher on: {self.repo_path}")
        
        self.observer = Observer()
        self.observer.schedule(self, str(self.repo_path), recursive=True)
        self.observer.start()
        
        print("✅ Code Watcher started")
    
    def stop_watching(self):
        """Stop watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self._save_metrics()
            print("🛑 Code Watcher stopped")
    
    # Public API for integration with other agents
    def get_hot_files(self, limit: int = 20) -> List[Dict]:
        """Get hottest files for PM prioritization"""
        hot_files = [
            {'path': path, **asdict(metrics)}
            for path, metrics in self.metrics.items()
            if metrics.temperature == 'hot'
        ]
        return sorted(hot_files, key=lambda x: x['edit_count'], reverse=True)[:limit]
    
    def get_cold_files(self, limit: int = 20) -> List[Dict]:
        """Get coldest files for cleanup suggestions"""
        cold_files = [
            {'path': path, **asdict(metrics)}
            for path, metrics in self.metrics.items()
            if metrics.temperature == 'cold' and not metrics.is_planned_feature
        ]
        return sorted(cold_files, key=lambda x: x.get('last_edited', ''), reverse=False)[:limit]
    
    def get_planned_features(self) -> List[Dict]:
        """Get files marked as planned features (PROTECTED)"""
        return [
            {'path': path, **asdict(metrics)}
            for path, metrics in self.metrics.items()
            if metrics.is_planned_feature
        ]
    
    def get_documentation_files(self) -> List[str]:
        """Get all documentation files for DocsConsolidator"""
        return [
            path for path in self.metrics.keys()
            if path.endswith('.md')
        ]
    
    def get_file_metrics(self, path: str) -> Optional[Dict]:
        """Get metrics for specific file"""
        if path in self.metrics:
            return asdict(self.metrics[path])
        return None
    
    def can_delete_file(self, path: str) -> Tuple[bool, str]:
        """
        Check if file can be safely deleted
        
        Returns: (can_delete, reason)
        """
        if path not in self.metrics:
            return (True, "File not tracked")
        
        metrics = self.metrics[path]
        
        # NEVER delete planned features
        if metrics.is_planned_feature:
            return (False, f"PROTECTED: {metrics.protection_reason}")
        
        # Don't delete if recently edited
        if metrics.temperature in ['hot', 'warm']:
            return (False, f"File is {metrics.temperature} - recently active")
        
        # Don't delete if imported by other files
        if metrics.imported_by:
            return (False, f"Imported by {len(metrics.imported_by)} files")
        
        # Safe to suggest deletion
        if metrics.temperature == 'cold':
            days_since_edit = "unknown"
            if metrics.last_edited:
                last_edit = datetime.fromisoformat(metrics.last_edited)
                days_since_edit = (datetime.now() - last_edit).days
            
            return (True, f"Cold file - last edited {days_since_edit} days ago")
        
        return (False, "Unknown status")
