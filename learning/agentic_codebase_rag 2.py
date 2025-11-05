"""
Agentic Codebase RAG - Autonomous Codebase Watcher

Autonomous agent that:
- Watches codebase for changes (git hooks)
- Auto-indexes new code
- Updates documentation
- Maintains "current state" snapshot
- Compares against PM plan
- Alerts team of drift
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib

from learning.codebase_rag import CodebaseRAG, CodeSnippet
from learning.deepseek_coder import DeepSeekCoder

logger = logging.getLogger(__name__)


class GitWatcher:
    """Watch git repository for changes"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.last_commit = None
        
    async def stream(self):
        """Stream git events"""
        from git import Repo
        
        repo = Repo(self.repo_path)
        
        while True:
            # Check for new commits
            current_commit = repo.head.commit.hexsha
            
            if current_commit != self.last_commit:
                # Get changed files
                if self.last_commit:
                    diff = repo.git.diff(
                        self.last_commit,
                        current_commit,
                        name_only=True
                    )
                    changed_files = diff.split('\n') if diff else []
                else:
                    changed_files = []
                
                yield {
                    'type': 'commit',
                    'commit_hash': current_commit,
                    'author': repo.head.commit.author.name,
                    'message': repo.head.commit.message,
                    'timestamp': repo.head.commit.committed_datetime,
                    'changed_files': changed_files
                }
                
                self.last_commit = current_commit
                
            await asyncio.sleep(5)  # Check every 5 seconds


class AgenticCodebaseRAG:
    """
    Autonomous agent for codebase management
    
    Features:
    - Watches git for changes
    - Auto-indexes changed files
    - Generates current state documentation
    - Compares to PM plan
    - Detects drift
    - Notifies team
    """
    
    def __init__(
        self,
        codebase_id: str,
        team_id: str,
        org_id: str,
        repo_path: str
    ):
        self.codebase_id = codebase_id
        self.team_id = team_id
        self.org_id = org_id
        self.repo_path = repo_path
        
        # Initialize components
        self.codebase_rag = CodebaseRAG()
        self.git_watcher = GitWatcher(repo_path)
        # Use Theta for DeepSeek (don't load locally)
        self.deepseek = DeepSeekCoder(model_size="33b", use_theta=True)
        
        self.running = False
        
    async def start_watching(self):
        """Start autonomous watching"""
        self.running = True
        logger.info(f"🤖 Agentic RAG started for {self.codebase_id}")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.watch_git_events()),
            asyncio.create_task(self.periodic_full_sync()),
            asyncio.create_task(self.periodic_state_update())
        ]
        
        await asyncio.gather(*tasks)
        
    async def stop_watching(self):
        """Stop watching"""
        self.running = False
        logger.info(f"🛑 Agentic RAG stopped for {self.codebase_id}")
        
    async def watch_git_events(self):
        """Watch for git commits/pushes"""
        logger.info("👀 Watching git events...")
        
        async for event in self.git_watcher.stream():
            if not self.running:
                break
                
            if event['type'] == 'commit':
                await self.handle_commit(event)
                
    async def handle_commit(self, event: Dict):
        """Handle new commit"""
        logger.info(f"📝 New commit by {event['author']}: {event['message']}")
        
        try:
            # 1. Extract changed files
            changed_files = event['changed_files']
            
            if not changed_files:
                logger.info("No files changed, skipping index")
                return
                
            # 2. Re-index changed files
            await self.reindex_files(changed_files)
            
            # 3. Update current state
            await self.update_current_state()
            
            # 4. Check for drift
            await self.check_drift()
            
            # 5. Notify team
            await self.notify_team(
                f"📝 {event['author']} committed: {event['message']}\n"
                f"Files changed: {len(changed_files)}"
            )
            
        except Exception as e:
            logger.error(f"Error handling commit: {e}")
            
    async def reindex_files(self, file_paths: List[str]):
        """Re-index specific files"""
        logger.info(f"🔄 Re-indexing {len(file_paths)} files...")
        
        # Filter code files only
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.rs', '.go', '.java'}
        code_files = [
            f for f in file_paths 
            if Path(f).suffix in code_extensions
        ]
        
        if not code_files:
            logger.info("No code files to index")
            return
            
        # Read and parse files
        snippets = []
        for file_path in code_files:
            full_path = Path(self.repo_path) / file_path
            
            if not full_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
                
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    
                # Create snippet
                snippet = CodeSnippet(
                    path=file_path,
                    content=content,
                    language=self._detect_language(file_path),
                    start_line=1,
                    end_line=len(content.split('\n')),
                    snippet_type='file',
                    name=Path(file_path).name
                )
                snippets.append(snippet)
                
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                
        # Generate embeddings and store
        if snippets:
            embeddings = self.codebase_rag.embedder.encode(
                [s.content for s in snippets]
            ).tolist()
            
            await self.codebase_rag._store_in_qdrant(
                codebase_id=self.codebase_id,
                user_id=self.team_id,  # Team-level storage
                mode="team",
                snippets=snippets,
                embeddings=embeddings
            )
            
            logger.info(f"✅ Indexed {len(snippets)} files")
            
    async def update_current_state(self):
        """Generate current state documentation"""
        logger.info("📊 Updating current state...")
        
        try:
            # 1. Analyze codebase structure
            structure = await self.analyze_structure()
            
            # 2. Generate state documentation with AI
            state_doc = await self.generate_state_doc(structure)
            
            # 3. Store in database
            await self.store_current_state(state_doc)
            
            logger.info("✅ Current state updated")
            
        except Exception as e:
            logger.error(f"Error updating current state: {e}")
            
    async def analyze_structure(self) -> Dict[str, Any]:
        """Analyze codebase structure"""
        from pathlib import Path
        
        structure = {
            'total_files': 0,
            'total_lines': 0,
            'languages': {},
            'directories': [],
            'entry_points': [],
            'dependencies': []
        }
        
        # Walk directory tree
        for path in Path(self.repo_path).rglob('*'):
            if path.is_file():
                # Skip git and node_modules
                if '.git' in path.parts or 'node_modules' in path.parts:
                    continue
                    
                structure['total_files'] += 1
                
                # Count lines
                try:
                    with open(path, 'r') as f:
                        lines = len(f.readlines())
                        structure['total_lines'] += lines
                        
                    # Track language
                    lang = self._detect_language(str(path))
                    structure['languages'][lang] = structure['languages'].get(lang, 0) + 1
                    
                except:
                    pass
                    
        return structure
        
    async def generate_state_doc(self, structure: Dict) -> str:
        """Generate state documentation with AI"""
        
        prompt = f"""
Generate a comprehensive "Current State" document for this codebase:

Structure:
- Total files: {structure['total_files']}
- Total lines: {structure['total_lines']}
- Languages: {structure['languages']}

Generate a markdown document with:
1. Overview
2. Architecture summary
3. Key components
4. Recent changes
5. Technical debt
6. Next steps

Be concise and technical.
"""
        
        state_doc = await self.deepseek.complete_code(
            code=prompt,
            position=len(prompt),
            language='markdown',
            max_tokens=500,
            temperature=0.3
        )
        
        return state_doc[0] if state_doc else "# Current State\n\nNo documentation generated."
        
    async def store_current_state(self, state_doc: str):
        """Store current state in database"""
        # Store in Theta RAG for querying
        embedding = self.codebase_rag.embedder.encode(state_doc).tolist()
        
        await self.codebase_rag.theta_rag.upsert_vectors(
            collection_name=f"{self.codebase_id}_state",
            points=[{
                "id": f"state_{datetime.now().isoformat()}",
                "vector": embedding,
                "payload": {
                    "type": "current_state",
                    "timestamp": datetime.now().isoformat(),
                    "content": state_doc,
                    "codebase_id": self.codebase_id,
                    "team_id": self.team_id
                }
            }]
        )
        
    async def check_drift(self):
        """Check for drift from PM plan"""
        # TODO: Implement PM plan comparison
        # This will be implemented in pm_integration.py
        pass
        
    async def notify_team(self, message: str):
        """Notify team of events"""
        # TODO: Implement team notifications
        # Could use webhooks, Slack, email, etc.
        logger.info(f"📢 Team notification: {message}")
        
    async def periodic_full_sync(self):
        """Periodic full re-index (daily)"""
        while self.running:
            await asyncio.sleep(86400)  # 24 hours
            
            logger.info("🔄 Starting daily full sync...")
            
            try:
                # Re-index entire codebase
                await self.codebase_rag.index_codebase(
                    repo_url=f"file://{self.repo_path}",
                    user_id=self.team_id,
                    mode="team",
                    learn_options={
                        "functions": True,
                        "classes": True,
                        "imports": True,
                        "comments": True
                    }
                )
                
                logger.info("✅ Daily full sync complete")
                
            except Exception as e:
                logger.error(f"Error in full sync: {e}")
                
    async def periodic_state_update(self):
        """Periodic state update (hourly)"""
        while self.running:
            await asyncio.sleep(3600)  # 1 hour
            
            logger.info("📊 Hourly state update...")
            await self.update_current_state()
            
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        ext = Path(file_path).suffix
        return ext_map.get(ext, 'unknown')


# Global registry of active agents
_active_agents: Dict[str, AgenticCodebaseRAG] = {}


async def start_agentic_rag(
    codebase_id: str,
    team_id: str,
    org_id: str,
    repo_path: str
) -> AgenticCodebaseRAG:
    """Start agentic RAG for a codebase"""
    
    if codebase_id in _active_agents:
        logger.warning(f"Agentic RAG already running for {codebase_id}")
        return _active_agents[codebase_id]
        
    agent = AgenticCodebaseRAG(
        codebase_id=codebase_id,
        team_id=team_id,
        org_id=org_id,
        repo_path=repo_path
    )
    
    # Start in background
    asyncio.create_task(agent.start_watching())
    
    _active_agents[codebase_id] = agent
    
    return agent


async def stop_agentic_rag(codebase_id: str):
    """Stop agentic RAG for a codebase"""
    
    if codebase_id in _active_agents:
        agent = _active_agents[codebase_id]
        await agent.stop_watching()
        del _active_agents[codebase_id]
        logger.info(f"✅ Stopped agentic RAG for {codebase_id}")
