"""
Code Generation Agent

Generates code from refined tickets with full context awareness.

Features:
- Reads refined tickets
- Analyzes Mermaid diagrams
- Understands project context
- Generates complete implementations
- Creates tests
- Handles dependencies
- Creates PRs
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess

from learning.deepseek_coder import DeepSeekCoder
from learning.agentic_codebase_rag import get_agentic_rag

logger = logging.getLogger(__name__)


class CodeGenerationAgent:
    """
    Generates code from refined tickets
    
    Workflow:
    1. Read refined ticket
    2. Analyze Mermaid diagram
    3. Get project context from Agentic RAG
    4. Generate implementation
    5. Generate tests
    6. Create PR
    7. Send to Atlas for review
    """
    
    def __init__(self):
        self.deepseek = DeepSeekCoder(model_size="6.7b")
        
    async def generate_from_ticket(
        self,
        ticket: Dict,
        codebase_id: str,
        repo_path: str,
        create_pr: bool = True
    ) -> Dict:
        """
        Generate complete implementation from ticket
        
        Args:
            ticket: Refined ticket with full context
            codebase_id: Codebase ID
            repo_path: Local repo path
            create_pr: Whether to create PR
            
        Returns:
            {
                'success': bool,
                'files_created': List[str],
                'files_modified': List[str],
                'tests_created': List[str],
                'pr_url': str,
                'explanation': str
            }
        """
        
        logger.info(f"🤖 Generating code for: {ticket['title']}")
        
        # Get project context
        agentic_rag = get_agentic_rag(codebase_id)
        project_context = await agentic_rag.get_current_state()
        
        # Analyze ticket
        implementation_plan = await self._create_implementation_plan(
            ticket,
            project_context
        )
        
        logger.info(f"📋 Implementation plan: {len(implementation_plan['steps'])} steps")
        
        # Generate code for each step
        generated_files = []
        for step in implementation_plan['steps']:
            files = await self._generate_step(
                step,
                ticket,
                project_context,
                repo_path
            )
            generated_files.extend(files)
            
        # Generate tests
        test_files = await self._generate_tests(
            ticket,
            generated_files,
            project_context,
            repo_path
        )
        
        # Create PR
        pr_url = None
        if create_pr:
            pr_url = await self._create_pr(
                ticket,
                generated_files,
                test_files,
                repo_path
            )
            
        return {
            'success': True,
            'files_created': [f['path'] for f in generated_files if f['action'] == 'create'],
            'files_modified': [f['path'] for f in generated_files if f['action'] == 'modify'],
            'tests_created': [f['path'] for f in test_files],
            'pr_url': pr_url,
            'explanation': implementation_plan['explanation']
        }
        
    async def _create_implementation_plan(
        self,
        ticket: Dict,
        project_context: Dict
    ) -> Dict:
        """Create step-by-step implementation plan"""
        
        prompt = f"""Create an implementation plan for this ticket.

Ticket: {ticket['title']}

Description:
{ticket.get('description', '')}

Mermaid Diagram:
{ticket.get('mermaid_diagram', 'None')}

Acceptance Criteria:
{chr(10).join(ticket.get('acceptance_criteria', []))}

Project Context:
- Type: {project_context.get('type')}
- Tech Stack: {', '.join(project_context.get('tech_stack', []))}
- Existing Components: {', '.join(project_context.get('components', [])[:10])}

Create a step-by-step implementation plan. For each step, specify:
1. What to do
2. Which files to create/modify
3. Key code to write
4. Dependencies on other steps

Format as JSON:
{{
  "explanation": "High-level approach",
  "steps": [
    {{
      "step": 1,
      "description": "Create component",
      "files": ["path/to/Component.tsx"],
      "action": "create",
      "dependencies": []
    }}
  ]
}}
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language='json',
                max_tokens=800,
                temperature=0.3
            )
            
            if result and len(result) > 0:
                import json
                return json.loads(result[0])
                
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            
        # Fallback plan
        return {
            'explanation': 'Simple implementation',
            'steps': [
                {
                    'step': 1,
                    'description': 'Implement feature',
                    'files': ['src/components/NewComponent.tsx'],
                    'action': 'create',
                    'dependencies': []
                }
            ]
        }
        
    async def _generate_step(
        self,
        step: Dict,
        ticket: Dict,
        project_context: Dict,
        repo_path: str
    ) -> List[Dict]:
        """Generate code for a single step"""
        
        generated_files = []
        
        for file_path in step['files']:
            # Check if file exists
            full_path = os.path.join(repo_path, file_path)
            file_exists = os.path.exists(full_path)
            
            if file_exists and step['action'] == 'create':
                # File exists, modify instead
                step['action'] = 'modify'
                
            # Get existing code if modifying
            existing_code = ''
            if step['action'] == 'modify' and file_exists:
                with open(full_path, 'r') as f:
                    existing_code = f.read()
                    
            # Generate code
            code = await self._generate_file_code(
                file_path=file_path,
                step=step,
                ticket=ticket,
                project_context=project_context,
                existing_code=existing_code
            )
            
            if code:
                # Write to file
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(code)
                    
                generated_files.append({
                    'path': file_path,
                    'action': step['action'],
                    'code': code
                })
                
                logger.info(f"✅ Generated: {file_path}")
                
        return generated_files
        
    async def _generate_file_code(
        self,
        file_path: str,
        step: Dict,
        ticket: Dict,
        project_context: Dict,
        existing_code: str = ''
    ) -> Optional[str]:
        """Generate code for a single file"""
        
        # Determine language from file extension
        ext = os.path.splitext(file_path)[1]
        language_map = {
            '.tsx': 'typescript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.js': 'javascript',
            '.py': 'python',
            '.rs': 'rust',
            '.go': 'go'
        }
        language = language_map.get(ext, 'typescript')
        
        # Build prompt
        if step['action'] == 'create':
            prompt = f"""Create a new file: {file_path}

Step: {step['description']}

Ticket: {ticket['title']}
Description: {ticket.get('description', '')}

Project Context:
- Type: {project_context.get('type')}
- Tech Stack: {', '.join(project_context.get('tech_stack', []))}

Requirements:
{chr(10).join(ticket.get('acceptance_criteria', []))}

Generate complete, production-ready code.
Include:
- All necessary imports
- Proper TypeScript types
- Error handling
- Comments for complex logic
- Follow existing project patterns

Output ONLY the code, no explanations.
"""
        else:  # modify
            prompt = f"""Modify existing file: {file_path}

Step: {step['description']}

Ticket: {ticket['title']}
Description: {ticket.get('description', '')}

Existing Code:
{existing_code}

Modify the code to implement the required changes.
Preserve existing functionality.
Follow existing code style.

Output the COMPLETE modified file, no explanations.
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language=language,
                max_tokens=2000,
                temperature=0.2
            )
            
            if result and len(result) > 0:
                return result[0].strip()
                
        except Exception as e:
            logger.error(f"Failed to generate code for {file_path}: {e}")
            
        return None
        
    async def _generate_tests(
        self,
        ticket: Dict,
        generated_files: List[Dict],
        project_context: Dict,
        repo_path: str
    ) -> List[Dict]:
        """Generate tests for generated code"""
        
        test_files = []
        
        for file_info in generated_files:
            # Determine test file path
            file_path = file_info['path']
            
            # Skip if already a test file
            if '.test.' in file_path or '.spec.' in file_path:
                continue
                
            # Create test file path
            base, ext = os.path.splitext(file_path)
            test_path = f"{base}.test{ext}"
            
            # Generate test code
            test_code = await self._generate_test_code(
                file_path=file_path,
                code=file_info['code'],
                ticket=ticket,
                project_context=project_context
            )
            
            if test_code:
                # Write test file
                full_test_path = os.path.join(repo_path, test_path)
                os.makedirs(os.path.dirname(full_test_path), exist_ok=True)
                with open(full_test_path, 'w') as f:
                    f.write(test_code)
                    
                test_files.append({
                    'path': test_path,
                    'code': test_code
                })
                
                logger.info(f"✅ Generated test: {test_path}")
                
        return test_files
        
    async def _generate_test_code(
        self,
        file_path: str,
        code: str,
        ticket: Dict,
        project_context: Dict
    ) -> Optional[str]:
        """Generate test code for a file"""
        
        prompt = f"""Generate tests for this code.

File: {file_path}

Code:
{code}

Ticket Requirements:
{chr(10).join(ticket.get('acceptance_criteria', []))}

Project Testing Framework: {project_context.get('test_framework', 'Jest')}

Generate comprehensive tests that:
- Test all acceptance criteria
- Cover edge cases
- Test error handling
- Follow project testing patterns

Output ONLY the test code, no explanations.
"""
        
        ext = os.path.splitext(file_path)[1]
        language_map = {
            '.tsx': 'typescript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.js': 'javascript',
            '.py': 'python'
        }
        language = language_map.get(ext, 'typescript')
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language=language,
                max_tokens=1500,
                temperature=0.2
            )
            
            if result and len(result) > 0:
                return result[0].strip()
                
        except Exception as e:
            logger.error(f"Failed to generate tests: {e}")
            
        return None
        
    async def _create_pr(
        self,
        ticket: Dict,
        generated_files: List[Dict],
        test_files: List[Dict],
        repo_path: str
    ) -> Optional[str]:
        """Create PR with generated code"""
        
        try:
            # Create branch
            branch_name = f"ai/{ticket['id']}-{ticket['title'][:30].replace(' ', '-').lower()}"
            
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=repo_path,
                check=True
            )
            
            # Stage all files
            all_files = generated_files + test_files
            for file_info in all_files:
                subprocess.run(
                    ['git', 'add', file_info['path']],
                    cwd=repo_path,
                    check=True
                )
                
            # Commit
            commit_message = f"""AI: {ticket['title']}

{ticket.get('description', '')[:200]}

Generated by AI Code Generation Agent

Files:
{chr(10).join('- ' + f['path'] for f in generated_files)}

Tests:
{chr(10).join('- ' + f['path'] for f in test_files)}

Ticket: {ticket['id']}
"""
            
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=repo_path,
                check=True
            )
            
            # Push
            subprocess.run(
                ['git', 'push', 'origin', branch_name],
                cwd=repo_path,
                check=True
            )
            
            # Create PR (using GitHub CLI if available)
            try:
                result = subprocess.run(
                    [
                        'gh', 'pr', 'create',
                        '--title', f"AI: {ticket['title']}",
                        '--body', ticket.get('description', ''),
                        '--label', 'ai-generated'
                    ],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                pr_url = result.stdout.strip()
                logger.info(f"✅ Created PR: {pr_url}")
                return pr_url
                
            except subprocess.CalledProcessError:
                logger.warning("GitHub CLI not available, PR not created")
                return f"Branch created: {branch_name}"
                
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None


# Global instance
_code_generation_agent = CodeGenerationAgent()


def get_code_generation_agent() -> CodeGenerationAgent:
    """Get global code generation agent"""
    return _code_generation_agent
