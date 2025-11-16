#!/usr/bin/env python3
"""
Deployment Analysis Script for Akashic IDE

Called by Electron to run deployment analysis
"""

import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.deployment_mapper import DeploymentMapper
from services.deployment_reconciliation import DeploymentReconciliation


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'No workspace path provided',
            'usage': 'analyze_deployments.py <workspace_path>'
        }))
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    
    try:
        # Run deployment mapper
        mapper = DeploymentMapper(workspace_path)
        result = await mapper.analyze_deployments()
        
        # Save report
        analysis_dir = Path(workspace_path) / '.akashic' / 'analysis'
        mapper.save_report(analysis_dir)
        
        # Run reconciliation if conflicts found
        reconciliation_result = None
        if result['conflicts']:
            reconciliation = DeploymentReconciliation(workspace_path)
            reconciliation_result = await reconciliation.reconcile_conflicts(
                result['conflicts'],
                result['deployment_map']
            )
            
            # Save reconciliation data as JSON for IDE
            reconciliation_dir = Path(workspace_path) / '.akashic' / 'reconciliation'
            reconciliation_dir.mkdir(parents=True, exist_ok=True)
            
            reconciliation_data_path = reconciliation_dir / 'reconciliation_data.json'
            with open(reconciliation_data_path, 'w') as f:
                json.dump({
                    'conflicts_analyzed': len(result['conflicts']),
                    'recommendations_generated': len(reconciliation_result['recommendations']),
                    'action_plan_steps': len(reconciliation_result['action_plan']),
                }, f, indent=2)
        
        # Output result as JSON
        print(json.dumps({
            'success': True,
            'folders_analyzed': len(result['deployment_map']),
            'conflicts': len(result['conflicts']),
            'recommendations': len(result['recommendations']),
        }))
        
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'success': False
        }))
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
