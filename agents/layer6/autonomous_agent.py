"""
Base class for Layer 6 Autonomous Agents

Autonomous agents can take actions without human approval.
They monitor the system, detect issues, and fix them automatically.
"""

from abc import abstractmethod
from typing import Dict, Any
from ..base import BaseAgent, AgentResult


class Layer6Agent(BaseAgent):
    """
    Base class for Layer 6 Autonomous Agents
    
    Key characteristics:
    - Can take actions WITHOUT human approval
    - Monitors system continuously
    - Self-healing and proactive
    - Learns from actions
    - Has safety constraints
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.autonomous_mode = True
        self.safety_checks_enabled = True
    
    @abstractmethod
    async def monitor(self) -> AgentResult:
        """Monitor system for issues or opportunities"""
        pass
    
    @abstractmethod
    async def decide(self, situation: Dict[str, Any]) -> AgentResult:
        """Decide what action to take (if any)"""
        pass
    
    @abstractmethod
    async def act(self, decision: Dict[str, Any]) -> AgentResult:
        """Take autonomous action"""
        pass
    
    @abstractmethod
    async def verify(self, action_result: Dict[str, Any]) -> AgentResult:
        """Verify action was successful"""
        pass
    
    async def execute_autonomous_cycle(self) -> AgentResult:
        """
        Execute full autonomous cycle:
        1. Monitor
        2. Decide
        3. Act
        4. Verify
        """
        # Monitor
        monitor_result = await self.monitor()
        if not monitor_result.success:
            return monitor_result
        
        # Decide
        decision_result = await self.decide(monitor_result.data)
        if not decision_result.success or not decision_result.data.get('should_act'):
            return decision_result
        
        # Safety check
        if self.safety_checks_enabled:
            safety_check = await self._safety_check(decision_result.data)
            if not safety_check:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'reason': 'Failed safety check'}
                )
        
        # Act
        action_result = await self.act(decision_result.data)
        if not action_result.success:
            return action_result
        
        # Verify
        verify_result = await self.verify(action_result.data)
        
        # Learn from action
        if self.kg_client:
            await self._record_action(decision_result.data, action_result.data, verify_result.data)
        
        return verify_result
    
    async def _safety_check(self, decision: Dict[str, Any]) -> bool:
        """
        Safety check before taking action
        Override in subclasses for specific safety rules
        """
        # Default: Allow all actions
        # Subclasses should implement specific safety rules
        return True
    
    async def _record_action(self, decision: Dict[str, Any], action: Dict[str, Any], result: Dict[str, Any]):
        """Record action in knowledge graph for learning"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="autonomous_action",
            data={
                'agent': self.metadata.name,
                'decision': decision,
                'action': action,
                'result': result,
                'success': result.get('success', False)
            },
            graph_type="workflow"
        )
