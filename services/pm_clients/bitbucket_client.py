"""
Bitbucket API Client
Handles all Bitbucket operations for PM integration
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BitbucketClient:
    """Bitbucket API client using REST API 2.0"""
    
    def __init__(
        self,
        workspace: Optional[str] = None,
        api_token: Optional[str] = None,
        email: Optional[str] = None
    ):
        """
        Initialize Bitbucket client
        
        Args:
            workspace: Bitbucket workspace name
            api_token: Atlassian API token (created at id.atlassian.com)
            email: Your email address (used for authentication)
        
        Note: As of Sept 2025, Bitbucket uses Atlassian API tokens with Basic auth
        """
        self.workspace = workspace or os.getenv("BITBUCKET_WORKSPACE")
        self.api_token = api_token or os.getenv("BITBUCKET_API_TOKEN")
        self.email = email or os.getenv("BITBUCKET_EMAIL") or os.getenv("JIRA_EMAIL")
        
        self.base_url = "https://api.bitbucket.org/2.0"
        
        # Use Basic auth with email + token
        self.auth = (self.email, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_repository(self, data: Dict) -> Dict:
        """
        Create a new repository
        
        Args:
            data: {
                "name": "Atlas",
                "description": "Atlas mobile application",
                "is_private": True,
                "scm": "git",
                "project": {"key": "CC"}  # Optional project
            }
        
        Returns:
            Created repository data
        """
        url = f"{self.base_url}/repositories/{self.workspace}/{data['name']}"
        
        response = requests.post(
            url,
            json=data,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        
        repo = response.json()
        logger.info(f"✅ Created Bitbucket repo: {repo['name']}")
        
        return repo
    
    def get_repositories(self) -> List[Dict]:
        """Get all repositories in workspace"""
        url = f"{self.base_url}/repositories/{self.workspace}"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get("values", [])
    
    def create_issue(self, repo_slug: str, data: Dict) -> Dict:
        """
        Create a new issue
        
        Args:
            repo_slug: Repository slug (name)
            data: {
                "title": "Add user authentication",
                "content": {"raw": "Implement JWT authentication"},
                "kind": "task",  # or "bug", "enhancement"
                "priority": "major",  # trivial, minor, major, critical, blocker
                "assignee": {"username": "username"}
            }
        
        Returns:
            Created issue data
        """
        url = f"{self.base_url}/repositories/{self.workspace}/{repo_slug}/issues"
        
        response = requests.post(
            url,
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        
        issue = response.json()
        logger.info(f"✅ Created Bitbucket issue #{issue['id']}: {issue['title']}")
        
        return issue
    
    def update_issue(self, repo_slug: str, issue_id: int, data: Dict) -> Dict:
        """
        Update an existing issue
        
        Args:
            repo_slug: Repository slug
            issue_id: Issue ID
            data: Fields to update
        
        Returns:
            Updated issue data
        """
        url = f"{self.base_url}/repositories/{self.workspace}/{repo_slug}/issues/{issue_id}"
        
        response = requests.put(
            url,
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        
        issue = response.json()
        logger.info(f"✅ Updated Bitbucket issue #{issue['id']}")
        
        return issue
    
    def get_issue(self, repo_slug: str, issue_id: int) -> Dict:
        """Get issue by ID"""
        url = f"{self.base_url}/repositories/{self.workspace}/{repo_slug}/issues/{issue_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def list_issues(
        self,
        repo_slug: str,
        state: Optional[str] = None,
        kind: Optional[str] = None
    ) -> List[Dict]:
        """
        List issues with filters
        
        Args:
            repo_slug: Repository slug
            state: "new", "open", "resolved", "on hold", "invalid", "duplicate", "wontfix", "closed"
            kind: "bug", "enhancement", "proposal", "task"
        
        Returns:
            List of issues
        """
        url = f"{self.base_url}/repositories/{self.workspace}/{repo_slug}/issues"
        
        params = {}
        if state:
            params["state"] = state
        if kind:
            params["kind"] = kind
        
        response = requests.get(
            url,
            params=params,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        
        data = response.json()
        issues = data.get("values", [])
        logger.info(f"📋 Fetched {len(issues)} Bitbucket issues")
        
        return issues
    
    def create_project(self, data: Dict) -> Dict:
        """
        Create a new project
        
        Args:
            data: {
                "name": "Colossal Capital",
                "key": "CC",
                "description": "Main project for all repos",
                "is_private": True
            }
        
        Returns:
            Created project data
        """
        url = f"{self.base_url}/workspaces/{self.workspace}/projects"
        
        response = requests.post(
            url,
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        
        project = response.json()
        logger.info(f"✅ Created Bitbucket project: {project['name']} ({project['key']})")
        
        return project
    
    def get_projects(self) -> List[Dict]:
        """Get all projects in workspace"""
        url = f"{self.base_url}/workspaces/{self.workspace}/projects"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get("values", [])
    
    def add_comment(self, repo_slug: str, issue_id: int, content: str) -> Dict:
        """Add a comment to an issue"""
        url = f"{self.base_url}/repositories/{self.workspace}/{repo_slug}/issues/{issue_id}/comments"
        
        data = {"content": {"raw": content}}
        
        response = requests.post(
            url,
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        
        comment = response.json()
        logger.info(f"💬 Added comment to issue #{issue_id}")
        
        return comment
    
    def get_changes_since(self, repo_slug: str, since: datetime) -> Dict:
        """
        Get all changes since a specific time
        Used for continuous monitoring
        
        Returns:
            {
                "issues_created": [...],
                "issues_updated": [...]
            }
        """
        # Get all issues
        all_issues = self.list_issues(repo_slug)
        
        created = []
        updated = []
        
        for issue in all_issues:
            created_at = datetime.fromisoformat(issue["created_on"].replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(issue["updated_on"].replace("Z", "+00:00"))
            
            if created_at > since:
                created.append(issue)
            elif updated_at > since:
                updated.append(issue)
        
        return {
            "issues_created": created,
            "issues_updated": updated
        }


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = BitbucketClient(
        workspace="colossalcapital",
        username="your-username",
        app_password="your-app-password"
    )
    
    # Create project
    project = client.create_project({
        "name": "Colossal Capital",
        "key": "CC",
        "description": "Main project for all repos",
        "is_private": True
    })
    
    print(f"Created project: {project['name']}")
    
    # Create repository
    repo = client.create_repository({
        "name": "Atlas",
        "description": "Atlas mobile application",
        "is_private": True,
        "scm": "git",
        "project": {"key": "CC"}
    })
    
    print(f"Created repo: {repo['name']}")
    
    # Create issue
    issue = client.create_issue("Atlas", {
        "title": "Add user authentication",
        "content": {"raw": "Implement JWT authentication for API endpoints"},
        "kind": "task",
        "priority": "major"
    })
    
    print(f"Created issue #{issue['id']}: {issue['title']}")
