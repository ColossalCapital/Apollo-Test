"""
Connector Deployment System

Flexible deployment supporting:
- Local: Docker or Podman
- Production: MicroK8s (Kubernetes)
"""

import asyncio
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Optional, Callable, Literal
from dataclasses import dataclass
from datetime import datetime
import os


DeploymentTarget = Literal["docker", "podman", "microk8s"]


@dataclass
class DeploymentResult:
    """Result of deployment"""
    success: bool
    deployment_id: str  # Container ID or K8s deployment name
    target: DeploymentTarget
    health_status: str = "unknown"
    endpoint: Optional[str] = None
    error: Optional[str] = None


@dataclass
class DeploymentProgress:
    """Progress event during deployment"""
    stage: str  # "building", "deploying", "health_check", "complete"
    message: str
    progress_percent: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        return {
            "stage": self.stage,
            "message": self.message,
            "progress_percent": self.progress_percent,
            "timestamp": self.timestamp.isoformat(),
        }


class ConnectorDeployer:
    """Deploys connectors to Docker, Podman, or MicroK8s"""
    
    def __init__(
        self,
        base_path: str = "/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/AckwardRootsInc",
        progress_callback: Optional[Callable] = None
    ):
        self.base_path = base_path
        self.progress_callback = progress_callback
        
        # Auto-detect available deployment targets
        self.available_targets = self.detect_available_targets()
    
    def detect_available_targets(self) -> list[DeploymentTarget]:
        """Detect which deployment targets are available"""
        targets = []
        
        # Check for Docker
        if self.command_exists("docker"):
            targets.append("docker")
        
        # Check for Podman
        if self.command_exists("podman"):
            targets.append("podman")
        
        # Check for MicroK8s
        if self.command_exists("microk8s"):
            targets.append("microk8s")
        
        return targets
    
    def command_exists(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            subprocess.run(
                ["which", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except:
            return False
    
    async def emit_progress(self, progress: DeploymentProgress):
        """Emit progress event"""
        if self.progress_callback:
            await self.progress_callback(progress)
        
        print(f"[{progress.timestamp.strftime('%H:%M:%S')}] {progress.stage}: {progress.message}")
    
    async def deploy_connector(
        self,
        integration_type: str,
        binary_path: str,
        credentials: Dict,
        target: Optional[DeploymentTarget] = None,
        environment: str = "development"
    ) -> DeploymentResult:
        """
        Deploy a connector
        
        Args:
            integration_type: Name of integration (e.g., "gmail")
            binary_path: Path to compiled binary
            credentials: Integration credentials
            target: Deployment target (auto-detect if None)
            environment: "development" or "production"
            
        Returns:
            DeploymentResult with deployment details
        """
        # Auto-select target if not specified
        if target is None:
            target = self.select_default_target(environment)
        
        if target not in self.available_targets:
            return DeploymentResult(
                success=False,
                deployment_id="",
                target=target,
                error=f"{target} not available on this system"
            )
        
        # Route to appropriate deployment method
        if target in ["docker", "podman"]:
            return await self.deploy_container(
                integration_type,
                binary_path,
                credentials,
                target
            )
        elif target == "microk8s":
            return await self.deploy_kubernetes(
                integration_type,
                binary_path,
                credentials
            )
    
    def select_default_target(self, environment: str) -> DeploymentTarget:
        """Select default deployment target based on environment"""
        if environment == "production":
            # Production: prefer MicroK8s
            if "microk8s" in self.available_targets:
                return "microk8s"
        
        # Development: prefer Podman, fallback to Docker
        if "podman" in self.available_targets:
            return "podman"
        elif "docker" in self.available_targets:
            return "docker"
        elif "microk8s" in self.available_targets:
            return "microk8s"
        
        raise RuntimeError("No deployment targets available")
    
    async def deploy_container(
        self,
        integration_type: str,
        binary_path: str,
        credentials: Dict,
        target: Literal["docker", "podman"]
    ) -> DeploymentResult:
        """Deploy using Docker or Podman"""
        
        # Stage 1: Build container image (40%)
        await self.emit_progress(DeploymentProgress(
            stage="building",
            message=f"Building {target} image...",
            progress_percent=10
        ))
        
        image_name = f"{integration_type}-connector:latest"
        dockerfile_path = await self.generate_dockerfile(integration_type, binary_path)
        
        build_result = await self.run_command([
            target, "build",
            "-t", image_name,
            "-f", dockerfile_path,
            str(Path(binary_path).parent.parent)
        ])
        
        if build_result.returncode != 0:
            return DeploymentResult(
                success=False,
                deployment_id="",
                target=target,
                error=f"Image build failed: {build_result.stderr}"
            )
        
        await self.emit_progress(DeploymentProgress(
            stage="building",
            message="✅ Image built successfully",
            progress_percent=40
        ))
        
        # Stage 2: Create and start container (30%)
        await self.emit_progress(DeploymentProgress(
            stage="deploying",
            message="Starting container...",
            progress_percent=50
        ))
        
        container_name = f"{integration_type}-connector"
        env_vars = self.prepare_env_vars(integration_type, credentials)
        
        # Stop existing container if running
        await self.run_command([target, "stop", container_name], check=False)
        await self.run_command([target, "rm", container_name], check=False)
        
        # Create and start new container
        run_args = [
            target, "run",
            "-d",
            "--name", container_name,
            "--restart", "unless-stopped",
            "-p", "8080:8080",  # Health check
            "-p", "9091:9091",  # Metrics
        ]
        
        # Add environment variables
        for key, value in env_vars.items():
            run_args.extend(["-e", f"{key}={value}"])
        
        run_args.append(image_name)
        
        run_result = await self.run_command(run_args)
        
        if run_result.returncode != 0:
            return DeploymentResult(
                success=False,
                deployment_id="",
                target=target,
                error=f"Container start failed: {run_result.stderr}"
            )
        
        container_id = run_result.stdout.strip()
        
        await self.emit_progress(DeploymentProgress(
            stage="deploying",
            message=f"✅ Container started: {container_id[:12]}",
            progress_percent=70
        ))
        
        # Stage 3: Health check (30%)
        await self.emit_progress(DeploymentProgress(
            stage="health_check",
            message="Waiting for health check...",
            progress_percent=80
        ))
        
        health_status = await self.wait_for_healthy(
            container_id,
            target,
            timeout=30
        )
        
        await self.emit_progress(DeploymentProgress(
            stage="complete",
            message=f"✅ Deployment complete - {health_status}",
            progress_percent=100
        ))
        
        return DeploymentResult(
            success=True,
            deployment_id=container_id,
            target=target,
            health_status=health_status,
            endpoint="http://localhost:8080"
        )
    
    async def deploy_kubernetes(
        self,
        integration_type: str,
        binary_path: str,
        credentials: Dict
    ) -> DeploymentResult:
        """Deploy to MicroK8s (Kubernetes)"""
        
        # Stage 1: Build and push image to MicroK8s registry (30%)
        await self.emit_progress(DeploymentProgress(
            stage="building",
            message="Building image for MicroK8s...",
            progress_percent=10
        ))
        
        image_name = f"localhost:32000/{integration_type}-connector:latest"
        dockerfile_path = await self.generate_dockerfile(integration_type, binary_path)
        
        # Build with Docker (MicroK8s uses Docker)
        build_result = await self.run_command([
            "docker", "build",
            "-t", image_name,
            "-f", dockerfile_path,
            str(Path(binary_path).parent.parent)
        ])
        
        if build_result.returncode != 0:
            return DeploymentResult(
                success=False,
                deployment_id="",
                target="microk8s",
                error=f"Image build failed: {build_result.stderr}"
            )
        
        # Push to MicroK8s registry
        push_result = await self.run_command(["docker", "push", image_name])
        
        if push_result.returncode != 0:
            return DeploymentResult(
                success=False,
                deployment_id="",
                target="microk8s",
                error=f"Image push failed: {push_result.stderr}"
            )
        
        await self.emit_progress(DeploymentProgress(
            stage="building",
            message="✅ Image pushed to registry",
            progress_percent=40
        ))
        
        # Stage 2: Generate and apply Kubernetes manifests (40%)
        await self.emit_progress(DeploymentProgress(
            stage="deploying",
            message="Applying Kubernetes manifests...",
            progress_percent=50
        ))
        
        manifests = self.generate_k8s_manifests(
            integration_type,
            image_name,
            credentials
        )
        
        manifest_path = f"/tmp/{integration_type}-k8s.yaml"
        with open(manifest_path, 'w') as f:
            yaml.dump_all(manifests, f)
        
        apply_result = await self.run_command([
            "microk8s", "kubectl", "apply", "-f", manifest_path
        ])
        
        if apply_result.returncode != 0:
            return DeploymentResult(
                success=False,
                deployment_id="",
                target="microk8s",
                error=f"Kubernetes apply failed: {apply_result.stderr}"
            )
        
        deployment_name = f"{integration_type}-connector"
        
        await self.emit_progress(DeploymentProgress(
            stage="deploying",
            message=f"✅ Deployment created: {deployment_name}",
            progress_percent=70
        ))
        
        # Stage 3: Wait for rollout (30%)
        await self.emit_progress(DeploymentProgress(
            stage="health_check",
            message="Waiting for rollout...",
            progress_percent=80
        ))
        
        rollout_result = await self.run_command([
            "microk8s", "kubectl", "rollout", "status",
            f"deployment/{deployment_name}",
            "--timeout=60s"
        ])
        
        health_status = "healthy" if rollout_result.returncode == 0 else "unhealthy"
        
        await self.emit_progress(DeploymentProgress(
            stage="complete",
            message=f"✅ Deployment complete - {health_status}",
            progress_percent=100
        ))
        
        # Get service endpoint
        svc_result = await self.run_command([
            "microk8s", "kubectl", "get", "svc",
            f"{integration_type}-connector",
            "-o", "jsonpath={.spec.clusterIP}"
        ])
        
        endpoint = f"http://{svc_result.stdout.strip()}:8080" if svc_result.returncode == 0 else None
        
        return DeploymentResult(
            success=True,
            deployment_id=deployment_name,
            target="microk8s",
            health_status=health_status,
            endpoint=endpoint
        )
    
    async def generate_dockerfile(self, integration_type: str, binary_path: str) -> str:
        """Generate Dockerfile for connector"""
        dockerfile_content = f"""FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    ca-certificates \\
    libssl3 \\
    && rm -rf /var/lib/apt/lists/*

# Copy binary
COPY target/release/{integration_type}-connector /usr/local/bin/connector

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 8080 9091

# Run connector
CMD ["/usr/local/bin/connector"]
"""
        
        dockerfile_path = f"{Path(binary_path).parent.parent}/Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        return dockerfile_path
    
    def prepare_env_vars(self, integration_type: str, credentials: Dict) -> Dict[str, str]:
        """Prepare environment variables for connector"""
        env_vars = {
            f"{integration_type.upper()}_API_KEY": credentials.get("api_key", ""),
            "KAFKA_BROKERS": os.getenv("KAFKA_BROKERS", "localhost:9092"),
            "KAFKA_TOPIC": f"{integration_type}_raw",
            "LOG_LEVEL": "info",
        }
        
        # Add OAuth credentials if present
        if "oauth_token" in credentials:
            env_vars[f"{integration_type.upper()}_OAUTH_TOKEN"] = credentials["oauth_token"]
        
        return env_vars
    
    def generate_k8s_manifests(
        self,
        integration_type: str,
        image_name: str,
        credentials: Dict
    ) -> list:
        """Generate Kubernetes manifests"""
        name = f"{integration_type}-connector"
        env_vars = self.prepare_env_vars(integration_type, credentials)
        
        # Deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": name},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {"labels": {"app": name}},
                    "spec": {
                        "containers": [{
                            "name": "connector",
                            "image": image_name,
                            "ports": [
                                {"containerPort": 8080, "name": "health"},
                                {"containerPort": 9091, "name": "metrics"}
                            ],
                            "env": [
                                {"name": k, "value": v}
                                for k, v in env_vars.items()
                            ],
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 10,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/health", "port": 8080},
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        # Service
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": name},
            "spec": {
                "selector": {"app": name},
                "ports": [
                    {"name": "health", "port": 8080, "targetPort": 8080},
                    {"name": "metrics", "port": 9091, "targetPort": 9091}
                ]
            }
        }
        
        return [deployment, service]
    
    async def wait_for_healthy(
        self,
        container_id: str,
        target: Literal["docker", "podman"],
        timeout: int = 30
    ) -> str:
        """Wait for container to be healthy"""
        for _ in range(timeout):
            inspect_result = await self.run_command([
                target, "inspect",
                "--format", "{{.State.Health.Status}}",
                container_id
            ], check=False)
            
            if inspect_result.returncode == 0:
                status = inspect_result.stdout.strip()
                if status == "healthy":
                    return "healthy"
            
            await asyncio.sleep(1)
        
        return "unhealthy"
    
    async def run_command(
        self,
        command: list,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        result = subprocess.CompletedProcess(
            args=command,
            returncode=process.returncode,
            stdout=stdout.decode('utf-8'),
            stderr=stderr.decode('utf-8')
        )
        
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(command)}\n{result.stderr}")
        
        return result


# Example usage
async def main():
    async def on_progress(progress: DeploymentProgress):
        print(f"Progress: {progress.to_dict()}")
    
    deployer = ConnectorDeployer(progress_callback=on_progress)
    
    print(f"Available targets: {deployer.available_targets}")
    
    # Deploy connector
    result = await deployer.deploy_connector(
        integration_type="gmail",
        binary_path="/path/to/binary",
        credentials={"api_key": "test_key"},
        target="podman",  # or "docker" or "microk8s"
        environment="development"
    )
    
    if result.success:
        print(f"\n✅ Deployment successful!")
        print(f"Target: {result.target}")
        print(f"ID: {result.deployment_id}")
        print(f"Health: {result.health_status}")
        print(f"Endpoint: {result.endpoint}")
    else:
        print(f"\n❌ Deployment failed!")
        print(f"Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
