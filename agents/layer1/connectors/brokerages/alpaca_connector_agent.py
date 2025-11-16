"""
Alpaca Connector Agent - Alpaca-specific API guidance and support
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class AlpacaConnectorAgent(BaseAgent):
    """
    Alpaca platform-specific connector.
    
    Provides guidance on:
    - Alpaca API v2
    - Paper trading
    - Algorithmic trading
    - WebSocket streaming
    """
    
    def __init__(self):
        super().__init__(
            name="Alpaca Connector",
            description="Alpaca API v2, paper trading, and algorithmic trading",
            capabilities=[
                "Alpaca API v2",
                "Paper Trading",
                "Algorithmic Trading",
                "WebSocket Streaming"
            ]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Alpaca-specific queries"""
        query_type = data.get('query_type', 'general')
        query = data.get('query', '')
        
        if 'auth' in query.lower() or query_type == 'authentication':
            return self._auth_help(data)
        elif 'paper' in query.lower() or query_type == 'paper_trading':
            return self._paper_trading_help(data)
        elif 'stream' in query.lower() or query_type == 'streaming':
            return self._streaming_help(data)
        elif 'order' in query.lower() or query_type == 'orders':
            return self._order_help(data)
        else:
            return self._general_help(data)
    
    def _auth_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """API key authentication guidance"""
        return {
            'status': 'success',
            'platform': 'Alpaca',
            'auth_guide': {
                'type': 'API Key Authentication',
                'steps': [
                    '1. Sign up at alpaca.markets',
                    '2. Generate API keys in dashboard',
                    '3. Get API Key ID and Secret Key',
                    '4. Use keys in headers for all requests'
                ],
                'headers': {
                    'APCA-API-KEY-ID': 'Your API Key ID',
                    'APCA-API-SECRET-KEY': 'Your Secret Key'
                },
                'endpoints': {
                    'live': 'https://api.alpaca.markets',
                    'paper': 'https://paper-api.alpaca.markets',
                    'data': 'https://data.alpaca.markets'
                },
                'code_example': '''
import alpaca_trade_api as tradeapi

# Initialize API
api = tradeapi.REST(
    key_id='YOUR_API_KEY',
    secret_key='YOUR_SECRET_KEY',
    base_url='https://paper-api.alpaca.markets'  # or live
)

# Get account info
account = api.get_account()
'''
            }
        }
    
    def _paper_trading_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Paper trading guidance"""
        return {
            'status': 'success',
            'platform': 'Alpaca',
            'paper_trading_guide': {
                'description': 'Free paper trading with $100,000 virtual cash',
                'features': [
                    'Same API as live trading',
                    'Real-time market data',
                    'Test algorithms risk-free',
                    'Reset account anytime'
                ],
                'how_to_use': [
                    '1. Use paper trading endpoint: paper-api.alpaca.markets',
                    '2. Use paper trading API keys (different from live)',
                    '3. All features identical to live trading',
                    '4. Reset account in dashboard if needed'
                ],
                'limitations': [
                    'Virtual money only',
                    'No real profit/loss',
                    'Some market impact simulation differences'
                ]
            }
        }
    
    def _streaming_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """WebSocket streaming guidance"""
        return {
            'status': 'success',
            'platform': 'Alpaca',
            'streaming_guide': {
                'description': 'Real-time market data and account updates via WebSocket',
                'streams': {
                    'trades': 'Real-time trade data',
                    'quotes': 'Real-time quote data',
                    'bars': 'Real-time bar data',
                    'account_updates': 'Account and order updates'
                },
                'code_example': '''
from alpaca_trade_api.stream import Stream

async def trade_callback(trade):
    print(f"Trade: {trade}")

# Initialize stream
stream = Stream(
    key_id='YOUR_API_KEY',
    secret_key='YOUR_SECRET_KEY',
    data_feed='iex'  # or 'sip' for full market data
)

# Subscribe to trades
stream.subscribe_trades(trade_callback, 'AAPL')

# Run stream
stream.run()
'''
            }
        }
    
    def _order_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Order placement guidance"""
        return {
            'status': 'success',
            'platform': 'Alpaca',
            'order_guide': {
                'order_types': [
                    'market - Execute at current market price',
                    'limit - Execute at specified price or better',
                    'stop - Trigger market order at stop price',
                    'stop_limit - Trigger limit order at stop price',
                    'trailing_stop - Dynamic stop based on price movement'
                ],
                'time_in_force': [
                    'day - Good for day',
                    'gtc - Good till canceled',
                    'ioc - Immediate or cancel',
                    'fok - Fill or kill'
                ],
                'code_example': '''
# Submit market order
api.submit_order(
    symbol='AAPL',
    qty=10,
    side='buy',
    type='market',
    time_in_force='day'
)

# Submit limit order
api.submit_order(
    symbol='AAPL',
    qty=10,
    side='buy',
    type='limit',
    time_in_force='gtc',
    limit_price=150.00
)

# Bracket order (entry + profit target + stop loss)
api.submit_order(
    symbol='AAPL',
    qty=10,
    side='buy',
    type='market',
    time_in_force='gtc',
    order_class='bracket',
    take_profit={'limit_price': 155.00},
    stop_loss={'stop_price': 145.00}
)
'''
            }
        }
    
    def _general_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """General Alpaca help"""
        return {
            'status': 'success',
            'platform': 'Alpaca',
            'message': 'I can help with Alpaca API, paper trading, streaming data, and algorithmic trading.',
            'example_questions': [
                'How do I authenticate with Alpaca?',
                'How do I use paper trading?',
                'How do I stream real-time data?',
                'How do I place a bracket order?'
            ],
            'key_features': [
                'Commission-free trading',
                'Free paper trading',
                'Real-time and historical data',
                'WebSocket streaming',
                'Fractional shares',
                'Perfect for algo trading'
            ]
        }
