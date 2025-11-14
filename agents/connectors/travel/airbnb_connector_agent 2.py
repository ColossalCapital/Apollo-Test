"""
Airbnb Connector Agent - Airbnb API Integration

Maintains Airbnb API connector for trip history and reservations.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class AirbnbConnectorAgent(Layer1Agent):
    """Airbnb API connector"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/airbnb"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="airbnb_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Airbnb connector - trip history and reservations",
            capabilities=[
                "booking_sync",
                "itinerary_extraction",
                "expense_tracking",
                "property_history",
                "review_tracking"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Airbnb connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Airbnb',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'endpoints': ['Airbnb API'],
                        'required': ['Airbnb Account', 'API Access'],
                        'scopes': ['reservations', 'profile', 'reviews']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Airbnb',
                    'sync_modes': {
                        'pull': 'Fetch bookings and trips',
                        'webhooks': 'Booking confirmation notifications'
                    },
                    'entities': {
                        'reservations': 'Past and upcoming bookings',
                        'properties': 'Properties visited',
                        'itineraries': 'Check-in/out dates and locations',
                        'expenses': 'Total costs and breakdowns',
                        'reviews': 'Your reviews and ratings',
                        'hosts': 'Host information'
                    },
                    'travel_intelligence': {
                        'trip_timeline': 'Complete travel history',
                        'expense_categorization': 'Business vs personal travel',
                        'location_tracking': 'Places visited worldwide'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Airbnb',
                    'message': 'Airbnb connector for travel tracking'
                },
                metadata={'agent': self.metadata.name}
            )
