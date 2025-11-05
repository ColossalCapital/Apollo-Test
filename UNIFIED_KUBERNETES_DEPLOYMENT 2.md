# 🚀 Unified Kubernetes Deployment Strategy

## 🎯 Vision: All Platforms → Same Kubernetes Cluster

**Infrastructure:**
- Terraspace manages Kubernetes cluster (dev, qa, prod)
- Juju Charms deploy to Kubernetes
- All 4 CI/CD platforms deploy to same cluster
- Smart coordination prevents duplicate work

---

## 🏗️ Architecture

```
Developer Commits
    ↓
Git Push (all 4 repos)
    ├─ GitHub Actions
    ├─ Bitbucket Pipelines
    ├─ GitLab Cloud CI
    └─ GitLab Self-Hosted CI
         ↓
    Redis Coordinator
    (splits work across platforms)
         ↓
    Juju Charms
    (deployment mechanism)
         ↓
    Kubernetes Cluster
    (managed by Terraspace)
    ├─ dev namespace
    ├─ qa namespace
    └─ prod namespace
```

---

## 🎯 Infrastructure Stack

### **Layer 1: Terraspace (Infrastructure as Code)**
- Manages Kubernetes cluster
- Provisions cloud resources
- Handles networking, storage, security
- Multi-environment (dev, qa, prod)

### **Layer 2: Kubernetes (Container Orchestration)**
- Single cluster, multiple namespaces
- dev, qa, prod isolation
- Shared resources (monitoring, logging)
- Auto-scaling, self-healing

### **Layer 3: Juju Charms (Deployment)**
- Deploys microservices to K8s
- Manages lifecycle (install, upgrade, scale)
- Handles relations between services
- All 4 CI/CD platforms use Juju

### **Layer 4: CI/CD Platforms (Triggers)**
- GitHub, Bitbucket, GitLab Cloud, GitLab Self-Hosted
- Detect changes, run tests
- Coordinate via Redis
- Deploy via Juju

---

## 📋 Terraspace Configuration

### **Directory Structure:**

```
terraspace/
├── config/
│   ├── terraform/
│   │   └── backend.tf
│   └── env/
│       ├── dev.tfvars
│       ├── qa.tfvars
│       └── prod.tfvars
├── app/
│   ├── stacks/
│   │   ├── kubernetes/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── networking/
│   │   │   ├── main.tf
│   │   │   └── variables.tf
│   │   └── monitoring/
│   │       ├── main.tf
│   │       └── variables.tf
│   └── modules/
│       └── k8s-cluster/
│           ├── main.tf
│           └── variables.tf
└── Terrafile
```

### **Kubernetes Cluster Stack:**

```hcl
# app/stacks/kubernetes/main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "colossalcapital-${var.environment}"
  role_arn = aws_iam_role.cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraspace"
    Project     = "ColossalCapital"
  }
}

# Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "main-${var.environment}"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.subnet_ids

  scaling_config {
    desired_size = var.node_count
    max_size     = var.node_count * 2
    min_size     = 1
  }

  instance_types = [var.instance_type]

  tags = {
    Environment = var.environment
  }
}

# Kubernetes Namespaces
resource "kubernetes_namespace" "dev" {
  metadata {
    name = "dev"
    labels = {
      environment = "dev"
    }
  }
}

resource "kubernetes_namespace" "qa" {
  metadata {
    name = "qa"
    labels = {
      environment = "qa"
    }
  }
}

resource "kubernetes_namespace" "prod" {
  metadata {
    name = "prod"
    labels = {
      environment = "prod"
    }
  }
}

# Juju Controller
resource "kubernetes_namespace" "juju" {
  metadata {
    name = "juju"
    labels = {
      component = "juju-controller"
    }
  }
}

output "cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "cluster_name" {
  value = aws_eks_cluster.main.name
}

output "kubeconfig" {
  value = aws_eks_cluster.main.certificate_authority[0].data
  sensitive = true
}
```

### **Environment Variables:**

```hcl
# config/env/dev.tfvars
environment   = "dev"
node_count    = 3
instance_type = "t3.large"

# config/env/qa.tfvars
environment   = "qa"
node_count    = 5
instance_type = "t3.xlarge"

# config/env/prod.tfvars
environment   = "prod"
node_count    = 10
instance_type = "t3.2xlarge"
```

### **Deploy with Terraspace:**

```bash
# Deploy dev environment
terraspace up kubernetes -y --env dev

# Deploy qa environment
terraspace up kubernetes -y --env qa

# Deploy prod environment
terraspace up kubernetes -y --env prod

# All environments share same cluster, different namespaces
```

---

## 🎯 Juju Charms for Kubernetes

### **Bootstrap Juju on Kubernetes:**

```bash
# Get kubeconfig from Terraspace
terraspace output kubernetes kubeconfig --env prod > kubeconfig.yaml

# Bootstrap Juju controller on K8s
juju bootstrap k8s juju-controller --config kubeconfig.yaml

# Add models for each environment
juju add-model dev k8s --config namespace=dev
juju add-model qa k8s --config namespace=qa
juju add-model prod k8s --config namespace=prod
```

### **Kubernetes Charm Structure:**

```yaml
# charms/auth-service/charmcraft.yaml
name: auth-service
type: charm
summary: Authentication service
description: JWT-based authentication with OAuth2

bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
    run-on:
      - name: ubuntu
        channel: "22.04"

# Kubernetes-specific
containers:
  auth-service:
    resource: auth-service-image

resources:
  auth-service-image:
    type: oci-image
    description: OCI image for auth-service

requires:
  postgresql:
    interface: postgresql
  redis:
    interface: redis

provides:
  auth-api:
    interface: http
```

### **Deploy Charms to Kubernetes:**

```bash
# Deploy to dev namespace
juju switch dev
juju deploy ./charms/auth-service --resource auth-service-image=ghcr.io/colossalcapital/auth-service:latest
juju deploy ./charms/trading-service --resource trading-service-image=ghcr.io/colossalcapital/trading-service:latest

# Deploy to qa namespace
juju switch qa
juju deploy ./charms/auth-service --resource auth-service-image=ghcr.io/colossalcapital/auth-service:qa
juju deploy ./charms/trading-service --resource trading-service-image=ghcr.io/colossalcapital/trading-service:qa

# Deploy to prod namespace
juju switch prod
juju deploy ./charms/auth-service --resource auth-service-image=ghcr.io/colossalcapital/auth-service:v1.0.0
juju deploy ./charms/trading-service --resource trading-service-image=ghcr.io/colossalcapital/trading-service:v1.0.0

# Add relations
juju relate auth-service postgresql
juju relate trading-service redis

# Scale
juju scale-application trading-service 3

# Check status
juju status
```

---

## 🔧 CI/CD Pipeline Integration

### **GitHub Actions:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes via Juju

on:
  push:
    branches: [main, develop, qa]

jobs:
  claim-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Claim features
        run: |
          pip install redis
          python3 scripts/claim_features.py github
      
      - name: Setup Juju
        run: |
          sudo snap install juju --classic
          
          # Configure kubeconfig
          echo "${{ secrets.KUBECONFIG }}" > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml
          
          # Bootstrap if needed
          juju bootstrap k8s juju-controller || true
      
      - name: Deploy to Kubernetes
        run: |
          # Determine environment
          if [ "${{ github.ref }}" = "refs/heads/main" ]; then
            ENV="prod"
          elif [ "${{ github.ref }}" = "refs/heads/qa" ]; then
            ENV="qa"
          else
            ENV="dev"
          fi
          
          # Switch to correct model
          juju switch $ENV
          
          # Deploy claimed features
          while read feature; do
            echo "🚀 Deploying $feature to $ENV namespace via Juju"
            
            # Build and push image
            docker build -t ghcr.io/colossalcapital/$feature:${{ github.sha }} ./services/$feature
            docker push ghcr.io/colossalcapital/$feature:${{ github.sha }}
            
            # Deploy with Juju
            juju deploy ./charms/$feature \
              --resource ${feature}-image=ghcr.io/colossalcapital/$feature:${{ github.sha }} \
              --trust
            
            # Wait for deployment
            juju wait-for application $feature --query='status=="active"'
          done < my-features.txt
      
      - name: Notify Linear
        uses: linear/action@v1
        with:
          api-key: ${{ secrets.LINEAR_API_KEY }}
          message: "✅ Deployed to $ENV via GitHub → Juju → Kubernetes"
```

### **Bitbucket Pipelines:**

```yaml
# bitbucket-pipelines.yml
image: atlassian/default-image:3

pipelines:
  branches:
    main:
      - step:
          name: Deploy to Kubernetes via Juju
          script:
            - pip install redis
            - python3 scripts/claim_features.py bitbucket
            
            # Setup Juju
            - snap install juju --classic
            - echo "$KUBECONFIG" > kubeconfig.yaml
            - export KUBECONFIG=kubeconfig.yaml
            - juju bootstrap k8s juju-controller || true
            
            # Deploy
            - ENV="prod"
            - juju switch $ENV
            - |
              while read feature; do
                echo "🚀 Deploying $feature to $ENV via Juju"
                
                docker build -t ghcr.io/colossalcapital/$feature:$BITBUCKET_COMMIT ./services/$feature
                docker push ghcr.io/colossalcapital/$feature:$BITBUCKET_COMMIT
                
                juju deploy ./charms/$feature \
                  --resource ${feature}-image=ghcr.io/colossalcapital/$feature:$BITBUCKET_COMMIT \
                  --trust
                
                juju wait-for application $feature --query='status=="active"'
              done < my-features.txt
```

### **GitLab CI:**

```yaml
# .gitlab-ci.yml
deploy:
  stage: deploy
  script:
    - pip install redis
    - python3 scripts/claim_features.py gitlab-cloud
    
    # Setup Juju
    - snap install juju --classic
    - echo "$KUBECONFIG" > kubeconfig.yaml
    - export KUBECONFIG=kubeconfig.yaml
    - juju bootstrap k8s juju-controller || true
    
    # Determine environment
    - |
      if [ "$CI_COMMIT_REF_NAME" = "main" ]; then
        ENV="prod"
      elif [ "$CI_COMMIT_REF_NAME" = "qa" ]; then
        ENV="qa"
      else
        ENV="dev"
      fi
    
    # Deploy
    - juju switch $ENV
    - |
      while read feature; do
        echo "🚀 Deploying $feature to $ENV via Juju"
        
        docker build -t ghcr.io/colossalcapital/$feature:$CI_COMMIT_SHA ./services/$feature
        docker push ghcr.io/colossalcapital/$feature:$CI_COMMIT_SHA
        
        juju deploy ./charms/$feature \
          --resource ${feature}-image=ghcr.io/colossalcapital/$feature:$CI_COMMIT_SHA \
          --trust
        
        juju wait-for application $feature --query='status=="active"'
      done < my-features.txt
```

---

## 📊 Deployment Flow

### **Complete Flow:**

```
1. Developer commits code
   ↓
2. Push to all 4 repos (git push all main)
   ↓
3. All 4 CI/CD platforms trigger
   ├─ GitHub Actions
   ├─ Bitbucket Pipelines
   ├─ GitLab Cloud CI
   └─ GitLab Self-Hosted CI
   ↓
4. Each platform claims features via Redis
   - GitHub: auth-service
   - Bitbucket: trading-service
   - GitLab Cloud: analytics-service
   - GitLab Self: frontend
   ↓
5. Each platform builds Docker images
   - Push to ghcr.io/colossalcapital/*
   ↓
6. Each platform deploys via Juju
   - juju deploy ./charms/auth-service
   - juju deploy ./charms/trading-service
   - etc.
   ↓
7. Juju deploys to Kubernetes
   - Same cluster
   - Correct namespace (dev/qa/prod)
   - Managed by Terraspace
   ↓
8. All features deployed!
   - No duplication
   - Parallel execution
   - Same cluster
```

---

## 🎯 Namespace Isolation

### **Kubernetes Namespaces:**

```yaml
# All environments in same cluster, isolated by namespace

apiVersion: v1
kind: Namespace
metadata:
  name: dev
  labels:
    environment: dev
    managed-by: terraspace
---
apiVersion: v1
kind: Namespace
metadata:
  name: qa
  labels:
    environment: qa
    managed-by: terraspace
---
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    environment: prod
    managed-by: terraspace
---
apiVersion: v1
kind: Namespace
metadata:
  name: juju
  labels:
    component: juju-controller
```

### **Resource Quotas:**

```yaml
# Dev namespace - smaller limits
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"

---
# QA namespace - medium limits
apiVersion: v1
kind: ResourceQuota
metadata:
  name: qa-quota
  namespace: qa
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    pods: "100"

---
# Prod namespace - large limits
apiVersion: v1
kind: ResourceQuota
metadata:
  name: prod-quota
  namespace: prod
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "500"
```

---

## 🔐 Access Control

### **RBAC for Juju:**

```yaml
# Juju service account with cluster-wide permissions
apiVersion: v1
kind: ServiceAccount
metadata:
  name: juju-controller
  namespace: juju

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: juju-controller
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: juju-controller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: juju-controller
subjects:
  - kind: ServiceAccount
    name: juju-controller
    namespace: juju
```

---

## 📈 Monitoring & Observability

### **Shared Monitoring Stack:**

```bash
# Deploy monitoring to shared namespace
juju switch monitoring
juju deploy prometheus-k8s
juju deploy grafana-k8s
juju deploy loki-k8s

# Relate to all environments
juju relate prometheus-k8s:metrics dev/auth-service:metrics
juju relate prometheus-k8s:metrics qa/auth-service:metrics
juju relate prometheus-k8s:metrics prod/auth-service:metrics

# Access Grafana
juju run grafana-k8s/0 get-admin-password
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

---

## 🚀 Quick Start

### **1. Setup Infrastructure with Terraspace:**

```bash
# Install Terraspace
gem install terraspace

# Initialize
cd terraspace
terraspace new project colossalcapital --plugin aws

# Deploy Kubernetes cluster
terraspace up kubernetes -y --env prod

# Get kubeconfig
terraspace output kubernetes kubeconfig --env prod > kubeconfig.yaml
export KUBECONFIG=kubeconfig.yaml
```

### **2. Bootstrap Juju:**

```bash
# Install Juju
sudo snap install juju --classic

# Bootstrap on Kubernetes
juju bootstrap k8s juju-controller

# Add models for each environment
juju add-model dev k8s --config namespace=dev
juju add-model qa k8s --config namespace=qa
juju add-model prod k8s --config namespace=prod
```

### **3. Setup Git Remotes:**

```bash
# Add all 4 remotes
git remote add all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@bitbucket.org:colossalcapital/project.git
git remote set-url --add --push all git@gitlab.com:colossalcapital/project.git
git remote set-url --add --push all git@gitlab.internal.colossalcapital.com:colossalcapital/project.git
```

### **4. Deploy:**

```bash
# Commit and push
git add .
git commit -m "Deploy new features"
git push all main

# All 4 CI/CD platforms trigger
# Each claims features via Redis
# Each deploys via Juju to same K8s cluster
# All features deployed to prod namespace!
```

---

## ✅ Benefits

### **Unified Infrastructure:**
- ✅ Single Kubernetes cluster
- ✅ Managed by Terraspace (IaC)
- ✅ Multiple namespaces (dev, qa, prod)
- ✅ Shared resources (monitoring, logging)

### **Flexible CI/CD:**
- ✅ 4 independent pipelines
- ✅ Smart work coordination
- ✅ No duplicate deployments
- ✅ Parallel execution

### **Juju Benefits:**
- ✅ Declarative deployments
- ✅ Lifecycle management
- ✅ Automatic scaling
- ✅ Service relations

### **Cost Efficiency:**
- ✅ Single cluster for all environments
- ✅ Namespace isolation
- ✅ Resource quotas
- ✅ Shared monitoring

---

## 🎉 The Complete Stack!

**Terraspace → Kubernetes → Juju → CI/CD (x4) → Same Cluster!**

Perfect for production deployment! 🚀
