"""
Uber Connector Agent - Uber API Integration

Connector agent that integrates with Uber API for ride history and travel data.
"""

from typing import Dict, Any
from ..base import ConnectorAgent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx


class UberConnectorAgent(ConnectorAgent):
    """
    Uber Connector - Ride history and travel data integration
    
    Provides:
    - Ride history
    - Trip details
    - Payment history
    - Travel patterns
    - Expense tracking
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.api_url = "https://api.uber.com/v1.2"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="uber_connector",
            layer=AgentLayer.CONNECTOR,
            version="1.0.0",
            description="Uber API integration for ride history and travel data",
            capabilities=[
                "ride_history",
                "trip_details",
                "payment_history",
                "travel_patterns",
                "expense_tracking"
            ],
            dependencies=[],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL, EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=True,
            wtf_purchasable=False,
            required_credentials=["access_token"]
        )
    
    async def connect(self, credentials: Dict[str, str]) -> AgentResult:
        """Connect to Uber API"""
        
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
    
    async def fetch_ride_history(self, access_token: str, limit: int = 50) -> AgentResult:
        """Fetch ride history"""
        
        try:
            response = await self.client.get(
                f"{self.api_url}/history",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                history = response.json()
                return AgentResult(
                    success=True,
                    data=history,
                    metadata={'agent': self.metadata.name, 'count': len(history.get('history', []))}
                )
            else:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'error': 'Failed to fetch history'}
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
