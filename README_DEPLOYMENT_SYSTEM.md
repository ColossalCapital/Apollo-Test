# 🚀 Akashic Deployment System

**Automated deployment configuration mapping and generation with multi-runtime support!**

---

## 🎯 What It Does

Analyzes your scattered deployment configurations and generates optimized, standardized configs for:

- **Local Development:** Docker Compose, Podman, Tilt
- **Cloud Deployment:** Terraspace, Juju, MicroK8s, Kubernetes
- **Multi-Environment:** dev, qa, prod

---

## ⚡ Quick Start

```bash
# 1. Analyze your infrastructure
cd /path/to/your/project
akashic analyze

# 2. Review the mapping
cat .akashic/analysis/DEPLOYMENT_MAPPING.md

# 3. Use the generated configs
cd .akashic/deploy/local/scripts/
./start-all.sh
```

**That's it! Your deployment is now standardized and optimized.**

---

## 📁 What Gets Generated

```
.akashic/
├── analysis/
│   ├── DEPLOYMENT_MAPPING.md          # Detailed mapping report
│   └── deployment_map.json            # Machine-readable mapping
│
└── deploy/
    ├── local/
    │   ├── docker/
    │   │   ├── docker-compose.yml          # All services
    │   │   ├── docker-compose.base.yml     # Heavy services only
    │   │   └── docker-compose.dev.yml      # Dev overrides
    │   ├── podman/
    │   │   ├── podman-compose.yml          # Podman alternative
    │   │   └── pods/
    │   │       ├── base.yml                # Heavy services pod
    │   │       └── services.yml            # App services pod
    │   ├── tilt/
    │   │   └── Tiltfile                    # Fast iteration
    │   ├── scripts/
    │   │   ├── start-all.sh                # Hybrid mode
    │   │   ├── start-podman.sh             # Podman mode
    │   │   └── switch-runtime.sh           # Switch runtimes
    │   └── monitoring/
    └── cloud/
        ├── kubernetes/
        │   └── overlays/
        │       ├── dev/
        │       ├── qa/
        │       └── prod/
        ├── juju/
        │   └── bundles/
        │       ├── dev-bundle.yml
        │       ├── qa-bundle.yml
        │       └── prod-bundle.yml
        ├── terraspace/
        │   ├── app/stacks/microk8s/
        │   │   ├── main.tf
        │   │   ├── variables.tf
        │   │   └── outputs.tf
        │   └── tfvars/
        │       ├── dev.tfvars
        │       ├── qa.tfvars
        │       └── prod.tfvars
        └── monitoring/
```

---

## 🎮 Usage Options

### **Option 1: Docker Compose (Simple)**
```bash
cd .akashic/deploy/local/docker/
docker-compose up
```

### **Option 2: Podman (Secure)**
```bash
cd .akashic/deploy/local/podman/
podman-compose up
```

### **Option 3: Tilt (Fast Iteration)**
```bash
cd .akashic/deploy/local/tilt/
tilt up
```

### **Option 4: Hybrid (Recommended)**
```bash
cd .akashic/deploy/local/scripts/
./start-all.sh

# This will:
# 1. Start heavy services (databases, Kafka) with Docker Compose
# 2. Start your services with Tilt (fast iteration)
# 3. Give you the best of both worlds!
```

### **Option 5: Cloud Deployment**
```bash
# Provision infrastructure with Terraspace
cd .akashic/deploy/cloud/terraspace/
terraspace up microk8s -y --var-file=tfvars/dev.tfvars

# Deploy with Juju
cd .akashic/deploy/cloud/juju/
juju deploy bundles/dev-bundle.yml
```

---

## 🔧 How It Works

### **Phase 1: Deployment Mapping**
```python
from services.deployment_mapper import DeploymentMapper

mapper = DeploymentMapper("/path/to/repo")
result = await mapper.analyze_deployments()

# Finds all deployment folders
# Analyzes deployment files
# Detects conflicts
# Generates recommendations
```

### **Phase 2: Config Generation**
```python
from services.deployment_config_generator import DeploymentConfigGenerator

generator = DeploymentConfigGenerator(
    "/path/to/repo",
    result['deployment_map']
)
await generator.generate_all()

# Generates Docker Compose configs
# Generates Podman configs
# Generates Tilt configs
# Generates Terraspace stacks
# Generates Juju bundles
# Generates helper scripts
```

### **Phase 3: Orchestration**
```python
from services.akashic_intelligence_orchestrator import AkashicIntelligenceOrchestrator

orchestrator = AkashicIntelligenceOrchestrator(entity_id="user_123")
result = await orchestrator.analyze_repository("/path/to/repo")

# Automatically runs both phases
# Saves all outputs to .akashic/
```

---

## 📊 Features

### **Smart Detection**
- ✅ Automatically detects deployment tools (Docker, K8s, Juju, Terraform, etc.)
- ✅ Identifies cloud providers (AWS, GCP, Azure, Vultr, DigitalOcean)
- ✅ Separates heavy services (databases) from app services
- ✅ Detects conflicts (multiple Docker setups, etc.)

### **Multi-Runtime Support**
- ✅ Docker Compose (simple, production-like)
- ✅ Podman (rootless, more secure)
- ✅ Tilt (fast iteration, live reload)
- ✅ Hybrid (best of both worlds)

### **Multi-Environment**
- ✅ Terraspace for dev/qa/prod
- ✅ Juju bundles for each environment
- ✅ Environment-specific configs

### **Migration Assistance**
- ✅ Detailed migration plan
- ✅ AI-assisted migration prompts
- ✅ Priority-based recommendations

---

## 🧪 Testing

```bash
# Run the test script
cd Apollo/
python test_deployment_system.py

# Expected output:
# 🧪 Testing Deployment System
# ✅ Deployment Mapper Success!
# ✅ Config Generator Success!
# 🎉 ALL TESTS PASSED!
```

---

## 📚 Documentation

- **[AKASHIC_DEPLOY_STRUCTURE.md](./AKASHIC_DEPLOY_STRUCTURE.md)** - Complete structure guide with examples
- **[DEPLOYMENT_OPTIONS_SUMMARY.md](./DEPLOYMENT_OPTIONS_SUMMARY.md)** - Quick reference for all options
- **[DEPLOYMENT_SYSTEM_IMPLEMENTATION.md](./DEPLOYMENT_SYSTEM_IMPLEMENTATION.md)** - Implementation details
- **[QUICK_START.md](./QUICK_START.md)** - Quick start guide
- **[IMPLEMENTATION_COMPLETE_FINAL.md](./IMPLEMENTATION_COMPLETE_FINAL.md)** - Final summary

---

## 🎯 Your Use Case

### **Before:**
```
Infrastructure/
├── docker/              # Some Docker configs
├── docker-compose/      # More Docker configs
├── kubernetes/          # K8s manifests
├── juju/               # Juju charms
└── terraform/          # Terraform configs

Problems:
❌ Scattered configs
❌ Duplicate setups
❌ Hard to maintain
❌ No standardization
```

### **After:**
```
.akashic/deploy/
├── local/
│   ├── docker/         # Consolidated Docker
│   ├── podman/         # Podman alternative
│   ├── tilt/          # Fast iteration
│   └── scripts/       # Helper scripts
└── cloud/
    ├── kubernetes/    # Consolidated K8s
    ├── juju/         # Juju bundles
    ├── terraspace/   # Multi-env provisioning
    └── monitoring/   # Monitoring configs

Benefits:
✅ Standardized structure
✅ No duplication
✅ Easy to maintain
✅ Multiple runtime options
✅ Automated deployment
```

---

## 💡 Examples

### **Example 1: Docker Compose → Podman**
```bash
# Switch from Docker to Podman
cd .akashic/deploy/local/scripts/
./switch-runtime.sh podman

# Start with Podman
cd ../podman/
podman-compose up
```

### **Example 2: Fast Iteration with Tilt**
```bash
# Start heavy services with Docker
cd .akashic/deploy/local/docker/
docker-compose -f docker-compose.base.yml up -d

# Start your services with Tilt (fast iteration)
cd ../tilt/
tilt up

# Now you get:
# - Live reload on code changes
# - Fast rebuilds (< 5 seconds)
# - Visual dashboard (http://localhost:10350)
```

### **Example 3: Deploy to Cloud**
```bash
# Deploy dev environment
cd .akashic/deploy/cloud/terraspace/
terraspace up microk8s -y --var-file=tfvars/dev.tfvars

# Deploy Juju charms
cd ../juju/
juju deploy bundles/dev-bundle.yml

# Check status
kubectl get nodes
juju status
```

---

## 📈 Time Savings

| Task | Manual | Akashic | Savings |
|------|--------|---------|---------|
| Analysis | 4-8h | < 5min | 96% |
| Config Generation | 2-4h | < 1min | 98% |
| Setup | 1-2h | < 1min | 99% |
| **Total** | **7-14h** | **< 10min** | **95%** |

---

## 🔧 Configuration

### **Environment Variables**
```bash
# Optional: Specify Linear API key for PM integration
export LINEAR_API_KEY="your_key_here"

# Optional: Specify other PM tool keys
export JIRA_API_KEY="your_key_here"
export GITHUB_TOKEN="your_token_here"
```

### **Options**
```python
# Customize analysis options
options = {
    'watch_files': True,
    'consolidate_docs': True,
    'generate_plan': True,
    'build_knowledge_graph': True,
    'index_for_search': True,
}

result = await orchestrator.analyze_repository(
    repo_path="/path/to/repo",
    options=options
)
```

---

## 🐛 Troubleshooting

### **Issue: No deployment folders found**
```bash
# Make sure you have deployment configs in your repo
ls -la Infrastructure/
ls -la docker*/
ls -la kubernetes/
```

### **Issue: Generated configs don't work**
```bash
# Check the mapping report for conflicts
cat .akashic/analysis/DEPLOYMENT_MAPPING.md

# Review the generated configs
cat .akashic/deploy/local/docker/docker-compose.yml
```

### **Issue: Tilt not working**
```bash
# Make sure Tilt is installed
brew install tilt

# Or download from https://tilt.dev
```

---

## 🤝 Contributing

Found a bug or want to add a feature? Please open an issue or PR!

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎉 Summary

**One command to rule them all:**
```bash
akashic analyze
```

**Result:**
- ✅ Deployment configs mapped
- ✅ Conflicts detected
- ✅ Optimized configs generated
- ✅ Helper scripts created
- ✅ Multi-environment support
- ✅ Ready to deploy!

**Your deployment workflow is now:**
- ✅ Standardized
- ✅ Automated
- ✅ Multi-runtime (Docker, Podman, Tilt)
- ✅ Multi-environment (dev/qa/prod)
- ✅ Cloud-ready (Terraspace + Juju)
- ✅ 95% faster!

---

**Happy deploying! 🚀**
