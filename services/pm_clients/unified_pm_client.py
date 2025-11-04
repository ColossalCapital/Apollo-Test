"""
Unified PM Client for Akashic
Seamlessly integrates Jira, Linear, GitHub, and Bitbucket
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from .jira_client import JiraClient
from .linear_client import LinearClient
from .github_client import GitHubClient
from .bitbucket_client import BitbucketClient

logger = logging.getLogger(__name__)


class UnifiedPMClient:
    """
    Unified PM client that works seamlessly with all PM tools
    Automatically syncs tickets across Jira, Linear, GitHub, and Bitbucket
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize unified PM client
        
        Args:
            config_path: Path to .akashic/pm_config.yaml
        """
        self.config = self._load_config(config_path)
        self.clients = self._initialize_clients()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load PM configuration"""
        if config_path is None:
            # Try to find config in current directory
            config_path = Path.cwd() / ".akashic" / "pm_config.yaml"
        
        if not Path(config_path).exists():
            logger.warning(f"Config not found: {config_path}, using defaults")
            return self._default_config()
        
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "pm_tools": {
                "jira": {"enabled": True},
                "linear": {"enabled": True},
                "github": {"enabled": True},
                "bitbucket": {"enabled": True}
            },
            "sync": {
                "direction": "bidirectional",
                "auto_sync": True
            }
        }
    
    def _initialize_clients(self) -> Dict[str, Any]:
        """Initialize PM tool clients"""
        clients = {}
        
        pm_config = self.config.get("pm_tools", {})
        
        # Jira
        if pm_config.get("jira", {}).get("enabled"):
            try:
                clients["jira"] = JiraClient()
                logger.info("✅ Jira client initialized")
            except Exception as e:
                logger.warning(f"⚠️  Jira client failed: {e}")
        
        # Linear
        if pm_config.get("linear", {}).get("enabled"):
            try:
                clients["linear"] = LinearClient()
                logger.info("✅ Linear client initialized")
            except Exception as e:
                logger.warning(f"⚠️  Linear client failed: {e}")
        
        # GitHub
        if pm_config.get("github", {}).get("enabled"):
            try:
                github_config = pm_config.get("github", {})
                clients["github"] = GitHubClient(
                    owner=github_config.get("org", os.getenv("GITHUB_ORG"))
                )
                logger.info("✅ GitHub client initialized")
            except Exception as e:
                logger.warning(f"⚠️  GitHub client failed: {e}")
        
        # Bitbucket
        if pm_config.get("bitbucket", {}).get("enabled"):
            try:
                clients["bitbucket"] = BitbucketClient()
                logger.info("✅ Bitbucket client initialized")
            except Exception as e:
                logger.warning(f"⚠️  Bitbucket client failed: {e}")
        
        return clients
    
    def create_ticket(
        self,
        title: str,
        description: str,
        ticket_type: str = "Task",
        priority: str = "Medium",
        labels: Optional[List[str]] = None,
        sync_to: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a ticket and sync to all enabled PM tools
        
        Args:
            title: Ticket title
            description: Ticket description
            ticket_type: Task, Bug, Feature, etc.
            priority: Low, Medium, High, Critical
            labels: List of labels/tags
            sync_to: Which tools to sync to (default: all enabled)
        
        Returns:
            Dictionary with ticket IDs from each PM tool
        """
        if sync_to is None:
            sync_to = list(self.clients.keys())
        
        results = {}
        
        # Create in Jira
        if "jira" in sync_to and "jira" in self.clients:
            try:
                jira_config = self.config["pm_tools"]["jira"]
                
                # Build Jira issue data
                issue_data = {
                    "fields": {
                        "project": {"key": jira_config.get("project_key", "AKASHIC")},
                        "summary": title,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": description
                                        }
                                    ]
                                }
                            ]
                        },
                        "issuetype": {"name": jira_config.get("default_issue_type", "Task")}
                    }
                }
                
                # Add labels if provided
                if labels:
                    issue_data["fields"]["labels"] = labels
                
                issue = self.clients["jira"].create_issue(issue_data)
                results["jira"] = {
                    "id": issue["key"],
                    "url": f"{jira_config['site_url']}/browse/{issue['key']}"
                }
                logger.info(f"✅ Created Jira ticket: {issue['key']}")
            except Exception as e:
                logger.error(f"❌ Jira creation failed: {e}")
                results["jira"] = {"error": str(e)}
        
        # Create in Linear
        if "linear" in sync_to and "linear" in self.clients:
            try:
                linear_config = self.config["pm_tools"]["linear"]
                issue = self.clients["linear"].create_issue({
                    "teamId": linear_config.get("team_key", "AKASHIC"),
                    "title": title,
                    "description": description,
                    "priority": self._map_priority_to_linear(priority),
                    "labelIds": labels or []
                })
                results["linear"] = {
                    "id": issue["id"],
                    "url": issue.get("url", "")
                }
                logger.info(f"✅ Created Linear issue: {issue['id']}")
            except Exception as e:
                logger.error(f"❌ Linear creation failed: {e}")
                results["linear"] = {"error": str(e)}
        
        # Create in GitHub
        if "github" in sync_to and "github" in self.clients:
            try:
                github_config = self.config["pm_tools"]["github"]
                issue = self.clients["github"].create_issue(
                    repo=github_config.get("repo", "Akashic"),
                    data={
                        "title": title,
                        "body": description,
                        "labels": labels or []
                    }
                )
                results["github"] = {
                    "id": issue["number"],
                    "url": issue["html_url"]
                }
                logger.info(f"✅ Created GitHub issue: #{issue['number']}")
            except Exception as e:
                logger.error(f"❌ GitHub creation failed: {e}")
                results["github"] = {"error": str(e)}
        
        # Create in Bitbucket
        if "bitbucket" in sync_to and "bitbucket" in self.clients:
            try:
                bitbucket_config = self.config["pm_tools"]["bitbucket"]
                issue = self.clients["bitbucket"].create_issue(
                    repo_slug=bitbucket_config.get("repo", "akashic"),
                    data={
                        "title": title,
                        "content": {"raw": description},
                        "kind": ticket_type.lower(),
                        "priority": priority.lower()
                    }
                )
                results["bitbucket"] = {
                    "id": issue["id"],
                    "url": f"https://bitbucket.org/{bitbucket_config['workspace']}/{bitbucket_config['repo']}/issues/{issue['id']}"
                }
                logger.info(f"✅ Created Bitbucket issue: #{issue['id']}")
            except Exception as e:
                logger.error(f"❌ Bitbucket creation failed: {e}")
                results["bitbucket"] = {"error": str(e)}
        
        return results
    
    def sync_all(self) -> Dict[str, Any]:
        """
        Sync all tickets across all PM tools
        
        Returns:
            Sync results
        """
        results = {
            "synced": 0,
            "errors": 0,
            "details": []
        }
        
        # Get tickets from all sources
        all_tickets = self._get_all_tickets()
        
        # Sync each ticket
        for ticket in all_tickets:
            try:
                self._sync_ticket(ticket)
                results["synced"] += 1
            except Exception as e:
                logger.error(f"❌ Sync failed for {ticket['id']}: {e}")
                results["errors"] += 1
                results["details"].append({
                    "ticket": ticket["id"],
                    "error": str(e)
                })
        
        return results
    
    def _get_all_tickets(self) -> List[Dict]:
        """Get tickets from all PM tools"""
        tickets = []
        
        # TODO: Implement ticket fetching from each tool
        # This will merge tickets from Jira, Linear, GitHub, Bitbucket
        
        return tickets
    
    def _sync_ticket(self, ticket: Dict):
        """Sync a single ticket across all tools"""
        # TODO: Implement ticket syncing logic
        pass
    
    def _map_priority_to_linear(self, priority: str) -> int:
        """Map priority string to Linear priority number"""
        mapping = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4
        }
        return mapping.get(priority, 3)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all PM tool connections"""
        status = {}
        
        for tool, client in self.clients.items():
            try:
                # Test connection
                if tool == "jira":
                    client.get_current_user()
                elif tool == "linear":
                    client.get_viewer()
                elif tool == "github":
                    client.get_user()
                elif tool == "bitbucket":
                    client.get_repositories()
                
                status[tool] = {"connected": True, "error": None}
            except Exception as e:
                status[tool] = {"connected": False, "error": str(e)}
        
        return status
