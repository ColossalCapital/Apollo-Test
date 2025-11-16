"""
Google Maps Connector Agent - Google Maps API Integration

Connector agent that integrates with Google Maps API for location data.
"""

from typing import Dict, Any
from ..base import ConnectorAgent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx


class GoogleMapsConnectorAgent(ConnectorAgent):
    """
    Google Maps Connector - Location and travel data integration
    
    Provides:
    - Location history
    - Timeline data
    - Place visits
    - Travel patterns
    - Saved places
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.api_url = "https://maps.googleapis.com/maps/api"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="google_maps_connector",
            layer=AgentLayer.CONNECTOR,
            version="1.0.0",
            description="Google Maps API integration for location and travel data",
            capabilities=[
                "location_history",
                "timeline_data",
                "place_visits",
                "travel_patterns",
                "saved_places"
            ],
            dependencies=[],
            
            # Metadata for filtering
            entity_types=[EntityType.PERSONAL],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=True,
            wtf_purchasable=False,
            required_credentials=["api_key"]
        )
    
    async def connect(self, credentials: Dict[str, str]) -> AgentResult:
        """Connect to Google Maps API"""
        
        api_key = credentials.get('api_key')
        
        try:
            # Test connection with a simple geocoding request
            response = await self.client.get(
                f"{self.api_url}/geocode/json",
                params={"address": "1600 Amphitheatre Parkway, Mountain View, CA", "key": api_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    return AgentResult(
                        success=True,
                        data={"status": "connected"},
                        metadata={'agent': self.metadata.name}
                    )
            
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
    
    async def fetch_location_history(self, api_key: str, start_date: str, end_date: str) -> AgentResult:
        """Fetch location history (requires Google Takeout data)"""
        
        try:
            # Note: Google Maps Timeline API is not publicly available
            # Users need to export data via Google Takeout
            # This would process the exported JSON data
            
            return AgentResult(
                success=True,
                data={"message": "Use Google Takeout to export location history"},
                metadata={'agent': self.metadata.name}
            )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
