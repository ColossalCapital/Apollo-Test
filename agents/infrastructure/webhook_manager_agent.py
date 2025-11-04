"""
Webhook Manager Agent - Manages webhooks from all data sources
"""

from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent


class WebhookManagerAgent(BaseAgent):
    """
    Manages webhooks from all data sources.
    
    Capabilities:
    - Webhook registration
    - Event processing
    - Retry logic
    - Signature verification
    - Event routing
    """
    
    def __init__(self):
        super().__init__(
            name="Webhook Manager",
            description="Manages webhooks from all data sources",
            capabilities=[
                "Webhook Registration",
                "Event Processing",
                "Retry Logic",
                "Signature Verification",
                "Event Routing"
            ]
        )
        
        # Webhook tracking
        self.webhooks: Dict[str, Dict[str, Any]] = {}
        self.event_queue: List[Dict[str, Any]] = []
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook management requests.
        
        Supported actions:
        - register: Register a new webhook
        - process_event: Process incoming webhook event
        - verify_signature: Verify webhook signature
        - get_webhooks: Get all registered webhooks
        - retry_failed: Retry failed webhook deliveries
        """
        action = data.get('action', 'process_event')
        
        if action == 'register':
            return self._register_webhook(data)
        elif action == 'process_event':
            return self._process_event(data)
        elif action == 'verify_signature':
            return self._verify_signature(data)
        elif action == 'get_webhooks':
            return self._get_webhooks(data)
        elif action == 'retry_failed':
            return self._retry_failed(data)
        else:
            return {
                'status': 'error',
                'message': f'Unknown action: {action}'
            }
    
    def _register_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new webhook"""
        platform = data.get('platform')
        url = data.get('url')
        events = data.get('events', [])
        
        if not all([platform, url]):
            return {
                'status': 'error',
                'message': 'platform and url required'
            }
        
        webhook_id = f"wh_{platform.lower()}_{datetime.now().timestamp()}"
        
        webhook_info = {
            'id': webhook_id,
            'platform': platform,
            'url': url,
            'events': events,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_delivery': None,
            'delivery_count': 0,
            'failure_count': 0
        }
        
        return {
            'status': 'success',
            'message': 'Webhook registered successfully',
            'webhook': webhook_info,
            'secret': 'whsec_' + 'x' * 32  # Simulated webhook secret
        }
    
    def _process_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook event"""
        platform = data.get('platform')
        event_type = data.get('event_type')
        payload = data.get('payload', {})
        signature = data.get('signature')
        
        if not all([platform, event_type]):
            return {
                'status': 'error',
                'message': 'platform and event_type required'
            }
        
        # Verify signature
        signature_valid = self._verify_webhook_signature(platform, payload, signature)
        
        if not signature_valid:
            return {
                'status': 'error',
                'message': 'Invalid webhook signature',
                'code': 'INVALID_SIGNATURE'
            }
        
        # Process event based on type
        processing_result = self._route_event(platform, event_type, payload)
        
        return {
            'status': 'success',
            'message': 'Event processed successfully',
            'event_id': f"evt_{datetime.now().timestamp()}",
            'platform': platform,
            'event_type': event_type,
            'processing_result': processing_result
        }
    
    def _verify_signature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify webhook signature"""
        platform = data.get('platform')
        payload = data.get('payload')
        signature = data.get('signature')
        
        if not all([platform, payload, signature]):
            return {
                'status': 'error',
                'message': 'platform, payload, and signature required'
            }
        
        is_valid = self._verify_webhook_signature(platform, payload, signature)
        
        return {
            'status': 'success',
            'valid': is_valid,
            'platform': platform
        }
    
    def _get_webhooks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get all registered webhooks"""
        user_id = data.get('user_id')
        platform = data.get('platform')  # Optional filter
        
        # Simulate webhook list
        webhooks = [
            {
                'id': 'wh_stripe_001',
                'platform': 'Stripe',
                'events': ['payment.succeeded', 'payment.failed'],
                'status': 'active',
                'delivery_count': 1234,
                'failure_count': 5,
                'success_rate': 99.6
            },
            {
                'id': 'wh_quickbooks_001',
                'platform': 'QuickBooks',
                'events': ['invoice.created', 'payment.received'],
                'status': 'active',
                'delivery_count': 567,
                'failure_count': 2,
                'success_rate': 99.6
            },
            {
                'id': 'wh_github_001',
                'platform': 'GitHub',
                'events': ['push', 'pull_request'],
                'status': 'active',
                'delivery_count': 890,
                'failure_count': 12,
                'success_rate': 98.7
            }
        ]
        
        if platform:
            webhooks = [w for w in webhooks if w['platform'].lower() == platform.lower()]
        
        return {
            'status': 'success',
            'webhooks': webhooks,
            'total': len(webhooks)
        }
    
    def _retry_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Retry failed webhook deliveries"""
        webhook_id = data.get('webhook_id')
        event_id = data.get('event_id')
        
        if not webhook_id:
            return {
                'status': 'error',
                'message': 'webhook_id required'
            }
        
        # Simulate retry
        retry_result = {
            'webhook_id': webhook_id,
            'event_id': event_id,
            'retry_attempt': 2,
            'status': 'success',
            'delivered_at': datetime.now().isoformat()
        }
        
        return {
            'status': 'success',
            'message': 'Webhook delivery retried successfully',
            'result': retry_result
        }
    
    def _verify_webhook_signature(self, platform: str, payload: Any, signature: str) -> bool:
        """Verify webhook signature (platform-specific)"""
        # In real implementation, this would verify using platform-specific methods
        # For now, simulate verification
        return signature is not None and len(signature) > 0
    
    def _route_event(self, platform: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route webhook event to appropriate handler"""
        # Route to different agents based on event type
        routing = {
            'payment': 'ledger_agent',
            'invoice': 'invoice_agent',
            'transaction': 'ledger_agent',
            'email': 'email_agent',
            'calendar': 'calendar_agent',
            'commit': 'github_agent',
            'pull_request': 'github_agent'
        }
        
        # Determine target agent
        target_agent = 'default_agent'
        for key, agent in routing.items():
            if key in event_type.lower():
                target_agent = agent
                break
        
        return {
            'routed_to': target_agent,
            'event_type': event_type,
            'processed_at': datetime.now().isoformat()
        }
