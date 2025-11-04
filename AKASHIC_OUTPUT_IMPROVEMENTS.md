# Akashic Output Improvements - Roadmap

## 🎯 Current Issues

After running analysis, several folders are empty or incomplete:

### **Empty/Missing:**
- ❌ `analysis/current_state/` - Empty
- ❌ `analysis/future_state/` - Empty  
- ❌ `docs/diagrams/rendered/` - Empty (mermaid not rendered)
- ❌ `docs/mermaid_diagrams/` - Empty
- ❌ `docs/project_plans/` - Empty

### **Working:**
- ✅ `docs/PROJECT_DOCS.md` - Good!
- ✅ `docs/diagrams/mermaid/*.md` - Mermaid code generated
- ✅ `analysis/CURRENT_STATE.md` - Generated
- ✅ `analysis/FUTURE_STATE.md` - Generated

---

## 📊 What's Happening Now

### **Current Folder Structure:**

```
.akashic/
├── analysis/
│   ├── CURRENT_STATE.md          ✅ Generated (single file)
│   ├── FUTURE_STATE.md            ✅ Generated (single file)
│   ├── ISSUES_REPORT.md           ✅ Generated
│   ├── RESTRUCTURING_PLAN.md      ✅ Generated
│   ├── current_state/             ❌ Empty (should have detailed files)
│   └── future_state/              ❌ Empty (should have detailed files)
├── docs/
│   ├── PROJECT_DOCS.md            ✅ Generated (good!)
│   ├── diagrams/
│   │   ├── mermaid/
│   │   │   ├── file_temperature.md      ✅ Mermaid code
│   │   │   ├── project_structure.md     ✅ Mermaid code
│   │   │   └── analysis_flow.md         ✅ Mermaid code
│   │   └── rendered/              ❌ Empty (should have PNG/SVG)
│   ├── mermaid_diagrams/          ❌ Empty (duplicate?)
│   └── project_plans/             ❌ Empty (should have plans)
├── pm/                            ⏳ Not implemented yet
│   ├── linear/
│   └── jira/
└── config/
    └── .akashic.yml               ✅ Generated
```

---

## 🔧 Improvements Needed

### **Phase 1: Expand Analysis Outputs** (High Priority)

#### **1.1 Current State Breakdown**

Instead of single `CURRENT_STATE.md`, create detailed breakdown:

```
analysis/current_state/
├── README.md                    # Overview
├── file_inventory.md            # All files with metadata
├── hot_files_analysis.md        # Active development areas
├── cold_files_analysis.md       # Unused/stale code
├── dependencies.md              # External dependencies
├── tech_stack.md                # Technologies used
└── metrics.md                   # Code metrics
```

**Implementation:**
```python
async def _generate_current_state_breakdown(self, output_dir: Path, results: Dict):
    """Generate detailed current state analysis"""
    current_state_dir = output_dir / "analysis" / "current_state"
    current_state_dir.mkdir(parents=True, exist_ok=True)
    
    scan_data = results['phases'].get('code_scan', {})
    
    # 1. File Inventory
    inventory = self._generate_file_inventory(scan_data)
    (current_state_dir / "file_inventory.md").write_text(inventory)
    
    # 2. Hot Files Analysis
    hot_analysis = self._generate_hot_files_analysis(scan_data.get('hot_files', []))
    (current_state_dir / "hot_files_analysis.md").write_text(hot_analysis)
    
    # 3. Cold Files Analysis
    cold_analysis = self._generate_cold_files_analysis(scan_data.get('cold_files', []))
    (current_state_dir / "cold_files_analysis.md").write_text(cold_analysis)
    
    # 4. Dependencies
    deps = self._analyze_dependencies(scan_data)
    (current_state_dir / "dependencies.md").write_text(deps)
    
    # 5. Tech Stack
    tech = self._analyze_tech_stack(scan_data)
    (current_state_dir / "tech_stack.md").write_text(tech)
    
    # 6. Metrics
    metrics = self._generate_metrics(scan_data)
    (current_state_dir / "metrics.md").write_text(metrics)
```

#### **1.2 Future State Planning**

Instead of single `FUTURE_STATE.md`, create actionable plans:

```
analysis/future_state/
├── README.md                    # Overview
├── roadmap.md                   # Timeline and milestones
├── features_to_implement.md     # Planned features
├── refactoring_plan.md          # Code improvements
├── deprecation_plan.md          # What to remove
└── migration_plan.md            # Technology migrations
```

#### **1.3 Project Plans**

Create structured project plans:

```
docs/project_plans/
├── README.md                    # Overview
├── epic_1_infrastructure.md     # Infrastructure improvements
├── epic_2_features.md           # New features
├── epic_3_refactoring.md        # Code quality
└── sprint_breakdown.md          # Sprint planning
```

---

### **Phase 2: Render Mermaid Diagrams** (Medium Priority)

#### **2.1 Install Mermaid CLI**

```bash
# In Apollo container
npm install -g @mermaid-js/mermaid-cli
```

#### **2.2 Render Diagrams**

```python
async def _render_mermaid_diagrams(self, output_dir: Path):
    """Render mermaid diagrams to PNG/SVG"""
    import subprocess
    
    mermaid_dir = output_dir / "docs" / "diagrams" / "mermaid"
    rendered_dir = output_dir / "docs" / "diagrams" / "rendered"
    rendered_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all mermaid files
    for mermaid_file in mermaid_dir.glob("*.md"):
        output_png = rendered_dir / f"{mermaid_file.stem}.png"
        output_svg = rendered_dir / f"{mermaid_file.stem}.svg"
        
        try:
            # Render to PNG
            subprocess.run([
                "mmdc",
                "-i", str(mermaid_file),
                "-o", str(output_png),
                "-t", "dark",
                "-b", "transparent"
            ], check=True)
            
            # Render to SVG
            subprocess.run([
                "mmdc",
                "-i", str(mermaid_file),
                "-o", str(output_svg),
                "-t", "dark",
                "-b", "transparent"
            ], check=True)
            
            logger.info(f"✅ Rendered {mermaid_file.name}")
        except Exception as e:
            logger.error(f"❌ Failed to render {mermaid_file.name}: {e}")
```

**Result:**
```
docs/diagrams/rendered/
├── file_temperature.png
├── file_temperature.svg
├── project_structure.png
├── project_structure.svg
├── analysis_flow.png
└── analysis_flow.svg
```

---

### **Phase 3: PM Integration** (Low Priority - After Core Features)

#### **3.1 Linear Integration**

```
pm/linear/
├── README.md                    # Integration status
├── tickets.json                 # Generated tickets
├── epics.json                   # Epic structure
└── sync_log.md                  # Sync history
```

#### **3.2 Jira Integration**

```
pm/jira/
├── README.md                    # Integration status
├── issues.json                  # Generated issues
├── epics.json                   # Epic structure
└── sync_log.md                  # Sync history
```

---

## 🎯 Implementation Priority

### **Priority 1: Expand Analysis Outputs** ⭐⭐⭐

**Why:** Users need detailed breakdowns, not just summary files

**Tasks:**
1. Create `current_state/` breakdown (7 files)
2. Create `future_state/` planning (6 files)
3. Create `project_plans/` structure (5 files)

**Estimated Time:** 2-3 hours

**Impact:** High - Makes analysis actually useful

---

### **Priority 2: Render Mermaid Diagrams** ⭐⭐

**Why:** Visual diagrams are more useful than code blocks

**Tasks:**
1. Install mermaid-cli in Apollo container
2. Implement `_render_mermaid_diagrams()` function
3. Generate PNG and SVG for each diagram

**Estimated Time:** 1-2 hours

**Impact:** Medium - Nice to have, but not critical

---

### **Priority 3: PM Integration** ⭐

**Why:** Automated ticket creation is powerful but complex

**Tasks:**
1. Implement Linear API integration
2. Implement Jira API integration
3. Create ticket generation logic
4. Handle authentication and sync

**Estimated Time:** 4-6 hours

**Impact:** High - But only after core features work

---

## 🚀 Quick Wins

### **Immediate Improvements (30 minutes):**

1. **Create placeholder README files:**
   ```python
   # Add to _save_results()
   (output_dir / "analysis" / "current_state" / "README.md").write_text("# Current State Analysis\n\nDetailed breakdown coming soon...")
   (output_dir / "analysis" / "future_state" / "README.md").write_text("# Future State Planning\n\nDetailed plans coming soon...")
   (output_dir / "docs" / "project_plans" / "README.md").write_text("# Project Plans\n\nStructured plans coming soon...")
   ```

2. **Copy mermaid files to mermaid_diagrams/ (for compatibility):**
   ```python
   # Duplicate mermaid files
   import shutil
   mermaid_src = output_dir / "docs" / "diagrams" / "mermaid"
   mermaid_dst = output_dir / "docs" / "mermaid_diagrams"
   if mermaid_src.exists():
       shutil.copytree(mermaid_src, mermaid_dst, dirs_exist_ok=True)
   ```

3. **Add note about rendered diagrams:**
   ```python
   # Add to rendered/ folder
   (output_dir / "docs" / "diagrams" / "rendered" / "README.md").write_text(
       "# Rendered Diagrams\n\n"
       "Mermaid diagram rendering coming soon!\n\n"
       "For now, view the mermaid code in `../mermaid/` and paste into:\n"
       "https://mermaid.live/\n"
   )
   ```

---

## 📝 Summary

**Current State:**
- ✅ Basic analysis works
- ✅ PROJECT_DOCS.md is good
- ✅ Mermaid code generated
- ❌ Many folders empty
- ❌ No diagram rendering
- ❌ No PM integration

**Next Steps:**
1. **Expand analysis outputs** (Priority 1)
2. **Render mermaid diagrams** (Priority 2)
3. **PM integration** (Priority 3 - after core features)

**Quick Wins:**
- Add README files to empty folders
- Copy mermaid files for compatibility
- Add instructions for viewing diagrams

**Files to Modify:**
- `Apollo/services/akashic_intelligence_orchestrator.py`
- Add new helper functions for detailed breakdowns
- Add mermaid rendering logic
- Add PM integration (later)
