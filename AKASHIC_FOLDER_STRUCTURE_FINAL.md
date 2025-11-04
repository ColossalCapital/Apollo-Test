# 🎯 .akashic/ Folder Structure (FINAL)

## 📁 Complete Structure

```
.akashic/
├── analysis/                          # Project Analysis ✅ IMPLEMENTED
│   ├── CURRENT_STATE.md
│   ├── FUTURE_STATE.md
│   ├── DOCUMENTATION_ANALYSIS.md
│   ├── TESTING_ANALYSIS.md
│   ├── file_metrics.json
│   └── current_state/
│       ├── README.md
│       ├── file_inventory.md
│       ├── hot_files_analysis.md
│       ├── cold_files_analysis.md
│       ├── dependencies.md
│       ├── tech_stack.md
│       └── metrics.md
│
├── docs/                              # Consolidated Documentation
│   ├── PROJECT_DOCS.md
│   ├── API_DOCS.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   └── diagrams/                      # Mermaid Diagrams
│       ├── architecture.mmd
│       ├── data_flow.mmd
│       ├── deployment.mmd
│       └── rendered/                  # PNG/SVG exports
│           ├── architecture.png
│           ├── architecture.svg
│           ├── data_flow.png
│           └── deployment.png
│
├── deploy/                            # Deployment Configs 🎯 TO IMPLEMENT
│   ├── local/                         # Local Development
│   │   ├── docker/
│   │   │   ├── docker-compose.yml
│   │   │   ├── docker-compose.dev.yml
│   │   │   ├── Dockerfile.dev
│   │   │   └── .env.example
│   │   ├── podman/
│   │   │   ├── podman-compose.yml
│   │   │   ├── Containerfile.dev
│   │   │   └── .env.example
│   │   ├── microk8s/
│   │   │   ├── install-local.sh
│   │   │   ├── namespace.yaml
│   │   │   ├── resource-quotas.yaml
│   │   │   └── manifests/
│   │   │       ├── apollo.yaml
│   │   │       ├── postgres.yaml
│   │   │       └── redis.yaml
│   │   ├── tilt/
│   │   │   ├── Tiltfile
│   │   │   └── tilt_config.json
│   │   ├── skaffold/
│   │   │   └── skaffold.yaml
│   │   ├── monitoring/                # Local monitoring
│   │   │   ├── prometheus.yml
│   │   │   ├── grafana/
│   │   │   │   └── dashboards/
│   │   │   └── docker-compose.monitoring.yml
│   │   └── scripts/
│   │       ├── dev-setup.sh           # Auto-detects: MicroK8s → Docker → Podman
│   │       ├── deploy-local.sh
│   │       ├── stop-local.sh
│   │       └── sync-to-cloud.sh
│   │
│   └── cloud/                         # Cloud Deployment
│       ├── terraspace/                # Infrastructure as Code
│       │   ├── config/
│       │   │   ├── terraform/
│       │   │   │   └── backend.tf
│       │   │   └── env/
│       │   │       ├── dev.tfvars
│       │   │       ├── qa.tfvars
│       │   │       └── prod.tfvars
│       │   └── app/
│       │       └── stacks/
│       │           ├── microk8s/
│       │           │   ├── main.tf
│       │           │   ├── variables.tf
│       │           │   ├── outputs.tf
│       │           │   └── install-microk8s.sh
│       │           ├── monitoring/    # Cloud monitoring stack
│       │           │   ├── main.tf
│       │           │   ├── prometheus.tf
│       │           │   ├── grafana.tf
│       │           │   └── alertmanager.tf
│       │           └── networking/
│       │               ├── main.tf
│       │               └── vpc.tf
│       │
│       ├── charms/                    # Juju Charms
│       │   ├── auth-service/
│       │   │   ├── charmcraft.yaml
│       │   │   ├── metadata.yaml
│       │   │   └── src/
│       │   │       └── charm.py
│       │   ├── trading-service/
│       │   │   ├── charmcraft.yaml
│       │   │   ├── metadata.yaml
│       │   │   └── src/
│       │   │       └── charm.py
│       │   └── analytics-service/
│       │       ├── charmcraft.yaml
│       │       ├── metadata.yaml
│       │       └── src/
│       │           └── charm.py
│       │
│       ├── pipelines/                 # CI/CD Pipelines
│       │   ├── github/
│       │   │   └── workflows/
│       │   │       ├── deploy.yml
│       │   │       ├── test.yml
│       │   │       └── analyze.yml
│       │   ├── bitbucket/
│       │   │   └── bitbucket-pipelines.yml
│       │   ├── gitlab/
│       │   │   └── .gitlab-ci.yml
│       │   └── gitlab-self/
│       │       └── .gitlab-ci.yml
│       │
│       ├── coordinator/               # Deployment Coordinator
│       │   ├── deployment_coordinator.py
│       │   ├── requirements.txt
│       │   ├── Dockerfile
│       │   └── redis-config.yaml
│       │
│       ├── monitoring/                # Cloud monitoring configs
│       │   ├── prometheus/
│       │   │   ├── rules.yaml
│       │   │   └── alerts.yaml
│       │   ├── grafana/
│       │   │   └── dashboards/
│       │   │       ├── deployment.json
│       │   │       ├── services.json
│       │   │       └── infrastructure.json
│       │   └── alertmanager/
│       │       └── config.yaml
│       │
│       └── scripts/
│           ├── setup-cloud.sh
│           ├── deploy-to-cloud.sh
│           ├── provision-infrastructure.sh
│           └── sync-repos.sh
│
├── pm/                                # Project Management Integration
│   ├── linear/
│   │   ├── project.json
│   │   ├── tickets.json
│   │   └── config.yaml
│   ├── jira/
│   │   ├── project.json
│   │   ├── issues.json
│   │   └── config.yaml
│   └── github/
│       ├── issues.json
│       └── config.yaml
│
├── restructuring/                     # Code Reorganization Plans
│   ├── proposed_structure.md
│   ├── migration_plan.md
│   └── refactoring_tickets.json
│
├── .config/                           # Akashic Configuration
│   ├── .akashic.yml                   # Main config
│   ├── ignore_patterns.txt
│   └── analysis_config.json
│
└── README.md                          # .akashic/ Overview
```

---

## 📊 Key Changes from Previous Version

### **1. Diagrams Moved to docs/**
```
OLD: .akashic/diagrams/
NEW: .akashic/docs/diagrams/
```
**Reason:** Diagrams are documentation, should be with docs

### **2. Monitoring Split by Context**
```
Local Monitoring:
.akashic/deploy/local/monitoring/
├── prometheus.yml
├── grafana/
└── docker-compose.monitoring.yml

Cloud Monitoring:
.akashic/deploy/cloud/monitoring/
├── prometheus/
├── grafana/
└── alertmanager/

Cloud Infrastructure (Terraspace):
.akashic/deploy/cloud/terraspace/app/stacks/monitoring/
├── main.tf
├── prometheus.tf
└── grafana.tf
```

**Reason:**
- **Local monitoring:** For monitoring local dev services
- **Cloud monitoring:** Configs for deployed monitoring stack
- **Cloud infrastructure:** Terraspace provisions the monitoring infrastructure

---

## 🎯 Folder Purposes

### **analysis/** ✅ IMPLEMENTED
**Purpose:** Project intelligence and metrics
**Generated by:** Akashic analysis engine
**Contents:**
- Documentation coverage analysis
- Testing coverage analysis
- Current state breakdown (7 files)
- File metrics and trends

### **docs/**
**Purpose:** All project documentation
**Generated by:** Akashic + manual
**Contents:**
- Consolidated markdown docs
- API documentation
- Architecture docs
- **Mermaid diagrams** (source + rendered)

### **deploy/local/**
**Purpose:** Local development deployment
**Used by:** Developers
**Contents:**
- Docker/Podman/MicroK8s configs
- Tilt/Skaffold for hot reload
- Auto-detect scripts
- Local monitoring setup

### **deploy/cloud/**
**Purpose:** Cloud deployment
**Used by:** CI/CD pipelines
**Contents:**
- Terraspace (infrastructure)
- Juju Charms (services)
- CI/CD pipelines (4 platforms)
- Deployment coordinator
- Cloud monitoring configs

### **pm/**
**Purpose:** Project management integration
**Generated by:** Akashic + PM APIs
**Contents:**
- Linear tickets
- Jira issues
- GitHub issues
- Sync configurations

### **restructuring/**
**Purpose:** Code reorganization plans
**Generated by:** Akashic analysis
**Contents:**
- Proposed structure
- Migration plans
- Refactoring tickets

---

## 🔄 Workflow Examples

### **1. Local Development**
```bash
# Setup (auto-detects runtime)
cd .akashic/deploy/local/scripts
./dev-setup.sh

# If MicroK8s detected:
# → Uses Tilt + Juju
# → Monitoring at http://localhost:3000 (Grafana)

# If Docker detected:
# → Uses Docker Compose
# → Monitoring: docker-compose -f docker-compose.monitoring.yml up
```

### **2. Generate Documentation**
```bash
# Analyze project
akashic analyze

# Generates:
.akashic/analysis/
├── DOCUMENTATION_ANALYSIS.md
├── TESTING_ANALYSIS.md
└── current_state/

# Generate diagrams
akashic diagrams generate

# Generates:
.akashic/docs/diagrams/
├── architecture.mmd
├── data_flow.mmd
└── rendered/
    ├── architecture.png
    └── data_flow.png
```

### **3. Deploy to Cloud**
```bash
# Provision infrastructure
cd .akashic/deploy/cloud/terraspace
terraspace up microk8s -y --env prod
terraspace up monitoring -y --env prod

# Deploy services (via CI/CD)
git push all main

# Monitor
# → Grafana: https://grafana.prod.example.com
# → Prometheus: https://prometheus.prod.example.com
```

### **4. Create PM Tickets**
```bash
# Analyze and create tickets
akashic analyze --create-tickets

# Generates:
.akashic/pm/
├── linear/tickets.json
├── jira/issues.json
└── github/issues.json

# Tickets created in:
# - Linear (from GitHub)
# - Jira (from Bitbucket)
# - GitHub Issues (from GitLab)
```

---

## 📝 Configuration Example

### **.akashic/.config/.akashic.yml**
```yaml
version: "1.0"

project:
  name: "ColossalCapital"
  type: "microservices"

analysis:
  enabled: true
  auto_analyze: true

deployment:
  local:
    preferred: "microk8s"
    fallback: ["docker", "podman"]
    monitoring:
      enabled: true
      prometheus_port: 9090
      grafana_port: 3000
  
  cloud:
    provider: "aws"
    orchestrator: "microk8s"
    deployment_tool: "juju"
    monitoring:
      prometheus: true
      grafana: true
      alertmanager: true
    ci_cd_platforms:
      - github
      - bitbucket
      - gitlab-cloud
      - gitlab-self

documentation:
  auto_consolidate: true
  generate_diagrams: true
  diagram_formats:
    - mermaid
    - png
    - svg

pm_integration:
  linear:
    enabled: true
  jira:
    enabled: true
  github:
    enabled: true
```

---

## ✅ Summary of Changes

| Item | Old Location | New Location | Reason |
|------|-------------|--------------|--------|
| **Diagrams** | `.akashic/diagrams/` | `.akashic/docs/diagrams/` | Diagrams are documentation |
| **Local Monitoring** | `.akashic/monitoring/` | `.akashic/deploy/local/monitoring/` | Context-specific |
| **Cloud Monitoring Configs** | `.akashic/monitoring/` | `.akashic/deploy/cloud/monitoring/` | Deployment-related |
| **Cloud Monitoring Infra** | N/A | `.akashic/deploy/cloud/terraspace/app/stacks/monitoring/` | Provisioned by Terraspace |

---

## 🎯 Quick Reference

### **Analysis:**
```bash
akashic analyze
# Output: .akashic/analysis/
```

### **Documentation:**
```bash
akashic docs consolidate
akashic diagrams generate
# Output: .akashic/docs/
```

### **Local Dev:**
```bash
cd .akashic/deploy/local/scripts
./dev-setup.sh
# Monitoring: http://localhost:3000
```

### **Cloud Deploy:**
```bash
cd .akashic/deploy/cloud/terraspace
terraspace up microk8s -y --env prod
terraspace up monitoring -y --env prod
# Monitoring: https://grafana.prod.example.com
```

### **PM Integration:**
```bash
akashic analyze --create-tickets
# Output: .akashic/pm/
```

---

## 🎉 Perfect Structure!

**Everything in `.akashic/`:**
- ✅ Analysis & metrics
- ✅ Documentation & diagrams (in docs/)
- ✅ Local deployment (with local monitoring)
- ✅ Cloud deployment (with cloud monitoring)
- ✅ CI/CD pipelines
- ✅ Infrastructure as code
- ✅ PM integration
- ✅ Monitoring (context-specific)

**One folder, complete project intelligence!** 🚀
