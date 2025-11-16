"""
Connector Agents - Platform-specific integration agents

Reorganized structure:
- brokerages/: Trading brokerages (IB, TD, Schwab, Alpaca)
- exchanges/: Major crypto exchanges (Binance, Coinbase, Kraken)
- market_data/: Market data providers (24 connectors)
- financial/: Financial services (QuickBooks, Plaid, Stripe, InvestorProfiles, NewsSentiment)
- communication/: Email, calendar, messaging (Gmail, GCal, Slack)
- productivity/: Docs, code, storage (GitHub, Notion, GDrive, Spotify)
"""

# Brokerages
from .brokerages.ib_connector_agent import IBConnectorAgent
from .brokerages.td_connector_agent import TDConnectorAgent
from .brokerages.schwab_connector_agent import SchwabConnectorAgent
from .brokerages.alpaca_connector_agent import AlpacaConnectorAgent

# Exchanges
from .exchanges.binance_connector_agent import BinanceConnectorAgent
from .exchanges.coinbase_connector_agent import CoinbaseConnectorAgent
from .exchanges.kraken_connector_agent import KrakenConnectorAgent

# Financial
from .financial.quickbooks_connector_agent import QuickBooksConnectorAgent
from .financial.plaid_connector_agent import PlaidConnectorAgent
from .financial.stripe_connector_agent import StripeConnectorAgent
from .financial.investor_profiles_connector_agent import InvestorProfilesConnectorAgent
from .financial.news_sentiment_connector_agent import NewsSentimentConnectorAgent

# Communication
from .communication.gmail_connector_agent import GmailConnectorAgent
from .communication.gcal_connector_agent import GCalConnectorAgent
from .communication.slack_connector_agent import SlackConnectorAgent

# Productivity
from .productivity.github_connector_agent import GitHubConnectorAgent
from .productivity.notion_connector_agent import NotionConnectorAgent
from .productivity.gdrive_connector_agent import GDriveConnectorAgent
from .productivity.spotify_connector_agent import SpotifyConnectorAgent

__all__ = [
    # Brokerages
    'IBConnectorAgent',
    'TDConnectorAgent',
    'SchwabConnectorAgent',
    'AlpacaConnectorAgent',
    # Exchanges
    'BinanceConnectorAgent',
    'CoinbaseConnectorAgent',
    'KrakenConnectorAgent',
    # Financial
    'QuickBooksConnectorAgent',
    'PlaidConnectorAgent',
    'StripeConnectorAgent',
    'InvestorProfilesConnectorAgent',
    'NewsSentimentConnectorAgent',
    # Communication
    'GmailConnectorAgent',
    'GCalConnectorAgent',
    'SlackConnectorAgent',
    # Productivity
    'GitHubConnectorAgent',
    'NotionConnectorAgent',
    'GDriveConnectorAgent',
    'SpotifyConnectorAgent',
]
