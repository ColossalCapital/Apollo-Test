"""
Strava Connector Agent - Strava API Integration

Maintains Strava API connector for cycling and running activities.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class StravaConnectorAgent(Layer1Agent):
    """Strava API connector"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/strava"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="strava_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Strava connector - cycling, running, social fitness",
            capabilities=[
                "activity_sync",
                "route_analysis",
                "segment_times",
                "social_features"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Strava connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Strava',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'endpoints': ['Strava API v3'],
                        'required': ['Client ID', 'Client Secret'],
                        'scopes': ['activity:read_all', 'profile:read_all']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Strava',
                    'sync_modes': {
                        'pull': 'Fetch activities and routes',
                        'webhooks': 'Real-time activity updates'
                    },
                    'entities': {
                        'activities': 'Runs, rides, swims',
                        'routes': 'GPS tracks and elevation',
                        'segments': 'Segment times and leaderboards',
                        'gear': 'Equipment tracking',
                        'kudos': 'Social interactions'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Strava',
                    'message': 'Strava connector for social fitness'
                },
                metadata={'agent': self.metadata.name}
            )
