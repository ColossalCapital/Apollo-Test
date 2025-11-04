"""
GitHub Connector Agent - GitHub-specific API guidance and support
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class GitHubConnectorAgent(Layer1Agent):
    """GitHub platform-specific connector for repository management"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="github_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="GitHub connector maintenance - keeps Rust connector up-to-date",
            capabilities=["github_api", "repository_management", "pull_requests", "issues", "actions"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process GitHub-specific queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'GitHub',
                    'auth_guide': {
                        'type': 'Personal Access Token or GitHub App',
                        'tokens': ['Classic PAT', 'Fine-grained PAT', 'GitHub App JWT'],
                        'header': 'Authorization: Bearer ghp_...'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'repositories':
            return AgentResult(
                success=True,
                data={
                    'platform': 'GitHub',
                    'repo_guide': {
                        'list': 'GET /user/repos',
                        'get': 'GET /repos/{owner}/{repo}',
                        'create': 'POST /user/repos',
                        'webhooks': 'POST /repos/{owner}/{repo}/hooks'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'GitHub',
                    'message': 'I can help with GitHub API, repository management, and CI/CD integration.'
                },
                metadata={'agent': self.metadata.name}
            )
