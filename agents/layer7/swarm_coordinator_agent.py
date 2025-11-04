"""
Swarm Coordinator Agent - Multi-Agent Orchestration

Layer 7 Swarm agent that coordinates multiple agents to solve complex problems.
"""

from typing import Dict, Any, List
from .swarm_agent import Layer7Agent
from ..base import AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext, PrivacyLevel, AgentCategory
import httpx
import json
import asyncio


class SwarmCoordinatorAgent(Layer7Agent):
    """Swarm Coordinator - Multi-agent orchestration"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="swarm_coordinator",
            layer=AgentLayer.LAYER_5_META,
            version="1.0.0",
            description="Multi-agent coordination for complex problem-solving",
            capabilities=["task_decomposition", "agent_assignment", "parallel_execution", "result_merging", "failure_handling"],
            dependencies=["meta_orchestrator", "all_layer3_agents"],
            entity_types=[EntityType.TRADING_FIRM, EntityType.BUSINESS],
            app_contexts=[AppContext.DELT, AppContext.AKASHIC],
            requires_subscription=["enterprise"],
            byok_enabled=False,
            wtf_purchasable=False,
            estimated_tokens_per_call=3000,
            estimated_cost_per_call=0.020,
            rate_limit="10/hour",
            avg_response_time_ms=5000,
            requires_gpu=False,
            can_run_offline=False,
            data_retention_days=365,
            privacy_level=PrivacyLevel.ORG_PRIVATE,
            pii_handling=False,
            gdpr_compliant=True,
            api_version="v1",
            webhook_support=True,
            real_time_sync=False,
            sync_frequency=None,
            free_tier_limit=0,
            pro_tier_limit=0,
            enterprise_only=True,
            beta=False,
            supports_continuous_learning=True,
            training_cost_wtf=500,
            training_frequency="after_20_interactions",
            model_storage_location="filecoin",
            has_ui_component=True,
            icon="network",
            color="#8B5CF6",
            category=AgentCategory.WORKFLOW,
            health_check_endpoint="/health/swarm_coordinator",
            alert_on_failure=True,
            fallback_agent=None,
            documentation_url="https://docs.colossalcapital.com/agents/swarm-coordinator",
            example_use_cases=[
                "Build and deploy trading strategy (parallel analysis)",
                "Comprehensive market analysis (multiple experts)",
                "Multi-domain problem solving",
                "Complex workflow orchestration"
            ],
            setup_guide_url="https://docs.colossalcapital.com/setup/swarm-coordinator"
        )
    
    async def decompose(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose complex task into subtasks"""
        
        prompt = f"""You are a task decomposition expert. Break down this complex task into subtasks.

TASK:
{json.dumps(task, indent=2)}

DECOMPOSE into subtasks that can be executed in parallel.
Each subtask should specify:
1. What needs to be done
2. Which type of agent should handle it
3. Dependencies on other subtasks
4. Expected output

Return as JSON array of subtasks.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            subtasks = json.loads(llm_response['choices'][0]['message']['content'])
            
            return subtasks
            
        except Exception as e:
            return []
    
    async def assign(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assign subtasks to appropriate agents"""
        
        assignments = {}
        for i, subtask in enumerate(subtasks):
            agent_type = subtask.get('agent_type', 'generic')
            assignments[f"subtask_{i}"] = {
                'subtask': subtask,
                'agent': agent_type,
                'status': 'pending'
            }
        
        return assignments
    
    async def coordinate(self, assignments: Dict[str, Any]) -> AgentResult:
        """Coordinate parallel execution of subtasks"""
        
        try:
            # Execute all subtasks in parallel
            tasks = []
            for task_id, assignment in assignments.items():
                tasks.append(self._execute_subtask(task_id, assignment))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return AgentResult(
                success=True,
                data={'results': results},
                metadata={'agent': self.metadata.name, 'num_subtasks': len(results)}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def merge(self, results: List[AgentResult]) -> AgentResult:
        """Merge results from multiple agents"""
        
        # Combine all successful results
        merged_data = {}
        for i, result in enumerate(results):
            if isinstance(result, AgentResult) and result.success:
                merged_data[f"result_{i}"] = result.data
        
        return AgentResult(
            success=True,
            data=merged_data,
            metadata={'agent': self.metadata.name, 'merged_count': len(merged_data)}
        )
    
    async def _execute_subtask(self, task_id: str, assignment: Dict[str, Any]) -> AgentResult:
        """Execute a single subtask"""
        
        # In production, this would call the actual agent
        # For now, simulate execution
        await asyncio.sleep(0.1)  # Simulate work
        
        return AgentResult(
            success=True,
            data={'task_id': task_id, 'result': 'completed'},
            metadata={'agent': assignment.get('agent', 'unknown')}
        )
