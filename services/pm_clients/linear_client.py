"""
Linear API Client
Handles all Linear operations for PM integration
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LinearClient:
    """Linear API client using GraphQL"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LINEAR_API_KEY")
        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(self.base_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        if "errors" in data:
            raise Exception(f"Linear API error: {data['errors']}")
        
        return data["data"]
    
    def get_viewer(self) -> Dict:
        """Get current user info"""
        query = """
        query {
            viewer {
                id
                name
                email
                displayName
            }
        }
        """
        result = self._query(query)
        return result["viewer"]
    
    def get_teams(self) -> List[Dict]:
        """Get all teams"""
        query = """
        query {
            teams {
                nodes {
                    id
                    key
                    name
                    description
                }
            }
        }
        """
        result = self._query(query)
        return result["teams"]["nodes"]
    
    def create_issue(self, data: Dict) -> Dict:
        """
        Create a new issue
        
        Args:
            data: {
                "title": "Issue title",
                "description": "Issue description",
                "teamId": "team-id",
                "assigneeId": "user-id",
                "priority": 1,  # 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
                "labelIds": ["label-id-1", "label-id-2"],
                "parentId": "parent-issue-id",
                "projectId": "project-id",
                "estimate": 5  # story points
            }
        
        Returns:
            Created issue data
        """
        query = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    url
                    state {
                        name
                    }
                    priority
                    createdAt
                    updatedAt
                }
            }
        }
        """
        
        result = self._query(query, {"input": data})
        
        if result["issueCreate"]["success"]:
            issue = result["issueCreate"]["issue"]
            logger.info(f"✅ Created Linear issue {issue['identifier']}: {issue['title']}")
            return issue
        else:
            raise Exception("Failed to create Linear issue")
    
    def update_issue(self, issue_id: str, data: Dict) -> Dict:
        """
        Update an existing issue
        
        Args:
            issue_id: Linear issue ID
            data: Fields to update
        
        Returns:
            Updated issue data
        """
        query = """
        mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                    updatedAt
                }
            }
        }
        """
        
        result = self._query(query, {"id": issue_id, "input": data})
        
        if result["issueUpdate"]["success"]:
            issue = result["issueUpdate"]["issue"]
            logger.info(f"✅ Updated Linear issue {issue['identifier']}")
            return issue
        else:
            raise Exception("Failed to update Linear issue")
    
    def get_issue(self, issue_id: str) -> Dict:
        """Get issue by ID"""
        query = """
        query Issue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                url
                state {
                    id
                    name
                }
                priority
                estimate
                team {
                    id
                    name
                }
                assignee {
                    id
                    name
                    email
                }
                labels {
                    nodes {
                        id
                        name
                    }
                }
                parent {
                    id
                    identifier
                }
                project {
                    id
                    name
                }
                createdAt
                updatedAt
            }
        }
        """
        
        result = self._query(query, {"id": issue_id})
        return result["issue"]
    
    def list_issues(
        self,
        team_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        state: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Dict]:
        """
        List issues with filters
        
        Args:
            team_id: Filter by team
            assignee_id: Filter by assignee
            state: Filter by state name
            project_id: Filter by project
        
        Returns:
            List of issues
        """
        # Build filter
        filters = []
        if team_id:
            filters.append(f'team: {{id: {{eq: "{team_id}"}}}}')
        if assignee_id:
            filters.append(f'assignee: {{id: {{eq: "{assignee_id}"}}}}')
        if state:
            filters.append(f'state: {{name: {{eq: "{state}"}}}}')
        if project_id:
            filters.append(f'project: {{id: {{eq: "{project_id}"}}}}')
        
        filter_str = ", ".join(filters) if filters else ""
        
        query = f"""
        query Issues {{
            issues({f"filter: {{{filter_str}}}" if filter_str else ""}) {{
                nodes {{
                    id
                    identifier
                    title
                    description
                    url
                    state {{
                        name
                    }}
                    priority
                    estimate
                    team {{
                        id
                        name
                    }}
                    assignee {{
                        id
                        name
                    }}
                    labels {{
                        nodes {{
                            name
                        }}
                    }}
                    createdAt
                    updatedAt
                }}
            }}
        }}
        """
        
        result = self._query(query)
        issues = result["issues"]["nodes"]
        logger.info(f"📋 Fetched {len(issues)} Linear issues")
        
        return issues
    
    def get_teams(self) -> List[Dict]:
        """Get all teams"""
        query = """
        query Teams {
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        
        result = self._query(query)
        return result["teams"]["nodes"]
    
    def get_team_states(self, team_id: str) -> List[Dict]:
        """Get workflow states for a team"""
        query = """
        query Team($id: String!) {
            team(id: $id) {
                states {
                    nodes {
                        id
                        name
                        type
                    }
                }
            }
        }
        """
        
        result = self._query(query, {"id": team_id})
        return result["team"]["states"]["nodes"]
    
    def get_labels(self, team_id: Optional[str] = None) -> List[Dict]:
        """Get labels (optionally filtered by team)"""
        if team_id:
            query = """
            query Team($id: String!) {
                team(id: $id) {
                    labels {
                        nodes {
                            id
                            name
                            color
                        }
                    }
                }
            }
            """
            result = self._query(query, {"id": team_id})
            return result["team"]["labels"]["nodes"]
        else:
            query = """
            query Labels {
                issueLabels {
                    nodes {
                        id
                        name
                        color
                    }
                }
            }
            """
            result = self._query(query)
            return result["issueLabels"]["nodes"]
    
    def create_project(self, team_id: str, name: str, description: str = "") -> Dict:
        """Create a project (epic)"""
        query = """
        mutation ProjectCreate($input: ProjectCreateInput!) {
            projectCreate(input: $input) {
                success
                project {
                    id
                    name
                    description
                    url
                }
            }
        }
        """
        
        data = {
            "teamIds": [team_id],
            "name": name,
            "description": description
        }
        
        result = self._query(query, {"input": data})
        
        if result["projectCreate"]["success"]:
            project = result["projectCreate"]["project"]
            logger.info(f"🎯 Created Linear project: {project['name']}")
            return project
        else:
            raise Exception("Failed to create Linear project")
    
    def get_changes_since(self, since: datetime) -> Dict:
        """
        Get all changes since a specific time
        Used for continuous monitoring
        
        Returns:
            {
                "issues_updated": [...],
                "issues_created": [...]
            }
        """
        since_iso = since.isoformat()
        
        query = f"""
        query Issues {{
            issues(filter: {{updatedAt: {{gt: "{since_iso}"}}}}) {{
                nodes {{
                    id
                    identifier
                    title
                    state {{
                        name
                    }}
                    createdAt
                    updatedAt
                }}
            }}
        }}
        """
        
        result = self._query(query)
        issues = result["issues"]["nodes"]
        
        created = []
        updated = []
        
        for issue in issues:
            created_at = datetime.fromisoformat(issue["createdAt"].replace("Z", "+00:00"))
            if created_at > since:
                created.append(issue)
            else:
                updated.append(issue)
        
        return {
            "issues_created": created,
            "issues_updated": updated
        }
    
    def add_comment(self, issue_id: str, body: str) -> Dict:
        """Add a comment to an issue"""
        query = """
        mutation CommentCreate($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
                comment {
                    id
                    body
                    createdAt
                }
            }
        }
        """
        
        data = {
            "issueId": issue_id,
            "body": body
        }
        
        result = self._query(query, {"input": data})
        
        if result["commentCreate"]["success"]:
            comment = result["commentCreate"]["comment"]
            logger.info(f"💬 Added comment to Linear issue")
            return comment
        else:
            raise Exception("Failed to add comment")


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = LinearClient()
    
    # Get teams
    teams = client.get_teams()
    team_id = teams[0]["id"]
    print(f"Team: {teams[0]['name']} ({team_id})")
    
    # Create issue
    issue = client.create_issue({
        "title": "Add user authentication",
        "description": "Implement JWT authentication for API endpoints",
        "teamId": team_id,
        "priority": 2  # High
    })
    
    print(f"Created issue {issue['identifier']}: {issue['url']}")
    
    # List issues
    issues = client.list_issues(team_id=team_id)
    print(f"Found {len(issues)} issues")
    
    # Monitor changes
    since = datetime.now()
    # ... wait some time ...
    changes = client.get_changes_since(since)
    print(f"Changes: {len(changes['issues_created'])} created, {len(changes['issues_updated'])} updated")
