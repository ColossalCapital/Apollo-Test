"""
Base class for Layer 7 Swarm Intelligence Agents

Swarm agents coordinate multiple agents to solve complex problems.
"""

from abc import abstractmethod
from typing import Dict, Any, List
from ..base import BaseAgent, AgentResult


class Layer7Agent(BaseAgent):
    """
    Base class for Layer 7 Swarm Intelligence Agents
    
    Key characteristics:
    - Coordinates multiple agents
    - Distributed problem-solving
    - Consensus decision-making
    - Emergent intelligence
    - Parallel execution
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.agent_registry = {}
    
    @abstractmethod
    async def decompose(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose complex task into subtasks"""
        pass
    
    @abstractmethod
    async def assign(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assign subtasks to appropriate agents"""
        pass
    
    @abstractmethod
    async def coordinate(self, assignments: Dict[str, Any]) -> AgentResult:
        """Coordinate execution of subtasks"""
        pass
    
    @abstractmethod
    async def merge(self, results: List[AgentResult]) -> AgentResult:
        """Merge results from multiple agents"""
        pass
    
    async def execute_swarm(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute full swarm intelligence cycle:
        1. Decompose task
        2. Assign to agents
        3. Coordinate execution
        4. Merge results
        """
        # Decompose
        subtasks = await self.decompose(task)
        
        # Assign
        assignments = await self.assign(subtasks)
        
        # Coordinate
        execution_result = await self.coordinate(assignments)
        
        if not execution_result.success:
            return execution_result
        
        # Merge
        results = execution_result.data.get('results', [])
        merged_result = await self.merge(results)
        
        # Learn from swarm execution
        if self.kg_client:
            await self._record_swarm_execution(task, subtasks, results, merged_result)
        
        return merged_result
    
    async def _record_swarm_execution(self, task: Dict[str, Any], subtasks: List[Dict[str, Any]], 
                                     results: List[AgentResult], merged_result: AgentResult):
        """Record swarm execution for learning"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="swarm_execution",
            data={
                'agent': self.metadata.name,
                'task': task,
                'subtasks': subtasks,
                'num_agents': len(results),
                'success': merged_result.success
            },
            graph_type="workflow"
        )
