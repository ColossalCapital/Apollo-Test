"""
Core Agent - Central routing and orchestration
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent


class CoreAgent(BaseAgent):
    """Core orchestration agent for multi-agent workflows"""
    
    def __init__(self):
        super().__init__(
            name="Core Agent",
            description="Central orchestration and routing for complex multi-agent workflows",
            capabilities=["Agent Routing", "Workflow Orchestration", "Context Management", "Multi-Agent Coordination"]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process core orchestration requests"""
        query_type = data.get('query_type', 'general')
        
        if query_type == 'route':
            return {
                'status': 'success',
                'message': 'Routing to appropriate agent',
                'suggested_agent': self._suggest_agent(data.get('query', ''))
            }
        elif query_type == 'orchestrate':
            return {
                'status': 'success',
                'message': 'Orchestrating multi-agent workflow',
                'workflow': self._create_workflow(data.get('task', ''))
            }
        else:
            return {
                'status': 'success',
                'message': 'Core agent ready for orchestration tasks'
            }
    
    def _suggest_agent(self, query: str) -> str:
        """Suggest appropriate agent based on query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['invoice', 'ledger', 'accounting']):
            return 'ledger'
        elif any(word in query_lower for word in ['trade', 'stock', 'portfolio']):
            return 'trading'
        elif any(word in query_lower for word in ['email', 'message']):
            return 'email'
        else:
            return 'router'
    
    def _create_workflow(self, task: str) -> Dict[str, Any]:
        """Create multi-agent workflow"""
        return {
            'steps': [
                {'agent': 'router', 'action': 'analyze_task'},
                {'agent': 'appropriate_agent', 'action': 'process_task'},
                {'agent': 'router', 'action': 'aggregate_results'}
            ],
            'estimated_time': '2-5 seconds'
        }
