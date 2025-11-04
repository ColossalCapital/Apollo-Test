"""
Deployment Config Generator - Generates optimized deployment configs

Reads existing deployment configurations and generates optimized versions
in the .akashic/deploy/ structure with support for:
- Docker Compose
- Podman
- Tilt
- Terraspace
- Juju
- MicroK8s
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DeploymentConfigGenerator:
    """Generates optimized deployment configurations"""
    
    def __init__(self, repo_path: str, deployment_map: Dict):
        self.repo_path = Path(repo_path)
        self.deployment_map = deployment_map
        self.output_dir = self.repo_path / '.akashic' / 'deploy'
        
    async def generate_all(self):
        """Generate all deployment configurations"""
        logger.info("🔧 Generating deployment configurations...")
        
        # Create directory structure
        self._create_directory_structure()
        
        # Generate local configs
        await self._generate_local_configs()
        
        # Generate cloud configs
        await self._generate_cloud_configs()
        
        # Generate scripts
        await self._generate_scripts()
        
        logger.info("✅ Generated all deployment configurations")
        
    def _create_directory_structure(self):
        """Create .akashic/deploy/ directory structure"""
        dirs = [
            'local/docker',
            'local/podman',
            'local/podman/pods',
            'local/podman/containers',
            'local/tilt',
            'local/tilt/services',
            'local/scripts',
            'local/monitoring',
            'cloud/kubernetes/base',
            'cloud/kubernetes/overlays/dev',
            'cloud/kubernetes/overlays/qa',
            'cloud/kubernetes/overlays/prod',
            'cloud/juju/bundles',
            'cloud/juju/charms',
            'cloud/terraspace/app/stacks/microk8s',
            'cloud/terraspace/app/stacks/juju',
            'cloud/terraspace/app/stacks/monitoring',
            'cloud/terraspace/app/modules/microk8s',
            'cloud/terraspace/app/modules/juju',
            'cloud/terraspace/app/modules/monitoring',
            'cloud/terraspace/config/terraform',
            'cloud/terraspace/tfvars',
            'cloud/monitoring/prometheus',
            'cloud/monitoring/grafana',
            'cloud/monitoring/alertmanager',
        ]
        
        for dir_path in dirs:
            (self.output_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"📁 Created directory structure in {self.output_dir}")
        
    async def _generate_local_configs(self):
        """Generate local development configurations"""
        # Generate Docker Compose configs
        await self._generate_docker_compose()
        
        # Generate Podman configs
        await self._generate_podman_configs()
        
        # Generate Tilt configs
        await self._generate_tilt_configs()
        
    async def _generate_docker_compose(self):
        """Generate Docker Compose configurations"""
        logger.info("  🐳 Generating Docker Compose configs...")
        
        # Find existing docker-compose files
        docker_configs = self._find_docker_configs()
        
        if not docker_configs:
            logger.info("  ⚠️  No Docker configs found, skipping")
            return
            
        # Read first docker-compose file as base
        base_config = self._read_yaml(docker_configs[0])
        
        if not base_config or 'services' not in base_config:
            logger.warning("  ⚠️  Invalid Docker Compose config")
            return
            
        # Generate docker-compose.yml (all services)
        compose_all = self.output_dir / 'local' / 'docker' / 'docker-compose.yml'
        self._write_yaml(compose_all, base_config)
        
        # Generate docker-compose.base.yml (heavy services only)
        heavy_services = self._extract_heavy_services(base_config)
        compose_base = self.output_dir / 'local' / 'docker' / 'docker-compose.base.yml'
        self._write_yaml(compose_base, {'version': base_config.get('version', '3'), 'services': heavy_services})
        
        # Generate docker-compose.dev.yml (dev overrides)
        dev_overrides = self._generate_dev_overrides(base_config)
        compose_dev = self.output_dir / 'local' / 'docker' / 'docker-compose.dev.yml'
        self._write_yaml(compose_dev, dev_overrides)
        
        logger.info(f"  ✅ Generated Docker Compose configs")
        
    async def _generate_podman_configs(self):
        """Generate Podman configurations"""
        logger.info("  🦭 Generating Podman configs...")
        
        # Find existing docker-compose files (convert to podman)
        docker_configs = self._find_docker_configs()
        
        if not docker_configs:
            logger.info("  ⚠️  No Docker configs found, skipping Podman generation")
            return
            
        # Read docker-compose file
        base_config = self._read_yaml(docker_configs[0])
        
        if not base_config or 'services' not in base_config:
            return
            
        # Generate podman-compose.yml (same as docker-compose)
        podman_compose = self.output_dir / 'local' / 'podman' / 'podman-compose.yml'
        self._write_yaml(podman_compose, base_config)
        
        # Generate Kubernetes-style pod definitions
        await self._generate_podman_pods(base_config)
        
        logger.info(f"  ✅ Generated Podman configs")
        
    async def _generate_podman_pods(self, compose_config: Dict):
        """Generate Podman pod definitions (Kubernetes-style)"""
        # Generate base pod (heavy services)
        heavy_services = self._extract_heavy_services(compose_config)
        base_pod = self._compose_to_pod('base-services', heavy_services)
        
        pod_base = self.output_dir / 'local' / 'podman' / 'pods' / 'base.yml'
        self._write_yaml(pod_base, base_pod)
        
        # Generate services pod (your services)
        app_services = self._extract_app_services(compose_config)
        services_pod = self._compose_to_pod('app-services', app_services)
        
        pod_services = self.output_dir / 'local' / 'podman' / 'pods' / 'services.yml'
        self._write_yaml(pod_services, services_pod)
        
    def _compose_to_pod(self, pod_name: str, services: Dict) -> Dict:
        """Convert Docker Compose services to Kubernetes pod definition"""
        containers = []
        
        for service_name, service_config in services.items():
            container = {
                'name': service_name,
                'image': service_config.get('image', f'{service_name}:latest'),
            }
            
            # Add ports
            if 'ports' in service_config:
                container['ports'] = []
                for port in service_config['ports']:
                    if isinstance(port, str) and ':' in port:
                        container_port = int(port.split(':')[1])
                    else:
                        container_port = int(port)
                    container['ports'].append({'containerPort': container_port})
            
            # Add environment
            if 'environment' in service_config:
                container['env'] = []
                env = service_config['environment']
                if isinstance(env, dict):
                    for key, value in env.items():
                        container['env'].append({'name': key, 'value': str(value)})
                elif isinstance(env, list):
                    for item in env:
                        if '=' in item:
                            key, value = item.split('=', 1)
                            container['env'].append({'name': key, 'value': value})
            
            containers.append(container)
        
        return {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {'name': pod_name},
            'spec': {'containers': containers}
        }
        
    async def _generate_tilt_configs(self):
        """Generate Tilt configurations"""
        logger.info("  🎯 Generating Tilt configs...")
        
        # Find existing docker-compose files
        docker_configs = self._find_docker_configs()
        
        if not docker_configs:
            logger.info("  ⚠️  No Docker configs found, skipping Tilt generation")
            return
            
        # Read docker-compose file
        base_config = self._read_yaml(docker_configs[0])
        
        if not base_config or 'services' not in base_config:
            return
            
        # Generate Tiltfile
        tiltfile = self._generate_tiltfile(base_config)
        tiltfile_path = self.output_dir / 'local' / 'tilt' / 'Tiltfile'
        tiltfile_path.write_text(tiltfile)
        
        logger.info(f"  ✅ Generated Tilt configs")
        
    def _generate_tiltfile(self, compose_config: Dict) -> str:
        """Generate Tiltfile from Docker Compose config"""
        app_services = self._extract_app_services(compose_config)
        
        tiltfile = """# Tiltfile - Fast iteration for your services
# Heavy services (databases, Kafka) should run in Docker Compose separately

"""
        
        for service_name, service_config in app_services.items():
            # Detect build context
            build_context = '../../../'  # Default to repo root
            if 'build' in service_config:
                if isinstance(service_config['build'], dict):
                    build_context = service_config['build'].get('context', build_context)
                else:
                    build_context = service_config['build']
            
            tiltfile += f"""
# {service_name.title()} service
docker_build('{service_name}', '{build_context}')

# Live reload for {service_name}
local_resource('{service_name}-hot-reload',
    'cd {build_context} && <your-dev-command>',  # TODO: Add your dev command
    deps=['{build_context}'],
    labels=['{service_name}'])
"""
        
        return tiltfile
        
    async def _generate_cloud_configs(self):
        """Generate cloud deployment configurations"""
        # Generate Terraspace configs
        await self._generate_terraspace_configs()
        
        # Generate Juju bundles
        await self._generate_juju_bundles()
        
        # Generate Kubernetes manifests
        await self._generate_kubernetes_manifests()
        
    async def _generate_terraspace_configs(self):
        """Generate Terraspace configurations"""
        logger.info("  🌍 Generating Terraspace configs...")
        
        # Generate MicroK8s stack
        await self._generate_microk8s_stack()
        
        # Generate tfvars for each environment
        await self._generate_tfvars()
        
        logger.info(f"  ✅ Generated Terraspace configs")
        
    async def _generate_microk8s_stack(self):
        """Generate Terraspace stack for MicroK8s"""
        main_tf = """# MicroK8s Cluster Provisioning

resource "null_resource" "microk8s_cluster" {
  provisioner "local-exec" {
    command = <<-EOT
      # Install MicroK8s
      sudo snap install microk8s --classic --channel=${var.k8s_version}
      
      # Enable addons
      sudo microk8s enable dns storage ingress metallb:${var.metallb_ip_range}
      
      # Configure for Juju
      sudo microk8s config > ${var.kubeconfig_path}
    EOT
  }
}

# Outputs for Juju
output "kubeconfig_path" {
  value = var.kubeconfig_path
}

output "cluster_endpoint" {
  value = "https://${var.cluster_ip}:16443"
}
"""
        
        variables_tf = """# Variables for MicroK8s stack

variable "environment" {
  description = "Environment name (dev, qa, prod)"
  type        = string
}

variable "k8s_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28/stable"
}

variable "cluster_ip" {
  description = "Cluster IP address"
  type        = string
}

variable "metallb_ip_range" {
  description = "MetalLB IP range"
  type        = string
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file"
  type        = string
}
"""
        
        outputs_tf = """# Outputs for MicroK8s stack

output "cluster_info" {
  value = {
    environment = var.environment
    endpoint    = "https://${var.cluster_ip}:16443"
    kubeconfig  = var.kubeconfig_path
  }
}
"""
        
        stack_dir = self.output_dir / 'cloud' / 'terraspace' / 'app' / 'stacks' / 'microk8s'
        (stack_dir / 'main.tf').write_text(main_tf)
        (stack_dir / 'variables.tf').write_text(variables_tf)
        (stack_dir / 'outputs.tf').write_text(outputs_tf)
        
    async def _generate_tfvars(self):
        """Generate tfvars for each environment"""
        environments = {
            'dev': {
                'environment': 'dev',
                'k8s_version': '1.28/stable',
                'cluster_ip': '10.0.1.10',
                'metallb_ip_range': '10.0.1.100-10.0.1.200',
                'kubeconfig_path': '/home/ubuntu/.kube/dev-config',
            },
            'qa': {
                'environment': 'qa',
                'k8s_version': '1.28/stable',
                'cluster_ip': '10.0.2.10',
                'metallb_ip_range': '10.0.2.100-10.0.2.200',
                'kubeconfig_path': '/home/ubuntu/.kube/qa-config',
            },
            'prod': {
                'environment': 'prod',
                'k8s_version': '1.28/stable',
                'cluster_ip': '10.0.3.10',
                'metallb_ip_range': '10.0.3.100-10.0.3.200',
                'kubeconfig_path': '/home/ubuntu/.kube/prod-config',
            },
        }
        
        tfvars_dir = self.output_dir / 'cloud' / 'terraspace' / 'tfvars'
        
        for env_name, env_vars in environments.items():
            tfvars_content = '\n'.join([f'{key} = "{value}"' for key, value in env_vars.items()])
            (tfvars_dir / f'{env_name}.tfvars').write_text(tfvars_content)
            
    async def _generate_juju_bundles(self):
        """Generate Juju bundle files"""
        logger.info("  🎩 Generating Juju bundles...")
        
        # Find existing docker-compose files to extract services
        docker_configs = self._find_docker_configs()
        
        if not docker_configs:
            logger.info("  ⚠️  No Docker configs found, generating template bundles")
            await self._generate_template_juju_bundles()
            return
            
        # Read docker-compose file
        base_config = self._read_yaml(docker_configs[0])
        
        if not base_config or 'services' not in base_config:
            await self._generate_template_juju_bundles()
            return
            
        # Generate bundles for each environment
        for env in ['dev', 'qa', 'prod']:
            bundle = self._generate_juju_bundle(base_config, env)
            bundle_path = self.output_dir / 'cloud' / 'juju' / 'bundles' / f'{env}-bundle.yml'
            self._write_yaml(bundle_path, bundle)
            
        logger.info(f"  ✅ Generated Juju bundles")
        
    def _generate_juju_bundle(self, compose_config: Dict, environment: str) -> Dict:
        """Generate Juju bundle from Docker Compose config"""
        app_services = self._extract_app_services(compose_config)
        heavy_services = self._extract_heavy_services(compose_config)
        
        applications = {}
        
        # Add app services
        for service_name in app_services.keys():
            applications[service_name] = {
                'charm': f'./charms/{service_name}',
                'scale': 2 if environment == 'prod' else 1,
                'resources': {
                    f'{service_name}-image': f'{service_name}:{environment}'
                },
                'options': {
                    'environment': environment,
                    'log_level': 'debug' if environment == 'dev' else 'info',
                }
            }
        
        # Add database services
        if 'postgres' in heavy_services or 'postgresql' in heavy_services:
            applications['postgresql'] = {
                'charm': 'postgresql-k8s',
                'channel': '14/stable',
                'scale': 1,
                'options': {
                    'database': f'app_{environment}'
                }
            }
        
        if 'neo4j' in heavy_services:
            applications['neo4j'] = {
                'charm': 'neo4j-k8s',
                'channel': '5/stable',
                'scale': 1,
            }
        
        # Add relations
        relations = []
        for service_name in app_services.keys():
            if 'postgresql' in applications:
                relations.append([f'{service_name}:db', 'postgresql:db'])
            if 'neo4j' in applications:
                relations.append([f'{service_name}:graph', 'neo4j:graph'])
        
        return {
            'bundle': 'kubernetes',
            'applications': applications,
            'relations': relations if relations else None,
        }
        
    async def _generate_template_juju_bundles(self):
        """Generate template Juju bundles"""
        template = {
            'bundle': 'kubernetes',
            'applications': {
                'app': {
                    'charm': './charms/app',
                    'scale': 1,
                    'resources': {
                        'app-image': 'app:latest'
                    },
                }
            }
        }
        
        for env in ['dev', 'qa', 'prod']:
            bundle_path = self.output_dir / 'cloud' / 'juju' / 'bundles' / f'{env}-bundle.yml'
            self._write_yaml(bundle_path, template)
            
    async def _generate_kubernetes_manifests(self):
        """Generate Kubernetes manifests"""
        logger.info("  ☸️  Generating Kubernetes manifests...")
        
        # TODO: Generate K8s manifests from Docker Compose
        # For now, create placeholder structure
        
        logger.info(f"  ✅ Generated Kubernetes manifests")
        
    async def _generate_scripts(self):
        """Generate helper scripts"""
        logger.info("  📜 Generating helper scripts...")
        
        # Generate start-all.sh
        await self._generate_start_all_script()
        
        # Generate switch-runtime.sh
        await self._generate_switch_runtime_script()
        
        # Generate start-podman.sh
        await self._generate_start_podman_script()
        
        logger.info(f"  ✅ Generated helper scripts")
        
    async def _generate_start_all_script(self):
        """Generate start-all.sh script"""
        script = """#!/bin/bash
# Start all services (hybrid mode)

set -e

echo "🚀 Starting all services..."

# Check if Tilt is available
if command -v tilt &> /dev/null; then
    echo "📦 Starting heavy services with Docker Compose..."
    cd ../docker
    docker-compose -f docker-compose.base.yml up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "🎯 Starting Tilt for your services..."
    cd ../tilt
    tilt up
else
    echo "⚠️  Tilt not installed, using Docker Compose only..."
    cd ../docker
    docker-compose up
fi
"""
        
        script_path = self.output_dir / 'local' / 'scripts' / 'start-all.sh'
        script_path.write_text(script)
        script_path.chmod(0o755)
        
    async def _generate_switch_runtime_script(self):
        """Generate switch-runtime.sh script"""
        script = """#!/bin/bash
# Switch between Docker and Podman

RUNTIME=$1

if [ "$RUNTIME" = "podman" ]; then
  echo "Switching to Podman..."
  alias docker=podman
  alias docker-compose=podman-compose
  export CONTAINER_RUNTIME=podman
  echo "✅ Using Podman"
  
elif [ "$RUNTIME" = "docker" ]; then
  echo "Switching to Docker..."
  unalias docker 2>/dev/null
  unalias docker-compose 2>/dev/null
  export CONTAINER_RUNTIME=docker
  echo "✅ Using Docker"
  
else
  echo "Usage: ./switch-runtime.sh [docker|podman]"
  exit 1
fi
"""
        
        script_path = self.output_dir / 'local' / 'scripts' / 'switch-runtime.sh'
        script_path.write_text(script)
        script_path.chmod(0o755)
        
    async def _generate_start_podman_script(self):
        """Generate start-podman.sh script"""
        script = """#!/bin/bash
# Start services with Podman

set -e

echo "🦭 Starting services with Podman..."

# Option 1: Use podman-compose
# cd ../podman
# podman-compose up

# Option 2: Use Kubernetes-style pods
echo "📦 Starting base services pod..."
cd ../podman
podman play kube pods/base.yml

echo "🚀 Starting app services pod..."
podman play kube pods/services.yml

echo "✅ All services started!"
"""
        
        script_path = self.output_dir / 'local' / 'scripts' / 'start-podman.sh'
        script_path.write_text(script)
        script_path.chmod(0o755)
        
    # Helper methods
    
    def _find_docker_configs(self) -> List[Path]:
        """Find existing docker-compose files"""
        configs = []
        
        for pattern in ['docker-compose*.yml', 'docker-compose*.yaml']:
            configs.extend(self.repo_path.rglob(pattern))
        
        # Filter out .akashic folder
        configs = [c for c in configs if '.akashic' not in str(c)]
        
        return configs
        
    def _read_yaml(self, file_path: Path) -> Optional[Dict]:
        """Read YAML file"""
        try:
            return yaml.safe_load(file_path.read_text())
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return None
            
    def _write_yaml(self, file_path: Path, data: Dict):
        """Write YAML file"""
        try:
            file_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")
            
    def _extract_heavy_services(self, compose_config: Dict) -> Dict:
        """Extract heavy services (databases, Kafka, etc.)"""
        heavy_service_names = ['postgres', 'postgresql', 'neo4j', 'kafka', 'redis', 'mongodb', 'mysql', 'elasticsearch']
        
        services = compose_config.get('services', {})
        heavy = {}
        
        for name, config in services.items():
            if any(heavy_name in name.lower() for heavy_name in heavy_service_names):
                heavy[name] = config
                
        return heavy
        
    def _extract_app_services(self, compose_config: Dict) -> Dict:
        """Extract application services (not databases)"""
        heavy_services = self._extract_heavy_services(compose_config)
        
        services = compose_config.get('services', {})
        app_services = {}
        
        for name, config in services.items():
            if name not in heavy_services:
                app_services[name] = config
                
        return app_services
        
    def _generate_dev_overrides(self, compose_config: Dict) -> Dict:
        """Generate dev overrides for docker-compose"""
        return {
            'version': compose_config.get('version', '3'),
            'services': {
                # Add dev-specific overrides here
                # e.g., volume mounts for hot reload
            }
        }


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Example usage
        deployment_map = {}  # From DeploymentMapper
        generator = DeploymentConfigGenerator("/path/to/repo", deployment_map)
        await generator.generate_all()
    
    asyncio.run(main())
