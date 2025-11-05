"""
Agent Discovery System
Dynamically discovers all available agents by scanning the agents directory
"""
import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List
from .base_agent import BaseAgent


def discover_all_agents() -> Dict[str, List[Dict[str, str]]]:
    """
    Dynamically discover all agents by scanning the agents directory.
    Returns a dictionary organized by category with agent metadata.
    """
    agents_dir = Path(__file__).parent
    discovered_agents = {}
    
    # Categories to scan
    categories = [
        'finance', 'communication', 'development', 'documents', 'legal',
        'business', 'health', 'insurance', 'media', 'analytics', 'modern',
        'web', 'web3', 'infrastructure', 'core', 'knowledge'
    ]
    
    # Scan connector subdirectories
    connector_categories = ['brokerages', 'exchanges', 'data_sources', 'market_data']
    
    for category in categories:
        category_path = agents_dir / category
        if not category_path.exists():
            continue
            
        agents_in_category = []
        
        # Scan for agent files
        for agent_file in category_path.glob('*_agent.py'):
            if agent_file.name == 'base_agent.py':
                continue
                
            agent_id = agent_file.stem.replace('_agent', '')
            
            # Try to import and get metadata
            try:
                module_path = f'agents.{category}.{agent_file.stem}'
                module = importlib.import_module(module_path)
                
                # Find the agent class
                agent_class = None
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseAgent) and 
                        obj != BaseAgent):
                        agent_class = obj
                        break
                
                if agent_class:
                    # Instantiate to get metadata
                    instance = agent_class()
                    agents_in_category.append({
                        'id': agent_id,
                        'name': instance.name,
                        'description': instance.description,
                        'category': category.capitalize(),
                        'capabilities': instance.capabilities,
                        'icon': _get_icon_for_agent(agent_id, category)
                    })
            except Exception as e:
                # If import fails, add basic info
                agents_in_category.append({
                    'id': agent_id,
                    'name': agent_id.replace('_', ' ').title() + ' Agent',
                    'description': f'{agent_id.replace("_", " ").title()} agent',
                    'category': category.capitalize(),
                    'capabilities': [],
                    'icon': _get_icon_for_agent(agent_id, category)
                })
        
        if agents_in_category:
            discovered_agents[category] = agents_in_category
    
    # Scan connectors
    connectors_path = agents_dir / 'connectors'
    if connectors_path.exists():
        all_connectors = []
        
        for connector_category in connector_categories:
            connector_cat_path = connectors_path / connector_category
            if not connector_cat_path.exists():
                continue
                
            for agent_file in connector_cat_path.glob('*_agent.py'):
                agent_id = agent_file.stem.replace('_agent', '')
                all_connectors.append({
                    'id': agent_id,
                    'name': agent_id.replace('_', ' ').title().replace('Connector', '') + ' Connector',
                    'description': f'{agent_id.replace("_", " ").title()} connector',
                    'category': 'Connectors',
                    'capabilities': ['API Integration', 'Data Sync'],
                    'icon': 'link-outline'
                })
        
        if all_connectors:
            discovered_agents['connectors'] = all_connectors
    
    return discovered_agents


def _get_icon_for_agent(agent_id: str, category: str) -> str:
    """Get appropriate icon for an agent based on its ID and category"""
    icon_map = {
        # Finance
        'ledger': 'book-outline',
        'tax': 'calculator-outline',
        'invoice': 'receipt-outline',
        'budget': 'wallet-outline',
        'trading': 'trending-up-outline',
        'forex': 'cash-outline',
        'stocks': 'stats-chart-outline',
        'options': 'git-branch-outline',
        'futures': 'flash-outline',
        'arbitrage': 'swap-horizontal-outline',
        'sentiment': 'pulse-outline',
        'backtest': 'time-outline',
        'portfolio': 'pie-chart-outline',
        'strategy': 'trending-up-outline',
        
        # Communication
        'email': 'mail-outline',
        'calendar': 'calendar-outline',
        'slack': 'chatbubbles-outline',
        'teams': 'people-outline',
        'contact': 'person-outline',
        
        # Development
        'code': 'code-slash-outline',
        'github': 'logo-github',
        'devops': 'server-outline',
        'api': 'cloud-outline',
        
        # Documents
        'document': 'document-text-outline',
        'pdf': 'document-outline',
        'ocr': 'scan-outline',
        'notion': 'layers-outline',
        'drive': 'cloud-upload-outline',
        'knowledge': 'library-outline',
        'wiki': 'book-outline',
        'research': 'search-outline',
        'translation': 'language-outline',
        
        # Legal
        'legal': 'hammer-outline',
        'contract': 'document-text-outline',
        'compliance': 'shield-checkmark-outline',
        'ip': 'lock-closed-outline',
        
        # Business
        'grant': 'gift-outline',
        'sales': 'cart-outline',
        'marketing': 'megaphone-outline',
        'hr': 'people-outline',
        'crm': 'people-circle-outline',
        'analytics': 'analytics-outline',
        'business_strategy': 'bulb-outline',
        'operations': 'settings-outline',
        'project': 'folder-outline',
        'travel': 'airplane-outline',
        'charity': 'heart-outline',
        
        # Health
        'health': 'fitness-outline',
        'nutrition': 'nutrition-outline',
        
        # Insurance
        'insurance': 'shield-outline',
        'claims': 'document-text-outline',
        'risk': 'warning-outline',
        
        # Media
        'image': 'image-outline',
        'video': 'videocam-outline',
        'audio': 'musical-notes-outline',
        'content': 'create-outline',
        'vision': 'eye-outline',
        'music': 'musical-note-outline',
        
        # Analytics
        'data': 'bar-chart-outline',
        'metrics': 'speedometer-outline',
        'forecast': 'trending-up-outline',
        'report': 'document-text-outline',
        'ml': 'hardware-chip-outline',
        'text': 'text-outline',
        'schema': 'grid-outline',
        'router': 'git-network-outline',
        'materialize': 'cube-outline',
        
        # Modern
        'slang': 'chatbox-outline',
        'meme': 'happy-outline',
        'social': 'share-social-outline',
        
        # Web
        'web': 'globe-outline',
        'seo': 'search-outline',
        'scraper': 'download-outline',
        'integration': 'link-outline',
        
        # Web3
        'blockchain': 'cube-outline',
        'nft': 'image-outline',
        'defi': 'swap-horizontal-outline',
        'crypto': 'logo-bitcoin',
        'auction': 'hammer-outline',
        
        # Infrastructure
        'connection_monitor': 'pulse-outline',
        'rate_limit_manager': 'speedometer-outline',
        'api_version_monitor': 'code-working-outline',
        'webhook_manager': 'git-network-outline',
    }
    
    # Check for broker/exchange patterns
    if 'broker' in agent_id:
        return 'business-outline'
    if 'exchange' in agent_id:
        return 'logo-bitcoin'
    if 'connector' in agent_id:
        return 'link-outline'
    
    return icon_map.get(agent_id, 'ellipse-outline')


def get_agent_count() -> Dict[str, int]:
    """Get count of agents by category"""
    agents = discover_all_agents()
    return {
        category: len(agent_list)
        for category, agent_list in agents.items()
    }


def get_total_agent_count() -> int:
    """Get total number of agents"""
    agents = discover_all_agents()
    return sum(len(agent_list) for agent_list in agents.values())
