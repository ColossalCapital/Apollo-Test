"""
Analytics Agent - LLM-Powered Business Analytics

Layer 3 Domain Expert agent that provides business analytics and insights.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class AnalyticsAgent(Layer3Agent):
    """
    Analytics Agent - LLM-powered business analytics
    
    Provides:
    - Metrics analysis
    - KPI tracking
    - Trend identification
    - Forecasting
    - Dashboard recommendations
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="analytics",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered business analytics and insights",
            capabilities=[
                "metrics_analysis",
                "kpi_tracking",
                "trend_identification",
                "forecasting",
                "dashboard_recommendations"
            ],
            dependencies=["knowledge_graph", "data_analyst"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS, EntityType.TRADING_FIRM],
            app_contexts=[AppContext.ATLAS, AppContext.DELT],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Provide analytics and insights"""
        
        metrics = domain_data.get('metrics', {})
        timeframe = domain_data.get('timeframe', '30d')
        
        prompt = f"""You are an expert business analyst. Analyze these metrics and provide insights.

METRICS:
{json.dumps(metrics, indent=2)}

TIMEFRAME: {timeframe}

ANALYZE:
1. Key trends and patterns
2. Performance vs targets
3. Anomalies or outliers
4. Growth rates and momentum
5. Leading vs lagging indicators
6. Correlation analysis
7. Forecasts and predictions
8. Risk indicators
9. Optimization opportunities
10. Recommended actions
11. Dashboard visualizations
12. Alert thresholds

Return as JSON with detailed analytics and actionable insights.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_analytics_in_kg(analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'timeframe': timeframe}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_analytics_in_kg(self, analytics: Dict[str, Any]):
        """Store analytics in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="analytics_report",
            data=analytics,
            graph_type="business"
        )
