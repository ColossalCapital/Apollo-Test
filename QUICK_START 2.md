# 🚀 Quick Start Guide

## One Command to Rule Them All

```bash
akashic analyze
```

That's it! Everything else is automatic.

---

## What Happens

### **Automatic (< 5 minutes):**

1. **Scans** your entire codebase
2. **Detects** project type (Web3, React, Python API, etc.)
3. **Maps** scattered deployment configs
4. **Pulls** existing tickets from Linear/Jira/GitHub/Bitbucket
5. **Generates** new tickets for improvements
6. **Detects** conflicts between local and cloud
7. **Creates** AI reconciliation plan
8. **Saves** everything to `.akashic/`

### **Manual (10-15 minutes):**

1. **Review** recommendations
2. **Choose** reconciliation options
3. **Apply** changes

---

## Quick Commands

```bash
# Analyze project
akashic analyze

# Review results
cat .akashic/analysis/PROJECT_TYPE_DETECTION.md
cat .akashic/analysis/DEPLOYMENT_MAPPING.md
cat .akashic/pm/RECONCILIATION_REPORT.md

# Reconcile PM tickets
akashic pm reconcile --apply \
  --choice "Setup K8s=keep_local" \
  --choice "Add tests=merge"

# Apply scaffolding (auto or custom)
akashic scaffold apply --auto
# OR
akashic scaffold apply --custom

# Start AI agents
akashic agents start

# Monitor progress
akashic dashboard
```

---

## Output Structure

```
.akashic/
├── analysis/
│   ├── PROJECT_TYPE_DETECTION.md      # What type of project
│   ├── DEPLOYMENT_MAPPING.md          # Where deployments are
│   ├── SCAFFOLDING_PLAN.md            # What to build
│   ├── RESTRUCTURING_PLAN.md          # How to improve
│   └── CURRENT_STATE.md               # Where you are now
│
├── docs/
│   ├── PROJECT_DOCS.md                # Consolidated docs
│   ├── DEPLOYMENT_GUIDE.md            # How to deploy
│   └── TESTING_GUIDE.md               # How to test
│
└── pm/
    ├── linear/tickets.json            # Linear tickets
    ├── jira/issues.json               # Jira issues
    ├── github/issues.json             # GitHub issues
    ├── bitbucket/issues.json          # Bitbucket issues
    └── RECONCILIATION_REPORT.md       # Conflicts & choices
```

---

## Example: Infrastructure Folder

### **Before:**
```
Infrastructure/
├── docker/
├── docker-compose/
├── kubernetes/
├── juju/
├── terraform/
└── cost-optimization/
```

### **After Analysis:**
```
.akashic/
├── analysis/
│   └── DEPLOYMENT_MAPPING.md
│       "Found 6 deployment folders"
│       "Detected 2 conflicts"
│       "Generated migration plan"
│
└── deploy/
    ├── local/
    │   └── docker/  (consolidated)
    └── cloud/
        ├── kubernetes/
        ├── juju/
        └── terraform/
```

---

## Example: PM Reconciliation

### **Conflict Detected:**
```
Local ticket: "Setup K8s" (HIGH priority, 2h estimate)
Cloud ticket: "Setup K8s" (MEDIUM priority, 8h estimate)
```

### **AI Recommendation:**
```
Use local version (Akashic scaffolding is faster)
```

### **Your Choice:**
```bash
akashic pm reconcile --apply --choice "Setup K8s=keep_local"
```

### **Result:**
```
✅ Updated cloud ticket to HIGH priority, 2h estimate
✅ All tickets aligned
```

---

## Time Savings

| Task | Manual | Akashic | Savings |
|------|--------|---------|---------|
| Analysis | 4-8h | < 5min | 96% |
| Planning | 2-4h | < 5min | 98% |
| Tickets | 1-2h | < 1min | 99% |
| Scaffolding | 4-8h | < 5min | 98% |
| **Total** | **11-22h** | **< 20min** | **95%** |

---

## Cloud Provider Support

**Supported:**
- AWS (EKS, EC2, S3, RDS)
- GCP (GKE, Compute, Cloud Storage)
- Azure (AKS, VMs, Blob Storage)
- **Vultr** (VKE, Compute, Object Storage) - 50-75% cheaper!
- DigitalOcean (DOKS, Droplets, Spaces)

**Cost Comparison (Web3 Project):**
- AWS: $188/month
- Vultr: $69/month
- **Savings: 63%**

---

## Project Types Supported

1. **Web3** → Scaffold-ETH-2 UI + Hardhat/Foundry
2. **React** → Vite + TailwindCSS + Playwright
3. **Python API** → FastAPI + pytest + OpenAPI
4. **Rust** → Cargo + cross-compilation
5. **Mobile** → React Native / Flutter
6. **ML** → Jupyter + TensorFlow/PyTorch

---

## PM Tools Supported

- **Linear** (recommended)
- **Jira**
- **GitHub Issues**
- **Bitbucket Issues**

All support bi-directional sync with AI reconciliation.

---

## Need Help?

```bash
# Get help
akashic help

# Check version
akashic version

# Run diagnostics
akashic doctor

# View logs
akashic logs

# Reset (if needed)
akashic reset
```

---

## Documentation

- **Complete Workflow:** `COMPLETE_AI_LIFECYCLE.md`
- **Implementation Status:** `IMPLEMENTATION_COMPLETE_V2.md`
- **Vultr Support:** `VULTR_CLOUD_SUPPORT.md`
- **Final Summary:** `FINAL_SUMMARY.md`

---

**That's it! One command, complete project intelligence.** 🎉
