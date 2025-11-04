# 🚀 MicroK8s + OpenYurt Deployment Strategy

## 🎯 Vision: Terraspace → MicroK8s → Juju Charms → OpenYurt Edge

**Why MicroK8s?**
- ✅ Native Juju integration
- ✅ Lightweight, fast deployment
- ✅ Perfect for Juju Charms
- ✅ Easy to manage
- ✅ OpenYurt compatible

**Why OpenYurt?**
- ✅ Edge computing support
- ✅ Cloud-edge collaboration
- ✅ Autonomous edge nodes
- ✅ Future-proof architecture

---

## 🏗️ Architecture

```
Terraspace (IaC)
    ↓
MicroK8s Cluster
├─ Control Plane (cloud)
├─ Worker Nodes (cloud)
└─ Edge Nodes (OpenYurt - future)
    ↓
Namespaces
├─ dev
├─ qa
├─ prod
└─ juju
    ↓
Juju Charms
    ↓
4 CI/CD Platforms
├─ GitHub Actions
├─ Bitbucket Pipelines
├─ GitLab Cloud CI
└─ GitLab Self-Hosted CI
```

---

## 📋 Terraspace + MicroK8s Configuration

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
│   │   ├── microk8s/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── networking/
│   │   └── monitoring/
│   └── modules/
│       └── microk8s-cluster/
│           ├── main.tf
│           ├── install.sh
│           └── variables.tf
└── Terrafile
```

### **MicroK8s Stack:**

```hcl
# app/stacks/microk8s/main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# EC2 Instances for MicroK8s
resource "aws_instance" "microk8s_control_plane" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.control_plane_instance_type
  
  count = var.control_plane_count
  
  vpc_security_group_ids = [aws_security_group.microk8s.id]
  subnet_id              = var.subnet_ids[count.index % length(var.subnet_ids)]
  
  user_data = templatefile("${path.module}/install-microk8s.sh", {
    node_type   = "control-plane"
    environment = var.environment
    node_index  = count.index
  })
  
  tags = {
    Name        = "microk8s-control-${var.environment}-${count.index}"
    Environment = var.environment
    ManagedBy   = "Terraspace"
    NodeType    = "control-plane"
  }
}

resource "aws_instance" "microk8s_workers" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.worker_instance_type
  
  count = var.worker_count
  
  vpc_security_group_ids = [aws_security_group.microk8s.id]
  subnet_id              = var.subnet_ids[count.index % length(var.subnet_ids)]
  
  user_data = templatefile("${path.module}/install-microk8s.sh", {
    node_type   = "worker"
    environment = var.environment
    node_index  = count.index
  })
  
  tags = {
    Name        = "microk8s-worker-${var.environment}-${count.index}"
    Environment = var.environment
    ManagedBy   = "Terraspace"
    NodeType    = "worker"
  }
}

# Security Group
resource "aws_security_group" "microk8s" {
  name        = "microk8s-${var.environment}"
  description = "Security group for MicroK8s cluster"
  vpc_id      = var.vpc_id
  
  # Kubernetes API
  ingress {
    from_port   = 16443
    to_port     = 16443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Cluster communication
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }
  
  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "microk8s-${var.environment}"
    Environment = var.environment
  }
}

# Load Balancer for API
resource "aws_lb" "microk8s_api" {
  name               = "microk8s-api-${var.environment}"
  internal           = false
  load_balancer_type = "network"
  subnets            = var.subnet_ids
  
  tags = {
    Name        = "microk8s-api-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "microk8s_api" {
  name     = "microk8s-api-${var.environment}"
  port     = 16443
  protocol = "TCP"
  vpc_id   = var.vpc_id
  
  health_check {
    protocol = "TCP"
    port     = 16443
  }
}

resource "aws_lb_listener" "microk8s_api" {
  load_balancer_arn = aws_lb.microk8s_api.arn
  port              = 16443
  protocol          = "TCP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.microk8s_api.arn
  }
}

resource "aws_lb_target_group_attachment" "microk8s_api" {
  count            = var.control_plane_count
  target_group_arn = aws_lb_target_group.microk8s_api.arn
  target_id        = aws_instance.microk8s_control_plane[count.index].id
  port             = 16443
}

output "cluster_endpoint" {
  value = "https://${aws_lb.microk8s_api.dns_name}:16443"
}

output "control_plane_ips" {
  value = aws_instance.microk8s_control_plane[*].public_ip
}

output "worker_ips" {
  value = aws_instance.microk8s_workers[*].public_ip
}
```

### **MicroK8s Installation Script:**

```bash
#!/bin/bash
# app/stacks/microk8s/install-microk8s.sh

set -e

NODE_TYPE="${node_type}"
ENVIRONMENT="${environment}"
NODE_INDEX="${node_index}"

echo "🚀 Installing MicroK8s on $NODE_TYPE node $NODE_INDEX for $ENVIRONMENT"

# Update system
apt-get update
apt-get upgrade -y

# Install MicroK8s
snap install microk8s --classic --channel=1.28/stable

# Add ubuntu user to microk8s group
usermod -a -G microk8s ubuntu
chown -f -R ubuntu ~/.kube

# Wait for MicroK8s to be ready
microk8s status --wait-ready

if [ "$NODE_TYPE" = "control-plane" ]; then
  echo "📋 Setting up control plane node"
  
  # Enable essential addons
  microk8s enable dns
  microk8s enable storage
  microk8s enable ingress
  microk8s enable metallb:10.64.140.43-10.64.140.49
  microk8s enable cert-manager
  microk8s enable prometheus
  microk8s enable metrics-server
  
  # Enable Juju integration
  microk8s enable juju
  
  # Create namespaces
  microk8s kubectl create namespace dev || true
  microk8s kubectl create namespace qa || true
  microk8s kubectl create namespace prod || true
  microk8s kubectl create namespace juju || true
  microk8s kubectl create namespace monitoring || true
  
  # Label namespaces
  microk8s kubectl label namespace dev environment=dev
  microk8s kubectl label namespace qa environment=qa
  microk8s kubectl label namespace prod environment=prod
  
  # Apply resource quotas
  cat <<EOF | microk8s kubectl apply -f -
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
EOF
  
  # Get join token for workers
  microk8s add-node > /tmp/join-token.txt
  
  # Save kubeconfig
  microk8s config > /tmp/kubeconfig.yaml
  
  echo "✅ Control plane setup complete"
  echo "📋 Join token saved to /tmp/join-token.txt"
  
elif [ "$NODE_TYPE" = "worker" ]; then
  echo "👷 Setting up worker node"
  
  # Workers will join via join token
  # This will be handled by Terraspace provisioner
  
  echo "✅ Worker node ready to join"
fi

echo "🎉 MicroK8s installation complete!"
```

### **Environment Variables:**

```hcl
# config/env/dev.tfvars
environment                = "dev"
control_plane_count        = 1
worker_count              = 2
control_plane_instance_type = "t3.large"
worker_instance_type       = "t3.large"

# config/env/qa.tfvars
environment                = "qa"
control_plane_count        = 1
worker_count              = 3
control_plane_instance_type = "t3.xlarge"
worker_instance_type       = "t3.xlarge"

# config/env/prod.tfvars
environment                = "prod"
control_plane_count        = 3
worker_count              = 5
control_plane_instance_type = "t3.2xlarge"
worker_instance_type       = "t3.2xlarge"
```

---

## 🎯 Juju Integration with MicroK8s

### **Bootstrap Juju on MicroK8s:**

```bash
# MicroK8s has native Juju support!
# No need for separate bootstrap

# Install Juju
sudo snap install juju --classic

# Get kubeconfig from MicroK8s
microk8s config > ~/.kube/config

# Add MicroK8s cloud to Juju
juju add-k8s microk8s --controller microk8s-controller

# Bootstrap (automatic with MicroK8s addon)
juju bootstrap microk8s microk8s-controller

# Add models for each environment
juju add-model dev microk8s --config namespace=dev
juju add-model qa microk8s --config namespace=qa
juju add-model prod microk8s --config namespace=prod
```

### **Or Use MicroK8s Juju Addon:**

```bash
# Even easier - MicroK8s has built-in Juju addon!
microk8s enable juju

# This automatically:
# - Installs Juju controller
# - Configures Juju for MicroK8s
# - Sets up default model

# Just add your models
juju add-model dev --config namespace=dev
juju add-model qa --config namespace=qa
juju add-model prod --config namespace=prod
```

---

## 🌐 OpenYurt Integration (Future Edge Computing)

### **What is OpenYurt?**

OpenYurt extends Kubernetes to edge computing:
- ✅ Cloud-edge collaboration
- ✅ Autonomous edge nodes (work offline)
- ✅ Edge traffic management
- ✅ Edge device management
- ✅ Compatible with MicroK8s

### **Install OpenYurt on MicroK8s:**

```bash
# Install OpenYurt components
kubectl apply -f https://raw.githubusercontent.com/openyurtio/openyurt/master/config/setup/all_in_one.yaml

# Convert existing nodes to edge nodes
kubectl label node <node-name> openyurt.io/is-edge-worker=true

# Create NodePool for edge nodes
cat <<EOF | kubectl apply -f -
apiVersion: apps.openyurt.io/v1alpha1
kind: NodePool
metadata:
  name: edge-pool-1
spec:
  type: Edge
  selector:
    matchLabels:
      openyurt.io/nodepool: edge-pool-1
  taints:
    - key: node-role.openyurt.io/edge
      value: "true"
      effect: NoSchedule
EOF
```

### **Edge Node Setup:**

```bash
# On edge device (Raspberry Pi, edge server, etc.)
# Install MicroK8s
snap install microk8s --classic

# Join to cloud cluster
microk8s join <cloud-cluster-ip>:25000/<token>

# Label as edge node
kubectl label node <edge-node> openyurt.io/is-edge-worker=true
kubectl label node <edge-node> openyurt.io/nodepool=edge-pool-1
```

### **Deploy to Edge with Juju:**

```bash
# Create edge model
juju add-model edge --config namespace=edge

# Deploy to edge nodes
juju deploy ./charms/edge-analytics \
  --constraints "tags=edge-pool-1"

# Edge nodes can work autonomously
# Even if disconnected from cloud!
```

### **Terraspace + OpenYurt:**

```hcl
# app/stacks/microk8s/openyurt.tf

# Install OpenYurt on MicroK8s cluster
resource "null_resource" "install_openyurt" {
  depends_on = [aws_instance.microk8s_control_plane]
  
  provisioner "remote-exec" {
    connection {
      host        = aws_instance.microk8s_control_plane[0].public_ip
      user        = "ubuntu"
      private_key = file(var.ssh_private_key_path)
    }
    
    inline = [
      "microk8s kubectl apply -f https://raw.githubusercontent.com/openyurtio/openyurt/master/config/setup/all_in_one.yaml",
      "sleep 30",
      "microk8s kubectl wait --for=condition=Ready pod -l app=yurt-controller-manager -n kube-system --timeout=300s"
    ]
  }
}

# Create edge node pool
resource "null_resource" "create_edge_pool" {
  depends_on = [null_resource.install_openyurt]
  
  provisioner "remote-exec" {
    connection {
      host        = aws_instance.microk8s_control_plane[0].public_ip
      user        = "ubuntu"
      private_key = file(var.ssh_private_key_path)
    }
    
    inline = [
      <<-EOT
        cat <<EOF | microk8s kubectl apply -f -
        apiVersion: apps.openyurt.io/v1alpha1
        kind: NodePool
        metadata:
          name: edge-pool-${var.environment}
        spec:
          type: Edge
          selector:
            matchLabels:
              openyurt.io/nodepool: edge-pool-${var.environment}
        EOF
      EOT
    ]
  }
}
```

---

## 🚀 Complete Deployment Flow

### **1. Deploy Infrastructure with Terraspace:**

```bash
# Deploy MicroK8s cluster
cd terraspace
terraspace up microk8s -y --env prod

# Get cluster info
terraspace output microk8s cluster_endpoint --env prod
terraspace output microk8s control_plane_ips --env prod
```

### **2. Configure MicroK8s:**

```bash
# SSH to control plane
CONTROL_PLANE_IP=$(terraspace output microk8s control_plane_ips --env prod | jq -r '.[0]')
ssh ubuntu@$CONTROL_PLANE_IP

# Get kubeconfig
microk8s config > kubeconfig.yaml

# Enable Juju addon
microk8s enable juju

# Add models
juju add-model dev --config namespace=dev
juju add-model qa --config namespace=qa
juju add-model prod --config namespace=prod
```

### **3. Setup CI/CD:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to MicroK8s via Juju

on:
  push:
    branches: [main, develop, qa]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Juju
        run: |
          sudo snap install juju --classic
          
          # Configure kubeconfig for MicroK8s
          echo "${{ secrets.MICROK8S_KUBECONFIG }}" > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml
          
          # Add MicroK8s cloud
          juju add-k8s microk8s --controller microk8s-controller
      
      - name: Claim features
        run: |
          pip install redis
          python3 scripts/claim_features.py github
      
      - name: Deploy to MicroK8s
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
            echo "🚀 Deploying $feature to MicroK8s $ENV namespace"
            
            # Build and push image
            docker build -t ghcr.io/colossalcapital/$feature:${{ github.sha }} ./services/$feature
            docker push ghcr.io/colossalcapital/$feature:${{ github.sha }}
            
            # Deploy with Juju to MicroK8s
            juju deploy ./charms/$feature \
              --resource ${feature}-image=ghcr.io/colossalcapital/$feature:${{ github.sha }} \
              --trust
            
            # Wait for deployment
            juju wait-for application $feature --query='status=="active"'
            
            echo "✅ $feature deployed to MicroK8s!"
          done < my-features.txt
```

### **4. Deploy and Monitor:**

```bash
# Commit and push
git add .
git commit -m "Deploy to MicroK8s"
git push all main

# All 4 CI/CD platforms trigger
# Each deploys via Juju to MicroK8s
# Same cluster, different features!

# Monitor with Juju
juju status
juju debug-log

# Monitor with MicroK8s
microk8s kubectl get pods -A
microk8s kubectl top nodes
microk8s kubectl top pods -A
```

---

## 📊 Architecture Benefits

### **MicroK8s Advantages:**
- ✅ Lightweight (minimal resource usage)
- ✅ Fast deployment (seconds, not minutes)
- ✅ Native Juju integration
- ✅ Built-in addons (DNS, storage, ingress)
- ✅ Easy to manage
- ✅ Perfect for Juju Charms

### **OpenYurt Advantages:**
- ✅ Edge computing ready
- ✅ Autonomous edge nodes
- ✅ Cloud-edge collaboration
- ✅ Works with MicroK8s
- ✅ Future-proof architecture

### **Combined Benefits:**
- ✅ Cloud deployment (MicroK8s)
- ✅ Edge deployment (OpenYurt)
- ✅ Juju Charms everywhere
- ✅ Single management interface
- ✅ Seamless cloud-edge workloads

---

## 🌐 Future Edge Use Cases

### **Trading Edge Nodes:**
```bash
# Deploy trading algorithms to edge
juju switch edge
juju deploy ./charms/trading-algo \
  --constraints "tags=edge-pool-1"

# Low-latency trading at edge
# Autonomous operation if disconnected
# Sync to cloud when connected
```

### **Analytics Edge Nodes:**
```bash
# Process data at edge
juju deploy ./charms/edge-analytics \
  --constraints "tags=edge-pool-1"

# Reduce bandwidth to cloud
# Real-time processing at edge
# Send aggregated data to cloud
```

### **IoT Edge Nodes:**
```bash
# IoT data processing at edge
juju deploy ./charms/iot-processor \
  --constraints "tags=edge-pool-1"

# Process sensor data locally
# Autonomous operation
# Sync to cloud periodically
```

---

## ✅ Quick Commands

```bash
# Terraspace
terraspace up microk8s -y --env prod
terraspace output microk8s cluster_endpoint --env prod

# MicroK8s
microk8s status
microk8s kubectl get nodes
microk8s kubectl get pods -A
microk8s enable juju
microk8s config > kubeconfig.yaml

# Juju
juju status
juju switch prod
juju deploy ./charms/auth-service
juju scale-application auth-service 3
juju debug-log

# OpenYurt (future)
kubectl get nodepools
kubectl get pods -n edge
kubectl describe nodepool edge-pool-1
```

---

## 🎉 The Complete Stack!

**Terraspace → MicroK8s → Juju Charms → OpenYurt Edge**

- ✅ Easy deployment (MicroK8s)
- ✅ Native Juju support
- ✅ Edge computing ready (OpenYurt)
- ✅ 4 CI/CD platforms
- ✅ Same cluster deployment
- ✅ Future-proof architecture

**Perfect for cloud AND edge deployment!** 🚀
