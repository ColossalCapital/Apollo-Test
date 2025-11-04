"""
Deployment Mapper - Maps scattered deployment configurations

Analyzes deployment-related folders (docker, kubernetes, juju, terraform, etc.)
and maps their functionality to the standardized .akashic/deploy/ structure.

Handles:
- Docker Compose files
- Kubernetes manifests
- Juju charms
- Terraform/Terraspace configs
- Cost optimization configs
- CI/CD pipelines
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeploymentMapper:
    """Maps scattered deployment configurations to .akashic/deploy/"""
    
    # Deployment-related folder patterns
    DEPLOYMENT_FOLDERS = [
        'docker',
        'docker-compose',
        'podman',
        'kubernetes',
        'k8s',
        'microk8s',
        'juju',
        'terraform',
        'terraspace',
        'tilt',
        'ansible',
        'helm',
        'ci',
        'cd',
        '.github/workflows',
        '.gitlab-ci',
        'bitbucket-pipelines',
        'jenkins',
        'cost-optimization',
        'monitoring',
        'observability',
    ]
    
    # File patterns to analyze
    FILE_PATTERNS = {
        'docker': ['Dockerfile', 'docker-compose*.yml', 'docker-compose*.yaml', '.dockerignore'],
        'podman': ['Containerfile', 'podman-compose*.yml', 'podman-compose*.yaml'],
        'kubernetes': ['*.yaml', '*.yml', 'kustomization.yaml'],
        'juju': ['*.yaml', 'charmcraft.yaml', 'metadata.yaml', 'bundle.yaml'],
        'terraform': ['*.tf', '*.tfvars', 'terraform.tfstate'],
        'terraspace': ['*.tf', '*.tfvars', 'config/terraform/*.tf'],
        'tilt': ['Tiltfile', 'tilt_config.json'],
        'ci_cd': ['.github/workflows/*.yml', '.gitlab-ci.yml', 'bitbucket-pipelines.yml', 'Jenkinsfile'],
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.deployment_map = {
            'local': {},
            'cloud': {},
            'ci_cd': {},
            'monitoring': {},
            'cost_optimization': {},
        }
        self.conflicts = []
        self.recommendations = []
        
    async def analyze_deployments(self) -> Dict:
        """Analyze all deployment configurations"""
        logger.info("🗺️  Analyzing deployment configurations...")
        
        # Find all deployment-related folders
        deployment_folders = self._find_deployment_folders()
        
        # Analyze each folder
        for folder in deployment_folders:
            await self._analyze_folder(folder)
        
        # Detect conflicts and overlaps
        self._detect_conflicts()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Create mapping report
        report = self._create_report()
        
        logger.info(f"✅ Analyzed {len(deployment_folders)} deployment folders")
        
        return {
            'deployment_map': self.deployment_map,
            'conflicts': self.conflicts,
            'recommendations': self.recommendations,
            'report': report,
        }
    
    def _find_deployment_folders(self) -> List[Path]:
        """Find all deployment-related folders"""
        folders = []
        
        for pattern in self.DEPLOYMENT_FOLDERS:
            # Handle nested patterns like .github/workflows
            if '/' in pattern:
                path = self.repo_path / pattern
                if path.exists():
                    folders.append(path)
            else:
                # Find all matching folders
                for folder in self.repo_path.rglob(pattern):
                    if folder.is_dir() and not self._should_ignore(folder):
                        folders.append(folder)
        
        return folders
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored"""
        ignore_patterns = [
            '.git',
            'node_modules',
            '__pycache__',
            '.venv',
            'venv',
            '.akashic',
        ]
        
        path_str = str(path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    async def _analyze_folder(self, folder: Path):
        """Analyze a deployment folder"""
        folder_name = folder.name.lower()
        rel_path = folder.relative_to(self.repo_path)
        
        logger.info(f"  📂 Analyzing {rel_path}")
        
        # Categorize folder
        category = self._categorize_folder(folder_name)
        
        # Find all relevant files
        files = self._find_deployment_files(folder)
        
        # Analyze each file
        file_analysis = []
        for file in files:
            analysis = await self._analyze_file(file)
            if analysis:
                file_analysis.append(analysis)
        
        # Store in deployment map
        if category not in self.deployment_map:
            self.deployment_map[category] = {}
        
        self.deployment_map[category][str(rel_path)] = {
            'folder': str(rel_path),
            'files': [str(f.relative_to(self.repo_path)) for f in files],
            'analysis': file_analysis,
            'target_location': self._suggest_target_location(category, folder_name),
        }
    
    def _categorize_folder(self, folder_name: str) -> str:
        """Categorize deployment folder"""
        if folder_name in ['docker', 'docker-compose', 'podman', 'tilt']:
            return 'local'
        elif folder_name in ['kubernetes', 'k8s', 'microk8s', 'juju', 'terraform', 'terraspace', 'helm']:
            return 'cloud'
        elif folder_name in ['ci', 'cd'] or 'workflow' in folder_name or 'pipeline' in folder_name:
            return 'ci_cd'
        elif folder_name in ['monitoring', 'observability', 'prometheus', 'grafana']:
            return 'monitoring'
        elif 'cost' in folder_name or 'optimization' in folder_name:
            return 'cost_optimization'
        else:
            return 'cloud'  # Default to cloud
    
    def _suggest_target_location(self, category: str, folder_name: str) -> str:
        """Suggest target location in .akashic/deploy/"""
        if category == 'local':
            if 'docker' in folder_name:
                return '.akashic/deploy/local/docker/'
            elif 'podman' in folder_name:
                return '.akashic/deploy/local/podman/'
            elif 'tilt' in folder_name:
                return '.akashic/deploy/local/tilt/'
            else:
                return '.akashic/deploy/local/scripts/'
        elif category == 'cloud':
            if 'kubernetes' in folder_name or 'k8s' in folder_name or 'microk8s' in folder_name:
                return '.akashic/deploy/cloud/kubernetes/'
            elif 'juju' in folder_name:
                return '.akashic/deploy/cloud/juju/'
            elif 'terraspace' in folder_name:
                return '.akashic/deploy/cloud/terraspace/'
            elif 'terraform' in folder_name:
                return '.akashic/deploy/cloud/terraspace/'  # Migrate Terraform to Terraspace
            else:
                return '.akashic/deploy/cloud/kubernetes/'
        elif category == 'ci_cd':
            return '.akashic/ci/'
        elif category == 'monitoring':
            return '.akashic/deploy/cloud/monitoring/'
        elif category == 'cost_optimization':
            return '.akashic/analysis/cost-optimization/'
        else:
            return '.akashic/deploy/cloud/'
    
    def _find_deployment_files(self, folder: Path) -> List[Path]:
        """Find all deployment files in folder"""
        files = []
        
        # Common deployment file patterns
        patterns = [
            '*.yml',
            '*.yaml',
            '*.tf',
            '*.tfvars',
            'Dockerfile*',
            'Containerfile*',
            'docker-compose*',
            'podman-compose*',
            'Tiltfile',
            '*.sh',
            '*.py',
            'Makefile',
            'Jenkinsfile',
        ]
        
        for pattern in patterns:
            files.extend(folder.glob(pattern))
            files.extend(folder.rglob(pattern))
        
        # Remove duplicates
        return list(set(files))
    
    async def _analyze_file(self, file: Path) -> Optional[Dict]:
        """Analyze a deployment file"""
        try:
            content = file.read_text()
            
            analysis = {
                'file': file.name,
                'type': self._detect_file_type(file),
                'size': file.stat().st_size,
                'services': [],
                'dependencies': [],
                'environment': [],
            }
            
            # Parse based on file type
            if file.suffix in ['.yml', '.yaml']:
                try:
                    data = yaml.safe_load(content)
                    if isinstance(data, dict):
                        # Docker Compose
                        if 'services' in data:
                            analysis['services'] = list(data['services'].keys())
                        # Kubernetes
                        if 'kind' in data:
                            analysis['kubernetes_kind'] = data['kind']
                        # Juju
                        if 'charm' in data or 'charms' in data:
                            analysis['juju_charm'] = True
                except:
                    pass
            
            # Detect cloud providers
            if 'aws' in content.lower():
                analysis['cloud_providers'] = analysis.get('cloud_providers', []) + ['aws']
            if 'gcp' in content.lower() or 'google' in content.lower():
                analysis['cloud_providers'] = analysis.get('cloud_providers', []) + ['gcp']
            if 'azure' in content.lower():
                analysis['cloud_providers'] = analysis.get('cloud_providers', []) + ['azure']
            if 'vultr' in content.lower():
                analysis['cloud_providers'] = analysis.get('cloud_providers', []) + ['vultr']
            if 'digitalocean' in content.lower():
                analysis['cloud_providers'] = analysis.get('cloud_providers', []) + ['digitalocean']
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file}: {e}")
            return None
    
    def _detect_file_type(self, file: Path) -> str:
        """Detect deployment file type"""
        name = file.name.lower()
        parent_str = str(file.parent).lower()
        
        if 'dockerfile' in name:
            return 'docker'
        elif 'containerfile' in name:
            return 'podman'
        elif 'docker-compose' in name:
            return 'docker-compose'
        elif 'podman-compose' in name:
            return 'podman-compose'
        elif name == 'tiltfile':
            return 'tilt'
        elif name.endswith('.tf'):
            if 'terraspace' in parent_str:
                return 'terraspace'
            else:
                return 'terraform'
        elif 'kubernetes' in parent_str or 'k8s' in parent_str or 'microk8s' in parent_str:
            return 'kubernetes'
        elif 'juju' in parent_str:
            return 'juju'
        elif 'workflow' in parent_str or name == '.gitlab-ci.yml':
            return 'ci_cd'
        else:
            return 'unknown'
    
    def _detect_conflicts(self):
        """Detect conflicts and overlapping configurations"""
        self.conflicts = []
        
        # Check for multiple Docker setups
        docker_folders = []
        for category, folders in self.deployment_map.items():
            for folder_path, data in folders.items():
                if 'docker' in folder_path.lower():
                    docker_folders.append(folder_path)
        
        if len(docker_folders) > 1:
            self.conflicts.append({
                'type': 'docker_overlap',
                'severity': 'high',
                'description': f'Multiple Docker configurations found in {len(docker_folders)} locations',
                'locations': docker_folders,
                'recommendation': 'Consolidate all Docker configs to .akashic/deploy/local/docker/',
            })
        
        # Check for multiple Kubernetes setups
        k8s_folders = []
        for category, folders in self.deployment_map.items():
            for folder_path, data in folders.items():
                if 'kubernetes' in folder_path.lower() or 'k8s' in folder_path.lower():
                    k8s_folders.append(folder_path)
        
        if len(k8s_folders) > 1:
            self.conflicts.append({
                'type': 'kubernetes_overlap',
                'severity': 'high',
                'description': f'Multiple Kubernetes configurations found in {len(k8s_folders)} locations',
                'locations': k8s_folders,
                'recommendation': 'Consolidate all Kubernetes configs to .akashic/deploy/cloud/kubernetes/',
            })
    
    def _generate_recommendations(self):
        """Generate migration recommendations"""
        self.recommendations = []
        
        for category, folders in self.deployment_map.items():
            for folder_path, data in folders.items():
                target = data['target_location']
                
                self.recommendations.append({
                    'source': folder_path,
                    'target': target,
                    'category': category,
                    'files_count': len(data['files']),
                    'action': 'move',
                    'priority': 'high' if category in ['local', 'cloud'] else 'medium',
                })
    
    def _create_report(self) -> str:
        """Create deployment mapping report"""
        report = f"""# Deployment Configuration Mapping

Generated: {datetime.now().isoformat()}

## Summary

- **Deployment Folders Found:** {sum(len(folders) for folders in self.deployment_map.values())}
- **Conflicts Detected:** {len(self.conflicts)}
- **Migration Recommendations:** {len(self.recommendations)}

## Current Deployment Structure

"""
        
        for category, folders in self.deployment_map.items():
            if not folders:
                continue
                
            report += f"\n### {category.replace('_', ' ').title()}\n\n"
            
            for folder_path, data in folders.items():
                report += f"**{folder_path}** ({len(data['files'])} files)\n"
                report += f"- Target: `{data['target_location']}`\n"
                
                # Show services if any
                for file_analysis in data['analysis']:
                    if file_analysis.get('services'):
                        report += f"- Services: {', '.join(file_analysis['services'])}\n"
                    if file_analysis.get('cloud_providers'):
                        report += f"- Cloud Providers: {', '.join(file_analysis['cloud_providers'])}\n"
                
                report += "\n"
        
        # Conflicts
        if self.conflicts:
            report += "\n## ⚠️  Conflicts Detected\n\n"
            
            for conflict in self.conflicts:
                report += f"### {conflict['type'].replace('_', ' ').title()}\n"
                report += f"**Severity:** {conflict['severity'].upper()}\n\n"
                report += f"{conflict['description']}\n\n"
                report += "**Locations:**\n"
                for loc in conflict['locations']:
                    report += f"- `{loc}`\n"
                report += f"\n**Recommendation:** {conflict['recommendation']}\n\n"
        
        # Migration Plan
        report += "\n## 📋 Migration Plan\n\n"
        
        for i, rec in enumerate(self.recommendations, 1):
            report += f"{i}. **{rec['source']}** → `{rec['target']}`\n"
            report += f"   - Category: {rec['category']}\n"
            report += f"   - Files: {rec['files_count']}\n"
            report += f"   - Priority: {rec['priority'].upper()}\n\n"
        
        # Cursor Prompt
        report += "\n## 🤖 AI-Assisted Migration Prompt\n\n"
        report += "```\n"
        report += "Migrate deployment configurations to .akashic/deploy/ structure:\n\n"
        
        for rec in self.recommendations:
            report += f"1. Move {rec['source']} to {rec['target']}\n"
            report += f"   - Update all references in CI/CD pipelines\n"
            report += f"   - Update documentation\n"
            report += f"   - Test deployment after migration\n\n"
        
        report += "After migration:\n"
        report += "- Verify all deployments still work\n"
        report += "- Update README with new structure\n"
        report += "- Archive old deployment folders\n"
        report += "```\n"
        
        return report
    
    def save_report(self, output_dir: Path):
        """Save deployment mapping report"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = output_dir / "DEPLOYMENT_MAPPING.md"
        report_path.write_text(self._create_report())
        
        # Also save JSON for programmatic access
        json_path = output_dir / "deployment_map.json"
        with open(json_path, 'w') as f:
            json.dump({
                'deployment_map': {k: {k2: {**v2, 'analysis': []} for k2, v2 in v.items()} for k, v in self.deployment_map.items()},
                'conflicts': self.conflicts,
                'recommendations': self.recommendations,
            }, f, indent=2)
        
        logger.info(f"📝 Saved deployment mapping to {report_path}")


if __name__ == "__main__":
    import asyncio
    
    async def main():
        mapper = DeploymentMapper("/path/to/repo")
        result = await mapper.analyze_deployments()
        mapper.save_report(Path("/path/to/repo/.akashic/analysis"))
    
    asyncio.run(main())
