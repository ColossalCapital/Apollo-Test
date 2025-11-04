"""
Meta Orchestrator Agent - LLM-Powered System-Wide Orchestration

Layer 5 Meta-Orchestration agent that uses LLM to route requests to
the best agents and optimize system-wide workflows.
"""

from typing import Dict, Any, List
from ...base import Layer5Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class MetaOrchestratorAgent(Layer5Agent):
    """
    Meta Orchestrator - LLM-powered system-wide routing and optimization
    
    Responsibilities:
    1. Analyze incoming requests
    2. Route to best agent(s) based on context
    3. Coordinate multi-agent workflows
    4. Optimize agent selection over time
    5. Learn from outcomes
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="meta_orchestrator",
            layer=AgentLayer.LAYER_5_META,
            version="1.0.0",
            description="LLM-powered system-wide agent routing and optimization",
            capabilities=["agent_routing", "workflow_optimization", "multi_agent_coordination", "system_learning"],
            dependencies=[]  # Meta agent can call any agent
        )
    
    async def optimize(self, request: Dict[str, Any]) -> AgentResult:
        """
        Optimize and route request to best agent(s)
        
        Args:
            request: {
                "type": "user_request",
                "content": "...",
                "context": {...},
                "user_id": "...",
                "history": [...]
            }
            
        Returns:
            AgentResult with routing decision and execution
        """
        
        # Analyze request and decide routing
        routing_decision = await self._analyze_and_route(request)
        
        # Execute the routing
        results = await self._execute_routing(routing_decision)
        
        # Learn from the outcome
        await self._learn_from_outcome(request, routing_decision, results)
        
        return AgentResult(
            success=True,
            data={
                "routing_decision": routing_decision,
                "results": results,
                "optimizations_applied": True
            },
            metadata={'agent': self.metadata.name}
        )
    
    async def _analyze_and_route(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze request and decide routing"""
        
        prompt = f"""You are the Meta Orchestrator. Analyze this request and decide which agent(s) to route it to.

REQUEST:
{json.dumps(request, indent=2)}

AVAILABLE AGENTS:
Layer 1 (Parsers): gmail_parser, quickbooks_parser, plaid_parser
Layer 2 (Recognition): person_recognition, company_recognition
Layer 3 (Domain Experts): financial_analyst, trading_strategy, entity_governance
Layer 4 (Workflows): invoice_workflow, meeting_orchestrator
Layer 5 (Meta): meta_orchestrator, learning_agent

ANALYZE:
1. What is the user trying to do?
2. Which layer(s) should handle this?
3. Which specific agent(s)?
4. Should multiple agents work together?
5. What's the optimal sequence?

CONSIDER:
- User history (have they done this before?)
- Context (what entity/project?)
- Complexity (simple vs complex request)
- Urgency (time-sensitive?)

Return as JSON:
{{
    "intent": "...",
    "complexity": "simple|medium|complex",
    "routing": {{
        "primary_agent": "...",
        "supporting_agents": [...],
        "sequence": [
            {{"agent": "...", "action": "..."}},
            {{"agent": "...", "action": "..."}}
        ]
    }},
    "optimizations": [
        "Skip Layer 2 (entity already known)",
        "Use cached result from yesterday",
        "Auto-approve (trusted pattern)"
    ],
    "estimated_time": "2 seconds"
}}
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
            return json.loads(llm_response['choices'][0]['message']['content'])
            
        except Exception as e:
            # Fallback to simple routing
            return {
                "intent": "unknown",
                "routing": {"primary_agent": "gmail_parser"},
                "optimizations": []
            }
    
    async def _execute_routing(self, routing_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the routing decision"""
        
        results = []
        
        for step in routing_decision.get('routing', {}).get('sequence', []):
            agent_name = step.get('agent')
            action = step.get('action')
            
            # TODO: Use agent factory to call agents
            result = await self._call_agent(agent_name, action)
            results.append({
                "agent": agent_name,
                "action": action,
                "result": result
            })
        
        return results
    
    async def _call_agent(self, agent_name: str, action: str) -> Dict[str, Any]:
        """Call another agent"""
        # TODO: Implement agent factory integration
        return {"success": True, "agent": agent_name, "action": action}
    
    async def _learn_from_outcome(
        self, 
        request: Dict[str, Any], 
        routing: Dict[str, Any], 
        results: List[Dict[str, Any]]
    ):
        """Learn from the outcome to improve future routing"""
        
        # Store in knowledge graph for learning
        if self.kg_client:
            await self.kg_client.create_entity(
                entity_type="routing_outcome",
                data={
                    "request_type": request.get('type'),
                    "routing_decision": routing,
                    "success": all(r.get('result', {}).get('success', False) for r in results),
                    "execution_time": sum(r.get('result', {}).get('time', 0) for r in results)
                }
            )
