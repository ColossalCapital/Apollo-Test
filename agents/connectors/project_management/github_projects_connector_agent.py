"""
GitHub Projects Connector Agent - Bidirectional GitHub Projects API Integration

Maintains the Rust-based GitHub Projects connector in AckwardRootsInc with
bidirectional sync capabilities.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class GitHubProjectsConnectorAgent(Layer1Agent):
    """GitHub Projects API connector with bidirectional sync"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/github-projects"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="github_projects_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="GitHub Projects connector - bidirectional sync with GitHub Projects API",
            capabilities=[
                "project_sync",
                "issue_sync",
                "pr_sync",
                "milestone_sync",
                "webhook_handling",
                "bidirectional_sync"
            ],
            dependencies=["github_connector"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process GitHub Projects connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'GitHub Projects',
                    'auth_guide': {
                        'type': 'Personal Access Token + GitHub App',
                        'endpoints': ['GitHub GraphQL API v4', 'GitHub REST API v3'],
                        'required': ['Personal Access Token', 'Repo access'],
                        'scopes': ['repo', 'project', 'read:org', 'write:org']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'GitHub Projects',
                    'sync_modes': {
                        'pull': 'Fetch issues, PRs, projects from GitHub',
                        'push': 'Create/update issues, PRs in GitHub',
                        'bidirectional': 'Real-time sync via webhooks',
                        'conflict_resolution': 'GitHub-first (canonical source)'
                    },
                    'entities': {
                        'issues': 'Full CRUD with labels, assignees, milestones',
                        'pull_requests': 'Full CRUD with reviews, checks',
                        'projects': 'Full CRUD with columns, cards',
                        'milestones': 'Full CRUD with due dates',
                        'labels': 'Full CRUD',
                        'repositories': 'Read-only repo structure'
                    },
                    'webhooks': {
                        'issues': 'Issue created, updated, closed',
                        'pull_request': 'PR opened, merged, closed',
                        'project_card': 'Card moved, created, deleted',
                        'milestone': 'Milestone created, updated'
                    },
                    'native_integration': {
                        'issues_to_prs': 'Automatic linking',
                        'commits_to_issues': 'Closes #123 syntax',
                        'ci_cd': 'GitHub Actions integration'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'pm_tool_migration':
            return AgentResult(
                success=True,
                data={
                    'platform': 'GitHub Projects',
                    'migration_support': {
                        'from_jira': {
                            'supported': True,
                            'mapping': {
                                'jira_issue': 'github_issue',
                                'jira_epic': 'github_milestone',
                                'jira_sprint': 'github_project_column',
                                'jira_component': 'github_label'
                            }
                        },
                        'from_linear': {
                            'supported': True,
                            'mapping': {
                                'linear_issue': 'github_issue',
                                'linear_project': 'github_milestone',
                                'linear_cycle': 'github_project',
                                'linear_label': 'github_label'
                            }
                        },
                        'bidirectional_sync': True,
                        'conflict_resolution': 'github_canonical'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'GitHub Projects',
                    'message': 'GitHub Projects connector for developer-native project management'
                },
                metadata={'agent': self.metadata.name}
            )
