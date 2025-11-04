# Continuous Monitoring API Endpoints

## Base URL
```
http://localhost:8002/api/akashic
```

---

## Workflow Endpoints

### 1. Analyze Repository
**POST** `/analyze`

Runs the initial workflow (Steps 1-4):
- Scans codebase
- Indexes for AI
- Analyzes patterns
- Generates project plan

```bash
curl -X POST http://localhost:8002/api/akashic/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "user_123",
    "org_id": "org_456",
    "repo_path": "/path/to/repo",
    "options": {
      "watch_files": true,
      "consolidate_docs": true,
      "generate_plan": true,
      "build_knowledge_graph": true,
      "index_for_search": true
    }
  }'
```

**Response:**
```json
{
  "status": "completed",
  "repo_path": "/path/to/repo",
  "started_at": "2025-10-31T20:00:00",
  "completed_at": "2025-10-31T20:05:00",
  "phases": {
    "code_scan": { "total_files": 27, "hot_files": [], "cold_files": [] },
    "docs_consolidation": { "total_docs": 10 },
    "project_plan": { "ticket_count": 0 },
    "knowledge_graph": { "node_count": 27 },
    "rag_indexing": { "chunk_count": 0 }
  },
  "output_dir": "/path/to/repo/.akashic"
}
```

---

## Continuous Monitoring Endpoints

### 2. Docs Consolidator

#### Start
**POST** `/monitoring/docs-consolidator/start/{entity_id}`

Starts watching `*.md` files and consolidating to `.akashic/docs/`

```bash
curl -X POST "http://localhost:8002/api/akashic/monitoring/docs-consolidator/start/user_123?repo_path=/path/to/repo"
```

**Response:**
```json
{
  "status": "started",
  "entity_id": "user_123",
  "watching": "*.md files",
  "output": "/path/to/repo/.akashic/docs/"
}
```

#### Stop
**POST** `/monitoring/docs-consolidator/stop/{entity_id}`

```bash
curl -X POST http://localhost:8002/api/akashic/monitoring/docs-consolidator/stop/user_123
```

---

### 3. Duplicate Detector

#### Start
**POST** `/monitoring/duplicate-detector/start/{entity_id}`

Starts detecting overlapping code and creating merge plans

```bash
curl -X POST "http://localhost:8002/api/akashic/monitoring/duplicate-detector/start/user_123?repo_path=/path/to/repo&similarity_threshold=0.7"
```

**Parameters:**
- `similarity_threshold` (optional): 0.0-1.0, default 0.7 (70% similarity)

**Response:**
```json
{
  "status": "started",
  "entity_id": "user_123",
  "similarity_threshold": 0.7,
  "watching": "All code files",
  "output": "/path/to/repo/.akashic/restructuring/"
}
```

#### Stop
**POST** `/monitoring/duplicate-detector/stop/{entity_id}`

```bash
curl -X POST http://localhost:8002/api/akashic/monitoring/duplicate-detector/stop/user_123
```

---

### 4. Linear Sync

#### Start
**POST** `/monitoring/linear-sync/start/{entity_id}`

Starts syncing tickets with Linear

```bash
curl -X POST "http://localhost:8002/api/akashic/monitoring/linear-sync/start/user_123?repo_path=/path/to/repo&linear_api_key=lin_api_xxx"
```

**Response:**
```json
{
  "status": "started",
  "entity_id": "user_123",
  "watching": "Code changes & Linear tickets",
  "output": "/path/to/repo/.akashic/pm/linear/"
}
```

#### Stop
**POST** `/monitoring/linear-sync/stop/{entity_id}`

```bash
curl -X POST http://localhost:8002/api/akashic/monitoring/linear-sync/stop/user_123
```

---

### 5. Monitoring Status

**GET** `/monitoring/status/{entity_id}`

Get status of all continuous monitoring services

```bash
curl http://localhost:8002/api/akashic/monitoring/status/user_123
```

**Response:**
```json
{
  "entity_id": "user_123",
  "file_watcher": {
    "active": true,
    "watching": "All files",
    "output": ".akashic/analysis/"
  },
  "docs_consolidator": {
    "active": true,
    "watching": "*.md files",
    "output": ".akashic/docs/"
  },
  "duplicate_detector": {
    "active": false,
    "watching": "Code files",
    "output": ".akashic/restructuring/"
  },
  "linear_sync": {
    "active": false,
    "watching": "Tickets & commits",
    "output": ".akashic/pm/linear/"
  }
}
```

---

### 6. Stop All Monitoring

**POST** `/stop-monitoring/{entity_id}`

Stops all monitoring services for an entity

```bash
curl -X POST http://localhost:8002/api/akashic/stop-monitoring/user_123
```

**Response:**
```json
{
  "status": "stopped",
  "entity_id": "user_123"
}
```

---

## File Tracking Endpoints

### Record File Open
**POST** `/record-file-open/{entity_id}`

```bash
curl -X POST "http://localhost:8002/api/akashic/record-file-open/user_123?file_path=src/main.py"
```

### Record File Close
**POST** `/record-file-close/{entity_id}`

```bash
curl -X POST "http://localhost:8002/api/akashic/record-file-close/user_123?file_path=src/main.py"
```

### Record File Run
**POST** `/record-file-run/{entity_id}`

```bash
curl -X POST "http://localhost:8002/api/akashic/record-file-run/user_123?file_path=src/main.py"
```

---

## Integration with Akashic IDE

The Akashic IDE calls these endpoints when you click the monitoring buttons:

```typescript
// Start Docs Consolidator
const startDocsConsolidation = async () => {
  const response = await fetch(
    `http://localhost:8002/api/akashic/monitoring/docs-consolidator/start/${entityId}?repo_path=${loadedCodebase}`,
    { method: 'POST' }
  );
  const data = await response.json();
  setIsDocsConsolidating(true);
};

// Start Duplicate Detector
const startDuplicateDetector = async () => {
  const response = await fetch(
    `http://localhost:8002/api/akashic/monitoring/duplicate-detector/start/${entityId}?repo_path=${loadedCodebase}&similarity_threshold=0.7`,
    { method: 'POST' }
  );
  const data = await response.json();
  setIsDuplicateDetecting(true);
};

// Get Status
const getMonitoringStatus = async () => {
  const response = await fetch(
    `http://localhost:8002/api/akashic/monitoring/status/${entityId}`
  );
  const data = await response.json();
  // Update UI with status
};
```

---

## Implementation Status

✅ **Implemented:**
- Workflow endpoints (analyze repository)
- File tracking endpoints
- Monitoring status endpoint
- API structure for all services

🚧 **TODO (Backend Implementation):**
- Docs Consolidator service logic
- Duplicate Detector service logic
- Linear Sync service logic

The API endpoints are ready, but the actual service implementations need to be built. The endpoints currently return success responses but don't perform the actual monitoring yet.

---

## Next Steps

1. **Implement Docs Consolidator Service**
   - Watch for `*.md` files using file system watcher
   - Parse and consolidate content
   - Write to `.akashic/docs/`
   - Remove original files

2. **Implement Duplicate Detector Service**
   - Use semantic code analysis (embeddings)
   - Compare code similarity
   - Generate merge plans
   - Create Cursor/Windsurf prompts

3. **Implement Linear Sync Service**
   - Connect to Linear API
   - Watch for code commits
   - Update ticket status
   - Sync bidirectionally

4. **Add WebSocket Support**
   - Real-time updates to Akashic IDE
   - Live monitoring status
   - Instant notifications

5. **Add Configuration**
   - Read from `.akashic/config/.akashic.yml`
   - Allow customization of thresholds
   - Enable/disable services per project
