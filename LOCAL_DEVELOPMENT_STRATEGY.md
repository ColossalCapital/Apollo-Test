# 🚀 Local Development Strategy

## 🎯 Vision: Fast Local Dev → Seamless Cloud Deploy

**Local Development:**
- MicroK8s (local single-node cluster)
- Juju Charms (same as cloud!)
- Skaffold (hot reload)
- Tilt (automated workflows)
- No git commits needed

**Cloud Deployment:**
- 4 Git platforms
- MicroK8s (multi-node cluster)
- Juju Charms
- CI/CD pipelines

---

## 🏗️ Architecture Comparison

### **Cloud (Production):**
```
Git Commit → 4 Platforms → Redis Coordinator → Juju → MicroK8s Cloud
```

### **Local (Development):**
```
Code Change → Skaffold/Tilt → Juju → MicroK8s Local
```

**Same deployment mechanism (Juju), different triggers!**

---

## 📋 Local Development Stack

### **Layer 1: MicroK8s (Local)**
- Single-node Kubernetes
- Runs on your laptop/workstation
- Same as cloud, just smaller

### **Layer 2: Juju (Local)**
- Same charms as cloud
- Deploy to local MicroK8s
- Test charms before cloud

### **Layer 3: Skaffold (Hot Reload)**
- Watches file changes
- Auto-rebuilds containers
- Auto-deploys to MicroK8s
- Hot reload for fast iteration

### **Layer 4: Tilt (Workflow Automation)**
- Orchestrates entire dev workflow
- Manages multiple services
- Live updates
- Beautiful UI

---

## 🚀 Local Setup

### **1. Install MicroK8s (Local):**

```bash
# Install MicroK8s
sudo snap install microk8s --classic --channel=1.28/stable

# Add user to group
sudo usermod -a -G microk8s $USER
newgrp microk8s

# Wait for ready
microk8s status --wait-ready

# Enable essential addons
microk8s enable dns
microk8s enable storage
microk8s enable ingress
microk8s enable registry  # Local container registry!
microk8s enable juju      # Native Juju support!

# Create dev namespace
microk8s kubectl create namespace dev
microk8s kubectl config set-context --current --namespace=dev

# Alias for convenience
echo "alias kubectl='microk8s kubectl'" >> ~/.bashrc
source ~/.bashrc
```

### **2. Install Juju (Local):**

```bash
# Install Juju
sudo snap install juju --classic

# Add MicroK8s cloud (automatic with addon!)
juju add-k8s microk8s-local

# Bootstrap (already done by addon)
juju bootstrap microk8s-local local-controller

# Add dev model
juju add-model dev microk8s-local --config namespace=dev
```

### **3. Install Skaffold:**

```bash
# Install Skaffold
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
sudo install skaffold /usr/local/bin/

# Verify
skaffold version
```

### **4. Install Tilt:**

```bash
# Install Tilt
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash

# Verify
tilt version
```

---

## 📁 Project Structure

```
ColossalCapital/
├── services/
│   ├── auth-service/
│   │   ├── Dockerfile
│   │   ├── src/
│   │   └── tests/
│   ├── trading-service/
│   │   ├── Dockerfile
│   │   ├── src/
│   │   └── tests/
│   └── analytics-service/
│       ├── Dockerfile
│       ├── src/
│       └── tests/
├── charms/
│   ├── auth-service/
│   │   ├── charmcraft.yaml
│   │   └── src/charm.py
│   ├── trading-service/
│   │   ├── charmcraft.yaml
│   │   └── src/charm.py
│   └── analytics-service/
│       ├── charmcraft.yaml
│       └── src/charm.py
├── skaffold.yaml          # Skaffold config
├── Tiltfile               # Tilt config
├── docker-compose.yml     # Local dependencies (Redis, PostgreSQL)
└── scripts/
    ├── dev-setup.sh
    ├── deploy-local.sh
    └── sync-to-cloud.sh
```

---

## 🔧 Skaffold Configuration

### **skaffold.yaml:**

```yaml
apiVersion: skaffold/v4beta6
kind: Config
metadata:
  name: colossalcapital-dev

# Local build configuration
build:
  artifacts:
    - image: localhost:32000/auth-service
      context: services/auth-service
      docker:
        dockerfile: Dockerfile
      sync:
        manual:
          - src: "src/**/*.py"
            dest: /app/src
    
    - image: localhost:32000/trading-service
      context: services/trading-service
      docker:
        dockerfile: Dockerfile
      sync:
        manual:
          - src: "src/**/*.py"
            dest: /app/src
    
    - image: localhost:32000/analytics-service
      context: services/analytics-service
      docker:
        dockerfile: Dockerfile
      sync:
        manual:
          - src: "src/**/*.py"
            dest: /app/src
  
  # Use MicroK8s local registry
  local:
    push: true
    useBuildkit: true

# Deploy with Juju
deploy:
  kubectl: {}

# Port forwarding for local access
portForward:
  - resourceType: service
    resourceName: auth-service
    namespace: dev
    port: 8000
    localPort: 8000
  
  - resourceType: service
    resourceName: trading-service
    namespace: dev
    port: 8001
    localPort: 8001
  
  - resourceType: service
    resourceName: analytics-service
    namespace: dev
    port: 8002
    localPort: 8002

# File watching
profiles:
  - name: dev
    activation:
      - command: dev
    patches:
      - op: add
        path: /build/artifacts/0/docker/buildArgs
        value:
          DEBUG: "true"
```

---

## 🎯 Tilt Configuration

### **Tiltfile:**

```python
# Tiltfile - Orchestrates entire dev workflow

# Load extensions
load('ext://helm_remote', 'helm_remote')
load('ext://restart_process', 'docker_build_with_restart')

# Set default namespace
k8s_yaml('k8s/namespace.yaml')

# Local dependencies (PostgreSQL, Redis, Kafka)
docker_compose('docker-compose.yml')

# Auth Service
docker_build(
    'localhost:32000/auth-service',
    context='services/auth-service',
    dockerfile='services/auth-service/Dockerfile',
    live_update=[
        sync('services/auth-service/src', '/app/src'),
        run('pip install -r requirements.txt', trigger='services/auth-service/requirements.txt'),
        restart_container()
    ]
)

# Deploy with Juju
local_resource(
    'deploy-auth-service',
    cmd='juju deploy ./charms/auth-service --resource auth-service-image=localhost:32000/auth-service:latest',
    deps=['charms/auth-service'],
    labels=['juju']
)

# Trading Service
docker_build(
    'localhost:32000/trading-service',
    context='services/trading-service',
    dockerfile='services/trading-service/Dockerfile',
    live_update=[
        sync('services/trading-service/src', '/app/src'),
        run('pip install -r requirements.txt', trigger='services/trading-service/requirements.txt'),
        restart_container()
    ]
)

local_resource(
    'deploy-trading-service',
    cmd='juju deploy ./charms/trading-service --resource trading-service-image=localhost:32000/trading-service:latest',
    deps=['charms/trading-service'],
    labels=['juju']
)

# Analytics Service
docker_build(
    'localhost:32000/analytics-service',
    context='services/analytics-service',
    dockerfile='services/analytics-service/Dockerfile',
    live_update=[
        sync('services/analytics-service/src', '/app/src'),
        run('pip install -r requirements.txt', trigger='services/analytics-service/requirements.txt'),
        restart_container()
    ]
)

local_resource(
    'deploy-analytics-service',
    cmd='juju deploy ./charms/analytics-service --resource analytics-service-image=localhost:32000/analytics-service:latest',
    deps=['charms/analytics-service'],
    labels=['juju']
)

# Port forwarding
k8s_resource(
    'auth-service',
    port_forwards=['8000:8000'],
    labels=['services']
)

k8s_resource(
    'trading-service',
    port_forwards=['8001:8001'],
    labels=['services']
)

k8s_resource(
    'analytics-service',
    port_forwards=['8002:8002'],
    labels=['services']
)

# Live reload for frontend
local_resource(
    'frontend-dev',
    serve_cmd='cd frontend && npm run dev',
    deps=['frontend/src'],
    labels=['frontend']
)

# Run tests on file change
local_resource(
    'run-tests',
    cmd='pytest services/*/tests/',
    deps=['services/*/tests/', 'services/*/src/'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    labels=['tests']
)

# Juju status dashboard
local_resource(
    'juju-status',
    serve_cmd='watch -n 2 juju status --color',
    labels=['monitoring']
)

print("""
🚀 Tilt is running!

Services:
- Auth Service: http://localhost:8000
- Trading Service: http://localhost:8001
- Analytics Service: http://localhost:8002
- Frontend: http://localhost:3000

Tilt UI: http://localhost:10350

Press 'space' to open Tilt UI in browser
""")
```

---

## 🔄 Development Workflows

### **Workflow 1: Hot Reload Development (Fastest)**

```bash
# Start Tilt (watches everything)
tilt up

# Tilt UI opens at http://localhost:10350
# Edit any file → Auto-rebuild → Auto-deploy → Live reload!

# Example: Edit auth service
vim services/auth-service/src/main.py
# Save → Tilt detects → Rebuilds → Deploys → Live!

# View logs in Tilt UI
# All services, all logs, beautiful UI
```

### **Workflow 2: Skaffold Development**

```bash
# Start Skaffold dev mode
skaffold dev

# Watches files
# Rebuilds on change
# Deploys to MicroK8s
# Streams logs

# Edit file
vim services/trading-service/src/strategy.py
# Save → Auto-rebuild → Auto-deploy!

# Stop with Ctrl+C
# Auto-cleans up deployments
```

### **Workflow 3: Manual Juju Deployment**

```bash
# Build image
docker build -t localhost:32000/auth-service:latest services/auth-service/
docker push localhost:32000/auth-service:latest

# Deploy with Juju
juju deploy ./charms/auth-service \
  --resource auth-service-image=localhost:32000/auth-service:latest

# Check status
juju status

# Update
juju refresh auth-service \
  --resource auth-service-image=localhost:32000/auth-service:latest

# Scale
juju scale-application auth-service 3

# Remove
juju remove-application auth-service
```

### **Workflow 4: Docker Compose (Dependencies Only)**

```bash
# Start local dependencies
docker-compose up -d

# Services:
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
# - Kafka: localhost:9092
# - Qdrant: localhost:6333

# Stop
docker-compose down
```

---

## 🎯 Local vs Cloud Comparison

| Feature | Local Dev | Cloud Deploy |
|---------|-----------|--------------|
| **Trigger** | File change | Git commit |
| **Build** | Skaffold/Tilt | CI/CD pipeline |
| **Registry** | MicroK8s local | ghcr.io |
| **Deploy** | Juju (local) | Juju (cloud) |
| **Cluster** | MicroK8s (1 node) | MicroK8s (multi-node) |
| **Namespace** | dev | dev/qa/prod |
| **Speed** | Seconds | Minutes |
| **Testing** | Manual | Automated |
| **Monitoring** | Tilt UI | Prometheus/Grafana |

**Key Insight: Same Juju Charms, different environments!**

---

## 🚀 Quick Start Scripts

### **dev-setup.sh:**

```bash
#!/bin/bash
# scripts/dev-setup.sh

set -e

echo "🚀 Setting up local development environment"

# Install MicroK8s
echo "📦 Installing MicroK8s..."
sudo snap install microk8s --classic --channel=1.28/stable
sudo usermod -a -G microk8s $USER

# Wait for ready
microk8s status --wait-ready

# Enable addons
echo "🔌 Enabling MicroK8s addons..."
microk8s enable dns storage ingress registry juju

# Install Juju
echo "🎯 Installing Juju..."
sudo snap install juju --classic

# Bootstrap Juju
echo "🎪 Bootstrapping Juju..."
juju bootstrap microk8s-local local-controller
juju add-model dev microk8s-local --config namespace=dev

# Install Skaffold
echo "⚡ Installing Skaffold..."
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
sudo install skaffold /usr/local/bin/

# Install Tilt
echo "🎡 Installing Tilt..."
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash

# Create namespace
echo "📁 Creating dev namespace..."
microk8s kubectl create namespace dev

# Start dependencies
echo "🐳 Starting local dependencies..."
docker-compose up -d

echo "✅ Local development environment ready!"
echo ""
echo "Next steps:"
echo "  1. Run 'tilt up' for full dev environment"
echo "  2. Or run 'skaffold dev' for hot reload"
echo "  3. Or run './scripts/deploy-local.sh' for manual deploy"
echo ""
echo "Tilt UI: http://localhost:10350"
echo "Services will be at:"
echo "  - Auth: http://localhost:8000"
echo "  - Trading: http://localhost:8001"
echo "  - Analytics: http://localhost:8002"
```

### **deploy-local.sh:**

```bash
#!/bin/bash
# scripts/deploy-local.sh

set -e

SERVICE=$1

if [ -z "$SERVICE" ]; then
  echo "Usage: ./deploy-local.sh <service-name>"
  echo "Example: ./deploy-local.sh auth-service"
  exit 1
fi

echo "🚀 Deploying $SERVICE locally"

# Build image
echo "🔨 Building image..."
docker build -t localhost:32000/$SERVICE:latest services/$SERVICE/
docker push localhost:32000/$SERVICE:latest

# Deploy with Juju
echo "🎯 Deploying with Juju..."
juju deploy ./charms/$SERVICE \
  --resource ${SERVICE}-image=localhost:32000/$SERVICE:latest \
  --trust

# Wait for ready
echo "⏳ Waiting for deployment..."
juju wait-for application $SERVICE --query='status=="active"' --timeout=5m

echo "✅ $SERVICE deployed!"
echo ""
echo "Check status: juju status"
echo "View logs: juju debug-log --include $SERVICE"
```

### **sync-to-cloud.sh:**

```bash
#!/bin/bash
# scripts/sync-to-cloud.sh

set -e

echo "🚀 Syncing local changes to cloud"

# Run tests
echo "🧪 Running tests..."
pytest services/*/tests/ || {
  echo "❌ Tests failed! Fix tests before syncing to cloud."
  exit 1
}

# Commit changes
echo "📝 Committing changes..."
git add .
git commit -m "Sync local changes to cloud"

# Push to all remotes
echo "☁️ Pushing to all cloud platforms..."
git push all main

echo "✅ Changes synced to cloud!"
echo ""
echo "Cloud deployments will start automatically:"
echo "  - GitHub Actions"
echo "  - Bitbucket Pipelines"
echo "  - GitLab Cloud CI"
echo "  - GitLab Self-Hosted CI"
echo ""
echo "Monitor deployments:"
echo "  - GitHub: https://github.com/ColossalCapital/project/actions"
echo "  - Bitbucket: https://bitbucket.org/colossalcapital/project/pipelines"
echo "  - GitLab: https://gitlab.com/colossalcapital/project/-/pipelines"
```

---

## 🎨 Tilt UI Features

### **Beautiful Dashboard:**
- 📊 All services status
- 📝 Live logs (all services)
- 🔄 Build status
- ⚡ Hot reload status
- 🎯 Resource usage
- 🐛 Error highlighting

### **Quick Actions:**
- 🔄 Rebuild service
- 🔁 Restart service
- 📋 View logs
- 🐛 Debug pod
- 🔍 Search logs
- 📊 View metrics

### **Keyboard Shortcuts:**
- `space` - Open in browser
- `r` - Rebuild all
- `s` - View service logs
- `t` - Run tests
- `q` - Quit

---

## 🔍 Debugging

### **Debug with Tilt:**

```bash
# Start Tilt with debug mode
tilt up -- --debug

# View logs for specific service
tilt logs auth-service

# Exec into pod
tilt exec auth-service -- /bin/bash

# View resource usage
tilt resources
```

### **Debug with Juju:**

```bash
# View application status
juju status

# View logs
juju debug-log --include auth-service

# Exec into unit
juju ssh auth-service/0

# View config
juju config auth-service

# View relations
juju show-application auth-service
```

### **Debug with kubectl:**

```bash
# View pods
kubectl get pods -n dev

# View logs
kubectl logs -f auth-service-0 -n dev

# Exec into pod
kubectl exec -it auth-service-0 -n dev -- /bin/bash

# Port forward
kubectl port-forward auth-service-0 8000:8000 -n dev

# View events
kubectl get events -n dev --sort-by='.lastTimestamp'
```

---

## 📊 Development Metrics

### **Local Development Speed:**
- File change → Live reload: **< 5 seconds**
- Full rebuild: **< 30 seconds**
- Deploy to local MicroK8s: **< 10 seconds**
- Total iteration time: **< 45 seconds**

### **Cloud Deployment Speed:**
- Git commit → CI/CD trigger: **< 10 seconds**
- Build + test: **2-5 minutes**
- Deploy to cloud: **1-2 minutes**
- Total deployment time: **3-7 minutes**

**Local is 4-9x faster for iteration!**

---

## ✅ Best Practices

### **Local Development:**
1. ✅ Use Tilt for full dev environment
2. ✅ Use Skaffold for focused service dev
3. ✅ Test locally before cloud sync
4. ✅ Use same Juju charms as cloud
5. ✅ Keep local dependencies in Docker Compose

### **Cloud Deployment:**
1. ✅ Always run tests before commit
2. ✅ Use `sync-to-cloud.sh` script
3. ✅ Monitor CI/CD pipelines
4. ✅ Verify deployment in each environment
5. ✅ Use same charms as local

### **Juju Charms:**
1. ✅ Test charms locally first
2. ✅ Use same charm for local and cloud
3. ✅ Version your charms
4. ✅ Document charm configuration
5. ✅ Use charm relations for dependencies

---

## 🎯 Complete Workflow

### **Day-to-Day Development:**

```bash
# Morning: Start dev environment
tilt up

# Tilt UI opens, all services running
# Edit code, see changes live!

# Afternoon: Test new feature
vim services/trading-service/src/strategy.py
# Save → Auto-rebuild → Auto-deploy → Test!

# Evening: Sync to cloud
./scripts/sync-to-cloud.sh

# Cloud deployments start automatically
# Monitor in CI/CD dashboards
```

### **Testing New Charm:**

```bash
# 1. Create charm locally
cd charms/new-service
juju charm create

# 2. Test locally
juju deploy ./charms/new-service \
  --resource new-service-image=localhost:32000/new-service:latest

# 3. Verify
juju status
juju debug-log --include new-service

# 4. If works, commit
git add charms/new-service
git commit -m "Add new-service charm"
git push all main

# 5. Cloud deploys automatically!
```

---

## 🎉 Summary

### **Local Development:**
- ✅ MicroK8s (single-node)
- ✅ Juju Charms (same as cloud!)
- ✅ Tilt (hot reload, beautiful UI)
- ✅ Skaffold (fast iteration)
- ✅ Docker Compose (dependencies)
- ✅ Seconds to see changes

### **Cloud Deployment:**
- ✅ MicroK8s (multi-node)
- ✅ Juju Charms (same as local!)
- ✅ 4 Git platforms
- ✅ CI/CD pipelines
- ✅ Redis coordinator
- ✅ Minutes to deploy

**Same charms, different environments, seamless workflow!** 🚀

---

## 💬 Quick Commands

```bash
# Setup
./scripts/dev-setup.sh

# Start dev environment
tilt up

# Deploy single service
./scripts/deploy-local.sh auth-service

# Sync to cloud
./scripts/sync-to-cloud.sh

# View status
juju status
tilt resources

# Debug
tilt logs auth-service
juju debug-log --include auth-service
kubectl logs -f auth-service-0 -n dev
```

---

## 🔮 Future Enhancements

### **Local Development:**
- VS Code integration
- IntelliJ integration
- Remote debugging
- Performance profiling
- Load testing

### **Cloud Deployment:**
- Canary deployments
- Blue-green deployments
- A/B testing
- Feature flags
- Automated rollback

**The complete development to production pipeline!** 🎉
