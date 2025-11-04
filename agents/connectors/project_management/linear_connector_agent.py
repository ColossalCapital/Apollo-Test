"""
Linear Connector Agent - Bidirectional Linear API Integration

Maintains the Rust-based Linear connector in AckwardRootsInc with
bidirectional sync capabilities.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class LinearConnectorAgent(Layer1Agent):
    """Linear API connector with bidirectional sync"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/linear"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="linear_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Linear connector maintenance - bidirectional sync with Linear API",
            capabilities=[
                "project_sync",
                "issue_sync",
                "comment_sync",
                "status_updates",
                "webhook_handling",
                "bidirectional_sync"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Linear connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Linear',
                    'auth_guide': {
                        'type': 'OAuth 2.0 + API Key',
                        'endpoints': ['Linear GraphQL API'],
                        'required': ['API Key', 'Workspace ID'],
                        'scopes': ['read', 'write', 'admin']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Linear',
                    'sync_modes': {
                        'pull': 'Fetch issues, projects, comments from Linear',
                        'push': 'Create/update issues, projects in Linear',
                        'bidirectional': 'Real-time sync via webhooks',
                        'conflict_resolution': 'Last-write-wins with merge strategies'
                    },
                    'entities': {
                        'issues': 'Full CRUD with status, assignee, labels',
                        'projects': 'Full CRUD with milestones, roadmaps',
                        'comments': 'Full CRUD with mentions, reactions',
                        'teams': 'Read-only team structure',
                        'users': 'Read-only user profiles'
                    },
                    'webhooks': {
                        'issue_created': 'New issue notification',
                        'issue_updated': 'Issue change notification',
                        'comment_created': 'New comment notification',
                        'status_changed': 'Status update notification'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'jira_migration':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Linear',
                    'jira_migration': {
                        'supported': True,
                        'mapping': {
                            'jira_issue': 'linear_issue',
                            'jira_epic': 'linear_project',
                            'jira_sprint': 'linear_cycle',
                            'jira_component': 'linear_label',
                            'jira_status': 'linear_state'
                        },
                        'bidirectional_sync': True,
                        'conflict_resolution': 'Configurable (linear_wins, jira_wins, manual)'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Linear',
                    'message': 'Linear connector for bidirectional project management sync'
                },
                metadata={'agent': self.metadata.name}
            )
