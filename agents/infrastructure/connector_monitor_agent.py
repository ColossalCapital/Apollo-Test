"""
ConnectorMonitorAgent

Monitors ALL data connectors (27+ exchanges) for changes:
- New symbols added
- Symbols removed
- Rate limit changes
- Regional restrictions
- WebSocket limit changes
- API endpoint changes

Runs 24/7, checks every minute, triggers updates when changes detected.
"""

from typing import Dict, List, Optional, Set
import asyncio
import aiohttp
from datetime import datetime
import json
import os

class ConnectorMonitorAgent:
    def __init__(self):
        self.connectors = {
            'binance': {
                'name': 'Binance',
                'rest_api': 'https://api.binance.com/api/v3',
                'ws_base': 'wss://stream.binance.com:9443/ws',
                'ws_limit': 100,  # symbols per WebSocket
                'check_interval': 60,  # seconds
                'regions': {
                    'US': 'https://api.binance.us/api/v3',
                    'GLOBAL': 'https://api.binance.com/api/v3',
                },
            },
            'coinbase': {
                'name': 'Coinbase',
                'rest_api': 'https://api.exchange.coinbase.com',
                'ws_base': 'wss://ws-feed.exchange.coinbase.com',
                'ws_limit': 50,
                'check_interval': 60,
                'regions': {
                    'GLOBAL': 'https://api.exchange.coinbase.com',
                },
            },
            'kraken': {
                'name': 'Kraken',
                'rest_api': 'https://api.kraken.com/0/public',
                'ws_base': 'wss://ws.kraken.com',
                'ws_limit': 50,
                'check_interval': 60,
                'regions': {
                    'GLOBAL': 'https://api.kraken.com/0/public',
                },
            },
            'bybit': {
                'name': 'Bybit',
                'rest_api': 'https://api.bybit.com/v5',
                'ws_base': 'wss://stream.bybit.com/v5/public/linear',
                'ws_limit': 100,
                'check_interval': 60,
                'regions': {
                    'GLOBAL': 'https://api.bybit.com/v5',
                },
            },
            'gemini': {
                'name': 'Gemini',
                'rest_api': 'https://api.gemini.com/v1',
                'ws_base': 'wss://api.gemini.com/v1/marketdata',
                'ws_limit': 50,
                'check_interval': 60,
                'regions': {
                    'GLOBAL': 'https://api.gemini.com/v1',
                },
            },
            # Add remaining 22+ connectors here
        }
        
        # Store last known state
        self.last_known_state = {}
        
        # Store detected changes
        self.detected_changes = []
        
        # Base path to connector code
        self.connector_base_path = "/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/AckwardRootsInc/code/connectors/exchanges"
    
    async def monitor_all_connectors(self):
        """Monitor ALL connectors in parallel - runs 24/7"""
        print("🚀 ConnectorMonitorAgent starting...")
        print(f"   Monitoring {len(self.connectors)} connectors")
        
        while True:
            try:
                # Monitor all connectors in parallel
                tasks = [
                    self.monitor_connector(name, config)
                    for name, config in self.connectors.items()
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    connector_name = list(self.connectors.keys())[i]
                    
                    if isinstance(result, Exception):
                        print(f"❌ Error monitoring {connector_name}: {result}")
                    elif result:
                        print(f"🚨 Changes detected in {connector_name}!")
                        await self.trigger_update(connector_name, result)
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                await asyncio.sleep(60)
    
    async def monitor_connector(self, connector_name: str, config: Dict) -> Optional[List[Dict]]:
        """Monitor ONE specific connector for changes"""
        changes = []
        
        try:
            # 1. Check for symbol changes
            symbol_change = await self.check_symbols(connector_name, config)
            if symbol_change:
                changes.append(symbol_change)
            
            # 2. Check for rate limit changes
            rate_limit_change = await self.check_rate_limits(connector_name, config)
            if rate_limit_change:
                changes.append(rate_limit_change)
            
            # 3. Check for regional restrictions
            region_change = await self.check_regional_restrictions(connector_name, config)
            if region_change:
                changes.append(region_change)
            
            # 4. Check for WebSocket limit changes
            ws_change = await self.check_websocket_limits(connector_name, config)
            if ws_change:
                changes.append(ws_change)
            
            return changes if changes else None
            
        except Exception as e:
            print(f"❌ Error monitoring {connector_name}: {e}")
            return None
    
    async def check_symbols(self, connector_name: str, config: Dict) -> Optional[Dict]:
        """Check if symbol list changed"""
        async with aiohttp.ClientSession() as session:
            try:
                current_symbols = await self._fetch_symbols(session, connector_name, config)
                
                if current_symbols is None:
                    return None
                
                # Get last known symbols
                state_key = f'{connector_name}_symbols'
                last_symbols = self.last_known_state.get(state_key, set())
                
                # Compare
                if current_symbols != last_symbols:
                    new_symbols = current_symbols - last_symbols
                    removed_symbols = last_symbols - current_symbols
                    
                    # Update state
                    self.last_known_state[state_key] = current_symbols
                    
                    print(f"📊 {connector_name}: {len(current_symbols)} symbols (+{len(new_symbols)} -{len(removed_symbols)})")
                    
                    return {
                        'type': 'symbols_changed',
                        'connector': connector_name,
                        'new_symbols': list(new_symbols),
                        'removed_symbols': list(removed_symbols),
                        'total_symbols': len(current_symbols),
                        'timestamp': datetime.now().isoformat(),
                    }
                
            except Exception as e:
                print(f"❌ Error checking symbols for {connector_name}: {e}")
        
        return None
    
    async def _fetch_symbols(self, session: aiohttp.ClientSession, connector_name: str, config: Dict) -> Optional[Set[str]]:
        """Fetch current symbol list from exchange API"""
        
        if connector_name == 'binance':
            try:
                async with session.get(f"{config['rest_api']}/exchangeInfo") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING'}
            except Exception as e:
                print(f"❌ Error fetching Binance symbols: {e}")
        
        elif connector_name == 'coinbase':
            try:
                async with session.get(f"{config['rest_api']}/products") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {p['id'] for p in data if p.get('status') == 'online'}
            except Exception as e:
                print(f"❌ Error fetching Coinbase symbols: {e}")
        
        elif connector_name == 'kraken':
            try:
                async with session.get(f"{config['rest_api']}/AssetPairs") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('error') == []:
                            return set(data.get('result', {}).keys())
            except Exception as e:
                print(f"❌ Error fetching Kraken symbols: {e}")
        
        elif connector_name == 'bybit':
            try:
                async with session.get(f"{config['rest_api']}/market/instruments-info?category=linear") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('retCode') == 0:
                            return {item['symbol'] for item in data.get('result', {}).get('list', [])}
            except Exception as e:
                print(f"❌ Error fetching Bybit symbols: {e}")
        
        elif connector_name == 'gemini':
            try:
                async with session.get(f"{config['rest_api']}/symbols") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return set(data)
            except Exception as e:
                print(f"❌ Error fetching Gemini symbols: {e}")
        
        # Add more exchanges as needed
        
        return None
    
    async def check_rate_limits(self, connector_name: str, config: Dict) -> Optional[Dict]:
        """Check if rate limits changed"""
        # TODO: Implement rate limit checking
        # Most exchanges return rate limit info in headers
        return None
    
    async def check_regional_restrictions(self, connector_name: str, config: Dict) -> Optional[Dict]:
        """Check if regional restrictions changed"""
        # TODO: Implement regional restriction checking
        # Test API access from different regions
        return None
    
    async def check_websocket_limits(self, connector_name: str, config: Dict) -> Optional[Dict]:
        """Check if WebSocket limits changed"""
        # TODO: Implement WebSocket limit checking
        # Usually documented in API docs
        return None
    
    async def trigger_update(self, connector_name: str, changes: List[Dict]):
        """Trigger ConnectorCodeAgent to update connector"""
        print(f"🔔 Triggering update for {connector_name}")
        print(f"   Changes: {json.dumps(changes, indent=2)}")
        
        # Save changes to file for ConnectorCodeAgent to process
        changes_file = f"/tmp/connector_changes_{connector_name}_{datetime.now().timestamp()}.json"
        
        with open(changes_file, 'w') as f:
            json.dump({
                'connector': connector_name,
                'timestamp': datetime.now().isoformat(),
                'changes': changes,
            }, f, indent=2)
        
        print(f"   Saved changes to: {changes_file}")
        
        # TODO: Trigger ConnectorCodeAgent
        # For now, just log the changes
        # Later: await connector_code_agent.update_connector(connector_name, changes)
    
    def get_connector_stats(self) -> Dict:
        """Get statistics about monitored connectors"""
        stats = {
            'total_connectors': len(self.connectors),
            'connectors': {},
        }
        
        for name, config in self.connectors.items():
            state_key = f'{name}_symbols'
            symbol_count = len(self.last_known_state.get(state_key, set()))
            
            stats['connectors'][name] = {
                'name': config['name'],
                'symbols': symbol_count,
                'ws_limit': config['ws_limit'],
                'regions': list(config['regions'].keys()),
            }
        
        return stats


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Connector Monitor Agent')
    parser.add_argument('--test', action='store_true', help='Run single test check')
    parser.add_argument('--monitor', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--connector', type=str, help='Test specific connector')
    
    args = parser.parse_args()
    
    agent = ConnectorMonitorAgent()
    
    if args.test:
        # Run single check
        async def test():
            if args.connector:
                config = agent.connectors.get(args.connector)
                if config:
                    print(f"Testing {args.connector}...")
                    result = await agent.monitor_connector(args.connector, config)
                    print(f"Result: {result}")
                else:
                    print(f"Unknown connector: {args.connector}")
            else:
                print("Testing all connectors...")
                tasks = [
                    agent.monitor_connector(name, config)
                    for name, config in agent.connectors.items()
                ]
                results = await asyncio.gather(*tasks)
                
                for name, result in zip(agent.connectors.keys(), results):
                    print(f"{name}: {result}")
                
                # Print stats
                stats = agent.get_connector_stats()
                print(f"\nStats: {json.dumps(stats, indent=2)}")
        
        asyncio.run(test())
    
    elif args.monitor:
        # Run continuous monitoring
        print("Starting continuous monitoring...")
        asyncio.run(agent.monitor_all_connectors())
    
    else:
        parser.print_help()
