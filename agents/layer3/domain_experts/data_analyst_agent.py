"""
Data Analyst Agent - LLM-Powered Data Analysis

Layer 3 Domain Expert agent that provides data analysis, insights,
and visualization recommendations.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class DataAnalystAgent(Layer3Agent):
    """
    Data Analyst Agent - LLM-powered data analysis
    
    Provides:
    - Statistical analysis
    - Trend detection
    - Anomaly detection
    - Visualization recommendations
    - Predictive insights
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="data_analyst",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered data analysis and insights",
            capabilities=[
                "statistical_analysis",
                "trend_detection",
                "anomaly_detection",
                "visualization_recommendations",
                "predictive_insights"
            ],
            dependencies=["knowledge_graph"]
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Analyze data and provide insights"""
        
        dataset = domain_data.get('dataset', {})
        analysis_type = domain_data.get('analysis_type', 'exploratory')
        
        prompt = f"""You are an expert data analyst. Analyze this dataset and provide insights.

DATASET:
{json.dumps(dataset, indent=2)}

ANALYSIS TYPE: {analysis_type}

PROVIDE:
1. Statistical summary (mean, median, std dev, etc.)
2. Key trends and patterns
3. Anomalies or outliers
4. Correlations between variables
5. Visualization recommendations (chart types)
6. Predictive insights
7. Actionable recommendations
8. Data quality assessment

Return as JSON with comprehensive data analysis.
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
                await self._store_analysis_in_kg(analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'analysis_type': analysis_type}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_analysis_in_kg(self, analysis: Dict[str, Any]):
        """Store analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="data_analysis",
            data=analysis,
            graph_type="technical"
        )
