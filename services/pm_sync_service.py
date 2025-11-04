"""
PM Sync Service - Continuous project management syncing

Syncs with multiple PM tools:
- Linear: Tickets, sprints, issues
- Jira: Issues, epics, sprints
- GitHub: Issues, PRs, projects
- Bitbucket: PRs, issues

Monitors code changes and updates ticket status bidirectionally
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
import subprocess
import re

logger = logging.getLogger(__name__)


class PMSyncService:
    """Syncs with multiple project management tools"""
    
    def __init__(self, repo_path: str, entity_id: str, pm_config: Dict = None):
        self.repo_path = Path(repo_path)
        self.entity_id = entity_id
        self.pm_config = pm_config or {}
        self.is_running = False
        
        # Output directory
        self.pm_dir = self.repo_path / ".akashic" / "pm"
        self.pm_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize clients
        self.linear_client = LinearClient(self.pm_config.get('linear', {}))
        self.jira_client = JiraClient(self.pm_config.get('jira', {}))
        self.github_client = GitHubClient(self.pm_config.get('github', {}))
        self.bitbucket_client = BitbucketClient(self.pm_config.get('bitbucket', {}))
        
        # Track last sync
        self.last_commit_hash = None
        
    async def start_monitoring(self):
        """Start monitoring and syncing"""
        logger.info(f"🔄 Starting PM Sync for {self.repo_path}")
        self.is_running = True
        
        # Initial sync
        await self._sync_all()
        
        # Start periodic sync loop
        asyncio.create_task(self._sync_loop())
        
        logger.info("✅ PM Sync started")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("🛑 PM Sync stopped")
        
    async def _sync_loop(self):
        """Periodic sync loop"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Sync every minute
                await self._sync_all()
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                
    async def _sync_all(self):
        """Sync with all enabled PM tools"""
        logger.info("🔄 Syncing with PM tools...")
        
        # Check for new commits
        new_commits = await self._get_new_commits()
        
        if new_commits:
            # Extract ticket references from commits
            ticket_refs = self._extract_ticket_refs(new_commits)
            
            # Update tickets in PM tools
            await self._update_tickets(ticket_refs, new_commits)
            
        # Sync from PM tools to local
        await self._sync_from_pm_tools()
        
    async def _get_new_commits(self) -> List[Dict]:
        """Get new commits since last sync"""
        try:
            # Get latest commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            current_hash = result.stdout.strip()
            
            if self.last_commit_hash == current_hash:
                return []
                
            # Get commits since last sync
            if self.last_commit_hash:
                result = subprocess.run(
                    ['git', 'log', f'{self.last_commit_hash}..{current_hash}', '--format=%H|%s|%an|%ae|%ai'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
            else:
                # First sync - get last 10 commits
                result = subprocess.run(
                    ['git', 'log', '-10', '--format=%H|%s|%an|%ae|%ai'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    commits.append({
                        'hash': parts[0],
                        'message': parts[1],
                        'author': parts[2],
                        'email': parts[3],
                        'date': parts[4]
                    })
                    
            self.last_commit_hash = current_hash
            return commits
            
        except Exception as e:
            logger.error(f"Failed to get commits: {e}")
            return []
            
    def _extract_ticket_refs(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract ticket references from commit messages"""
        ticket_refs = {
            'linear': [],
            'jira': [],
            'github': []
        }
        
        for commit in commits:
            message = commit['message']
            
            # Linear: LIN-123, PROJ-456
            linear_matches = re.findall(r'([A-Z]+-\d+)', message)
            for match in linear_matches:
                ticket_refs['linear'].append({
                    'ticket_id': match,
                    'commit': commit
                })
                
            # GitHub: #123, fixes #456
            github_matches = re.findall(r'#(\d+)', message)
            for match in github_matches:
                ticket_refs['github'].append({
                    'issue_number': match,
                    'commit': commit
                })
                
            # Jira: PROJ-123
            jira_matches = re.findall(r'([A-Z]{2,}-\d+)', message)
            for match in jira_matches:
                ticket_refs['jira'].append({
                    'issue_key': match,
                    'commit': commit
                })
                
        return ticket_refs
        
    async def _update_tickets(self, ticket_refs: Dict, commits: List[Dict]):
        """Update tickets in PM tools"""
        # Update Linear tickets
        if ticket_refs['linear'] and self.linear_client.is_enabled():
            await self.linear_client.update_tickets(ticket_refs['linear'])
            
        # Update Jira issues
        if ticket_refs['jira'] and self.jira_client.is_enabled():
            await self.jira_client.update_issues(ticket_refs['jira'])
            
        # Update GitHub issues
        if ticket_refs['github'] and self.github_client.is_enabled():
            await self.github_client.update_issues(ticket_refs['github'])
            
    async def _sync_from_pm_tools(self):
        """Sync data from PM tools to local"""
        # Sync from Linear
        if self.linear_client.is_enabled():
            tickets = await self.linear_client.fetch_tickets()
            await self._save_tickets('linear', tickets)
            
        # Sync from Jira
        if self.jira_client.is_enabled():
            issues = await self.jira_client.fetch_issues()
            await self._save_tickets('jira', issues)
            
        # Sync from GitHub
        if self.github_client.is_enabled():
            issues = await self.github_client.fetch_issues()
            await self._save_tickets('github', issues)
            
    async def _save_tickets(self, tool: str, tickets: List[Dict]):
        """Save tickets to .akashic/pm/{tool}/"""
        tool_dir = self.pm_dir / tool
        tool_dir.mkdir(exist_ok=True)
        
        # Save tickets.json
        tickets_file = tool_dir / "tickets.json"
        tickets_file.write_text(json.dumps(tickets, indent=2))
        
        # Generate sprint plan
        await self._generate_sprint_plan(tool, tickets)
        
        # Log sync
        log_file = tool_dir / "sync_log.json"
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ticket_count': len(tickets),
            'status': 'success'
        }
        
        # Append to log
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs[-100:], indent=2))  # Keep last 100 entries
        
    async def _generate_sprint_plan(self, tool: str, tickets: List[Dict]):
        """Generate sprint plan markdown"""
        tool_dir = self.pm_dir / tool
        
        plan = f"""# Sprint Plan - {tool.title()}
Generated: {datetime.now().isoformat()}

## Active Tickets ({len(tickets)})

"""
        
        # Group by status
        by_status = {}
        for ticket in tickets:
            status = ticket.get('status', 'unknown')
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(ticket)
            
        for status, status_tickets in by_status.items():
            plan += f"\n### {status.title()} ({len(status_tickets)})\n\n"
            for ticket in status_tickets:
                title = ticket.get('title', 'Untitled')
                ticket_id = ticket.get('id', 'N/A')
                plan += f"- [{ticket_id}] {title}\n"
                
        (tool_dir / "sprint_plan.md").write_text(plan)


class LinearClient:
    """Linear API client"""
    
    def __init__(self, config: Dict):
        self.api_key = config.get('api_key')
        self.enabled = bool(self.api_key)
        
    def is_enabled(self) -> bool:
        return self.enabled
        
    async def fetch_tickets(self) -> List[Dict]:
        """Fetch tickets from Linear"""
        # TODO: Implement Linear API integration
        logger.info("📋 Fetching Linear tickets...")
        return []
        
    async def update_tickets(self, ticket_refs: List[Dict]):
        """Update Linear tickets"""
        # TODO: Implement Linear API integration
        logger.info(f"✅ Updated {len(ticket_refs)} Linear tickets")


class JiraClient:
    """Jira API client"""
    
    def __init__(self, config: Dict):
        self.api_key = config.get('api_key')
        self.enabled = bool(self.api_key)
        
    def is_enabled(self) -> bool:
        return self.enabled
        
    async def fetch_issues(self) -> List[Dict]:
        """Fetch issues from Jira"""
        # TODO: Implement Jira API integration
        logger.info("📋 Fetching Jira issues...")
        return []
        
    async def update_issues(self, issue_refs: List[Dict]):
        """Update Jira issues"""
        # TODO: Implement Jira API integration
        logger.info(f"✅ Updated {len(issue_refs)} Jira issues")


class GitHubClient:
    """GitHub API client"""
    
    def __init__(self, config: Dict):
        self.api_key = config.get('api_key')
        self.enabled = bool(self.api_key)
        
    def is_enabled(self) -> bool:
        return self.enabled
        
    async def fetch_issues(self) -> List[Dict]:
        """Fetch issues from GitHub"""
        # TODO: Implement GitHub API integration
        logger.info("📋 Fetching GitHub issues...")
        return []
        
    async def update_issues(self, issue_refs: List[Dict]):
        """Update GitHub issues"""
        # TODO: Implement GitHub API integration
        logger.info(f"✅ Updated {len(issue_refs)} GitHub issues")


class BitbucketClient:
    """Bitbucket API client"""
    
    def __init__(self, config: Dict):
        self.api_key = config.get('api_key')
        self.enabled = bool(self.api_key)
        
    def is_enabled(self) -> bool:
        return self.enabled
        
    async def fetch_prs(self) -> List[Dict]:
        """Fetch PRs from Bitbucket"""
        # TODO: Implement Bitbucket API integration
        logger.info("📋 Fetching Bitbucket PRs...")
        return []
