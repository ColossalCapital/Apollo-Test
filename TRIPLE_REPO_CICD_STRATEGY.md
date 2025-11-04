# 🚀 Triple Repository CI/CD Strategy

## 🎯 Vision: GitHub + Bitbucket + GitLab (Cloud & Self-Hosted)

Complete multi-platform redundancy with intelligent deployment coordination.

**Platforms:**
- ✅ GitHub (Primary) → Linear
- ✅ Bitbucket (Mirror) → Jira
- ✅ GitLab Cloud (Mirror) → GitLab Issues
- ✅ GitLab Self-Hosted (Juju Charms) → GitLab Issues

---

## 🏗️ Architecture

```
Developer Commits
    ↓
Git Push (all repos simultaneously)
    ├─ GitHub (Primary)
    │   ├─ GitHub Actions CI/CD
    │   ├─ Linear Integration
    │   └─ Claims: Features A, B
    │
    ├─ Bitbucket (Mirror)
    │   ├─ Bitbucket Pipelines CI/CD
    │   ├─ Jira Integration
    │   └─ Claims: Feature C
    │
    ├─ GitLab Cloud (Mirror)
    │   ├─ GitLab CI/CD
    │   ├─ GitLab Issues
    │   └─ Claims: Feature D
    │
    └─ GitLab Self-Hosted (Juju Charms)
        ├─ GitLab CI/CD
        ├─ GitLab Issues
        ├─ On-premise deployment
        └─ Claims: Feature E

Result: All features deployed, no duplication! ✅
```

---

## 📋 Git Configuration

### **Setup All Remotes:**

```bash
# Add all remotes
git remote add github git@github.com:ColossalCapital/project.git
git remote add bitbucket git@bitbucket.org:colossalcapital/project.git
git remote add gitlab git@gitlab.com:colossalcapital/project.git
git remote add gitlab-self git@gitlab.internal.colossalcapital.com:colossalcapital/project.git

# Create "all" remote that pushes to all platforms
git remote add all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@bitbucket.org:colossalcapital/project.git
git remote set-url --add --push all git@gitlab.com:colossalcapital/project.git
git remote set-url --add --push all git@gitlab.internal.colossalcapital.com:colossalcapital/project.git

# Now push to all 4 platforms at once!
git push all main
```

### **Git Aliases:**

```bash
# Add to ~/.gitconfig
[alias]
    pushall = !git push github && git push bitbucket && git push gitlab && git push gitlab-self
    pullall = !git pull github && git pull bitbucket && git pull gitlab && git pull gitlab-self
    syncall = !git push all --all && git push all --tags
    status-all = !git remote -v | grep -E '(github|bitbucket|gitlab)'
```

---

## 🔧 GitLab CI/CD Configuration

### **File: `.gitlab-ci.yml`**

```yaml
# GitLab CI/CD Pipeline
# Works for both GitLab Cloud and Self-Hosted

stages:
  - sync
  - test
  - lint
  - security
  - deploy

variables:
  REDIS_URL: $DEPLOYMENT_COORDINATOR_REDIS_URL
  PLATFORM: gitlab

# Sync to other platforms (optional for cloud)
sync-repos:
  stage: sync
  only:
    - main
    - develop
    - qa
  script:
    - |
      # Only run on GitLab Cloud (not self-hosted)
      if [ "$CI_SERVER_HOST" = "gitlab.com" ]; then
        git remote add github https://oauth2:$GITHUB_TOKEN@github.com/ColossalCapital/$CI_PROJECT_NAME.git || true
        git remote add bitbucket https://x-token-auth:$BITBUCKET_TOKEN@bitbucket.org/colossalcapital/$CI_PROJECT_NAME.git || true
        git push github $CI_COMMIT_REF_NAME || true
        git push bitbucket $CI_COMMIT_REF_NAME || true
      fi

# Detect changed features
detect-features:
  stage: test
  script:
    - |
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
      
      # Save to artifacts
      echo "${FEATURES[@]}" > features.txt
  artifacts:
    paths:
      - features.txt

# Claim features via Redis coordinator
claim-features:
  stage: test
  needs: [detect-features]
  script:
    - pip install redis
    - |
      python3 << 'EOF'
      import os
      from deployment_coordinator import DeploymentCoordinator
      
      coordinator = DeploymentCoordinator(os.environ['REDIS_URL'])
      
      commit_sha = os.environ['CI_COMMIT_SHA']
      
      with open('features.txt') as f:
          all_features = f.read().strip().split()
      
      # Determine platform
      if 'gitlab.com' in os.environ.get('CI_SERVER_HOST', ''):
          platform = 'gitlab-cloud'
      else:
          platform = 'gitlab-self'
      
      # Claim features
      my_features = coordinator.get_my_features(
          commit_sha, 
          all_features, 
          platform
      )
      
      print(f"{platform} claimed: {my_features}")
      
      with open('my-features.txt', 'w') as f:
          f.write('\n'.join(my_features))
      EOF
  artifacts:
    paths:
      - my-features.txt

# Run tests
test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=. --cov-report=xml
    - coverage report --fail-under=80
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

# Lint code
lint:
  stage: lint
  script:
    - pip install flake8 black mypy
    - flake8 .
    - black --check .
    - mypy .

# Security scan
security:
  stage: security
  script:
    - pip install safety bandit
    - safety check
    - bandit -r . -f json -o bandit-report.json
  artifacts:
    reports:
      sast: bandit-report.json

# Deploy to Dev
deploy-dev:
  stage: deploy
  needs: [test, lint, security, claim-features]
  only:
    - develop
  environment:
    name: development
  script:
    - |
      while read feature; do
        echo "🚀 GitLab deploying: $feature"
        
        # Determine deployment target
        if [ "$CI_SERVER_HOST" = "gitlab.com" ]; then
          # GitLab Cloud → Deploy to cloud
          echo "Deploying to cloud..."
          # kubectl apply -f k8s/$feature.yaml
        else
          # GitLab Self-Hosted → Deploy to Juju Charms
          echo "Deploying to Juju Charms..."
          # juju deploy ./$feature --to lxd:0
        fi
        
        # Notify GitLab Issues
        curl -X POST "$CI_API_V4_URL/projects/$CI_PROJECT_ID/issues" \
          -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
          -d "title=Deployed $feature to dev" \
          -d "description=Deployed from GitLab CI/CD"
      done < my-features.txt

# Deploy to QA
deploy-qa:
  stage: deploy
  needs: [test, lint, security, claim-features]
  only:
    - qa
  environment:
    name: staging
  script:
    - |
      while read feature; do
        echo "🚀 GitLab deploying to QA: $feature"
        
        if [ "$CI_SERVER_HOST" = "gitlab.com" ]; then
          echo "Deploying to cloud QA..."
          # kubectl apply -f k8s/$feature.yaml --namespace=qa
        else
          echo "Deploying to Juju Charms QA..."
          # juju deploy ./$feature --to lxd:1
        fi
      done < my-features.txt

# Deploy to Production
deploy-prod:
  stage: deploy
  needs: [test, lint, security, claim-features]
  only:
    - main
  environment:
    name: production
  when: manual  # Require manual approval
  script:
    - |
      while read feature; do
        echo "🚀 GitLab deploying to PRODUCTION: $feature"
        
        if [ "$CI_SERVER_HOST" = "gitlab.com" ]; then
          echo "Deploying to cloud production..."
          # kubectl apply -f k8s/$feature.yaml --namespace=production
        else
          echo "Deploying to Juju Charms production..."
          # juju deploy ./$feature --to lxd:2
        fi
        
        # Notify GitLab Issues
        curl -X POST "$CI_API_V4_URL/projects/$CI_PROJECT_ID/issues" \
          -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
          -d "title=🚀 Deployed $feature to production" \
          -d "description=Deployed from GitLab CI/CD"
      done < my-features.txt
```

---

## 🎯 Juju Charms Integration

### **Why Juju Charms for Self-Hosted?**

**Benefits:**
- Declarative infrastructure
- Automatic scaling
- Built-in monitoring
- Easy updates
- Multi-cloud support

### **Charm Deployment:**

```bash
# Deploy microservices as Juju charms
juju deploy ./auth-service --to lxd:0
juju deploy ./trading-service --to lxd:1
juju deploy ./analytics-service --to lxd:2
juju deploy ./frontend --to lxd:3

# Add relations
juju relate auth-service postgresql
juju relate trading-service redis
juju relate analytics-service kafka

# Scale
juju scale-application trading-service 3

# Monitor
juju status
```

### **Charm Structure:**

```
charms/
├── auth-service/
│   ├── charmcraft.yaml
│   ├── src/
│   │   └── charm.py
│   └── metadata.yaml
├── trading-service/
│   ├── charmcraft.yaml
│   ├── src/
│   │   └── charm.py
│   └── metadata.yaml
└── ...
```

### **Example Charm (auth-service):**

```yaml
# charmcraft.yaml
name: auth-service
summary: Authentication service
description: |
  JWT-based authentication service
  with OAuth2 support

bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
    run-on:
      - name: ubuntu
        channel: "22.04"

parts:
  charm:
    plugin: python
    source: .
    python-packages:
      - fastapi
      - pyjwt
      - sqlalchemy
```

```python
# src/charm.py
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

class AuthServiceCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
    
    def _on_start(self, event):
        # Start the service
        self.unit.status = ActiveStatus("Auth service running")
    
    def _on_config_changed(self, event):
        # Handle configuration changes
        pass

if __name__ == "__main__":
    main(AuthServiceCharm)
```

---

## 🔄 Deployment Coordinator (Enhanced)

### **Support for 4 Platforms:**

```python
# deployment_coordinator.py (enhanced)
class DeploymentCoordinator:
    """
    Coordinates deployments across 4 platforms:
    - GitHub
    - Bitbucket
    - GitLab Cloud
    - GitLab Self-Hosted
    """
    
    PLATFORMS = ['github', 'bitbucket', 'gitlab-cloud', 'gitlab-self']
    
    def get_my_features(
        self, 
        commit_sha: str, 
        all_features: list, 
        platform: str
    ) -> list:
        """
        Determine which features this platform should deploy
        
        Priority order:
        1. GitLab Self-Hosted (on-premise, highest priority)
        2. GitHub (primary)
        3. Bitbucket (mirror)
        4. GitLab Cloud (mirror)
        """
        my_features = []
        
        # GitLab Self-Hosted gets first pick
        if platform == 'gitlab-self':
            priority = 0
        elif platform == 'github':
            priority = 1
        elif platform == 'bitbucket':
            priority = 2
        else:  # gitlab-cloud
            priority = 3
        
        for feature in all_features:
            if self.claim_deployment(commit_sha, feature, platform):
                my_features.append(feature)
        
        return my_features
```

---

## 📊 Deployment Dashboard

### **Real-Time Monitoring:**

```python
# dashboard.py (enhanced)
@app.route('/deployments/<commit_sha>')
def get_deployment_status(commit_sha):
    """Get deployment status across all 4 platforms"""
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
        ],
        'gitlab_cloud_deployed': [
            f for f, p in status.items() 
            if p.startswith('gitlab-cloud:')
        ],
        'gitlab_self_deployed': [
            f for f, p in status.items() 
            if p.startswith('gitlab-self:')
        ]
    })
```

**Example Response:**
```json
{
  "commit": "abc123",
  "complete": true,
  "github_deployed": ["auth-service"],
  "bitbucket_deployed": ["trading-service"],
  "gitlab_cloud_deployed": ["analytics-service"],
  "gitlab_self_deployed": ["frontend"],
  "features": {
    "auth-service": "github:2025-11-01T12:00:00",
    "trading-service": "bitbucket:2025-11-01T12:00:05",
    "analytics-service": "gitlab-cloud:2025-11-01T12:00:10",
    "frontend": "gitlab-self:2025-11-01T12:00:15"
  }
}
```

---

## 🎯 Platform-Specific Features

### **GitHub:**
- ✅ GitHub Actions (most mature)
- ✅ Linear integration
- ✅ Dependabot
- ✅ Code scanning
- ✅ Large community

### **Bitbucket:**
- ✅ Bitbucket Pipelines
- ✅ Jira integration (native)
- ✅ Atlassian ecosystem
- ✅ Enterprise features

### **GitLab Cloud:**
- ✅ GitLab CI/CD (powerful)
- ✅ Built-in container registry
- ✅ Built-in package registry
- ✅ GitLab Issues
- ✅ Auto DevOps

### **GitLab Self-Hosted:**
- ✅ On-premise deployment
- ✅ Full control
- ✅ Juju Charms integration
- ✅ Air-gapped support
- ✅ Custom runners
- ✅ Enterprise security

---

## 🔐 Secrets Management

### **GitHub Secrets:**
```
BITBUCKET_TOKEN
GITLAB_TOKEN
GITLAB_SELF_TOKEN
LINEAR_API_KEY
DEPLOYMENT_COORDINATOR_REDIS_URL
```

### **Bitbucket Variables:**
```
GITHUB_TOKEN
GITLAB_TOKEN
GITLAB_SELF_TOKEN
JIRA_API_TOKEN
DEPLOYMENT_COORDINATOR_REDIS_URL
```

### **GitLab Cloud Variables:**
```
GITHUB_TOKEN
BITBUCKET_TOKEN
GITLAB_SELF_TOKEN
DEPLOYMENT_COORDINATOR_REDIS_URL
```

### **GitLab Self-Hosted Variables:**
```
GITHUB_TOKEN
BITBUCKET_TOKEN
GITLAB_CLOUD_TOKEN
DEPLOYMENT_COORDINATOR_REDIS_URL
JUJU_CONTROLLER
JUJU_MODEL
```

---

## 🚀 Quick Start

### **1. Setup All Repositories:**

```bash
# Create repos on all platforms
# GitHub: https://github.com/ColossalCapital/project
# Bitbucket: https://bitbucket.org/colossalcapital/project
# GitLab Cloud: https://gitlab.com/colossalcapital/project
# GitLab Self-Hosted: https://gitlab.internal.colossalcapital.com/colossalcapital/project

# Add all remotes
git remote add github git@github.com:ColossalCapital/project.git
git remote add bitbucket git@bitbucket.org:colossalcapital/project.git
git remote add gitlab git@gitlab.com:colossalcapital/project.git
git remote add gitlab-self git@gitlab.internal.colossalcapital.com:colossalcapital/project.git

# Setup push to all
git remote add all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@github.com:ColossalCapital/project.git
git remote set-url --add --push all git@bitbucket.org:colossalcapital/project.git
git remote set-url --add --push all git@gitlab.com:colossalcapital/project.git
git remote set-url --add --push all git@gitlab.internal.colossalcapital.com:colossalcapital/project.git

# Push to all platforms
git push all main
```

### **2. Configure CI/CD:**

```bash
# Copy pipeline configs
cp .akashic/pipelines/github/* .github/workflows/
cp .akashic/pipelines/bitbucket/bitbucket-pipelines.yml .
cp .akashic/pipelines/gitlab/.gitlab-ci.yml .

# Configure secrets on each platform
```

### **3. Deploy Redis Coordinator:**

```bash
# Deploy to Kubernetes or Docker
kubectl apply -f k8s/redis-coordinator.yaml

# Or Docker Compose
docker-compose up -d redis
```

### **4. Setup Juju (for self-hosted):**

```bash
# Install Juju
sudo snap install juju --classic

# Bootstrap controller
juju bootstrap localhost lxd-controller

# Add model
juju add-model production

# Deploy charms
juju deploy ./charms/auth-service
juju deploy ./charms/trading-service
```

### **5. Push and Deploy:**

```bash
# Make changes
git add .
git commit -m "Add new feature"

# Push to all platforms
git push all main

# All 4 CI/CD pipelines run
# Work is automatically split
# All features deployed!
```

---

## 📈 Benefits Summary

### **Redundancy:**
- ✅ 4 independent CI/CD systems
- ✅ No single point of failure
- ✅ Automatic failover
- ✅ Geographic distribution

### **Flexibility:**
- ✅ GitHub for open source
- ✅ Bitbucket for enterprise
- ✅ GitLab Cloud for DevOps
- ✅ GitLab Self-Hosted for on-premise

### **Integration:**
- ✅ GitHub → Linear
- ✅ Bitbucket → Jira
- ✅ GitLab → GitLab Issues
- ✅ All platforms → Same cloud

### **Performance:**
- ✅ Parallel deployments
- ✅ Smart work splitting
- ✅ No duplicate work
- ✅ Faster overall deployment

### **Security:**
- ✅ On-premise option (GitLab Self-Hosted)
- ✅ Air-gapped deployment
- ✅ Full control
- ✅ Enterprise compliance

---

## 🎯 Use Cases

### **Startup Phase:**
- GitHub (primary)
- GitLab Cloud (backup)
- Fast iteration

### **Growth Phase:**
- GitHub + Bitbucket
- Linear + Jira
- Team flexibility

### **Enterprise Phase:**
- All 4 platforms
- GitLab Self-Hosted (on-premise)
- Juju Charms deployment
- Full redundancy

### **Platform Launch:**
- GitLab Self-Hosted (Juju Charms)
- On-premise deployment
- Full control
- Enterprise security

---

## ✅ Success Criteria

**Multi-Platform Setup Complete When:**
- ✅ All 4 repos exist and sync
- ✅ All 4 CI/CD pipelines working
- ✅ Redis coordinator deployed
- ✅ Smart work splitting active
- ✅ PM integrations working
- ✅ Juju Charms ready (for self-hosted)
- ✅ All deploy to same cloud
- ✅ No duplicate deployments

**Result:** Ultimate redundancy and flexibility! 🎉

---

## 🔮 Future Enhancements

### **Additional Platforms:**
- Azure DevOps
- AWS CodePipeline
- Google Cloud Build
- Jenkins (self-hosted)

### **Advanced Features:**
- Canary deployments
- Blue-green deployments
- A/B testing
- Feature flags
- Rollback automation

### **Monitoring:**
- Deployment metrics
- Performance tracking
- Error rate monitoring
- Cost optimization

---

## 💬 Quick Commands

```bash
# Push to all platforms
git push all main

# Check status on all platforms
git status-all

# Pull from all platforms
git pullall

# Sync everything
git syncall

# Deploy to Juju
juju deploy ./auth-service

# Check Juju status
juju status

# Scale service
juju scale-application auth-service 3
```

---

## 🎉 The Ultimate CI/CD Setup!

**One commit → Four platforms → Smart coordination → Same cloud → No duplication!**

Perfect for launching the platform with Juju Charms! 🚀
