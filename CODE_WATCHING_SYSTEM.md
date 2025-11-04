# 🤖 Autonomous Code Watching System

## ✅ Already Implemented!

You have a complete **Agentic Codebase RAG** system in:
- `Apollo/learning/agentic_codebase_rag.py`

---

## 🎯 What It Does

### **1. Git Watching**
```python
class GitWatcher:
    """Watch git repository for changes"""
    
    async def stream(self):
        """Stream git events"""
        while True:
            # Check for new commits every 5 seconds
            current_commit = repo.head.commit.hexsha
            
            if current_commit != self.last_commit:
                yield {
                    'type': 'commit',
                    'commit_hash': current_commit,
                    'author': repo.head.commit.author.name,
                    'message': repo.head.commit.message,
                    'changed_files': [list of changed files]
                }
```

### **2. Autonomous Actions on Commit**
```python
async def handle_commit(self, event):
    """Handle new commit"""
    
    # 1. Re-index changed files
    await self.reindex_files(changed_files)
    
    # 2. Update current state documentation
    await self.update_current_state()
    
    # 3. Check for drift from PM plan
    await self.check_drift()
    
    # 4. Notify team
    await self.notify_team(
        f"📝 {author} committed: {message}\n"
        f"Files changed: {count}"
    )
```

### **3. Auto-Indexing**
```python
async def reindex_files(self, file_paths):
    """Re-index specific files"""
    
    # Filter code files (.py, .ts, .rs, etc.)
    code_files = filter_code_files(file_paths)
    
    # Read and parse
    for file in code_files:
        content = read_file(file)
        snippet = create_snippet(file, content)
        
    # Generate embeddings
    embeddings = encode(snippets)
    
    # Store in Qdrant (team-level)
    await store_in_qdrant(snippets, embeddings)
```

### **4. Current State Documentation**
```python
async def update_current_state(self):
    """Generate current state documentation"""
    
    # 1. Analyze codebase structure
    structure = {
        'total_files': 304,
        'total_lines': 45000,
        'languages': {'Python': 150, 'TypeScript': 100, 'Rust': 54},
        'entry_points': ['main.py', 'index.ts'],
        'dependencies': [...],
        'recent_changes': [...]
    }
    
    # 2. Generate documentation with DeepSeek
    state_doc = await deepseek.generate(
        f"Generate current state documentation for:\n{structure}"
    )
    
    # 3. Store in database
    await store_current_state(state_doc)
```

### **5. Drift Detection**
```python
async def check_drift(self):
    """Check for drift from PM plan"""
    
    # 1. Get current state
    current_state = await get_current_state()
    
    # 2. Get PM plan from Linear
    pm_plan = await get_pm_plan()
    
    # 3. Compare with DeepSeek
    drift_analysis = await deepseek.analyze_drift(
        current_state, pm_plan
    )
    
    # 4. If significant drift, alert team
    if drift_analysis['drift_score'] > 0.3:
        await notify_team(
            f"⚠️ Drift detected!\n{drift_analysis['summary']}"
        )
```

### **6. Team Notifications**
```python
async def notify_team(self, message):
    """Notify team via Slack/Email"""
    
    # Send to Slack
    await slack_client.send_message(
        channel=self.team_channel,
        text=message
    )
    
    # Send email to team
    await email_client.send(
        to=self.team_emails,
        subject="Codebase Update",
        body=message
    )
```

---

## 🚀 How to Use

### **1. Start Watching a Codebase**

```python
from learning.agentic_codebase_rag import AgenticCodebaseRAG

# Initialize
watcher = AgenticCodebaseRAG(
    codebase_id="colossalcapital_main",
    team_id="team_123",
    org_id="org_1",
    repo_path="/path/to/ColossalCapital"
)

# Start autonomous watching
await watcher.start_watching()
```

### **2. What Happens Automatically**

```
Developer commits code
  ↓
Git watcher detects commit (5 sec polling)
  ↓
Extract changed files
  ↓
Re-index changed files in Qdrant
  ↓
Update current state documentation
  ↓
Compare to PM plan (Linear)
  ↓
Detect drift (if any)
  ↓
Notify team via Slack/Email
```

### **3. Background Tasks**

The watcher runs 3 background tasks:

**Task 1: Git Events**
```python
async def watch_git_events(self):
    """Watch for commits"""
    async for event in self.git_watcher.stream():
        await self.handle_commit(event)
```

**Task 2: Periodic Full Sync**
```python
async def periodic_full_sync(self):
    """Full re-index every 24 hours"""
    while self.running:
        await asyncio.sleep(86400)  # 24 hours
        await self.full_reindex()
```

**Task 3: Periodic State Update**
```python
async def periodic_state_update(self):
    """Update state every hour"""
    while self.running:
        await asyncio.sleep(3600)  # 1 hour
        await self.update_current_state()
```

---

## 📊 Example Workflow

### **Scenario: Developer Adds Email Validation**

```
1. Developer commits:
   - Added: src/utils/validation.py
   - Modified: src/routes/auth.py
   
2. Git watcher detects (within 5 seconds)

3. Auto-reindex:
   ✅ Indexed validation.py (50 lines)
   ✅ Indexed auth.py (120 lines)
   
4. Update current state:
   📊 Current State:
   - Total files: 305 (+1)
   - New module: validation
   - Updated: auth routes
   
5. Check drift:
   ✅ No drift - matches PM plan ticket #47
   
6. Notify team:
   📝 John committed: Add email validation
   Files changed: 2
   Status: ✅ On track with PM plan
```

### **Scenario: Developer Goes Off-Plan**

```
1. Developer commits:
   - Added: src/experimental/new_feature.py
   
2. Git watcher detects

3. Auto-reindex:
   ✅ Indexed new_feature.py
   
4. Update current state:
   📊 Current State:
   - New experimental feature detected
   
5. Check drift:
   ⚠️ DRIFT DETECTED!
   - New feature not in PM plan
   - No Linear ticket found
   - Drift score: 0.7
   
6. Notify team:
   ⚠️ Drift Alert!
   John added experimental feature
   Not in PM plan - needs review
   Recommend: Create Linear ticket
```

---

## 🔧 Integration with Akashic

### **Enable in Akashic IDE**

Add to Akashic settings:
```typescript
{
  "codeWatching": {
    "enabled": true,
    "autoIndex": true,
    "notifyOnDrift": true,
    "checkInterval": 5  // seconds
  }
}
```

### **UI Indicators**

```
File Explorer:
📁 src/
  📄 main.py ✅ (indexed 2 min ago)
  📄 auth.py 🔄 (indexing...)
  📄 new.py ⚠️ (drift detected)
```

### **Status Bar**

```
🤖 Code Watcher: Active | Last sync: 2 min ago | Files: 304 | Drift: None
```

---

## 📈 Benefits

**For Developers:**
- ✅ Code automatically indexed on commit
- ✅ Always up-to-date documentation
- ✅ Drift alerts keep you on track
- ✅ No manual indexing needed

**For PMs:**
- ✅ Real-time view of codebase state
- ✅ Automatic drift detection
- ✅ Team notifications
- ✅ Always synced with Linear

**For Teams:**
- ✅ Shared knowledge base
- ✅ Automatic documentation
- ✅ Better coordination
- ✅ Less context switching

---

## 💰 Cost

**Per Codebase:**
- Git watching: $0 (local)
- Qdrant indexing: $0 (local) or ~$0.01/month (cloud)
- DeepSeek analysis: $0 (local Ollama)
- Notifications: $0 (Slack/Email)

**Total: ~$0.01/month per codebase**

---

## ✅ Summary

**You already have:**
1. ✅ Git watcher (5 sec polling)
2. ✅ Auto-indexing on commit
3. ✅ Current state documentation
4. ✅ Drift detection
5. ✅ Team notifications
6. ✅ Periodic full syncs

**Just need to:**
1. Start the watcher for your codebase
2. Configure team notifications
3. Connect to Linear for PM plan comparison

**The autonomous code watching system is ready to use!** 🤖🔍
