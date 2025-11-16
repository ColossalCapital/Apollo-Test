"""
Charles Schwab Connector Agent - Schwab-specific API guidance and support
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class SchwabConnectorAgent(BaseAgent):
    """
    Charles Schwab platform-specific connector.
    
    Provides guidance on:
    - Schwab API integration
    - StreetSmart Edge integration
    - Fractional shares
    - API authentication
    """
    
    def __init__(self):
        super().__init__(
            name="Schwab Connector",
            description="Charles Schwab API, StreetSmart Edge, and platform guidance",
            capabilities=[
                "Schwab API Integration",
                "StreetSmart Edge",
                "Fractional Shares",
                "API Authentication"
            ]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Schwab-specific queries"""
        query_type = data.get('query_type', 'general')
        query = data.get('query', '')
        
        if 'auth' in query.lower() or query_type == 'authentication':
            return self._auth_help(data)
        elif 'fractional' in query.lower() or query_type == 'fractional':
            return self._fractional_help(data)
        elif 'order' in query.lower() or query_type == 'orders':
            return self._order_help(data)
        else:
            return self._general_help(data)
    
    def _auth_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """OAuth authentication guidance"""
        return {
            'status': 'success',
            'platform': 'Charles Schwab',
            'auth_guide': {
                'type': 'OAuth 2.0',
                'note': 'Schwab acquired TD Ameritrade - API migration in progress',
                'steps': [
                    '1. Register app at Schwab Developer Portal',
                    '2. Get App Key and Secret',
                    '3. Implement OAuth 2.0 flow',
                    '4. Exchange authorization code for tokens',
                    '5. Use refresh token for new access tokens'
                ],
                'endpoints': {
                    'authorization': 'https://api.schwabapi.com/v1/oauth/authorize',
                    'token': 'https://api.schwabapi.com/v1/oauth/token'
                },
                'migration_note': 'TD Ameritrade customers: Migrate to Schwab API by March 2026'
            }
        }
    
    def _fractional_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fractional shares guidance"""
        return {
            'status': 'success',
            'platform': 'Charles Schwab',
            'fractional_guide': {
                'description': 'Schwab Stock Slices - Buy fractional shares for as little as $5',
                'supported_stocks': 'S&P 500 stocks',
                'minimum_investment': '$5',
                'how_to_order': [
                    '1. Specify dollar amount instead of shares',
                    '2. Use orderType: DOLLAR_BASED',
                    '3. Set quantity as dollar amount',
                    '4. Submit order during market hours'
                ],
                'limitations': [
                    'Only available for S&P 500 stocks',
                    'Market orders only (no limit orders)',
                    'Only during regular market hours'
                ]
            }
        }
    
    def _order_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Order placement guidance"""
        return {
            'status': 'success',
            'platform': 'Charles Schwab',
            'order_guide': {
                'order_types': [
                    'Market',
                    'Limit',
                    'Stop',
                    'Stop Limit',
                    'Trailing Stop'
                ],
                'time_in_force': [
                    'DAY - Good for day',
                    'GTC - Good till canceled',
                    'FOK - Fill or kill',
                    'IOC - Immediate or cancel'
                ],
                'code_example': '''
# Place market order
order = {
    "orderType": "MARKET",
    "session": "NORMAL",
    "duration": "DAY",
    "orderStrategyType": "SINGLE",
    "orderLegCollection": [{
        "instruction": "BUY",
        "quantity": 10,
        "instrument": {
            "symbol": "AAPL",
            "assetType": "EQUITY"
        }
    }]
}
'''
            }
        }
    
    def _general_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """General Schwab help"""
        return {
            'status': 'success',
            'platform': 'Charles Schwab',
            'message': 'I can help with Schwab API, OAuth, fractional shares, and order placement.',
            'example_questions': [
                'How do I authenticate with Schwab API?',
                'How do I buy fractional shares?',
                'What order types does Schwab support?',
                'How do I migrate from TD Ameritrade?'
            ],
            'important_notes': [
                'Schwab acquired TD Ameritrade in 2020',
                'TD API will be deprecated - migrate to Schwab API',
                'Fractional shares available for S&P 500 stocks'
            ]
        }
