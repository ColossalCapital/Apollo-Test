"""
MyFitnessPal Connector Agent - MyFitnessPal API Integration

Connector agent that integrates with MyFitnessPal API for nutrition tracking.
"""

from typing import Dict, Any
from ..base import ConnectorAgent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx


class MyFitnessPalConnectorAgent(ConnectorAgent):
    """
    MyFitnessPal Connector - Nutrition tracking integration
    
    Provides:
    - Food diary data
    - Calorie tracking
    - Macro nutrients
    - Weight tracking
    - Exercise logging
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.api_url = "https://api.myfitnesspal.com/v2"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="myfitnesspal_connector",
            layer=AgentLayer.CONNECTOR,
            version="1.0.0",
            description="MyFitnessPal API integration for nutrition tracking",
            capabilities=[
                "food_diary_sync",
                "calorie_tracking",
                "macro_nutrients",
                "weight_tracking",
                "exercise_logging"
            ],
            dependencies=[],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=True,
            wtf_purchasable=False,
            required_credentials=["access_token"]
        )
    
    async def connect(self, credentials: Dict[str, str]) -> AgentResult:
        """Connect to MyFitnessPal API"""
        
        access_token = credentials.get('access_token')
        
        try:
            # Test connection
            response = await self.client.get(
                f"{self.api_url}/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return AgentResult(
                    success=True,
                    data={"user": user_data, "status": "connected"},
                    metadata={'agent': self.metadata.name}
                )
            else:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'error': 'Authentication failed'}
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def fetch_food_diary(self, access_token: str, date: str) -> AgentResult:
        """Fetch food diary for a specific date"""
        
        try:
            response = await self.client.get(
                f"{self.api_url}/diary",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"date": date}
            )
            
            if response.status_code == 200:
                diary = response.json()
                return AgentResult(
                    success=True,
                    data=diary,
                    metadata={'agent': self.metadata.name, 'date': date}
                )
            else:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'error': 'Failed to fetch diary'}
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
