"""
Universal Vault Agent

Manages cross-service connections and automations.
Enables Apollo agents to work across Atlas, Delt, and Akashic.
"""

from typing import Dict, Any, List, Optional
import aiohttp
import json
from .base_agent import BaseAgent


class UniversalVaultAgent(BaseAgent):
    """
    Universal Vault Agent
    
    Coordinates cross-service actions and manages credentials
    """
    
    def __init__(self):
        super().__init__(
            name="UniversalVaultAgent",
            description="Manage connections and automations across all services",
            category="platform"
        )
        self.vault_api = "http://localhost:8090"
    
    async def execute_cross_service_action(
        self,
        user_id: str,
        source_service: str,
        target_service: str,
        agent_name: str,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute action in target service using stored credentials
        
        Example:
            # From Delt, send email via Atlas
            result = await vault_agent.execute_cross_service_action(
                user_id="user123",
                source_service="delt",
                target_service="atlas",
                agent_name="EmailAgent",
                method="send_email",
                params={
                    "to": "user@example.com",
                    "subject": "Trade Alert",
                    "body": "BTC dropped below $60k"
                }
            )
        """
        # 1. Check permissions
        has_permission = await self.check_permission(
            user_id, source_service, target_service
        )
        
        if not has_permission:
            return {
                "success": False,
                "error": "Permission denied"
            }
        
        # 2. Get credentials from vault
        credentials = await self.get_credentials(
            user_id, target_service
        )
        
        # 3. Get target agent
        from . import get_agent
        target_agent = get_agent(agent_name)
        
        if not target_agent:
            return {
                "success": False,
                "error": f"Agent {agent_name} not found"
            }
        
        # 4. Execute action with credentials
        try:
            result = await target_agent.execute(
                method=method,
                params=params,
                credentials=credentials,
                context={
                    "user_id": user_id,
                    "source_service": source_service,
                    "app_context": target_service
                }
            )
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_permission(
        self,
        user_id: str,
        source_service: str,
        target_service: str
    ) -> bool:
        """Check if source service has permission to access target"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.vault_api}/vault/{user_id}/permissions"
            ) as response:
                if response.status == 200:
                    permissions = await response.json()
                    service_perms = permissions.get(source_service, [])
                    return target_service in service_perms or "*" in service_perms
                return False
    
    async def get_credentials(
        self,
        user_id: str,
        service: str
    ) -> Dict[str, Any]:
        """Get credentials for service from vault"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.vault_api}/vault/{user_id}"
            ) as response:
                if response.status == 200:
                    vault = await response.json()
                    # Extract relevant credentials
                    return self._extract_credentials(vault, service)
                return {}
    
    def _extract_credentials(
        self,
        vault: Dict[str, Any],
        service: str
    ) -> Dict[str, Any]:
        """Extract credentials for specific service"""
        connections = vault.get("connections", {})
        
        # Map service to connection type
        service_map = {
            "email": connections.get("productivity", {}).get("email", []),
            "calendar": connections.get("productivity", {}).get("calendar", []),
            "slack": connections.get("communication", {}).get("slack", []),
            "github": connections.get("development", {}).get("github", []),
            "broker": connections.get("financial", {}).get("brokers", []),
            "exchange": connections.get("financial", {}).get("exchanges", []),
        }
        
        return service_map.get(service, [])
    
    async def sync_connection_to_all_services(
        self,
        user_id: str,
        connection: Dict[str, Any]
    ):
        """
        When a connection is added in one service,
        sync it to all other services
        """
        services = [
            ("atlas", "http://localhost:8001/api/vault-event"),
            ("delt", "http://localhost:8080/api/vault-event"),
            ("akashic", "http://localhost:3000/api/vault-event"),
        ]
        
        async with aiohttp.ClientSession() as session:
            for service_name, service_url in services:
                try:
                    await session.post(
                        service_url,
                        json={
                            "user_id": user_id,
                            "event_type": "connection_added",
                            "connection": connection
                        }
                    )
                except Exception as e:
                    print(f"Failed to notify {service_name}: {e}")
    
    async def create_automation(
        self,
        user_id: str,
        automation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create cross-service automation
        
        Example:
            automation = {
                "name": "BTC Alert Email",
                "trigger": {
                    "type": "market_signal",
                    "source_service": "delt",
                    "condition": {"symbol": "BTC", "price": "<60000"}
                },
                "action": {
                    "target_service": "atlas",
                    "agent_name": "EmailAgent",
                    "method": "send_email",
                    "params": {
                        "to": "user@example.com",
                        "subject": "BTC Alert",
                        "body": "BTC dropped below $60k"
                    }
                }
            }
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.vault_api}/vault/{user_id}/automation",
                json=automation
            ) as response:
                return await response.json()
    
    async def get_available_agents(
        self,
        service: str
    ) -> List[Dict[str, Any]]:
        """Get list of available agents for a service"""
        from . import get_all_agents
        
        all_agents = get_all_agents()
        
        # Filter agents by service context
        service_agents = []
        for agent in all_agents:
            if self._agent_supports_service(agent, service):
                service_agents.append({
                    "name": agent.name,
                    "description": agent.description,
                    "category": agent.category,
                    "methods": agent.get_available_methods()
                })
        
        return service_agents
    
    def _agent_supports_service(
        self,
        agent: BaseAgent,
        service: str
    ) -> bool:
        """Check if agent supports service"""
        # Map services to agent categories
        service_categories = {
            "atlas": ["communication", "documents", "business", "analytics"],
            "delt": ["finance", "trading", "analytics"],
            "akashic": ["development", "analytics"],
        }
        
        return agent.category in service_categories.get(service, [])


# Example usage functions for common cross-service actions

async def send_email_from_delt(
    user_id: str,
    to: str,
    subject: str,
    body: str
) -> Dict[str, Any]:
    """Helper: Send email from Delt using Atlas EmailAgent"""
    vault_agent = UniversalVaultAgent()
    
    return await vault_agent.execute_cross_service_action(
        user_id=user_id,
        source_service="delt",
        target_service="atlas",
        agent_name="EmailAgent",
        method="send_email",
        params={
            "to": to,
            "subject": subject,
            "body": body
        }
    )


async def create_calendar_event_from_delt(
    user_id: str,
    title: str,
    date: str,
    reminder: str = "1 hour"
) -> Dict[str, Any]:
    """Helper: Create calendar event from Delt using Atlas CalendarAgent"""
    vault_agent = UniversalVaultAgent()
    
    return await vault_agent.execute_cross_service_action(
        user_id=user_id,
        source_service="delt",
        target_service="atlas",
        agent_name="CalendarAgent",
        method="create_event",
        params={
            "title": title,
            "date": date,
            "reminder": reminder
        }
    )


async def send_slack_message_from_delt(
    user_id: str,
    channel: str,
    message: str
) -> Dict[str, Any]:
    """Helper: Send Slack message from Delt using Atlas SlackAgent"""
    vault_agent = UniversalVaultAgent()
    
    return await vault_agent.execute_cross_service_action(
        user_id=user_id,
        source_service="delt",
        target_service="atlas",
        agent_name="SlackAgent",
        method="send_message",
        params={
            "channel": channel,
            "message": message
        }
    )


async def commit_to_github_from_akashic(
    user_id: str,
    repo: str,
    branch: str,
    message: str,
    files: List[str]
) -> Dict[str, Any]:
    """Helper: Commit to GitHub from Akashic using Atlas GitHubAgent"""
    vault_agent = UniversalVaultAgent()
    
    return await vault_agent.execute_cross_service_action(
        user_id=user_id,
        source_service="akashic",
        target_service="atlas",
        agent_name="GitHubAgent",
        method="commit",
        params={
            "repo": repo,
            "branch": branch,
            "message": message,
            "files": files
        }
    )
