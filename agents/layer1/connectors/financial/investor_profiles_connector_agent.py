"""
Investor Profiles Connector Agent
Connects to investor profile data from AckwardRootsInc
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class InvestorProfilesConnectorAgent(BaseAgent):
    """Connector for investor profile data and analytics"""
    
    def __init__(self):
        super().__init__(
            name="Investor Profiles Connector",
            description="Connects to investor profile data, risk tolerance, investment preferences, and portfolio allocations",
            capabilities=[
                "Investor Profile Retrieval",
                "Risk Tolerance Analysis",
                "Investment Preference Tracking",
                "Portfolio Allocation Data",
                "Investor Segmentation"
            ]
        )
        self.base_url = "http://localhost:8090"  # AckwardRootsInc investor_profiles service
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process investor profile requests"""
        action = data.get('action', 'get_profile')
        investor_id = data.get('investor_id')
        
        if not investor_id:
            return {
                'status': 'error',
                'message': 'investor_id is required'
            }
        
        if action == 'get_profile':
            return self._get_investor_profile(investor_id)
        elif action == 'get_risk_tolerance':
            return self._get_risk_tolerance(investor_id)
        elif action == 'get_preferences':
            return self._get_investment_preferences(investor_id)
        elif action == 'get_allocation':
            return self._get_portfolio_allocation(investor_id)
        else:
            return {
                'status': 'error',
                'message': f'Unknown action: {action}'
            }
    
    def _get_investor_profile(self, investor_id: str) -> Dict[str, Any]:
        """Get complete investor profile"""
        return {
            'status': 'success',
            'investor_id': investor_id,
            'profile': {
                'name': 'Sample Investor',
                'risk_tolerance': 'moderate',
                'investment_horizon': '10-20 years',
                'goals': ['retirement', 'wealth_growth'],
                'constraints': ['esg_focused', 'no_crypto']
            },
            'source': 'investor_profiles_connector'
        }
    
    def _get_risk_tolerance(self, investor_id: str) -> Dict[str, Any]:
        """Get investor risk tolerance"""
        return {
            'status': 'success',
            'investor_id': investor_id,
            'risk_tolerance': {
                'level': 'moderate',
                'score': 6.5,
                'volatility_tolerance': 'medium',
                'loss_tolerance': '15%',
                'time_horizon': 'long_term'
            }
        }
    
    def _get_investment_preferences(self, investor_id: str) -> Dict[str, Any]:
        """Get investment preferences"""
        return {
            'status': 'success',
            'investor_id': investor_id,
            'preferences': {
                'asset_classes': ['stocks', 'bonds', 'real_estate'],
                'sectors': ['technology', 'healthcare', 'renewable_energy'],
                'esg_focus': True,
                'dividend_preference': 'growth',
                'geographic_preference': ['us', 'developed_markets']
            }
        }
    
    def _get_portfolio_allocation(self, investor_id: str) -> Dict[str, Any]:
        """Get recommended portfolio allocation"""
        return {
            'status': 'success',
            'investor_id': investor_id,
            'allocation': {
                'stocks': 0.60,
                'bonds': 0.25,
                'real_estate': 0.10,
                'cash': 0.05
            },
            'rebalance_frequency': 'quarterly'
        }
