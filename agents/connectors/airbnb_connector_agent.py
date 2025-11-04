"""
Airbnb Connector Agent - Airbnb API Integration

Connector agent that integrates with Airbnb for travel and accommodation data.
"""

from typing import Dict, Any
from ..base import ConnectorAgent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx


class AirbnbConnectorAgent(ConnectorAgent):
    """
    Airbnb Connector - Travel and accommodation data integration
    
    Provides:
    - Booking history
    - Trip details
    - Property information
    - Travel patterns
    - Expense tracking
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.api_url = "https://api.airbnb.com/v2"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="airbnb_connector",
            layer=AgentLayer.CONNECTOR,
            version="1.0.0",
            description="Airbnb API integration for travel and accommodation data",
            capabilities=[
                "booking_history",
                "trip_details",
                "property_info",
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
        """Connect to Airbnb API"""
        
        access_token = credentials.get('access_token')
        
        try:
            # Test connection
            response = await self.client.get(
                f"{self.api_url}/users/me",
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
    
    async def fetch_trips(self, access_token: str, limit: int = 50) -> AgentResult:
        """Fetch trip history"""
        
        try:
            response = await self.client.get(
                f"{self.api_url}/reservations",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": limit, "role": "guest"}
            )
            
            if response.status_code == 200:
                trips = response.json()
                return AgentResult(
                    success=True,
                    data=trips,
                    metadata={'agent': self.metadata.name, 'count': len(trips.get('reservations', []))}
                )
            else:
                return AgentResult(
                    success=False,
                    data={},
                    metadata={'agent': self.metadata.name, 'error': 'Failed to fetch trips'}
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
