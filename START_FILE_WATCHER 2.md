# Start File Watcher - Quick Guide 🚀

## ✅ Phase 1 Complete: Multi-Project Detection & File Watcher

### **What We Built:**

1. **Multi-Project Detector** (`services/multi_project_detector.py`)
   - Scans directory tree for `.akashic` folders
   - Builds hierarchical project structure
   - Detects root and sub-projects
   - Creates missing `.akashic` directories

2. **File Watcher** (`services/akashic_file_watcher.py`)
   - Monitors all detected projects
   - Tracks file changes (create, modify, delete)
   - Updates `.akashic/analysis/` for each project
   - Propagates changes to parent projects
   - Updates master plan for root projects

---

## 🚀 How to Run:

### **1. Install Dependencies:**

```bash
cd Apollo
pip install watchdog
```

### **2. Test Multi-Project Detection:**

```bash
# From Apollo directory
python -m services.multi_project_detector /path/to/ColossalCapital
```

**Example Output:**
```
🔍 Scanning for .akashic projects in: /Users/you/ColossalCapital
  📁 Found: Root (root)
    📂 Found: Atlas (sub_project)
    📂 Found: Apollo (sub_project)
    📂 Found: Akashic (sub_project)
✅ Found 4 projects:
   - Root projects: 1
   - Sub-projects: 3

📊 Project Hierarchy:
📁 Root
  📂 Atlas
  📂 Apollo
  📂 Akashic

💾 Saved project registry to: /Users/you/ColossalCapital/.akashic/project_registry.json
📁 Creating .akashic for: Root
  ✅ Created: /Users/you/ColossalCapital/.akashic
```

### **3. Start File Watcher:**

```bash
# From Apollo directory
python -m services.akashic_file_watcher /path/to/ColossalCapital
```

**Example Output:**
```
🔍 Scanning for .akashic projects in: /Users/you/ColossalCapital
  📁 Found: Root (root)
    📂 Found: Atlas (sub_project)
    📂 Found: Apollo (sub_project)
    📂 Found: Akashic (sub_project)

👁️  Starting File Watcher for 4 projects...
  ✅ Watching: Root (root)
  ✅ Watching: Atlas (sub_project)
  ✅ Watching: Apollo (sub_project)
  ✅ Watching: Akashic (sub_project)

🔄 File Watcher active. Monitoring for changes...

📝 [MODIFIED] main.py
   Project: Apollo
   ✅ Updated analysis for Apollo
   ↗️  Updated parent: Root
   📊 Would update master plan (Phase 2)
```

---

## 📁 What Gets Created:

### **Root Project (.akashic/):**
```
ColossalCapital/
└── .akashic/
    ├── config.json                    # Project config
    ├── project_registry.json          # All projects registry
    ├── analysis/
    │   ├── changes.log               # All changes
    │   ├── files.json                # File inventory
    │   └── child_project_changes.log # Sub-project changes
    ├── docs/
    ├── restructuring/
    ├── pm/
    ├── diagrams/
    └── planning/
```

### **Sub-Project (.akashic/):**
```
ColossalCapital/Apollo/
└── .akashic/
    ├── config.json                    # Project config
    ├── analysis/
    │   ├── changes.log               # Apollo changes
    │   └── files.json                # Apollo files
    ├── docs/
    ├── restructuring/
    ├── pm/
    ├── diagrams/
    └── planning/
```

---

## 📊 Files Created:

### **1. project_registry.json** (Root .akashic)

```json
{
  "generated_at": "2024-10-31T21:00:00",
  "root_path": "/Users/you/ColossalCapital",
  "total_projects": 4,
  "hierarchy": {
    "path": "/Users/you/ColossalCapital",
    "name": "Root",
    "type": "root",
    "children": [
      {
        "path": "/Users/you/ColossalCapital/Atlas",
        "name": "Atlas",
        "type": "sub_project",
        "children": []
      },
      {
        "path": "/Users/you/ColossalCapital/Apollo",
        "name": "Apollo",
        "type": "sub_project",
        "children": []
      }
    ]
  }
}
```

### **2. config.json** (Each .akashic)

```json
{
  "project_name": "Apollo",
  "project_type": "sub_project",
  "created_at": "2024-10-31T21:00:00",
  "parent_project": "/Users/you/ColossalCapital"
}
```

### **3. changes.log** (Each .akashic/analysis/)

```json
{"timestamp": "2024-10-31T21:05:00", "file": "services/main.py", "event": "modified", "lines": 150}
{"timestamp": "2024-10-31T21:06:00", "file": "api/routes.py", "event": "created", "lines": 45}
{"timestamp": "2024-10-31T21:07:00", "file": "old_file.py", "event": "deleted", "lines": 0}
```

### **4. files.json** (Each .akashic/analysis/)

```json
{
  "project": "Apollo",
  "last_updated": "2024-10-31T21:10:00",
  "total_files": 145,
  "by_type": {
    ".py": 89,
    ".js": 32,
    ".md": 24
  },
  "files": {
    "services/main.py": {
      "path": "services/main.py",
      "type": ".py",
      "size": 4096,
      "lines": 150,
      "last_modified": "2024-10-31T21:05:00",
      "todos": 3
    }
  }
}
```

---

## 🎯 What Happens When You Edit a File:

### **Scenario: Edit `/ColossalCapital/Apollo/services/main.py`**

1. **File Watcher Detects Change**
   ```
   📝 [MODIFIED] main.py
      Project: Apollo
   ```

2. **Analyzes the Change**
   - Counts lines
   - Detects TODOs
   - Extracts imports
   - Calculates file size

3. **Updates Apollo's .akashic/analysis/**
   - Appends to `changes.log`
   - Updates `files.json` inventory

4. **Updates Parent (Root) .akashic/analysis/**
   - Appends to `child_project_changes.log`

5. **Would Update Master Plan** (Phase 2)
   - Will regenerate project plan
   - Will sync with cloud

---

## 🔄 Next Steps:

### **Phase 2: Project Plan Generator** (Next!)

Will implement:
- Analyze codebase structure
- Generate epics from modules
- Generate stories from features
- Generate tasks from TODOs
- Aggregate sub-project plans into master plan

### **Then:**
- Phase 3: Cloud State Puller
- Phase 4: Reconciliation Engine
- Phase 5: Triaging UI
- Phase 6: Sync Executor
- Phase 7: Continuous Monitoring

---

## ✅ Phase 1 Status:

- ✅ Multi-Project Detection
- ✅ Hierarchical Project Structure
- ✅ File Watcher with Multi-Project Support
- ✅ Change Tracking
- ✅ Parent/Child Updates
- ✅ Auto-create .akashic directories

**Ready for Phase 2!** 🚀
