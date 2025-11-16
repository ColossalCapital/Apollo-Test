"""
Uber Connector Agent - Uber API Integration

Maintains Uber API connector for ride history and expense tracking.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class UberConnectorAgent(Layer1Agent):
    """Uber API connector"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/uber"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="uber_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Uber connector - ride history and expense tracking",
            capabilities=[
                "ride_history",
                "expense_tracking",
                "route_analysis",
                "business_vs_personal",
                "receipt_extraction"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Uber connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Uber',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'endpoints': ['Uber API'],
                        'required': ['Uber Account', 'API Access'],
                        'scopes': ['history', 'profile', 'places']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Uber',
                    'sync_modes': {
                        'pull': 'Fetch ride history',
                        'webhooks': 'Trip completion notifications'
                    },
                    'entities': {
                        'trips': 'All ride history',
                        'receipts': 'Digital receipts',
                        'routes': 'Pickup and dropoff locations',
                        'expenses': 'Cost breakdown',
                        'drivers': 'Driver ratings',
                        'payment': 'Payment methods used'
                    },
                    'categorization': {
                        'business_rides': 'Auto-categorize for tax deduction',
                        'personal_rides': 'Personal expense tracking',
                        'commute_patterns': 'Identify regular routes'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Uber',
                    'message': 'Uber connector for ride tracking'
                },
                metadata={'agent': self.metadata.name}
            )
