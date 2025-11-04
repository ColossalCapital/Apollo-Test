"""
ClickUp Connector Agent - Bidirectional ClickUp API Integration

Maintains the Rust-based ClickUp connector in AckwardRootsInc with
bidirectional sync capabilities.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class ClickUpConnectorAgent(Layer1Agent):
    """ClickUp API connector with bidirectional sync"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/clickup"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="clickup_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="ClickUp connector - bidirectional sync with ClickUp API",
            capabilities=[
                "project_sync",
                "task_sync",
                "doc_sync",
                "goal_sync",
                "time_tracking_sync",
                "webhook_handling",
                "bidirectional_sync"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process ClickUp connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'ClickUp',
                    'auth_guide': {
                        'type': 'OAuth 2.0 + API Token',
                        'endpoints': ['ClickUp API v2'],
                        'required': ['API Token', 'Workspace ID'],
                        'scopes': ['read', 'write', 'admin']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'ClickUp',
                    'sync_modes': {
                        'pull': 'Fetch tasks, docs, goals, time entries from ClickUp',
                        'push': 'Create/update tasks, docs, goals in ClickUp',
                        'bidirectional': 'Real-time sync via webhooks',
                        'conflict_resolution': 'Last-write-wins with version control'
                    },
                    'entities': {
                        'tasks': 'Full CRUD with subtasks, checklists, custom fields',
                        'lists': 'Full CRUD with statuses, templates',
                        'folders': 'Full CRUD with hierarchy',
                        'spaces': 'Full CRUD with multiple workspaces',
                        'docs': 'Full CRUD with collaborative editing',
                        'goals': 'Full CRUD with targets, metrics',
                        'time_tracking': 'Full CRUD with time entries',
                        'dashboards': 'Read-only dashboard data',
                        'automations': 'Read-only automation rules'
                    },
                    'webhooks': {
                        'taskCreated': 'New task notification',
                        'taskUpdated': 'Task change notification',
                        'taskDeleted': 'Task deletion notification',
                        'taskCommentPosted': 'New comment notification',
                        'taskTimeTracked': 'Time entry notification'
                    },
                    'all_in_one': {
                        'docs': 'Built-in documentation',
                        'goals': 'OKR tracking',
                        'time_tracking': 'Native time tracking',
                        'dashboards': 'Custom reporting',
                        'automations': 'Workflow automation'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'pm_tool_migration':
            return AgentResult(
                success=True,
                data={
                    'platform': 'ClickUp',
                    'migration_support': {
                        'from_jira': {
                            'supported': True,
                            'mapping': {
                                'jira_issue': 'clickup_task',
                                'jira_epic': 'clickup_folder',
                                'jira_sprint': 'clickup_list',
                                'jira_component': 'clickup_tag',
                                'jira_status': 'clickup_status'
                            }
                        },
                        'from_linear': {
                            'supported': True,
                            'mapping': {
                                'linear_issue': 'clickup_task',
                                'linear_project': 'clickup_folder',
                                'linear_cycle': 'clickup_list',
                                'linear_label': 'clickup_tag'
                            }
                        },
                        'from_asana': {
                            'supported': True,
                            'mapping': {
                                'asana_task': 'clickup_task',
                                'asana_project': 'clickup_list',
                                'asana_portfolio': 'clickup_space',
                                'asana_section': 'clickup_status'
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
                    'platform': 'ClickUp',
                    'message': 'ClickUp connector for all-in-one project management'
                },
                metadata={'agent': self.metadata.name}
            )
