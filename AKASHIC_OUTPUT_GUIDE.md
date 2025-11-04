# Akashic Output Files Guide

## What Each File Does

### **📊 analysis/CURRENT_STATE.md**
**Purpose:** Snapshot of the codebase right now
- File activity (hot/warm/cool/cold)
- Code quality metrics
- Documentation coverage
- Test coverage
- Immediate recommendations

### **📚 docs/PROJECT_DOCS.md**
**Purpose:** Consolidated documentation + source for PM integrations
- All documentation content in one place
- Extracted TODO/FIXME/FUTURE items → Linear/Jira tickets
- Feature descriptions → GitHub issues
- Requirements → Project planning
- **This is the source for auto-creating tickets!**

### **🎯 planning/FUTURE_STATE.md**
**Purpose:** Where the project is headed
- Planned features (from TODO/FIXME markers)
- Roadmap items
- Version planning
- Feature priorities
- **Source for sprint planning**

### **⚠️ issues/ISSUES_REPORT.md**
**Purpose:** Problems that need fixing
- Technical debt
- Code smells
- Security issues
- Performance problems
- Deprecated code
- **Source for bug tickets and cleanup tasks**

### **🔄 restructuring/RESTRUCTURING_PLAN.md**
**Purpose:** How to reorganize the codebase
- Duplicate code detection
- Scattered functionality
- Files to merge/move/delete
- Refactoring suggestions
- **Source for refactoring tickets**

### **📈 diagrams/mermaid/**
**Purpose:** Visual representations
- Architecture diagrams
- Data flow
- File relationships
- **For documentation and onboarding**

### **📋 pm/**
**Purpose:** PM tool integration data
- Linear tickets (auto-created)
- Jira issues (auto-synced)
- GitHub issues (auto-generated)
- Bitbucket tasks
- **Automated ticket creation from docs**

---

## How They Work Together

```
PROJECT_DOCS.md (source)
    ↓
Extract TODOs/Features
    ↓
FUTURE_STATE.md (planning)
    ↓
Create Tickets
    ↓
pm/linear/ (tickets)
```

```
CURRENT_STATE.md (analysis)
    ↓
Identify Problems
    ↓
ISSUES_REPORT.md (bugs)
    ↓
Create Bug Tickets
    ↓
pm/jira/ (issues)
```

```
CURRENT_STATE.md (cold files)
    ↓
Detect Duplicates
    ↓
RESTRUCTURING_PLAN.md (refactor)
    ↓
Create Refactor Tickets
    ↓
pm/github/ (tasks)
```
