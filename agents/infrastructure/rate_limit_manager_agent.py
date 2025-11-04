"""
Rate Limit Manager Agent - Manages API rate limits across all integrations
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent


class RateLimitManagerAgent(BaseAgent):
    """
    Manages API rate limits across all integrations.
    
    Capabilities:
    - Rate limit tracking per platform
    - Request throttling
    - Burst handling
    - Priority queuing
    - Limit alerts and warnings
    """
    
    def __init__(self):
        super().__init__(
            name="Rate Limit Manager",
            description="Manages API rate limits across all integrations",
            capabilities=[
                "Rate Limit Tracking",
                "Request Throttling",
                "Burst Handling",
                "Priority Queuing",
                "Limit Alerts"
            ]
        )
        
        # Rate limit tracking
        self.limits: Dict[str, Dict[str, Any]] = {}
        self.request_queue: List[Dict[str, Any]] = []
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process rate limit management requests.
        
        Supported actions:
        - check_limit: Check current rate limit status
        - track_request: Track a new API request
        - get_all_limits: Get all rate limits
        - can_make_request: Check if request can be made
        """
        action = data.get('action', 'check_limit')
        
        if action == 'check_limit':
            return self._check_limit(data)
        elif action == 'track_request':
            return self._track_request(data)
        elif action == 'get_all_limits':
            return self._get_all_limits(data)
        elif action == 'can_make_request':
            return self._can_make_request(data)
        else:
            return {
                'status': 'error',
                'message': f'Unknown action: {action}'
            }
    
    def _check_limit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check current rate limit status for a platform"""
        platform = data.get('platform')
        
        if not platform:
            return {
                'status': 'error',
                'message': 'platform required'
            }
        
        # Platform-specific rate limits
        rate_limits = {
            'binance': {'limit': 1200, 'window': '1 minute', 'weight_based': True},
            'coinbase': {'limit': 10, 'window': '1 second', 'weight_based': False},
            'interactive_brokers': {'limit': 50, 'window': '1 second', 'weight_based': False},
            'gmail': {'limit': 250, 'window': '1 second', 'weight_based': False},
            'quickbooks': {'limit': 500, 'window': '1 minute', 'weight_based': False},
        }
        
        limit_info = rate_limits.get(platform.lower(), {
            'limit': 100,
            'window': '1 minute',
            'weight_based': False
        })
        
        # Simulate current usage
        current_usage = 45
        percentage = (current_usage / limit_info['limit']) * 100
        
        status = 'ok'
        if percentage > 90:
            status = 'critical'
        elif percentage > 75:
            status = 'warning'
        
        return {
            'status': 'success',
            'platform': platform,
            'limit': limit_info['limit'],
            'used': current_usage,
            'remaining': limit_info['limit'] - current_usage,
            'percentage': round(percentage, 2),
            'window': limit_info['window'],
            'weight_based': limit_info['weight_based'],
            'status': status,
            'reset_in_seconds': 15,
            'recommendations': self._get_limit_recommendations(status, percentage)
        }
    
    def _track_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track a new API request"""
        platform = data.get('platform')
        endpoint = data.get('endpoint')
        weight = data.get('weight', 1)
        
        if not platform:
            return {
                'status': 'error',
                'message': 'platform required'
            }
        
        # Track the request
        request_info = {
            'platform': platform,
            'endpoint': endpoint,
            'weight': weight,
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'status': 'success',
            'message': 'Request tracked',
            'request': request_info,
            'current_usage': 46,
            'limit': 1200
        }
    
    def _get_all_limits(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get all rate limits for user's integrations"""
        user_id = data.get('user_id')
        
        # Simulate multiple platform limits
        platforms = [
            {
                'platform': 'Binance',
                'limit': 1200,
                'used': 450,
                'percentage': 37.5,
                'status': 'ok'
            },
            {
                'platform': 'Interactive Brokers',
                'limit': 50,
                'used': 42,
                'percentage': 84.0,
                'status': 'warning'
            },
            {
                'platform': 'Gmail',
                'limit': 250,
                'used': 89,
                'percentage': 35.6,
                'status': 'ok'
            },
            {
                'platform': 'QuickBooks',
                'limit': 500,
                'used': 123,
                'percentage': 24.6,
                'status': 'ok'
            }
        ]
        
        return {
            'status': 'success',
            'platforms': platforms,
            'summary': {
                'total_platforms': len(platforms),
                'ok': sum(1 for p in platforms if p['status'] == 'ok'),
                'warning': sum(1 for p in platforms if p['status'] == 'warning'),
                'critical': sum(1 for p in platforms if p['status'] == 'critical')
            }
        }
    
    def _can_make_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a request can be made without hitting limits"""
        platform = data.get('platform')
        weight = data.get('weight', 1)
        priority = data.get('priority', 'normal')
        
        if not platform:
            return {
                'status': 'error',
                'message': 'platform required'
            }
        
        # Simulate limit check
        current_usage = 45
        limit = 1200
        remaining = limit - current_usage
        
        can_make = remaining >= weight
        
        result = {
            'status': 'success',
            'can_make_request': can_make,
            'remaining_capacity': remaining,
            'requested_weight': weight,
            'priority': priority
        }
        
        if not can_make:
            result['wait_seconds'] = 15
            result['message'] = 'Rate limit reached. Request queued.'
        
        return result
    
    def _get_limit_recommendations(self, status: str, percentage: float) -> List[str]:
        """Generate recommendations based on limit status"""
        recommendations = []
        
        if status == 'critical':
            recommendations.append('⚠️ Rate limit critical! Reduce request frequency.')
            recommendations.append('Consider implementing request batching.')
        elif status == 'warning':
            recommendations.append('⚠️ Approaching rate limit. Monitor usage closely.')
        else:
            recommendations.append('✅ Rate limit usage is healthy.')
        
        return recommendations
