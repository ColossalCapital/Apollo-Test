"""
Customer Support Agent - LLM-Powered Customer Support

Layer 3 Domain Expert agent that provides intelligent customer support
and ticket management.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class CustomerSupportAgent(Layer3Agent):
    """
    Customer Support Agent - LLM-powered support automation
    
    Provides:
    - Ticket classification and routing
    - Automated response suggestions
    - Knowledge base search
    - Sentiment analysis
    - Escalation detection
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="customer_support",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered customer support and ticket management",
            capabilities=[
                "ticket_classification",
                "response_generation",
                "knowledge_base_search",
                "sentiment_analysis",
                "escalation_detection"
            ],
            dependencies=["knowledge_graph"]
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Analyze customer support ticket"""
        
        ticket = domain_data.get('ticket', {})
        
        prompt = f"""You are an expert customer support agent. Analyze this support ticket and provide recommendations.

TICKET:
Subject: {ticket.get('subject', 'N/A')}
Message: {ticket.get('message', 'N/A')}
Customer: {ticket.get('customer', 'N/A')}
Priority: {ticket.get('priority', 'Normal')}

ANALYZE:
1. Ticket classification (bug, feature request, question, complaint)
2. Sentiment analysis (positive, neutral, negative, urgent)
3. Suggested response
4. Knowledge base articles to reference
5. Escalation needed? (yes/no with reason)
6. Estimated resolution time
7. Required team/department

Return as JSON with detailed customer support analysis.
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
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_ticket_in_kg(ticket, analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'ticket_id': ticket.get('id')}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_ticket_in_kg(self, ticket: Dict[str, Any], analysis: Dict[str, Any]):
        """Store ticket analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="support_ticket",
            data={'ticket': ticket, 'analysis': analysis},
            graph_type="business"
        )
