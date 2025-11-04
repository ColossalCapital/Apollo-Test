"""
Bidirectional Sync Service
Syncs tickets between local .akashic/ and cloud PM tools (Linear, Jira, GitHub)
Handles conflict detection and resolution
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from .pm_universal_adapter import (
    UniversalTicket, PMTool, PMToolMapping,
    TicketType, TicketStatus, TicketPriority
)
from .pm_clients.github_client import GitHubClient
from .pm_clients.linear_client import LinearClient

logger = logging.getLogger(__name__)


class BidirectionalSyncService:
    """
    Bidirectional sync between local .akashic/ and PM tools
    
    Sync Strategy:
    1. Load local tickets from .akashic/pm/tickets.json
    2. Load remote tickets from all connected PM tools
    3. Detect conflicts (same ticket modified in multiple places)
    4. Resolve conflicts (last-write-wins or manual)
    5. Sync changes bidirectionally
    6. Save updated tickets locally
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.akashic_path = self.repo_path / ".akashic"
        self.pm_path = self.akashic_path / "pm"
        self.tickets_file = self.pm_path / "tickets.json"
        self.sync_log_file = self.pm_path / "sync_log.json"
        self.conflicts_file = self.pm_path / "conflicts.json"
        
        # PM clients
        self.github_client = None
        self.linear_client = None
        self.jira_client = None
        
        # Ensure directories exist
        self.pm_path.mkdir(parents=True, exist_ok=True)
    
    def connect_github(self, owner: str, repo: str, token: Optional[str] = None):
        """Connect to GitHub"""
        self.github_client = GitHubClient(token=token, owner=owner, repo=repo)
        logger.info(f"🔗 Connected to GitHub: {owner}/{repo}")
    
    def connect_linear(self, api_key: Optional[str] = None):
        """Connect to Linear"""
        self.linear_client = LinearClient(api_key=api_key)
        logger.info(f"🔗 Connected to Linear")
    
    async def sync_all(self):
        """
        Perform full bidirectional sync with all connected PM tools
        """
        logger.info("🔄 Starting bidirectional sync...")
        
        # 1. Load local tickets
        local_tickets = self._load_local_tickets()
        logger.info(f"📂 Loaded {len(local_tickets)} local tickets")
        
        # 2. Load remote tickets from all PM tools
        remote_tickets = {}
        
        if self.github_client:
            remote_tickets[PMTool.GITHUB] = await self._load_github_tickets()
        
        if self.linear_client:
            remote_tickets[PMTool.LINEAR] = await self._load_linear_tickets()
        
        # 3. Detect conflicts
        conflicts = self._detect_conflicts(local_tickets, remote_tickets)
        
        if conflicts:
            logger.warning(f"⚠️  Detected {len(conflicts)} conflicts")
            self._save_conflicts(conflicts)
            
            # 4. Resolve conflicts (last-write-wins for now)
            local_tickets = self._resolve_conflicts(conflicts, local_tickets)
        
        # 5. Sync changes bidirectionally
        await self._sync_to_remote(local_tickets)
        await self._sync_from_remote(remote_tickets, local_tickets)
        
        # 6. Save updated tickets locally
        self._save_local_tickets(local_tickets)
        
        # 7. Log sync
        self._log_sync(len(local_tickets), len(conflicts))
        
        logger.info("✅ Sync complete!")
    
    async def sync_from_documentation(self, doc_path: str):
        """
        Convert documentation to tickets and sync to all PM tools
        
        This is the key workflow:
        1. Parse documentation
        2. Create universal tickets
        3. Sync to all PM tools
        4. Save locally
        """
        from .pm_universal_adapter import DocumentationToTicketConverter
        
        logger.info(f"📄 Converting documentation: {doc_path}")
        
        # Convert docs to tickets
        converter = DocumentationToTicketConverter()
        new_tickets = converter.convert_feature_docs_to_tickets(doc_path)
        
        logger.info(f"📋 Created {len(new_tickets)} tickets from documentation")
        
        # Load existing tickets
        existing_tickets = self._load_local_tickets()
        
        # Add new tickets (avoid duplicates)
        for ticket in new_tickets:
            if not any(t.id == ticket.id for t in existing_tickets):
                existing_tickets.append(ticket)
        
        # Sync to all PM tools
        await self._sync_to_remote(existing_tickets)
        
        # Save locally
        self._save_local_tickets(existing_tickets)
        
        logger.info("✅ Documentation synced to PM tools!")
        
        return new_tickets
    
    def _load_local_tickets(self) -> List[UniversalTicket]:
        """Load tickets from local .akashic/pm/tickets.json"""
        if not self.tickets_file.exists():
            return []
        
        try:
            with open(self.tickets_file, 'r') as f:
                data = json.load(f)
                return [self._dict_to_ticket(t) for t in data]
        except Exception as e:
            logger.error(f"Failed to load local tickets: {e}")
            return []
    
    def _save_local_tickets(self, tickets: List[UniversalTicket]):
        """Save tickets to local .akashic/pm/tickets.json"""
        try:
            data = [self._ticket_to_dict(t) for t in tickets]
            with open(self.tickets_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Saved {len(tickets)} tickets locally")
        except Exception as e:
            logger.error(f"Failed to save local tickets: {e}")
    
    async def _load_github_tickets(self) -> List[UniversalTicket]:
        """Load tickets from GitHub"""
        try:
            issues = self.github_client.list_issues(state="all")
            tickets = [
                PMToolMapping.from_tool_format(issue, PMTool.GITHUB)
                for issue in issues
            ]
            logger.info(f"📥 Loaded {len(tickets)} tickets from GitHub")
            return tickets
        except Exception as e:
            logger.error(f"Failed to load GitHub tickets: {e}")
            return []
    
    async def _load_linear_tickets(self) -> List[UniversalTicket]:
        """Load tickets from Linear"""
        try:
            issues = self.linear_client.list_issues()
            tickets = [
                PMToolMapping.from_tool_format(issue, PMTool.LINEAR)
                for issue in issues
            ]
            logger.info(f"📥 Loaded {len(tickets)} tickets from Linear")
            return tickets
        except Exception as e:
            logger.error(f"Failed to load Linear tickets: {e}")
            return []
    
    def _detect_conflicts(
        self,
        local: List[UniversalTicket],
        remote: Dict[PMTool, List[UniversalTicket]]
    ) -> List[Dict]:
        """
        Detect conflicts between local and remote tickets
        
        A conflict occurs when:
        - Same ticket modified in multiple places
        - Different values for same field
        - Both modified after last sync
        """
        conflicts = []
        
        for local_ticket in local:
            for tool, remote_tickets in remote.items():
                # Find matching remote ticket
                remote_id = local_ticket.synced_to.get(tool)
                if not remote_id:
                    continue
                
                remote_ticket = next(
                    (t for t in remote_tickets if t.source_id == remote_id),
                    None
                )
                
                if not remote_ticket:
                    continue
                
                # Check if both were modified
                if (local_ticket.updated_at and remote_ticket.updated_at and
                    local_ticket.updated_at != remote_ticket.updated_at):
                    
                    # Detect field differences
                    differences = self._find_differences(local_ticket, remote_ticket)
                    
                    if differences:
                        conflicts.append({
                            "local": local_ticket,
                            "remote": remote_ticket,
                            "tool": tool,
                            "differences": differences
                        })
        
        return conflicts
    
    def _find_differences(self, local: UniversalTicket, remote: UniversalTicket) -> List[str]:
        """Find differences between two tickets"""
        differences = []
        
        fields = ["title", "description", "status", "priority", "assignee"]
        for field in fields:
            local_val = getattr(local, field)
            remote_val = getattr(remote, field)
            if local_val != remote_val:
                differences.append(field)
        
        return differences
    
    def _resolve_conflicts(
        self,
        conflicts: List[Dict],
        local_tickets: List[UniversalTicket]
    ) -> List[UniversalTicket]:
        """
        Resolve conflicts using last-write-wins strategy
        
        Future: Add manual resolution UI
        """
        for conflict in conflicts:
            local = conflict["local"]
            remote = conflict["remote"]
            
            # Last-write-wins
            if remote.updated_at > local.updated_at:
                # Remote wins - update local
                idx = next(i for i, t in enumerate(local_tickets) if t.id == local.id)
                local_tickets[idx] = remote
                logger.info(f"🔄 Conflict resolved: Remote wins for {local.id}")
            else:
                # Local wins - will sync to remote
                logger.info(f"🔄 Conflict resolved: Local wins for {local.id}")
        
        return local_tickets
    
    async def _sync_to_remote(self, tickets: List[UniversalTicket]):
        """Sync local tickets to remote PM tools"""
        for ticket in tickets:
            # Sync to GitHub
            if self.github_client:
                await self._sync_ticket_to_github(ticket)
            
            # Sync to Linear
            if self.linear_client:
                await self._sync_ticket_to_linear(ticket)
    
    async def _sync_ticket_to_github(self, ticket: UniversalTicket):
        """Sync single ticket to GitHub"""
        try:
            github_data = PMToolMapping.to_tool_format(ticket, PMTool.GITHUB)
            
            if PMTool.GITHUB not in ticket.synced_to:
                # Create new issue
                issue = self.github_client.create_issue(github_data)
                ticket.synced_to[PMTool.GITHUB] = str(issue["number"])
            else:
                # Update existing issue
                issue_number = int(ticket.synced_to[PMTool.GITHUB])
                self.github_client.update_issue(issue_number, github_data)
        except Exception as e:
            logger.error(f"Failed to sync ticket {ticket.id} to GitHub: {e}")
    
    async def _sync_ticket_to_linear(self, ticket: UniversalTicket):
        """Sync single ticket to Linear"""
        try:
            linear_data = PMToolMapping.to_tool_format(ticket, PMTool.LINEAR)
            
            if PMTool.LINEAR not in ticket.synced_to:
                # Create new issue
                issue = self.linear_client.create_issue(linear_data)
                ticket.synced_to[PMTool.LINEAR] = issue["id"]
            else:
                # Update existing issue
                issue_id = ticket.synced_to[PMTool.LINEAR]
                self.linear_client.update_issue(issue_id, linear_data)
        except Exception as e:
            logger.error(f"Failed to sync ticket {ticket.id} to Linear: {e}")
    
    async def _sync_from_remote(
        self,
        remote: Dict[PMTool, List[UniversalTicket]],
        local: List[UniversalTicket]
    ):
        """Sync remote tickets to local"""
        for tool, remote_tickets in remote.items():
            for remote_ticket in remote_tickets:
                # Check if ticket exists locally
                local_ticket = next(
                    (t for t in local if t.synced_to.get(tool) == remote_ticket.source_id),
                    None
                )
                
                if not local_ticket:
                    # New ticket from remote - add to local
                    local.append(remote_ticket)
                    logger.info(f"📥 Added new ticket from {tool.value}: {remote_ticket.title}")
    
    def _save_conflicts(self, conflicts: List[Dict]):
        """Save conflicts to file for manual resolution"""
        try:
            data = [
                {
                    "local_id": c["local"].id,
                    "remote_id": c["remote"].source_id,
                    "tool": c["tool"].value,
                    "differences": c["differences"]
                }
                for c in conflicts
            ]
            with open(self.conflicts_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conflicts: {e}")
    
    def _log_sync(self, ticket_count: int, conflict_count: int):
        """Log sync operation"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "ticket_count": ticket_count,
                "conflict_count": conflict_count
            }
            
            # Load existing log
            log = []
            if self.sync_log_file.exists():
                with open(self.sync_log_file, 'r') as f:
                    log = json.load(f)
            
            # Append new entry
            log.append(log_entry)
            
            # Keep last 100 entries
            log = log[-100:]
            
            # Save log
            with open(self.sync_log_file, 'w') as f:
                json.dump(log, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log sync: {e}")
    
    def _ticket_to_dict(self, ticket: UniversalTicket) -> Dict:
        """Convert UniversalTicket to dict for JSON serialization"""
        return {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "type": ticket.type.value,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "parent_id": ticket.parent_id,
            "epic_id": ticket.epic_id,
            "assignee": ticket.assignee,
            "team": ticket.team,
            "labels": ticket.labels,
            "affected_files": ticket.affected_files,
            "story_points": ticket.story_points,
            "suggested_agent": ticket.suggested_agent,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
            "source_tool": ticket.source_tool.value if ticket.source_tool else None,
            "source_id": ticket.source_id,
            "synced_to": {k.value: v for k, v in ticket.synced_to.items()}
        }
    
    def _dict_to_ticket(self, data: Dict) -> UniversalTicket:
        """Convert dict to UniversalTicket"""
        return UniversalTicket(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            type=TicketType(data["type"]),
            status=TicketStatus(data["status"]),
            priority=TicketPriority(data["priority"]),
            parent_id=data.get("parent_id"),
            epic_id=data.get("epic_id"),
            assignee=data.get("assignee"),
            team=data.get("team"),
            labels=data.get("labels", []),
            affected_files=data.get("affected_files", []),
            story_points=data.get("story_points"),
            suggested_agent=data.get("suggested_agent"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            source_tool=PMTool(data["source_tool"]) if data.get("source_tool") else None,
            source_id=data.get("source_id"),
            synced_to={PMTool(k): v for k, v in data.get("synced_to", {}).items()}
        )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize sync service
        sync = BidirectionalSyncService("/path/to/repo")
        
        # Connect to PM tools
        sync.connect_github(owner="your-org", repo="your-repo")
        sync.connect_linear()
        
        # Sync from documentation
        tickets = await sync.sync_from_documentation("docs/features/auth.md")
        print(f"Created {len(tickets)} tickets from documentation")
        
        # Perform full sync
        await sync.sync_all()
    
    asyncio.run(main())
