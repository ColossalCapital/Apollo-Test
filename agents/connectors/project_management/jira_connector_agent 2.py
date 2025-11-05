"""
Jira Connector Agent - Bidirectional Jira API Integration

Maintains the Rust-based Jira connector in AckwardRootsInc with
bidirectional sync capabilities.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class JiraConnectorAgent(Layer1Agent):
    """Jira API connector with bidirectional sync"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/jira"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="jira_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Jira connector maintenance - bidirectional sync with Jira API",
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
        """Process Jira connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Jira',
                    'auth_guide': {
                        'type': 'OAuth 2.0 + API Token',
                        'endpoints': ['Jira REST API v3'],
                        'required': ['API Token', 'Site URL', 'Email'],
                        'scopes': ['read:jira-work', 'write:jira-work', 'manage:jira-project']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Jira',
                    'sync_modes': {
                        'pull': 'Fetch issues, projects, comments from Jira',
                        'push': 'Create/update issues, projects in Jira',
                        'bidirectional': 'Real-time sync via webhooks',
                        'conflict_resolution': 'Last-write-wins with merge strategies'
                    },
                    'entities': {
                        'issues': 'Full CRUD with status, assignee, labels, custom fields',
                        'epics': 'Full CRUD with epic links',
                        'sprints': 'Full CRUD with sprint planning',
                        'projects': 'Full CRUD with project settings',
                        'comments': 'Full CRUD with mentions, attachments',
                        'boards': 'Read-only board structure',
                        'users': 'Read-only user profiles'
                    },
                    'webhooks': {
                        'jira:issue_created': 'New issue notification',
                        'jira:issue_updated': 'Issue change notification',
                        'comment_created': 'New comment notification',
                        'worklog_updated': 'Time tracking notification'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'linear_migration':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Jira',
                    'linear_migration': {
                        'supported': True,
                        'mapping': {
                            'linear_issue': 'jira_issue',
                            'linear_project': 'jira_epic',
                            'linear_cycle': 'jira_sprint',
                            'linear_label': 'jira_component',
                            'linear_state': 'jira_status'
                        },
                        'bidirectional_sync': True,
                        'conflict_resolution': 'Configurable (jira_wins, linear_wins, manual)'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Jira',
                    'message': 'Jira connector for bidirectional project management sync'
                },
                metadata={'agent': self.metadata.name}
            )
