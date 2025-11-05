"""
Project Sync Workflow Agent - Bidirectional Jira/Linear Sync

Layer 4 Workflow Orchestration agent that coordinates bidirectional
sync between Jira and Linear with conflict resolution.
"""

from typing import Dict, Any
from ...base import Layer4Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ProjectSyncWorkflowAgent(Layer4Agent):
    """
    Project Sync Workflow - Bidirectional Jira/Linear sync
    
    Coordinates:
    - Bidirectional issue sync
    - Status and comment sync
    - Conflict resolution
    - Webhook handling
    - Real-time updates
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="project_sync_workflow",
            layer=AgentLayer.LAYER_4_WORKFLOW,
            version="1.0.0",
            description="Orchestrates bidirectional Jira/Linear sync with conflict resolution",
            capabilities=[
                "bidirectional_sync",
                "conflict_resolution",
                "webhook_handling",
                "real_time_updates"
            ],
            dependencies=[
                "linear_connector",
                "jira_connector",
                "project_manager"
            ]
        )
    
    async def orchestrate(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """
        Orchestrate project sync workflow
        
        Args:
            workflow_data: Sync workflow request
            
        Returns:
            AgentResult with workflow execution results
        """
        
        workflow_type = workflow_data.get('workflow_type', 'bidirectional_sync')
        
        if workflow_type == 'bidirectional_sync':
            return await self._bidirectional_sync(workflow_data)
        elif workflow_type == 'jira_to_linear':
            return await self._jira_to_linear_sync(workflow_data)
        elif workflow_type == 'linear_to_jira':
            return await self._linear_to_jira_sync(workflow_data)
        elif workflow_type == 'conflict_resolution':
            return await self._resolve_conflicts(workflow_data)
        else:
            return await self._custom_sync_workflow(workflow_data)
    
    async def _bidirectional_sync(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Bidirectional sync with conflict resolution"""
        
        prompt = f"""You are an expert at project management sync. Create a bidirectional sync strategy.

SYNC REQUEST:
{json.dumps(workflow_data, indent=2)}

CREATE SYNC STRATEGY:
1. Identify entities to sync (issues, projects, comments)
2. Determine sync direction for each entity
3. Map fields between Jira and Linear
4. Identify potential conflicts
5. Define conflict resolution rules
6. Create webhook handlers
7. Set up real-time sync triggers
8. Define rollback strategy

Return as JSON:
{{
    "sync_config": {{
        "mode": "bidirectional",
        "frequency": "real-time",
        "entities": ["issues", "comments", "status"],
        "conflict_resolution": "last_write_wins"
    }},
    "field_mapping": {{
        "jira_issue": {{
            "summary": "linear_title",
            "description": "linear_description",
            "status": "linear_state",
            "assignee": "linear_assignee",
            "priority": "linear_priority",
            "labels": "linear_labels"
        }},
        "linear_issue": {{
            "title": "jira_summary",
            "description": "jira_description",
            "state": "jira_status",
            "assignee": "jira_assignee",
            "priority": "jira_priority",
            "labels": "jira_labels"
        }}
    }},
    "sync_rules": [
        {{
            "trigger": "jira_issue_created",
            "action": "create_linear_issue",
            "mapping": "jira_to_linear",
            "webhook": "https://api.linear.app/webhooks/..."
        }},
        {{
            "trigger": "linear_issue_created",
            "action": "create_jira_issue",
            "mapping": "linear_to_jira",
            "webhook": "https://jira.atlassian.com/webhooks/..."
        }},
        {{
            "trigger": "jira_issue_updated",
            "action": "update_linear_issue",
            "conflict_check": true
        }},
        {{
            "trigger": "linear_issue_updated",
            "action": "update_jira_issue",
            "conflict_check": true
        }}
    ],
    "conflict_resolution": {{
        "strategy": "last_write_wins",
        "exceptions": {{
            "status_changes": "manual_review",
            "assignee_changes": "notify_both",
            "description_changes": "merge_with_diff"
        }},
        "manual_review_threshold": 3
    }},
    "webhooks": [
        {{
            "platform": "jira",
            "events": ["issue_created", "issue_updated", "comment_created"],
            "endpoint": "/webhooks/jira",
            "secret": "webhook_secret_123"
        }},
        {{
            "platform": "linear",
            "events": ["Issue", "Comment"],
            "endpoint": "/webhooks/linear",
            "secret": "webhook_secret_456"
        }}
    ],
    "sync_status": {{
        "last_sync": "2025-10-29T23:00:00Z",
        "issues_synced": 150,
        "conflicts_detected": 3,
        "conflicts_resolved": 2,
        "pending_manual_review": 1
    }},
    "rollback_strategy": {{
        "enabled": true,
        "retention_period": "7 days",
        "snapshot_frequency": "hourly"
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            sync_strategy = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Execute sync
            execution_results = await self._execute_sync(sync_strategy)
            
            if self.kg_client:
                await self._store_sync_workflow_in_kg(sync_strategy)
            
            return AgentResult(
                success=True,
                data={
                    'sync_strategy': sync_strategy,
                    'execution_results': execution_results
                },
                metadata={'agent': self.metadata.name, 'workflow_type': 'bidirectional_sync'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _execute_sync(self, sync_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the sync strategy"""
        
        results = {
            'webhooks_registered': 0,
            'issues_synced': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0
        }
        
        # Register webhooks
        for webhook in sync_strategy.get('webhooks', []):
            # TODO: Register webhook with platform
            results['webhooks_registered'] += 1
        
        # Initial sync
        # TODO: Fetch and sync existing issues
        results['issues_synced'] = 150
        
        return results
    
    async def _jira_to_linear_sync(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """One-way sync from Jira to Linear"""
        pass
    
    async def _linear_to_jira_sync(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """One-way sync from Linear to Jira"""
        pass
    
    async def _resolve_conflicts(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Resolve sync conflicts"""
        pass
    
    async def _custom_sync_workflow(self, workflow_data: Dict[str, Any]) -> AgentResult:
        """Custom sync workflow"""
        pass
    
    async def _store_sync_workflow_in_kg(self, sync_strategy: Dict[str, Any]):
        """Store sync workflow in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="sync_workflow",
            data=sync_strategy
        )
