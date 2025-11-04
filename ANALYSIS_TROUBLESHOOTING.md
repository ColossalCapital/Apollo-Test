# Analysis Troubleshooting Guide

## ❌ Error: "Analysis failed"

### **Common Causes:**

1. **Apollo not running**
2. **Missing dependencies**
3. **Path translation issues**
4. **Permission errors**

---

## 🔍 Debugging Steps

### **1. Check Apollo is Running**

```bash
# Check if Apollo is running
curl http://localhost:8002/health

# Expected response:
{"status":"healthy"}
```

**If not running:**
```bash
cd Apollo
python -m uvicorn api.main:app --reload --port 8002
```

---

### **2. Check Endpoint Directly**

```bash
curl -X POST http://localhost:8002/api/akashic/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/your/repo",
    "entity_id": "user_123",
    "options": {
      "watch_files": true,
      "consolidate_docs": true,
      "generate_plan": false,
      "build_knowledge_graph": false,
      "index_for_search": false,
      "save_results": true
    }
  }'
```

---

### **3. Check Apollo Logs**

```bash
# Apollo logs will show detailed error
tail -f apollo.log

# Or check console output if running in terminal
```

**Look for:**
- Import errors (missing dependencies)
- Path errors (file not found)
- Permission errors (can't write to directory)

---

### **4. Test with Minimal Options**

Start with minimal options to isolate the issue:

```json
{
  "repo_path": "/path/to/repo",
  "entity_id": "user_123",
  "options": {
    "watch_files": true,
    "consolidate_docs": false,
    "generate_plan": false,
    "build_knowledge_graph": false,
    "index_for_search": false,
    "save_results": true
  }
}
```

Then enable options one by one:
1. ✅ `watch_files` only
2. ✅ + `consolidate_docs`
3. ✅ + `generate_plan`
4. ✅ + `build_knowledge_graph`
5. ✅ + `index_for_search`

---

## 🐛 Common Errors

### **Error: "ModuleNotFoundError: No module named 'agents'"**

**Cause:** Missing dependencies

**Fix:**
```bash
cd Apollo
pip install -r requirements.txt
```

---

### **Error: "FileNotFoundError: [Errno 2] No such file or directory"**

**Cause:** Path translation issue or repo doesn't exist

**Fix:**
1. Check repo path is correct
2. Check you have read permissions
3. Try absolute path instead of relative

---

### **Error: "PermissionError: [Errno 13] Permission denied"**

**Cause:** Can't write to `.akashic/` folder

**Fix:**
```bash
# Give write permissions
chmod -R 755 /path/to/repo

# Or run as sudo (not recommended)
sudo python -m uvicorn api.main:app --reload --port 8002
```

---

### **Error: "KeyError: 'phases'"**

**Cause:** Analysis didn't complete, response structure incomplete

**Fix:**
1. Check Apollo logs for actual error
2. Disable optional features (knowledge_graph, index_for_search)
3. Try with minimal options first

---

## ✅ Successful Analysis

**Expected response:**
```json
{
  "status": "completed",
  "repo_path": "/path/to/repo",
  "started_at": "2025-11-01T12:34:56",
  "completed_at": "2025-11-01T12:36:23",
  "phases": {
    "code_scan": {
      "total_files": 127,
      "hot_files": [...],
      "cold_files": [...],
      "planned_features": [...]
    },
    "docs_consolidation": {...},
    "project_plan": {...},
    "restructuring": {...}
  },
  "monitoring": {
    "status": "active"
  }
}
```

**Expected files created:**
```
.akashic/
├── analysis/
│   ├── CURRENT_STATE.md
│   ├── FUTURE_STATE.md
│   ├── ISSUES_REPORT.md
│   └── RESTRUCTURING_PLAN.md
├── docs/
│   └── PROJECT_DOCS.md
├── pm/
│   └── (PM integration files)
└── config/
    └── .akashic.yml
```

---

## 🔧 Quick Fixes

### **Reset Everything:**
```bash
# Stop Apollo
pkill -f uvicorn

# Remove .akashic folder
rm -rf /path/to/repo/.akashic

# Restart Apollo
cd Apollo
python -m uvicorn api.main:app --reload --port 8002

# Try analysis again
```

---

### **Enable Debug Logging:**

```python
# In Apollo/api/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

### **Test Individual Components:**

```python
# Test CodeWatcherAgent
from agents.analytics.code_watcher_agent import CodeWatcherAgent

watcher = CodeWatcherAgent(repo_path="/path/to/repo", entity_id="test")
results = await watcher.initial_scan()
print(results)
```

---

## 📞 Still Having Issues?

1. **Check Apollo logs** for detailed error
2. **Try minimal options** to isolate problem
3. **Test components individually** to find failing part
4. **Check permissions** on repo directory
5. **Verify dependencies** are installed

**Most common fix:** Disable `build_knowledge_graph` and `index_for_search` options - these require additional services (Neo4j, Qdrant) that might not be running.
