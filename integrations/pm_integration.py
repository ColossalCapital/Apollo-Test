"""
PM Integration Layer

Universal adapter for project management tools:
- Linear (local/default)
- Jira
- Asana
- GitHub Projects
- ClickUp
- Monday.com

Features:
- Bidirectional sync
- Ticket translation
- Mermaid diagram handling
- Conflict resolution
"""

import os
import logging
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PMAdapter(ABC):
    """Base class for PM tool adapters"""
    
    @abstractmethod
    async def get_all_tickets(self, project_id: str) -> List[Dict]:
        """Get all tickets from project"""
        pass
        
    @abstractmethod
    async def get_ticket(self, ticket_id: str) -> Dict:
        """Get single ticket"""
        pass
        
    @abstractmethod
    async def create_ticket(self, ticket: Dict) -> str:
        """Create ticket, return ID"""
        pass
        
    @abstractmethod
    async def update_ticket(self, ticket_id: str, updates: Dict):
        """Update ticket"""
        pass


class LinearAdapter(PMAdapter):
    """Linear.app integration (local default)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LINEAR_API_KEY")
        self.endpoint = "https://api.linear.app/graphql"
        
    async def get_all_tickets(self, project_id: str) -> List[Dict]:
        """Get all issues from Linear project"""
        query = """
        query($projectId: String!) {
          project(id: $projectId) {
            issues {
              nodes {
                id
                title
                description
                state { name }
                assignee { name email }
                priority
                estimate
                labels { nodes { name } }
                createdAt
                updatedAt
              }
            }
          }
        }
        """
        
        result = await self._graphql(query, {"projectId": project_id})
        return result['data']['project']['issues']['nodes']
        
    async def get_ticket(self, ticket_id: str) -> Dict:
        """Get single Linear issue"""
        query = """
        query($issueId: String!) {
          issue(id: $issueId) {
            id
            title
            description
            state { name }
            assignee { name email }
            priority
            estimate
            labels { nodes { name } }
            createdAt
            updatedAt
          }
        }
        """
        
        result = await self._graphql(query, {"issueId": ticket_id})
        return result['data']['issue']
        
    async def create_ticket(self, ticket: Dict) -> str:
        """Create Linear issue"""
        mutation = """
        mutation($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            issue { id }
          }
        }
        """
        
        result = await self._graphql(mutation, {"input": ticket})
        return result['data']['issueCreate']['issue']['id']
        
    async def update_ticket(self, ticket_id: str, updates: Dict):
        """Update Linear issue"""
        mutation = """
        mutation($id: String!, $input: IssueUpdateInput!) {
          issueUpdate(id: $id, input: $input) {
            success
          }
        }
        """
        
        await self._graphql(mutation, {"id": ticket_id, "input": updates})
        
    async def _graphql(self, query: str, variables: Dict) -> Dict:
        """Execute GraphQL query"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json={"query": query, "variables": variables},
                headers={"Authorization": self.api_key}
            ) as resp:
                return await resp.json()


class JiraAdapter(PMAdapter):
    """Jira integration"""
    
    def __init__(self, api_key: Optional[str] = None, domain: Optional[str] = None):
        self.api_key = api_key or os.getenv("JIRA_API_KEY")
        self.domain = domain or os.getenv("JIRA_DOMAIN")
        self.endpoint = f"https://{self.domain}/rest/api/3"
        
    async def get_all_tickets(self, project_key: str) -> List[Dict]:
        """Get all issues from Jira project"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.endpoint}/search",
                params={"jql": f"project={project_key}"},
                headers=self._headers()
            ) as resp:
                result = await resp.json()
                return result.get('issues', [])
                
    async def get_ticket(self, ticket_id: str) -> Dict:
        """Get single Jira issue"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.endpoint}/issue/{ticket_id}",
                headers=self._headers()
            ) as resp:
                return await resp.json()
                
    async def create_ticket(self, ticket: Dict) -> str:
        """Create Jira issue"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/issue",
                json=ticket,
                headers=self._headers()
            ) as resp:
                result = await resp.json()
                return result['id']
                
    async def update_ticket(self, ticket_id: str, updates: Dict):
        """Update Jira issue"""
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.endpoint}/issue/{ticket_id}",
                json=updates,
                headers=self._headers()
            ) as resp:
                return await resp.json()
                
    def _headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }


class GitHubProjectsAdapter(PMAdapter):
    """GitHub Projects integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GITHUB_TOKEN")
        self.endpoint = "https://api.github.com/graphql"
        
    async def get_all_tickets(self, project_id: str) -> List[Dict]:
        """Get all issues from GitHub project"""
        query = """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      title
                      body
                      state
                      assignees(first: 1) {
                        nodes { login }
                      }
                      labels(first: 10) {
                        nodes { name }
                      }
                      createdAt
                      updatedAt
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        result = await self._graphql(query, {"projectId": project_id})
        return result['data']['node']['items']['nodes']
        
    async def get_ticket(self, ticket_id: str) -> Dict:
        """Get single GitHub issue"""
        query = """
        query($issueId: ID!) {
          node(id: $issueId) {
            ... on Issue {
              id
              title
              body
              state
              assignees(first: 1) {
                nodes { login }
              }
              labels(first: 10) {
                nodes { name }
              }
              createdAt
              updatedAt
            }
          }
        }
        """
        
        result = await self._graphql(query, {"issueId": ticket_id})
        return result['data']['node']
        
    async def create_ticket(self, ticket: Dict) -> str:
        """Create GitHub issue"""
        mutation = """
        mutation($input: CreateIssueInput!) {
          createIssue(input: $input) {
            issue { id }
          }
        }
        """
        
        result = await self._graphql(mutation, {"input": ticket})
        return result['data']['createIssue']['issue']['id']
        
    async def update_ticket(self, ticket_id: str, updates: Dict):
        """Update GitHub issue"""
        mutation = """
        mutation($id: ID!, $input: UpdateIssueInput!) {
          updateIssue(input: $input) {
            issue { id }
          }
        }
        """
        
        updates['id'] = ticket_id
        await self._graphql(mutation, {"input": updates})
        
    async def _graphql(self, query: str, variables: Dict) -> Dict:
        """Execute GraphQL query"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json={"query": query, "variables": variables},
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as resp:
                return await resp.json()


class PMIntegrationLayer:
    """
    Universal PM adapter
    
    Translates between Linear (local) and external PM tools
    """
    
    ADAPTERS = {
        "linear": LinearAdapter,
        "jira": JiraAdapter,
        "github": GitHubProjectsAdapter,
        # TODO: Add more adapters
        # "asana": AsanaAdapter,
        # "clickup": ClickUpAdapter,
        # "monday": MondayAdapter
    }
    
    def __init__(self, pm_tool: str):
        self.pm_tool = pm_tool
        adapter_class = self.ADAPTERS.get(pm_tool)
        
        if not adapter_class:
            raise ValueError(f"Unsupported PM tool: {pm_tool}")
            
        self.adapter = adapter_class()
        
    async def sync_tickets(self, project_id: str) -> List[Dict]:
        """Sync tickets from PM tool"""
        tickets = await self.adapter.get_all_tickets(project_id)
        
        # Normalize format
        normalized = [self.normalize_ticket(t, self.pm_tool) for t in tickets]
        
        return normalized
        
    def normalize_ticket(self, ticket: Dict, source: str) -> Dict:
        """Normalize ticket to standard format"""
        
        if source == "linear":
            return {
                "id": ticket['id'],
                "title": ticket['title'],
                "description": ticket.get('description', ''),
                "status": ticket['state']['name'],
                "assignee": ticket.get('assignee', {}).get('name'),
                "priority": ticket.get('priority', 0),
                "labels": [l['name'] for l in ticket.get('labels', {}).get('nodes', [])],
                "created_at": ticket['createdAt'],
                "updated_at": ticket['updatedAt']
            }
            
        elif source == "jira":
            return {
                "id": ticket['id'],
                "title": ticket['fields']['summary'],
                "description": ticket['fields'].get('description', ''),
                "status": ticket['fields']['status']['name'],
                "assignee": ticket['fields'].get('assignee', {}).get('displayName'),
                "priority": ticket['fields'].get('priority', {}).get('name'),
                "labels": ticket['fields'].get('labels', []),
                "created_at": ticket['fields']['created'],
                "updated_at": ticket['fields']['updated']
            }
            
        elif source == "github":
            content = ticket.get('content', {})
            return {
                "id": ticket['id'],
                "title": content.get('title', ''),
                "description": content.get('body', ''),
                "status": content.get('state', 'open'),
                "assignee": content.get('assignees', {}).get('nodes', [{}])[0].get('login'),
                "priority": 0,  # GitHub doesn't have priority
                "labels": [l['name'] for l in content.get('labels', {}).get('nodes', [])],
                "created_at": content.get('createdAt'),
                "updated_at": content.get('updatedAt')
            }
            
        return ticket
