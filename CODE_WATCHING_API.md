# 🤖 Code Watching API Endpoints

## ✅ Now Available in Apollo!

The Agentic Codebase RAG system now has API endpoints for Akashic IDE integration.

---

## 📡 API Endpoints

### **1. Start Code Watching**

```http
POST /api/codebase/watch/start
```

**Request:**
```json
{
  "codebase_id": "colossalcapital_main",
  "entity_id": "user_123",
  "org_id": "org_1",
  "team_id": "team_123",
  "repo_path": "/Users/leonard/Documents/repos/.../ColossalCapital",
  "notify_slack": true,
  "notify_email": false
}
```

**Response:**
```json
{
  "status": "started",
  "codebase_id": "colossalcapital_main",
  "message": "Code watching started successfully"
}
```

**What it does:**
- ✅ Starts git watcher (polls every 5 seconds)
- ✅ Auto-indexes changed files on commit
- ✅ Updates current state documentation
- ✅ Detects drift from PM plan
- ✅ Notifies team via Slack/Email

---

### **2. Stop Code Watching**

```http
POST /api/codebase/watch/stop/{codebase_id}
```

**Example:**
```bash
curl -X POST http://localhost:8002/api/codebase/watch/stop/colossalcapital_main
```

**Response:**
```json
{
  "status": "stopped",
  "codebase_id": "colossalcapital_main",
  "message": "Code watching stopped"
}
```

---

### **3. Get Watcher Status**

```http
GET /api/codebase/watch/status/{codebase_id}
```

**Response:**
```json
{
  "codebase_id": "colossalcapital_main",
  "status": "running",
  "last_commit": "abc123def456",
  "last_sync": "2025-10-30T23:25:00Z",
  "files_indexed": 304,
  "drift_detected": false
}
```

---

### **4. List Active Watchers**

```http
GET /api/codebase/watch/list
```

**Response:**
```json
{
  "watchers": [
    {
      "codebase_id": "colossalcapital_main",
      "status": "running"
    },
    {
      "codebase_id": "akashic_ide",
      "status": "running"
    }
  ],
  "total": 2
}
```

---

## 🎨 Akashic IDE Integration

### **Add "Start Watching" Button**

```typescript
// In Akashic IDE
const startWatching = async () => {
  const response = await fetch('http://localhost:8002/api/codebase/watch/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      codebase_id: 'colossalcapital_main',
      entity_id: 'user_123',
      repo_path: loadedCodebase,
      notify_slack: true
    })
  });
  
  const data = await response.json();
  
  if (data.status === 'started') {
    setChatMessages(prev => [...prev, {
      role: 'assistant',
      content: `🤖 Code watching started!\n\nI'm now monitoring your codebase for changes.\n\n✨ I will:\n- Auto-index changed files\n- Update documentation\n- Detect drift from PM plan\n- Notify team of changes`
    }]);
  }
};
```

### **Status Indicator**

```typescript
// Poll for status
const checkWatcherStatus = async () => {
  const response = await fetch(
    `http://localhost:8002/api/codebase/watch/status/colossalcapital_main`
  );
  const status = await response.json();
  
  return status;
};

// Show in UI
{watcherStatus.status === 'running' && (
  <div style={{ 
    padding: '8px', 
    backgroundColor: '#d1fae5', 
    borderRadius: '6px' 
  }}>
    🤖 Code Watcher: Active
    <br />
    Last sync: {watcherStatus.last_sync}
    <br />
    Files indexed: {watcherStatus.files_indexed}
  </div>
)}
```

---

## 🔄 Complete Workflow

### **User Experience in Akashic:**

```
1. User loads codebase
   ↓
2. Clicks "Start Code Watching"
   ↓
3. Apollo starts AgenticCodebaseRAG
   ↓
4. Status shows: "🤖 Code Watcher: Active"
   ↓
5. Developer commits code
   ↓
6. Watcher detects (within 5 seconds)
   ↓
7. Auto-indexes changed files
   ↓
8. Updates current state docs
   ↓
9. Checks for drift
   ↓
10. Notifies in Akashic chat:
    "📝 New commit detected:
     - 2 files changed
     - Auto-indexed
     - No drift detected"
```

---

## 🎯 Example Usage

### **Start Watching from Akashic**

```typescript
// When codebase is loaded
const handleStartWatching = async () => {
  try {
    const response = await fetch('http://localhost:8002/api/codebase/watch/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codebase_id: `codebase_${Date.now()}`,
        entity_id: 'user_123',
        repo_path: loadedCodebase,
        notify_slack: false,
        notify_email: false
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Show success message
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: `✅ Code watching started!\n\n🤖 I'm now monitoring:\n${loadedCodebase}\n\nI'll notify you of any changes.`
      }]);
      
      // Start polling for status
      startStatusPolling();
    }
  } catch (error) {
    console.error('Failed to start watching:', error);
  }
};
```

### **Status Polling**

```typescript
const startStatusPolling = () => {
  const interval = setInterval(async () => {
    const status = await checkWatcherStatus();
    
    // Update UI with status
    setWatcherStatus(status);
    
    // If stopped, clear interval
    if (status.status === 'stopped') {
      clearInterval(interval);
    }
  }, 10000); // Check every 10 seconds
};
```

---

## 📊 UI Components for Akashic

### **Watcher Status Badge**

```typescript
const WatcherStatusBadge = ({ status }) => {
  const isActive = status?.status === 'running';
  
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '6px 12px',
      backgroundColor: isActive ? '#d1fae5' : '#fee2e2',
      borderRadius: '6px',
      fontSize: '12px'
    }}>
      <span>{isActive ? '🤖' : '⏸️'}</span>
      <span style={{ fontWeight: 'bold' }}>
        {isActive ? 'Watching' : 'Not Watching'}
      </span>
      {isActive && status.last_sync && (
        <span style={{ color: '#6b7280' }}>
          Last sync: {new Date(status.last_sync).toLocaleTimeString()}
        </span>
      )}
    </div>
  );
};
```

### **Control Buttons**

```typescript
<div style={{ display: 'flex', gap: '8px' }}>
  {!isWatching ? (
    <button onClick={handleStartWatching}>
      🤖 Start Code Watching
    </button>
  ) : (
    <button onClick={handleStopWatching}>
      ⏸️ Stop Watching
    </button>
  )}
  
  <button onClick={checkWatcherStatus}>
    🔄 Refresh Status
  </button>
</div>
```

---

## ✅ What's Available Now

**API Endpoints:**
- ✅ `POST /api/codebase/watch/start` - Start watching
- ✅ `POST /api/codebase/watch/stop/{id}` - Stop watching
- ✅ `GET /api/codebase/watch/status/{id}` - Get status
- ✅ `GET /api/codebase/watch/list` - List all watchers

**Features:**
- ✅ Git commit detection (5 second polling)
- ✅ Auto-indexing changed files
- ✅ Current state documentation
- ✅ Drift detection
- ✅ Team notifications
- ✅ Background task management

**Ready for Akashic Integration:**
- ✅ REST API endpoints
- ✅ JSON request/response
- ✅ Error handling
- ✅ Status tracking

---

## 🚀 Next Steps

**To integrate in Akashic:**

1. Add "Start Watching" button
2. Add status indicator
3. Poll for status updates
4. Show notifications in chat
5. Add stop/pause controls

**The API is ready - just needs UI integration!** 🎉
