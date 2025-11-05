"""
Amazon Connector Agent - Amazon API Integration

Maintains Amazon API connector for order history and purchase tracking.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class AmazonConnectorAgent(Layer1Agent):
    """Amazon API connector"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_connector_url = "http://localhost:8091/connectors/amazon"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="amazon_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Amazon connector - order history and purchase tracking",
            capabilities=[
                "order_sync",
                "purchase_tracking",
                "expense_categorization",
                "product_history",
                "subscription_tracking"
            ],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Process Amazon connector queries"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Amazon',
                    'auth_guide': {
                        'type': 'OAuth 2.0 + Scraping',
                        'endpoints': ['Amazon Advertising API', 'Web Scraping'],
                        'required': ['Amazon Account', 'Login Credentials'],
                        'note': 'Amazon has limited API access, may require scraping'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'sync_capabilities':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Amazon',
                    'sync_modes': {
                        'pull': 'Fetch order history',
                        'email_parsing': 'Parse Amazon confirmation emails'
                    },
                    'entities': {
                        'orders': 'All purchase history',
                        'products': 'Product details and categories',
                        'expenses': 'Total spending by category',
                        'subscriptions': 'Subscribe & Save items',
                        'returns': 'Return history',
                        'reviews': 'Your product reviews'
                    },
                    'categorization': {
                        'business_expenses': 'Office supplies, equipment',
                        'personal_purchases': 'Personal items',
                        'spending_patterns': 'Category-based analysis'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Amazon',
                    'message': 'Amazon connector for purchase tracking'
                },
                metadata={'agent': self.metadata.name}
            )
