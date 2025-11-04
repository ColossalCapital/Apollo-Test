# 🎯 Akashic Deploy Structure

## Overview

Two folders, clear separation of concerns:

1. **`Infrastructure/`** - Your custom, existing configs (source of truth)
2. **`.akashic/deploy/`** - Generated, standardized configs (managed by Akashic)

---

## 📁 Complete Structure

```
# Your existing configs (you manage)
Infrastructure/
├── docker-compose.complete-system.yml  # Your current setup
├── docker/                             # Custom Docker configs
├── kubernetes/                         # Custom K8s configs
├── juju/                              # Custom Juju charms
├── terraform/                         # Custom Terraform
└── cost-optimization/                 # Custom optimizations

# Generated configs (Akashic manages)
.akashic/
├── analysis/
│   ├── DEPLOYMENT_MAPPING.md          # Maps Infrastructure/ → .akashic/deploy/
│   └── deployment_map.json
│
└── deploy/
    ├── local/
    │   ├── docker/                    # Generated from Infrastructure/docker*
    │   │   ├── docker-compose.yml     # Optimized, standardized
    │   │   ├── docker-compose.base.yml  # Heavy services only
    │   │   └── docker-compose.dev.yml   # Dev overrides
    │   │
    │   ├── podman/                    # Generated Podman configs
    │   │   ├── podman-compose.yml     # Podman alternative
    │   │   ├── pods/                  # Pod definitions
    │   │   │   ├── base.yml
    │   │   │   └── services.yml
    │   │   └── containers/            # Individual containers
    │   │
    │   ├── tilt/                      # Generated Tilt configs (optional)
    │   │   ├── Tiltfile
    │   │   └── services/
    │   │       ├── apollo.yml
    │   │       ├── atlas.yml
    │   │       └── akashic.yml
    │   │
    │   ├── scripts/                   # Generated dev scripts
    │   │   ├── start-all.sh
    │   │   ├── start-base.sh          # Just databases/Kafka
    │   │   ├── start-services.sh      # Just your services
    │   │   ├── stop-all.sh
    │   │   ├── start-podman.sh        # Podman alternative
    │   │   └── switch-runtime.sh      # Switch Docker ↔ Podman
    │   │
    │   └── monitoring/                # Local monitoring
    │       ├── prometheus.yml
    │       ├── grafana/
    │       │   └── dashboards/
    │       └── docker-compose.monitoring.yml
    │
    └── cloud/
        ├── kubernetes/                # Generated from Infrastructure/kubernetes/
        │   ├── base/
        │   ├── overlays/
        │   │   ├── dev/
        │   │   ├── qa/
        │   │   └── prod/
        │   └── monitoring/
        │
        ├── juju/                      # Generated from Infrastructure/juju/
        │   ├── bundles/
        │   │   ├── dev-bundle.yml
        │   │   ├── qa-bundle.yml
        │   │   └── prod-bundle.yml
        │   └── charms/
        │
        ├── terraspace/                # Terraspace for multi-env deployments
        │   ├── app/
        │   │   ├── stacks/
        │   │   │   ├── microk8s/      # MicroK8s cluster provisioning
        │   │   │   │   ├── main.tf
        │   │   │   │   ├── variables.tf
        │   │   │   │   └── outputs.tf
        │   │   │   ├── juju/          # Juju controller setup
        │   │   │   └── monitoring/    # Monitoring infrastructure
        │   │   └── modules/
        │   │       ├── microk8s/
        │   │       ├── juju/
        │   │       └── monitoring/
        │   ├── config/
        │   │   └── terraform/
        │   │       ├── backend.tf
        │   │       └── provider.tf
        │   └── tfvars/
        │       ├── dev.tfvars
        │       ├── qa.tfvars
        │       └── prod.tfvars
        │
        └── monitoring/                # Cloud monitoring
            ├── prometheus/
            ├── grafana/
            └── alertmanager/
```

---

## 🌐 Terraspace + Juju Workflow

### **Why Terraspace?**

**Problem with Terraform:**
- Need separate folders for dev/qa/prod
- Duplicate code across environments
- Hard to maintain consistency

**Solution with Terraspace:**
- One codebase, multiple environments
- DRY (Don't Repeat Yourself)
- Easy to apply Juju charms after provisioning

### **Workflow:**

**Step 1: Provision MicroK8s with Terraspace**
```bash
# Deploy dev environment
cd .akashic/deploy/cloud/terraspace/
terraspace up microk8s -y --var-file=tfvars/dev.tfvars

# Deploy qa environment
terraspace up microk8s -y --var-file=tfvars/qa.tfvars

# Deploy prod environment
terraspace up microk8s -y --var-file=tfvars/prod.tfvars
```

**Step 2: Apply Juju Charms**
```bash
# Deploy charms to dev
juju deploy .akashic/deploy/cloud/juju/bundles/dev-bundle.yml

# Deploy charms to qa
juju deploy .akashic/deploy/cloud/juju/bundles/qa-bundle.yml

# Deploy charms to prod
juju deploy .akashic/deploy/cloud/juju/bundles/prod-bundle.yml
```

**Step 3: Monitor**
```bash
# Check cluster status
kubectl get nodes
juju status

# View monitoring
open http://grafana.dev.yourcompany.com
open http://grafana.qa.yourcompany.com
open http://grafana.prod.yourcompany.com
```

### **Example Terraspace Stack:**

**`.akashic/deploy/cloud/terraspace/app/stacks/microk8s/main.tf`**
```hcl
# Provisions MicroK8s cluster
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
```

**`.akashic/deploy/cloud/terraspace/tfvars/dev.tfvars`**
```hcl
environment = "dev"
k8s_version = "1.28/stable"
cluster_ip = "10.0.1.10"
metallb_ip_range = "10.0.1.100-10.0.1.200"
kubeconfig_path = "/home/ubuntu/.kube/dev-config"
```

**`.akashic/deploy/cloud/terraspace/tfvars/qa.tfvars`**
```hcl
environment = "qa"
k8s_version = "1.28/stable"
cluster_ip = "10.0.2.10"
metallb_ip_range = "10.0.2.100-10.0.2.200"
kubeconfig_path = "/home/ubuntu/.kube/qa-config"
```

**`.akashic/deploy/cloud/terraspace/tfvars/prod.tfvars`**
```hcl
environment = "prod"
k8s_version = "1.28/stable"
cluster_ip = "10.0.3.10"
metallb_ip_range = "10.0.3.100-10.0.3.200"
kubeconfig_path = "/home/ubuntu/.kube/prod-config"
```

### **Example Juju Bundle:**

**`.akashic/deploy/cloud/juju/bundles/dev-bundle.yml`**
```yaml
bundle: kubernetes
applications:
  apollo:
    charm: ./charms/apollo
    scale: 2
    resources:
      apollo-image: apollo:dev
    options:
      environment: dev
      log_level: debug
  
  atlas:
    charm: ./charms/atlas
    scale: 2
    resources:
      atlas-image: atlas:dev
    options:
      environment: dev
  
  postgresql:
    charm: postgresql-k8s
    channel: 14/stable
    scale: 1
    options:
      database: atlas_dev
  
  neo4j:
    charm: neo4j-k8s
    channel: 5/stable
    scale: 1

relations:
  - ["apollo:db", "postgresql:db"]
  - ["atlas:db", "postgresql:db"]
  - ["atlas:graph", "neo4j:graph"]
```

---

## 🐳 Podman Support

### **Why Podman?**

**Benefits:**
- Rootless containers (better security)
- Daemonless (no background service)
- Drop-in Docker replacement
- Pod support (like Kubernetes)
- Better for CI/CD

### **Usage:**

**Option 1: Use Podman Instead of Docker**
```bash
# Start with Podman
cd .akashic/deploy/local/podman/
podman-compose up
```

**Option 2: Switch Between Docker and Podman**
```bash
# Switch to Podman
cd .akashic/deploy/local/scripts/
./switch-runtime.sh podman

# Switch back to Docker
./switch-runtime.sh docker
```

**Option 3: Use Podman Pods (Kubernetes-like)**
```bash
# Start base pod (databases, Kafka)
cd .akashic/deploy/local/podman/
podman play kube pods/base.yml

# Start services pod (Apollo, Atlas)
podman play kube pods/services.yml
```

### **Generated Podman Configs:**

**`.akashic/deploy/local/podman/podman-compose.yml`**
```yaml
version: '3'
services:
  postgres:
    image: postgres:15
    # Same as Docker Compose
  
  apollo:
    build: ../../../Apollo
    # Same as Docker Compose
```

**`.akashic/deploy/local/podman/pods/base.yml`**
```yaml
# Kubernetes-style pod definition
apiVersion: v1
kind: Pod
metadata:
  name: base-services
spec:
  containers:
  - name: postgres
    image: postgres:15
    ports:
    - containerPort: 5432
  
  - name: neo4j
    image: neo4j:5
    ports:
    - containerPort: 7474
    - containerPort: 7687
  
  - name: kafka
    image: confluentinc/cp-kafka
    ports:
    - containerPort: 9092
```

**`.akashic/deploy/local/scripts/switch-runtime.sh`**
```bash
#!/bin/bash

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
```

---

## 🔄 Workflow

### **Step 1: Analysis**
```bash
akashic analyze
```

**What happens:**
- Scans `Infrastructure/` folder
- Finds all deployment configs
- Detects what you're using (Docker Compose, K8s, Juju, etc.)
- Maps functionality
- Generates report: `.akashic/analysis/DEPLOYMENT_MAPPING.md`

### **Step 2: Review**
```bash
cat .akashic/analysis/DEPLOYMENT_MAPPING.md
```

**Example output:**
```markdown
# Deployment Configuration Mapping

## Current Structure (Infrastructure/)
- docker-compose.complete-system.yml (19 services)
- docker/ (5 files)
- kubernetes/ (12 files)
- juju/ (8 files)

## Recommendations
1. Generate optimized Docker Compose → .akashic/deploy/local/docker/
2. Generate Tilt config → .akashic/deploy/local/tilt/ (optional)
3. Generate K8s manifests → .akashic/deploy/cloud/kubernetes/
4. Generate Juju bundles → .akashic/deploy/cloud/juju/
```

### **Step 3: Generate**
```bash
# Generate all configs
akashic deploy generate

# Or generate specific
akashic deploy generate --local-docker
akashic deploy generate --local-tilt
akashic deploy generate --cloud-k8s
```

**What happens:**
- Reads `Infrastructure/` configs
- Generates optimized versions in `.akashic/deploy/`
- Adds monitoring
- Adds dev scripts
- Follows best practices

### **Step 4: Use**

**Option A: Docker Compose (What You Use Now)**
```bash
# Use generated config
cd .akashic/deploy/local/docker/
docker-compose up

# Or use your existing config
cd Infrastructure/
docker-compose -f docker-compose.complete-system.yml up
```

**Option B: Tilt (If Computer Can Handle It)**
```bash
# Try Tilt for fast iteration
cd .akashic/deploy/local/tilt/
tilt up
```

**Option C: Hybrid (Recommended)**
```bash
# Start heavy services with Docker Compose
cd .akashic/deploy/local/docker/
docker-compose -f docker-compose.base.yml up -d

# Start your services with Tilt (fast iteration)
cd .akashic/deploy/local/tilt/
tilt up
```

---

## 🎯 Your Use Case: Docker Compose + Tilt

### **Current Setup:**
```yaml
# Infrastructure/docker-compose.complete-system.yml
services:
  postgres:
    image: postgres:15
    # ... heavy database
  
  neo4j:
    image: neo4j:5
    # ... heavy graph database
  
  kafka:
    image: confluentinc/cp-kafka
    # ... heavy message broker
  
  apollo:
    build: ../Apollo
    # ... your service
  
  atlas:
    build: ../Atlas
    # ... your service
```

### **After Akashic Generation:**

**File 1: `.akashic/deploy/local/docker/docker-compose.base.yml`**
```yaml
# Heavy services only (keep running)
services:
  postgres:
    image: postgres:15
    # ... optimized config
  
  neo4j:
    image: neo4j:5
    # ... optimized config
  
  kafka:
    image: confluentinc/cp-kafka
    # ... optimized config
```

**File 2: `.akashic/deploy/local/tilt/Tiltfile`**
```python
# Your services (fast iteration)
docker_build('apollo', '../../../Apollo')
docker_build('atlas', '../../../Atlas')

k8s_yaml('services/apollo.yml')
k8s_yaml('services/atlas.yml')

# Live reload on code changes
local_resource('apollo-hot-reload',
  'cd ../../../Apollo && python -m uvicorn main:app --reload',
  deps=['../../../Apollo/'],
  labels=['backend'])

local_resource('atlas-hot-reload',
  'cd ../../../Atlas && cargo watch -x run',
  deps=['../../../Atlas/src/'],
  labels=['backend'])
```

**File 3: `.akashic/deploy/local/scripts/start-all.sh`**
```bash
#!/bin/bash

# Start heavy services
echo "Starting databases and Kafka..."
cd ../docker
docker-compose -f docker-compose.base.yml up -d

# Wait for services to be ready
echo "Waiting for services..."
sleep 10

# Start Tilt (if available)
if command -v tilt &> /dev/null; then
  echo "Starting Tilt..."
  cd ../tilt
  tilt up
else
  echo "Tilt not installed, using Docker Compose..."
  cd ../docker
  docker-compose up
fi
```

### **Usage:**

**Simple (Docker Compose only):**
```bash
cd .akashic/deploy/local/docker/
docker-compose up
```

**Fast Iteration (Hybrid):**
```bash
# Terminal 1: Start heavy services
cd .akashic/deploy/local/docker/
docker-compose -f docker-compose.base.yml up -d

# Terminal 2: Start Tilt for your services
cd .akashic/deploy/local/tilt/
tilt up

# Now you get:
# - Live reload on code changes
# - Fast rebuilds (< 5 seconds)
# - Visual dashboard (http://localhost:10350)
```

**One Command:**
```bash
cd .akashic/deploy/local/scripts/
./start-all.sh
```

---

## 🔄 Continuous Sync

### **Scenario 1: You Modify Infrastructure/**
```bash
# You edit Infrastructure/docker-compose.complete-system.yml
vim Infrastructure/docker-compose.complete-system.yml

# Akashic detects change
akashic analyze --incremental

# Output:
# ⚠️  Detected changes in Infrastructure/
# 📝 Regenerating .akashic/deploy/

# Regenerate
akashic deploy generate --sync
```

### **Scenario 2: Akashic Updates .akashic/deploy/**
```bash
# Akashic generates new config
akashic deploy generate

# You review
cat .akashic/deploy/local/docker/docker-compose.yml

# You like it, sync back to Infrastructure/
akashic deploy sync --to-infrastructure

# Or keep them separate (recommended)
```

---

## 💡 Best Practices

### **1. Keep Infrastructure/ as Source of Truth**
- Your custom configs live here
- Akashic reads from here
- You commit this to git

### **2. Treat .akashic/deploy/ as Generated**
- Don't edit directly
- Regenerate when needed
- Add to `.gitignore` (optional)

### **3. Use Hybrid Approach**
- Heavy services (databases, Kafka) → Docker Compose
- Your services (Apollo, Atlas) → Tilt (fast iteration)
- Best of both worlds!

### **4. Monitoring Everywhere**
- Local: `.akashic/deploy/local/monitoring/`
- Cloud: `.akashic/deploy/cloud/monitoring/`
- Same configs, different targets

---

## 🎯 Decision Matrix

| Scenario | Docker Compose | Podman | Tilt | Hybrid |
|----------|----------------|--------|------|--------|
| **Simple setup** | ✅ | ✅ | ❌ | ❌ |
| **Fast iteration** | ❌ | ❌ | ✅ | ✅ |
| **Heavy services** | ✅ | ✅ | ❌ | ✅ |
| **Low-end computer** | ✅ | ✅ | ❌ | ❌ |
| **High-end computer** | ❌ | ❌ | ✅ | ✅ |
| **Production-like** | ✅ | ✅ | ❌ | ✅ |
| **Better security** | ❌ | ✅ | ❌ | ✅ |
| **Rootless** | ❌ | ✅ | ❌ | ✅ |
| **CI/CD** | ✅ | ✅ | ❌ | ✅ |

---

## 🚀 Getting Started

### **Step 1: Analyze**
```bash
cd /path/to/ColossalCapital
akashic analyze
```

### **Step 2: Review**
```bash
cat .akashic/analysis/DEPLOYMENT_MAPPING.md
```

### **Step 3: Generate**
```bash
# Generate Docker Compose (always)
akashic deploy generate --local-docker

# Generate Tilt (optional, if you want to try it)
akashic deploy generate --local-tilt

# Generate cloud configs
akashic deploy generate --cloud-k8s
akashic deploy generate --cloud-juju
```

### **Step 4: Try It**
```bash
# Option 1: Docker Compose (simple)
cd .akashic/deploy/local/docker/
docker-compose up

# Option 2: Tilt (fast iteration)
cd .akashic/deploy/local/tilt/
tilt up

# Option 3: Hybrid (recommended)
cd .akashic/deploy/local/scripts/
./start-all.sh
```

---

## 📊 Summary

**Two folders, clear roles:**

| Folder | Purpose | Managed By | Committed |
|--------|---------|------------|-----------|
| `Infrastructure/` | Custom configs | You | Yes |
| `.akashic/deploy/` | Generated configs | Akashic | Optional |

**Local Runtime Options:**
- **Docker Compose** - Simple, what you use now
- **Podman** - Rootless, more secure, drop-in replacement
- **Tilt** - Fast iteration, live reload
- **Hybrid** - Heavy services (Docker/Podman) + Your services (Tilt)

**Cloud Deployment:**
- **Terraspace** - One codebase, multiple environments (dev/qa/prod)
- **MicroK8s** - Lightweight Kubernetes
- **Juju** - Charm-based deployment
- **Workflow:** Terraspace provisions → Juju deploys charms

**Workflow:**
1. Akashic reads `Infrastructure/`
2. Generates optimized configs in `.akashic/deploy/`
3. You choose runtime (Docker, Podman, Tilt, Hybrid)
4. Deploy to cloud with Terraspace + Juju
5. Continuous sync keeps everything aligned

**Benefits:**
- ✅ Keep your existing configs
- ✅ Get optimized versions
- ✅ Multiple runtime options (Docker, Podman, Tilt)
- ✅ Terraspace for multi-environment deployments
- ✅ Juju charms for easy cloud deployment
- ✅ Gradual migration path
- ✅ Best practices built-in

**Your use case:**
- Keep using Docker Compose for heavy services
- Try Podman for better security (rootless)
- Try Tilt for your services (Apollo, Atlas, Akashic)
- Deploy to dev/qa/prod with Terraspace + Juju
- Get fast iteration (< 5 second rebuilds)
- Visual dashboard for monitoring

---

**Ready to try it?** 🚀
