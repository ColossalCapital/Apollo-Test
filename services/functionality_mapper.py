"""
Functionality Mapper - Maps code organization and detects overlapping functionality

Monitors codebase structure and:
- Maps how functionality is implemented across directories
- Detects agents/modules with overlapping functionality
- Identifies organizational issues
- Creates reorganization plans
- Generates Cursor/Windsurf prompts
"""

import os
import ast
import asyncio
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logger = logging.getLogger(__name__)


class FunctionalityMapper:
    """Maps code organization and detects overlapping functionality"""
    
    def __init__(self, repo_path: str, entity_id: str, similarity_threshold: float = 0.7):
        self.repo_path = Path(repo_path)
        self.entity_id = entity_id
        self.similarity_threshold = similarity_threshold
        self.observer = None
        self.is_running = False
        
        # Storage for analysis
        self.modules = {}  # path -> module info
        self.functionality_map = {}  # functionality -> [files]
        self.overlaps = []  # List of detected overlaps
        
        # Output directory
        self.output_dir = self.repo_path / ".akashic" / "restructuring"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def start_monitoring(self):
        """Start monitoring the codebase"""
        logger.info(f"🗺️ Starting Functionality Mapper for {self.repo_path}")
        self.is_running = True
        
        # Initial scan
        await self._scan_codebase()
        
        # Start file watcher
        event_handler = CodeChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.repo_path), recursive=True)
        self.observer.start()
        
        logger.info(f"✅ Functionality Mapper started - watching {self.repo_path}")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("🛑 Functionality Mapper stopped")
        
    async def _scan_codebase(self):
        """Scan entire codebase and build functionality map"""
        logger.info("📊 Scanning codebase for functionality mapping...")
        
        # Find all Python files
        python_files = list(self.repo_path.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_ignore(file_path):
                continue
                
            await self._analyze_file(file_path)
        
        # Detect overlaps
        await self._detect_overlaps()
        
        # Generate report
        await self._generate_report()
        
        logger.info(f"✅ Scanned {len(self.modules)} modules, found {len(self.overlaps)} overlaps")
        
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'node_modules',
            '.akashic',
            'test_',
            '_test.py',
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
        
    async def _analyze_file(self, file_path: Path):
        """Analyze a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            # Extract information
            module_info = {
                'path': str(file_path.relative_to(self.repo_path)),
                'classes': [],
                'functions': [],
                'imports': [],
                'functionality': set()
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    module_info['classes'].append(node.name)
                    module_info['functionality'].add(self._extract_functionality(node.name))
                    
                elif isinstance(node, ast.FunctionDef):
                    module_info['functions'].append(node.name)
                    module_info['functionality'].add(self._extract_functionality(node.name))
                    
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info['imports'].append(node.module)
            
            self.modules[str(file_path)] = module_info
            
            # Update functionality map
            for func in module_info['functionality']:
                if func not in self.functionality_map:
                    self.functionality_map[func] = []
                self.functionality_map[func].append(str(file_path))
                
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            
    def _extract_functionality(self, name: str) -> str:
        """Extract functionality type from name"""
        name_lower = name.lower()
        
        # Common functionality patterns
        patterns = {
            'auth': ['auth', 'login', 'token', 'session', 'password'],
            'database': ['db', 'database', 'sql', 'query', 'model'],
            'api': ['api', 'endpoint', 'route', 'handler'],
            'storage': ['storage', 'file', 'upload', 'download'],
            'cache': ['cache', 'redis', 'memcache'],
            'queue': ['queue', 'task', 'job', 'worker'],
            'email': ['email', 'mail', 'smtp'],
            'notification': ['notification', 'notify', 'alert'],
            'payment': ['payment', 'stripe', 'billing'],
            'analytics': ['analytics', 'tracking', 'metrics'],
        }
        
        for functionality, keywords in patterns.items():
            if any(keyword in name_lower for keyword in keywords):
                return functionality
                
        return 'general'
        
    async def _detect_overlaps(self):
        """Detect overlapping functionality across directories"""
        self.overlaps = []
        
        for functionality, files in self.functionality_map.items():
            if len(files) > 1:
                # Group by directory
                dir_groups = {}
                for file_path in files:
                    dir_path = str(Path(file_path).parent)
                    if dir_path not in dir_groups:
                        dir_groups[dir_path] = []
                    dir_groups[dir_path].append(file_path)
                
                # If functionality exists in multiple directories, it's an overlap
                if len(dir_groups) > 1:
                    self.overlaps.append({
                        'functionality': functionality,
                        'directories': list(dir_groups.keys()),
                        'files': files,
                        'severity': 'high' if len(dir_groups) > 2 else 'medium'
                    })
                    
    async def _generate_report(self):
        """Generate reorganization plan"""
        if not self.overlaps:
            logger.info("No overlaps detected - codebase is well organized!")
            return
            
        report = f"""# Functionality Mapping Report
Generated: {datetime.now().isoformat()}

## Summary
- **Total Modules Analyzed:** {len(self.modules)}
- **Functionality Types Found:** {len(self.functionality_map)}
- **Overlaps Detected:** {len(self.overlaps)}

## Overlapping Functionality

"""
        
        for overlap in self.overlaps:
            report += f"""### {overlap['functionality'].title()} Functionality
**Severity:** {overlap['severity'].upper()}

**Found in {len(overlap['directories'])} different directories:**
"""
            for directory in overlap['directories']:
                files_in_dir = [f for f in overlap['files'] if directory in f]
                report += f"\n**{directory}/**\n"
                for file in files_in_dir:
                    module = self.modules.get(file, {})
                    classes = ', '.join(module.get('classes', []))
                    functions = ', '.join(module.get('functions', []))[:100]
                    report += f"- `{Path(file).name}`\n"
                    if classes:
                        report += f"  - Classes: {classes}\n"
                    if functions:
                        report += f"  - Functions: {functions}...\n"
                        
            # Generate reorganization suggestion
            primary_dir = overlap['directories'][0]
            report += f"""
**Recommended Action:**
Consolidate all {overlap['functionality']} functionality into `{primary_dir}/`

**Cursor Prompt:**
```
Reorganize {overlap['functionality']} functionality:
1. Keep primary implementation in {primary_dir}/
2. Move or merge files from other directories:
"""
            for dir in overlap['directories'][1:]:
                report += f"   - {dir}/ → {primary_dir}/\n"
            report += """3. Update all imports throughout the codebase
4. Remove duplicate implementations
5. Ensure all tests still pass
```

---

"""
        
        # Write report
        report_path = self.output_dir / "FUNCTIONALITY_MAP.md"
        report_path.write_text(report)
        logger.info(f"📝 Generated functionality map: {report_path}")
        
        # Also create a simple reorganization plan
        plan = f"""# Reorganization Plan
Generated: {datetime.now().isoformat()}

## Quick Actions

"""
        for i, overlap in enumerate(self.overlaps, 1):
            primary_dir = overlap['directories'][0]
            plan += f"{i}. **Consolidate {overlap['functionality']} → `{primary_dir}/`**\n"
            
        plan_path = self.output_dir / "REORGANIZATION_PLAN.md"
        plan_path.write_text(plan)
        
    async def on_file_changed(self, file_path: str):
        """Handle file change event"""
        if not self.is_running:
            return
            
        path = Path(file_path)
        if path.suffix == '.py' and not self._should_ignore(path):
            logger.info(f"📝 File changed: {path.name}")
            await self._analyze_file(path)
            await self._detect_overlaps()
            await self._generate_report()


class CodeChangeHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, mapper: FunctionalityMapper):
        self.mapper = mapper
        
    def on_modified(self, event):
        if not event.is_directory:
            asyncio.create_task(self.mapper.on_file_changed(event.src_path))
            
    def on_created(self, event):
        if not event.is_directory:
            asyncio.create_task(self.mapper.on_file_changed(event.src_path))
