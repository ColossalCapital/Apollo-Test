"""
MyFitnessPal Connector Agent - MyFitnessPal API Integration

Maintains MyFitnessPal API connector for nutrition tracking and meal logging.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class MyFitnessPalConnectorAgent(Layer1Agent):
    """MyFitnessPal API connector"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/myfitnesspal"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="myfitnesspal_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="MyFitnessPal connector - nutrition tracking and meal logging",
            capabilities=[
                "meal_logging",
                "calorie_tracking",
                "macro_tracking",
                "food_database",
                "recipe_analysis",
                "bidirectional_sync"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process MyFitnessPal connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'MyFitnessPal',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'endpoints': ['MyFitnessPal API'],
                        'required': ['Account', 'API Key'],
                        'scopes': ['diary.read', 'diary.write', 'nutrition.read']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'MyFitnessPal',
                    'sync_modes': {
                        'pull': 'Fetch meal logs and nutrition data',
                        'push': 'Log meals from Atlas meal photos',
                        'bidirectional': 'Two-way sync with Atlas'
                    },
                    'entities': {
                        'meals': 'Breakfast, lunch, dinner, snacks',
                        'foods': 'Individual food items',
                        'recipes': 'Custom recipes',
                        'nutrition': 'Calories, protein, carbs, fat',
                        'water': 'Water intake tracking',
                        'weight': 'Weight tracking over time'
                    },
                    'atlas_integration': {
                        'meal_photos': 'Atlas meal photos → MyFitnessPal logs',
                        'ai_recognition': 'AI identifies food from photos',
                        'auto_logging': 'Automatic meal logging'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'MyFitnessPal',
                    'message': 'MyFitnessPal connector for nutrition tracking'
                },
                metadata={'agent': self.metadata.name}
            )
