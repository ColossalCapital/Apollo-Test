"""
Project Plan Generator

Generate Linear project plans from indexed codebases.

Features:
- Analyze codebase structure
- Compare to project goals
- Identify incomplete features
- Detect technical debt
- Generate prioritized tickets
- Create Linear project
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import openai

from learning.codebase_indexer import get_codebase_indexer

logger = logging.getLogger(__name__)


class ProjectPlanGenerator:
    """
    Generate project plans from codebase analysis
    
    Workflow:
    1. Get codebase context from RAG
    2. Analyze current state
    3. Compare to project goals
    4. Generate ticket list
    5. Prioritize tickets
    6. Create Linear project
    """
    
    def __init__(self):
        self.indexer = get_codebase_indexer()
        
    async def generate_plan(
        self,
        codebase_id: str,
        project_goals: str,
        user_id: str,
        org_id: str
    ) -> Dict:
        """
        Generate project plan
        
        Args:
            codebase_id: Indexed codebase ID
            project_goals: Project goals/requirements
            user_id: User ID
            org_id: Organization ID
            
        Returns:
            {
                'success': bool,
                'tickets': List[Dict],
                'summary': str,
                'priorities': Dict
            }
        """
        
        logger.info(f"📋 Generating project plan for: {codebase_id}")
        
        try:
            # 1. Get codebase context
            codebase_context = await self._get_codebase_context(codebase_id)
            logger.info(f"Got codebase context: {codebase_context['stats']}")
            
            # 2. Analyze current state
            current_state = await self._analyze_current_state(codebase_context)
            logger.info(f"Current state: {current_state['summary']}")
            
            # 3. Generate tickets
            tickets = await self._generate_tickets(
                codebase_context,
                current_state,
                project_goals
            )
            logger.info(f"Generated {len(tickets)} tickets")
            
            # 4. Prioritize tickets
            prioritized = await self._prioritize_tickets(tickets, project_goals)
            logger.info(f"Prioritized tickets")
            
            # 5. Detect dependencies
            dependencies = await self._detect_dependencies(prioritized)
            logger.info(f"Detected {len(dependencies)} dependencies")
            
            # 6. Generate summary
            summary = await self._generate_summary(
                codebase_context,
                current_state,
                prioritized
            )
            
            return {
                'success': True,
                'tickets': prioritized,
                'dependencies': dependencies,
                'summary': summary,
                'codebase_context': codebase_context,
                'current_state': current_state
            }
            
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def _get_codebase_context(self, codebase_id: str) -> Dict:
        """Get codebase context from RAG"""
        
        # TODO: Query Theta RAG for codebase context
        # For now, return mock data
        
        return {
            'codebase_id': codebase_id,
            'stats': {
                'total_files': 150,
                'total_lines': 15000,
                'languages': {'python': 100, 'typescript': 50},
                'classes': 50,
                'functions': 200
            },
            'structure': {
                'has_backend': True,
                'has_frontend': True,
                'has_tests': True,
                'has_docs': False
            },
            'patterns': [
                'REST API',
                'React Framework',
                'Test Coverage'
            ]
        }
        
    async def _analyze_current_state(self, codebase_context: Dict) -> Dict:
        """Analyze current state of codebase"""
        
        stats = codebase_context['stats']
        structure = codebase_context['structure']
        
        # Calculate completeness
        completeness = 0
        if structure.get('has_backend'):
            completeness += 30
        if structure.get('has_frontend'):
            completeness += 30
        if structure.get('has_tests'):
            completeness += 20
        if structure.get('has_docs'):
            completeness += 20
            
        # Identify gaps
        gaps = []
        if not structure.get('has_docs'):
            gaps.append('Missing documentation')
        if stats.get('total_files', 0) < 50:
            gaps.append('Small codebase - needs more features')
        if 'Test Coverage' not in codebase_context.get('patterns', []):
            gaps.append('Low test coverage')
            
        return {
            'completeness': completeness,
            'gaps': gaps,
            'summary': f"{completeness}% complete, {len(gaps)} gaps identified"
        }
        
    async def _generate_tickets(
        self,
        codebase_context: Dict,
        current_state: Dict,
        project_goals: str
    ) -> List[Dict]:
        """Generate tickets using AI"""
        
        prompt = f"""Generate project tickets for this codebase.

Codebase Context:
- Files: {codebase_context['stats']['total_files']}
- Lines: {codebase_context['stats']['total_lines']}
- Languages: {', '.join(codebase_context['stats']['languages'].keys())}
- Patterns: {', '.join(codebase_context['patterns'])}

Current State:
- Completeness: {current_state['completeness']}%
- Gaps: {', '.join(current_state['gaps'])}

Project Goals:
{project_goals}

Generate 20-30 tickets to achieve the project goals.
For each ticket, provide:
1. Title (clear, actionable)
2. Description (detailed requirements)
3. Type (feature, bug, tech_debt, docs)
4. Priority (critical, high, medium, low)
5. Estimated hours

Format as JSON array:
[
  {{
    "title": "Add user authentication",
    "description": "Implement JWT-based authentication...",
    "type": "feature",
    "priority": "critical",
    "estimated_hours": 8
  }}
]
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a project planning expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            import json
            tickets = json.loads(response.choices[0].message.content)
            
            # Add IDs
            for i, ticket in enumerate(tickets):
                ticket['id'] = f"ticket_{i+1}"
                
            return tickets
            
        except Exception as e:
            logger.error(f"Failed to generate tickets: {e}")
            
            # Fallback: Generate basic tickets
            return self._generate_fallback_tickets(current_state)
            
    def _generate_fallback_tickets(self, current_state: Dict) -> List[Dict]:
        """Generate basic tickets as fallback"""
        
        tickets = []
        
        # Generate tickets for each gap
        for i, gap in enumerate(current_state['gaps']):
            tickets.append({
                'id': f"ticket_{i+1}",
                'title': f"Fix: {gap}",
                'description': f"Address the gap: {gap}",
                'type': 'tech_debt',
                'priority': 'high',
                'estimated_hours': 4
            })
            
        return tickets
        
    async def _prioritize_tickets(
        self,
        tickets: List[Dict],
        project_goals: str
    ) -> List[Dict]:
        """Prioritize tickets"""
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        sorted_tickets = sorted(
            tickets,
            key=lambda t: priority_order.get(t.get('priority', 'medium'), 2)
        )
        
        return sorted_tickets
        
    async def _detect_dependencies(self, tickets: List[Dict]) -> Dict:
        """Detect dependencies between tickets"""
        
        dependencies = {}
        
        # Simple heuristic: Authentication tickets must come first
        auth_tickets = [t for t in tickets if 'auth' in t['title'].lower()]
        other_tickets = [t for t in tickets if 'auth' not in t['title'].lower()]
        
        if auth_tickets:
            auth_id = auth_tickets[0]['id']
            for ticket in other_tickets:
                if 'user' in ticket['title'].lower():
                    dependencies[ticket['id']] = [auth_id]
                    
        return dependencies
        
    async def _generate_summary(
        self,
        codebase_context: Dict,
        current_state: Dict,
        tickets: List[Dict]
    ) -> str:
        """Generate project plan summary"""
        
        total_hours = sum(t.get('estimated_hours', 0) for t in tickets)
        
        by_priority = {}
        for ticket in tickets:
            priority = ticket.get('priority', 'medium')
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
        summary = f"""# Project Plan Summary

## Current State
- Completeness: {current_state['completeness']}%
- Gaps: {len(current_state['gaps'])}

## Generated Plan
- Total Tickets: {len(tickets)}
- Estimated Hours: {total_hours}
- Estimated Weeks: {total_hours / 40:.1f}

## By Priority
- Critical: {by_priority.get('critical', 0)}
- High: {by_priority.get('high', 0)}
- Medium: {by_priority.get('medium', 0)}
- Low: {by_priority.get('low', 0)}

## Next Steps
1. Review tickets
2. Adjust priorities if needed
3. Create Linear project
4. Start development!
"""
        
        return summary


# Global instance
_project_plan_generator = ProjectPlanGenerator()


def get_project_plan_generator() -> ProjectPlanGenerator:
    """Get global project plan generator"""
    return _project_plan_generator
