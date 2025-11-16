"""
Jira API Client
Handles all Jira operations for PM integration
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JiraClient:
    """Jira API client using REST API"""
    
    def __init__(
        self,
        site_url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None
    ):
        """
        Initialize Jira client
        
        Args:
            site_url: Your Jira site URL (e.g., https://your-domain.atlassian.net)
            email: Your Atlassian account email
            api_token: API token from https://id.atlassian.com/manage-profile/security/api-tokens
        """
        self.site_url = site_url or os.getenv("JIRA_SITE_URL")
        self.email = email or os.getenv("JIRA_EMAIL")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN")
        
        self.base_url = f"{self.site_url}/rest/api/3"
        self.auth = (self.email, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_project(self, data: Dict) -> Dict:
        """
        Create a new project
        
        Args:
            data: {
                "key": "ATLAS",  # Project key (uppercase)
                "name": "Atlas Mobile App",
                "projectTypeKey": "software",  # or "business"
                "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-agility-kanban",  # Optional
                "description": "Atlas mobile application",  # Optional
                "leadAccountId": "account-id"
            }
        
        Returns:
            Created project data
        """
        url = f"{self.base_url}/project"
        
        # Remove projectTemplateKey if it's the default (not supported in free tier)
        if data.get("projectTemplateKey") == "com.pyxis.greenhopper.jira:gh-simplified-agility-kanban":
            data = data.copy()
            data.pop("projectTemplateKey", None)
        
        response = requests.post(
            url,
            json=data,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        
        project = response.json()
        
        # Fetch full project details (create response only has key and id)
        full_project = self.get_project(project["key"])
        logger.info(f"✅ Created Jira project: {full_project.get('name', project['key'])} ({project['key']})")
        
        return full_project
    
    def get_project(self, project_key: str) -> Dict:
        """Get project details by key"""
        url = f"{self.base_url}/project/{project_key}"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        url = f"{self.base_url}/project"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def create_issue(self, data: Dict) -> Dict:
        """
        Create a new issue
        
        Args:
            data: {
                "fields": {
                    "project": {"key": "ATLAS"},
                    "summary": "Add user authentication",
                    "description": "Implement JWT authentication",
                    "issuetype": {"name": "Story"},
                    "priority": {"name": "High"},
                    "labels": ["backend", "security"],
                    "assignee": {"accountId": "account-id"}
                }
            }
        
        Returns:
            Created issue data
        """
        url = f"{self.base_url}/issue"
        
        response = requests.post(
            url,
            json=data,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        
        issue = response.json()
        logger.info(f"✅ Created Jira issue: {issue['key']}")
        
        return issue
    
    def update_issue(self, issue_key: str, data: Dict) -> Dict:
        """
        Update an existing issue
        
        Args:
            issue_key: Issue key (e.g., "ATLAS-123")
            data: Fields to update
        
        Returns:
            Updated issue data
        """
        url = f"{self.base_url}/issue/{issue_key}"
        
        response = requests.put(
            url,
            json=data,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        
        logger.info(f"✅ Updated Jira issue: {issue_key}")
        
        # Fetch updated issue
        return self.get_issue(issue_key)
    
    def get_issue(self, issue_key: str) -> Dict:
        """Get issue by key"""
        url = f"{self.base_url}/issue/{issue_key}"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """
        Search issues using JQL
        
        Args:
            jql: Jira Query Language string
            max_results: Maximum number of results
        
        Examples:
            "project = ATLAS AND status = 'In Progress'"
            "assignee = currentUser() AND status != Done"
        
        Returns:
            List of issues
        """
        url = f"{self.base_url}/search"
        
        params = {
            "jql": jql,
            "maxResults": max_results
        }
        
        response = requests.get(
            url,
            params=params,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        
        data = response.json()
        issues = data.get("issues", [])
        logger.info(f"📋 Found {len(issues)} Jira issues")
        
        return issues
    
    def create_epic(self, project_key: str, name: str, description: str = "") -> Dict:
        """
        Create an epic
        
        Args:
            project_key: Project key (e.g., "ATLAS")
            name: Epic name
            description: Epic description
        
        Returns:
            Created epic data
        """
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": name,
                "description": description,
                "issuetype": {"name": "Epic"}
            }
        }
        
        return self.create_issue(data)
    
    def get_changes_since(self, since: datetime, project_key: Optional[str] = None) -> Dict:
        """
        Get all changes since a specific time
        Used for continuous monitoring
        
        Args:
            since: Datetime to check from
            project_key: Optional project filter
        
        Returns:
            {
                "issues_created": [...],
                "issues_updated": [...]
            }
        """
        since_str = since.strftime("%Y-%m-%d %H:%M")
        
        # JQL for created issues
        jql_created = f"created >= '{since_str}'"
        if project_key:
            jql_created += f" AND project = {project_key}"
        
        # JQL for updated issues
        jql_updated = f"updated >= '{since_str}' AND created < '{since_str}'"
        if project_key:
            jql_updated += f" AND project = {project_key}"
        
        created = self.search_issues(jql_created)
        updated = self.search_issues(jql_updated)
        
        return {
            "issues_created": created,
            "issues_updated": updated
        }
    
    def add_comment(self, issue_key: str, body: str) -> Dict:
        """Add a comment to an issue"""
        url = f"{self.base_url}/issue/{issue_key}/comment"
        
        data = {"body": body}
        
        response = requests.post(
            url,
            json=data,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        
        comment = response.json()
        logger.info(f"💬 Added comment to {issue_key}")
        
        return comment
    
    def get_current_user(self) -> Dict:
        """Get current user info"""
        url = f"{self.base_url}/myself"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = JiraClient(
        site_url="https://your-domain.atlassian.net",
        email="your-email@example.com",
        api_token="your-api-token"
    )
    
    # Get current user
    user = client.get_current_user()
    print(f"Logged in as: {user['displayName']}")
    
    # Create project
    project = client.create_project({
        "key": "ATLAS",
        "name": "Atlas Mobile App",
        "projectTypeKey": "software",
        "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-agility-kanban",
        "description": "Atlas mobile application",
        "leadAccountId": user["accountId"]
    })
    
    print(f"Created project: {project['name']}")
    
    # Create epic
    epic = client.create_epic(
        project_key="ATLAS",
        name="User Authentication",
        description="Implement complete user authentication system"
    )
    
    print(f"Created epic: {epic['key']}")
    
    # Create story
    story = client.create_issue({
        "fields": {
            "project": {"key": "ATLAS"},
            "summary": "Add login screen",
            "description": "Create login screen with email/password",
            "issuetype": {"name": "Story"},
            "priority": {"name": "High"},
            "parent": {"key": epic["key"]}
        }
    })
    
    print(f"Created story: {story['key']}")
