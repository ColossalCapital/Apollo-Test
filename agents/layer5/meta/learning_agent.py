"""
Learning Agent - LLM-Powered System Learning and Optimization

Layer 5 Meta-Orchestration agent that uses LLM to learn from user
behavior and continuously optimize the system.
"""

from typing import Dict, Any, List
from ...base import Layer5Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class LearningAgent(Layer5Agent):
    """
    Learning Agent - LLM-powered continuous system improvement
    
    Responsibilities:
    1. Analyze user behavior patterns
    2. Identify optimization opportunities
    3. Create new automation rules
    4. Improve agent performance
    5. Personalize system behavior
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="learning_agent",
            layer=AgentLayer.LAYER_5_META,
            version="1.0.0",
            description="LLM-powered system learning and continuous optimization",
            capabilities=["pattern_learning", "automation_creation", "personalization", "performance_optimization"],
            dependencies=[]
        )
    
    async def optimize(self, context: Dict[str, Any]) -> AgentResult:
        """
        Learn from user behavior and optimize system
        
        Args:
            context: {
                "type": "learn",
                "user_id": "...",
                "time_period": "last_30_days",
                "focus": "all|workflows|agents|automation"
            }
            
        Returns:
            AgentResult with learned patterns and optimizations
        """
        
        # Analyze patterns
        patterns = await self._analyze_patterns(context)
        
        # Generate optimizations
        optimizations = await self._generate_optimizations(patterns)
        
        # Apply optimizations
        applied = await self._apply_optimizations(optimizations)
        
        return AgentResult(
            success=True,
            data={
                "patterns_discovered": patterns,
                "optimizations_generated": optimizations,
                "optimizations_applied": applied
            },
            metadata={'agent': self.metadata.name}
        )
    
    async def _analyze_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze user behavior patterns"""
        
        # Get user activity from knowledge graph
        user_activity = await self._get_user_activity(context.get('user_id'))
        
        prompt = f"""You are a learning agent. Analyze this user's behavior and identify patterns.

USER ACTIVITY (last 30 days):
{json.dumps(user_activity, indent=2)}

ANALYZE:
1. What are the recurring workflows?
2. What tasks are repetitive?
3. What decisions are predictable?
4. What can be automated?
5. What's causing friction?

IDENTIFY PATTERNS like:
- "Every Monday at 9am, user reviews invoices from Vendor X"
- "User always approves invoices < $1000 from trusted vendors"
- "User schedules meetings with John every Tuesday"
- "User always creates same type of task after certain emails"

Return as JSON:
{{
    "patterns": [
        {{
            "type": "recurring_workflow",
            "description": "Weekly invoice review",
            "frequency": "weekly",
            "confidence": 0.95,
            "automation_potential": "high"
        }},
        {{
            "type": "predictable_decision",
            "description": "Auto-approve small invoices from trusted vendors",
            "frequency": "daily",
            "confidence": 0.98,
            "automation_potential": "very_high"
        }}
    ],
    "insights": [
        "User spends 2 hours/week on manual invoice approval",
        "95% of invoices < $1000 are approved without changes",
        "User always schedules same meeting type with same people"
    ],
    "opportunities": [
        "Automate invoice approval for trusted vendors < $1000",
        "Auto-schedule recurring meetings",
        "Pre-fill task templates based on email type"
    ]
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            return json.loads(llm_response['choices'][0]['message']['content'])
            
        except Exception as e:
            return {"patterns": [], "insights": [], "opportunities": []}
    
    async def _generate_optimizations(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization rules from patterns"""
        
        prompt = f"""Based on these patterns, generate automation rules.

PATTERNS:
{json.dumps(patterns, indent=2)}

GENERATE RULES:
For each high-confidence pattern, create an automation rule.

Example rules:
- "IF invoice from Vendor X AND amount < $1000 THEN auto-approve"
- "IF email from John contains 'meeting' THEN auto-schedule Tuesday 2pm"
- "IF invoice received THEN create task 'Review invoice' assigned to user"

Return as JSON:
{{
    "rules": [
        {{
            "id": "rule_001",
            "name": "Auto-approve small invoices",
            "condition": "invoice.vendor in trusted_vendors AND invoice.amount < 1000",
            "action": "auto_approve_invoice",
            "confidence": 0.98,
            "estimated_time_saved": "30 minutes/week"
        }}
    ]
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            result = json.loads(llm_response['choices'][0]['message']['content'])
            return result.get('rules', [])
            
        except Exception as e:
            return []
    
    async def _apply_optimizations(self, optimizations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply optimization rules to the system"""
        
        applied = []
        
        for opt in optimizations:
            # Store rule in knowledge graph
            if self.kg_client:
                await self.kg_client.create_entity(
                    entity_type="automation_rule",
                    data=opt
                )
            
            applied.append({
                "rule_id": opt.get('id'),
                "status": "applied",
                "enabled": True
            })
        
        return applied
    
    async def _get_user_activity(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user activity from knowledge graph"""
        
        if not self.kg_client:
            return []
        
        # TODO: Query knowledge graph for user activity
        # For now, return mock data
        return [
            {"type": "invoice_approved", "vendor": "Vendor X", "amount": 500, "timestamp": "2025-10-15"},
            {"type": "invoice_approved", "vendor": "Vendor X", "amount": 750, "timestamp": "2025-10-22"},
            {"type": "meeting_scheduled", "participant": "John", "day": "Tuesday", "timestamp": "2025-10-16"}
        ]
