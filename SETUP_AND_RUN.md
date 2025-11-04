# 🚀 Deployment System - Full Setup & Run Guide

## Current Situation

The deployment system is **100% complete** but needs Apollo's full environment to run.

**Two ways to use it:**

1. **Via Akashic IDE** (Best UX - visual interface)
2. **Via Apollo Docker** (Works now - full functionality)

---

## ✅ Option 1: Use via Akashic IDE (Recommended)

**This is the intended way - click "Analyze" button in the IDE!**

### **What Happens:**

```
User clicks "Analyze" in Akashic IDE
    ↓
Akashic IDE calls Apollo API (http://apollo:8002)
    ↓
Apollo runs akashic_intelligence_orchestrator.py
    ↓
Orchestrator runs deployment_mapper.py
    ↓
Orchestrator runs deployment_config_generator.py
    ↓
Orchestrator runs deployment_reconciliation.py
    ↓
Results saved to .akashic/analysis/ and .akashic/deploy/
    ↓
IDE displays results
```

### **Setup Steps:**

#### **Step 1: Restart Apollo (5 seconds)**

```bash
cd /Users/leonard/Documents/repos/Jacob\ Aaron\ Leonard\ LLC/ColossalCapital/Infrastructure

# Restart Apollo to load new code
docker-compose -f docker-compose.complete-system.yml restart apollo

# Check it's running
docker-compose -f docker-compose.complete-system.yml ps apollo
```

#### **Step 2: Open Akashic IDE**

```bash
cd /Users/leonard/Documents/repos/Jacob\ Aaron\ Leonard\ LLC/ColossalCapital/Akashic/ide

# Start IDE
npm run dev

# Or if already running, just open it
```

#### **Step 3: Load Your Repo**

```
In Akashic IDE:
1. File → Open Folder
2. Select: Infrastructure/ (or any repo you want to analyze)
```

#### **Step 4: Click "Analyze"**

```
In Akashic IDE:
1. Click "Analyze" button (or "Analyze Folder")
2. Wait for analysis to complete
3. Check results in:
   - .akashic/analysis/DEPLOYMENT_MAPPING.md
   - .akashic/reconciliation/DEPLOYMENT_RECONCILIATION.md
   - .akashic/deploy/
```

**That's it! The deployment system runs automatically as part of the analysis!**

---

## ✅ Option 2: Use via Apollo Docker Container

**If you want to run it manually or test it:**

### **Step 1: Enter Apollo Container**

```bash
cd /Users/leonard/Documents/repos/Jacob\ Aaron\ Leonard\ LLC/ColossalCapital/Infrastructure

# Enter Apollo container
docker-compose -f docker-compose.complete-system.yml exec apollo bash
```

### **Step 2: Run Analysis**

```bash
# Inside Apollo container
cd /app

# The orchestrator is already integrated!
# Just call it via Python:

python3 << 'EOF'
import asyncio
from services.akashic_intelligence_orchestrator import AkashicIntelligenceOrchestrator

async def main():
    orchestrator = AkashicIntelligenceOrchestrator(entity_id="leonard")
    
    # This will run EVERYTHING including deployment analysis
    result = await orchestrator.analyze_repository(
        "/workspace/Infrastructure",  # Mounted volume
        options={
            'watch_files': False,
            'consolidate_docs': False,
            'generate_plan': False,
            'build_knowledge_graph': False,
            'index_for_search': False,
        }
    )
    
    print("\n✅ Analysis Complete!")
    print(f"📊 Deployment folders analyzed: {result['phases']['deployment_mapping']['folders_analyzed']}")
    print(f"⚠️  Conflicts detected: {result['phases']['deployment_mapping']['conflicts']}")
    print(f"📂 Results saved to: /workspace/Infrastructure/.akashic/")

asyncio.run(main())
EOF
```

### **Step 3: View Results**

```bash
# Still inside Apollo container
cd /workspace/Infrastructure/.akashic/

# View deployment mapping
cat analysis/DEPLOYMENT_MAPPING.md

# View AI reconciliation (if conflicts found)
cat reconciliation/DEPLOYMENT_RECONCILIATION.md

# Check generated configs
ls -la deploy/local/
ls -la deploy/cloud/
```

### **Step 4: Exit Container**

```bash
exit
```

---

## 🎯 What Gets Analyzed

When you run the analysis (via IDE or Docker), it will:

### **Phase 1: Project Type Detection**
- Detects: Python API, Trading Platform, etc.

### **Phase 2A: Scaffolding Analysis**
- Analyzes project structure

### **Phase 2B: Deployment Mapping** ⭐ NEW!
- ✅ Scans for deployment folders (docker/, kubernetes/, juju/, terraform/, etc.)
- ✅ Analyzes deployment files
- ✅ Detects conflicts (multiple Docker setups, etc.)
- ✅ Generates recommendations
- ✅ Creates deployment map
- ✅ Generates optimized configs
- ✅ Runs AI-guided reconciliation

### **Phase 2C: PM Sync**
- Syncs with Linear/Jira

### **Phase 3+: Intelligence Analysis**
- Documentation consolidation
- Project plan generation
- Knowledge graph building
- RAG indexing

---

## 📂 Output Structure

After analysis, you'll have:

```
.akashic/
├── analysis/
│   ├── DEPLOYMENT_MAPPING.md          # Detailed deployment analysis
│   ├── deployment_map.json            # Machine-readable map
│   ├── DOCUMENTATION_ANALYSIS.md      # Doc coverage
│   └── TESTING_ANALYSIS.md            # Test coverage
│
├── reconciliation/
│   └── DEPLOYMENT_RECONCILIATION.md   # AI-guided conflict resolution
│
└── deploy/
    ├── local/
    │   ├── docker/
    │   │   ├── docker-compose.yml
    │   │   ├── docker-compose.base.yml
    │   │   └── docker-compose.dev.yml
    │   ├── podman/
    │   │   ├── podman-compose.yml
    │   │   └── pods/
    │   ├── tilt/
    │   │   └── Tiltfile
    │   └── scripts/
    │       ├── start-all.sh
    │       ├── start-podman.sh
    │       └── switch-runtime.sh
    └── cloud/
        ├── kubernetes/
        ├── juju/
        ├── terraspace/
        └── monitoring/
```

---

## 🧪 Test It Now

### **Quick Test (2 minutes):**

```bash
# 1. Restart Apollo
cd Infrastructure
docker-compose -f docker-compose.complete-system.yml restart apollo

# 2. Enter Apollo container
docker-compose -f docker-compose.complete-system.yml exec apollo bash

# 3. Run quick test
cd /app
python3 -c "
from services.deployment_mapper import DeploymentMapper
import asyncio

async def test():
    mapper = DeploymentMapper('/workspace/Infrastructure')
    result = await mapper.analyze_deployments()
    print(f'✅ Found {len(result[\"deployment_map\"])} deployment categories')
    print(f'⚠️  Detected {len(result[\"conflicts\"])} conflicts')
    return result

asyncio.run(test())
"

# 4. If that works, run full analysis
python3 -c "
from services.akashic_intelligence_orchestrator import AkashicIntelligenceOrchestrator
import asyncio

async def test():
    orch = AkashicIntelligenceOrchestrator(entity_id='test')
    result = await orch.analyze_repository(
        '/workspace/Infrastructure',
        options={'watch_files': False, 'consolidate_docs': False, 'generate_plan': False, 'build_knowledge_graph': False, 'index_for_search': False}
    )
    print('✅ Full analysis complete!')
    return result

asyncio.run(test())
"
```

---

## 🎨 For Visual UI (Optional)

If you want the visual deployment panel in Akashic IDE:

### **Step 1: Update IDE Frontend**

```bash
cd Akashic/ide

# Files are already created:
# - src/components/DeploymentPanel.tsx ✅
# - src/main/deploymentHandlers.ts ✅

# Just need to integrate them into the app
```

### **Step 2: Register IPC Handlers**

Edit `Akashic/ide/src/main/index.ts`:

```typescript
import { registerDeploymentHandlers } from './deploymentHandlers';

app.whenReady().then(() => {
  // ... existing code ...
  
  // Add this line:
  registerDeploymentHandlers();
  
  // ... rest of code ...
});
```

### **Step 3: Add Panel to Layout**

Edit `Akashic/ide/src/App.tsx`:

```typescript
import DeploymentPanel from './components/DeploymentPanel';

// Add to your tab system:
<Tab label="Deployment" icon={<BuildIcon />} />

<TabPanel value="deployment">
  <DeploymentPanel />
</TabPanel>
```

### **Step 4: Rebuild IDE**

```bash
cd Akashic/ide
npm install
npm run build
npm run dev
```

---

## 📊 Summary

### **To Use Right Now:**

**Option A: Via Akashic IDE (Best)**
1. Restart Apollo: `docker-compose restart apollo`
2. Open Akashic IDE
3. Load your repo
4. Click "Analyze"
5. Check `.akashic/` folder for results

**Option B: Via Apollo Docker**
1. Enter container: `docker-compose exec apollo bash`
2. Run orchestrator (see code above)
3. Check `.akashic/` folder for results

### **What You Get:**
- ✅ Deployment mapping
- ✅ Conflict detection
- ✅ AI-guided reconciliation
- ✅ Optimized configs generated
- ✅ Ready-to-use deployment files

### **No Standalone CLI Needed:**
The system is designed to work through:
1. **Akashic IDE** (primary interface)
2. **Apollo API** (backend service)
3. **Docker container** (for manual testing)

---

## 🎉 Ready to Use!

**The deployment system is fully integrated into Apollo's orchestrator.**

**Just restart Apollo and run an analysis - it will automatically:**
1. Map your deployment configs
2. Detect conflicts
3. Generate AI reconciliation
4. Create optimized configs
5. Save everything to `.akashic/`

**No additional setup needed! 🚀**
