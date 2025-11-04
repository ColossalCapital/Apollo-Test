"""
Asana Connector Agent - Bidirectional Asana API Integration

Maintains the Rust-based Asana connector in AckwardRootsInc with
bidirectional sync capabilities.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class AsanaConnectorAgent(Layer1Agent):
    """Asana API connector with bidirectional sync"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/asana"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="asana_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Asana connector - bidirectional sync with Asana API",
            capabilities=[
                "project_sync",
                "task_sync",
                "portfolio_sync",
                "goal_sync",
                "webhook_handling",
                "bidirectional_sync"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Asana connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Asana',
                    'auth_guide': {
                        'type': 'OAuth 2.0 + Personal Access Token',
                        'endpoints': ['Asana REST API v1'],
                        'required': ['Personal Access Token', 'Workspace ID'],
                        'scopes': ['default']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Asana',
                    'sync_modes': {
                        'pull': 'Fetch tasks, projects, portfolios from Asana',
                        'push': 'Create/update tasks, projects in Asana',
                        'bidirectional': 'Real-time sync via webhooks',
                        'conflict_resolution': 'Last-write-wins with timestamps'
                    },
                    'entities': {
                        'tasks': 'Full CRUD with subtasks, dependencies, custom fields',
                        'projects': 'Full CRUD with sections, templates',
                        'portfolios': 'Full CRUD with goals, status updates',
                        'goals': 'Full CRUD with metrics, timelines',
                        'teams': 'Read-only team structure',
                        'users': 'Read-only user profiles',
                        'custom_fields': 'Full CRUD'
                    },
                    'webhooks': {
                        'task': 'Task created, updated, deleted',
                        'project': 'Project created, updated',
                        'story': 'Comment added',
                        'attachment': 'File attached'
                    },
                    'cross_functional': {
                        'marketing': 'Campaign management',
                        'sales': 'Deal tracking',
                        'operations': 'Process workflows',
                        'hr': 'Onboarding workflows'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'pm_tool_migration':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Asana',
                    'migration_support': {
                        'from_jira': {
                            'supported': True,
                            'mapping': {
                                'jira_issue': 'asana_task',
                                'jira_epic': 'asana_project',
                                'jira_sprint': 'asana_section',
                                'jira_component': 'asana_tag'
                            }
                        },
                        'from_linear': {
                            'supported': True,
                            'mapping': {
                                'linear_issue': 'asana_task',
                                'linear_project': 'asana_project',
                                'linear_cycle': 'asana_milestone',
                                'linear_label': 'asana_tag'
                            }
                        },
                        'bidirectional_sync': True,
                        'conflict_resolution': 'configurable'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Asana',
                    'message': 'Asana connector for cross-functional project management'
                },
                metadata={'agent': self.metadata.name}
            )
