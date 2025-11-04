# 🎵 Apollo Repository Restructure Plan

## 🎯 Goal

Reorganize Apollo to support:
1. **Conductor** - Smart GPU & model orchestration
2. **Studio** - Admin UI for managing AI
3. **API** - Universal compute interface
4. **Blender Rendering** - World Turtle Farm integration

---

## 📊 Current Structure → New Structure

### Current (Messy):
```
Apollo/
├─ agents/ (100+ agent files)
├─ api/
│  └─ main.py
├─ agentic/
│  └─ orchestrator/
└─ ... (mixed organization)
```

### New (Clean):
```
apollo/
├─ conductor/              ⭐ NEW! Smart orchestration
│  ├─ src/
│  │  ├─ selector/
│  │  ├─ scheduler/
│  │  ├─ optimizer/
│  │  └─ conductor.py
│  ├─ tests/
│  └─ requirements.txt
│
├─ api/                    ⭐ REORGANIZED
│  ├─ src/
│  │  ├─ routers/
│  │  ├─ services/
│  │  ├─ models/
│  │  └─ compliance/
│  ├─ tests/
│  └─ requirements.txt
│
├─ studio/                 ⭐ NEW! React UI
│  ├─ src/
│  │  ├─ pages/
│  │  ├─ components/
│  │  └─ services/
│  ├─ public/
│  └─ package.json
│
├─ agents/                 KEEP (agent definitions)
│  ├─ core/
│  ├─ finance/
│  ├─ legal/
│  └─ ...
│
├─ sdk/                    ⭐ NEW! Client libraries
│  ├─ python/
│  ├─ typescript/
│  └─ dart/
│
├─ workers/                ⭐ NEW! Background jobs
│  ├─ training_worker.py
│  ├─ rendering_worker.py  ⭐ Blender
│  └─ embedding_worker.py
│
├─ config/
│  ├─ conductor.yaml
│  ├─ models.yaml
│  └─ gpus.yaml
│
├─ docker-compose.yml      Full stack
├─ Makefile                Build commands
└─ README.md               Updated docs
```

---

## 📋 Reorganization Steps

### Step 1: Create New Directories

```bash
cd /path/to/Apollo

# Create Conductor module
mkdir -p conductor/src/{selector,scheduler,optimizer,router}
mkdir -p conductor/tests

# Create Studio UI
mkdir -p studio/src/{pages,components,hooks,services}
mkdir -p studio/public

# Create SDK
mkdir -p sdk/{python/apollo_sdk,typescript/src,dart/lib}

# Create Workers
mkdir -p workers

# Reorganize API
mkdir -p api/src/{routers,services,models,compliance}
mkdir -p api/tests
```

### Step 2: Move Existing Files

```bash
# Move orchestrator to Conductor
mv agentic/orchestrator/* conductor/src/

# Keep agents where they are (already organized)
# agents/ stays as is

# Reorganize API
# (Will detail specific moves)
```

### Step 3: Create New Files

```bash
# Conductor entry point
touch conductor/src/conductor.py

# Studio app
touch studio/src/App.tsx
touch studio/package.json

# SDK entry points
touch sdk/python/apollo_sdk/__init__.py
touch sdk/typescript/src/index.ts
touch sdk/dart/lib/apollo_sdk.dart

# Workers
touch workers/training_worker.py
touch workers/rendering_worker.py
touch workers/embedding_worker.py
```

---

## 🎯 Priority Files to Create

### Conductor Core:

**File:** `conductor/src/conductor.py`
```python
"""
Apollo Conductor - Smart GPU & Model Orchestration
Intelligently routes all compute jobs
"""

class Conductor:
    def __init__(self):
        self.model_selector = ModelSelector()
        self.gpu_scheduler = GPUScheduler()
        self.cost_optimizer = CostOptimizer()
        
    async def execute(self, job: ComputeJob) -> JobHandle:
        """
        Main entry point for all compute
        Handles: AI, rendering, backtesting, RAG
        """
        
        # 1. Analyze job
        analysis = await self.analyze_job(job)
        
        # 2. Select optimal model/resource
        selection = self.model_selector.select(job, analysis)
        
        # 3. Allocate GPU
        gpu = await self.gpu_scheduler.allocate(selection.gpu_type)
        
        # 4. Optimize cost
        optimized = self.cost_optimizer.optimize(selection, gpu)
        
        # 5. Execute
        handle = await self.execute_on_theta(optimized)
        
        return handle
```

---

### Studio Main App:

**File:** `studio/src/App.tsx`
```typescript
/**
 * Apollo Studio - AI Management Interface
 * Embedded in Atlas as a module
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';

export function ApolloStudio() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ConductorDashboard />} />
        <Route path="/training" element={<TrainingDashboard />} />
        <Route path="/rag" element={<RAGManager />} />
        <Route path="/rendering" element={<RenderQueue />} />
        <Route path="/agents" element={<AgentBuilder />} />
        <Route path="/monitoring" element={<PerformanceMonitor />} />
        <Route path="/governance" element={<DataGovernance />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### Simplified Delt SDK:

**File:** `sdk/dart/lib/apollo_sdk.dart`
```dart
/// Apollo SDK for Delt (Simplified)
/// Only chat functionality, no IDE features

library apollo_sdk;

export 'src/apollo_client.dart';
export 'src/chat_service.dart';
export 'src/conductor_client.dart';

class ApolloClient {
  final String apiUrl;
  final String authToken;
  
  ApolloClient({
    required this.apiUrl,
    required this.authToken,
  });
  
  /// Simple chat interface (for Delt mobile)
  Future<ChatResponse> chat(String message) async {
    final response = await http.post(
      '$apiUrl/api/v1/inference/chat',
      headers: {'Authorization': 'Bearer $authToken'},
      body: {'message': message},
    );
    
    return ChatResponse.fromJson(response.data);
  }
  
  /// Get data subscription recommendations
  Future<List<DataStream>> recommendDataStreams() async {
    // Apollo Conductor analyzes user's needs
    final response = await http.get(
      '$apiUrl/api/v1/conductor/recommend-data',
      headers: {'Authorization': 'Bearer $authToken'},
    );
    
    return (response.data as List)
        .map((d) => DataStream.fromJson(d))
        .toList();
  }
}
```

---

## 🎨 Apollo Studio Integration with Atlas

### How Studio Embeds in Atlas:

**File:** `atlas/packages/apollo-studio/ApolloStudioModule.tsx`
```typescript
/**
 * Apollo Studio embedded in Atlas
 * Power user interface for AI management
 */

import { ApolloStudio } from '@apollo/studio';

export function ApolloStudioModule() {
  const { user, authToken } = useAuth();
  
  // Only show to Team+ tiers
  if (!user.tier.includes(['team', 'hedge_fund', 'enterprise'])) {
    return <UpgradePrompt feature="Apollo Studio" />;
  }
  
  return (
    <ApolloStudio
      apiUrl="https://apollo-api.delt.capital"
      authToken={authToken}
      userId={user.id}
      theme="atlas-dark"
    />
  );
}
```

---

## 🔄 Migration Guide

### For Existing Apollo Code:

```bash
# 1. Create new structure (don't break existing)
mkdir -p conductor api/src studio sdk workers

# 2. Copy (not move) files to new structure
cp agentic/orchestrator/* conductor/src/

# 3. Update imports in new files
# (Keep old files working during transition)

# 4. Test new structure
pytest conductor/tests
npm test studio/

# 5. Once working, deprecate old structure
mv agentic agentic.old

# 6. Update all imports to new paths
# 7. Delete old structure
```

---

## 🎯 Deliverables

### By End of Restructure:

1. ✅ `conductor/` - Clean, focused orchestration
2. ✅ `api/` - Well-organized FastAPI backend
3. ✅ `studio/` - React UI for Atlas
4. ✅ `sdk/` - Client libraries (Python, TS, Dart)
5. ✅ `workers/` - Background job processors
6. ✅ `agents/` - Agent definitions (unchanged)
7. ✅ Clear documentation
8. ✅ Working examples
9. ✅ Docker compose for full stack
10. ✅ CI/CD pipelines

---

## 🚀 Next Steps

### Immediate:
1. Create new directory structure
2. Create core Conductor files
3. Create Studio skeleton
4. Create SDK packages
5. Update docker-compose.yml

### This Week:
- [ ] Restructure Apollo repo
- [ ] Create Conductor module
- [ ] Add Blender rendering support
- [ ] Create Studio skeleton

### Next Week:
- [ ] Build Studio UI pages
- [ ] Integrate with Atlas
- [ ] Test end-to-end
- [ ] Deploy to staging

---

**Ready to restructure Apollo now?** 🎵

