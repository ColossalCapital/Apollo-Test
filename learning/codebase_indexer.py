"""
Codebase Indexer

Index entire codebase for RAG and project planning.

Features:
- Parse all files by language
- Extract code structure
- Generate embeddings
- Store in Theta RAG
- Detect patterns
- Analyze dependencies
"""

import logging
import os
from typing import Dict, List, Optional
from pathlib import Path
import ast
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class CodebaseIndexer:
    """
    Index codebase for RAG
    
    Supports:
    - Python, JavaScript/TypeScript, Rust, Go
    - Structure extraction (classes, functions, imports)
    - Dependency analysis
    - Pattern detection
    - Theta RAG storage
    """
    
    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp'
        }
        
    async def index_codebase(
        self,
        repo_path: str,
        codebase_id: str,
        user_id: str,
        org_id: str
    ) -> Dict:
        """
        Index entire codebase
        
        Args:
            repo_path: Local path to repository
            codebase_id: Unique codebase identifier
            user_id: User ID
            org_id: Organization ID
            
        Returns:
            {
                'success': bool,
                'files_indexed': int,
                'structure': Dict,
                'patterns': List[str],
                'dependencies': Dict,
                'stats': Dict
            }
        """
        
        logger.info(f"📚 Indexing codebase: {codebase_id}")
        
        result = {
            'codebase_id': codebase_id,
            'started_at': datetime.now().isoformat(),
            'success': False
        }
        
        try:
            # 1. Scan repository
            files = await self._scan_repository(repo_path)
            logger.info(f"Found {len(files)} code files")
            
            # 2. Parse files
            parsed_files = []
            for file_path in files:
                parsed = await self._parse_file(file_path, repo_path)
                if parsed:
                    parsed_files.append(parsed)
                    
            logger.info(f"Parsed {len(parsed_files)} files")
            
            # 3. Extract structure
            structure = await self._extract_structure(parsed_files)
            logger.info(f"Extracted structure: {len(structure['classes'])} classes, {len(structure['functions'])} functions")
            
            # 4. Analyze dependencies
            dependencies = await self._analyze_dependencies(parsed_files)
            logger.info(f"Analyzed {len(dependencies)} dependencies")
            
            # 5. Detect patterns
            patterns = await self._detect_patterns(parsed_files, structure)
            logger.info(f"Detected {len(patterns)} patterns")
            
            # 6. Generate embeddings
            embeddings = await self._generate_embeddings(parsed_files, structure)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # 7. Store in Theta RAG
            await self._store_in_theta_rag(
                codebase_id,
                user_id,
                org_id,
                parsed_files,
                structure,
                dependencies,
                patterns,
                embeddings
            )
            
            # 8. Generate stats
            stats = {
                'total_files': len(files),
                'parsed_files': len(parsed_files),
                'total_lines': sum(f['lines'] for f in parsed_files),
                'languages': self._count_languages(parsed_files),
                'classes': len(structure['classes']),
                'functions': len(structure['functions']),
                'dependencies': len(dependencies),
                'patterns': len(patterns)
            }
            
            result.update({
                'success': True,
                'files_indexed': len(parsed_files),
                'structure': structure,
                'patterns': patterns,
                'dependencies': dependencies,
                'stats': stats,
                'completed_at': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Indexing complete: {codebase_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Indexing failed: {e}")
            result['error'] = str(e)
            return result
            
    async def _scan_repository(self, repo_path: str) -> List[str]:
        """Scan repository for code files"""
        
        code_files = []
        
        # Walk directory tree
        for root, dirs, files in os.walk(repo_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in [
                '.git', 'node_modules', '__pycache__', 'target',
                'build', 'dist', '.next', 'venv', 'env'
            ]]
            
            for file in files:
                ext = Path(file).suffix
                if ext in self.supported_extensions:
                    file_path = os.path.join(root, file)
                    code_files.append(file_path)
                    
        return code_files
        
    async def _parse_file(
        self,
        file_path: str,
        repo_path: str
    ) -> Optional[Dict]:
        """Parse a single file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            ext = Path(file_path).suffix
            language = self.supported_extensions[ext]
            
            # Get relative path
            rel_path = os.path.relpath(file_path, repo_path)
            
            # Parse based on language
            if language == 'python':
                parsed = await self._parse_python(content)
            elif language in ['javascript', 'typescript']:
                parsed = await self._parse_javascript(content)
            elif language == 'rust':
                parsed = await self._parse_rust(content)
            else:
                parsed = await self._parse_generic(content)
                
            return {
                'path': rel_path,
                'language': language,
                'lines': len(content.split('\n')),
                'content': content,
                **parsed
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
            
    async def _parse_python(self, content: str) -> Dict:
        """Parse Python file"""
        
        try:
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if node.col_offset == 0:
                        functions.append({
                            'name': node.name,
                            'line': node.lineno,
                            'args': [arg.arg for arg in node.args.args]
                        })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        imports.append(node.module)
                        
            return {
                'classes': classes,
                'functions': functions,
                'imports': imports
            }
            
        except Exception as e:
            logger.warning(f"Python parsing failed: {e}")
            return {'classes': [], 'functions': [], 'imports': []}
            
    async def _parse_javascript(self, content: str) -> Dict:
        """Parse JavaScript/TypeScript file"""
        
        # Simple regex-based parsing
        # TODO: Use proper JS parser (esprima, babel)
        
        classes = []
        functions = []
        imports = []
        
        # Find classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
            
        # Find functions
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\()'
        for match in re.finditer(func_pattern, content):
            name = match.group(1) or match.group(2)
            functions.append({
                'name': name,
                'line': content[:match.start()].count('\n') + 1
            })
            
        # Find imports
        import_pattern = r'import\s+.*?from\s+[\'"](.+?)[\'"]'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
            
        return {
            'classes': classes,
            'functions': functions,
            'imports': imports
        }
        
    async def _parse_rust(self, content: str) -> Dict:
        """Parse Rust file"""
        
        # Simple regex-based parsing
        
        structs = []
        functions = []
        imports = []
        
        # Find structs
        struct_pattern = r'struct\s+(\w+)'
        for match in re.finditer(struct_pattern, content):
            structs.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
            
        # Find functions
        func_pattern = r'fn\s+(\w+)'
        for match in re.finditer(func_pattern, content):
            functions.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
            
        # Find imports
        import_pattern = r'use\s+([\w:]+)'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
            
        return {
            'classes': structs,  # Treat structs as classes
            'functions': functions,
            'imports': imports
        }
        
    async def _parse_generic(self, content: str) -> Dict:
        """Generic parsing for unsupported languages"""
        
        return {
            'classes': [],
            'functions': [],
            'imports': []
        }
        
    async def _extract_structure(self, parsed_files: List[Dict]) -> Dict:
        """Extract overall codebase structure"""
        
        structure = {
            'classes': [],
            'functions': [],
            'modules': []
        }
        
        for file in parsed_files:
            # Add classes with file context
            for cls in file.get('classes', []):
                structure['classes'].append({
                    'name': cls['name'],
                    'file': file['path'],
                    'line': cls.get('line'),
                    'language': file['language']
                })
                
            # Add functions with file context
            for func in file.get('functions', []):
                structure['functions'].append({
                    'name': func['name'],
                    'file': file['path'],
                    'line': func.get('line'),
                    'language': file['language']
                })
                
            # Add module
            structure['modules'].append({
                'path': file['path'],
                'language': file['language'],
                'lines': file['lines']
            })
            
        return structure
        
    async def _analyze_dependencies(self, parsed_files: List[Dict]) -> Dict:
        """Analyze dependencies between files"""
        
        dependencies = {}
        
        for file in parsed_files:
            file_deps = []
            
            for imp in file.get('imports', []):
                # Check if import is internal (relative path)
                if imp.startswith('.') or '/' in imp:
                    file_deps.append(imp)
                    
            if file_deps:
                dependencies[file['path']] = file_deps
                
        return dependencies
        
    async def _detect_patterns(
        self,
        parsed_files: List[Dict],
        structure: Dict
    ) -> List[str]:
        """Detect code patterns"""
        
        patterns = []
        
        # Detect MVC pattern
        has_models = any('model' in f['path'].lower() for f in parsed_files)
        has_views = any('view' in f['path'].lower() or 'component' in f['path'].lower() for f in parsed_files)
        has_controllers = any('controller' in f['path'].lower() or 'route' in f['path'].lower() for f in parsed_files)
        
        if has_models and has_views and has_controllers:
            patterns.append('MVC Architecture')
            
        # Detect API pattern
        has_api = any('api' in f['path'].lower() or 'endpoint' in f['path'].lower() for f in parsed_files)
        if has_api:
            patterns.append('REST API')
            
        # Detect testing
        has_tests = any('test' in f['path'].lower() or 'spec' in f['path'].lower() for f in parsed_files)
        if has_tests:
            patterns.append('Test Coverage')
            
        # Detect frontend framework
        has_react = any('react' in str(f.get('imports', [])).lower() for f in parsed_files)
        if has_react:
            patterns.append('React Framework')
            
        return patterns
        
    async def _generate_embeddings(
        self,
        parsed_files: List[Dict],
        structure: Dict
    ) -> List[Dict]:
        """Generate embeddings for RAG"""
        
        embeddings = []
        
        # TODO: Use actual embedding model
        # For now, just prepare the data
        
        for file in parsed_files:
            embeddings.append({
                'type': 'file',
                'path': file['path'],
                'content': file['content'][:1000],  # First 1000 chars
                'metadata': {
                    'language': file['language'],
                    'lines': file['lines'],
                    'classes': len(file.get('classes', [])),
                    'functions': len(file.get('functions', []))
                }
            })
            
        return embeddings
        
    async def _store_in_theta_rag(
        self,
        codebase_id: str,
        user_id: str,
        org_id: str,
        parsed_files: List[Dict],
        structure: Dict,
        dependencies: Dict,
        patterns: List[str],
        embeddings: List[Dict]
    ):
        """Store in Theta RAG"""
        
        # TODO: Implement Theta RAG storage
        logger.info(f"Storing {len(embeddings)} embeddings in Theta RAG")
        
        # For now, just log
        logger.info(f"Codebase: {codebase_id}")
        logger.info(f"User: {user_id}, Org: {org_id}")
        logger.info(f"Files: {len(parsed_files)}")
        logger.info(f"Structure: {len(structure['classes'])} classes, {len(structure['functions'])} functions")
        logger.info(f"Dependencies: {len(dependencies)}")
        logger.info(f"Patterns: {patterns}")
        
    def _count_languages(self, parsed_files: List[Dict]) -> Dict[str, int]:
        """Count files by language"""
        
        counts = {}
        for file in parsed_files:
            lang = file['language']
            counts[lang] = counts.get(lang, 0) + 1
        return counts


# Global instance
_codebase_indexer = CodebaseIndexer()


def get_codebase_indexer() -> CodebaseIndexer:
    """Get global codebase indexer"""
    return _codebase_indexer
