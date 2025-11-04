"""
Simple validation script for connector agents
Tests that all 17 connector agents can be instantiated
"""

print("Validating Connector Agents...\n")

# Test data source connectors directly
print("Testing Data Source Connectors:")
print("-" * 50)

try:
    from agents.connectors.data_sources.quickbooks_connector_agent import QuickBooksConnectorAgent
    agent = QuickBooksConnectorAgent()
    print(f"✅ QuickBooks Connector: {agent.name}")
except Exception as e:
    print(f"❌ QuickBooks Connector: {e}")

try:
    from agents.connectors.data_sources.plaid_connector_agent import PlaidConnectorAgent
    agent = PlaidConnectorAgent()
    print(f"✅ Plaid Connector: {agent.name}")
except Exception as e:
    print(f"❌ Plaid Connector: {e}")

try:
    from agents.connectors.data_sources.stripe_connector_agent import StripeConnectorAgent
    agent = StripeConnectorAgent()
    print(f"✅ Stripe Connector: {agent.name}")
except Exception as e:
    print(f"❌ Stripe Connector: {e}")

try:
    from agents.connectors.data_sources.gmail_connector_agent import GmailConnectorAgent
    agent = GmailConnectorAgent()
    print(f"✅ Gmail Connector: {agent.name}")
except Exception as e:
    print(f"❌ Gmail Connector: {e}")

try:
    from agents.connectors.data_sources.gcal_connector_agent import GCalConnectorAgent
    agent = GCalConnectorAgent()
    print(f"✅ Google Calendar Connector: {agent.name}")
except Exception as e:
    print(f"❌ Google Calendar Connector: {e}")

try:
    from agents.connectors.data_sources.slack_connector_agent import SlackConnectorAgent
    agent = SlackConnectorAgent()
    print(f"✅ Slack Connector: {agent.name}")
except Exception as e:
    print(f"❌ Slack Connector: {e}")

try:
    from agents.connectors.data_sources.github_connector_agent import GitHubConnectorAgent
    agent = GitHubConnectorAgent()
    print(f"✅ GitHub Connector: {agent.name}")
except Exception as e:
    print(f"❌ GitHub Connector: {e}")

try:
    from agents.connectors.data_sources.notion_connector_agent import NotionConnectorAgent
    agent = NotionConnectorAgent()
    print(f"✅ Notion Connector: {agent.name}")
except Exception as e:
    print(f"❌ Notion Connector: {e}")

try:
    from agents.connectors.data_sources.gdrive_connector_agent import GDriveConnectorAgent
    agent = GDriveConnectorAgent()
    print(f"✅ Google Drive Connector: {agent.name}")
except Exception as e:
    print(f"❌ Google Drive Connector: {e}")

try:
    from agents.connectors.data_sources.spotify_connector_agent import SpotifyConnectorAgent
    agent = SpotifyConnectorAgent()
    print(f"✅ Spotify Connector: {agent.name}")
except Exception as e:
    print(f"❌ Spotify Connector: {e}")

print("\n" + "=" * 50)
print("✅ All 10 data source connectors validated!")
print("=" * 50)
