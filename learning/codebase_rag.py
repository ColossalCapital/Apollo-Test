"""
Codebase RAG - Index and Query Codebases with AI

Features:
- Index entire codebases into Qdrant
- Semantic code search
- Pattern recognition
- API documentation extraction
- Best practices learning
- Privacy-isolated storage

Two Modes:
1. Learning Mode: Index external codebases (read-only) to improve AI suggestions
2. Development Mode: Index user's project (read-write) for AI-assisted development
"""

import os
import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import asyncio

from git import Repo
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from learning.theta_rag_client import ThetaRAGClient, ThetaRAGConfig
from learning.jarvislabs_rag_client import JarvisLabsRAGClient

logger = logging.getLogger(__name__)


class CodeSnippet:
    """Represents a code snippet with metadata"""
    
    def __init__(
        self,
        path: str,
        content: str,
        language: str,
        start_line: int,
        end_line: int,
        snippet_type: str,  # "function", "class", "import", "comment"
        name: Optional[str] = None
    ):
        self.path = path
        self.content = content
        self.language = language
        self.start_line = start_line
        self.end_line = end_line
        self.snippet_type = snippet_type
        self.name = name
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "content": self.content,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "snippet_type": self.snippet_type,
            "name": self.name
        }


class LearnedPatterns:
    """Patterns learned from codebase"""
    
    def __init__(self):
        self.naming_conventions: List[str] = []
        self.architecture_patterns: List[str] = []
        self.api_patterns: List[str] = []
        self.error_handling_patterns: List[str] = []
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "naming_conventions": self.naming_conventions,
            "architecture_patterns": self.architecture_patterns,
            "api_patterns": self.api_patterns,
            "error_handling_patterns": self.error_handling_patterns
        }


class CodebaseIndex:
    """Metadata about indexed codebase"""
    
    def __init__(
        self,
        codebase_id: str,
        user_id: str,
        repo_url: str,
        mode: str,  # "learning" or "development"
        files_indexed: int,
        patterns_learned: int,
        embeddings_created: int
    ):
        self.codebase_id = codebase_id
        self.user_id = user_id
        self.repo_url = repo_url
        self.mode = mode
        self.files_indexed = files_indexed
        self.patterns_learned = patterns_learned
        self.embeddings_created = embeddings_created
        self.created_at = datetime.now()


class CodebaseRAG:
    """
    RAG system for codebase indexing and querying
    
    Uses:
    - Qdrant for vector storage
    - BGE embeddings for semantic search
    - Tree-sitter for code parsing
    - Privacy isolation per user
    """
    
    def __init__(
        self,
        theta_config: Optional[ThetaRAGConfig] = None,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "codebases"
    ):
        self.collection_name = collection_name
        
        # Load Theta config from environment if not provided
        self.theta_config = theta_config or ThetaRAGConfig.from_env()
        
        # Initialize storage backend with fallback
        self.active_provider = None
        
        if self.theta_config.enabled:
            try:
                # Try Theta RAG first (production)
                self.theta_rag = ThetaRAGClient(
                    api_key=self.theta_config.api_key,
                    wallet=self.theta_config.wallet
                )
                self.use_theta = True
                self.active_provider = "theta"
                logger.info("✅ Using Theta RAG (primary, 97% cheaper)")
                
                # Initialize JarvisLabs as fallback
                jarvislabs_key = os.getenv("JARVISLABS_API_KEY")
                if jarvislabs_key:
                    self.jarvislabs_rag = JarvisLabsRAGClient(api_key=jarvislabs_key)
                    logger.info("✅ JarvisLabs RAG ready as fallback")
                else:
                    self.jarvislabs_rag = None
                    logger.warning("⚠️  JarvisLabs not configured (no fallback)")
                    
            except Exception as e:
                logger.error(f"❌ Theta RAG failed to initialize: {e}")
                
                # Fallback to JarvisLabs
                jarvislabs_key = os.getenv("JARVISLABS_API_KEY")
                if jarvislabs_key:
                    logger.info("🔄 Falling back to JarvisLabs RAG...")
                    self.jarvislabs_rag = JarvisLabsRAGClient(api_key=jarvislabs_key)
                    self.use_theta = False
                    self.active_provider = "jarvislabs"
                    logger.info("✅ Using JarvisLabs RAG (fallback)")
                else:
                    # Final fallback to local Qdrant
                    logger.warning("🔄 Falling back to local Qdrant...")
                    self.qdrant = QdrantClient(url=qdrant_url)
                    self.qdrant_url = qdrant_url
                    self.use_theta = False
                    self.active_provider = "local"
                    logger.info("⚠️  Using local Qdrant (final fallback)")
        else:
            # Use local Qdrant (development)
            self.qdrant = QdrantClient(url=qdrant_url)
            self.qdrant_url = qdrant_url
            self.use_theta = False
            self.active_provider = "local"
            logger.info("⚠️  Using local Qdrant (development only)")
        
        # Initialize embedding model (BGE for code)
        self.embedder = SentenceTransformer('BAAI/bge-small-en-v1.5')
        
        # Create collection if it doesn't exist
        asyncio.create_task(self._ensure_collection())
        
        logger.info(f"CodebaseRAG initialized: {collection_name}")
    
    async def index_codebase(
        self,
        repo_url: str,
        user_id: str,
        mode: str,  # "learning" or "development"
        learn_options: Dict[str, bool],
        branch: str = "main"
    ) -> CodebaseIndex:
        """
        Index codebase into Qdrant with privacy isolation
        
        Steps:
        1. Clone repo (or read local)
        2. Parse all files
        3. Extract:
           - Functions/classes
           - Patterns
           - APIs
           - Documentation
        4. Generate embeddings (BGE model)
        5. Store in Qdrant with privacy namespace
        6. Store metadata in PostgreSQL
        
        Privacy Namespace:
        - Learning Mode: codebases/learning/{user_id}/{codebase_id}
        - Development Mode: codebases/development/{user_id}/{codebase_id}
        """
        logger.info(f"Indexing codebase: {repo_url} (mode: {mode})")
        
        try:
            # Generate codebase ID
            codebase_id = self._generate_codebase_id(repo_url, user_id)
            
            # Clone repository
            repo_path = await self._clone_repo(repo_url, branch, codebase_id)
            
            # Parse all files
            snippets = await self._parse_codebase(repo_path)
            logger.info(f"Parsed {len(snippets)} code snippets")
            
            # Learn patterns (if enabled)
            patterns = None
            if learn_options.get("patterns", False):
                patterns = await self._learn_patterns(snippets)
                logger.info(f"Learned {len(patterns.naming_conventions)} patterns")
            
            # Generate embeddings
            embeddings = await self._generate_embeddings(snippets)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Store in Qdrant with privacy namespace
            await self._store_in_qdrant(
                codebase_id,
                user_id,
                mode,
                snippets,
                embeddings
            )
            
            # Clean up cloned repo
            await self._cleanup_repo(repo_path)
            
            return CodebaseIndex(
                codebase_id=codebase_id,
                user_id=user_id,
                repo_url=repo_url,
                mode=mode,
                files_indexed=len(set(s.path for s in snippets)),
                patterns_learned=len(patterns.naming_conventions) if patterns else 0,
                embeddings_created=len(embeddings)
            )
            
        except Exception as e:
            logger.error(f"Codebase indexing failed: {e}")
            raise
    
    async def query_codebase(
        self,
        query: str,
        codebase_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[CodeSnippet]:
        """
        Semantic search across codebase
        
        Returns most relevant code snippets based on query
        """
        logger.info(f"Querying codebase {codebase_id}: {query}")
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Privacy filter
            filters = {
                "must": [
                    {"key": "codebase_id", "match": {"value": codebase_id}},
                    {"key": "user_id", "match": {"value": user_id}}
                ]
            }
            
            # Search with automatic failover
            if self.active_provider == "theta":
                try:
                    # Try Theta RAG first
                    results = await self.theta_rag.search(
                        collection_name=self.collection_name,
                        query_vector=query_embedding,
                        limit=limit,
                        filters=filters
                    )
                    logger.info(f"✅ Searched Theta RAG (earned TFUEL)")
                except Exception as e:
                    logger.error(f"❌ Theta RAG search failed: {e}")
                    
                    # Fallback to JarvisLabs
                    if self.jarvislabs_rag:
                        logger.info("🔄 Falling back to JarvisLabs...")
                        results = await self.jarvislabs_rag.search(
                            collection_name=self.collection_name,
                            query_vector=query_embedding,
                            limit=limit,
                            filters=filters
                        )
                        self.active_provider = "jarvislabs"  # Switch provider
                        logger.info(f"✅ Searched JarvisLabs RAG (fallback)")
                    else:
                        raise Exception("No fallback provider available")
                        
            elif self.active_provider == "jarvislabs":
                # Using JarvisLabs
                results = await self.jarvislabs_rag.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                    filters=filters
                )
                logger.info(f"✅ Searched JarvisLabs RAG")
            else:
                # Using local Qdrant
                results = self.qdrant.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                    query_filter=filters
                )
            
            # Convert results to CodeSnippet objects
            snippets = []
            for result in results:
                # Handle both Theta and local Qdrant response formats
                payload = result.get("payload") if isinstance(result, dict) else result.payload
                
                snippet = CodeSnippet(
                    path=payload["path"],
                    content=payload["content"],
                    language=payload["language"],
                    start_line=payload["start_line"],
                    end_line=payload["end_line"],
                    snippet_type=payload["snippet_type"],
                    name=payload.get("name")
                )
                snippets.append(snippet)
            
            logger.info(f"Found {len(snippets)} relevant snippets")
            return snippets
            
        except Exception as e:
            logger.error(f"Codebase query failed: {e}")
            raise
    
    async def learn_patterns(
        self,
        codebase_id: str,
        user_id: str
    ) -> LearnedPatterns:
        """
        Extract patterns from codebase:
        - Naming conventions
        - Architecture patterns
        - API design patterns
        - Error handling patterns
        """
        logger.info(f"Learning patterns from codebase: {codebase_id}")
        
        patterns = LearnedPatterns()
        
        # TODO: Implement pattern learning
        # For now, return empty patterns
        
        return patterns
    
    def _generate_codebase_id(self, repo_url: str, user_id: str) -> str:
        """Generate unique codebase ID"""
        hash_input = f"{repo_url}_{user_id}_{datetime.now().timestamp()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    async def _clone_repo(
        self,
        repo_url: str,
        branch: str,
        codebase_id: str
    ) -> Path:
        """Clone repository to temporary directory"""
        clone_dir = Path(f"/tmp/codebases/{codebase_id}")
        clone_dir.mkdir(parents=True, exist_ok=True)
        
        # Clone repository (shallow clone for speed)
        try:
            Repo.clone_from(
                repo_url,
                clone_dir,
                branch=branch,
                depth=1,  # Shallow clone
                single_branch=True
            )
            logger.info(f"Cloned repo to: {clone_dir}")
        except Exception as e:
            logger.error(f"Failed to clone repo: {e}")
            raise
        
        return clone_dir
    
    async def _parse_codebase(self, repo_path: Path) -> List[CodeSnippet]:
        """
        Parse all files in codebase
        
        Extracts:
        - Functions
        - Classes
        - Imports
        - Comments/documentation
        """
        snippets = []
        
        # Supported file extensions
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
        }
        
        # Walk through all files
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                language = extensions[file_path.suffix]
                
                # TODO: Use tree-sitter to parse file
                # For now, just read file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create snippet for entire file
                    snippet = CodeSnippet(
                        path=str(file_path.relative_to(repo_path)),
                        content=content,
                        language=language,
                        start_line=1,
                        end_line=len(content.split('\n')),
                        snippet_type="file"
                    )
                    snippets.append(snippet)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
        
        return snippets
    
    async def _learn_patterns(
        self,
        snippets: List[CodeSnippet]
    ) -> LearnedPatterns:
        """Learn patterns from code snippets"""
        patterns = LearnedPatterns()
        
        # TODO: Implement pattern learning with LLM
        # For now, return empty patterns
        
        return patterns
    
    async def _generate_embeddings(
        self,
        snippets: List[CodeSnippet]
    ) -> List[List[float]]:
        """Generate embeddings for code snippets"""
        embeddings = []
        
        # Batch encode for efficiency
        texts = [snippet.content for snippet in snippets]
        
        # Generate embeddings with BGE model
        batch_embeddings = self.embedder.encode(
            texts,
            show_progress_bar=True,
            batch_size=32
        )
        
        # Convert to list of lists
        embeddings = [emb.tolist() for emb in batch_embeddings]
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    async def _store_in_qdrant(
        self,
        codebase_id: str,
        user_id: str,
        mode: str,
        snippets: List[CodeSnippet],
        embeddings: List[List[float]]
    ):
        """Store snippets and embeddings with privacy isolation (Theta or local)"""
        
        # Create points with privacy namespace
        points = []
        for i, (snippet, embedding) in enumerate(zip(snippets, embeddings)):
            point_id = hashlib.sha256(
                f"{codebase_id}_{snippet.path}_{snippet.start_line}".encode()
            ).hexdigest()[:16]
            
            payload = {
                "codebase_id": codebase_id,
                "user_id": user_id,
                "mode": mode,
                "path": snippet.path,
                "language": snippet.language,
                "content": snippet.content,
                "start_line": snippet.start_line,
                "end_line": snippet.end_line,
                "snippet_type": snippet.snippet_type,
                "name": snippet.name,
                # Privacy namespace
                "namespace": f"codebases/{mode}/{user_id}/{codebase_id}"
            }
            
            if self.use_theta:
                # Theta RAG format
                point = {
                    "id": point_id,
                    "vector": embedding,
                    "payload": payload
                }
            else:
                # Local Qdrant format
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            
            points.append(point)
        
        # Batch upsert with automatic failover
        if self.active_provider == "theta":
            try:
                # Try Theta RAG first
                result = await self.theta_rag.upsert_vectors(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.info(f"✅ Stored {len(points)} snippets in Theta RAG (earned TFUEL)")
            except Exception as e:
                logger.error(f"❌ Theta RAG storage failed: {e}")
                
                # Fallback to JarvisLabs
                if self.jarvislabs_rag:
                    logger.info("🔄 Falling back to JarvisLabs...")
                    result = await self.jarvislabs_rag.upsert_vectors(
                        collection_name=self.collection_name,
                        points=points
                    )
                    self.active_provider = "jarvislabs"  # Switch provider
                    logger.info(f"✅ Stored {len(points)} snippets in JarvisLabs RAG (fallback)")
                else:
                    raise Exception("No fallback provider available")
                    
        elif self.active_provider == "jarvislabs":
            # Using JarvisLabs
            result = await self.jarvislabs_rag.upsert_vectors(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"✅ Stored {len(points)} snippets in JarvisLabs RAG")
        else:
            # Using local Qdrant
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Stored {len(points)} snippets in local Qdrant")
    
    async def _cleanup_repo(self, repo_path: Path):
        """Clean up cloned repository"""
        import shutil
        try:
            shutil.rmtree(repo_path)
            logger.info(f"Cleaned up repo: {repo_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup repo: {e}")
    
    async def _ensure_collection(self):
        """Create collection if it doesn't exist (Theta or local)"""
        try:
            if self.use_theta:
                # Check if Theta RAG collection exists
                exists = await self.theta_rag.collection_exists(self.collection_name)
                if not exists:
                    await self.theta_rag.create_collection(
                        collection_name=self.collection_name,
                        vector_size=384,  # BGE-small embedding size
                        distance="cosine"
                    )
                    logger.info(f"✅ Created Theta RAG collection: {self.collection_name}")
            else:
                # Check if local Qdrant collection exists
                collections = self.qdrant.get_collections().collections
                collection_names = [c.name for c in collections]
                
                if self.collection_name not in collection_names:
                    self.qdrant.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=384,  # BGE-small embedding size
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Created local Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Failed to ensure collection (Qdrant not available, will use Theta RAG): {e}")
