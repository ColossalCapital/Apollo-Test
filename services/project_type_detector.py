"""
Project Type Detector
Analyzes codebase and automatically detects project type
Generates scaffolding recommendations
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re


@dataclass
class ProjectType:
    """Detected project type with confidence score"""
    primary: str
    secondary: List[str]
    confidence: float
    files_found: Dict[str, List[str]]
    recommendations: List[str]
    scaffold_type: str
    deployment_strategy: str
    testing_strategy: str


@dataclass
class ScaffoldPlan:
    """Complete scaffolding plan for project"""
    project_type: ProjectType
    ui_scaffold: Optional[Dict]
    deployment_scaffold: Dict
    testing_scaffold: Dict
    documentation_scaffold: Dict
    estimated_time_minutes: int


class ProjectTypeDetector:
    """
    Intelligent project type detection
    Analyzes files, dependencies, and structure
    """
    
    PROJECT_TYPES = {
        'web3': {
            'name': 'Web3/Blockchain',
            'scaffold': 'scaffold-eth-2',
            'deployment': 'hardhat + anvil → testnets',
            'testing': 'hardhat test + foundry',
            'indicators': [
                ('*.sol', 0.4, 'solidity_files'),
                ('hardhat.config.js', 0.3, 'hardhat_config'),
                ('hardhat.config.ts', 0.3, 'hardhat_config'),
                ('foundry.toml', 0.3, 'foundry_config'),
                ('remappings.txt', 0.2, 'foundry_remappings'),
            ],
            'dependencies': [
                (['ethers', 'web3.js', 'viem', '@nomicfoundation/hardhat'], 0.2),
            ],
        },
        'react': {
            'name': 'React Frontend',
            'scaffold': 'vite + react + typescript',
            'deployment': 'vercel / netlify / s3',
            'testing': 'vitest + playwright',
            'indicators': [
                ('package.json', 0.2, 'package_json'),
                ('*.jsx', 0.3, 'jsx_files'),
                ('*.tsx', 0.3, 'tsx_files'),
                ('vite.config.ts', 0.2, 'vite_config'),
                ('next.config.js', 0.2, 'next_config'),
            ],
            'dependencies': [
                (['react', 'react-dom'], 0.5),
            ],
        },
        'python_api': {
            'name': 'Python API',
            'scaffold': 'fastapi + uvicorn',
            'deployment': 'docker + kubernetes',
            'testing': 'pytest + httpx',
            'indicators': [
                ('requirements.txt', 0.2, 'requirements'),
                ('pyproject.toml', 0.2, 'pyproject'),
                ('api/**/*.py', 0.3, 'api_files'),
                ('routes/**/*.py', 0.3, 'route_files'),
                ('main.py', 0.2, 'main_file'),
            ],
            'dependencies': [
                (['fastapi', 'flask', 'django', 'starlette'], 0.5),
            ],
        },
        'rust': {
            'name': 'Rust Project',
            'scaffold': 'cargo workspace',
            'deployment': 'binary release / docker',
            'testing': 'cargo test + criterion',
            'indicators': [
                ('Cargo.toml', 0.5, 'cargo_toml'),
                ('src/main.rs', 0.3, 'main_rs'),
                ('src/lib.rs', 0.3, 'lib_rs'),
            ],
            'dependencies': [],
        },
        'mobile': {
            'name': 'Mobile App',
            'scaffold': 'react-native + expo',
            'deployment': 'app store / play store',
            'testing': 'jest + detox',
            'indicators': [
                ('app.json', 0.3, 'expo_config'),
                ('ios/**/*.swift', 0.3, 'ios_files'),
                ('android/**/*.kt', 0.3, 'android_files'),
            ],
            'dependencies': [
                (['react-native', 'expo'], 0.4),
            ],
        },
        'ml': {
            'name': 'Machine Learning',
            'scaffold': 'jupyter + mlflow',
            'deployment': 'model serving (theta gpu)',
            'testing': 'pytest + model validation',
            'indicators': [
                ('*.ipynb', 0.3, 'notebooks'),
                ('models/**/*.py', 0.3, 'model_files'),
                ('train.py', 0.2, 'training_script'),
            ],
            'dependencies': [
                (['tensorflow', 'pytorch', 'scikit-learn', 'transformers'], 0.5),
            ],
        },
        'nextjs': {
            'name': 'Next.js Application',
            'scaffold': 'next.js + typescript',
            'deployment': 'vercel / netlify / docker',
            'testing': 'jest + playwright',
            'indicators': [
                ('next.config.js', 0.5, 'next_config'),
                ('next.config.ts', 0.5, 'next_config_ts'),
                ('pages/**/*.tsx', 0.3, 'pages_dir'),
                ('app/**/*.tsx', 0.3, 'app_dir'),
            ],
            'dependencies': [
                (['next'], 0.5),
            ],
        },
        'vue': {
            'name': 'Vue.js Application',
            'scaffold': 'vite + vue3 + typescript',
            'deployment': 'vercel / netlify / s3',
            'testing': 'vitest + cypress',
            'indicators': [
                ('*.vue', 0.4, 'vue_files'),
                ('vite.config.ts', 0.2, 'vite_config'),
                ('vue.config.js', 0.3, 'vue_config'),
            ],
            'dependencies': [
                (['vue', '@vue/cli'], 0.5),
            ],
        },
        'angular': {
            'name': 'Angular Application',
            'scaffold': 'angular cli',
            'deployment': 'vercel / netlify / s3',
            'testing': 'jasmine + karma',
            'indicators': [
                ('angular.json', 0.5, 'angular_config'),
                ('*.component.ts', 0.3, 'component_files'),
                ('*.module.ts', 0.2, 'module_files'),
            ],
            'dependencies': [
                (['@angular/core'], 0.5),
            ],
        },
        'nodejs_api': {
            'name': 'Node.js API',
            'scaffold': 'express + typescript',
            'deployment': 'docker + kubernetes',
            'testing': 'jest + supertest',
            'indicators': [
                ('server.js', 0.3, 'server_file'),
                ('app.js', 0.3, 'app_file'),
                ('routes/**/*.js', 0.3, 'route_files'),
                ('controllers/**/*.js', 0.2, 'controller_files'),
            ],
            'dependencies': [
                (['express', 'koa', 'fastify', 'nestjs'], 0.5),
            ],
        },
        'golang_api': {
            'name': 'Go API',
            'scaffold': 'gin / fiber framework',
            'deployment': 'docker + kubernetes',
            'testing': 'go test + testify',
            'indicators': [
                ('go.mod', 0.5, 'go_mod'),
                ('main.go', 0.3, 'main_go'),
                ('**/*_test.go', 0.2, 'test_files'),
            ],
            'dependencies': [],
        },
        'flutter': {
            'name': 'Flutter Mobile App',
            'scaffold': 'flutter + dart',
            'deployment': 'app store / play store',
            'testing': 'flutter test + integration_test',
            'indicators': [
                ('pubspec.yaml', 0.5, 'pubspec'),
                ('lib/**/*.dart', 0.3, 'dart_files'),
                ('android/app/build.gradle', 0.2, 'android_config'),
            ],
            'dependencies': [],
        },
        'electron': {
            'name': 'Electron Desktop App',
            'scaffold': 'electron + react/vue',
            'deployment': 'electron-builder',
            'testing': 'spectron + jest',
            'indicators': [
                ('electron.js', 0.3, 'electron_main'),
                ('main.js', 0.3, 'main_file'),
                ('electron-builder.yml', 0.3, 'builder_config'),
            ],
            'dependencies': [
                (['electron'], 0.5),
            ],
        },
        'cli_tool': {
            'name': 'CLI Tool',
            'scaffold': 'commander / yargs',
            'deployment': 'npm / pip / cargo',
            'testing': 'unit tests + integration',
            'indicators': [
                ('bin/**/*', 0.3, 'bin_files'),
                ('cli.js', 0.3, 'cli_file'),
                ('cli.py', 0.3, 'cli_py'),
            ],
            'dependencies': [
                (['commander', 'yargs', 'click', 'typer', 'clap'], 0.3),
            ],
        },
        'library': {
            'name': 'Library/SDK',
            'scaffold': 'typescript / python package',
            'deployment': 'npm / pypi / crates.io',
            'testing': 'comprehensive unit tests',
            'indicators': [
                ('index.ts', 0.2, 'index_ts'),
                ('__init__.py', 0.2, 'init_py'),
                ('lib/**/*', 0.3, 'lib_files'),
            ],
            'dependencies': [],
        },
        'data_pipeline': {
            'name': 'Data Pipeline',
            'scaffold': 'airflow / dagster',
            'deployment': 'kubernetes / cloud',
            'testing': 'pytest + data validation',
            'indicators': [
                ('dags/**/*.py', 0.4, 'dag_files'),
                ('pipelines/**/*.py', 0.3, 'pipeline_files'),
                ('etl/**/*.py', 0.3, 'etl_files'),
            ],
            'dependencies': [
                (['airflow', 'dagster', 'prefect', 'luigi'], 0.4),
            ],
        },
        'microservice': {
            'name': 'Microservice',
            'scaffold': 'docker + kubernetes',
            'deployment': 'kubernetes / cloud run',
            'testing': 'integration + e2e tests',
            'indicators': [
                ('Dockerfile', 0.3, 'dockerfile'),
                ('docker-compose.yml', 0.2, 'compose'),
                ('k8s/**/*.yaml', 0.3, 'k8s_configs'),
                ('service.yaml', 0.2, 'service_config'),
            ],
            'dependencies': [],
        },
        'monorepo': {
            'name': 'Monorepo',
            'scaffold': 'nx / turborepo / lerna',
            'deployment': 'multi-target',
            'testing': 'workspace-wide testing',
            'indicators': [
                ('nx.json', 0.4, 'nx_config'),
                ('turbo.json', 0.4, 'turbo_config'),
                ('lerna.json', 0.4, 'lerna_config'),
                ('packages/**/*', 0.3, 'packages'),
                ('apps/**/*', 0.3, 'apps'),
            ],
            'dependencies': [
                (['nx', 'turbo', 'lerna'], 0.3),
            ],
        },
        'saas_platform': {
            'name': 'SaaS Platform',
            'scaffold': 'full-stack framework',
            'deployment': 'multi-tier cloud',
            'testing': 'e2e + integration + unit',
            'indicators': [
                ('frontend/**/*', 0.2, 'frontend_dir'),
                ('backend/**/*', 0.2, 'backend_dir'),
                ('database/**/*', 0.2, 'database_dir'),
                ('docker-compose.yml', 0.2, 'compose'),
            ],
            'dependencies': [],
        },
        'chrome_extension': {
            'name': 'Chrome Extension',
            'scaffold': 'manifest v3 + react',
            'deployment': 'chrome web store',
            'testing': 'jest + puppeteer',
            'indicators': [
                ('manifest.json', 0.5, 'manifest'),
                ('background.js', 0.3, 'background'),
                ('popup.html', 0.2, 'popup'),
            ],
            'dependencies': [],
        },
        'game': {
            'name': 'Game Development',
            'scaffold': 'unity / unreal / godot',
            'deployment': 'steam / itch.io / stores',
            'testing': 'playtest + unit tests',
            'indicators': [
                ('*.unity', 0.4, 'unity_files'),
                ('*.uproject', 0.4, 'unreal_files'),
                ('project.godot', 0.4, 'godot_project'),
                ('Assets/**/*', 0.2, 'assets'),
            ],
            'dependencies': [],
        },
        'iot': {
            'name': 'IoT Application',
            'scaffold': 'embedded + cloud',
            'deployment': 'device + cloud backend',
            'testing': 'hardware + integration tests',
            'indicators': [
                ('*.ino', 0.4, 'arduino_files'),
                ('platformio.ini', 0.3, 'platformio'),
                ('firmware/**/*', 0.3, 'firmware'),
            ],
            'dependencies': [],
        },
        'wordpress': {
            'name': 'WordPress Site/Plugin',
            'scaffold': 'wordpress + php',
            'deployment': 'wordpress hosting',
            'testing': 'phpunit + wp-cli',
            'indicators': [
                ('wp-config.php', 0.4, 'wp_config'),
                ('wp-content/**/*', 0.3, 'wp_content'),
                ('*.php', 0.2, 'php_files'),
            ],
            'dependencies': [],
        },
        'documentation': {
            'name': 'Documentation Site',
            'scaffold': 'docusaurus / mkdocs / vitepress',
            'deployment': 'github pages / netlify',
            'testing': 'link checking + build tests',
            'indicators': [
                ('docs/**/*.md', 0.4, 'docs_md'),
                ('docusaurus.config.js', 0.3, 'docusaurus'),
                ('mkdocs.yml', 0.3, 'mkdocs'),
            ],
            'dependencies': [
                (['docusaurus', 'mkdocs', 'vitepress'], 0.3),
            ],
        },
        'chrome_extension': {
            'name': 'Chrome Extension',
            'scaffold': 'chrome extension + react',
            'deployment': 'chrome web store',
            'testing': 'jest + puppeteer',
            'indicators': [
                ('manifest.json', 0.5, 'manifest'),
                ('background.js', 0.2, 'background'),
                ('content.js', 0.2, 'content'),
                ('popup.html', 0.2, 'popup'),
            ],
            'dependencies': [
                (['@types/chrome', 'webextension-polyfill'], 0.3),
            ],
        },
        'electron': {
            'name': 'Electron Desktop App',
            'scaffold': 'electron + react',
            'deployment': 'electron-builder',
            'testing': 'spectron + jest',
            'indicators': [
                ('electron.js', 0.3, 'electron_main'),
                ('main.js', 0.2, 'main'),
                ('electron-builder.yml', 0.3, 'builder_config'),
            ],
            'dependencies': [
                (['electron', 'electron-builder'], 0.5),
            ],
        },
        'vscode_extension': {
            'name': 'VS Code Extension',
            'scaffold': 'vscode extension',
            'deployment': 'vscode marketplace',
            'testing': 'vscode test',
            'indicators': [
                ('package.json', 0.2, 'package'),
                ('.vscode/launch.json', 0.3, 'launch_config'),
            ],
            'dependencies': [
                (['vscode', '@types/vscode'], 0.5),
            ],
        },
        'wordpress': {
            'name': 'WordPress Plugin/Theme',
            'scaffold': 'wordpress plugin',
            'deployment': 'wordpress.org / manual',
            'testing': 'phpunit + wp-cli',
            'indicators': [
                ('*.php', 0.3, 'php_files'),
                ('wp-content/**/*', 0.3, 'wp_content'),
                ('style.css', 0.2, 'theme_style'),
            ],
            'dependencies': [
                (['wordpress'], 0.3),
            ],
        },
        'shopify': {
            'name': 'Shopify App/Theme',
            'scaffold': 'shopify cli',
            'deployment': 'shopify app store',
            'testing': 'shopify test',
            'indicators': [
                ('shopify.app.toml', 0.5, 'shopify_config'),
                ('theme.liquid', 0.3, 'liquid_theme'),
                ('sections/**/*.liquid', 0.3, 'liquid_sections'),
            ],
            'dependencies': [
                (['@shopify/cli', '@shopify/app'], 0.3),
            ],
        },
        'discord_bot': {
            'name': 'Discord Bot',
            'scaffold': 'discord.js / discord.py',
            'deployment': 'heroku / railway',
            'testing': 'jest / pytest',
            'indicators': [
                ('bot.js', 0.3, 'bot_main'),
                ('bot.py', 0.3, 'bot_main_py'),
                ('commands/**/*', 0.3, 'commands'),
            ],
            'dependencies': [
                (['discord.js', 'discord.py'], 0.5),
            ],
        },
        'telegram_bot': {
            'name': 'Telegram Bot',
            'scaffold': 'telegraf / python-telegram-bot',
            'deployment': 'heroku / railway',
            'testing': 'jest / pytest',
            'indicators': [
                ('bot.js', 0.2, 'bot_main'),
                ('bot.py', 0.2, 'bot_main_py'),
            ],
            'dependencies': [
                (['telegraf', 'python-telegram-bot'], 0.5),
            ],
        },
        'unity': {
            'name': 'Unity Game',
            'scaffold': 'unity project',
            'deployment': 'steam / app stores',
            'testing': 'unity test framework',
            'indicators': [
                ('Assets/**/*.cs', 0.4, 'unity_scripts'),
                ('ProjectSettings/**/*', 0.3, 'project_settings'),
                ('*.unity', 0.3, 'unity_scenes'),
            ],
            'dependencies': [],
        },
        'unreal': {
            'name': 'Unreal Engine Game',
            'scaffold': 'unreal project',
            'deployment': 'steam / epic games',
            'testing': 'automation testing',
            'indicators': [
                ('*.uproject', 0.5, 'unreal_project'),
                ('Source/**/*.cpp', 0.3, 'cpp_source'),
                ('Content/**/*.uasset', 0.3, 'unreal_assets'),
            ],
            'dependencies': [],
        },
        'godot': {
            'name': 'Godot Game',
            'scaffold': 'godot project',
            'deployment': 'steam / itch.io',
            'testing': 'gut (godot unit test)',
            'indicators': [
                ('project.godot', 0.5, 'godot_project'),
                ('*.gd', 0.4, 'gdscript_files'),
                ('*.tscn', 0.3, 'godot_scenes'),
            ],
            'dependencies': [],
        },
        'jupyter': {
            'name': 'Jupyter Notebooks',
            'scaffold': 'jupyter + papermill',
            'deployment': 'nbviewer / binder',
            'testing': 'nbval + pytest',
            'indicators': [
                ('*.ipynb', 0.5, 'notebooks'),
                ('requirements.txt', 0.2, 'requirements'),
            ],
            'dependencies': [
                (['jupyter', 'jupyterlab', 'notebook'], 0.3),
            ],
        },
        'streamlit': {
            'name': 'Streamlit App',
            'scaffold': 'streamlit',
            'deployment': 'streamlit cloud',
            'testing': 'pytest + streamlit test',
            'indicators': [
                ('streamlit_app.py', 0.5, 'streamlit_main'),
                ('app.py', 0.3, 'app_main'),
            ],
            'dependencies': [
                (['streamlit'], 0.5),
            ],
        },
        'gradio': {
            'name': 'Gradio ML Interface',
            'scaffold': 'gradio',
            'deployment': 'huggingface spaces',
            'testing': 'pytest',
            'indicators': [
                ('app.py', 0.3, 'app_main'),
            ],
            'dependencies': [
                (['gradio'], 0.5),
            ],
        },
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.files_cache = {}
        
    def detect_project_type(self) -> ProjectType:
        """
        Analyze codebase and detect project type
        Returns primary type with confidence score
        """
        scores = {}
        files_found = {}
        
        for project_type, config in self.PROJECT_TYPES.items():
            score, found_files = self._calculate_score(project_type, config)
            scores[project_type] = score
            files_found[project_type] = found_files
        
        # Determine primary type (highest score)
        primary = max(scores, key=scores.get)
        primary_score = scores[primary]
        
        # Determine secondary types (score > 0.3 and not primary)
        secondary = [
            ptype for ptype, score in scores.items()
            if score > 0.3 and ptype != primary
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            primary, 
            secondary, 
            files_found[primary]
        )
        
        config = self.PROJECT_TYPES[primary]
        
        return ProjectType(
            primary=primary,
            secondary=secondary,
            confidence=primary_score,
            files_found=files_found[primary],
            recommendations=recommendations,
            scaffold_type=config['scaffold'],
            deployment_strategy=config['deployment'],
            testing_strategy=config['testing'],
        )
    
    def _calculate_score(
        self, 
        project_type: str, 
        config: Dict
    ) -> Tuple[float, Dict[str, List[str]]]:
        """Calculate confidence score for project type"""
        score = 0.0
        found_files = {}
        
        # Check file indicators
        for pattern, weight, key in config['indicators']:
            files = self._find_files(pattern)
            if files:
                score += weight
                found_files[key] = files
        
        # Check dependencies
        for deps, weight in config['dependencies']:
            if self._has_dependencies(deps):
                score += weight
                found_files['dependencies'] = deps
        
        return min(score, 1.0), found_files
    
    def _find_files(self, pattern: str) -> List[str]:
        """Find files matching pattern (searches recursively)"""
        if pattern in self.files_cache:
            return self.files_cache[pattern]
        
        # Always use ** for recursive search if not already present
        if '**' not in pattern and '/' not in pattern:
            # Convert simple patterns like '*.tsx' to '**/*.tsx'
            pattern = f'**/{pattern}'
        
        try:
            matches = list(self.repo_path.glob(pattern))
            # Exclude node_modules, .git, etc.
            matches = [
                m for m in matches
                if not any(part.startswith('.') or part == 'node_modules' 
                          for part in m.relative_to(self.repo_path).parts)
            ]
        except Exception:
            matches = []
        
        # Convert to relative paths
        result = [str(m.relative_to(self.repo_path)) for m in matches]
        self.files_cache[pattern] = result
        return result
    
    def _has_dependencies(self, deps: List[str]) -> bool:
        """Check if project has any of the dependencies (searches recursively)"""
        # Check all package.json files (including subdirectories)
        package_jsons = list(self.repo_path.glob('**/package.json'))
        for package_json in package_jsons:
            # Skip node_modules
            if 'node_modules' in str(package_json):
                continue
            
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    all_deps = {
                        **data.get('dependencies', {}),
                        **data.get('devDependencies', {}),
                    }
                    if any(dep in all_deps for dep in deps):
                        return True
            except:
                pass
        
        # Check requirements.txt
        requirements = self.repo_path / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements) as f:
                    content = f.read().lower()
                    if any(dep.lower() in content for dep in deps):
                        return True
            except:
                pass
        
        # Check Cargo.toml
        cargo_toml = self.repo_path / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                with open(cargo_toml) as f:
                    content = f.read().lower()
                    if any(dep.lower() in content for dep in deps):
                        return True
            except:
                pass
        
        return False
    
    def _generate_recommendations(
        self,
        primary: str,
        secondary: List[str],
        files_found: Dict[str, List[str]]
    ) -> List[str]:
        """Generate scaffolding recommendations"""
        recommendations = []
        
        if primary == 'web3':
            # Check if UI exists
            has_ui = any(
                self._find_files(pattern)
                for pattern in ['*.jsx', '*.tsx', 'pages/**/*.tsx']
            )
            
            if not has_ui:
                recommendations.append(
                    "🎨 Generate Scaffold-ETH-2 UI for contract interaction"
                )
            
            # Check for tests
            has_tests = any(
                self._find_files(pattern)
                for pattern in ['test/**/*.js', 'test/**/*.ts', 'test/**/*.sol']
            )
            
            if not has_tests:
                recommendations.append(
                    "🧪 Add contract tests (Hardhat or Foundry)"
                )
            
            recommendations.extend([
                "📜 Generate contract documentation from NatSpec",
                "🌐 Set up deployment to test networks (Sepolia, Mumbai)",
                "📊 Create contract interaction diagrams",
                "🔍 Add contract verification scripts",
            ])
        
        elif primary == 'react':
            recommendations.extend([
                "🎨 Set up component library (shadcn/ui)",
                "🧪 Add E2E tests (Playwright)",
                "📦 Configure build optimization",
                "🚀 Set up deployment pipeline (Vercel/Netlify)",
            ])
        
        elif primary == 'python_api':
            recommendations.extend([
                "📝 Generate OpenAPI documentation",
                "🧪 Add API integration tests",
                "🐳 Create Docker configuration",
                "📊 Set up monitoring (Prometheus/Grafana)",
            ])
        
        elif primary == 'rust':
            recommendations.extend([
                "📦 Set up cross-compilation",
                "🧪 Add benchmark suite (Criterion)",
                "📚 Generate documentation (cargo doc)",
                "🚀 Set up GitHub releases",
            ])
        
        return recommendations
    
    def generate_scaffold_plan(self) -> ScaffoldPlan:
        """
        Generate complete scaffolding plan
        """
        project_type = self.detect_project_type()
        
        ui_scaffold = None
        if project_type.primary == 'web3':
            ui_scaffold = self._plan_web3_ui_scaffold(project_type)
        elif project_type.primary == 'react':
            ui_scaffold = self._plan_react_scaffold(project_type)
        
        deployment_scaffold = self._plan_deployment_scaffold(project_type)
        testing_scaffold = self._plan_testing_scaffold(project_type)
        documentation_scaffold = self._plan_documentation_scaffold(project_type)
        
        # Estimate time
        estimated_time = self._estimate_scaffold_time(
            ui_scaffold,
            deployment_scaffold,
            testing_scaffold,
            documentation_scaffold
        )
        
        return ScaffoldPlan(
            project_type=project_type,
            ui_scaffold=ui_scaffold,
            deployment_scaffold=deployment_scaffold,
            testing_scaffold=testing_scaffold,
            documentation_scaffold=documentation_scaffold,
            estimated_time_minutes=estimated_time,
        )
    
    def _plan_web3_ui_scaffold(self, project_type: ProjectType) -> Dict:
        """Plan Scaffold-ETH-2 UI generation"""
        contracts = project_type.files_found.get('solidity_files', [])
        
        return {
            'type': 'scaffold-eth-2',
            'contracts': contracts,
            'components_to_generate': len(contracts),
            'features': [
                'Contract dashboard',
                'Read/Write tabs',
                'Event logs',
                'Transaction history',
                'Network switcher',
                'Wallet connection',
            ],
            'estimated_minutes': 5,
        }
    
    def _plan_react_scaffold(self, project_type: ProjectType) -> Dict:
        """Plan React project scaffold"""
        return {
            'type': 'vite-react-ts',
            'features': [
                'TypeScript setup',
                'TailwindCSS',
                'React Router',
                'Component library (shadcn/ui)',
            ],
            'estimated_minutes': 3,
        }
    
    def _plan_deployment_scaffold(self, project_type: ProjectType) -> Dict:
        """Plan deployment configuration"""
        primary = project_type.primary
        
        if primary == 'web3':
            return {
                'local': {
                    'runtime': 'anvil',
                    'files': [
                        '.akashic/deploy/local/hardhat/hardhat.config.js',
                        '.akashic/deploy/local/scripts/start-anvil.sh',
                        '.akashic/deploy/local/scripts/deploy-local.sh',
                    ],
                },
                'cloud': {
                    'networks': ['sepolia', 'mumbai', 'mainnet'],
                    'files': [
                        '.akashic/deploy/cloud/networks/sepolia.json',
                        '.akashic/deploy/cloud/scripts/deploy-sepolia.sh',
                        '.akashic/deploy/cloud/scripts/verify-contracts.sh',
                    ],
                },
                'estimated_minutes': 10,
            }
        elif primary == 'python_api':
            return {
                'local': {
                    'runtime': 'docker',
                    'files': [
                        '.akashic/deploy/local/docker/docker-compose.yml',
                        '.akashic/deploy/local/docker/Dockerfile',
                    ],
                },
                'cloud': {
                    'platform': 'kubernetes',
                    'files': [
                        '.akashic/deploy/cloud/terraspace/app/stacks/api/main.tf',
                        '.akashic/deploy/cloud/charms/api-service/charmcraft.yaml',
                    ],
                },
                'estimated_minutes': 15,
            }
        else:
            return {'estimated_minutes': 10}
    
    def _plan_testing_scaffold(self, project_type: ProjectType) -> Dict:
        """Plan testing configuration"""
        primary = project_type.primary
        
        if primary == 'web3':
            return {
                'frameworks': ['hardhat', 'foundry'],
                'test_types': ['unit', 'integration', 'fork'],
                'files': [
                    'test/Counter.test.js',
                    'test/integration/Deployment.test.js',
                ],
                'estimated_minutes': 10,
            }
        elif primary == 'react':
            return {
                'frameworks': ['vitest', 'playwright'],
                'test_types': ['unit', 'integration', 'e2e'],
                'files': [
                    'src/components/__tests__/Button.test.tsx',
                    'e2e/user-flow.spec.ts',
                ],
                'estimated_minutes': 10,
            }
        else:
            return {'estimated_minutes': 10}
    
    def _plan_documentation_scaffold(self, project_type: ProjectType) -> Dict:
        """Plan documentation generation"""
        return {
            'files': [
                '.akashic/docs/PROJECT_DOCS.md',
                '.akashic/docs/API_DOCS.md',
                '.akashic/docs/DEPLOYMENT_GUIDE.md',
                '.akashic/docs/TESTING_GUIDE.md',
            ],
            'diagrams': [
                '.akashic/docs/diagrams/architecture.mmd',
                '.akashic/docs/diagrams/deployment_flow.mmd',
            ],
            'estimated_minutes': 5,
        }
    
    def _estimate_scaffold_time(
        self,
        ui_scaffold: Optional[Dict],
        deployment_scaffold: Dict,
        testing_scaffold: Dict,
        documentation_scaffold: Dict,
    ) -> int:
        """Estimate total scaffolding time in minutes"""
        total = 0
        
        if ui_scaffold:
            total += ui_scaffold.get('estimated_minutes', 0)
        
        total += deployment_scaffold.get('estimated_minutes', 0)
        total += testing_scaffold.get('estimated_minutes', 0)
        total += documentation_scaffold.get('estimated_minutes', 0)
        
        return total
    
    def save_detection_report(self, output_path: str):
        """Save detection report to markdown"""
        project_type = self.detect_project_type()
        
        report = f"""# 🔍 Project Type Detection Report

## Detected Project Type

**Primary:** {project_type.primary.upper()} ({self.PROJECT_TYPES[project_type.primary]['name']})
**Confidence:** {project_type.confidence * 100:.1f}%
**Secondary Types:** {', '.join(project_type.secondary) if project_type.secondary else 'None'}

## Files Found

"""
        
        for key, files in project_type.files_found.items():
            report += f"### {key.replace('_', ' ').title()}\n"
            for file in files[:10]:  # Limit to 10 files
                report += f"- `{file}`\n"
            if len(files) > 10:
                report += f"- ... and {len(files) - 10} more\n"
            report += "\n"
        
        report += f"""## Scaffolding Strategy

**UI Scaffold:** {project_type.scaffold_type}
**Deployment:** {project_type.deployment_strategy}
**Testing:** {project_type.testing_strategy}

## Recommendations

"""
        
        for i, rec in enumerate(project_type.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""

## Next Steps

1. Review recommendations above
2. Run `akashic scaffold generate` to create scaffolding
3. Run `akashic deploy setup` to configure deployment
4. Start development with `./akashic/deploy/local/scripts/dev-setup.sh`

---

*Generated by Akashic Intelligence*
"""
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        
        return output_path


def main():
    """CLI interface for project type detection"""
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    detector = ProjectTypeDetector(repo_path)
    project_type = detector.detect_project_type()
    
    print(f"\n🔍 Project Type Detection")
    print(f"=" * 50)
    print(f"Primary: {project_type.primary} ({project_type.confidence * 100:.1f}%)")
    print(f"Secondary: {', '.join(project_type.secondary) if project_type.secondary else 'None'}")
    print(f"\n📊 Scaffolding Strategy:")
    print(f"  UI: {project_type.scaffold_type}")
    print(f"  Deployment: {project_type.deployment_strategy}")
    print(f"  Testing: {project_type.testing_strategy}")
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(project_type.recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Generate scaffold plan
    plan = detector.generate_scaffold_plan()
    print(f"\n⏱️  Estimated scaffolding time: {plan.estimated_time_minutes} minutes")
    
    # Save report
    report_path = os.path.join(repo_path, '.akashic', 'analysis', 'PROJECT_TYPE_DETECTION.md')
    detector.save_detection_report(report_path)
    print(f"\n📝 Report saved to: {report_path}")


if __name__ == '__main__':
    main()
