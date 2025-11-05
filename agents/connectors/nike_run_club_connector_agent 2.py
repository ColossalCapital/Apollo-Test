"""
Nike Run Club Connector Agent - Nike Run Club API Integration

Connector agent that integrates with Nike Run Club API for fitness tracking.
"""

from typing import Dict, Any
from ..base import ConnectorAgent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx


class NikeRunClubConnectorAgent(ConnectorAgent):
    """
    Nike Run Club Connector - Fitness tracking integration
    
    Provides:
    - Running activity data
    - Workout history
    - Personal records
    - Achievement tracking
    - Social features
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.api_url = "https://api.nike.com/sport/v3"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="nike_run_club_connector",
            layer=AgentLayer.CONNECTOR,
            version="1.0.0",
            description="Nike Run Club API integration for fitness tracking",
            capabilities=[
                "activity_sync",
                "workout_history",
                "personal_records",
                "achievement_tracking",
                "social_features"
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
        """Connect to Nike Run Club API"""
        
        access_token = credentials.get('access_token')
        
        try:
            # Test connection
            response = await self.client.get(
                f"{self.api_url}/me",
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
    
    async def fetch_activities(self, access_token: str, limit: int = 50) -> AgentResult:
        """Fetch running activities"""
        
        try:
            response = await self.client.get(
                f"{self.api_url}/me/activities",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                activities = response.json()
                return AgentResult(
                    success=True,
                    data=activities,
                    metadata={'agent': self.metadata.name, 'count': len(activities.get('activities', []))}
                )
            else:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'error': 'Failed to fetch activities'}
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
