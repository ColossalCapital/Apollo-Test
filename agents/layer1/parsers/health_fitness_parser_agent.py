"""
Health & Fitness Parser Agent - LLM-Powered Health Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse health and fitness data
from multiple sources (Apple Health, Strava, Nike Run Club, MyFitnessPal).
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class HealthFitnessParserAgent(Layer1Agent):
    """
    Health & Fitness Parser - LLM-powered health data parsing
    
    Takes health data and extracts:
    - Activity patterns and trends
    - Nutrition insights
    - Sleep quality analysis
    - Workout performance
    - Health correlations
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="health_fitness_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered health and fitness data parsing",
            capabilities=[
                "activity_analysis",
                "nutrition_tracking",
                "sleep_analysis",
                "workout_performance",
                "health_correlations"
            ],
            dependencies=[
                "apple_health_connector",
                "strava_connector",
                "nike_run_club_connector",
                "myfitnesspal_connector"
            ]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from health and fitness sources"""
        
        prompt = f"""You are an expert at analyzing health and fitness data. Extract structured information from this data.

HEALTH DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Activity summary (steps, distance, calories)
2. Workout analysis (type, duration, intensity)
3. Nutrition insights (calories, macros, meal patterns)
4. Sleep quality (duration, stages, quality score)
5. Health trends (week over week, month over month)
6. Correlations (sleep vs performance, nutrition vs energy)
7. Goal progress (fitness goals, weight goals)
8. Recommendations for improvement
9. Anomalies or concerns
10. Personal records and achievements

Return as JSON with detailed health and fitness analysis.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_health_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'health_fitness'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_health_in_kg(self, health_data: Dict[str, Any]):
        """Store parsed health data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="health_fitness",
            data=health_data,
            graph_type="personal"
        )
