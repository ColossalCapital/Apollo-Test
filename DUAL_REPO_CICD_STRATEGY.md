# Dual Repository CI/CD Strategy

## 🎯 Vision: GitHub + Bitbucket Redundancy

Just like we use both Linear AND Jira for project management, we'll use both GitHub AND Bitbucket for code versioning and CI/CD.

**Benefits:**
- ✅ Redundancy - No single point of failure
- ✅ Flexibility - Use best features from each
- ✅ Backup - Always have a mirror
- ✅ Team Choice - Developers can use preferred platform
- ✅ Integration Options - More PM/tool integrations

---

## 🏗️ Architecture

### **Primary Repository: GitHub**
- Main development workflow
- PR reviews and discussions
- GitHub Actions CI/CD
- Integration with Linear
- Public/private repo options

### **Mirror Repository: Bitbucket**
- Automatic sync from GitHub
- Bitbucket Pipelines CI/CD
- Integration with Jira
- Atlassian ecosystem integration
- Enterprise features

### **Sync Strategy:**
```
Developer → GitHub (primary)
    ↓
Auto-sync → Bitbucket (mirror)
    ↓
Both run CI/CD pipelines
    ↓
Deploy to same environments
```

---

## 📋 Implementation Plan

### **Phase 1: Repository Setup**

#### **1.1 GitHub Repository**
```bash
# Initialize GitHub repo (if not exists)
git remote add github git@github.com:ColossalCapital/project-name.git
git push github main
```

#### **1.2 Bitbucket Repository**
```bash
# Add Bitbucket as second remote
git remote add bitbucket git@bitbucket.org:colossalcapital/project-name.git
git push bitbucket main
```

#### **1.3 Automatic Sync**
```bash
# Push to both remotes
git remote add all git@github.com:ColossalCapital/project-name.git
git remote set-url --add --push all git@github.com:ColossalCapital/project-name.git
git remote set-url --add --push all git@bitbucket.org:colossalcapital/project-name.git

# Now 'git push all' pushes to both!
git push all main
```

---

### **Phase 2: CI/CD Pipeline Generation**

Apollo will generate BOTH pipeline configurations:

```python
async def _generate_cicd_pipelines(self, repo_path: str, analysis: Dict) -> Dict:
    """
    Generate CI/CD pipelines for BOTH GitHub and Bitbucket
    """
    results = {
        'github': self._generate_github_actions(repo_path, analysis),
        'bitbucket': self._generate_bitbucket_pipelines(repo_path, analysis),
        'sync_strategy': 'dual_primary',
        'environments': ['dev', 'qa', 'prod']
    }
    
    return results
```

---

## 🔧 GitHub Actions Configuration

### **File: `.github/workflows/ci-cd.yml`**

```yaml
name: CI/CD Pipeline (GitHub)

on:
  push:
    branches: [develop, qa, main]
  pull_request:
    branches: [develop, qa, main]

env:
  SYNC_TO_BITBUCKET: true

jobs:
  # Sync to Bitbucket first
  sync-bitbucket:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Sync to Bitbucket
        run: |
          git remote add bitbucket https://x-token-auth:${{ secrets.BITBUCKET_TOKEN }}@bitbucket.org/colossalcapital/${{ github.event.repository.name }}.git
          git push bitbucket ${{ github.ref }}
  
  # Run tests
  test:
    runs-on: ubuntu-latest
    needs: sync-bitbucket
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml
      
      - name: Check coverage
        run: |
          coverage report --fail-under=80
      
      - name: Upload to Codecov
        uses: codecov/codecov-action@v3
  
  # Lint code
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run linting
        run: |
          pip install flake8 black mypy
          flake8 .
          black --check .
          mypy .
  
  # Security scan
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run security scan
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  
  # Deploy to Dev
  deploy-dev:
    needs: [test, lint, security]
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: development
    steps:
      - name: Deploy to Dev
        run: |
          echo "Deploying to dev environment..."
          # Deployment commands
      
      - name: Notify Linear
        uses: linear/action@v1
        with:
          api-key: ${{ secrets.LINEAR_API_KEY }}
          message: "Deployed to dev from GitHub Actions"
  
  # Deploy to QA
  deploy-qa:
    needs: [test, lint, security]
    if: github.ref == 'refs/heads/qa'
    runs-on: ubuntu-latest
    environment: qa
    steps:
      - name: Deploy to QA
        run: |
          echo "Deploying to QA environment..."
          # Deployment commands
      
      - name: Notify Linear
        uses: linear/action@v1
        with:
          api-key: ${{ secrets.LINEAR_API_KEY }}
          message: "Deployed to QA from GitHub Actions"
  
  # Deploy to Production
  deploy-prod:
    needs: [test, lint, security]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Production
        run: |
          echo "Deploying to production..."
          # Deployment commands
      
      - name: Notify Linear
        uses: linear/action@v1
        with:
          api-key: ${{ secrets.LINEAR_API_KEY }}
          message: "🚀 Deployed to production from GitHub Actions"
      
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ github.run_number }}
          release_name: Release v${{ github.run_number }}
```

---

## 🔧 Bitbucket Pipelines Configuration

### **File: `bitbucket-pipelines.yml`**

```yaml
image: python:3.11

definitions:
  steps:
    - step: &test
        name: Test
        caches:
          - pip
        script:
          - pip install -r requirements.txt
          - pip install pytest pytest-cov
          - pytest --cov=. --cov-report=xml
          - coverage report --fail-under=80
        artifacts:
          - coverage.xml
    
    - step: &lint
        name: Lint
        script:
          - pip install flake8 black mypy
          - flake8 .
          - black --check .
          - mypy .
    
    - step: &security
        name: Security Scan
        script:
          - pip install safety bandit
          - safety check
          - bandit -r . -f json -o bandit-report.json
    
    - step: &deploy-dev
        name: Deploy to Dev
        deployment: development
        script:
          - echo "Deploying to dev environment..."
          # Deployment commands
          - curl -X POST $JIRA_WEBHOOK_URL -d '{"message":"Deployed to dev from Bitbucket"}'
    
    - step: &deploy-qa
        name: Deploy to QA
        deployment: staging
        script:
          - echo "Deploying to QA environment..."
          # Deployment commands
          - curl -X POST $JIRA_WEBHOOK_URL -d '{"message":"Deployed to QA from Bitbucket"}'
    
    - step: &deploy-prod
        name: Deploy to Production
        deployment: production
        trigger: manual
        script:
          - echo "Deploying to production..."
          # Deployment commands
          - curl -X POST $JIRA_WEBHOOK_URL -d '{"message":"🚀 Deployed to production from Bitbucket"}'

pipelines:
  branches:
    develop:
      - parallel:
          - step: *test
          - step: *lint
          - step: *security
      - step: *deploy-dev
    
    qa:
      - parallel:
          - step: *test
          - step: *lint
          - step: *security
      - step: *deploy-qa
    
    main:
      - parallel:
          - step: *test
          - step: *lint
          - step: *security
      - step: *deploy-prod
  
  pull-requests:
    '**':
      - parallel:
          - step: *test
          - step: *lint
          - step: *security
```

---

## 🔄 Automatic Sync Strategy

### **Option 1: GitHub → Bitbucket (Recommended)**

**GitHub Action to sync:**
```yaml
# .github/workflows/sync-to-bitbucket.yml
name: Sync to Bitbucket

on:
  push:
    branches: ['**']

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Sync to Bitbucket
        run: |
          git remote add bitbucket https://x-token-auth:${{ secrets.BITBUCKET_TOKEN }}@bitbucket.org/colossalcapital/${{ github.event.repository.name }}.git
          git push bitbucket --all
          git push bitbucket --tags
```

### **Option 2: Bidirectional Sync**

**For true dual-primary setup:**
```yaml
# GitHub Action
name: Bidirectional Sync

on:
  push:
    branches: ['**']

jobs:
  sync-to-bitbucket:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Push to Bitbucket
        run: |
          git remote add bitbucket https://x-token-auth:${{ secrets.BITBUCKET_TOKEN }}@bitbucket.org/colossalcapital/${{ github.event.repository.name }}.git
          git push bitbucket ${{ github.ref }}
```

**Bitbucket Webhook:**
```yaml
# bitbucket-pipelines.yml
pipelines:
  custom:
    sync-to-github:
      - step:
          name: Sync to GitHub
          script:
            - git remote add github https://$GITHUB_TOKEN@github.com/ColossalCapital/$BITBUCKET_REPO_SLUG.git
            - git push github $BITBUCKET_BRANCH
```

---

## 📊 PM Integration

### **GitHub → Linear**

```yaml
# .github/workflows/linear-integration.yml
name: Linear Integration

on:
  pull_request:
    types: [opened, closed]
  issues:
    types: [opened, closed]

jobs:
  sync-linear:
    runs-on: ubuntu-latest
    steps:
      - name: Sync to Linear
        uses: linear/action@v1
        with:
          api-key: ${{ secrets.LINEAR_API_KEY }}
          event: ${{ github.event_name }}
```

### **Bitbucket → Jira**

```yaml
# bitbucket-pipelines.yml
pipelines:
  custom:
    jira-sync:
      - step:
          name: Sync to Jira
          script:
            - curl -X POST https://your-domain.atlassian.net/rest/api/3/issue \
              -H "Authorization: Bearer $JIRA_API_TOKEN" \
              -H "Content-Type: application/json" \
              -d @jira-issue.json
```

---

## 🎯 Deployment Strategy

### **Multi-Environment Setup:**

```
┌─────────────────────────────────────────┐
│         Developer Commits               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         GitHub (Primary)                │
│  - PR Review                            │
│  - GitHub Actions CI/CD                 │
│  - Linear Integration                   │
└──────────────┬──────────────────────────┘
               │
               │ Auto-sync
               ▼
┌─────────────────────────────────────────┐
│         Bitbucket (Mirror)              │
│  - Bitbucket Pipelines CI/CD            │
│  - Jira Integration                     │
│  - Atlassian Tools                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Environments                    │
│  - Dev (auto-deploy from develop)      │
│  - QA (auto-deploy from qa)            │
│  - Prod (manual approval from main)    │
└─────────────────────────────────────────┘
```

---

## 🔐 Secrets Management

### **GitHub Secrets:**
```
BITBUCKET_TOKEN       # For syncing to Bitbucket
LINEAR_API_KEY        # For Linear integration
SNYK_TOKEN           # For security scanning
DEPLOY_KEY_DEV       # Dev environment
DEPLOY_KEY_QA        # QA environment
DEPLOY_KEY_PROD      # Prod environment
```

### **Bitbucket Variables:**
```
GITHUB_TOKEN         # For syncing to GitHub
JIRA_API_TOKEN       # For Jira integration
JIRA_WEBHOOK_URL     # For notifications
DEPLOY_KEY_DEV       # Dev environment
DEPLOY_KEY_QA        # QA environment
DEPLOY_KEY_PROD      # Prod environment
```

---

## 📋 Apollo Implementation

### **Pipeline Generator Function:**

```python
async def _generate_dual_cicd_pipelines(
    self, 
    repo_path: str, 
    analysis: Dict
) -> Dict:
    """
    Generate CI/CD pipelines for BOTH GitHub and Bitbucket
    """
    
    # Detect project type
    project_type = self._detect_project_type(repo_path)
    test_framework = self._detect_test_framework(repo_path)
    
    results = {
        'github': {
            'workflows': [],
            'secrets_needed': [],
            'integrations': ['linear']
        },
        'bitbucket': {
            'pipelines': [],
            'variables_needed': [],
            'integrations': ['jira']
        },
        'sync_strategy': 'github_to_bitbucket',
        'environments': ['dev', 'qa', 'prod']
    }
    
    # Generate GitHub Actions
    github_workflows = self._generate_github_workflows(
        project_type, 
        test_framework,
        analysis
    )
    results['github']['workflows'] = github_workflows
    
    # Generate Bitbucket Pipelines
    bitbucket_pipelines = self._generate_bitbucket_pipeline(
        project_type,
        test_framework,
        analysis
    )
    results['bitbucket']['pipelines'] = bitbucket_pipelines
    
    # Generate sync configuration
    sync_config = self._generate_sync_config()
    results['sync_config'] = sync_config
    
    return results
```

---

## 📁 Output Structure

After analysis, Apollo generates:

```
.akashic/
├── pipelines/
│   ├── github/
│   │   ├── ci-cd.yml
│   │   ├── sync-to-bitbucket.yml
│   │   ├── linear-integration.yml
│   │   └── README.md
│   ├── bitbucket/
│   │   ├── bitbucket-pipelines.yml
│   │   ├── jira-integration.yml
│   │   └── README.md
│   └── DEPLOYMENT_GUIDE.md
├── pm/
│   ├── linear/
│   │   └── tickets.json
│   └── jira/
│       └── issues.json
└── docs/
    └── DUAL_REPO_STRATEGY.md
```

---

## ✅ Benefits Summary

### **Redundancy:**
- ✅ Two independent CI/CD systems
- ✅ No single point of failure
- ✅ Automatic backup

### **Flexibility:**
- ✅ Use GitHub for open source
- ✅ Use Bitbucket for enterprise
- ✅ Team can choose preferred platform

### **Integration:**
- ✅ GitHub → Linear (modern PM)
- ✅ Bitbucket → Jira (enterprise PM)
- ✅ Best of both worlds

### **Features:**
- ✅ GitHub Actions (powerful, flexible)
- ✅ Bitbucket Pipelines (Atlassian integration)
- ✅ Both run same tests
- ✅ Both deploy to same environments

---

## 🚀 Quick Start

### **1. Setup Repositories:**
```bash
# Add both remotes
git remote add github git@github.com:ColossalCapital/project.git
git remote add bitbucket git@bitbucket.org:colossalcapital/project.git

# Push to both
git push github main
git push bitbucket main
```

### **2. Generate Pipelines:**
```bash
# In Akashic IDE:
1. Load codebase
2. Click "Analyze Folder"
3. Check .akashic/pipelines/
```

### **3. Configure Secrets:**
```bash
# GitHub
gh secret set BITBUCKET_TOKEN
gh secret set LINEAR_API_KEY

# Bitbucket
# Use Bitbucket UI to add variables
```

### **4. Deploy:**
```bash
# Push to trigger both pipelines
git push github main
# Auto-syncs to Bitbucket
# Both pipelines run
# Both deploy to prod
```

---

## 🎯 Success Criteria

**Dual Repository Setup Complete When:**
- ✅ Both GitHub and Bitbucket repos exist
- ✅ Auto-sync configured
- ✅ GitHub Actions pipeline working
- ✅ Bitbucket Pipelines working
- ✅ Linear integration active
- ✅ Jira integration active
- ✅ Both deploy to same environments
- ✅ Team can use either platform

**Result:** Redundant, flexible, integrated CI/CD system! 🎉
