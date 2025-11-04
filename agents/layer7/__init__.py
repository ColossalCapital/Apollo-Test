"""
Layer 7: Swarm Intelligence

Multi-agent collaboration for complex problem-solving.
These agents coordinate multiple agents to work together.
"""

from .swarm_coordinator_agent import SwarmCoordinatorAgent
from .consensus_agent import ConsensusAgent
from .emergent_intelligence_agent import EmergentIntelligenceAgent

__all__ = [
    'SwarmCoordinatorAgent',
    'ConsensusAgent',
    'EmergentIntelligenceAgent',
]
