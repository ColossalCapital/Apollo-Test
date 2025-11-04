# 🚀 Connector Deployment Guide

## Overview

The connector deployment system supports three targets:
- **Docker** - Local development (most common)
- **Podman** - Local development (rootless alternative)
- **MicroK8s** - Production Kubernetes deployment

---

## 🎯 Deployment Targets

### **Local Development**

**Docker (Recommended for Mac/Windows):**
```bash
# Auto-detected if Docker Desktop is installed
# Deploys as container with restart policy
```

**Podman (Recommended for Linux):**
```bash
# Auto-detected if Podman is installed
# Rootless containers, more secure
```

### **Production**

**MicroK8s (Kubernetes):**
```bash
# Auto-detected if MicroK8s is installed
# Full Kubernetes deployment with:
# - Deployment (replicas, rolling updates)
# - Service (load balancing)
# - Health checks (liveness, readiness)
# - Auto-scaling (optional)
```

---

## 📦 Installation

### Install Docker (Mac/Windows)
```bash
# Download Docker Desktop
# https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
```

### Install Podman (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install podman

# Verify installation
podman --version
```

### Install MicroK8s (Production)
```bash
# Ubuntu/Debian
sudo snap install microk8s --classic

# Add user to microk8s group
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
newgrp microk8s

# Enable required addons
microk8s enable dns
microk8s enable registry
microk8s enable ingress

# Verify installation
microk8s status
```

---

## 🔧 Usage

### **Automatic Target Selection**

The deployer automatically selects the best target:

```python
from Apollo.agents.connectors.deployer import ConnectorDeployer

deployer = ConnectorDeployer()

# Development: Uses Podman > Docker > MicroK8s
result = await deployer.deploy_connector(
    integration_type="gmail",
    binary_path="/path/to/binary",
    credentials={"api_key": "xxx"},
    environment="development"  # Auto-selects Podman or Docker
)

# Production: Uses MicroK8s > Podman > Docker
result = await deployer.deploy_connector(
    integration_type="gmail",
    binary_path="/path/to/binary",
    credentials={"api_key": "xxx"},
    environment="production"  # Auto-selects MicroK8s
)
```

### **Manual Target Selection**

```python
# Force specific target
result = await deployer.deploy_connector(
    integration_type="gmail",
    binary_path="/path/to/binary",
    credentials={"api_key": "xxx"},
    target="microk8s"  # Force MicroK8s
)
```

---

## 🏗️ Deployment Flow

### **Docker/Podman Flow**

```
1. Generate Dockerfile
   ├── Base image: debian:bookworm-slim
   ├── Copy binary
   ├── Health check endpoint
   └── Expose ports (8080, 9091)

2. Build image
   └── docker/podman build -t gmail-connector:latest

3. Create container
   ├── Environment variables (API keys, Kafka config)
   ├── Port mapping (8080:8080, 9091:9091)
   ├── Restart policy (unless-stopped)
   └── Health check (every 10s)

4. Start container
   └── docker/podman run -d gmail-connector

5. Health check
   └── Wait for /health endpoint (30s timeout)

6. Complete
   └── Return container ID and endpoint
```

### **MicroK8s Flow**

```
1. Build image
   └── docker build -t localhost:32000/gmail-connector:latest

2. Push to MicroK8s registry
   └── docker push localhost:32000/gmail-connector:latest

3. Generate Kubernetes manifests
   ├── Deployment
   │   ├── Replicas: 1 (configurable)
   │   ├── Container spec
   │   ├── Environment variables
   │   ├── Liveness probe (/health)
   │   └── Readiness probe (/health)
   └── Service
       ├── ClusterIP (internal)
       └── Ports (8080, 9091)

4. Apply manifests
   └── microk8s kubectl apply -f manifests.yaml

5. Wait for rollout
   └── microk8s kubectl rollout status deployment/gmail-connector

6. Complete
   └── Return deployment name and service endpoint
```

---

## 📊 Deployment Result

```python
@dataclass
class DeploymentResult:
    success: bool
    deployment_id: str       # Container ID or K8s deployment name
    target: DeploymentTarget # "docker", "podman", or "microk8s"
    health_status: str       # "healthy" or "unhealthy"
    endpoint: Optional[str]  # http://localhost:8080 or http://10.1.1.5:8080
    error: Optional[str]     # Error message if failed
```

**Example:**
```python
if result.success:
    print(f"✅ Deployed to {result.target}")
    print(f"ID: {result.deployment_id}")
    print(f"Health: {result.health_status}")
    print(f"Endpoint: {result.endpoint}")
else:
    print(f"❌ Deployment failed: {result.error}")
```

---

## 🔍 Monitoring

### **Docker/Podman**

```bash
# View logs
docker logs -f gmail-connector
podman logs -f gmail-connector

# Check health
curl http://localhost:8080/health

# View metrics
curl http://localhost:9091/metrics

# Inspect container
docker inspect gmail-connector
podman inspect gmail-connector

# Stop container
docker stop gmail-connector
podman stop gmail-connector
```

### **MicroK8s**

```bash
# View pods
microk8s kubectl get pods

# View logs
microk8s kubectl logs -f deployment/gmail-connector

# Check health
microk8s kubectl get pods -l app=gmail-connector

# View metrics
microk8s kubectl port-forward svc/gmail-connector 9091:9091
curl http://localhost:9091/metrics

# Scale deployment
microk8s kubectl scale deployment/gmail-connector --replicas=3

# Delete deployment
microk8s kubectl delete deployment gmail-connector
microk8s kubectl delete service gmail-connector
```

---

## 🔐 Environment Variables

All connectors receive these environment variables:

```bash
# Integration-specific
{INTEGRATION}_API_KEY=xxx
{INTEGRATION}_OAUTH_TOKEN=xxx  # If OAuth

# Kafka configuration
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC={integration}_raw

# Logging
LOG_LEVEL=info
```

**Example for Gmail:**
```bash
GMAIL_API_KEY=sk_test_xxx
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=gmail_raw
LOG_LEVEL=info
```

---

## 🎛️ Configuration

### **Dockerfile Template**

```dockerfile
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy binary
COPY target/release/{integration}-connector /usr/local/bin/connector

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 8080 9091

# Run connector
CMD ["/usr/local/bin/connector"]
```

### **Kubernetes Deployment**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gmail-connector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gmail-connector
  template:
    metadata:
      labels:
        app: gmail-connector
    spec:
      containers:
      - name: connector
        image: localhost:32000/gmail-connector:latest
        ports:
        - containerPort: 8080
          name: health
        - containerPort: 9091
          name: metrics
        env:
        - name: GMAIL_API_KEY
          value: "xxx"
        - name: KAFKA_BROKERS
          value: "kafka:9092"
        - name: KAFKA_TOPIC
          value: "gmail_raw"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: gmail-connector
spec:
  selector:
    app: gmail-connector
  ports:
  - name: health
    port: 8080
    targetPort: 8080
  - name: metrics
    port: 9091
    targetPort: 9091
```

---

## 🚨 Troubleshooting

### **Container won't start**

```bash
# Check logs
docker logs gmail-connector

# Common issues:
# - Missing environment variables
# - Binary not executable
# - Port already in use
```

### **Health check failing**

```bash
# Check if service is running
curl http://localhost:8080/health

# Common issues:
# - Service not listening on 0.0.0.0
# - Health endpoint not implemented
# - Firewall blocking port
```

### **MicroK8s deployment stuck**

```bash
# Check pod status
microk8s kubectl describe pod gmail-connector-xxx

# Common issues:
# - Image pull failed (check registry)
# - Resource limits exceeded
# - ConfigMap/Secret missing
```

---

## 📈 Production Best Practices

### **MicroK8s Production Setup**

```bash
# 1. Enable monitoring
microk8s enable prometheus
microk8s enable grafana

# 2. Enable auto-scaling
microk8s enable metrics-server

# 3. Configure HPA (Horizontal Pod Autoscaler)
kubectl autoscale deployment gmail-connector \
  --cpu-percent=80 \
  --min=2 \
  --max=10

# 4. Set resource limits
kubectl set resources deployment gmail-connector \
  --limits=cpu=500m,memory=512Mi \
  --requests=cpu=100m,memory=128Mi

# 5. Enable ingress for external access
microk8s enable ingress
```

### **High Availability**

```yaml
# Multi-replica deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

---

## ✅ Summary

**Local Development:**
- Use Docker or Podman
- Single container per connector
- Easy debugging with logs
- Quick iteration

**Production:**
- Use MicroK8s (Kubernetes)
- Multiple replicas for HA
- Auto-scaling based on load
- Health checks and rolling updates
- Prometheus metrics
- Grafana dashboards

**The deployment system automatically selects the best target based on environment!** 🚀
