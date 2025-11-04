"""
Scaffold Generator
Auto-generates project scaffolding based on detected type
Creates UI, deployment configs, tests, and documentation
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from .project_type_detector import ProjectTypeDetector, ScaffoldPlan


@dataclass
class ScaffoldResult:
    """Result of scaffolding operation"""
    success: bool
    files_created: List[str]
    directories_created: List[str]
    commands_run: List[str]
    errors: List[str]
    next_steps: List[str]


class ScaffoldGenerator:
    """
    Generates project scaffolding based on detected type
    Creates complete development environment
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.akashic_path = self.repo_path / '.akashic'
        self.detector = ProjectTypeDetector(str(repo_path))
    
    def generate_full_scaffold(self) -> ScaffoldResult:
        """
        Generate complete scaffolding for project
        """
        # Detect project type
        plan = self.detector.generate_scaffold_plan()
        project_type = plan.project_type
        
        files_created = []
        directories_created = []
        commands_run = []
        errors = []
        
        print(f"🎯 Generating scaffold for {project_type.primary} project...")
        
        # Create .akashic structure
        dirs = self._create_akashic_structure()
        directories_created.extend(dirs)
        
        # Generate based on project type
        if project_type.primary == 'web3':
            result = self._generate_web3_scaffold(plan)
        elif project_type.primary == 'react':
            result = self._generate_react_scaffold(plan)
        elif project_type.primary == 'python_api':
            result = self._generate_python_api_scaffold(plan)
        elif project_type.primary == 'rust':
            result = self._generate_rust_scaffold(plan)
        else:
            result = self._generate_generic_scaffold(plan)
        
        files_created.extend(result['files'])
        directories_created.extend(result['directories'])
        commands_run.extend(result['commands'])
        errors.extend(result.get('errors', []))
        
        # Generate documentation
        doc_files = self._generate_documentation(plan)
        files_created.extend(doc_files)
        
        # Generate next steps
        next_steps = self._generate_next_steps(project_type)
        
        return ScaffoldResult(
            success=len(errors) == 0,
            files_created=files_created,
            directories_created=directories_created,
            commands_run=commands_run,
            errors=errors,
            next_steps=next_steps,
        )
    
    def _create_akashic_structure(self) -> List[str]:
        """Create .akashic directory structure"""
        directories = [
            '.akashic',
            '.akashic/analysis',
            '.akashic/analysis/current_state',
            '.akashic/analysis/restructuring',
            '.akashic/docs',
            '.akashic/docs/diagrams',
            '.akashic/docs/diagrams/rendered',
            '.akashic/deploy',
            '.akashic/deploy/local',
            '.akashic/deploy/local/scripts',
            '.akashic/deploy/local/monitoring',
            '.akashic/deploy/cloud',
            '.akashic/deploy/cloud/scripts',
            '.akashic/deploy/cloud/monitoring',
            '.akashic/pm',
            '.akashic/pm/linear',
            '.akashic/pm/jira',
            '.akashic/pm/github',
            '.akashic/.config',
        ]
        
        created = []
        for directory in directories:
            path = self.repo_path / directory
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                created.append(str(path.relative_to(self.repo_path)))
        
        return created
    
    def _generate_web3_scaffold(self, plan: ScaffoldPlan) -> Dict:
        """Generate Web3 project scaffolding"""
        files = []
        directories = []
        commands = []
        errors = []
        
        print("🌐 Generating Web3 scaffolding...")
        
        # 1. Generate Scaffold-ETH-2 UI
        if plan.ui_scaffold:
            print("  📦 Setting up Scaffold-ETH-2...")
            ui_result = self._setup_scaffold_eth2(plan)
            files.extend(ui_result['files'])
            directories.extend(ui_result['directories'])
            commands.extend(ui_result['commands'])
            errors.extend(ui_result.get('errors', []))
        
        # 2. Generate deployment configs
        print("  🚀 Creating deployment configs...")
        deploy_files = self._generate_web3_deployment_configs()
        files.extend(deploy_files)
        
        # 3. Generate test configs
        print("  🧪 Creating test configs...")
        test_files = self._generate_web3_test_configs()
        files.extend(test_files)
        
        # 4. Generate local dev script
        print("  🔧 Creating dev setup script...")
        script_file = self._generate_web3_dev_script()
        files.append(script_file)
        
        return {
            'files': files,
            'directories': directories,
            'commands': commands,
            'errors': errors,
        }
    
    def _setup_scaffold_eth2(self, plan: ScaffoldPlan) -> Dict:
        """Set up Scaffold-ETH-2 UI"""
        scaffold_path = self.akashic_path / 'scaffold'
        
        files = []
        directories = []
        commands = []
        errors = []
        
        # Check if scaffold already exists
        if scaffold_path.exists():
            print("    ℹ️  Scaffold directory already exists, skipping...")
            return {'files': [], 'directories': [], 'commands': [], 'errors': []}
        
        # Create scaffold directory
        scaffold_path.mkdir(parents=True, exist_ok=True)
        directories.append(str(scaffold_path.relative_to(self.repo_path)))
        
        # Generate package.json for scaffold
        package_json = {
            "name": "scaffold-eth-2-custom",
            "version": "1.0.0",
            "private": True,
            "workspaces": ["packages/*"],
            "scripts": {
                "dev": "cd packages/nextjs && yarn dev",
                "build": "cd packages/nextjs && yarn build",
                "start": "cd packages/nextjs && yarn start",
            }
        }
        
        package_json_path = scaffold_path / 'package.json'
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        files.append(str(package_json_path.relative_to(self.repo_path)))
        
        # Generate README
        readme_content = """# Scaffold-ETH-2 UI

Auto-generated UI for smart contract interaction.

## Quick Start

```bash
# Install dependencies
yarn install

# Start development server
yarn dev
```

Visit http://localhost:3000

## Features

- 🎨 Interactive contract dashboard
- 📝 Read/Write contract functions
- 📊 Event logs
- 🔄 Transaction history
- 🌐 Network switcher
- 💰 Wallet connection

## Generated Components

This UI was auto-generated from your smart contracts.
Each contract has its own component in `packages/nextjs/components/`.

"""
        
        readme_path = scaffold_path / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        files.append(str(readme_path.relative_to(self.repo_path)))
        
        # Note: Full Scaffold-ETH-2 setup would clone the template
        # For now, we create the structure and document it
        
        return {
            'files': files,
            'directories': directories,
            'commands': commands,
            'errors': errors,
        }
    
    def _generate_web3_deployment_configs(self) -> List[str]:
        """Generate Web3 deployment configurations"""
        files = []
        
        # Local deployment - Anvil start script
        anvil_script = """#!/bin/bash
# Start Anvil (local Ethereum node)

echo "📡 Starting Anvil..."
anvil \\
  --port 8545 \\
  --chain-id 31337 \\
  --accounts 10 \\
  --balance 10000 \\
  --gas-limit 30000000

"""
        
        anvil_path = self.akashic_path / 'deploy/local/scripts/start-anvil.sh'
        with open(anvil_path, 'w') as f:
            f.write(anvil_script)
        os.chmod(anvil_path, 0o755)
        files.append(str(anvil_path.relative_to(self.repo_path)))
        
        # Local deployment script
        deploy_local = """#!/bin/bash
# Deploy contracts to local Anvil node

set -e

echo "🚀 Deploying contracts to local network..."

# Check if Anvil is running
if ! nc -z localhost 8545; then
    echo "❌ Anvil not running! Start it with: ./start-anvil.sh"
    exit 1
fi

# Deploy with Hardhat
npx hardhat deploy --network localhost

echo "✅ Contracts deployed!"
echo "  - Network: localhost:8545"
echo "  - Chain ID: 31337"

"""
        
        deploy_path = self.akashic_path / 'deploy/local/scripts/deploy-local.sh'
        with open(deploy_path, 'w') as f:
            f.write(deploy_local)
        os.chmod(deploy_path, 0o755)
        files.append(str(deploy_path.relative_to(self.repo_path)))
        
        # Cloud deployment - Sepolia config
        sepolia_config = {
            "network": "sepolia",
            "chainId": 11155111,
            "rpc": "https://sepolia.infura.io/v3/${INFURA_API_KEY}",
            "explorer": "https://sepolia.etherscan.io",
            "gasPrice": "auto",
        }
        
        sepolia_path = self.akashic_path / 'deploy/cloud/networks/sepolia.json'
        sepolia_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sepolia_path, 'w') as f:
            json.dump(sepolia_config, f, indent=2)
        files.append(str(sepolia_path.relative_to(self.repo_path)))
        
        # Cloud deployment script
        deploy_sepolia = """#!/bin/bash
# Deploy contracts to Sepolia testnet

set -e

echo "🚀 Deploying to Sepolia testnet..."

# Check environment variables
if [ -z "$PRIVATE_KEY" ]; then
    echo "❌ PRIVATE_KEY not set!"
    exit 1
fi

if [ -z "$INFURA_API_KEY" ]; then
    echo "❌ INFURA_API_KEY not set!"
    exit 1
fi

# Deploy
npx hardhat deploy --network sepolia

echo "✅ Deployed to Sepolia!"
echo "  - View on Etherscan: https://sepolia.etherscan.io"

"""
        
        deploy_sepolia_path = self.akashic_path / 'deploy/cloud/scripts/deploy-sepolia.sh'
        with open(deploy_sepolia_path, 'w') as f:
            f.write(deploy_sepolia)
        os.chmod(deploy_sepolia_path, 0o755)
        files.append(str(deploy_sepolia_path.relative_to(self.repo_path)))
        
        return files
    
    def _generate_web3_test_configs(self) -> List[str]:
        """Generate Web3 test configurations"""
        files = []
        
        # Hardhat test config
        test_config = """// Hardhat test configuration
// Auto-generated by Akashic

module.exports = {
  networks: {
    hardhat: {
      chainId: 31337,
    },
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
  mocha: {
    timeout: 40000,
  },
};

"""
        
        config_path = self.akashic_path / 'deploy/local/hardhat/test.config.js'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            f.write(test_config)
        files.append(str(config_path.relative_to(self.repo_path)))
        
        return files
    
    def _generate_web3_dev_script(self) -> str:
        """Generate Web3 development setup script"""
        script = """#!/bin/bash
# Web3 Development Setup
# Auto-generated by Akashic

set -e

echo "🚀 Setting up Web3 development environment"
echo "=========================================="

# Check for required tools
echo "🔍 Checking dependencies..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install: https://nodejs.org"
    exit 1
fi

if ! command -v yarn &> /dev/null; then
    echo "❌ Yarn not found! Installing..."
    npm install -g yarn
fi

if ! command -v anvil &> /dev/null; then
    echo "⚠️  Anvil not found! Installing Foundry..."
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
fi

echo "✅ All dependencies installed"

# Start Anvil
echo ""
echo "📡 Starting Anvil (local Ethereum node)..."
./start-anvil.sh &
ANVIL_PID=$!

# Wait for Anvil to start
sleep 3

# Deploy contracts
echo ""
echo "📜 Deploying contracts..."
./deploy-local.sh

# Start Scaffold-ETH-2 UI (if exists)
if [ -d "../../scaffold" ]; then
    echo ""
    echo "🎨 Starting Scaffold-ETH-2 UI..."
    cd ../../scaffold
    yarn install
    yarn dev &
    UI_PID=$!
    
    echo ""
    echo "✅ Web3 dev environment ready!"
    echo ""
    echo "Services:"
    echo "  - Anvil: http://localhost:8545"
    echo "  - UI: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for Ctrl+C
    trap "kill $ANVIL_PID $UI_PID 2>/dev/null" EXIT
    wait
else
    echo ""
    echo "✅ Anvil and contracts ready!"
    echo ""
    echo "Services:"
    echo "  - Anvil: http://localhost:8545"
    echo ""
    echo "To generate UI, run: akashic scaffold generate"
    echo "Press Ctrl+C to stop Anvil"
    
    trap "kill $ANVIL_PID 2>/dev/null" EXIT
    wait
fi

"""
        
        script_path = self.akashic_path / 'deploy/local/scripts/dev-setup.sh'
        with open(script_path, 'w') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        
        return str(script_path.relative_to(self.repo_path))
    
    def _generate_react_scaffold(self, plan: ScaffoldPlan) -> Dict:
        """Generate React project scaffolding"""
        # TODO: Implement React scaffolding
        return {'files': [], 'directories': [], 'commands': []}
    
    def _generate_python_api_scaffold(self, plan: ScaffoldPlan) -> Dict:
        """Generate Python API scaffolding"""
        # TODO: Implement Python API scaffolding
        return {'files': [], 'directories': [], 'commands': []}
    
    def _generate_rust_scaffold(self, plan: ScaffoldPlan) -> Dict:
        """Generate Rust project scaffolding"""
        # TODO: Implement Rust scaffolding
        return {'files': [], 'directories': [], 'commands': []}
    
    def _generate_generic_scaffold(self, plan: ScaffoldPlan) -> Dict:
        """Generate generic project scaffolding"""
        return {'files': [], 'directories': [], 'commands': []}
    
    def _generate_documentation(self, plan: ScaffoldPlan) -> List[str]:
        """Generate project documentation"""
        files = []
        project_type = plan.project_type
        
        # Deployment guide
        deployment_guide = f"""# 🚀 Deployment Guide

## Project Type: {project_type.primary.upper()}

### Local Development

**Strategy:** {project_type.deployment_strategy}

#### Quick Start

```bash
cd .akashic/deploy/local/scripts
./dev-setup.sh
```

This will:
- Set up local development environment
- Start required services
- Deploy to local network
- Open development UI (if applicable)

### Cloud Deployment

#### Test Networks

For {project_type.primary} projects, we recommend deploying to test networks first:

```bash
cd .akashic/deploy/cloud/scripts
./deploy-testnet.sh
```

#### Production

⚠️ **Important:** Always test thoroughly on testnets before deploying to production!

```bash
cd .akashic/deploy/cloud/scripts
./deploy-production.sh
```

### Monitoring

Monitor your deployments:
- Local: Check logs in terminal
- Cloud: View in deployment dashboard

---

*Auto-generated by Akashic Intelligence*
"""
        
        deployment_path = self.akashic_path / 'docs/DEPLOYMENT_GUIDE.md'
        with open(deployment_path, 'w') as f:
            f.write(deployment_guide)
        files.append(str(deployment_path.relative_to(self.repo_path)))
        
        # Testing guide
        testing_guide = f"""# 🧪 Testing Guide

## Project Type: {project_type.primary.upper()}

### Testing Strategy

**Framework:** {project_type.testing_strategy}

### Running Tests

#### Unit Tests

```bash
# Run all unit tests
npm test  # or: cargo test, pytest, etc.
```

#### Integration Tests

```bash
# Run integration tests
npm run test:integration
```

#### End-to-End Tests

```bash
# Run E2E tests
npm run test:e2e
```

### Test Coverage

View test coverage:

```bash
npm run test:coverage
```

### Continuous Testing

Tests run automatically on:
- Every commit (pre-commit hook)
- Every pull request (CI/CD)
- Before deployment

---

*Auto-generated by Akashic Intelligence*
"""
        
        testing_path = self.akashic_path / 'docs/TESTING_GUIDE.md'
        with open(testing_path, 'w') as f:
            f.write(testing_guide)
        files.append(str(testing_path.relative_to(self.repo_path)))
        
        return files
    
    def _generate_next_steps(self, project_type) -> List[str]:
        """Generate next steps for user"""
        steps = [
            "📝 Review generated files in .akashic/",
            "🔧 Configure environment variables (if needed)",
            "🚀 Run: cd .akashic/deploy/local/scripts && ./dev-setup.sh",
        ]
        
        if project_type.primary == 'web3':
            steps.extend([
                "🌐 Visit http://localhost:3000 to see your contract UI",
                "📜 Deploy to testnet: cd .akashic/deploy/cloud/scripts && ./deploy-sepolia.sh",
            ])
        
        steps.extend([
            "📚 Read deployment guide: .akashic/docs/DEPLOYMENT_GUIDE.md",
            "🧪 Read testing guide: .akashic/docs/TESTING_GUIDE.md",
        ])
        
        return steps


def main():
    """CLI interface for scaffold generation"""
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    generator = ScaffoldGenerator(repo_path)
    result = generator.generate_full_scaffold()
    
    print(f"\n{'✅' if result.success else '❌'} Scaffolding {'Complete' if result.success else 'Failed'}!")
    print(f"=" * 50)
    
    if result.directories_created:
        print(f"\n📁 Directories Created: {len(result.directories_created)}")
        for directory in result.directories_created[:5]:
            print(f"  - {directory}")
        if len(result.directories_created) > 5:
            print(f"  ... and {len(result.directories_created) - 5} more")
    
    if result.files_created:
        print(f"\n📄 Files Created: {len(result.files_created)}")
        for file in result.files_created[:10]:
            print(f"  - {file}")
        if len(result.files_created) > 10:
            print(f"  ... and {len(result.files_created) - 10} more")
    
    if result.errors:
        print(f"\n⚠️  Errors:")
        for error in result.errors:
            print(f"  - {error}")
    
    print(f"\n🎯 Next Steps:")
    for i, step in enumerate(result.next_steps, 1):
        print(f"  {i}. {step}")


if __name__ == '__main__':
    main()
