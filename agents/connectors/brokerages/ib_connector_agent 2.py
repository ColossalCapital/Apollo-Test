"""
Interactive Brokers Connector Agent - IB-specific TWS API guidance and support
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class IBConnectorAgent(BaseAgent):
    """
    Interactive Brokers platform-specific connector.
    
    Provides guidance on:
    - TWS API integration
    - IB order types (Bracket, OCA, etc.)
    - Margin requirements
    - Gateway connection
    - Market data subscriptions
    - IB-specific error codes
    """
    
    def __init__(self):
        super().__init__(
            name="IB Connector",
            description="Interactive Brokers TWS API, order types, and platform-specific guidance",
            capabilities=[
                "TWS API Integration",
                "IB Order Types",
                "Margin Requirements",
                "Gateway Connection",
                "Market Data Subscriptions",
                "Error Code Resolution"
            ]
        )
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process IB-specific queries.
        
        Supported queries:
        - how_to_place_order: Guide for placing specific order types
        - margin_requirements: Get margin requirements
        - error_code: Explain IB error codes
        - connection_help: Help with TWS/Gateway connection
        - market_data: Market data subscription help
        """
        query_type = data.get('query_type', 'general')
        query = data.get('query', '')
        
        if 'order' in query.lower() or query_type == 'how_to_place_order':
            return self._order_guidance(data)
        elif 'margin' in query.lower() or query_type == 'margin_requirements':
            return self._margin_info(data)
        elif 'error' in query.lower() or query_type == 'error_code':
            return self._error_code_help(data)
        elif 'connect' in query.lower() or query_type == 'connection_help':
            return self._connection_help(data)
        elif 'data' in query.lower() or query_type == 'market_data':
            return self._market_data_help(data)
        else:
            return self._general_help(data)
    
    def _order_guidance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on placing orders"""
        order_type = data.get('order_type', 'bracket').lower()
        
        guides = {
            'bracket': {
                'description': 'Bracket orders combine a parent order with profit target and stop loss',
                'steps': [
                    '1. Create parent order (BUY/SELL)',
                    '2. Set profit target (LIMIT order)',
                    '3. Set stop loss (STOP order)',
                    '4. Submit as bracket order'
                ],
                'code_example': '''
from ib_insync import *

# Connect to TWS
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Create bracket order
contract = Stock('AAPL', 'SMART', 'USD')
parent = MarketOrder('BUY', 100)
takeProfit = LimitOrder('SELL', 100, limitPrice=155.0)
stopLoss = StopOrder('SELL', 100, stopPrice=145.0)

bracket = ib.bracketOrder(parent, takeProfit, stopLoss)
for o in bracket:
    ib.placeOrder(contract, o)
''',
                'common_errors': [
                    'Error 201: Order rejected - check margin requirements',
                    'Error 110: Price does not conform to minimum price variation'
                ]
            },
            'oca': {
                'description': 'One-Cancels-All: Multiple orders where filling one cancels others',
                'steps': [
                    '1. Create multiple orders',
                    '2. Assign same OCA group ID',
                    '3. Set OCA type (Cancel with Block, Reduce with Block, etc.)',
                    '4. Submit orders'
                ],
                'code_example': '''
# OCA Order Example
order1 = LimitOrder('BUY', 100, limitPrice=150.0)
order2 = LimitOrder('BUY', 100, limitPrice=148.0)

# Assign OCA group
oca_group = f"OCA_{int(time.time())}"
order1.ocaGroup = oca_group
order2.ocaGroup = oca_group
order1.ocaType = 1  # Cancel with block

ib.placeOrder(contract, order1)
ib.placeOrder(contract, order2)
'''
            }
        }
        
        guide = guides.get(order_type, {
            'description': f'Order type: {order_type}',
            'message': 'Specific guide not available. Check IB API documentation.'
        })
        
        return {
            'status': 'success',
            'platform': 'Interactive Brokers',
            'order_type': order_type,
            'guide': guide
        }
    
    def _margin_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide margin requirement information"""
        asset_type = data.get('asset_type', 'stock')
        
        margin_info = {
            'stock': {
                'reg_t_margin': '50%',
                'maintenance_margin': '25%',
                'day_trading_buying_power': '4x',
                'notes': 'Pattern day trader rules apply if 4+ day trades in 5 days'
            },
            'option': {
                'long_option': '100% premium',
                'short_option': 'Varies by strategy',
                'spread': 'Max loss of spread',
                'notes': 'Options approval level required'
            }
        }
        
        return {
            'status': 'success',
            'platform': 'Interactive Brokers',
            'asset_type': asset_type,
            'margin_requirements': margin_info.get(asset_type, {})
        }
    
    def _error_code_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Explain IB error codes"""
        error_code = data.get('error_code')
        
        error_codes = {
            '201': {
                'message': 'Order rejected - insufficient margin',
                'solution': 'Reduce order size or add funds to account'
            },
            '110': {
                'message': 'Price does not conform to minimum price variation',
                'solution': 'Adjust limit price to valid increment (e.g., $0.01 for stocks)'
            },
            '162': {
                'message': 'Historical market data Service error',
                'solution': 'Check market data subscriptions'
            },
            '502': {
                'message': 'Couldn\'t connect to TWS',
                'solution': 'Ensure TWS/Gateway is running and API is enabled'
            }
        }
        
        error_info = error_codes.get(str(error_code), {
            'message': f'Error code {error_code}',
            'solution': 'Check IB API documentation or contact support'
        })
        
        return {
            'status': 'success',
            'platform': 'Interactive Brokers',
            'error_code': error_code,
            'error_info': error_info
        }
    
    def _connection_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Help with TWS/Gateway connection"""
        return {
            'status': 'success',
            'platform': 'Interactive Brokers',
            'connection_guide': {
                'steps': [
                    '1. Download and install TWS or IB Gateway',
                    '2. Enable API in TWS: File → Global Configuration → API → Settings',
                    '3. Enable "ActiveX and Socket Clients"',
                    '4. Set Socket port (default: 7497 for TWS, 4001 for Gateway)',
                    '5. Add trusted IP addresses (127.0.0.1 for local)',
                    '6. Restart TWS/Gateway'
                ],
                'common_issues': [
                    {
                        'issue': 'Connection refused',
                        'solution': 'Check if TWS/Gateway is running and API is enabled'
                    },
                    {
                        'issue': 'Already connected',
                        'solution': 'Use different client ID or disconnect existing connection'
                    }
                ],
                'ports': {
                    'TWS_live': 7496,
                    'TWS_paper': 7497,
                    'Gateway_live': 4001,
                    'Gateway_paper': 4002
                }
            }
        }
    
    def _market_data_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Help with market data subscriptions"""
        return {
            'status': 'success',
            'platform': 'Interactive Brokers',
            'market_data_guide': {
                'subscription_types': [
                    'US Securities Snapshot and Futures Value Bundle',
                    'US Equity and Options Add-On Streaming Bundle',
                    'Level II (Market Depth)'
                ],
                'how_to_subscribe': [
                    '1. Log in to Account Management',
                    '2. Go to Settings → User Settings → Market Data Subscriptions',
                    '3. Select desired subscriptions',
                    '4. Accept agreements and submit'
                ],
                'free_data': 'Delayed data (15-20 minutes) available for free',
                'real_time_cost': 'Varies by exchange, typically $1-10/month per exchange'
            }
        }
    
    def _general_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """General IB help"""
        return {
            'status': 'success',
            'platform': 'Interactive Brokers',
            'message': 'I can help with IB-specific questions about orders, margin, connections, and market data.',
            'example_questions': [
                'How do I place a bracket order on IB?',
                'What are the margin requirements for options?',
                'Why am I getting error code 201?',
                'How do I connect to TWS API?',
                'How do I subscribe to real-time market data?'
            ]
        }
