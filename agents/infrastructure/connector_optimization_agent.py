"""
ConnectorOptimizationAgent

Calculates optimal strategies for connectors:
- Number of WebSocket connections needed
- Symbol distribution across connections
- IP pool requirements
- Regional routing strategy

Pure logic agent - no external dependencies.
"""

from typing import Dict, List, Set
import math

class ConnectorOptimizationAgent:
    def __init__(self):
        self.strategies = {}
    
    def calculate_websocket_strategy(
        self,
        connector_name: str,
        total_symbols: int,
        ws_limit: int,
    ) -> Dict:
        """
        Calculate optimal WebSocket connection strategy
        
        Args:
            connector_name: Name of connector (e.g., 'binance')
            total_symbols: Total number of symbols to subscribe to
            ws_limit: Maximum symbols per WebSocket connection
        
        Returns:
            Strategy dict with connection details
        """
        # Calculate number of connections needed
        num_connections = math.ceil(total_symbols / ws_limit)
        
        # Distribute symbols evenly across connections
        symbols_per_connection = []
        remaining = total_symbols
        
        for i in range(num_connections):
            if i == num_connections - 1:
                # Last connection gets remaining symbols
                symbols_per_connection.append(remaining)
            else:
                symbols_per_connection.append(ws_limit)
                remaining -= ws_limit
        
        strategy = {
            'connector': connector_name,
            'total_symbols': total_symbols,
            'ws_limit': ws_limit,
            'num_connections': num_connections,
            'symbols_per_connection': symbols_per_connection,
            'strategy_type': 'even_distribution',
            'efficiency': (total_symbols / (num_connections * ws_limit)) * 100,  # % utilization
        }
        
        # Store strategy
        self.strategies[connector_name] = strategy
        
        return strategy
    
    def calculate_ip_pool_requirements(
        self,
        connector_name: str,
        num_connections: int,
        max_connections_per_ip: int = 100,
    ) -> Dict:
        """
        Calculate IP pool requirements
        
        Args:
            connector_name: Name of connector
            num_connections: Number of WebSocket connections
            max_connections_per_ip: Maximum connections per IP (default: 100)
        
        Returns:
            IP pool strategy
        """
        # Calculate number of IPs needed
        num_ips = math.ceil(num_connections / max_connections_per_ip)
        
        # Distribute connections across IPs
        connections_per_ip = []
        remaining = num_connections
        
        for i in range(num_ips):
            if i == num_ips - 1:
                connections_per_ip.append(remaining)
            else:
                connections_per_ip.append(max_connections_per_ip)
                remaining -= max_connections_per_ip
        
        return {
            'connector': connector_name,
            'num_connections': num_connections,
            'max_connections_per_ip': max_connections_per_ip,
            'num_ips_needed': num_ips,
            'connections_per_ip': connections_per_ip,
            'utilization': (num_connections / (num_ips * max_connections_per_ip)) * 100,
        }
    
    def calculate_regional_strategy(
        self,
        connector_name: str,
        regions: List[str],
        symbols_per_region: Dict[str, int] = None,
    ) -> Dict:
        """
        Calculate regional routing strategy
        
        Args:
            connector_name: Name of connector
            regions: List of regions (e.g., ['US', 'EU', 'ASIA'])
            symbols_per_region: Optional dict of symbols per region
        
        Returns:
            Regional strategy
        """
        if symbols_per_region is None:
            # Equal distribution
            symbols_per_region = {region: 0 for region in regions}
        
        return {
            'connector': connector_name,
            'regions': regions,
            'symbols_per_region': symbols_per_region,
            'total_regions': len(regions),
        }
    
    def optimize_connector(
        self,
        connector_name: str,
        total_symbols: int,
        ws_limit: int,
        regions: List[str] = None,
        max_connections_per_ip: int = 100,
    ) -> Dict:
        """
        Calculate complete optimization strategy for connector
        
        Args:
            connector_name: Name of connector
            total_symbols: Total symbols to subscribe to
            ws_limit: WebSocket symbol limit
            regions: List of regions (optional)
            max_connections_per_ip: Max connections per IP
        
        Returns:
            Complete optimization strategy
        """
        print(f"🎯 Optimizing {connector_name}...")
        
        # 1. WebSocket strategy
        ws_strategy = self.calculate_websocket_strategy(
            connector_name,
            total_symbols,
            ws_limit,
        )
        
        print(f"   WebSocket: {ws_strategy['num_connections']} connections")
        print(f"   Distribution: {ws_strategy['symbols_per_connection']}")
        print(f"   Efficiency: {ws_strategy['efficiency']:.1f}%")
        
        # 2. IP pool strategy
        ip_strategy = self.calculate_ip_pool_requirements(
            connector_name,
            ws_strategy['num_connections'],
            max_connections_per_ip,
        )
        
        print(f"   IP Pool: {ip_strategy['num_ips_needed']} IPs needed")
        print(f"   IP Distribution: {ip_strategy['connections_per_ip']}")
        
        # 3. Regional strategy (if applicable)
        regional_strategy = None
        if regions:
            regional_strategy = self.calculate_regional_strategy(
                connector_name,
                regions,
            )
            print(f"   Regions: {regional_strategy['total_regions']}")
        
        # Complete strategy
        complete_strategy = {
            'connector': connector_name,
            'websocket_strategy': ws_strategy,
            'ip_strategy': ip_strategy,
            'regional_strategy': regional_strategy,
            'summary': {
                'total_symbols': total_symbols,
                'websocket_connections': ws_strategy['num_connections'],
                'ips_needed': ip_strategy['num_ips_needed'],
                'regions': len(regions) if regions else 0,
            }
        }
        
        return complete_strategy
    
    def get_strategy(self, connector_name: str) -> Dict:
        """Get stored strategy for connector"""
        return self.strategies.get(connector_name)
    
    def compare_strategies(self, connector1: str, connector2: str) -> Dict:
        """Compare strategies between two connectors"""
        strategy1 = self.strategies.get(connector1)
        strategy2 = self.strategies.get(connector2)
        
        if not strategy1 or not strategy2:
            return {'error': 'One or both strategies not found'}
        
        return {
            'connector1': {
                'name': connector1,
                'connections': strategy1['num_connections'],
                'efficiency': strategy1['efficiency'],
            },
            'connector2': {
                'name': connector2,
                'connections': strategy2['num_connections'],
                'efficiency': strategy2['efficiency'],
            },
            'comparison': {
                'more_connections': connector1 if strategy1['num_connections'] > strategy2['num_connections'] else connector2,
                'more_efficient': connector1 if strategy1['efficiency'] > strategy2['efficiency'] else connector2,
            }
        }


# CLI for testing
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Connector Optimization Agent')
    parser.add_argument('--connector', type=str, required=True, help='Connector name')
    parser.add_argument('--symbols', type=int, required=True, help='Total symbols')
    parser.add_argument('--limit', type=int, required=True, help='WebSocket symbol limit')
    parser.add_argument('--regions', type=str, nargs='+', help='Regions (e.g., US EU ASIA)')
    
    args = parser.parse_args()
    
    agent = ConnectorOptimizationAgent()
    
    strategy = agent.optimize_connector(
        args.connector,
        args.symbols,
        args.limit,
        args.regions,
    )
    
    print(f"\n✅ Optimization complete!")
    print(json.dumps(strategy, indent=2))
