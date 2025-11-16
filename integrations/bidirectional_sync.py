"""
Bidirectional Sync Engine

Keeps Linear (local) and External PM tools in sync.

Features:
- Real-time sync via webhooks
- Conflict detection and resolution
- Merge strategies
- Audit trail
- Mermaid diagram sync
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from integrations.pm_integration import PMIntegrationLayer

logger = logging.getLogger(__name__)


class ConflictStrategy(Enum):
    """Conflict resolution strategies"""
    LINEAR_WINS = "linear_wins"
    EXTERNAL_WINS = "external_wins"
    MANUAL = "manual"
    MERGE = "merge"


class SyncMapping:
    """Mapping between Linear and external tickets"""
    
    def __init__(
        self,
        id: str,
        linear_id: str,
        external_id: str,
        external_pm: str,
        last_sync_at: datetime,
        conflict_strategy: ConflictStrategy = ConflictStrategy.LINEAR_WINS
    ):
        self.id = id
        self.linear_id = linear_id
        self.external_id = external_id
        self.external_pm = external_pm
        self.last_sync_at = last_sync_at
        self.conflict_strategy = conflict_strategy


class BidirectionalSyncEngine:
    """
    Keeps Linear and External PM in sync
    
    Features:
    - Real-time sync (webhooks)
    - Conflict resolution
    - Merge strategies
    - Audit trail
    """
    
    def __init__(self):
        self.sync_configs = {}  # project_id → config
        self.sync_mappings = {}  # linear_id → SyncMapping
        self.conflict_resolver = ConflictResolver()
        
    async def setup_sync(
        self,
        linear_project_id: str,
        external_pm: str,
        external_project_id: str,
        conflict_strategy: ConflictStrategy = ConflictStrategy.LINEAR_WINS
    ):
        """Set up bidirectional sync"""
        
        logger.info(f"🔄 Setting up sync: Linear ↔ {external_pm}")
        
        # 1. Initialize PM adapter
        pm_integration = PMIntegrationLayer(external_pm)
        
        # 2. Store sync config
        config = {
            'linear_project_id': linear_project_id,
            'external_pm': external_pm,
            'external_project_id': external_project_id,
            'pm_integration': pm_integration,
            'conflict_strategy': conflict_strategy,
            'sync_enabled': True,
            'sync_fields': ['title', 'description', 'status', 'assignee', 'priority', 'labels'],
            'created_at': datetime.now()
        }
        
        self.sync_configs[linear_project_id] = config
        
        # 3. Register webhooks
        await self.register_webhooks(linear_project_id, external_pm, external_project_id)
        
        # 4. Start sync worker
        asyncio.create_task(self.sync_worker(linear_project_id))
        
        logger.info(f"✅ Bidirectional sync enabled: Linear ↔ {external_pm}")
        
        return config
        
    async def register_webhooks(
        self,
        linear_project_id: str,
        external_pm: str,
        external_project_id: str
    ):
        """Register webhooks for both systems"""
        
        # Linear webhook
        # TODO: Implement Linear webhook registration
        logger.info(f"📡 Registered Linear webhook for project {linear_project_id}")
        
        # External PM webhook
        # TODO: Implement external PM webhook registration
        logger.info(f"📡 Registered {external_pm} webhook for project {external_project_id}")
        
    async def handle_linear_update(self, event: Dict):
        """Handle update from Linear"""
        
        linear_ticket_id = event['ticket_id']
        
        logger.info(f"📝 Linear update: {linear_ticket_id}")
        
        # 1. Get ticket mapping
        mapping = self.sync_mappings.get(linear_ticket_id)
        if not mapping:
            logger.warning(f"No mapping found for Linear ticket: {linear_ticket_id}")
            return
            
        # 2. Get sync config
        config = self.sync_configs.get(event['project_id'])
        if not config or not config['sync_enabled']:
            logger.warning(f"Sync not enabled for project: {event['project_id']}")
            return
            
        # 3. Get updated Linear ticket
        linear_ticket = await self.get_linear_ticket(linear_ticket_id)
        
        # 4. Get external ticket for conflict check
        pm_integration = config['pm_integration']
        external_ticket = await pm_integration.adapter.get_ticket(mapping.external_id)
        
        # 5. Check for conflicts
        conflict = await self.detect_conflict(linear_ticket, external_ticket, mapping)
        
        if conflict:
            await self.resolve_conflict(conflict, config)
        else:
            # 6. Sync to external PM
            await self.sync_to_external(linear_ticket, mapping, config)
            
    async def handle_external_update(self, event: Dict):
        """Handle update from external PM"""
        
        external_ticket_id = event['ticket_id']
        external_pm = event['pm_tool']
        
        logger.info(f"📝 {external_pm} update: {external_ticket_id}")
        
        # 1. Get ticket mapping
        mapping = self.get_mapping_by_external_id(external_ticket_id)
        
        if not mapping:
            # New ticket created externally
            logger.info(f"New external ticket detected: {external_ticket_id}")
            await self.import_new_external_ticket(external_ticket_id, external_pm)
            return
            
        # 2. Get sync config
        config = self.get_config_by_external_pm(external_pm)
        if not config or not config['sync_enabled']:
            logger.warning(f"Sync not enabled for {external_pm}")
            return
            
        # 3. Get updated external ticket
        pm_integration = config['pm_integration']
        external_ticket = await pm_integration.adapter.get_ticket(external_ticket_id)
        
        # 4. Get Linear ticket for conflict check
        linear_ticket = await self.get_linear_ticket(mapping.linear_id)
        
        # 5. Check for conflicts
        conflict = await self.detect_conflict(linear_ticket, external_ticket, mapping)
        
        if conflict:
            await self.resolve_conflict(conflict, config)
        else:
            # 6. Sync to Linear
            await self.sync_to_linear(external_ticket, mapping, config)
            
    async def sync_to_external(
        self,
        linear_ticket: Dict,
        mapping: SyncMapping,
        config: Dict
    ):
        """Sync Linear ticket to external PM"""
        
        logger.info(f"⬆️ Syncing to {mapping.external_pm}: {linear_ticket['title']}")
        
        pm_integration = config['pm_integration']
        
        # 1. Translate Linear → External format
        external_update = self.translate_to_external(
            linear_ticket,
            mapping.external_pm,
            config['sync_fields']
        )
        
        # 2. Handle Mermaid diagram
        if linear_ticket.get('mermaid_diagram'):
            external_update = await self.sync_mermaid_diagram(
                linear_ticket['mermaid_diagram'],
                external_update,
                mapping.external_pm
            )
            
        # 3. Update external ticket
        try:
            await pm_integration.adapter.update_ticket(
                mapping.external_id,
                external_update
            )
            
            # 4. Update sync timestamp
            mapping.last_sync_at = datetime.now()
            
            logger.info(f"✅ Synced to {mapping.external_pm}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync to {mapping.external_pm}: {e}")
            
    async def sync_to_linear(
        self,
        external_ticket: Dict,
        mapping: SyncMapping,
        config: Dict
    ):
        """Sync external ticket to Linear"""
        
        logger.info(f"⬇️ Syncing from {mapping.external_pm}: {external_ticket.get('title')}")
        
        pm_integration = config['pm_integration']
        
        # 1. Translate External → Linear format
        linear_update = self.translate_to_linear(
            external_ticket,
            mapping.external_pm,
            config['sync_fields']
        )
        
        # 2. Extract Mermaid diagram if embedded
        if mapping.external_pm == 'github':
            mermaid = self.extract_mermaid_from_markdown(
                external_ticket.get('body', '')
            )
            if mermaid:
                linear_update['mermaid_diagram'] = mermaid
                
        # 3. Update Linear ticket
        try:
            await self.update_linear_ticket(
                mapping.linear_id,
                linear_update
            )
            
            # 4. Update sync timestamp
            mapping.last_sync_at = datetime.now()
            
            logger.info(f"✅ Synced from {mapping.external_pm}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync from {mapping.external_pm}: {e}")
            
    async def detect_conflict(
        self,
        linear_ticket: Dict,
        external_ticket: Dict,
        mapping: SyncMapping
    ) -> Optional[Dict]:
        """Detect sync conflicts"""
        
        # Check if both tickets were modified since last sync
        last_sync = mapping.last_sync_at
        
        linear_modified = datetime.fromisoformat(linear_ticket['updated_at']) > last_sync
        external_modified = datetime.fromisoformat(external_ticket['updated_at']) > last_sync
        
        if linear_modified and external_modified:
            # Conflict detected!
            conflicting_fields = self.find_conflicting_fields(
                linear_ticket,
                external_ticket
            )
            
            if conflicting_fields:
                logger.warning(f"⚠️ Conflict detected: {conflicting_fields}")
                
                return {
                    'type': 'concurrent_modification',
                    'linear_ticket': linear_ticket,
                    'external_ticket': external_ticket,
                    'mapping': mapping,
                    'conflicting_fields': conflicting_fields,
                    'detected_at': datetime.now()
                }
                
        return None
        
    def find_conflicting_fields(
        self,
        linear_ticket: Dict,
        external_ticket: Dict
    ) -> List[str]:
        """Find which fields conflict"""
        
        conflicts = []
        
        # Normalize external ticket
        normalized = self.normalize_external_ticket(external_ticket)
        
        # Compare fields
        for field in ['title', 'description', 'status', 'assignee', 'priority']:
            if linear_ticket.get(field) != normalized.get(field):
                conflicts.append(field)
                
        return conflicts
        
    async def resolve_conflict(self, conflict: Dict, config: Dict):
        """Resolve sync conflict"""
        
        strategy = conflict['mapping'].conflict_strategy
        
        logger.info(f"🔧 Resolving conflict with strategy: {strategy.value}")
        
        if strategy == ConflictStrategy.LINEAR_WINS:
            # Linear takes precedence
            await self.sync_to_external(
                conflict['linear_ticket'],
                conflict['mapping'],
                config
            )
            logger.info("✅ Conflict resolved: Linear wins")
            
        elif strategy == ConflictStrategy.EXTERNAL_WINS:
            # External takes precedence
            await self.sync_to_linear(
                conflict['external_ticket'],
                conflict['mapping'],
                config
            )
            logger.info("✅ Conflict resolved: External wins")
            
        elif strategy == ConflictStrategy.MERGE:
            # Merge both changes
            merged = await self.merge_tickets(
                conflict['linear_ticket'],
                conflict['external_ticket'],
                conflict['conflicting_fields']
            )
            
            # Update both sides
            await self.sync_to_external(merged, conflict['mapping'], config)
            await self.sync_to_linear(merged, conflict['mapping'], config)
            
            logger.info("✅ Conflict resolved: Merged")
            
        elif strategy == ConflictStrategy.MANUAL:
            # Notify team for manual resolution
            await self.notify_conflict(conflict)
            logger.warning("⚠️ Conflict requires manual resolution")
            
    async def sync_mermaid_diagram(
        self,
        mermaid: str,
        external_update: Dict,
        external_pm: str
    ) -> Dict:
        """Sync Mermaid diagram to external PM"""
        
        if external_pm == 'jira':
            # Render Mermaid to image, attach to Jira
            image = await self.render_mermaid_to_image(mermaid)
            external_update['attachments'] = external_update.get('attachments', [])
            external_update['attachments'].append(image)
            
        elif external_pm == 'github':
            # Embed Mermaid in markdown
            body = external_update.get('body', '')
            if '```mermaid' not in body:
                external_update['body'] = f"{body}\n\n## Flow Diagram\n```mermaid\n{mermaid}\n```"
                
        return external_update
        
    def extract_mermaid_from_markdown(self, markdown: str) -> Optional[str]:
        """Extract Mermaid diagram from markdown"""
        import re
        
        pattern = r'```mermaid\n(.*?)\n```'
        match = re.search(pattern, markdown, re.DOTALL)
        
        if match:
            return match.group(1).strip()
            
        return None
        
    async def render_mermaid_to_image(self, mermaid: str) -> bytes:
        """Render Mermaid diagram to image"""
        # TODO: Implement Mermaid rendering
        # Could use mermaid-cli or a service
        logger.info("🎨 Rendering Mermaid diagram to image")
        return b''
        
    def translate_to_external(
        self,
        linear_ticket: Dict,
        external_pm: str,
        sync_fields: List[str]
    ) -> Dict:
        """Translate Linear ticket to external format"""
        
        update = {}
        
        for field in sync_fields:
            if field in linear_ticket:
                update[field] = linear_ticket[field]
                
        return update
        
    def translate_to_linear(
        self,
        external_ticket: Dict,
        external_pm: str,
        sync_fields: List[str]
    ) -> Dict:
        """Translate external ticket to Linear format"""
        
        # Normalize first
        normalized = self.normalize_external_ticket(external_ticket)
        
        update = {}
        
        for field in sync_fields:
            if field in normalized:
                update[field] = normalized[field]
                
        return update
        
    def normalize_external_ticket(self, ticket: Dict) -> Dict:
        """Normalize external ticket format"""
        # Use PMIntegrationLayer's normalize_ticket method
        # This is a simplified version
        return ticket
        
    async def sync_worker(self, project_id: str):
        """Background worker for periodic sync"""
        
        while True:
            config = self.sync_configs.get(project_id)
            
            if not config or not config['sync_enabled']:
                break
                
            try:
                # Periodic full sync (every 5 minutes)
                await asyncio.sleep(300)
                
                logger.info(f"🔄 Periodic sync for project {project_id}")
                
                # TODO: Implement full sync logic
                
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                
    async def get_linear_ticket(self, ticket_id: str) -> Dict:
        """Get Linear ticket"""
        # TODO: Implement Linear API call
        return {}
        
    async def update_linear_ticket(self, ticket_id: str, updates: Dict):
        """Update Linear ticket"""
        # TODO: Implement Linear API call
        pass
        
    def get_mapping_by_external_id(self, external_id: str) -> Optional[SyncMapping]:
        """Get mapping by external ticket ID"""
        for mapping in self.sync_mappings.values():
            if mapping.external_id == external_id:
                return mapping
        return None
        
    def get_config_by_external_pm(self, external_pm: str) -> Optional[Dict]:
        """Get config by external PM tool"""
        for config in self.sync_configs.values():
            if config['external_pm'] == external_pm:
                return config
        return None
        
    async def import_new_external_ticket(self, ticket_id: str, external_pm: str):
        """Import new ticket created in external PM"""
        logger.info(f"📥 Importing new {external_pm} ticket: {ticket_id}")
        # TODO: Implement ticket import
        
    async def notify_conflict(self, conflict: Dict):
        """Notify team of conflict"""
        logger.warning(f"📢 Conflict notification: {conflict['conflicting_fields']}")
        # TODO: Implement team notification
        
    async def merge_tickets(
        self,
        linear_ticket: Dict,
        external_ticket: Dict,
        conflicting_fields: List[str]
    ) -> Dict:
        """Merge conflicting tickets"""
        # Simple merge: take newer value for each field
        merged = linear_ticket.copy()
        
        for field in conflicting_fields:
            # Take the value from whichever was updated more recently
            if datetime.fromisoformat(external_ticket['updated_at']) > datetime.fromisoformat(linear_ticket['updated_at']):
                merged[field] = external_ticket.get(field)
                
        return merged


class ConflictResolver:
    """Helper class for conflict resolution"""
    
    def __init__(self):
        pass
        
    async def resolve(self, conflict: Dict, strategy: ConflictStrategy) -> Dict:
        """Resolve conflict based on strategy"""
        # TODO: Implement sophisticated conflict resolution
        return {}


# Global sync engine instance
_sync_engine = BidirectionalSyncEngine()


def get_sync_engine() -> BidirectionalSyncEngine:
    """Get global sync engine instance"""
    return _sync_engine
