"""
QuickBooks Connector Agent - QuickBooks-specific API guidance and support
"""

from typing import Dict, Any
from ....base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class QuickBooksConnectorAgent(Layer1Agent):
    """QuickBooks platform-specific connector for accounting and invoicing"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="quickbooks_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="QuickBooks API, invoice sync, and accounting integration",
            capabilities=["quickbooks_api", "invoice_sync", "expense_tracking", "pl_reports", "tax_categories"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract data from QuickBooks API"""
        query_type = raw_data.get('query_type', 'general')
        
        if query_type == 'authentication':
            return AgentResult(
                success=True,
                data={
                    'platform': 'QuickBooks',
                    'auth_guide': {
                        'type': 'OAuth 2.0',
                        'scopes': ['com.intuit.quickbooks.accounting'],
                        'endpoints': {
                            'auth': 'https://appcenter.intuit.com/connect/oauth2',
                            'token': 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
                        }
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        elif query_type == 'invoices':
            return AgentResult(
                success=True,
                data={
                    'platform': 'QuickBooks',
                    'invoice_guide': {
                        'endpoint': '/v3/company/{realmId}/invoice',
                        'methods': ['create', 'read', 'update', 'delete'],
                        'example': 'POST /v3/company/123456/invoice'
                    }
                },
                metadata={'agent': self.metadata.name}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    'platform': 'QuickBooks',
                    'message': 'I can help with QuickBooks API, invoices, and accounting integration.'
                },
                metadata={'agent': self.metadata.name}
            )
