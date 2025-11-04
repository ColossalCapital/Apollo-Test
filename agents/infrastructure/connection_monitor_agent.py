"""
Connection Monitor Agent - Monitors WebSocket connections, API health, and auto-reconnection
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class ConnectionMonitorAgent(BaseAgent):
    """
    Monitors WebSocket connections, API health, and keeps integrations up-to-date.
    
    Capabilities:
    - WebSocket health monitoring
    - API connection status tracking
    - Auto-reconnection logic
    - Rate limit tracking per platform
    - API version update detection
    - Connection diagnostics and troubleshooting
    """
    
    def __init__(self):
        super().__init__(
            name="Connection Monitor",
            description="Monitors WebSocket connections, API health, and keeps integrations up-to-date",
            capabilities=[
                "WebSocket Health Monitoring",
                "API Connection Status",
                "Auto-Reconnection",
                "Rate Limit Tracking",
                "API Version Updates",
                "Connection Diagnostics"
            ]
        )
        
        # Connection state tracking
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.reconnect_attempts: Dict[str, int] = {}
        self.max_reconnect_attempts = 5
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process connection monitoring requests.
        
        Supported actions:
        - check_health: Check health of a specific connection
        - check_all: Check all connections
        - reconnect: Attempt to reconnect a dropped connection
        - get_diagnostics: Get detailed diagnostics for a connection
        """
        action = data.get('action', 'check_health')
        
        if action == 'check_health':
            return self._check_connection_health(data)
        elif action == 'check_all':
            return self._check_all_connections(data)
        elif action == 'reconnect':
            return self._reconnect(data)
        elif action == 'get_diagnostics':
            return self._get_diagnostics(data)
        else:
            return {
                'status': 'error',
                'message': f'Unknown action: {action}'
            }
    
    def _check_connection_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a specific connection"""
        connection_id = data.get('connection_id')
        platform = data.get('platform')
        
        if not connection_id:
            return {
                'status': 'error',
                'message': 'connection_id required'
            }
        
        # Simulate health check
        health_status = {
            'connection_id': connection_id,
            'platform': platform,
            'status': 'healthy',
            'last_ping': 'just now',
            'latency_ms': 45,
            'uptime_hours': 24.5,
            'reconnect_count': self.reconnect_attempts.get(connection_id, 0),
            'issues': []
        }
        
        return {
            'status': 'success',
            'health': health_status,
            'recommendations': self._generate_recommendations(health_status)
        }
    
    def _check_all_connections(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of all connections"""
        user_id = data.get('user_id')
        
        # Simulate checking multiple connections
        connections = [
            {
                'connection_id': 'ib_ws_001',
                'platform': 'Interactive Brokers',
                'type': 'WebSocket',
                'status': 'healthy',
                'latency_ms': 42
            },
            {
                'connection_id': 'binance_ws_001',
                'platform': 'Binance',
                'type': 'WebSocket',
                'status': 'healthy',
                'latency_ms': 38
            },
            {
                'connection_id': 'gmail_api_001',
                'platform': 'Gmail',
                'type': 'REST API',
                'status': 'healthy',
                'rate_limit_used': '45/100'
            }
        ]
        
        healthy_count = sum(1 for c in connections if c['status'] == 'healthy')
        
        return {
            'status': 'success',
            'summary': {
                'total_connections': len(connections),
                'healthy': healthy_count,
                'degraded': 0,
                'down': 0
            },
            'connections': connections
        }
    
    def _reconnect(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to reconnect a dropped connection"""
        connection_id = data.get('connection_id')
        platform = data.get('platform')
        
        if not connection_id:
            return {
                'status': 'error',
                'message': 'connection_id required'
            }
        
        # Track reconnection attempts
        attempts = self.reconnect_attempts.get(connection_id, 0) + 1
        self.reconnect_attempts[connection_id] = attempts
        
        if attempts > self.max_reconnect_attempts:
            return {
                'status': 'error',
                'message': f'Max reconnection attempts ({self.max_reconnect_attempts}) exceeded',
                'recommendation': 'Check API credentials and platform status'
            }
        
        # Simulate reconnection
        return {
            'status': 'success',
            'message': f'Successfully reconnected to {platform}',
            'connection_id': connection_id,
            'attempt_number': attempts,
            'connection_quality': 'good'
        }
    
    def _get_diagnostics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed diagnostics for a connection"""
        connection_id = data.get('connection_id')
        platform = data.get('platform')
        
        diagnostics = {
            'connection_id': connection_id,
            'platform': platform,
            'checks': {
                'api_key_valid': True,
                'network_reachable': True,
                'rate_limits_ok': True,
                'platform_status': 'operational',
                'ssl_certificate': 'valid',
                'dns_resolution': 'ok'
            },
            'performance': {
                'avg_latency_ms': 45,
                'packet_loss': '0%',
                'jitter_ms': 2,
                'bandwidth_mbps': 100
            },
            'recent_errors': [],
            'maintenance_windows': []
        }
        
        return {
            'status': 'success',
            'diagnostics': diagnostics,
            'overall_health': 'excellent'
        }
    
    def _generate_recommendations(self, health_status: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on health status"""
        recommendations = []
        
        if health_status.get('latency_ms', 0) > 100:
            recommendations.append('High latency detected. Consider checking network connection.')
        
        if health_status.get('reconnect_count', 0) > 3:
            recommendations.append('Frequent reconnections detected. Check API credentials.')
        
        if not recommendations:
            recommendations.append('Connection is healthy. No action needed.')
        
        return recommendations
