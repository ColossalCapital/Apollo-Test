"""
ConnectorCodeAgent

Automatically updates connector code using LLM:
- Reads change notifications from ConnectorMonitorAgent
- Uses LLM to generate Rust code updates
- Updates symbol lists (CSV/JSON)
- Updates WebSocket connection logic
- Runs tests
- Commits changes to git
- Triggers deployment

This is the CORE of autonomous connector management!
"""

from typing import Dict, List, Optional
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class ConnectorCodeAgent:
    def __init__(self):
        # Base path to AckwardRootsInc connectors
        self.connector_base_path = "/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/AckwardRootsInc/code/connectors/exchanges"
        
        # Track updates
        self.update_history = []
    
    async def process_changes(self, changes_file: str):
        """Process changes from ConnectorMonitorAgent"""
        print(f"📥 Processing changes from: {changes_file}")
        
        # Load changes
        with open(changes_file, 'r') as f:
            change_data = json.load(f)
        
        connector_name = change_data['connector']
        changes = change_data['changes']
        
        print(f"🔧 Updating {connector_name} connector...")
        
        # Process each change
        for change in changes:
            if change['type'] == 'symbols_changed':
                await self.update_symbols(connector_name, change)
            
            elif change['type'] == 'websocket_limit_changed':
                await self.update_websocket_strategy(connector_name, change)
            
            elif change['type'] == 'regional_restriction_changed':
                await self.update_regional_routing(connector_name, change)
        
        # Test the updated connector
        test_passed = await self.test_connector(connector_name)
        
        if test_passed:
            # Commit changes
            await self.commit_changes(connector_name, changes)
            
            # Trigger deployment
            await self.trigger_deployment(connector_name)
            
            print(f"✅ {connector_name} updated successfully!")
        else:
            print(f"❌ Tests failed for {connector_name}, rolling back...")
            await self.rollback_changes(connector_name)
    
    async def update_symbols(self, connector_name: str, change: Dict):
        """Update symbol list (CSV and JSON files)"""
        connector_path = f"{self.connector_base_path}/{connector_name}"
        
        new_symbols = change.get('new_symbols', [])
        removed_symbols = change.get('removed_symbols', [])
        total_symbols = change.get('total_symbols', 0)
        
        print(f"  📝 Updating symbols: +{len(new_symbols)} -{len(removed_symbols)}")
        
        # Update CSV file
        csv_file = f"{connector_path}/{connector_name}_symbols.csv"
        if os.path.exists(csv_file):
            await self._update_csv_symbols(csv_file, new_symbols, removed_symbols)
        
        # Update JSON file
        json_file = f"{connector_path}/{connector_name}_symbols.json"
        if os.path.exists(json_file):
            await self._update_json_symbols(json_file, new_symbols, removed_symbols)
        
        # Update connection_manager.rs if needed
        # Calculate new WebSocket strategy
        from .connector_optimization_agent import ConnectorOptimizationAgent
        
        optimizer = ConnectorOptimizationAgent()
        
        # Get connector config (ws_limit)
        ws_limit = self._get_ws_limit(connector_name)
        
        strategy = optimizer.calculate_websocket_strategy(
            connector_name,
            total_symbols,
            ws_limit,
        )
        
        # If number of connections changed, update connection_manager.rs
        current_connections = self._get_current_connections(connector_path)
        if strategy['num_connections'] != current_connections:
            print(f"  🔌 Updating WebSocket connections: {current_connections} → {strategy['num_connections']}")
            await self._update_connection_manager(connector_path, strategy)
    
    async def _update_csv_symbols(self, csv_file: str, new_symbols: List[str], removed_symbols: List[str]):
        """Update CSV symbol file"""
        # Read current symbols
        with open(csv_file, 'r') as f:
            lines = f.readlines()
        
        # Parse symbols (skip header if exists)
        current_symbols = set()
        header = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if i == 0 and not line.replace(',', '').replace('_', '').isalnum():
                header = line
            elif line:
                current_symbols.add(line.split(',')[0])  # First column is symbol
        
        # Add new symbols
        current_symbols.update(new_symbols)
        
        # Remove symbols
        current_symbols.difference_update(removed_symbols)
        
        # Write back
        with open(csv_file, 'w') as f:
            if header:
                f.write(header + '\n')
            
            for symbol in sorted(current_symbols):
                f.write(f"{symbol}\n")
        
        print(f"    ✅ Updated {csv_file}")
    
    async def _update_json_symbols(self, json_file: str, new_symbols: List[str], removed_symbols: List[str]):
        """Update JSON symbol file"""
        # Read current symbols
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Assume structure: {"symbols": [...]} or just [...]
        if isinstance(data, dict) and 'symbols' in data:
            current_symbols = set(data['symbols'])
        elif isinstance(data, list):
            current_symbols = set(data)
        else:
            current_symbols = set()
        
        # Add new symbols
        current_symbols.update(new_symbols)
        
        # Remove symbols
        current_symbols.difference_update(removed_symbols)
        
        # Write back
        with open(json_file, 'w') as f:
            if isinstance(data, dict):
                data['symbols'] = sorted(list(current_symbols))
                json.dump(data, f, indent=2)
            else:
                json.dump(sorted(list(current_symbols)), f, indent=2)
        
        print(f"    ✅ Updated {json_file}")
    
    def _get_ws_limit(self, connector_name: str) -> int:
        """Get WebSocket symbol limit for connector"""
        # Default limits (can be read from config)
        limits = {
            'binance': 100,
            'coinbase': 50,
            'kraken': 50,
            'bybit': 100,
            'gemini': 50,
        }
        return limits.get(connector_name, 50)
    
    def _get_current_connections(self, connector_path: str) -> int:
        """Get current number of WebSocket connections from code"""
        connection_manager = f"{connector_path}/src/connection_manager.rs"
        
        if not os.path.exists(connection_manager):
            return 1  # Default
        
        # Parse Rust code to find number of connections
        # Look for patterns like: connections: Vec<WebSocket>
        # This is simplified - in production, use proper Rust parser
        with open(connection_manager, 'r') as f:
            content = f.read()
        
        # Simple heuristic: count WebSocket connection creations
        # In real implementation, parse AST
        return 1  # Placeholder
    
    async def _update_connection_manager(self, connector_path: str, strategy: Dict):
        """Update connection_manager.rs with new WebSocket strategy"""
        connection_manager = f"{connector_path}/src/connection_manager.rs"
        
        print(f"    🔧 Updating connection_manager.rs...")
        
        # TODO: Use LLM to generate Rust code
        # See: LLM_CODE_GENERATION_INTEGRATION.md for implementation plan
        
        # Future implementation:
        # 1. Read current code
        # 2. Generate prompt for DeepSeek Coder
        # 3. Call Theta Model API
        # 4. Validate generated code
        # 5. Write updated code
        
        # For now: Add strategy comment
        strategy_comment = f"""
// AUTO-GENERATED by ConnectorCodeAgent
// Strategy: {strategy['num_connections']} WebSocket connections
// Distribution: {strategy['symbols_per_connection']}
// Efficiency: {strategy['efficiency']:.1f}%
// Updated: {datetime.now().isoformat()}
//
// TODO: This will be replaced by LLM-generated Rust code
// Model: deepseek-coder-connector-specialist (fine-tuned on 27+ connectors)
// Training: Theta GPU ($1-2 per job)
// Inference: Theta Model API ($0.001 per update)
"""
        
        if os.path.exists(connection_manager):
            with open(connection_manager, 'r') as f:
                content = f.read()
            
            # Add strategy comment at top
            with open(connection_manager, 'w') as f:
                f.write(strategy_comment + '\n' + content)
            
            print(f"    ✅ Updated connection_manager.rs (LLM integration pending)")
            print(f"    📚 See: LLM_CODE_GENERATION_INTEGRATION.md")
    
    async def update_websocket_strategy(self, connector_name: str, change: Dict):
        """Update WebSocket connection strategy"""
        connector_path = f"{self.connector_base_path}/{connector_name}"
        
        old_limit = change.get('old_limit')
        new_limit = change.get('new_limit')
        
        print(f"  🔌 Updating WebSocket limit: {old_limit} → {new_limit}")
        
        # Recalculate strategy with new limit
        # This would trigger _update_connection_manager
        pass
    
    async def update_regional_routing(self, connector_name: str, change: Dict):
        """Update regional routing logic"""
        connector_path = f"{self.connector_base_path}/{connector_name}"
        
        region = change.get('region')
        accessible = change.get('accessible')
        
        print(f"  🌍 Updating regional routing: {region} → {accessible}")
        
        # Update geo_router.rs or config
        # In production: Use LLM to generate Rust code
        pass
    
    async def test_connector(self, connector_name: str) -> bool:
        """Run tests for connector"""
        connector_path = f"{self.connector_base_path}/{connector_name}"
        
        print(f"  🧪 Testing {connector_name}...")
        
        # Run cargo test
        try:
            result = subprocess.run(
                ['cargo', 'test'],
                cwd=connector_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )
            
            if result.returncode == 0:
                print(f"    ✅ Tests passed!")
                return True
            else:
                print(f"    ❌ Tests failed:")
                print(result.stderr)
                return False
        
        except subprocess.TimeoutExpired:
            print(f"    ❌ Tests timed out")
            return False
        
        except Exception as e:
            print(f"    ❌ Error running tests: {e}")
            return False
    
    async def commit_changes(self, connector_name: str, changes: List[Dict]):
        """Commit changes to git"""
        connector_path = f"{self.connector_base_path}/{connector_name}"
        
        # Create commit message
        change_types = [c['type'] for c in changes]
        commit_msg = f"[Apollo AI] Auto-update {connector_name}: {', '.join(change_types)}"
        
        print(f"  📝 Committing changes...")
        
        try:
            # Git add
            subprocess.run(['git', 'add', '.'], cwd=connector_path, check=True)
            
            # Git commit
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=connector_path,
                check=True,
            )
            
            print(f"    ✅ Committed: {commit_msg}")
            
            # Track update
            self.update_history.append({
                'connector': connector_name,
                'timestamp': datetime.now().isoformat(),
                'changes': changes,
                'commit_message': commit_msg,
            })
        
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Git commit failed: {e}")
    
    async def rollback_changes(self, connector_name: str):
        """Rollback changes if tests fail"""
        connector_path = f"{self.connector_base_path}/{connector_name}"
        
        print(f"  ↩️  Rolling back changes...")
        
        try:
            subprocess.run(
                ['git', 'reset', '--hard', 'HEAD'],
                cwd=connector_path,
                check=True,
            )
            print(f"    ✅ Changes rolled back")
        
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Rollback failed: {e}")
    
    async def trigger_deployment(self, connector_name: str):
        """Trigger deployment of updated connector"""
        print(f"  🚀 Triggering deployment for {connector_name}...")
        
        # In production: Trigger CI/CD pipeline
        # For now: Just log
        
        deployment_script = f"{self.connector_base_path}/../../../deploy/scripts/deploy-connector.sh"
        
        if os.path.exists(deployment_script):
            try:
                subprocess.run(
                    [deployment_script, connector_name],
                    check=True,
                )
                print(f"    ✅ Deployment triggered")
            except subprocess.CalledProcessError as e:
                print(f"    ❌ Deployment failed: {e}")
        else:
            print(f"    ⚠️  Deployment script not found (would deploy in production)")
    
    def get_update_history(self) -> List[Dict]:
        """Get history of updates"""
        return self.update_history


# CLI for testing
if __name__ == "__main__":
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description='Connector Code Agent')
    parser.add_argument('--changes-file', type=str, help='Path to changes JSON file')
    parser.add_argument('--connector', type=str, help='Connector name')
    parser.add_argument('--test', action='store_true', help='Test mode (no commits)')
    
    args = parser.parse_args()
    
    agent = ConnectorCodeAgent()
    
    if args.changes_file:
        # Process changes from file
        asyncio.run(agent.process_changes(args.changes_file))
    
    elif args.connector:
        # Manual test
        print(f"Testing {args.connector}...")
        
        # Create fake changes
        fake_changes = {
            'connector': args.connector,
            'timestamp': datetime.now().isoformat(),
            'changes': [
                {
                    'type': 'symbols_changed',
                    'new_symbols': ['TESTUSDT', 'DEMOUSDT'],
                    'removed_symbols': [],
                    'total_symbols': 502,
                }
            ],
        }
        
        # Save to temp file
        temp_file = f'/tmp/test_changes_{args.connector}.json'
        with open(temp_file, 'w') as f:
            json.dump(fake_changes, f, indent=2)
        
        print(f"Created test changes: {temp_file}")
        
        if not args.test:
            asyncio.run(agent.process_changes(temp_file))
        else:
            print("Test mode - no changes will be committed")
    
    else:
        parser.print_help()
