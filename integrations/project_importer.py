"""
Project Importer

Import existing projects from external PM tools into Linear + Akashic.

Features:
- Import from Jira, Asana, GitHub Projects, etc.
- AI-generate Mermaid diagrams from descriptions
- Enrich ticket descriptions
- Create Linear project
- Set up bidirectional sync
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from integrations.pm_integration import PMIntegrationLayer
from integrations.bidirectional_sync import get_sync_engine, ConflictStrategy
from learning.deepseek_coder import DeepSeekCoder

logger = logging.getLogger(__name__)


class ProjectImporter:
    """
    Import existing project from external PM tool
    
    Supports:
    - Jira → Linear + Mermaid
    - Asana → Linear + Mermaid
    - GitHub Projects → Linear + Mermaid
    - ClickUp → Linear + Mermaid
    """
    
    def __init__(self):
        self.deepseek = DeepSeekCoder(model_size="6.7b")
        self.sync_engine = get_sync_engine()
        
    async def import_project(
        self,
        external_pm: str,
        project_id: str,
        codebase_id: str,
        team_id: str,
        org_id: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Import entire project from external PM
        
        Args:
            external_pm: PM tool (jira, asana, github, etc.)
            project_id: External project ID
            codebase_id: Associated codebase ID
            team_id: Team ID
            org_id: Organization ID
            options: Import options
            
        Returns:
            Import result with stats
        """
        
        logger.info(f"🔄 Importing {external_pm} project: {project_id}")
        
        # Default options
        options = options or {
            'generate_mermaid': True,
            'enrich_descriptions': True,
            'enable_sync': True,
            'conflict_strategy': ConflictStrategy.LINEAR_WINS
        }
        
        try:
            # 1. Connect to external PM
            pm_integration = PMIntegrationLayer(external_pm)
            
            # 2. Fetch all tickets
            logger.info(f"📥 Fetching tickets from {external_pm}...")
            external_tickets = await pm_integration.sync_tickets(project_id)
            logger.info(f"Found {len(external_tickets)} tickets")
            
            # 3. Analyze project structure
            project_structure = await self.analyze_project_structure(
                external_tickets,
                external_pm
            )
            
            # 4. Create Linear project
            logger.info(f"📝 Creating Linear project...")
            linear_project = await self.create_linear_project(
                name=project_structure['name'],
                description=project_structure['description'],
                team_id=team_id,
                codebase_id=codebase_id
            )
            
            # 5. Import tickets with AI enhancement
            logger.info(f"🤖 Importing tickets with AI enhancement...")
            imported_tickets = []
            
            for i, ext_ticket in enumerate(external_tickets):
                logger.info(f"Importing ticket {i+1}/{len(external_tickets)}: {ext_ticket['title']}")
                
                linear_ticket = await self.import_ticket(
                    ext_ticket,
                    linear_project['id'],
                    external_pm,
                    options
                )
                
                imported_tickets.append(linear_ticket)
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
                
            # 6. Generate project-level Mermaid diagrams
            if options['generate_mermaid']:
                logger.info(f"🎨 Generating project diagrams...")
                await self.generate_project_diagrams(
                    linear_project['id'],
                    imported_tickets
                )
                
            # 7. Set up bidirectional sync
            if options['enable_sync']:
                logger.info(f"🔄 Setting up bidirectional sync...")
                await self.sync_engine.setup_sync(
                    linear_project_id=linear_project['id'],
                    external_pm=external_pm,
                    external_project_id=project_id,
                    conflict_strategy=options['conflict_strategy']
                )
                
            logger.info(f"✅ Import complete: {len(imported_tickets)} tickets")
            
            return {
                'success': True,
                'linear_project': linear_project,
                'tickets_imported': len(imported_tickets),
                'sync_enabled': options['enable_sync'],
                'external_pm': external_pm,
                'external_project_id': project_id
            }
            
        except Exception as e:
            logger.error(f"❌ Import failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def import_ticket(
        self,
        external_ticket: Dict,
        linear_project_id: str,
        external_pm: str,
        options: Dict
    ) -> Dict:
        """Import single ticket with AI enhancement"""
        
        # 1. Translate to Linear format
        linear_ticket = self.translate_to_linear(external_ticket, external_pm)
        linear_ticket['project_id'] = linear_project_id
        
        # 2. AI Enhancement: Generate Mermaid diagram
        if options['generate_mermaid'] and external_ticket.get('description'):
            try:
                mermaid = await self.generate_mermaid_from_description(
                    title=external_ticket['title'],
                    description=external_ticket['description']
                )
                
                if mermaid:
                    linear_ticket['mermaid_diagram'] = mermaid
                    logger.info(f"✅ Generated Mermaid diagram for: {external_ticket['title']}")
                    
            except Exception as e:
                logger.warning(f"Failed to generate Mermaid: {e}")
                
        # 3. AI Enhancement: Enrich description
        if options['enrich_descriptions'] and external_ticket.get('description'):
            try:
                enriched = await self.enrich_description(
                    external_ticket['description']
                )
                
                if enriched:
                    linear_ticket['description'] = enriched
                    logger.info(f"✅ Enriched description for: {external_ticket['title']}")
                    
            except Exception as e:
                logger.warning(f"Failed to enrich description: {e}")
                
        # 4. Create in Linear
        created_ticket = await self.create_linear_ticket(linear_ticket)
        
        # 5. Store mapping (for sync)
        await self.store_ticket_mapping(
            linear_id=created_ticket['id'],
            external_id=external_ticket['id'],
            external_pm=external_pm
        )
        
        return created_ticket
        
    async def generate_mermaid_from_description(
        self,
        title: str,
        description: str
    ) -> Optional[str]:
        """Use AI to generate Mermaid diagram from ticket description"""
        
        prompt = f"""Analyze this feature ticket and generate a Mermaid flow diagram.

Title: {title}

Description:
{description}

Generate a clear, concise Mermaid diagram showing:
1. User flow
2. System components
3. Data flow
4. Decision points

Output ONLY the Mermaid code (graph TD format), no explanation or markdown fences.
Example format:
graph TD
    A[Start] --> B[Action]
    B --> C[Decision]
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language='mermaid',
                max_tokens=300,
                temperature=0.3
            )
            
            if result and len(result) > 0:
                mermaid = result[0].strip()
                
                # Validate it starts with graph
                if mermaid.startswith('graph '):
                    return mermaid
                    
        except Exception as e:
            logger.error(f"Error generating Mermaid: {e}")
            
        return None
        
    async def enrich_description(self, description: str) -> Optional[str]:
        """Use AI to enrich ticket description"""
        
        prompt = f"""Improve this ticket description by adding:
1. Clear acceptance criteria
2. Technical considerations
3. Potential edge cases

Original description:
{description}

Output the enriched description in markdown format.
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language='markdown',
                max_tokens=500,
                temperature=0.4
            )
            
            if result and len(result) > 0:
                return result[0].strip()
                
        except Exception as e:
            logger.error(f"Error enriching description: {e}")
            
        return None
        
    async def analyze_project_structure(
        self,
        tickets: List[Dict],
        external_pm: str
    ) -> Dict:
        """Analyze project structure from tickets"""
        
        # Extract project info
        structure = {
            'name': f"Imported from {external_pm}",
            'description': f"Project imported from {external_pm}",
            'total_tickets': len(tickets),
            'statuses': {},
            'priorities': {},
            'assignees': set(),
            'labels': set()
        }
        
        for ticket in tickets:
            # Count statuses
            status = ticket.get('status', 'unknown')
            structure['statuses'][status] = structure['statuses'].get(status, 0) + 1
            
            # Count priorities
            priority = ticket.get('priority', 'unknown')
            structure['priorities'][priority] = structure['priorities'].get(priority, 0) + 1
            
            # Collect assignees
            if ticket.get('assignee'):
                structure['assignees'].add(ticket['assignee'])
                
            # Collect labels
            for label in ticket.get('labels', []):
                structure['labels'].add(label)
                
        # Convert sets to lists
        structure['assignees'] = list(structure['assignees'])
        structure['labels'] = list(structure['labels'])
        
        return structure
        
    async def generate_project_diagrams(
        self,
        project_id: str,
        tickets: List[Dict]
    ):
        """Generate project-level Mermaid diagrams"""
        
        # Generate project roadmap diagram
        roadmap = await self.generate_roadmap_diagram(tickets)
        
        if roadmap:
            # Store as project documentation
            await self.store_project_diagram(
                project_id=project_id,
                diagram_type='roadmap',
                mermaid=roadmap
            )
            
    async def generate_roadmap_diagram(self, tickets: List[Dict]) -> Optional[str]:
        """Generate project roadmap Mermaid diagram"""
        
        # Group tickets by status
        by_status = {}
        for ticket in tickets:
            status = ticket.get('status', 'unknown')
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(ticket)
            
        # Generate Gantt chart
        mermaid = "gantt\n"
        mermaid += "    title Project Roadmap\n"
        mermaid += "    dateFormat YYYY-MM-DD\n"
        
        for status, status_tickets in by_status.items():
            mermaid += f"    section {status}\n"
            for ticket in status_tickets[:5]:  # Limit to 5 per status
                mermaid += f"    {ticket['title'][:30]} :2024-01-01, 7d\n"
                
        return mermaid
        
    def translate_to_linear(self, ticket: Dict, external_pm: str) -> Dict:
        """Translate external ticket to Linear format"""
        
        return {
            'title': ticket['title'],
            'description': ticket.get('description', ''),
            'status': self.map_status(ticket.get('status'), external_pm),
            'assignee': ticket.get('assignee'),
            'priority': self.map_priority(ticket.get('priority'), external_pm),
            'labels': ticket.get('labels', []),
            'external_id': ticket['id'],
            'external_pm': external_pm
        }
        
    def map_status(self, status: Optional[str], external_pm: str) -> str:
        """Map external status to Linear status"""
        
        status_map = {
            'jira': {
                'To Do': 'todo',
                'In Progress': 'in_progress',
                'In Review': 'in_review',
                'Done': 'done'
            },
            'github': {
                'open': 'todo',
                'closed': 'done'
            }
        }
        
        pm_map = status_map.get(external_pm, {})
        return pm_map.get(status, 'todo')
        
    def map_priority(self, priority: Optional[Any], external_pm: str) -> int:
        """Map external priority to Linear priority (0-4)"""
        
        if not priority:
            return 2  # Medium
            
        priority_map = {
            'jira': {
                'Highest': 4,
                'High': 3,
                'Medium': 2,
                'Low': 1,
                'Lowest': 0
            }
        }
        
        pm_map = priority_map.get(external_pm, {})
        
        if isinstance(priority, str):
            return pm_map.get(priority, 2)
        elif isinstance(priority, int):
            return min(priority, 4)
            
        return 2
        
    async def create_linear_project(
        self,
        name: str,
        description: str,
        team_id: str,
        codebase_id: str
    ) -> Dict:
        """Create Linear project"""
        # TODO: Implement Linear API call
        logger.info(f"Creating Linear project: {name}")
        
        return {
            'id': f"linear_project_{team_id}_{codebase_id}",
            'name': name,
            'description': description,
            'team_id': team_id,
            'codebase_id': codebase_id,
            'created_at': datetime.now().isoformat()
        }
        
    async def create_linear_ticket(self, ticket: Dict) -> Dict:
        """Create Linear ticket"""
        # TODO: Implement Linear API call
        logger.info(f"Creating Linear ticket: {ticket['title']}")
        
        return {
            'id': f"linear_ticket_{ticket['external_id']}",
            **ticket,
            'created_at': datetime.now().isoformat()
        }
        
    async def store_ticket_mapping(
        self,
        linear_id: str,
        external_id: str,
        external_pm: str
    ):
        """Store ticket mapping for sync"""
        # TODO: Store in database
        logger.info(f"Storing mapping: {linear_id} ↔ {external_id}")
        
    async def store_project_diagram(
        self,
        project_id: str,
        diagram_type: str,
        mermaid: str
    ):
        """Store project-level diagram"""
        # TODO: Store in database
        logger.info(f"Storing {diagram_type} diagram for project {project_id}")


# Global importer instance
_project_importer = ProjectImporter()


def get_project_importer() -> ProjectImporter:
    """Get global project importer instance"""
    return _project_importer
