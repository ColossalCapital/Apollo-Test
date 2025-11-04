"""
Consensus Agent - Multi-Agent Consensus Decision Making

Layer 7 Swarm agent that gets consensus from multiple agents for critical decisions.
"""

from typing import Dict, Any, List
from .swarm_agent import Layer7Agent
from ..base import AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext, PrivacyLevel, AgentCategory
import httpx
import json


class ConsensusAgent(Layer7Agent):
    """Consensus Agent - Multi-agent consensus"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="consensus",
            layer=AgentLayer.LAYER_5_META,
            version="1.0.0",
            description="Multi-agent consensus decision making",
            capabilities=["agent_polling", "opinion_aggregation", "conflict_resolution", "weighted_voting", "confidence_scoring"],
            dependencies=["meta_orchestrator", "all_layer3_agents"],
            entity_types=[EntityType.BUSINESS, EntityType.TRADING_FIRM],
            app_contexts=[AppContext.AKASHIC],
            requires_subscription=["pro"],
            byok_enabled=False,
            wtf_purchasable=False,
            estimated_tokens_per_call=2500,
            estimated_cost_per_call=0.015,
            rate_limit="20/hour",
            avg_response_time_ms=3000,
            requires_gpu=False,
            can_run_offline=False,
            data_retention_days=180,
            privacy_level=PrivacyLevel.ORG_PRIVATE,
            pii_handling=False,
            gdpr_compliant=True,
            api_version="v1",
            webhook_support=False,
            real_time_sync=False,
            sync_frequency=None,
            free_tier_limit=0,
            pro_tier_limit=100,
            enterprise_only=False,
            beta=False,
            supports_continuous_learning=True,
            training_cost_wtf=300,
            training_frequency="after_30_interactions",
            model_storage_location="filecoin",
            has_ui_component=True,
            icon="users",
            color="#10B981",
            category=AgentCategory.WORKFLOW,
            health_check_endpoint="/health/consensus",
            alert_on_failure=False,
            fallback_agent=None,
            documentation_url="https://docs.colossalcapital.com/agents/consensus",
            example_use_cases=[
                "Should we deploy this code? (multiple experts vote)",
                "Is this strategy viable? (consensus from analysts)",
                "Critical business decisions",
                "Risk assessment with multiple perspectives"
            ],
            setup_guide_url="https://docs.colossalcapital.com/setup/consensus"
        )
    
    async def decompose(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose question into agent queries"""
        
        question = task.get('question', '')
        agents = task.get('agents', [])
        
        subtasks = []
        for agent in agents:
            subtasks.append({
                'agent': agent,
                'question': question,
                'type': 'opinion'
            })
        
        return subtasks
    
    async def assign(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assign questions to agents"""
        
        assignments = {}
        for i, subtask in enumerate(subtasks):
            assignments[f"agent_{i}"] = subtask
        
        return assignments
    
    async def coordinate(self, assignments: Dict[str, Any]) -> AgentResult:
        """Get opinions from all agents"""
        
        opinions = []
        for agent_id, assignment in assignments.items():
            # In production, query actual agent
            opinion = {
                'agent': assignment['agent'],
                'answer': 'yes',  # Placeholder
                'confidence': 0.8,
                'reasoning': 'Analysis complete'
            }
            opinions.append(opinion)
        
        return AgentResult(
            success=True,
            data={'results': opinions},
            metadata={'agent': self.metadata.name}
        )
    
    async def merge(self, results: List[AgentResult]) -> AgentResult:
        """Calculate consensus from opinions"""
        
        opinions = results[0].data.get('results', []) if results else []
        
        # Weighted voting
        total_weight = 0
        weighted_sum = 0
        
        for opinion in opinions:
            confidence = opinion.get('confidence', 0.5)
            answer = 1 if opinion.get('answer') == 'yes' else 0
            weighted_sum += answer * confidence
            total_weight += confidence
        
        consensus_score = weighted_sum / total_weight if total_weight > 0 else 0
        consensus = 'yes' if consensus_score > 0.5 else 'no'
        
        return AgentResult(
            success=True,
            data={
                'consensus': consensus,
                'confidence': consensus_score,
                'opinions': opinions
            },
            metadata={'agent': self.metadata.name, 'num_opinions': len(opinions)}
        )
