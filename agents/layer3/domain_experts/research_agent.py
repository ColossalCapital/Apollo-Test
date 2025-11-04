"""
Research Agent - LLM-Powered Research and Analysis

Layer 3 Domain Expert agent that conducts research and provides insights.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class ResearchAgent(Layer3Agent):
    """
    Research Agent - LLM-powered research and analysis
    
    Provides:
    - Market research
    - Competitive analysis
    - User research insights
    - Industry trends
    - Literature review
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="research",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered research and competitive analysis",
            capabilities=[
                "market_research",
                "competitive_analysis",
                "user_research",
                "trend_analysis",
                "literature_review"
            ],
            dependencies=["knowledge_graph"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Conduct research and provide insights"""
        
        research_topic = domain_data.get('topic', '')
        research_type = domain_data.get('type', 'market')
        
        prompt = f"""You are an expert researcher. Conduct research on this topic.

TOPIC: {research_topic}
TYPE: {research_type}

RESEARCH:
1. Key findings and insights
2. Market size and trends (if applicable)
3. Competitive landscape
4. Target audience analysis
5. Opportunities and threats
6. Data sources and citations
7. Recommendations
8. Next steps for deeper research

Return as JSON with comprehensive research findings.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            research_findings = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_research_in_kg(research_findings)
            
            return AgentResult(
                success=True,
                data=research_findings,
                metadata={'agent': self.metadata.name, 'topic': research_topic}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_research_in_kg(self, research: Dict[str, Any]):
        """Store research findings in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="research_findings",
            data=research,
            graph_type="business"
        )
