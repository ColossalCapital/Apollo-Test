"""
Apollo Agent Factory

Factory for creating and managing agent instances with dependency injection.

Usage:
    from agents.factory import AgentFactory
    from knowledge_graph import get_knowledge_graph
    
    kg = await get_knowledge_graph()
    factory = AgentFactory(kg_client=kg)
    
    # Create agents
    meeting_agent = factory.create("meeting_orchestrator")
    research_agent = factory.create("research")
    
    # Create with dependencies
    workflow = factory.create_workflow("meeting_orchestrator")
"""

from typing import Dict, Optional, Any, List
import logging

from .base import (
    Layer1Agent, Layer2Agent, Layer3Agent, Layer4Agent, Layer5Agent,
    AgentLayer
)
from .registry import AgentRegistry, get_registry

logger = logging.getLogger(__name__)


# ============================================================================
# AGENT FACTORY
# ============================================================================

class AgentFactory:
    """
    Factory for creating agent instances with dependency injection
    
    Handles:
    - Agent instantiation
    - Dependency injection (KG client, other agents)
    - Agent caching (reuse instances)
    - Dependency resolution
    """
    
    def __init__(
        self,
        kg_client=None,
        cache_agents: bool = True
    ):
        """
        Initialize agent factory
        
        Args:
            kg_client: Neo4j knowledge graph client
            cache_agents: Whether to cache agent instances
        """
        self.kg = kg_client
        self.cache_agents = cache_agents
        self.registry = get_registry()
        
        # Cache of instantiated agents
        self._agent_cache: Dict[str, Any] = {}
        
        logger.info(f"AgentFactory initialized (caching={cache_agents})")
    
    def create(
        self,
        agent_name: str,
        layer: Optional[AgentLayer] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Create an agent instance
        
        Args:
            agent_name: Name of the agent
            layer: Optional layer hint (speeds up lookup)
            **kwargs: Additional arguments for agent constructor
            
        Returns:
            Agent instance or None if not found
            
        Example:
            agent = factory.create("meeting_orchestrator")
            agent = factory.create("research", layer=AgentLayer.LAYER_3_DOMAIN)
        """
        # Check cache first
        if self.cache_agents and agent_name in self._agent_cache:
            logger.debug(f"Returning cached agent: {agent_name}")
            return self._agent_cache[agent_name]
        
        # Find agent in registry
        entry = None
        if layer:
            entry = self.registry.get_agent_entry(layer, agent_name)
        else:
            # Search all layers
            for check_layer in AgentLayer:
                entry = self.registry.get_agent_entry(check_layer, agent_name)
                if entry:
                    layer = check_layer
                    break
        
        if not entry:
            logger.error(f"Agent not found: {agent_name}")
            return None
        
        # Create instance based on layer
        agent = self._instantiate_agent(entry.agent_class, layer, **kwargs)
        
        # Cache if enabled
        if self.cache_agents and agent:
            self._agent_cache[agent_name] = agent
        
        logger.info(f"Created agent: {agent_name} (layer={layer.name})")
        return agent
    
    def _instantiate_agent(
        self,
        agent_class: type,
        layer: AgentLayer,
        **kwargs
    ) -> Optional[Any]:
        """Instantiate agent based on layer"""
        try:
            if layer == AgentLayer.LAYER_1_EXTRACTION:
                # Layer 1 agents don't need dependencies
                return agent_class(**kwargs)
            
            elif layer == AgentLayer.LAYER_2_RECOGNITION:
                # Layer 2 agents don't need KG
                return agent_class(**kwargs)
            
            elif layer == AgentLayer.LAYER_3_DOMAIN:
                # Layer 3 agents need KG client
                return agent_class(kg_client=self.kg, **kwargs)
            
            elif layer == AgentLayer.LAYER_4_WORKFLOW:
                # Layer 4 agents need KG client
                return agent_class(kg_client=self.kg, **kwargs)
            
            elif layer == AgentLayer.LAYER_5_META:
                # Layer 5 agents need KG client
                return agent_class(kg_client=self.kg, **kwargs)
            
            else:
                logger.error(f"Unknown layer: {layer}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to instantiate agent: {e}")
            return None
    
    def create_workflow(
        self,
        workflow_name: str,
        resolve_dependencies: bool = True
    ) -> Optional[Layer4Agent]:
        """
        Create a workflow agent with all dependencies resolved
        
        Args:
            workflow_name: Name of the workflow agent
            resolve_dependencies: Whether to create and register dependencies
            
        Returns:
            Workflow agent with dependencies registered
            
        Example:
            workflow = factory.create_workflow("meeting_orchestrator")
            # All dependencies (email_parser, calendar, etc.) are registered
        """
        # Create the workflow agent
        workflow = self.create(workflow_name, layer=AgentLayer.LAYER_4_WORKFLOW)
        if not workflow:
            return None
        
        # Resolve dependencies if requested
        if resolve_dependencies:
            entry = self.registry.get_agent_entry(
                AgentLayer.LAYER_4_WORKFLOW,
                workflow_name
            )
            
            if entry and entry.dependencies:
                logger.info(f"Resolving dependencies for {workflow_name}: {entry.dependencies}")
                
                for dep_name in entry.dependencies:
                    # Create dependency agent
                    dep_agent = self.create(dep_name)
                    if dep_agent:
                        # Register with workflow
                        workflow.register_agent(dep_name, dep_agent)
                        logger.debug(f"Registered dependency: {dep_name}")
                    else:
                        logger.warning(f"Failed to create dependency: {dep_name}")
        
        return workflow
    
    def create_layer1_agent(self, agent_name: str) -> Optional[Layer1Agent]:
        """Create Layer 1 agent"""
        return self.create(agent_name, layer=AgentLayer.LAYER_1_EXTRACTION)
    
    def create_layer2_agent(self, agent_name: str) -> Optional[Layer2Agent]:
        """Create Layer 2 agent"""
        return self.create(agent_name, layer=AgentLayer.LAYER_2_RECOGNITION)
    
    def create_layer3_agent(self, agent_name: str) -> Optional[Layer3Agent]:
        """Create Layer 3 agent"""
        return self.create(agent_name, layer=AgentLayer.LAYER_3_DOMAIN)
    
    def create_layer4_agent(self, agent_name: str) -> Optional[Layer4Agent]:
        """Create Layer 4 agent"""
        return self.create(agent_name, layer=AgentLayer.LAYER_4_WORKFLOW)
    
    def create_layer5_agent(self, agent_name: str) -> Optional[Layer5Agent]:
        """Create Layer 5 agent"""
        return self.create(agent_name, layer=AgentLayer.LAYER_5_META)
    
    def create_agent_chain(
        self,
        agent_names: List[str]
    ) -> List[Any]:
        """
        Create a chain of agents
        
        Args:
            agent_names: List of agent names in order
            
        Returns:
            List of agent instances
            
        Example:
            chain = factory.create_agent_chain([
                "email_parser",
                "person_recognition",
                "research"
            ])
        """
        agents = []
        for name in agent_names:
            agent = self.create(name)
            if agent:
                agents.append(agent)
            else:
                logger.warning(f"Failed to create agent in chain: {name}")
        
        return agents
    
    def clear_cache(self):
        """Clear agent cache"""
        self._agent_cache.clear()
        logger.info("Agent cache cleared")
    
    def get_cached_agents(self) -> List[str]:
        """Get list of cached agent names"""
        return list(self._agent_cache.keys())
    
    def validate_agent(self, agent_name: str) -> tuple[bool, Optional[str]]:
        """
        Validate that an agent can be created
        
        Returns:
            (is_valid, error_message)
        """
        # Check if agent exists
        found = False
        for layer in AgentLayer:
            if self.registry.get_agent_entry(layer, agent_name):
                found = True
                break
        
        if not found:
            return False, f"Agent '{agent_name}' not found in registry"
        
        # Check dependencies
        for layer in AgentLayer:
            entry = self.registry.get_agent_entry(layer, agent_name)
            if entry:
                valid, missing = self.registry.validate_dependencies(layer, agent_name)
                if not valid:
                    return False, f"Missing dependencies: {missing}"
                break
        
        return True, None


# ============================================================================
# SINGLETON FACTORY
# ============================================================================

_factory_instance: Optional[AgentFactory] = None


def get_factory(kg_client=None) -> AgentFactory:
    """Get singleton factory instance"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AgentFactory(kg_client=kg_client)
    return _factory_instance


def set_factory(factory: AgentFactory):
    """Set singleton factory instance"""
    global _factory_instance
    _factory_instance = factory


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def create_agent(agent_name: str, kg_client=None) -> Optional[Any]:
    """Convenience function to create an agent"""
    factory = get_factory(kg_client=kg_client)
    return factory.create(agent_name)


async def create_workflow(workflow_name: str, kg_client=None) -> Optional[Layer4Agent]:
    """Convenience function to create a workflow with dependencies"""
    factory = get_factory(kg_client=kg_client)
    return factory.create_workflow(workflow_name)
