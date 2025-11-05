# 🚀 Intelligent Dual-Deployment Strategy

## 🎯 The Vision

**One commit → Two repos → Smart deployment splitting → Same cloud resources → No duplicate work!**

---

## 🏗️ Architecture

```
Developer Commits
    ↓
Git Push (both repos simultaneously)
    ├─ GitHub (Primary)
    │   ├─ Detects: Features A, B, C
    │   ├─ Claims: Features A, B
    │   └─ Deploys: A, B to cloud
    │
    └─ Bitbucket (Mirror)
        ├─ Detects: Features A, B, C
        ├─ Sees: A, B already claimed by GitHub
        ├─ Claims: Feature C
        └─ Deploys: C to cloud

Result: All features deployed, no duplication! ✅
```

---

## 🔧 Solution 1: Push to Both Repos Simultaneously

### **Git Configuration:**

```bash
# One-time setup
git remote add github git@github.com:ColossalCapital/project.git
git remote add bitbucket git@bitbucket.org:colossalcapital/project.git

# Create "all" remote that pushes to both
git remote add all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@bitbucket.org:colossalcapital/project.git

# Now push to both at once!
git push all main
```

### **Git Aliases for Easy Use:**

```bash
# Add to ~/.gitconfig
[alias]
    pushall = !git push github && git push bitbucket
    pullall = !git pull github && git pull bitbucket
    syncall = !git push all --all && git push all --tags
```

### **Usage:**

```bash
# Commit changes
git add .
git commit -m "Add new feature"

# Push to both repos
git push all main

# Or use alias
git pushall
```

---

## 🤖 Solution 2: Intelligent Deployment Coordination

### **The Problem:**
Both GitHub Actions and Bitbucket Pipelines trigger on the same commit. Without coordination, they'd both try to deploy everything → duplicate work, conflicts, race conditions.

### **The Solution: Deployment Coordinator Service**

**Shared Redis/Database for Coordination:**

```python
# deployment_coordinator.py
import redis
import hashlib
from datetime import datetime, timedelta

class DeploymentCoordinator:
    """
    Coordinates deployments between GitHub and Bitbucket
    to prevent duplicate work
    """
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.lock_ttl = 300  # 5 minutes
    
    def claim_deployment(
        self, 
        commit_sha: str, 
        feature: str, 
        platform: str
    ) -> bool:
        """
        Try to claim a feature deployment
        
        Returns True if claimed, False if already claimed by other platform
        """
        lock_key = f"deploy:{commit_sha}:{feature}"
        
        # Try to set lock with NX (only if not exists)
        claimed = self.redis.set(
            lock_key,
            platform,
            ex=self.lock_ttl,
            nx=True
        )
        
        if claimed:
            # We claimed it!
            self.redis.hset(
                f"deployment:{commit_sha}",
                feature,
                f"{platform}:{datetime.utcnow().isoformat()}"
            )
            return True
        
        # Someone else claimed it
        return False
    
    def get_my_features(
        self, 
        commit_sha: str, 
        all_features: list, 
        platform: str
    ) -> list:
        """
        Determine which features this platform should deploy
        
        Strategy: Each platform tries to claim features in order.
        First to claim wins. This naturally splits the work.
        """
        my_features = []
        
        for feature in all_features:
            if self.claim_deployment(commit_sha, feature, platform):
                my_features.append(feature)
        
        return my_features
    
    def get_deployment_status(self, commit_sha: str) -> dict:
        """Get status of all feature deployments for this commit"""
        return self.redis.hgetall(f"deployment:{commit_sha}")
```

---

## 📋 GitHub Actions with Coordination

```yaml
# .github/workflows/intelligent-deploy.yml
name: Intelligent Deployment

on:
  push:
    branches: [main, develop, qa]

env:
  REDIS_URL: ${{ secrets.DEPLOYMENT_COORDINATOR_REDIS_URL }}
  PLATFORM: github

jobs:
  detect-features:
    runs-on: ubuntu-latest
    outputs:
      features: ${{ steps.detect.outputs.features }}
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 2
      
      - name: Detect changed features
        id: detect
        run: |
          # Detect which features changed
          CHANGED_FILES=$(git diff --name-only HEAD^ HEAD)
          
          FEATURES=()
          if echo "$CHANGED_FILES" | grep -q "^services/auth/"; then
            FEATURES+=("auth-service")
          fi
          if echo "$CHANGED_FILES" | grep -q "^services/trading/"; then
            FEATURES+=("trading-service")
          fi
          if echo "$CHANGED_FILES" | grep -q "^services/analytics/"; then
            FEATURES+=("analytics-service")
          fi
          if echo "$CHANGED_FILES" | grep -q "^frontend/"; then
            FEATURES+=("frontend")
          fi
          
          # Output as JSON array
          echo "features=$(printf '%s\n' "${FEATURES[@]}" | jq -R . | jq -s .)" >> $GITHUB_OUTPUT
  
  claim-features:
    needs: detect-features
    runs-on: ubuntu-latest
    outputs:
      my-features: ${{ steps.claim.outputs.my-features }}
    steps:
      - name: Claim features
        id: claim
        run: |
          # Install Python and dependencies
          pip install redis
          
          # Run coordinator
          python3 << 'EOF'
          import os
          import json
          from deployment_coordinator import DeploymentCoordinator
          
          coordinator = DeploymentCoordinator(os.environ['REDIS_URL'])
          
          commit_sha = os.environ['GITHUB_SHA']
          all_features = json.loads('${{ needs.detect-features.outputs.features }}')
          platform = os.environ['PLATFORM']
          
          # Claim features
          my_features = coordinator.get_my_features(
              commit_sha, 
              all_features, 
              platform
          )
          
          print(f"GitHub claimed: {my_features}")
          
          # Output for next job
          with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
              f.write(f"my-features={json.dumps(my_features)}\n")
          EOF
  
  deploy:
    needs: claim-features
    runs-on: ubuntu-latest
    strategy:
      matrix:
        feature: ${{ fromJson(needs.claim-features.outputs.my-features) }}
    steps:
      - name: Deploy ${{ matrix.feature }}
        run: |
          echo "🚀 GitHub deploying: ${{ matrix.feature }}"
          
          # Deploy based on feature
          case "${{ matrix.feature }}" in
            "auth-service")
              echo "Deploying auth service..."
              # kubectl apply -f k8s/auth-service.yaml
              ;;
            "trading-service")
              echo "Deploying trading service..."
              # kubectl apply -f k8s/trading-service.yaml
              ;;
            "analytics-service")
              echo "Deploying analytics service..."
              # kubectl apply -f k8s/analytics-service.yaml
              ;;
            "frontend")
              echo "Deploying frontend..."
              # kubectl apply -f k8s/frontend.yaml
              ;;
          esac
      
      - name: Notify Linear
        uses: linear/action@v1
        with:
          api-key: ${{ secrets.LINEAR_API_KEY }}
          message: "✅ GitHub deployed ${{ matrix.feature }}"
  
  verify-complete:
    needs: [detect-features, deploy]
    runs-on: ubuntu-latest
    steps:
      - name: Verify all features deployed
        run: |
          pip install redis
          
          python3 << 'EOF'
          import os
          import json
          import time
          from deployment_coordinator import DeploymentCoordinator
          
          coordinator = DeploymentCoordinator(os.environ['REDIS_URL'])
          
          commit_sha = os.environ['GITHUB_SHA']
          all_features = json.loads('${{ needs.detect-features.outputs.features }}')
          
          # Wait up to 10 minutes for all features to be deployed
          timeout = 600
          start = time.time()
          
          while time.time() - start < timeout:
              status = coordinator.get_deployment_status(commit_sha)
              
              deployed = set(status.keys())
              expected = set(all_features)
              
              if deployed == expected:
                  print("✅ All features deployed!")
                  print(f"Status: {status}")
                  break
              
              missing = expected - deployed
              print(f"⏳ Waiting for: {missing}")
              time.sleep(10)
          else:
              print("❌ Timeout waiting for all features")
              exit(1)
          EOF
```

---

## 📋 Bitbucket Pipelines with Coordination

```yaml
# bitbucket-pipelines.yml
image: python:3.11

definitions:
  steps:
    - step: &detect-features
        name: Detect Features
        script:
          - |
            # Detect changed features
            CHANGED_FILES=$(git diff --name-only HEAD^ HEAD)
            
            FEATURES=()
            if echo "$CHANGED_FILES" | grep -q "^services/auth/"; then
              FEATURES+=("auth-service")
            fi
            if echo "$CHANGED_FILES" | grep -q "^services/trading/"; then
              FEATURES+=("trading-service")
            fi
            if echo "$CHANGED_FILES" | grep -q "^services/analytics/"; then
              FEATURES+=("analytics-service")
            fi
            if echo "$CHANGED_FILES" | grep -q "^frontend/"; then
              FEATURES+=("frontend")
            fi
            
            echo "${FEATURES[@]}" > features.txt
        artifacts:
          - features.txt
    
    - step: &claim-features
        name: Claim Features
        script:
          - pip install redis
          - |
            python3 << 'EOF'
            import os
            from deployment_coordinator import DeploymentCoordinator
            
            coordinator = DeploymentCoordinator(os.environ['REDIS_URL'])
            
            commit_sha = os.environ['BITBUCKET_COMMIT']
            
            with open('features.txt') as f:
                all_features = f.read().strip().split()
            
            # Claim features
            my_features = coordinator.get_my_features(
                commit_sha, 
                all_features, 
                'bitbucket'
            )
            
            print(f"Bitbucket claimed: {my_features}")
            
            with open('my-features.txt', 'w') as f:
                f.write('\n'.join(my_features))
            EOF
        artifacts:
          - my-features.txt
    
    - step: &deploy-feature
        name: Deploy Features
        script:
          - |
            while read feature; do
              echo "🚀 Bitbucket deploying: $feature"
              
              case "$feature" in
                "auth-service")
                  echo "Deploying auth service..."
                  # kubectl apply -f k8s/auth-service.yaml
                  ;;
                "trading-service")
                  echo "Deploying trading service..."
                  # kubectl apply -f k8s/trading-service.yaml
                  ;;
                "analytics-service")
                  echo "Deploying analytics service..."
                  # kubectl apply -f k8s/analytics-service.yaml
                  ;;
                "frontend")
                  echo "Deploying frontend..."
                  # kubectl apply -f k8s/frontend.yaml
                  ;;
              esac
              
              # Notify Jira
              curl -X POST $JIRA_WEBHOOK_URL \
                -d "{\"message\":\"✅ Bitbucket deployed $feature\"}"
            done < my-features.txt

pipelines:
  branches:
    main:
      - step: *detect-features
      - step: *claim-features
      - step: *deploy-feature
```

---

## 🎯 How It Works

### **Scenario: Deploy 4 Features**

**Commit includes changes to:**
1. Auth Service
2. Trading Service
3. Analytics Service
4. Frontend

**Timeline:**

```
T+0s: Developer pushes to both repos
    ↓
T+1s: GitHub Actions starts
    - Detects: [auth, trading, analytics, frontend]
    - Claims: auth ✅
    - Claims: trading ✅
    - Bitbucket not started yet, so GitHub gets first pick
    ↓
T+2s: Bitbucket Pipelines starts
    - Detects: [auth, trading, analytics, frontend]
    - Tries auth: ❌ Already claimed by GitHub
    - Tries trading: ❌ Already claimed by GitHub
    - Claims: analytics ✅
    - Claims: frontend ✅
    ↓
T+3s: Both deploy their claimed features in parallel
    - GitHub deploys: auth, trading
    - Bitbucket deploys: analytics, frontend
    ↓
T+5m: All features deployed!
    - GitHub verifies: All 4 features deployed ✅
    - Bitbucket verifies: All 4 features deployed ✅
```

**Result:** Work split automatically, no duplication! 🎉

---

## 🔄 Alternative Strategy: Feature Assignment

If you want more control, assign features to platforms:

```yaml
# .akashic/deployment-config.yml
deployment_strategy: assigned

feature_assignments:
  github:
    - auth-service
    - trading-service
    - data-pipeline
  
  bitbucket:
    - analytics-service
    - frontend
    - reporting

# Both platforms deploy to same cloud
cloud_provider: aws
kubernetes_cluster: production-cluster
namespace: production
```

**GitHub only deploys its assigned features:**
```yaml
- name: Check if my feature
  run: |
    if grep -q "${{ matrix.feature }}" .akashic/deployment-config.yml | grep -A 10 "github:"; then
      echo "MY_FEATURE=true" >> $GITHUB_ENV
    fi

- name: Deploy
  if: env.MY_FEATURE == 'true'
  run: kubectl apply -f k8s/${{ matrix.feature }}.yaml
```

---

## 📊 Deployment Coordinator Dashboard

```python
# dashboard.py
from flask import Flask, jsonify
from deployment_coordinator import DeploymentCoordinator

app = Flask(__name__)
coordinator = DeploymentCoordinator(REDIS_URL)

@app.route('/deployments/<commit_sha>')
def get_deployment_status(commit_sha):
    """Get real-time deployment status"""
    status = coordinator.get_deployment_status(commit_sha)
    
    return jsonify({
        'commit': commit_sha,
        'features': status,
        'complete': len(status) == expected_features,
        'github_deployed': [
            f for f, p in status.items() 
            if p.startswith('github:')
        ],
        'bitbucket_deployed': [
            f for f, p in status.items() 
            if p.startswith('bitbucket:')
        ]
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})
```

**View in browser:**
```
http://deployment-coordinator.internal/deployments/abc123

{
  "commit": "abc123",
  "complete": true,
  "github_deployed": ["auth-service", "trading-service"],
  "bitbucket_deployed": ["analytics-service", "frontend"],
  "features": {
    "auth-service": "github:2025-11-01T15:30:00",
    "trading-service": "github:2025-11-01T15:30:05",
    "analytics-service": "bitbucket:2025-11-01T15:30:10",
    "frontend": "bitbucket:2025-11-01T15:30:15"
  }
}
```

---

## ✅ Benefits

### **Smart Work Splitting:**
- ✅ No duplicate deployments
- ✅ Automatic load balancing
- ✅ Faster overall deployment (parallel)
- ✅ Same cloud resources
- ✅ No conflicts

### **Redundancy:**
- ✅ If GitHub fails, Bitbucket can claim all features
- ✅ If Bitbucket fails, GitHub can claim all features
- ✅ Automatic failover

### **Visibility:**
- ✅ Real-time dashboard
- ✅ Know which platform deployed what
- ✅ Track deployment progress
- ✅ Verify completion

---

## 🚀 Quick Start

### **1. Setup Redis Coordinator:**
```bash
# Deploy Redis
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: deployment-coordinator
spec:
  ports:
  - port: 6379
  selector:
    app: redis
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
EOF
```

### **2. Configure Git:**
```bash
git remote add all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@bitbucket.org:colossalcapital/project.git
```

### **3. Add Secrets:**
```bash
# GitHub
gh secret set DEPLOYMENT_COORDINATOR_REDIS_URL

# Bitbucket (via UI)
# Add REDIS_URL variable
```

### **4. Push:**
```bash
git push all main
# Both pipelines run, work splits automatically!
```

---

## 🎉 Result

**One commit → Two repos → Smart splitting → Same cloud → No duplication!**

Perfect! 🚀
