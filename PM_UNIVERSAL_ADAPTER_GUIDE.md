# PM Universal Adapter - Complete Guide

## Overview

The **Universal PM Adapter** provides a single abstraction layer that maps between all PM tools, enabling:
1. **Bidirectional sync** between local `.akashic/` and cloud PM tools
2. **Documentation-to-tickets** conversion
3. **Cross-tool compatibility** (Linear ↔ Jira ↔ GitHub ↔ Bitbucket)

## Universal Ticket Format

All PM tools map to this single format:

```python
UniversalTicket(
    id="task-123",
    title="Add user authentication",
    description="Implement JWT auth...",
    type=TicketType.TASK,
    status=TicketStatus.IN_PROGRESS,
    priority=TicketPriority.HIGH,
    parent_id="story-456",
    epic_id="epic-789",
    assignee="john@example.com",
    team="backend-team",
    labels=["backend", "security"],
    affected_files=["api/auth.py"],
    story_points=5,
    suggested_agent="Backend Specialist",
    source_tool=PMTool.LINEAR,
    source_id="LIN-123",
    synced_to={
        PMTool.JIRA: "PROJ-456",
        PMTool.GITHUB: "789"
    }
)
```

## PM Tool Mappings

### Linear ↔ Universal

| Universal | Linear |
|-----------|--------|
| EPIC | initiative |
| STORY | feature |
| TASK | task |
| BUG | bug |
| SUBTASK | sub-issue |
| Priority 1-4 | 1=Critical, 4=Low |

### Jira ↔ Universal

| Universal | Jira |
|-----------|------|
| EPIC | Epic |
| STORY | Story |
| TASK | Task |
| BUG | Bug |
| SUBTASK | Sub-task |
| SPIKE | Spike |
| Priority | Highest/High/Medium/Low/Lowest |

### GitHub ↔ Universal

| Universal | GitHub |
|-----------|--------|
| EPIC | label: "epic" |
| STORY | label: "enhancement" |
| TASK | label: "task" |
| BUG | label: "bug" |
| Priority | label: "priority: high" |
| Status | open/closed + labels |

## Usage Examples

### 1. Convert Documentation to Tickets

```python
from services.pm_universal_adapter import DocumentationToTicketConverter

# Convert feature doc to tickets
converter = DocumentationToTicketConverter()
tickets = converter.convert_feature_docs_to_tickets("docs/features/auth.md")

# Result: 1 Epic + 3 Stories + 10 Tasks
for ticket in tickets:
    print(f"{ticket.type.value}: {ticket.title}")
```

**Documentation Format:**
```markdown
# User Authentication (Epic)

Description of the feature...

## User Story 1: Login Flow
As a user, I want to log in with email/password...

### Implementation Tasks
- Create login API endpoint
- Add JWT token generation
- Implement token validation

## User Story 2: Password Reset
As a user, I want to reset my password...

### Implementation Tasks
- Create password reset API
- Send reset email
- Validate reset token
```

**Generated Tickets:**
- 1 Epic: "User Authentication"
- 2 Stories: "Login Flow", "Password Reset"
- 6 Tasks: "Create login API endpoint", etc.

### 2. Sync to Multiple PM Tools

```python
from services.pm_universal_adapter import PMToolMapping, PMTool

# Convert to Linear format
linear_data = PMToolMapping.to_tool_format(ticket, PMTool.LINEAR)

# Create in Linear
linear_api.create_issue(linear_data)

# Convert to Jira format
jira_data = PMToolMapping.to_tool_format(ticket, PMTool.JIRA)

# Create in Jira
jira_api.create_issue(jira_data)

# Convert to GitHub format
github_data = PMToolMapping.to_tool_format(ticket, PMTool.GITHUB)

# Create in GitHub
github_api.create_issue(github_data)
```

### 3. Bidirectional Sync

```python
from services.pm_universal_adapter import BidirectionalSync

sync = BidirectionalSync(repo_path="/path/to/repo")

# Sync with all PM tools
await sync.sync([PMTool.LINEAR, PMTool.JIRA, PMTool.GITHUB])

# Process:
# 1. Load local tickets from .akashic/pm/tickets.json
# 2. Load remote tickets from Linear, Jira, GitHub
# 3. Detect conflicts (same ticket modified in multiple places)
# 4. Resolve conflicts (last-write-wins)
# 5. Sync changes bidirectionally
# 6. Save updated tickets locally
```

### 4. Import from PM Tool

```python
# Fetch from Linear
linear_issues = linear_api.get_issues(project_id="PROJ")

# Convert to universal format
universal_tickets = [
    PMToolMapping.from_tool_format(issue, PMTool.LINEAR)
    for issue in linear_issues
]

# Sync to Jira
for ticket in universal_tickets:
    jira_data = PMToolMapping.to_tool_format(ticket, PMTool.JIRA)
    jira_api.create_issue(jira_data)
    
    # Track sync
    ticket.synced_to[PMTool.JIRA] = jira_issue_key
```

## Workflow: Documentation → Tickets → Agents

### Step 1: Write Feature Documentation

```markdown
# Payment Integration

Integrate Stripe payment processing.

## User Story: Accept Payments
As a user, I want to pay with credit card...

### Backend Tasks
- Create Stripe API client
- Add payment endpoint
- Store payment records

### Frontend Tasks
- Create payment form
- Add card validation
- Show payment confirmation
```

### Step 2: Convert to Tickets

```python
converter = DocumentationToTicketConverter()
tickets = converter.convert_feature_docs_to_tickets("docs/features/payment.md")

# Enrichment: Add technical details from .akashic analysis
for ticket in tickets:
    if ticket.type == TicketType.TASK:
        # Find affected files
        ticket.affected_files = find_affected_files(ticket.title)
        
        # Suggest specialist agent
        ticket.suggested_agent = suggest_agent(ticket)
        
        # Estimate complexity
        ticket.estimated_complexity = estimate_complexity(ticket)
```

### Step 3: Sync to PM Tools

```python
# Sync to Linear
for ticket in tickets:
    linear_data = PMToolMapping.to_tool_format(ticket, PMTool.LINEAR)
    linear_id = linear_api.create_issue(linear_data)
    ticket.synced_to[PMTool.LINEAR] = linear_id

# Sync to Jira
for ticket in tickets:
    jira_data = PMToolMapping.to_tool_format(ticket, PMTool.JIRA)
    jira_key = jira_api.create_issue(jira_data)
    ticket.synced_to[PMTool.JIRA] = jira_key

# Save locally
save_tickets(tickets, ".akashic/pm/tickets.json")
```

### Step 4: Assign to Specialist Agents

```python
from services.specialist_agents import SpecialistAgentRegistry

for ticket in tickets:
    if ticket.type == TicketType.TASK:
        # Match to specialist agent
        agent = SpecialistAgentRegistry.match_agent({
            "title": ticket.title,
            "affected_files": ticket.affected_files,
            "labels": ticket.labels
        })
        
        # Assign ticket to agent
        ticket.assignee = agent.name
        ticket.suggested_agent = agent.name
        
        # Update in PM tools
        update_ticket_in_all_tools(ticket)
```

## Conflict Resolution

### Scenario: Ticket Modified in Multiple Places

**Local (.akashic):**
```json
{
  "id": "task-123",
  "title": "Add user auth",
  "status": "in_progress",
  "updated_at": "2024-11-02T10:00:00Z"
}
```

**Linear:**
```json
{
  "id": "LIN-123",
  "title": "Add user authentication (updated)",
  "state": "In Progress",
  "updatedAt": "2024-11-02T11:00:00Z"
}
```

**Resolution Strategy:**
1. **Detect conflict:** Both modified after last sync
2. **Compare timestamps:** Linear updated later (11:00 vs 10:00)
3. **Last-write-wins:** Use Linear version
4. **Update local:** Sync Linear changes to local
5. **Propagate:** Update Jira/GitHub with Linear version

### Manual Resolution (Future)

For critical conflicts, prompt user:
```
Conflict detected for ticket "Add user auth":

Local: status=in_progress, updated 10:00
Linear: status=in_progress, title changed, updated 11:00
Jira: status=done, updated 10:30

Which version should win?
1. Local
2. Linear
3. Jira
4. Manual merge
```

## File Structure

```
.akashic/
├── pm/
│   ├── tickets.json          # All tickets in universal format
│   ├── sync_log.json         # Sync history
│   └── conflicts.json        # Unresolved conflicts
```

**tickets.json:**
```json
[
  {
    "id": "epic-789",
    "title": "Payment Integration",
    "type": "epic",
    "status": "in_progress",
    "synced_to": {
      "linear": "LIN-789",
      "jira": "PROJ-789",
      "github": "123"
    }
  },
  {
    "id": "story-456",
    "title": "Accept Payments",
    "type": "story",
    "epic_id": "epic-789",
    "synced_to": {
      "linear": "LIN-456",
      "jira": "PROJ-456"
    }
  }
]
```

## API Endpoints (Future)

```python
# Convert documentation to tickets
POST /api/pm/convert-docs
{
  "doc_path": "docs/features/auth.md",
  "target_tools": ["linear", "jira"]
}

# Sync tickets
POST /api/pm/sync
{
  "tools": ["linear", "jira", "github"]
}

# Get ticket status across all tools
GET /api/pm/tickets/{ticket_id}/status
Response:
{
  "local": {"status": "in_progress"},
  "linear": {"status": "In Progress", "id": "LIN-123"},
  "jira": {"status": "In Progress", "key": "PROJ-456"},
  "github": {"state": "open", "number": 789}
}
```

## Benefits

1. **Single Source of Truth:** Local `.akashic/` folder
2. **Multi-Tool Support:** Works with Linear, Jira, GitHub, Bitbucket
3. **Documentation-Driven:** Convert docs to tickets automatically
4. **Conflict Resolution:** Automatic conflict detection and resolution
5. **Agent Integration:** Tickets include specialist agent suggestions
6. **Bidirectional Sync:** Changes flow both ways
7. **No Vendor Lock-in:** Switch PM tools anytime

## Next Steps

1. Implement Linear API client
2. Implement Jira API client
3. Implement GitHub API client
4. Build conflict resolution UI
5. Add webhook support for real-time sync
6. Create Akashic IDE integration

---

**This is the foundation for autonomous development: Documentation → Tickets → Agents → Code!** 🚀
