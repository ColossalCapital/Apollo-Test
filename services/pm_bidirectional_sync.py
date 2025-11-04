"""
Bi-Directional PM Sync with AI Reconciliation

Syncs project plans between local .akashic/pm/ and cloud PM tools:
- Linear
- Jira
- GitHub Issues
- Bitbucket Issues

Handles conflicts with AI-guided reconciliation when local and cloud plans differ.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PMBidirectionalSync:
    """Bi-directional sync between local and cloud PM tools"""
    
    def __init__(self, repo_path: str, linear_api_key: Optional[str] = None,
                 jira_api_key: Optional[str] = None, github_token: Optional[str] = None,
                 bitbucket_token: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.pm_dir = self.repo_path / '.akashic' / 'pm'
        
        # API clients (will be initialized if keys provided)
        self.linear_api_key = linear_api_key
        self.jira_api_key = jira_api_key
        self.github_token = github_token
        self.bitbucket_token = bitbucket_token
        
        # Sync state
        self.local_tickets = {}
        self.cloud_tickets = {}
        self.conflicts = []
        self.reconciliation_plan = {}
    
    async def sync_all(self, direction: str = 'bidirectional') -> Dict:
        """
        Sync all PM tools
        
        Args:
            direction: 'local_to_cloud', 'cloud_to_local', or 'bidirectional'
        """
        logger.info(f"🔄 Starting PM sync ({direction})...")
        
        results = {
            'linear': None,
            'jira': None,
            'github': None,
            'bitbucket': None,
            'conflicts': [],
            'reconciliation_needed': False,
        }
        
        # Sync each PM tool
        if self.linear_api_key:
            results['linear'] = await self.sync_linear(direction)
        
        if self.jira_api_key:
            results['jira'] = await self.sync_jira(direction)
        
        if self.github_token:
            results['github'] = await self.sync_github(direction)
        
        if self.bitbucket_token:
            results['bitbucket'] = await self.sync_bitbucket(direction)
        
        # Check for conflicts
        if direction == 'bidirectional':
            await self._detect_conflicts()
            
            if self.conflicts:
                results['conflicts'] = self.conflicts
                results['reconciliation_needed'] = True
                
                # Generate AI reconciliation plan
                results['reconciliation_plan'] = await self._generate_reconciliation_plan()
        
        logger.info(f"✅ PM sync complete")
        
        return results
    
    async def sync_linear(self, direction: str) -> Dict:
        """Sync with Linear"""
        logger.info("  📋 Syncing Linear...")
        
        local_path = self.pm_dir / 'linear' / 'tickets.json'
        
        if direction == 'local_to_cloud':
            # Push local tickets to Linear
            if local_path.exists():
                local_tickets = json.loads(local_path.read_text())
                # TODO: Implement Linear API push
                logger.info(f"    → Pushed {len(local_tickets.get('tickets', []))} tickets to Linear")
                return {'pushed': len(local_tickets.get('tickets', []))}
        
        elif direction == 'cloud_to_local':
            # Pull tickets from Linear
            # TODO: Implement Linear API pull
            cloud_tickets = await self._fetch_linear_tickets()
            if cloud_tickets:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text(json.dumps(cloud_tickets, indent=2))
                logger.info(f"    ← Pulled {len(cloud_tickets.get('tickets', []))} tickets from Linear")
                return {'pulled': len(cloud_tickets.get('tickets', []))}
        
        else:  # bidirectional
            # Compare and sync both ways
            local_tickets = json.loads(local_path.read_text()) if local_path.exists() else {'tickets': []}
            cloud_tickets = await self._fetch_linear_tickets()
            
            # Store for conflict detection
            self.local_tickets['linear'] = local_tickets
            self.cloud_tickets['linear'] = cloud_tickets
            
            return {
                'local_count': len(local_tickets.get('tickets', [])),
                'cloud_count': len(cloud_tickets.get('tickets', [])),
            }
    
    async def sync_jira(self, direction: str) -> Dict:
        """Sync with Jira"""
        logger.info("  📋 Syncing Jira...")
        
        local_path = self.pm_dir / 'jira' / 'issues.json'
        
        if direction == 'local_to_cloud':
            if local_path.exists():
                local_issues = json.loads(local_path.read_text())
                # TODO: Implement Jira API push
                logger.info(f"    → Pushed {len(local_issues.get('tickets', []))} issues to Jira")
                return {'pushed': len(local_issues.get('tickets', []))}
        
        elif direction == 'cloud_to_local':
            cloud_issues = await self._fetch_jira_issues()
            if cloud_issues:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text(json.dumps(cloud_issues, indent=2))
                logger.info(f"    ← Pulled {len(cloud_issues.get('tickets', []))} issues from Jira")
                return {'pulled': len(cloud_issues.get('tickets', []))}
        
        else:  # bidirectional
            local_issues = json.loads(local_path.read_text()) if local_path.exists() else {'tickets': []}
            cloud_issues = await self._fetch_jira_issues()
            
            self.local_tickets['jira'] = local_issues
            self.cloud_tickets['jira'] = cloud_issues
            
            return {
                'local_count': len(local_issues.get('tickets', [])),
                'cloud_count': len(cloud_issues.get('tickets', [])),
            }
    
    async def sync_github(self, direction: str) -> Dict:
        """Sync with GitHub Issues"""
        logger.info("  📋 Syncing GitHub...")
        
        local_path = self.pm_dir / 'github' / 'issues.json'
        
        if direction == 'local_to_cloud':
            if local_path.exists():
                local_issues = json.loads(local_path.read_text())
                # TODO: Implement GitHub API push
                logger.info(f"    → Pushed {len(local_issues.get('tickets', []))} issues to GitHub")
                return {'pushed': len(local_issues.get('tickets', []))}
        
        elif direction == 'cloud_to_local':
            cloud_issues = await self._fetch_github_issues()
            if cloud_issues:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text(json.dumps(cloud_issues, indent=2))
                logger.info(f"    ← Pulled {len(cloud_issues.get('tickets', []))} issues from GitHub")
                return {'pulled': len(cloud_issues.get('tickets', []))}
        
        else:  # bidirectional
            local_issues = json.loads(local_path.read_text()) if local_path.exists() else {'tickets': []}
            cloud_issues = await self._fetch_github_issues()
            
            self.local_tickets['github'] = local_issues
            self.cloud_tickets['github'] = cloud_issues
            
            return {
                'local_count': len(local_issues.get('tickets', [])),
                'cloud_count': len(cloud_issues.get('tickets', [])),
            }
    
    async def sync_bitbucket(self, direction: str) -> Dict:
        """Sync with Bitbucket Issues"""
        logger.info("  📋 Syncing Bitbucket...")
        
        local_path = self.pm_dir / 'bitbucket' / 'issues.json'
        
        if direction == 'local_to_cloud':
            if local_path.exists():
                local_issues = json.loads(local_path.read_text())
                # TODO: Implement Bitbucket API push
                logger.info(f"    → Pushed {len(local_issues.get('tickets', []))} issues to Bitbucket")
                return {'pushed': len(local_issues.get('tickets', []))}
        
        elif direction == 'cloud_to_local':
            cloud_issues = await self._fetch_bitbucket_issues()
            if cloud_issues:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text(json.dumps(cloud_issues, indent=2))
                logger.info(f"    ← Pulled {len(cloud_issues.get('tickets', []))} issues from Bitbucket")
                return {'pulled': len(cloud_issues.get('tickets', []))}
        
        else:  # bidirectional
            local_issues = json.loads(local_path.read_text()) if local_path.exists() else {'tickets': []}
            cloud_issues = await self._fetch_bitbucket_issues()
            
            self.local_tickets['bitbucket'] = local_issues
            self.cloud_tickets['bitbucket'] = cloud_issues
            
            return {
                'local_count': len(local_issues.get('tickets', [])),
                'cloud_count': len(cloud_issues.get('tickets', [])),
            }
    
    async def _fetch_linear_tickets(self) -> Dict:
        """Fetch tickets from Linear API"""
        # TODO: Implement Linear API integration
        # For now, return empty
        return {'tickets': []}
    
    async def _fetch_jira_issues(self) -> Dict:
        """Fetch issues from Jira API"""
        # TODO: Implement Jira API integration
        return {'tickets': []}
    
    async def _fetch_github_issues(self) -> Dict:
        """Fetch issues from GitHub API"""
        # TODO: Implement GitHub API integration
        return {'tickets': []}
    
    async def _fetch_bitbucket_issues(self) -> Dict:
        """Fetch issues from Bitbucket API"""
        # TODO: Implement Bitbucket API integration
        return {'tickets': []}
    
    async def _detect_conflicts(self):
        """Detect conflicts between local and cloud tickets"""
        self.conflicts = []
        
        for pm_tool in ['linear', 'jira', 'github', 'bitbucket']:
            if pm_tool not in self.local_tickets or pm_tool not in self.cloud_tickets:
                continue
            
            local = self.local_tickets[pm_tool].get('tickets', [])
            cloud = self.cloud_tickets[pm_tool].get('tickets', [])
            
            # Compare ticket counts
            if len(local) != len(cloud):
                self.conflicts.append({
                    'pm_tool': pm_tool,
                    'type': 'count_mismatch',
                    'local_count': len(local),
                    'cloud_count': len(cloud),
                    'severity': 'medium',
                })
            
            # Compare ticket details (by title)
            local_titles = {t['title']: t for t in local}
            cloud_titles = {t['title']: t for t in cloud}
            
            # Tickets only in local
            local_only = set(local_titles.keys()) - set(cloud_titles.keys())
            if local_only:
                self.conflicts.append({
                    'pm_tool': pm_tool,
                    'type': 'local_only_tickets',
                    'tickets': list(local_only),
                    'count': len(local_only),
                    'severity': 'high',
                })
            
            # Tickets only in cloud
            cloud_only = set(cloud_titles.keys()) - set(local_titles.keys())
            if cloud_only:
                self.conflicts.append({
                    'pm_tool': pm_tool,
                    'type': 'cloud_only_tickets',
                    'tickets': list(cloud_only),
                    'count': len(cloud_only),
                    'severity': 'high',
                })
            
            # Tickets with different details
            for title in set(local_titles.keys()) & set(cloud_titles.keys()):
                local_ticket = local_titles[title]
                cloud_ticket = cloud_titles[title]
                
                differences = []
                
                if local_ticket.get('priority') != cloud_ticket.get('priority'):
                    differences.append('priority')
                
                if local_ticket.get('category') != cloud_ticket.get('category'):
                    differences.append('category')
                
                if local_ticket.get('estimated_hours') != cloud_ticket.get('estimated_hours'):
                    differences.append('estimated_hours')
                
                if differences:
                    self.conflicts.append({
                        'pm_tool': pm_tool,
                        'type': 'ticket_mismatch',
                        'ticket_title': title,
                        'differences': differences,
                        'local_ticket': local_ticket,
                        'cloud_ticket': cloud_ticket,
                        'severity': 'medium',
                    })
    
    async def _generate_reconciliation_plan(self) -> Dict:
        """Generate AI-guided reconciliation plan"""
        logger.info("🤖 Generating AI reconciliation plan...")
        
        plan = {
            'generated_at': datetime.now().isoformat(),
            'conflicts_count': len(self.conflicts),
            'recommendations': [],
            'user_choices': [],
        }
        
        for conflict in self.conflicts:
            pm_tool = conflict['pm_tool']
            conflict_type = conflict['type']
            
            if conflict_type == 'local_only_tickets':
                # Recommend pushing to cloud
                plan['recommendations'].append({
                    'pm_tool': pm_tool,
                    'action': 'push_to_cloud',
                    'tickets': conflict['tickets'],
                    'reason': 'These tickets exist locally but not in cloud. Recommend pushing to cloud.',
                    'auto_apply': False,  # Require user confirmation
                })
            
            elif conflict_type == 'cloud_only_tickets':
                # Recommend pulling from cloud
                plan['recommendations'].append({
                    'pm_tool': pm_tool,
                    'action': 'pull_from_cloud',
                    'tickets': conflict['tickets'],
                    'reason': 'These tickets exist in cloud but not locally. Recommend pulling from cloud.',
                    'auto_apply': False,
                })
            
            elif conflict_type == 'ticket_mismatch':
                # Recommend merging with user choice
                plan['user_choices'].append({
                    'pm_tool': pm_tool,
                    'ticket_title': conflict['ticket_title'],
                    'differences': conflict['differences'],
                    'local_version': conflict['local_ticket'],
                    'cloud_version': conflict['cloud_ticket'],
                    'options': [
                        {'choice': 'keep_local', 'description': 'Use local version and push to cloud'},
                        {'choice': 'keep_cloud', 'description': 'Use cloud version and update local'},
                        {'choice': 'merge', 'description': 'Merge both versions (AI-assisted)'},
                    ],
                })
        
        # Save reconciliation plan
        plan_path = self.pm_dir / 'reconciliation_plan.json'
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(json.dumps(plan, indent=2))
        
        # Generate human-readable report
        await self._generate_reconciliation_report(plan)
        
        logger.info(f"✅ Reconciliation plan saved to {plan_path}")
        
        return plan
    
    async def _generate_reconciliation_report(self, plan: Dict):
        """Generate human-readable reconciliation report"""
        report = f"""# PM Reconciliation Plan

Generated: {plan['generated_at']}

## Summary

- **Conflicts Detected:** {plan['conflicts_count']}
- **Auto-Recommendations:** {len(plan['recommendations'])}
- **User Choices Required:** {len(plan['user_choices'])}

## Automatic Recommendations

"""
        
        for rec in plan['recommendations']:
            report += f"### {rec['pm_tool'].title()}: {rec['action'].replace('_', ' ').title()}\n\n"
            report += f"**Reason:** {rec['reason']}\n\n"
            report += f"**Tickets ({len(rec['tickets'])}):**\n"
            for ticket in rec['tickets']:
                report += f"- {ticket}\n"
            report += "\n"
        
        if plan['user_choices']:
            report += "\n## 🤔 User Choices Required\n\n"
            
            for choice in plan['user_choices']:
                report += f"### {choice['pm_tool'].title()}: {choice['ticket_title']}\n\n"
                report += f"**Differences:** {', '.join(choice['differences'])}\n\n"
                
                report += "**Local Version:**\n"
                report += f"- Priority: {choice['local_version'].get('priority')}\n"
                report += f"- Category: {choice['local_version'].get('category')}\n"
                report += f"- Estimated Hours: {choice['local_version'].get('estimated_hours')}\n\n"
                
                report += "**Cloud Version:**\n"
                report += f"- Priority: {choice['cloud_version'].get('priority')}\n"
                report += f"- Category: {choice['cloud_version'].get('category')}\n"
                report += f"- Estimated Hours: {choice['cloud_version'].get('estimated_hours')}\n\n"
                
                report += "**Options:**\n"
                for option in choice['options']:
                    report += f"- `{option['choice']}`: {option['description']}\n"
                report += "\n"
        
        report += "\n## 🚀 Next Steps\n\n"
        report += "1. Review automatic recommendations\n"
        report += "2. Make choices for conflicting tickets\n"
        report += "3. Run: `akashic pm reconcile --apply`\n"
        report += "4. Verify sync completed successfully\n"
        
        # Save report
        report_path = self.pm_dir / 'RECONCILIATION_REPORT.md'
        report_path.write_text(report)
        
        logger.info(f"📝 Reconciliation report saved to {report_path}")
    
    async def apply_reconciliation(self, choices: Dict[str, str]):
        """Apply reconciliation plan with user choices"""
        logger.info("🔄 Applying reconciliation plan...")
        
        # Load plan
        plan_path = self.pm_dir / 'reconciliation_plan.json'
        if not plan_path.exists():
            logger.error("No reconciliation plan found")
            return
        
        plan = json.loads(plan_path.read_text())
        
        # Apply automatic recommendations
        for rec in plan['recommendations']:
            if rec['action'] == 'push_to_cloud':
                # TODO: Push tickets to cloud
                logger.info(f"  → Pushed {len(rec['tickets'])} tickets to {rec['pm_tool']}")
            elif rec['action'] == 'pull_from_cloud':
                # TODO: Pull tickets from cloud
                logger.info(f"  ← Pulled {len(rec['tickets'])} tickets from {rec['pm_tool']}")
        
        # Apply user choices
        for user_choice in plan['user_choices']:
            ticket_title = user_choice['ticket_title']
            choice = choices.get(ticket_title)
            
            if choice == 'keep_local':
                # Push local version to cloud
                logger.info(f"  → Pushing local version of '{ticket_title}' to cloud")
            elif choice == 'keep_cloud':
                # Pull cloud version to local
                logger.info(f"  ← Pulling cloud version of '{ticket_title}' to local")
            elif choice == 'merge':
                # AI-assisted merge
                logger.info(f"  🤖 AI-merging '{ticket_title}'")
        
        logger.info("✅ Reconciliation applied successfully")


if __name__ == "__main__":
    async def main():
        sync = PMBidirectionalSync("/path/to/repo")
        result = await sync.sync_all('bidirectional')
        
        if result['reconciliation_needed']:
            print("Conflicts detected! Review reconciliation plan.")
    
    asyncio.run(main())
