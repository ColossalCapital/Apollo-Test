"""
Plaid Connector Agent - Plaid-specific API guidance and support
"""

from typing import Dict, Any
from ....base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class PlaidConnectorAgent(Layer1Agent):
    """Plaid platform-specific connector for bank account linking"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="plaid_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Plaid Link, bank connections, and transaction sync",
            capabilities=["plaid_link", "bank_connections", "transaction_sync", "balance_checks", "identity_verification"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract data from Plaid API"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Plaid',
                    'auth_guide': {
                        'type': 'API Keys (client_id + secret)',
                        'environments': ['sandbox', 'development', 'production'],
                        'link_token': 'Required for Plaid Link initialization'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'link':
            return AgentResult(
                success=True,
                data={
                    'platform': 'Plaid',
                    'link_guide': {
                        'flow': ['Create link_token', 'Initialize Plaid Link', 'Exchange public_token', 'Get access_token'],
                        'products': ['transactions', 'auth', 'identity', 'balance', 'investments']
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'Plaid',
                    'message': 'I can help with Plaid Link, bank connections, and transaction syncing.'
                },
                metadata={'agent': self.metadata.name}
            )
