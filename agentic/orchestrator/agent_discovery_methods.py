"""
Agent Discovery Methods for Meta-Orchestrator
These methods enable self-aware agent discovery and intelligent routing
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def discover_agents_mixin(self):
    """
    Mixin methods for agent discovery in MetaOrchestrator
    Add these methods to the MetaOrchestrator class
    """
    
    def _discover_agents(self):
        """
        Self-Discovery: Dynamically discover all available agents
        
        This makes the orchestrator self-aware of its capabilities.
        It can adapt to new agents being added without code changes.
        """
        try:
            from agents.discovery import discover_all_agents, get_agent_count, get_total_agent_count
            
            logger.info("🔍 Meta-Orchestrator discovering available agents...")
            
            # Discover all agents dynamically
            agents_by_category = discover_all_agents()
            agent_counts = get_agent_count()
            total_count = get_total_agent_count()
            
            # Build agent capability map for intelligent routing
            self.agent_cache = {}
            self.agent_capabilities_map = {}
            self.category_map = {}
            
            for category, agent_list in agents_by_category.items():
                self.category_map[category] = []
                for agent in agent_list:
                    agent_id = agent['id']
                    self.agent_cache[agent_id] = agent
                    self.category_map[category].append(agent_id)
                    
                    # Map capabilities to agents for smart routing
                    for capability in agent.get('capabilities', []):
                        if capability not in self.agent_capabilities_map:
                            self.agent_capabilities_map[capability] = []
                        self.agent_capabilities_map[capability].append(agent_id)
            
            self.last_discovery_time = datetime.utcnow()
            
            logger.info(f"✅ Discovered {total_count} agents across {len(agents_by_category)} categories")
            logger.info(f"📊 Categories: {', '.join(agents_by_category.keys())}")
            logger.info(f"🎯 Capabilities mapped: {len(self.agent_capabilities_map)}")
            
        except Exception as e:
            logger.error(f"❌ Agent discovery failed: {e}")
            self.agent_cache = {}
            self.agent_capabilities_map = {}
            self.category_map = {}
    
    def refresh_agent_discovery(self):
        """Refresh agent discovery (useful when new agents are added)"""
        logger.info("🔄 Refreshing agent discovery...")
        self._discover_agents()
    
    def get_agents_by_capability(self, capability: str) -> List[str]:
        """
        Find agents that have a specific capability
        
        This enables the orchestrator to intelligently select agents
        based on what the user needs, not just by category.
        
        Example:
            agents = orchestrator.get_agents_by_capability("Trading")
            # Returns: ['trading', 'forex', 'stocks', 'options', 'futures']
        """
        capability_lower = capability.lower()
        matching_agents = []
        
        # Exact match
        for cap, agents in self.agent_capabilities_map.items():
            if cap.lower() == capability_lower:
                matching_agents.extend(agents)
        
        # Partial match if no exact match
        if not matching_agents:
            for cap, agents in self.agent_capabilities_map.items():
                if capability_lower in cap.lower():
                    matching_agents.extend(agents)
        
        return list(set(matching_agents))  # Remove duplicates
    
    def get_agents_by_category(self, category: str) -> List[str]:
        """
        Get all agents in a specific category
        
        Example:
            agents = orchestrator.get_agents_by_category("finance")
            # Returns: ['ledger', 'tax', 'trading', 'portfolio', ...]
        """
        return self.category_map.get(category.lower(), [])
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific agent
        
        Returns:
            {
                'id': 'ledger',
                'name': 'Ledger Agent',
                'description': 'Accounting and bookkeeping',
                'category': 'Finance',
                'capabilities': ['Transaction Categorization', 'P&L Reports'],
                'icon': 'book-outline'
            }
        """
        return self.agent_cache.get(agent_id)
    
    def find_best_agent_for_task(self, task_description: str) -> Optional[str]:
        """
        Intelligently find the best agent for a given task
        
        Uses capability matching and keyword analysis to select
        the most appropriate agent.
        
        Example:
            agent_id = orchestrator.find_best_agent_for_task("analyze my spending")
            # Returns: 'ledger' or 'budget'
        """
        task_lower = task_description.lower()
        
        # Try capability matching first
        for capability, agents in self.agent_capabilities_map.items():
            if capability.lower() in task_lower:
                return agents[0] if agents else None
        
        # Try category matching
        for category, agents in self.category_map.items():
            if category in task_lower:
                return agents[0] if agents else None
        
        # Try agent name matching
        for agent_id, agent_info in self.agent_cache.items():
            if agent_id in task_lower or agent_info['name'].lower() in task_lower:
                return agent_id
        
        return None
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """
        Get statistics about discovered agents
        
        Returns:
            {
                'total_agents': 137,
                'categories': 15,
                'capabilities': 200,
                'last_discovery': '2025-10-28T14:30:00',
                'by_category': {'finance': 20, 'communication': 5, ...}
            }
        """
        return {
            'total_agents': len(self.agent_cache),
            'categories': len(self.category_map),
            'capabilities': len(self.agent_capabilities_map),
            'last_discovery': self.last_discovery_time.isoformat() if self.last_discovery_time else None,
            'by_category': {cat: len(agents) for cat, agents in self.category_map.items()}
        }
