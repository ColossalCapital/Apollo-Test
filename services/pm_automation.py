"""
PM Automation Service

Automated project management service that:
- Monitors codebase changes
- Updates project plans automatically
- Syncs with Linear
- Creates/updates tickets
- Tracks progress
- Detects drift
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from learning.agentic_codebase_rag import AgenticCodebaseRAG
# from agents.pm.linear_integration import LinearClient  # TODO: Implement LinearClient
from learning.theta_edgecloud import ThetaEdgeCloud

logger = logging.getLogger(__name__)


class PMAutomationService:
    """
    Automated PM Service
    
    Features:
    - Auto-create tickets from project plans
    - Auto-update tickets based on code changes
    - Sync codebase state with Linear
    - Detect drift from plan
    - Generate progress reports
    """
    
    def __init__(
        self,
        entity_id: str,
        org_id: Optional[str] = None,
        linear_api_key: Optional[str] = None
    ):
        self.entity_id = entity_id
        self.org_id = org_id
        
        # Initialize components
        # self.linear = LinearClient(api_key=linear_api_key or os.getenv("LINEAR_API_KEY"))  # TODO: Implement LinearClient
        self.linear = None  # Placeholder until LinearClient is implemented
        self.theta = ThetaEdgeCloud(api_key=os.getenv("THETA_API_KEY"))
        
        # Track active codebases
        self.watchers: Dict[str, AgenticCodebaseRAG] = {}
        
        # Track Linear projects
        self.linear_projects: Dict[str, str] = {}  # codebase_id -> linear_project_id
        
    async def start(self):
        """Start PM automation service"""
        logger.info("🚀 Starting PM Automation Service")
        
        # Start periodic sync
        asyncio.create_task(self.periodic_sync())
        
        # Start progress tracking
        asyncio.create_task(self.track_progress())
        
    async def register_codebase(
        self,
        codebase_id: str,
        repo_path: str,
        team_id: Optional[str] = None
    ):
        """Register a codebase for PM automation"""
        
        logger.info(f"📝 Registering codebase: {codebase_id}")
        
        # Start code watcher
        watcher = AgenticCodebaseRAG(
            codebase_id=codebase_id,
            team_id=team_id or self.entity_id,
            org_id=self.org_id or self.entity_id,
            repo_path=repo_path
        )
        
        await watcher.start_watching()
        self.watchers[codebase_id] = watcher
        
        # Create Linear project
        linear_project = await self.create_linear_project(codebase_id, repo_path)
        self.linear_projects[codebase_id] = linear_project["id"]
        
        logger.info(f"✅ Codebase registered: {codebase_id}")
        logger.info(f"📋 Linear project: {linear_project['name']}")
        
    async def create_linear_project(
        self,
        codebase_id: str,
        repo_path: str
    ) -> Dict[str, Any]:
        """Create Linear project for codebase"""
        
        # Generate project plan
        plan = await self.generate_project_plan(codebase_id, repo_path)
        
        # Create Linear project
        project = await self.linear.create_project(
            name=f"{codebase_id} - Automated PM",
            description=plan["summary"],
            team_id=self.linear.get_team_id()
        )
        
        # Create tickets for each phase/task
        for phase in plan["phases"]:
            # Create phase milestone
            milestone = await self.linear.create_milestone(
                project_id=project["id"],
                name=phase["name"],
                description=phase["description"]
            )
            
            # Create tickets for tasks
            for task in phase["tasks"]:
                ticket = await self.linear.create_ticket(
                    project_id=project["id"],
                    milestone_id=milestone["id"],
                    title=task["title"],
                    description=task["description"],
                    priority=task.get("priority", "medium"),
                    estimate=task.get("estimate", 3)
                )
                
                logger.info(f"  ✅ Created ticket: {ticket['identifier']} - {task['title']}")
                
        return project
        
    async def generate_project_plan(
        self,
        codebase_id: str,
        repo_path: str
    ) -> Dict[str, Any]:
        """Generate project plan for codebase"""
        
        # Analyze codebase structure
        from learning.codebase_indexer import CodebaseIndexer
        
        indexer = CodebaseIndexer(codebase_path=repo_path)
        analysis = await indexer.analyze()
        
        # Generate plan with AI
        prompt = f"""
Generate a project plan for this codebase:

Analysis:
{json.dumps(analysis, indent=2)}

Create a structured project plan with:
1. Summary (2-3 sentences)
2. Phases (3-5 phases)
3. Tasks per phase (3-7 tasks each)
4. Priorities (high/medium/low)
5. Estimates (story points)
6. Dependencies

Return JSON:
{{
  "summary": "...",
  "phases": [
    {{
      "name": "Phase 1: Core Features",
      "description": "...",
      "tasks": [
        {{
          "title": "Task title",
          "description": "Task description",
          "priority": "high|medium|low",
          "estimate": 3,
          "dependencies": ["task_id"]
        }}
      ]
    }}
  ]
}}
"""
        
        response = await self.theta.query_chatbot(
            chatbot_id="project_planner",
            query=prompt,
            mode="json"
        )
        
        return json.loads(response)
        
    async def periodic_sync(self):
        """Periodically sync codebases with Linear"""
        interval = int(os.getenv("PM_SYNC_INTERVAL", "600"))
        
        while True:
            await asyncio.sleep(interval)
            
            try:
                logger.info("🔄 Starting periodic PM sync...")
                
                for codebase_id, watcher in self.watchers.items():
                    await self.sync_codebase(codebase_id)
                    
                logger.info("✅ PM sync complete")
                
            except Exception as e:
                logger.error(f"Error in PM sync: {e}")
                
    async def sync_codebase(self, codebase_id: str):
        """Sync codebase state with Linear"""
        
        logger.info(f"🔄 Syncing {codebase_id}...")
        
        # Get current state from watcher
        watcher = self.watchers.get(codebase_id)
        if not watcher:
            return
            
        # Get Linear project
        project_id = self.linear_projects.get(codebase_id)
        if not project_id:
            return
            
        # Check for completed work
        # TODO: Implement code analysis to detect completed features
        
        # Update ticket statuses
        # TODO: Auto-update tickets based on code changes
        
        # Detect drift
        drift = await self.detect_drift(codebase_id)
        if drift["has_drift"]:
            logger.warning(f"⚠️ Drift detected in {codebase_id}")
            await self.handle_drift(codebase_id, drift)
            
    async def detect_drift(self, codebase_id: str) -> Dict[str, Any]:
        """Detect drift from project plan"""
        
        # Get current codebase state
        watcher = self.watchers.get(codebase_id)
        if not watcher:
            return {"has_drift": False}
            
        # Get Linear tickets
        project_id = self.linear_projects.get(codebase_id)
        tickets = await self.linear.get_project_tickets(project_id)
        
        # Compare actual vs planned
        # TODO: Implement drift detection logic
        
        return {
            "has_drift": False,
            "drift_score": 0.0,
            "details": []
        }
        
    async def handle_drift(self, codebase_id: str, drift: Dict[str, Any]):
        """Handle detected drift"""
        
        logger.info(f"🔧 Handling drift for {codebase_id}")
        
        # Create drift report
        report = f"""
# Drift Detected: {codebase_id}

**Drift Score:** {drift['drift_score']}

**Details:**
{chr(10).join(f"- {d}" for d in drift['details'])}

**Recommended Actions:**
1. Review project plan
2. Update tickets
3. Adjust timeline
"""
        
        # Create Linear ticket for drift
        project_id = self.linear_projects.get(codebase_id)
        await self.linear.create_ticket(
            project_id=project_id,
            title=f"⚠️ Drift Detected - Review Required",
            description=report,
            priority="high",
            labels=["drift", "review-needed"]
        )
        
    async def track_progress(self):
        """Track progress and generate reports"""
        
        while True:
            await asyncio.sleep(86400)  # Daily
            
            try:
                logger.info("📊 Generating progress reports...")
                
                for codebase_id in self.watchers.keys():
                    report = await self.generate_progress_report(codebase_id)
                    await self.send_progress_report(codebase_id, report)
                    
                logger.info("✅ Progress reports sent")
                
            except Exception as e:
                logger.error(f"Error generating progress reports: {e}")
                
    async def generate_progress_report(self, codebase_id: str) -> str:
        """Generate progress report for codebase"""
        
        # Get Linear tickets
        project_id = self.linear_projects.get(codebase_id)
        tickets = await self.linear.get_project_tickets(project_id)
        
        # Calculate metrics
        total = len(tickets)
        completed = len([t for t in tickets if t["state"]["name"] == "Done"])
        in_progress = len([t for t in tickets if t["state"]["name"] == "In Progress"])
        todo = total - completed - in_progress
        
        progress_pct = (completed / total * 100) if total > 0 else 0
        
        report = f"""
# Progress Report: {codebase_id}

**Date:** {datetime.utcnow().strftime("%Y-%m-%d")}

## Summary
- **Total Tickets:** {total}
- **Completed:** {completed} ({progress_pct:.1f}%)
- **In Progress:** {in_progress}
- **To Do:** {todo}

## Recent Activity
{await self.get_recent_activity(codebase_id)}

## Upcoming Milestones
{await self.get_upcoming_milestones(project_id)}

## Blockers
{await self.get_blockers(project_id)}
"""
        
        return report
        
    async def get_recent_activity(self, codebase_id: str) -> str:
        """Get recent activity for codebase"""
        # TODO: Implement
        return "- Recent commits\n- Ticket updates\n- Code reviews"
        
    async def get_upcoming_milestones(self, project_id: str) -> str:
        """Get upcoming milestones"""
        # TODO: Implement
        return "- Phase 1 completion (2 days)\n- Phase 2 start (3 days)"
        
    async def get_blockers(self, project_id: str) -> str:
        """Get current blockers"""
        tickets = await self.linear.get_project_tickets(project_id)
        blockers = [t for t in tickets if "blocked" in t.get("labels", [])]
        
        if not blockers:
            return "None"
            
        return "\n".join(f"- {t['identifier']}: {t['title']}" for t in blockers)
        
    async def send_progress_report(self, codebase_id: str, report: str):
        """Send progress report"""
        
        # Save to file
        output_path = os.getenv("DOCS_OUTPUT_PATH", "/workspace/consolidated_docs")
        report_file = f"{output_path}/progress_reports/{codebase_id}_{datetime.utcnow().strftime('%Y%m%d')}.md"
        
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report)
            
        logger.info(f"📄 Progress report saved: {report_file}")
        
        # Send via Slack if configured
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook:
            # TODO: Send to Slack
            pass


# ============================================================================
# Service Entry Point
# ============================================================================

async def main():
    """Start PM automation service"""
    
    entity_id = os.getenv("ENTITY_ID", "default")
    org_id = os.getenv("ORG_ID")
    
    service = PMAutomationService(
        entity_id=entity_id,
        org_id=org_id
    )
    
    await service.start()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 PM Automation Service stopped")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())
