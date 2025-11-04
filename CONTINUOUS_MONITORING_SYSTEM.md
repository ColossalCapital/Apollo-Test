# Continuous Monitoring System - Akashic Intelligence

## Overview
The Continuous Monitoring system watches your **codebase** for changes and automatically updates the **`.akashic/` directory** with analysis, plans, and recommendations. It runs continuously in the background after the initial workflow completes.

## How It Works

```
Codebase Changes → Continuous Monitors → .akashic/ Updates → Actionable Plans
```

The monitors watch your code, detect patterns/issues, and generate plans that can be used to create precise prompts for Cursor/Windsurf/other AI tools.

---

## Monitoring Services

### 1. 👁️ **File Watcher**
**Watches:** All files in the codebase  
**Updates:** `.akashic/analysis/`

**What it does:**
- Tracks file edit frequency (hot/warm/cool/cold)
- Detects TODO/FIXME/FUTURE markers
- Updates file metrics in real-time
- Identifies files that haven't been touched in a while

**Output:**
- `.akashic/analysis/file_metrics.json` - Real-time file statistics
- `.akashic/analysis/CURRENT_STATE.md` - Updated state analysis

**Use Case:**
While coding in Cursor, the File Watcher notices you haven't touched `old_feature.py` in 3 months. It marks it as "cold" and suggests archival in the next analysis update.

---

### 2. 📝 **Docs Consolidator**
**Watches:** `*.md` files throughout the codebase  
**Updates:** `.akashic/docs/`

**What it does:**
- Monitors for new `.md` files created by Cursor/Windsurf
- Consolidates documentation into `.akashic/docs/`
- Removes redundant `.md` files from codebase directories
- Merges overlapping documentation
- Maintains a single source of truth

**Output:**
- `.akashic/docs/PROJECT_DOCS.md` - Consolidated documentation
- `.akashic/docs/current_state/` - Current documentation state
- `.akashic/docs/future_state/` - Planned documentation

**Use Case:**
```
You use Cursor to generate a feature:
1. Cursor creates: /features/auth/AUTH_DESIGN.md
2. Docs Consolidator detects the new .md file
3. Consolidates content into .akashic/docs/PROJECT_DOCS.md
4. Removes AUTH_DESIGN.md from /features/auth/
5. Updates .akashic/docs/ with consolidated info
```

**Result:** Clean codebase, all docs in one place.

---

### 3. 🗺️ **Functionality Mapper** (NEW)
**Watches:** Code organization and functionality implementation  
**Updates:** `.akashic/restructuring/`

**What it does:**
- Maps how functionality is implemented across the codebase
- Detects agents/modules with overlapping functionality in different directories
- Identifies organizational issues (e.g., similar agents scattered across dirs)
- Analyzes code structure and relationships
- Creates reorganization plans
- Generates specific prompts for AI tools

**Output:**
- `.akashic/restructuring/MERGE_PLAN.md` - Detailed merge strategy
- `.akashic/restructuring/DUPLICATE_REPORT.md` - List of duplicates
- `.akashic/planning/REFACTOR_PROMPTS.md` - Ready-to-use prompts

**Use Case:**
```
Scenario (Apollo Repo Example):
1. You're building Apollo AI agents
2. You create: /agents/auth/authentication_agent.py
3. Later, you create: /services/security/auth_service.py
4. Both handle authentication but in different directories

Functionality Mapper:
1. Maps all authentication-related functionality
2. Detects overlap between /agents/auth/ and /services/security/
3. Analyzes which structure is better
4. Creates reorganization plan in .akashic/restructuring/REORGANIZATION_PLAN.md:

   ## Reorganization Plan: Authentication Functionality
   
   **Overlapping Functionality Detected:**
   - `/agents/auth/authentication_agent.py` (150 lines)
   - `/services/security/auth_service.py` (200 lines)
   - `/utils/auth_helpers.py` (50 lines)
   
   **Analysis:**
   - All three handle authentication
   - Scattered across 3 different directories
   - Creates confusion about where auth logic lives
   
   **Recommended Structure:**
   ```
   /agents/auth/
   ├── authentication_agent.py  (main agent)
   ├── auth_service.py          (service layer)
   └── auth_utils.py            (helpers)
   ```
   
   **Action Plan:**
   1. Move: /services/security/auth_service.py → /agents/auth/
   2. Move: /utils/auth_helpers.py → /agents/auth/auth_utils.py
   3. Update: All imports to point to new locations
   4. Consolidate: Duplicate token validation logic
   
   **Cursor Prompt:**
   ```
   Reorganize authentication code:
   1. Move /services/security/auth_service.py to /agents/auth/auth_service.py
   2. Move /utils/auth_helpers.py to /agents/auth/auth_utils.py
   3. Update all imports throughout the codebase
   4. Remove duplicate token validation - use the one in auth_service.py
   ```

5. You copy the prompt to Cursor
6. Cursor executes the reorganization perfectly
7. Functionality Mapper updates .akashic/ to reflect new structure
```

**Result:** Clean organization, all auth code in one place, easy to find and maintain.

---

### 4. 🔄 **PM Sync** (Project Management Sync)
**Watches:** Code changes and PM tool status  
**Updates:** `.akashic/pm/`

**What it does:**
- Syncs with multiple PM tools: Linear, Jira, GitHub, Bitbucket
- Tracks ticket/issue progress based on code changes
- Auto-updates status when code is committed
- Creates new tickets/issues for detected problems
- Bidirectional sync (code → PM tools, PM tools → code)

**Output:**
- `.akashic/pm/linear/tickets.json` - Linear tickets
- `.akashic/pm/jira/issues.json` - Jira issues
- `.akashic/pm/github/issues.json` - GitHub issues
- `.akashic/pm/bitbucket/prs.json` - Bitbucket PRs
- `.akashic/pm/*/sprint_plan.md` - Sprint planning
- `.akashic/pm/*/sync_log.json` - Sync history

**Use Case:**
```
1. Linear ticket: "Implement user login"
2. You commit code to /auth/login.py with message: "feat: add login #LIN-123"
3. PM Sync detects the commit
4. Updates Linear ticket LIN-123 status to "In Review"
5. Creates GitHub issue if tests fail
6. Logs all activity in .akashic/pm/
7. Syncs sprint progress across all tools
```

---

## Workflow Integration

### Initial Workflow (One-time)
```
1️⃣ Analyze Repo → Scan entire codebase
2️⃣ Index for AI → Build semantic index
3️⃣ Deep Analysis → Analyze patterns
4️⃣ Generate Plan → Create project plan
```

### Continuous Monitoring (Always Running)
```
👁️ File Watcher → Tracks all file changes
📝 Docs Consolidator → Manages documentation
🗺️ Functionality Mapper → Maps code organization
🔄 PM Sync → Syncs with PM tools (Linear, Jira, GitHub, Bitbucket)
```

---

## Benefits

### 1. **Clean Codebase**
- No scattered `.md` files
- No duplicate functionality
- Organized documentation

### 2. **Stay On Track**
- Duplicate detection prevents drift
- Merge plans keep architecture clean
- Project plans guide development

### 3. **AI Tool Integration**
- Generated prompts work perfectly with Cursor/Windsurf
- Specific, actionable instructions
- Context-aware suggestions

### 4. **Automatic Maintenance**
- Continuous updates without manual work
- Real-time analysis
- Always up-to-date project state

---

## Example: Full Workflow

### Day 1: Initial Setup
```bash
# Run initial workflow
1️⃣ Analyze Repo
2️⃣ Index for AI
3️⃣ Deep Analysis
4️⃣ Generate Plan

# Turn on continuous monitoring
👁️ File Watcher: ON
📝 Docs Consolidator: ON
🔍 Duplicate Detector: ON
🔄 Linear Sync: ON
```

### Day 2-30: Development
```
You work in Cursor/Windsurf:
├─ Create features
├─ Generate code
├─ Write docs
└─ Make changes

Continuous Monitoring:
├─ Watches all changes
├─ Consolidates docs
├─ Detects duplicates
├─ Updates .akashic/
└─ Creates merge plans
```

### Result
```
.akashic/
├── analysis/          ✅ Always current
├── docs/              ✅ Consolidated
├── planning/          ✅ Up-to-date
├── issues/            ✅ Auto-detected
├── restructuring/     ✅ Merge plans ready
└── pm/linear/         ✅ Tickets synced
```

---

## Configuration

Edit `.akashic/config/.akashic.yml`:

```yaml
version: 1.0.0
auto_sync: true

continuous_monitoring:
  file_watcher:
    enabled: true
    scan_interval: 5  # seconds
    
  docs_consolidator:
    enabled: true
    watch_patterns: ["*.md", "*.txt"]
    auto_remove: true  # Remove from codebase after consolidation
    
  duplicate_detector:
    enabled: true
    similarity_threshold: 0.7  # 70% similarity = duplicate
    scan_interval: 60  # seconds
    
  linear_sync:
    enabled: true
    sync_interval: 300  # 5 minutes

pm_integrations:
  linear:
    enabled: true
  jira:
    enabled: false
  github:
    enabled: true
  bitbucket:
    enabled: false
```

---

## Future Enhancements

- **Jira Integration** - Same as Linear
- **GitHub Issues Sync** - Auto-create issues from detected problems
- **Bitbucket Integration** - PR tracking
- **Slack Notifications** - Alert when duplicates detected
- **Auto-PR Creation** - Create PRs for merge plans
- **Code Quality Monitoring** - Track complexity, test coverage
- **Security Scanning** - Detect vulnerabilities
- **Performance Monitoring** - Track performance regressions

---

## Summary

The Continuous Monitoring system is your **always-on project guardian**:

✅ Keeps codebase clean  
✅ Prevents duplicate work  
✅ Maintains documentation  
✅ Generates actionable plans  
✅ Integrates with AI tools  
✅ Keeps project on track  

**Turn it on once, benefit forever.** 🚀
