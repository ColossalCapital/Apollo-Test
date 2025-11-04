"""
GitHub Issues API Client
Handles all GitHub Issues operations for PM integration
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub Issues API client"""
    
    def __init__(self, token: Optional[str] = None, owner: str = None, repo: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def set_repository(self, owner: str, repo: str):
        """Set the repository to work with"""
        self.owner = owner
        self.repo = repo
    
    def get_user(self) -> Dict:
        """Get authenticated user info"""
        url = f"{self.base_url}/user"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_issue(self, repo: Optional[str] = None, data: Optional[Dict] = None) -> Dict:
        """
        Create a new issue
        
        Args:
            repo: Repository name (optional, uses self.repo if not provided)
            data: {
                "title": "Issue title",
                "body": "Issue description",
                "labels": ["bug", "priority: high"],
                "assignees": ["username"],
                "milestone": 1
            }
        
        Returns:
            Created issue data with number, url, etc.
        """
        # Use provided repo or fall back to instance repo
        target_repo = repo or self.repo
        if not target_repo:
            raise ValueError("Repository name must be provided")
        
        url = f"{self.base_url}/repos/{self.owner}/{target_repo}/issues"
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        
        issue = response.json()
        logger.info(f"✅ Created GitHub issue #{issue['number']}: {issue['title']}")
        
        return issue
    
    def update_issue(self, issue_number: int, data: Dict) -> Dict:
        """
        Update an existing issue
        
        Args:
            issue_number: Issue number
            data: Fields to update (title, body, state, labels, assignees, milestone)
        
        Returns:
            Updated issue data
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        
        response = requests.patch(url, json=data, headers=self.headers)
        response.raise_for_status()
        
        issue = response.json()
        logger.info(f"✅ Updated GitHub issue #{issue['number']}")
        
        return issue
    
    def get_issue(self, issue_number: int) -> Dict:
        """Get issue by number"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def list_issues(
        self, 
        state: str = "open",
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        List issues with filters
        
        Args:
            state: "open", "closed", or "all"
            labels: Filter by labels
            assignee: Filter by assignee
            since: Only issues updated after this date
        
        Returns:
            List of issues
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        
        params = {"state": state}
        if labels:
            params["labels"] = ",".join(labels)
        if assignee:
            params["assignee"] = assignee
        if since:
            params["since"] = since.isoformat()
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        issues = response.json()
        logger.info(f"📋 Fetched {len(issues)} GitHub issues")
        
        return issues
    
    def close_issue(self, issue_number: int) -> Dict:
        """Close an issue"""
        return self.update_issue(issue_number, {"state": "closed"})
    
    def reopen_issue(self, issue_number: int) -> Dict:
        """Reopen a closed issue"""
        return self.update_issue(issue_number, {"state": "open"})
    
    def add_labels(self, issue_number: int, labels: List[str]) -> Dict:
        """Add labels to an issue"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/labels"
        
        response = requests.post(url, json={"labels": labels}, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def remove_label(self, issue_number: int, label: str) -> None:
        """Remove a label from an issue"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/labels/{label}"
        
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
    
    def add_assignees(self, issue_number: int, assignees: List[str]) -> Dict:
        """Add assignees to an issue"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/assignees"
        
        response = requests.post(url, json={"assignees": assignees}, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def create_comment(self, issue_number: int, body: str) -> Dict:
        """Add a comment to an issue"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        
        response = requests.post(url, json={"body": body}, headers=self.headers)
        response.raise_for_status()
        
        comment = response.json()
        logger.info(f"💬 Added comment to issue #{issue_number}")
        
        return comment
    
    def list_milestones(self, state: str = "open") -> List[Dict]:
        """List milestones (used as epics)"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/milestones"
        
        response = requests.get(url, params={"state": state}, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def create_milestone(self, title: str, description: str = "", due_on: Optional[str] = None) -> Dict:
        """Create a milestone (epic)"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/milestones"
        
        data = {"title": title, "description": description}
        if due_on:
            data["due_on"] = due_on
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        
        milestone = response.json()
        logger.info(f"🎯 Created milestone: {milestone['title']}")
        
        return milestone
    
    def get_changes_since(self, since: datetime) -> Dict:
        """
        Get all changes since a specific time
        Used for continuous monitoring
        
        Returns:
            {
                "issues_updated": [...],
                "issues_closed": [...],
                "new_issues": [...]
            }
        """
        # Get all issues updated since timestamp
        all_issues = self.list_issues(state="all", since=since)
        
        new_issues = []
        updated_issues = []
        closed_issues = []
        
        for issue in all_issues:
            created_at = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(issue["updated_at"].replace("Z", "+00:00"))
            
            if created_at > since:
                new_issues.append(issue)
            elif updated_at > since:
                if issue["state"] == "closed":
                    closed_issues.append(issue)
                else:
                    updated_issues.append(issue)
        
        return {
            "new_issues": new_issues,
            "updated_issues": updated_issues,
            "closed_issues": closed_issues
        }


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = GitHubClient(owner="your-org", repo="your-repo")
    
    # Create issue
    issue = client.create_issue({
        "title": "Add user authentication",
        "body": "Implement JWT authentication for API endpoints",
        "labels": ["backend", "security", "priority: high"],
        "assignees": ["backend-specialist"]
    })
    
    print(f"Created issue #{issue['number']}: {issue['html_url']}")
    
    # List open issues
    issues = client.list_issues(state="open", labels=["backend"])
    print(f"Found {len(issues)} open backend issues")
    
    # Monitor changes
    since = datetime.now()
    # ... wait some time ...
    changes = client.get_changes_since(since)
    print(f"Changes: {len(changes['new_issues'])} new, {len(changes['updated_issues'])} updated")
