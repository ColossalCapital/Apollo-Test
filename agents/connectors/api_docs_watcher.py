"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Docs Watcher Agent
Monitors API changes using existing connector agents
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

# Import existing connector agents
from agents.connectors.exchanges.coinbase_connector import CoinbaseConnectorAgent
from agents.connectors.exchanges.binance_connector import BinanceConnectorAgent
from agents.connectors.financial.quickbooks_connector import QuickBooksConnectorAgent

from .connector_generator import ConnectorGeneratorAgent


class APIDocsWatcherAgent:
    """
    Monitors API changes using existing connector agents
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.connector_generator = ConnectorGeneratorAgent()
        
        # Load all connector agents
        self.connector_agents = {
            "coinbase": CoinbaseConnectorAgent(),
            "binance": BinanceConnectorAgent(),
            "quickbooks": QuickBooksConnectorAgent(),
            # Add more as needed
        }
        
        print(f"📡 API Docs Watcher initialized with {len(self.connector_agents)} connectors")
    
    async def watch_all_apis(self):
        """Monitor all APIs for changes"""
        print("👁️  Starting API monitoring...")
        
        while True:
            for integration_type, agent in self.connector_agents.items():
                try:
                    await self.check_api_changes(integration_type, agent)
                except Exception as e:
                    print(f"❌ Error checking {integration_type}: {e}")
            
            # Check every hour
            await asyncio.sleep(3600)
    
    async def check_api_changes(self, integration_type: str, agent):
        """Check if API has changed (REST + WebSocket)"""
        
        print(f"🔍 Checking {integration_type} API...")
        
        # 1. Use the connector agent to fetch current API spec
        try:
            current_spec = await agent.get_api_spec()
            current_version = await agent.get_api_version()
            
            # Also fetch WebSocket spec for exchanges
            current_ws_spec = await agent.get_websocket_spec()
        except Exception as e:
            print(f"   ❌ Failed to fetch API spec: {e}")
            return
        
        # 2. Compare with stored spec
        stored_spec = await self._get_stored_spec(integration_type)
        
        if not stored_spec:
            # First time seeing this API
            full_spec = {
                "rest": current_spec,
                "websocket": current_ws_spec,
                "version": current_version
            }
            await self._store_spec(integration_type, full_spec, current_version)
            print(f"   📝 Stored initial API spec for {integration_type}")
            print(f"      REST endpoints: {len(current_spec.get('endpoints', {}))}")
            print(f"      WebSocket channels: {len(current_ws_spec.get('channels', {}))}")
            return
        
        # 3. Detect changes (REST + WebSocket)
        changes = self._detect_changes(stored_spec, {
            "rest": current_spec,
            "websocket": current_ws_spec,
            "version": current_version
        })
        
        if changes:
            print(f"   🚨 API changes detected for {integration_type}!")
            print(f"      {self._format_changes(changes)}")
            
            # 4. Trigger connector regeneration
            await self._trigger_regeneration(
                integration_type=integration_type,
                changes=changes,
                new_spec=current_spec,
                new_ws_spec=current_ws_spec,
                new_version=current_version
            )
            
            # 5. Update stored spec
            full_spec = {
                "rest": current_spec,
                "websocket": current_ws_spec,
                "version": current_version
            }
            await self._store_spec(integration_type, full_spec, current_version)
        else:
            print(f"   ✅ No changes detected for {integration_type}")
    
    def _detect_changes(self, old_spec: dict, new_spec: dict) -> Optional[Dict]:
        """Detect what changed in the API (REST + WebSocket)"""
        
        changes = {
            # REST API changes
            "new_endpoints": [],
            "removed_endpoints": [],
            "modified_endpoints": [],
            
            # WebSocket changes
            "new_ws_channels": [],
            "removed_ws_channels": [],
            "modified_ws_channels": [],
            "ws_message_format_changes": [],
            
            # Common changes
            "auth_changes": False,
            "rate_limit_changes": False,
            "version_change": False
        }
        
        # Extract REST and WebSocket specs
        old_rest = old_spec.get("rest", old_spec)  # Backwards compatibility
        new_rest = new_spec.get("rest", new_spec)
        old_ws = old_spec.get("websocket", {})
        new_ws = new_spec.get("websocket", {})
        
        # Compare REST endpoints
        old_endpoints = set(old_rest.get("endpoints", {}).keys())
        new_endpoints = set(new_rest.get("endpoints", {}).keys())
        
        changes["new_endpoints"] = list(new_endpoints - old_endpoints)
        changes["removed_endpoints"] = list(old_endpoints - new_endpoints)
        
        # Check for REST modifications
        for endpoint in old_endpoints & new_endpoints:
            old_hash = self._hash_dict(old_rest["endpoints"][endpoint])
            new_hash = self._hash_dict(new_rest["endpoints"][endpoint])
            
            if old_hash != new_hash:
                changes["modified_endpoints"].append(endpoint)
        
        # Compare WebSocket channels
        old_channels = set(old_ws.get("channels", {}).keys())
        new_channels = set(new_ws.get("channels", {}).keys())
        
        changes["new_ws_channels"] = list(new_channels - old_channels)
        changes["removed_ws_channels"] = list(old_channels - new_channels)
        
        # Check for WebSocket modifications
        for channel in old_channels & new_channels:
            old_hash = self._hash_dict(old_ws["channels"][channel])
            new_hash = self._hash_dict(new_ws["channels"][channel])
            
            if old_hash != new_hash:
                changes["modified_ws_channels"].append(channel)
        
        # Check WebSocket message format changes
        old_msg_formats = old_ws.get("message_formats", {})
        new_msg_formats = new_ws.get("message_formats", {})
        
        for msg_type in set(old_msg_formats.keys()) | set(new_msg_formats.keys()):
            old_format = old_msg_formats.get(msg_type)
            new_format = new_msg_formats.get(msg_type)
            
            if old_format != new_format:
                changes["ws_message_format_changes"].append(msg_type)
        
        # Check auth changes
        if old_rest.get("auth") != new_rest.get("auth") or old_ws.get("auth") != new_ws.get("auth"):
            changes["auth_changes"] = True
        
        # Check rate limit changes
        if old_rest.get("rate_limits") != new_rest.get("rate_limits") or old_ws.get("rate_limits") != new_ws.get("rate_limits"):
            changes["rate_limit_changes"] = True
        
        # Check version change
        if old_spec.get("version") != new_spec.get("version"):
            changes["version_change"] = True
        
        # Return None if no changes
        if not any([
            changes["new_endpoints"],
            changes["removed_endpoints"],
            changes["modified_endpoints"],
            changes["new_ws_channels"],
            changes["removed_ws_channels"],
            changes["modified_ws_channels"],
            changes["ws_message_format_changes"],
            changes["auth_changes"],
            changes["rate_limit_changes"],
            changes["version_change"]
        ]):
            return None
        
        return changes
    
    def _hash_dict(self, d: dict) -> str:
        """Hash a dictionary for comparison"""
        return hashlib.md5(json.dumps(d, sort_keys=True).encode()).hexdigest()
    
    def _format_changes(self, changes: Dict) -> str:
        """Format changes for display (REST + WebSocket)"""
        parts = []
        
        # REST API changes
        if changes["new_endpoints"]:
            parts.append(f"{len(changes['new_endpoints'])} new REST endpoints")
        
        if changes["removed_endpoints"]:
            parts.append(f"{len(changes['removed_endpoints'])} removed REST endpoints")
        
        if changes["modified_endpoints"]:
            parts.append(f"{len(changes['modified_endpoints'])} modified REST endpoints")
        
        # WebSocket changes
        if changes["new_ws_channels"]:
            parts.append(f"{len(changes['new_ws_channels'])} new WS channels")
        
        if changes["removed_ws_channels"]:
            parts.append(f"{len(changes['removed_ws_channels'])} removed WS channels")
        
        if changes["modified_ws_channels"]:
            parts.append(f"{len(changes['modified_ws_channels'])} modified WS channels")
        
        if changes["ws_message_format_changes"]:
            parts.append(f"{len(changes['ws_message_format_changes'])} WS message format changes")
        
        # Common changes
        if changes["auth_changes"]:
            parts.append("auth changed")
        
        if changes["rate_limit_changes"]:
            parts.append("rate limits changed")
        
        if changes["version_change"]:
            parts.append("version updated")
        
        return ", ".join(parts)
    
    async def _trigger_regeneration(
        self,
        integration_type: str,
        changes: Dict,
        new_spec: dict,
        new_ws_spec: dict,
        new_version: str
    ):
        """Trigger connector code regeneration (REST + WebSocket)"""
        
        reason = f"API updated to v{new_version}: {self._format_changes(changes)}"
        
        print(f"   🤖 Triggering connector regeneration...")
        print(f"      REST changes: {changes.get('new_endpoints', [])} new, {changes.get('modified_endpoints', [])} modified")
        print(f"      WebSocket changes: {changes.get('new_ws_channels', [])} new, {changes.get('modified_ws_channels', [])} modified")
        
        try:
            result = await self.connector_generator.generate_connector(
                integration_type=integration_type,
                reason=reason
            )
            
            print(f"   ✅ Connector regenerated successfully")
            print(f"      Version: {result.get('version')}")
            print(f"      Files: {', '.join(result.get('files_generated', []))}")
            
            # Notify users
            await self._notify_users_of_update(integration_type, changes, new_version)
            
        except Exception as e:
            print(f"   ❌ Regeneration failed: {e}")
    
    async def _notify_users_of_update(
        self,
        integration_type: str,
        changes: Dict,
        new_version: str
    ):
        """Notify users that connector was updated"""
        
        # TODO: Send notifications via Atlas
        print(f"   📧 Notifying users of {integration_type} update to v{new_version}")
        
        # Log to database
        if self.db:
            await self.db.execute("""
                INSERT INTO connector_updates (
                    integration_type,
                    version,
                    changes,
                    timestamp
                ) VALUES ($1, $2, $3, $4)
            """, integration_type, new_version, json.dumps(changes), datetime.utcnow())
    
    async def _get_stored_spec(self, integration_type: str) -> Optional[dict]:
        """Get stored API spec from database"""
        
        if not self.db:
            # Fallback to file storage
            try:
                with open(f"/tmp/api_specs/{integration_type}.json", 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                return None
        
        result = await self.db.fetchone("""
            SELECT spec FROM api_specs
            WHERE integration_type = $1
            ORDER BY created_at DESC
            LIMIT 1
        """, integration_type)
        
        return result["spec"] if result else None
    
    async def _store_spec(
        self,
        integration_type: str,
        spec: dict,
        version: str
    ):
        """Store API spec in database"""
        
        if not self.db:
            # Fallback to file storage
            import os
            os.makedirs("/tmp/api_specs", exist_ok=True)
            with open(f"/tmp/api_specs/{integration_type}.json", 'w') as f:
                json.dump(spec, f, indent=2)
            return
        
        await self.db.execute("""
            INSERT INTO api_specs (
                integration_type,
                version,
                spec,
                created_at
            ) VALUES ($1, $2, $3, $4)
        """, integration_type, version, spec, datetime.utcnow())


# Example usage
if __name__ == "__main__":
    watcher = APIDocsWatcherAgent()
    
    # Start monitoring
    asyncio.run(watcher.watch_all_apis())
