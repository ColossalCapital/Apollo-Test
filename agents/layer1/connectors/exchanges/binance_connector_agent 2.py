"""
Binance Connector Agent - Binance-specific API guidance and support
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class BinanceConnectorAgent(BaseAgent):
    """
    Binance platform-specific connector.
    
    Provides guidance on:
    - Binance API integration
    - Spot, futures, and margin trading
    - WebSocket streams
    - Trading pairs and fee structure
    """
    
    def __init__(self):
        super().__init__(
            name="Binance Connector",
            description="Binance API, spot/futures trading, and WebSocket streams",
            capabilities=[
                "Binance API",
                "Spot Trading",
                "Futures Trading",
                "Margin Trading",
                "WebSocket Streams"
            ]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Binance-specific queries"""
        query_type = data.get('query_type', 'general')
        query = data.get('query', '')
        
        if 'auth' in query.lower() or query_type == 'authentication':
            return self._auth_help(data)
        elif 'futures' in query.lower() or query_type == 'futures':
            return self._futures_help(data)
        elif 'stream' in query.lower() or query_type == 'streaming':
            return self._streaming_help(data)
        elif 'rate' in query.lower() or query_type == 'rate_limits':
            return self._rate_limits_help(data)
        else:
            return self._general_help(data)
    
    def _auth_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """API key authentication guidance"""
        return {
            'status': 'success',
            'platform': 'Binance',
            'auth_guide': {
                'type': 'API Key + HMAC SHA256 Signature',
                'steps': [
                    '1. Log in to Binance account',
                    '2. Go to API Management',
                    '3. Create new API key',
                    '4. Save API Key and Secret Key',
                    '5. Enable required permissions (Read, Spot Trading, Futures, etc.)',
                    '6. Whitelist IP addresses (recommended)',
                    '7. Sign requests with HMAC SHA256'
                ],
                'signature_process': [
                    '1. Create query string from parameters',
                    '2. Add timestamp parameter',
                    '3. Generate HMAC SHA256 signature using secret key',
                    '4. Append signature to request'
                ],
                'code_example': '''
import hmac
import hashlib
import time
import requests

api_key = 'YOUR_API_KEY'
secret_key = 'YOUR_SECRET_KEY'

# Create signature
timestamp = int(time.time() * 1000)
params = f'symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=0.01&price=50000&timestamp={timestamp}'
signature = hmac.new(secret_key.encode(), params.encode(), hashlib.sha256).hexdigest()

# Make request
headers = {'X-MBX-APIKEY': api_key}
url = f'https://api.binance.com/api/v3/order?{params}&signature={signature}'
response = requests.post(url, headers=headers)
'''
            }
        }
    
    def _futures_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Futures trading guidance"""
        return {
            'status': 'success',
            'platform': 'Binance',
            'futures_guide': {
                'types': {
                    'USDⓈ-M Futures': 'Settled in USDT/BUSD',
                    'COIN-M Futures': 'Settled in cryptocurrency'
                },
                'leverage': 'Up to 125x (use cautiously!)',
                'order_types': [
                    'LIMIT - Limit order',
                    'MARKET - Market order',
                    'STOP/STOP_MARKET - Stop loss',
                    'TAKE_PROFIT/TAKE_PROFIT_MARKET - Take profit',
                    'TRAILING_STOP_MARKET - Trailing stop'
                ],
                'position_modes': {
                    'One-way': 'Single position per symbol',
                    'Hedge': 'Long and short positions simultaneously'
                },
                'code_example': '''
# Place futures market order
params = {
    'symbol': 'BTCUSDT',
    'side': 'BUY',
    'type': 'MARKET',
    'quantity': 0.01,
    'timestamp': int(time.time() * 1000)
}

# Set leverage first
leverage_params = {
    'symbol': 'BTCUSDT',
    'leverage': 10,
    'timestamp': int(time.time() * 1000)
}
requests.post('https://fapi.binance.com/fapi/v1/leverage', params=leverage_params)
'''
            }
        }
    
    def _streaming_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """WebSocket streaming guidance"""
        return {
            'status': 'success',
            'platform': 'Binance',
            'streaming_guide': {
                'description': 'Real-time market data via WebSocket',
                'endpoints': {
                    'spot': 'wss://stream.binance.com:9443/ws',
                    'futures': 'wss://fstream.binance.com/ws'
                },
                'streams': [
                    'Trade Streams - <symbol>@trade',
                    'Kline/Candlestick - <symbol>@kline_<interval>',
                    'Individual Symbol Ticker - <symbol>@ticker',
                    'All Market Tickers - !ticker@arr',
                    'Depth Streams - <symbol>@depth',
                    'User Data Streams - Requires listen key'
                ],
                'code_example': '''
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Price: {data['p']}, Quantity: {data['q']}")

# Connect to trade stream
ws_url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
ws = websocket.WebSocketApp(ws_url, on_message=on_message)
ws.run_forever()

# Subscribe to multiple streams
streams = "btcusdt@trade/ethusdt@trade/bnbusdt@ticker"
ws_url = f"wss://stream.binance.com:9443/stream?streams={streams}"
'''
            }
        }
    
    def _rate_limits_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rate limits guidance"""
        return {
            'status': 'success',
            'platform': 'Binance',
            'rate_limits': {
                'description': 'Binance uses weight-based rate limiting',
                'limits': {
                    'requests': '1200 weight per minute',
                    'orders': '10 orders per second, 100,000 per day',
                    'raw_requests': '6100 per 5 minutes'
                },
                'weights': {
                    'GET /api/v3/ticker/price': 2,
                    'GET /api/v3/depth': '1-100 depending on limit',
                    'POST /api/v3/order': 1,
                    'GET /api/v3/account': 10
                },
                'headers': {
                    'X-MBX-USED-WEIGHT': 'Current weight used',
                    'X-MBX-ORDER-COUNT': 'Current order count'
                },
                'best_practices': [
                    'Monitor rate limit headers in responses',
                    'Use WebSocket for real-time data instead of polling',
                    'Batch requests when possible',
                    'Implement exponential backoff on 429 errors',
                    'Cache data when appropriate'
                ]
            }
        }
    
    def _general_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """General Binance help"""
        return {
            'status': 'success',
            'platform': 'Binance',
            'message': 'I can help with Binance API, spot/futures trading, WebSocket streams, and rate limits.',
            'example_questions': [
                'How do I authenticate with Binance API?',
                'How do I trade futures on Binance?',
                'How do I use WebSocket streams?',
                'What are the rate limits?',
                'How do I set leverage?'
            ],
            'key_features': [
                'Largest crypto exchange by volume',
                'Spot, futures, and margin trading',
                'Low fees (0.1% spot, 0.02% futures with BNB)',
                'High liquidity',
                'Advanced order types',
                'Real-time WebSocket streams'
            ],
            'important_notes': [
                'Use Binance.US if in the United States',
                'Enable 2FA for security',
                'Whitelist IP addresses for API keys',
                'Start with testnet for testing'
            ]
        }
