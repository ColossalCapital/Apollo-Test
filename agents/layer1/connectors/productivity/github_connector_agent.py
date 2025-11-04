"""
GitHub Connector Agent - GitHub-specific API guidance and support
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent


class GitHubConnectorAgent(BaseAgent):
    """GitHub platform-specific connector for repository management"""
    
    def __init__(self):
        super().__init__(
            name="GitHub Connector",
            description="GitHub API, repository management, and CI/CD integration",
            capabilities=["GitHub API", "Repository Management", "Pull Requests", "Issues", "Actions", "Webhooks"]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitHub-specific queries"""
        query_type = data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return {
                'status': 'success',
                'platform': 'GitHub',
                'auth_guide': {
                    'type': 'Personal Access Token or GitHub App',
                    'tokens': ['Classic PAT', 'Fine-grained PAT', 'GitHub App JWT'],
                    'header': 'Authorization: Bearer ghp_...'
                }
            }
        elif query_type == 'repositories':
            return {
                'status': 'success',
                'platform': 'GitHub',
                'repo_guide': {
                    'list': 'GET /user/repos',
                    'get': 'GET /repos/{owner}/{repo}',
                    'create': 'POST /user/repos',
                    'webhooks': 'POST /repos/{owner}/{repo}/hooks'
                }
            }
        else:
            return {
                'status': 'success',
                'platform': 'GitHub',
                'message': 'I can help with GitHub API, repository management, and CI/CD integration.'
            }
