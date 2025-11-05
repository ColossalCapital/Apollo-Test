#!/usr/bin/env python3
"""
Deployment Config Generation Script for Akashic IDE

Called by Electron to generate deployment configs
"""

import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.deployment_config_generator import DeploymentConfigGenerator


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'No workspace path provided',
            'usage': 'generate_deployment_configs.py <workspace_path>'
        }))
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    
    try:
        # Load deployment map
        deployment_map_path = Path(workspace_path) / '.akashic' / 'analysis' / 'deployment_map.json'
        
        if not deployment_map_path.exists():
            print(json.dumps({
                'error': 'No deployment map found. Run analysis first.',
                'success': False
            }))
            sys.exit(1)
        
        with open(deployment_map_path, 'r') as f:
            data = json.load(f)
            deployment_map = data.get('deployment_map', {})
        
        # Generate configs
        generator = DeploymentConfigGenerator(workspace_path, deployment_map)
        await generator.generate_all()
        
        # Output result as JSON
        print(json.dumps({
            'success': True,
            'message': 'Deployment configs generated successfully',
            'output_dir': str(Path(workspace_path) / '.akashic' / 'deploy')
        }))
        
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'success': False
        }))
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
