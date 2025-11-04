"""
TD Ameritrade Connector Agent - TD-specific API guidance and support
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class TDConnectorAgent(BaseAgent):
    """
    TD Ameritrade platform-specific connector.
    
    Provides guidance on:
    - TD Ameritrade API integration
    - thinkorswim integration
    - Options chains
    - Streaming data
    - Account management
    """
    
    def __init__(self):
        super().__init__(
            name="TD Connector",
            description="TD Ameritrade API, thinkorswim integration, and platform guidance",
            capabilities=[
                "TD API Integration",
                "thinkorswim",
                "Options Chains",
                "Streaming Data",
                "Account Management"
            ]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process TD-specific queries"""
        query_type = data.get('query_type', 'general')
        query = data.get('query', '')
        
        if 'auth' in query.lower() or query_type == 'authentication':
            return self._auth_help(data)
        elif 'option' in query.lower() or query_type == 'options':
            return self._options_help(data)
        elif 'stream' in query.lower() or query_type == 'streaming':
            return self._streaming_help(data)
        elif 'error' in query.lower() or query_type == 'error':
            return self._error_help(data)
        else:
            return self._general_help(data)
    
    def _auth_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """OAuth authentication guidance"""
        return {
            'status': 'success',
            'platform': 'TD Ameritrade',
            'auth_guide': {
                'type': 'OAuth 2.0',
                'steps': [
                    '1. Create app at https://developer.tdameritrade.com',
                    '2. Get Client ID (Consumer Key)',
                    '3. Set redirect URI (e.g., https://localhost)',
                    '4. Build authorization URL',
                    '5. User authorizes and gets auth code',
                    '6. Exchange auth code for access token',
                    '7. Use refresh token for new access tokens'
                ],
                'scopes': ['PlaceTrades', 'AccountAccess', 'MoveMoney'],
                'token_lifetime': {
                    'access_token': '30 minutes',
                    'refresh_token': '90 days'
                },
                'code_example': '''
import requests

# Step 1: Authorization URL
auth_url = f"https://auth.tdameritrade.com/auth?response_type=code&redirect_uri={redirect_uri}&client_id={client_id}%40AMER.OAUTHAP"

# Step 2: Exchange code for token
token_url = "https://api.tdameritrade.com/v1/oauth2/token"
data = {
    'grant_type': 'authorization_code',
    'access_type': 'offline',
    'code': auth_code,
    'client_id': client_id,
    'redirect_uri': redirect_uri
}
response = requests.post(token_url, data=data)
tokens = response.json()
'''
            }
        }
    
    def _options_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Options chain guidance"""
        return {
            'status': 'success',
            'platform': 'TD Ameritrade',
            'options_guide': {
                'endpoint': '/v1/marketdata/chains',
                'parameters': {
                    'symbol': 'Stock symbol (e.g., AAPL)',
                    'contractType': 'CALL, PUT, or ALL',
                    'strikeCount': 'Number of strikes',
                    'range': 'ITM, OTM, NTM, SAK, SBK, SNK, ALL'
                },
                'code_example': '''
# Get options chain
url = f"https://api.tdameritrade.com/v1/marketdata/chains"
params = {
    'apikey': client_id,
    'symbol': 'AAPL',
    'contractType': 'CALL',
    'strikeCount': 10,
    'range': 'OTM'
}
response = requests.get(url, params=params)
chain = response.json()
'''
            }
        }
    
    def _streaming_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Streaming data guidance"""
        return {
            'status': 'success',
            'platform': 'TD Ameritrade',
            'streaming_guide': {
                'description': 'Real-time market data via WebSocket',
                'steps': [
                    '1. Get streaming credentials from /userprincipals endpoint',
                    '2. Connect to WebSocket URL',
                    '3. Send login request with credentials',
                    '4. Subscribe to desired services (QUOTE, CHART, etc.)',
                    '5. Handle incoming messages'
                ],
                'services': [
                    'QUOTE - Level 1 quotes',
                    'OPTION - Options quotes',
                    'CHART_EQUITY - Chart data',
                    'TIMESALE_EQUITY - Time & sales',
                    'ACTIVES_NASDAQ - Most active stocks'
                ]
            }
        }
    
    def _error_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Error resolution"""
        error_code = data.get('error_code', 'unknown')
        
        errors = {
            '401': {
                'message': 'Unauthorized - Invalid or expired token',
                'solution': 'Refresh access token using refresh token'
            },
            '403': {
                'message': 'Forbidden - Insufficient permissions',
                'solution': 'Check OAuth scopes and account permissions'
            },
            '429': {
                'message': 'Too many requests',
                'solution': 'Implement rate limiting (120 requests/minute)'
            }
        }
        
        return {
            'status': 'success',
            'platform': 'TD Ameritrade',
            'error_info': errors.get(str(error_code), {
                'message': f'Error {error_code}',
                'solution': 'Check TD API documentation'
            })
        }
    
    def _general_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """General TD help"""
        return {
            'status': 'success',
            'platform': 'TD Ameritrade',
            'message': 'I can help with TD Ameritrade API, OAuth, options chains, and streaming data.',
            'example_questions': [
                'How do I authenticate with TD Ameritrade?',
                'How do I get options chains?',
                'How do I use streaming data?',
                'What are the rate limits?'
            ],
            'important_note': 'TD Ameritrade API v1 is being deprecated. Migrate to Schwab API by March 2026.'
        }
