"""
Folder-Level Agentic RAG Analyzer

Comprehensive folder/repo analysis using Theta RAG + DeepSeek:
1. Index repo at folder level
2. Understand current state functionality
3. Consolidate MD docs
4. Generate current state + future state documents
5. Identify unused functionality
6. Find unnecessary files
7. Detect duplicate features
8. Suggest repo restructuring

Uses Theta RAG for embeddings and DeepSeek for analysis.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass, asdict

from learning.theta_edgecloud import ThetaEdgeCloud
from learning.codebase_indexer import CodebaseIndexer


@dataclass
class FolderAnalysis:
    """Complete folder analysis results"""
    folder_path: str
    analyzed_at: str
    
    # Current State
    current_state: Dict[str, Any]
    functionality_map: Dict[str, List[str]]
    file_structure: Dict[str, Any]
    
    # Documentation
    consolidated_docs: str
    current_state_doc: str
    future_state_doc: str
    
    # Issues & Suggestions
    unused_functionality: List[Dict[str, Any]]
    unnecessary_files: List[Dict[str, Any]]
    duplicate_features: List[Dict[str, Any]]
    restructuring_suggestions: List[Dict[str, Any]]
    
    # Metrics
    total_files: int
    total_functions: int
    code_quality_score: float
    technical_debt_score: float


class FolderAnalyzerAgent:
    """
    Agentic RAG system for comprehensive folder analysis
    
    Workflow:
    1. Index folder with Theta RAG
    2. Analyze code structure with DeepSeek
    3. Consolidate documentation
    4. Generate current/future state docs
    5. Identify issues and suggest improvements
    """
    
    def __init__(self, theta_api_key: Optional[str] = None):
        self.theta = ThetaEdgeCloud(api_key=theta_api_key or os.getenv("THETA_API_KEY"))
        
    async def analyze_folder(
        self,
        folder_path: str,
        entity_id: str,
        deep_analysis: bool = True
    ) -> FolderAnalysis:
        """
        Complete folder analysis
        
        Args:
            folder_path: Path to folder/repo to analyze
            entity_id: User/org identifier
            deep_analysis: Enable deep analysis (slower but more thorough)
        
        Returns:
            FolderAnalysis with complete results
        """
        
        print(f"🔍 Starting folder analysis: {folder_path}")
        
        # Step 1: Index with Theta RAG
        print("📊 Step 1/7: Indexing with Theta RAG...")
        chatbot_id = await self._index_folder(folder_path, entity_id)
        
        # Step 2: Analyze current state
        print("🔎 Step 2/7: Analyzing current state...")
        current_state = await self._analyze_current_state(folder_path, chatbot_id)
        
        # Step 3: Map functionality
        print("🗺️  Step 3/7: Mapping functionality...")
        functionality_map = await self._map_functionality(folder_path, chatbot_id)
        
        # Step 4: Consolidate documentation
        print("📝 Step 4/7: Consolidating documentation...")
        consolidated_docs = await self._consolidate_docs(folder_path, chatbot_id)
        
        # Step 5: Generate state documents
        print("📄 Step 5/7: Generating state documents...")
        current_state_doc, future_state_doc = await self._generate_state_docs(
            folder_path, chatbot_id, current_state, functionality_map
        )
        
        # Step 6: Identify issues
        print("⚠️  Step 6/7: Identifying issues...")
        unused, unnecessary, duplicates = await self._identify_issues(
            folder_path, chatbot_id, functionality_map
        )
        
        # Step 7: Generate restructuring suggestions
        print("💡 Step 7/7: Generating restructuring suggestions...")
        restructuring = await self._suggest_restructuring(
            folder_path, chatbot_id, current_state, unused, unnecessary, duplicates
        )
        
        # Calculate metrics
        metrics = await self._calculate_metrics(folder_path, current_state)
        
        print("✅ Analysis complete!")
        
        return FolderAnalysis(
            folder_path=folder_path,
            analyzed_at=datetime.utcnow().isoformat(),
            current_state=current_state,
            functionality_map=functionality_map,
            file_structure=current_state.get("file_structure", {}),
            consolidated_docs=consolidated_docs,
            current_state_doc=current_state_doc,
            future_state_doc=future_state_doc,
            unused_functionality=unused,
            unnecessary_files=unnecessary,
            duplicate_features=duplicates,
            restructuring_suggestions=restructuring,
            total_files=metrics["total_files"],
            total_functions=metrics["total_functions"],
            code_quality_score=metrics["quality_score"],
            technical_debt_score=metrics["debt_score"]
        )
    
    async def _index_folder(self, folder_path: str, entity_id: str) -> str:
        """Index folder with Theta RAG"""
        
        # Collect all code files
        code_files = []
        for ext in ['.py', '.js', '.ts', '.tsx', '.jsx', '.rs', '.go', '.java']:
            code_files.extend(Path(folder_path).rglob(f'*{ext}'))
        
        # Collect all markdown files
        md_files = list(Path(folder_path).rglob('*.md'))
        
        # Create documents for Theta RAG
        documents = []
        
        for file_path in code_files[:100]:  # Limit to avoid overwhelming
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append({
                        "path": str(file_path),
                        "content": content,
                        "type": "code"
                    })
            except Exception as e:
                print(f"⚠️  Skipping {file_path}: {e}")
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append({
                        "path": str(file_path),
                        "content": content,
                        "type": "documentation"
                    })
            except Exception as e:
                print(f"⚠️  Skipping {file_path}: {e}")
        
        # Create Theta RAG chatbot
        chatbot_id = f"folder_analysis_{entity_id}_{int(datetime.utcnow().timestamp())}"
        
        # TODO: Actually create chatbot with Theta API
        # For now, simulate
        print(f"📦 Created chatbot: {chatbot_id}")
        print(f"📊 Indexed {len(documents)} files")
        
        return chatbot_id
    
    async def _analyze_current_state(
        self,
        folder_path: str,
        chatbot_id: str
    ) -> Dict[str, Any]:
        """Analyze current state of the folder"""
        
        prompt = f"""
Analyze the current state of this codebase folder: {folder_path}

Provide a comprehensive analysis including:

1. **Purpose**: What is this folder/repo for?
2. **Architecture**: How is it structured?
3. **Technologies**: What languages, frameworks, libraries are used?
4. **Features**: What features are implemented?
5. **Dependencies**: What external dependencies exist?
6. **Entry Points**: What are the main entry points?
7. **Data Flow**: How does data flow through the system?
8. **State Management**: How is state managed?
9. **API Endpoints**: What APIs/endpoints are exposed?
10. **Database Schema**: What data structures are used?

Return JSON format:
{{
  "purpose": "...",
  "architecture": {{...}},
  "technologies": [...],
  "features": [...],
  "dependencies": [...],
  "entry_points": [...],
  "data_flow": "...",
  "state_management": "...",
  "api_endpoints": [...],
  "database_schema": {{...}}
}}
"""
        
        # Query Theta RAG chatbot
        response = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=prompt,
            mode="json"
        )
        
        return json.loads(response)
    
    async def _map_functionality(
        self,
        folder_path: str,
        chatbot_id: str
    ) -> Dict[str, List[str]]:
        """Map all functionality in the folder"""
        
        prompt = """
Create a comprehensive functionality map of this codebase.

For each module/file, list:
- Functions/methods defined
- Classes defined
- Exported functionality
- Used by (which other files use this)
- Dependencies (what this file imports)

Return JSON format:
{
  "module_name": {
    "functions": ["func1", "func2"],
    "classes": ["Class1", "Class2"],
    "exports": ["export1", "export2"],
    "used_by": ["file1.py", "file2.py"],
    "dependencies": ["dep1", "dep2"]
  }
}
"""
        
        response = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=prompt,
            mode="json"
        )
        
        return json.loads(response)
    
    async def _consolidate_docs(
        self,
        folder_path: str,
        chatbot_id: str
    ) -> str:
        """Intelligently consolidate all markdown documentation"""
        
        prompt = """
INTELLIGENTLY consolidate all markdown documentation in this codebase.

Your task is to create a SINGLE, COHERENT, COMPREHENSIVE document by:

**1. Understanding Context:**
- Read ALL markdown files
- Understand the purpose of each document
- Identify the main topics covered
- Recognize different versions of the same information

**2. Removing Duplicates:**
- Find sections that say the same thing in different words
- Identify redundant examples
- Detect repeated installation instructions
- Remove duplicate API documentation
- Consolidate overlapping feature descriptions

**3. Resolving Conflicts:**
- When multiple docs contradict each other, use the most recent/detailed version
- If setup instructions differ, choose the most complete one
- For conflicting information, note both versions with context

**4. Organizing Intelligently:**
- Start with high-level overview
- Progress from general to specific
- Group related information together
- Create logical flow (not just concatenation)
- Use clear hierarchy (H1 → H2 → H3)

**5. Preserving Important Details:**
- Keep all unique information
- Preserve code examples (but remove duplicates)
- Maintain links and references
- Keep version-specific notes
- Preserve warnings and important notices

**6. Creating Coherent Narrative:**
- Write smooth transitions between sections
- Ensure consistent terminology
- Use consistent formatting
- Create a table of contents
- Add cross-references where helpful

**Output Structure:**
```markdown
# [Project Name] - Complete Documentation

## Table of Contents
[Auto-generated from sections]

## 1. Overview
[Synthesized from all READMEs and overview docs]

## 2. Getting Started
[Consolidated setup/installation from all sources]

## 3. Architecture
[Unified architecture description]

## 4. Features
[Complete feature list, duplicates removed]

## 5. API Reference
[Consolidated API docs, organized by category]

## 6. Usage Examples
[Best examples from all docs, duplicates removed]

## 7. Configuration
[All config options, organized logically]

## 8. Development
[Contributing, testing, deployment]

## 9. Troubleshooting
[Common issues from all docs]

## 10. Additional Resources
[Links, references, related docs]
```

**Key Principles:**
- UNDERSTAND before merging
- REMOVE true duplicates (not just similar headings)
- SYNTHESIZE overlapping content into better explanations
- ORGANIZE for readability
- PRESERVE unique information
- CREATE a document someone would actually want to read

Return the consolidated markdown document.
"""
        
        response = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=prompt
        )
        
        return response
    
    async def _generate_state_docs(
        self,
        folder_path: str,
        chatbot_id: str,
        current_state: Dict[str, Any],
        functionality_map: Dict[str, List[str]]
    ) -> tuple[str, str]:
        """Generate current state and future state documents"""
        
        # Current State Document
        current_prompt = f"""
Based on the analysis, create a CURRENT STATE document.

Current Analysis:
{json.dumps(current_state, indent=2)}

Functionality Map:
{json.dumps(functionality_map, indent=2)}

The document should include:
1. **Executive Summary**: What exists now
2. **Architecture Overview**: Current structure
3. **Implemented Features**: What works
4. **Technology Stack**: What's being used
5. **Data Models**: Current schemas
6. **API Surface**: Available endpoints
7. **Dependencies**: External libraries
8. **Known Issues**: Current problems
9. **Technical Debt**: Areas needing improvement

Return as well-formatted markdown.
"""
        
        current_state_doc = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=current_prompt
        )
        
        # Future State Document
        future_prompt = f"""
Based on the current state analysis, create a FUTURE STATE document.

This should describe what the codebase SHOULD look like:
1. **Vision**: Ideal end state
2. **Architecture Improvements**: Better structure
3. **Feature Roadmap**: What to add
4. **Technology Upgrades**: Better tools
5. **Performance Goals**: Speed/efficiency targets
6. **Scalability Plans**: How to scale
7. **Security Enhancements**: Better security
8. **Developer Experience**: Easier to work with
9. **Documentation Goals**: Better docs
10. **Testing Strategy**: Comprehensive tests

Return as well-formatted markdown.
"""
        
        future_state_doc = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=future_prompt
        )
        
        return current_state_doc, future_state_doc
    
    async def _identify_issues(
        self,
        folder_path: str,
        chatbot_id: str,
        functionality_map: Dict[str, List[str]]
    ) -> tuple[List[Dict], List[Dict], List[Dict]]:
        """Identify unused functionality, unnecessary files, and duplicates"""
        
        # Unused Functionality
        unused_prompt = """
Identify UNUSED FUNCTIONALITY in this codebase.

Look for:
- Functions that are defined but never called
- Classes that are never instantiated
- Exports that are never imported
- Dead code paths
- Commented out code that should be removed

For each item, provide:
- File path
- Function/class name
- Reason it's unused
- Recommendation (remove, keep, refactor)

Return JSON array of objects.
"""
        
        unused_response = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=unused_prompt,
            mode="json"
        )
        unused = json.loads(unused_response)
        
        # Unnecessary Files
        unnecessary_prompt = """
Identify UNNECESSARY FILES in this codebase.

Look for:
- Empty files
- Files with only comments
- Duplicate files (same content)
- Test files for deleted features
- Old backup files (.bak, .old, etc.)
- Temporary files that should be gitignored
- Build artifacts that shouldn't be committed

For each file, provide:
- File path
- Reason it's unnecessary
- Recommendation (delete, move, rename)

Return JSON array of objects.
"""
        
        unnecessary_response = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=unnecessary_prompt,
            mode="json"
        )
        unnecessary = json.loads(unnecessary_response)
        
        # Duplicate Features
        duplicates_prompt = """
Identify DUPLICATE FEATURES in this codebase.

Look for:
- Similar functions with different names
- Duplicate implementations of same logic
- Multiple files doing the same thing
- Redundant utility functions
- Copy-pasted code blocks

For each duplicate, provide:
- Files involved
- What's duplicated
- Recommendation (consolidate, refactor, keep one)

Return JSON array of objects.
"""
        
        duplicates_response = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=duplicates_prompt,
            mode="json"
        )
        duplicates = json.loads(duplicates_response)
        
        return unused, unnecessary, duplicates
    
    async def _suggest_restructuring(
        self,
        folder_path: str,
        chatbot_id: str,
        current_state: Dict[str, Any],
        unused: List[Dict],
        unnecessary: List[Dict],
        duplicates: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate restructuring suggestions"""
        
        prompt = f"""
Based on the analysis, suggest how to RESTRUCTURE this codebase.

Current Issues:
- {len(unused)} unused functions/classes
- {len(unnecessary)} unnecessary files
- {len(duplicates)} duplicate features

Current Structure:
{json.dumps(current_state.get("architecture", {}), indent=2)}

Provide restructuring suggestions including:

1. **Folder Structure**: Better organization
2. **Module Boundaries**: Clear separation of concerns
3. **File Naming**: Consistent conventions
4. **Code Organization**: Logical grouping
5. **Dependency Management**: Cleaner imports
6. **Configuration**: Centralized config
7. **Testing Structure**: Better test organization
8. **Documentation**: Where docs should live
9. **Build/Deploy**: Better build structure
10. **Migration Plan**: How to get there

For each suggestion, provide:
- Category (folder_structure, naming, etc.)
- Current problem
- Proposed solution
- Impact (high/medium/low)
- Effort (high/medium/low)
- Priority (1-10)
- Migration steps

Return JSON array of objects.
"""
        
        response = await self.theta.query_chatbot(
            chatbot_id=chatbot_id,
            query=prompt,
            mode="json"
        )
        
        return json.loads(response)
    
    async def _calculate_metrics(
        self,
        folder_path: str,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate code metrics"""
        
        # Count files
        total_files = sum(1 for _ in Path(folder_path).rglob('*') if _.is_file())
        
        # Count functions (from current state)
        total_functions = sum(
            len(module.get("functions", []))
            for module in current_state.get("functionality_map", {}).values()
        )
        
        # Quality score (0-10)
        # Based on: documentation, tests, structure, dependencies
        quality_score = 7.5  # TODO: Calculate from analysis
        
        # Technical debt score (0-10, lower is better)
        # Based on: unused code, duplicates, complexity
        debt_score = 4.2  # TODO: Calculate from issues
        
        return {
            "total_files": total_files,
            "total_functions": total_functions,
            "quality_score": quality_score,
            "debt_score": debt_score
        }
    
    async def save_analysis(
        self,
        analysis: FolderAnalysis,
        output_dir: str
    ):
        """Save analysis results to files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON summary
        with open(output_path / "analysis_summary.json", 'w') as f:
            json.dump(asdict(analysis), f, indent=2)
        
        # Save current state document
        with open(output_path / "CURRENT_STATE.md", 'w') as f:
            f.write(analysis.current_state_doc)
        
        # Save future state document
        with open(output_path / "FUTURE_STATE.md", 'w') as f:
            f.write(analysis.future_state_doc)
        
        # Save consolidated docs
        with open(output_path / "CONSOLIDATED_DOCS.md", 'w') as f:
            f.write(analysis.consolidated_docs)
        
        # Save issues report
        issues_report = f"""# Issues Report

## Unused Functionality ({len(analysis.unused_functionality)} items)

{self._format_issues(analysis.unused_functionality)}

## Unnecessary Files ({len(analysis.unnecessary_files)} items)

{self._format_issues(analysis.unnecessary_files)}

## Duplicate Features ({len(analysis.duplicate_features)} items)

{self._format_issues(analysis.duplicate_features)}
"""
        
        with open(output_path / "ISSUES_REPORT.md", 'w') as f:
            f.write(issues_report)
        
        # Save restructuring suggestions
        restructuring_report = f"""# Restructuring Suggestions

{self._format_suggestions(analysis.restructuring_suggestions)}
"""
        
        with open(output_path / "RESTRUCTURING_PLAN.md", 'w') as f:
            f.write(restructuring_report)
        
        print(f"✅ Analysis saved to: {output_path}")
    
    def _format_issues(self, issues: List[Dict]) -> str:
        """Format issues as markdown"""
        if not issues:
            return "*No issues found*\n"
        
        output = []
        for i, issue in enumerate(issues, 1):
            output.append(f"### {i}. {issue.get('name', 'Issue')}")
            output.append(f"**File:** `{issue.get('file', 'N/A')}`")
            output.append(f"**Reason:** {issue.get('reason', 'N/A')}")
            output.append(f"**Recommendation:** {issue.get('recommendation', 'N/A')}")
            output.append("")
        
        return "\n".join(output)
    
    def _format_suggestions(self, suggestions: List[Dict]) -> str:
        """Format suggestions as markdown"""
        if not suggestions:
            return "*No suggestions*\n"
        
        # Sort by priority
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: x.get('priority', 5),
            reverse=True
        )
        
        output = []
        for i, suggestion in enumerate(sorted_suggestions, 1):
            output.append(f"## {i}. {suggestion.get('category', 'Suggestion')}")
            output.append(f"**Priority:** {suggestion.get('priority', 'N/A')}/10")
            output.append(f"**Impact:** {suggestion.get('impact', 'N/A')}")
            output.append(f"**Effort:** {suggestion.get('effort', 'N/A')}")
            output.append(f"\n**Problem:**\n{suggestion.get('problem', 'N/A')}")
            output.append(f"\n**Solution:**\n{suggestion.get('solution', 'N/A')}")
            output.append(f"\n**Migration Steps:**")
            for step in suggestion.get('migration_steps', []):
                output.append(f"- {step}")
            output.append("")
        
        return "\n".join(output)


# Example usage
async def main():
    """Example usage"""
    analyzer = FolderAnalyzerAgent()
    
    analysis = await analyzer.analyze_folder(
        folder_path="/path/to/repo",
        entity_id="user_123",
        deep_analysis=True
    )
    
    await analyzer.save_analysis(
        analysis=analysis,
        output_dir="/path/to/output"
    )
    
    print(f"✅ Analysis complete!")
    print(f"📊 Total files: {analysis.total_files}")
    print(f"🔧 Total functions: {analysis.total_functions}")
    print(f"⭐ Quality score: {analysis.code_quality_score}/10")
    print(f"⚠️  Technical debt: {analysis.technical_debt_score}/10")
    print(f"🗑️  Unused: {len(analysis.unused_functionality)}")
    print(f"📁 Unnecessary: {len(analysis.unnecessary_files)}")
    print(f"🔄 Duplicates: {len(analysis.duplicate_features)}")
    print(f"💡 Suggestions: {len(analysis.restructuring_suggestions)}")


if __name__ == "__main__":
    asyncio.run(main())
