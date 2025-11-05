"""
Ticket Refinement Agent

Analyzes tickets and ensures they have enough information for AI development.

Features:
- Analyzes ticket completeness
- Asks clarifying questions
- Generates Mermaid diagrams
- Enriches descriptions
- Understands "use your best judgment"
- Learns from project context
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from learning.deepseek_coder import DeepSeekCoder
from learning.agentic_codebase_rag import get_agentic_rag

logger = logging.getLogger(__name__)


class TicketRefinementAgent:
    """
    Ensures tickets are properly scoped before development
    
    Workflow:
    1. Analyze ticket completeness
    2. Ask clarifying questions (if needed)
    3. Generate Mermaid diagram
    4. Enrich description
    5. Mark as "Ready for Development"
    """
    
    def __init__(self):
        self.deepseek = DeepSeekCoder(model_size="6.7b")
        
    async def analyze_ticket(
        self,
        ticket: Dict,
        codebase_id: str,
        project_context: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze ticket and determine if it's ready for development
        
        Returns:
            {
                'ready': bool,
                'completeness_score': float,  # 0-100
                'missing_info': List[str],
                'clarifying_questions': List[str],
                'suggested_improvements': Dict
            }
        """
        
        logger.info(f"🔍 Analyzing ticket: {ticket['title']}")
        
        # Get project context from Agentic RAG
        if not project_context:
            agentic_rag = get_agentic_rag(codebase_id)
            project_context = await agentic_rag.get_current_state()
            
        # Analyze completeness
        analysis = await self._analyze_completeness(ticket, project_context)
        
        # Generate clarifying questions
        if analysis['completeness_score'] < 80:
            questions = await self._generate_questions(ticket, analysis, project_context)
            analysis['clarifying_questions'] = questions
            
        # Suggest improvements
        improvements = await self._suggest_improvements(ticket, project_context)
        analysis['suggested_improvements'] = improvements
        
        return analysis
        
    async def _analyze_completeness(
        self,
        ticket: Dict,
        project_context: Dict
    ) -> Dict:
        """Analyze how complete the ticket is"""
        
        score = 0
        missing = []
        
        # Check title (10 points)
        if ticket.get('title') and len(ticket['title']) > 10:
            score += 10
        else:
            missing.append('clear_title')
            
        # Check description (20 points)
        if ticket.get('description') and len(ticket['description']) > 50:
            score += 20
        else:
            missing.append('detailed_description')
            
        # Check acceptance criteria (20 points)
        if 'acceptance_criteria' in ticket.get('description', '').lower():
            score += 20
        else:
            missing.append('acceptance_criteria')
            
        # Check Mermaid diagram (20 points)
        if ticket.get('mermaid_diagram'):
            score += 20
        else:
            missing.append('mermaid_diagram')
            
        # Check technical details (15 points)
        tech_keywords = ['api', 'endpoint', 'component', 'function', 'database', 'ui']
        if any(kw in ticket.get('description', '').lower() for kw in tech_keywords):
            score += 15
        else:
            missing.append('technical_details')
            
        # Check context/location (15 points)
        location_keywords = ['screen', 'page', 'component', 'file', 'module']
        if any(kw in ticket.get('description', '').lower() for kw in location_keywords):
            score += 15
        else:
            missing.append('location_context')
            
        return {
            'completeness_score': score,
            'missing_info': missing,
            'ready': score >= 80
        }
        
    async def _generate_questions(
        self,
        ticket: Dict,
        analysis: Dict,
        project_context: Dict
    ) -> List[Dict]:
        """Generate clarifying questions based on missing info"""
        
        questions = []
        
        # Build prompt for AI
        prompt = f"""Analyze this ticket and generate clarifying questions.

Ticket Title: {ticket['title']}
Description: {ticket.get('description', 'No description provided')}

Project Context:
- Type: {project_context.get('type', 'unknown')}
- Tech Stack: {', '.join(project_context.get('tech_stack', []))}
- Current Features: {', '.join(project_context.get('features', [])[:5])}

Missing Information: {', '.join(analysis['missing_info'])}

Generate 3-5 specific clarifying questions that would help fully scope this ticket.
For each question, include:
1. The question
2. Why it's important
3. Suggested default answer (if applicable)

Format as JSON array:
[
  {{
    "question": "Where should this dashboard be displayed?",
    "importance": "Determines which component to modify",
    "suggested_default": "Entity detail screen",
    "allow_ai_judgment": true
  }}
]
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language='json',
                max_tokens=500,
                temperature=0.4
            )
            
            if result and len(result) > 0:
                import json
                questions = json.loads(result[0])
                
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            # Fallback to template questions
            questions = self._get_template_questions(analysis['missing_info'])
            
        return questions
        
    def _get_template_questions(self, missing_info: List[str]) -> List[Dict]:
        """Template questions based on missing info"""
        
        templates = {
            'location_context': {
                'question': 'Where should this feature be implemented?',
                'importance': 'Determines which files/components to modify',
                'suggested_default': None,
                'allow_ai_judgment': True
            },
            'technical_details': {
                'question': 'What technical approach should be used?',
                'importance': 'Ensures correct implementation',
                'suggested_default': 'Use existing patterns in the codebase',
                'allow_ai_judgment': True
            },
            'acceptance_criteria': {
                'question': 'What are the acceptance criteria?',
                'importance': 'Defines when the feature is complete',
                'suggested_default': None,
                'allow_ai_judgment': False
            },
            'mermaid_diagram': {
                'question': 'Should I generate a flow diagram?',
                'importance': 'Visualizes the feature flow',
                'suggested_default': 'Yes, generate based on description',
                'allow_ai_judgment': True
            }
        }
        
        return [templates[info] for info in missing_info if info in templates]
        
    async def _suggest_improvements(
        self,
        ticket: Dict,
        project_context: Dict
    ) -> Dict:
        """Suggest improvements to the ticket"""
        
        improvements = {}
        
        # Suggest Mermaid diagram
        if not ticket.get('mermaid_diagram'):
            mermaid = await self._generate_mermaid(ticket, project_context)
            if mermaid:
                improvements['mermaid_diagram'] = mermaid
                
        # Suggest enhanced description
        if ticket.get('description'):
            enhanced = await self._enhance_description(ticket, project_context)
            if enhanced:
                improvements['enhanced_description'] = enhanced
                
        # Suggest acceptance criteria
        if 'acceptance_criteria' not in ticket.get('description', '').lower():
            criteria = await self._generate_acceptance_criteria(ticket, project_context)
            if criteria:
                improvements['acceptance_criteria'] = criteria
                
        return improvements
        
    async def _generate_mermaid(
        self,
        ticket: Dict,
        project_context: Dict
    ) -> Optional[str]:
        """Generate Mermaid diagram from ticket description"""
        
        prompt = f"""Generate a Mermaid flow diagram for this feature.

Title: {ticket['title']}
Description: {ticket.get('description', '')}

Project Type: {project_context.get('type', 'web app')}

Generate a clear, concise Mermaid diagram showing:
1. User flow
2. System components
3. Data flow
4. Decision points

Output ONLY the Mermaid code (graph TD format), no explanation.
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
                if mermaid.startswith('graph '):
                    return mermaid
                    
        except Exception as e:
            logger.error(f"Failed to generate Mermaid: {e}")
            
        return None
        
    async def _enhance_description(
        self,
        ticket: Dict,
        project_context: Dict
    ) -> Optional[str]:
        """Enhance ticket description with more details"""
        
        prompt = f"""Enhance this ticket description with technical details.

Original Description:
{ticket.get('description', '')}

Project Context:
- Type: {project_context.get('type')}
- Tech Stack: {', '.join(project_context.get('tech_stack', []))}

Add:
1. Technical approach
2. Components to modify
3. Potential edge cases
4. Testing considerations

Keep the original intent, just add helpful technical details.
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language='markdown',
                max_tokens=400,
                temperature=0.4
            )
            
            if result and len(result) > 0:
                return result[0].strip()
                
        except Exception as e:
            logger.error(f"Failed to enhance description: {e}")
            
        return None
        
    async def _generate_acceptance_criteria(
        self,
        ticket: Dict,
        project_context: Dict
    ) -> Optional[List[str]]:
        """Generate acceptance criteria"""
        
        prompt = f"""Generate acceptance criteria for this feature.

Title: {ticket['title']}
Description: {ticket.get('description', '')}

Generate 3-5 clear, testable acceptance criteria.
Format as a list:
- [ ] Criterion 1
- [ ] Criterion 2
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language='markdown',
                max_tokens=200,
                temperature=0.3
            )
            
            if result and len(result) > 0:
                # Parse criteria
                criteria = []
                for line in result[0].split('\n'):
                    if line.strip().startswith('- [ ]'):
                        criteria.append(line.strip()[6:])
                return criteria
                
        except Exception as e:
            logger.error(f"Failed to generate criteria: {e}")
            
        return None
        
    async def refine_ticket_interactive(
        self,
        ticket: Dict,
        codebase_id: str,
        user_responses: Optional[Dict] = None
    ) -> Dict:
        """
        Interactively refine ticket with user
        
        Args:
            ticket: Original ticket
            codebase_id: Codebase ID
            user_responses: User's answers to questions
            
        Returns:
            Refined ticket with all improvements
        """
        
        logger.info(f"🎯 Refining ticket: {ticket['title']}")
        
        # Get project context
        agentic_rag = get_agentic_rag(codebase_id)
        project_context = await agentic_rag.get_current_state()
        
        # Analyze ticket
        analysis = await self.analyze_ticket(ticket, codebase_id, project_context)
        
        # If user provided responses, apply them
        if user_responses:
            ticket = await self._apply_user_responses(
                ticket,
                analysis,
                user_responses,
                project_context
            )
            
        # Apply AI improvements
        if analysis['suggested_improvements']:
            ticket = await self._apply_improvements(
                ticket,
                analysis['suggested_improvements']
            )
            
        # Mark as ready if complete
        if analysis['completeness_score'] >= 80:
            ticket['status'] = 'ready_for_development'
            ticket['refined_at'] = datetime.now().isoformat()
            ticket['refined_by'] = 'ai'
            
        return {
            'ticket': ticket,
            'analysis': analysis,
            'ready': analysis['ready']
        }
        
    async def _apply_user_responses(
        self,
        ticket: Dict,
        analysis: Dict,
        user_responses: Dict,
        project_context: Dict
    ) -> Dict:
        """Apply user's responses to questions"""
        
        # Build enhanced description
        enhanced_parts = [ticket.get('description', '')]
        
        for question_id, response in user_responses.items():
            if response == 'use_ai_judgment':
                # AI decides based on project context
                ai_decision = await self._make_ai_decision(
                    question_id,
                    ticket,
                    project_context
                )
                enhanced_parts.append(f"\n\n**{question_id}:** {ai_decision} (AI decision)")
            else:
                # Use user's response
                enhanced_parts.append(f"\n\n**{question_id}:** {response}")
                
        ticket['description'] = '\n'.join(enhanced_parts)
        
        return ticket
        
    async def _make_ai_decision(
        self,
        question: str,
        ticket: Dict,
        project_context: Dict
    ) -> str:
        """AI makes decision when user says "use your best judgment" """
        
        prompt = f"""Make the best decision for this question based on project context.

Question: {question}

Ticket: {ticket['title']}
Description: {ticket.get('description', '')}

Project Context:
- Type: {project_context.get('type')}
- Tech Stack: {', '.join(project_context.get('tech_stack', []))}
- Existing Patterns: {', '.join(project_context.get('patterns', [])[:3])}

Provide a specific, actionable decision that follows best practices and existing patterns.
"""
        
        try:
            result = await self.deepseek.complete_code(
                code=prompt,
                position=len(prompt),
                language='markdown',
                max_tokens=150,
                temperature=0.3
            )
            
            if result and len(result) > 0:
                return result[0].strip()
                
        except Exception as e:
            logger.error(f"Failed to make AI decision: {e}")
            
        return "Follow existing patterns in the codebase"
        
    async def _apply_improvements(
        self,
        ticket: Dict,
        improvements: Dict
    ) -> Dict:
        """Apply suggested improvements to ticket"""
        
        if 'mermaid_diagram' in improvements:
            ticket['mermaid_diagram'] = improvements['mermaid_diagram']
            
        if 'enhanced_description' in improvements:
            ticket['description'] = improvements['enhanced_description']
            
        if 'acceptance_criteria' in improvements:
            criteria_text = '\n\n## Acceptance Criteria\n'
            for criterion in improvements['acceptance_criteria']:
                criteria_text += f'- [ ] {criterion}\n'
            ticket['description'] += criteria_text
            
        return ticket


# Global instance
_ticket_refinement_agent = TicketRefinementAgent()


def get_ticket_refinement_agent() -> TicketRefinementAgent:
    """Get global ticket refinement agent"""
    return _ticket_refinement_agent
