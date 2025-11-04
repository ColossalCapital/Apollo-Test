#!/usr/bin/env python3
"""
Documentation to PM Converter
Converts documentation into hierarchical PM tasks (bottom-up)
"""

import os
import re
from typing import List, Dict, Optional
from pathlib import Path
import yaml

from .pm_clients.linear_client import LinearClient
from .pm_clients.jira_client import JiraClient


class TaskTemplate:
    """Template for AI-completable atomic task"""
    
    def __init__(
        self,
        title: str,
        description: str,
        category: str,
        files: List[str],
        estimate_hours: int = 2,
        complexity: str = "simple"
    ):
        self.title = title
        self.description = description
        self.category = category
        self.files = files
        self.estimate_hours = estimate_hours
        self.complexity = complexity
        self.labels = [
            "ai-completable",
            category,
            complexity
        ]
    
    def to_linear_format(self) -> Dict:
        """Convert to Linear issue format"""
        return {
            "title": self.title,
            "description": self._format_description(),
            "estimate": self.estimate_hours,
            "priority": 3,  # Medium
            "labelIds": []  # Will be filled with actual label IDs
        }
    
    def _format_description(self) -> str:
        """Format description with template"""
        return f"""
{self.description}

## Acceptance Criteria
- [ ] Implementation complete
- [ ] Unit tests added (>80% coverage)
- [ ] Linting passes
- [ ] PR created with template

## Files to Modify
{chr(10).join(f'- {f}' for f in self.files)}

## Complexity
{self.complexity} ({self.estimate_hours}h)

## Labels
{', '.join(self.labels)}

## AI Agent Instructions
This task is designed to be completed by an AI agent:
1. Read the description
2. Generate code following the template
3. Write tests
4. Run linting
5. Create PR with filled template
"""


class Feature:
    """Collection of atomic tasks"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tasks: List[TaskTemplate] = []
    
    def add_task(self, task: TaskTemplate):
        self.tasks.append(task)
    
    def to_linear_format(self, team_id: str) -> Dict:
        """Convert to Linear issue format"""
        task_list = "\n".join(f"- [ ] {t.title}" for t in self.tasks)
        
        return {
            "teamId": team_id,
            "title": f"[Feature] {self.name}",
            "description": f"""
{self.description}

## Sub-tasks
{task_list}

## Estimate
{sum(t.estimate_hours for t in self.tasks)} hours total
""",
            "priority": 2  # High
        }


class Component:
    """Major system component"""
    
    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category  # frontend, backend, infrastructure
        self.features: List[Feature] = []
    
    def add_feature(self, feature: Feature):
        self.features.append(feature)
    
    def to_jira_format(self, project_key: str) -> Dict:
        """Convert to Jira issue format"""
        feature_list = "\n".join(f"* {f.name}" for f in self.features)
        
        return {
            "fields": {
                "project": {"key": project_key},
                "summary": f"[Component] {self.name}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": f"{self.description}\n\nFeatures:\n{feature_list}"
                        }]
                    }]
                },
                "issuetype": {"name": "Story"},
                "labels": ["component", self.category]
            }
        }


class Epic:
    """Major product functionality"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.components: List[Component] = []
    
    def add_component(self, component: Component):
        self.components.append(component)
    
    def to_jira_format(self, project_key: str) -> Dict:
        """Convert to Jira epic format"""
        component_list = "\n".join(f"* {c.name}" for c in self.components)
        
        return {
            "fields": {
                "project": {"key": project_key},
                "summary": f"[Epic] {self.name}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": f"{self.description}\n\nComponents:\n{component_list}"
                        }]
                    }]
                },
                "issuetype": {"name": "Epic"},
                "labels": ["epic"]
            }
        }


class DocumentationParser:
    """Parse documentation and extract features/tasks"""
    
    def __init__(self):
        self.features_pattern = re.compile(r'^##\s+Features?\s*$', re.MULTILINE | re.IGNORECASE)
        self.list_item_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    
    def parse_file(self, file_path: str) -> Dict:
        """Parse a markdown file and extract structure"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else Path(file_path).stem
        
        # Extract description (first paragraph after title)
        desc_match = re.search(r'^#.+?\n\n(.+?)(?:\n\n|\n#)', content, re.MULTILINE | re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract features
        features = self._extract_features(content)
        
        return {
            "title": title,
            "description": description,
            "features": features
        }
    
    def _extract_features(self, content: str) -> List[str]:
        """Extract feature list from content"""
        features = []
        
        # Find Features section
        features_match = self.features_pattern.search(content)
        if not features_match:
            return features
        
        # Get content after Features heading
        start = features_match.end()
        # Find next heading or end of file
        next_heading = re.search(r'\n##\s+', content[start:])
        end = start + next_heading.start() if next_heading else len(content)
        
        features_section = content[start:end]
        
        # Extract list items
        for match in self.list_item_pattern.finditer(features_section):
            feature = match.group(1).strip()
            features.append(feature)
        
        return features


class TaskDecomposer:
    """Decompose features into atomic AI-completable tasks"""
    
    def __init__(self):
        self.task_templates = {
            "api_endpoint": {
                "files": ["api/routes.py", "tests/test_api.py"],
                "estimate": 2,
                "complexity": "simple"
            },
            "ui_component": {
                "files": ["components/Component.tsx", "components/Component.test.tsx"],
                "estimate": 3,
                "complexity": "simple"
            },
            "database_model": {
                "files": ["models/model.py", "migrations/001_create_table.sql"],
                "estimate": 2,
                "complexity": "simple"
            },
            "service_function": {
                "files": ["services/service.py", "tests/test_service.py"],
                "estimate": 2,
                "complexity": "simple"
            }
        }
    
    def decompose_feature(self, feature_text: str, category: str = "backend") -> List[TaskTemplate]:
        """Break down a feature into atomic tasks"""
        tasks = []
        
        # Simple heuristic-based decomposition
        # In production, this would use Apollo AI to intelligently decompose
        
        if "api" in feature_text.lower() or "endpoint" in feature_text.lower():
            tasks.append(TaskTemplate(
                title=f"[API] {feature_text}",
                description=f"Implement {feature_text}",
                category="backend",
                files=self.task_templates["api_endpoint"]["files"],
                estimate_hours=self.task_templates["api_endpoint"]["estimate"]
            ))
        
        elif "ui" in feature_text.lower() or "component" in feature_text.lower():
            tasks.append(TaskTemplate(
                title=f"[UI] {feature_text}",
                description=f"Create {feature_text}",
                category="frontend",
                files=self.task_templates["ui_component"]["files"],
                estimate_hours=self.task_templates["ui_component"]["estimate"]
            ))
        
        else:
            # Generic task
            tasks.append(TaskTemplate(
                title=f"[{category.title()}] {feature_text}",
                description=f"Implement {feature_text}",
                category=category,
                files=["src/implementation.py", "tests/test_implementation.py"],
                estimate_hours=2
            ))
        
        return tasks


class DocToPMConverter:
    """Main converter class"""
    
    def __init__(
        self,
        linear_team_id: str,
        jira_project_key: str
    ):
        self.parser = DocumentationParser()
        self.decomposer = TaskDecomposer()
        self.linear = LinearClient()
        self.jira = JiraClient()
        self.linear_team_id = linear_team_id
        self.jira_project_key = jira_project_key
    
    def convert_file(
        self,
        file_path: str,
        create_tasks: bool = False
    ) -> Dict:
        """
        Convert a documentation file to PM tasks
        
        Args:
            file_path: Path to markdown file
            create_tasks: If True, create tasks in Linear/Jira
        
        Returns:
            Dictionary with task hierarchy
        """
        # Parse documentation
        doc = self.parser.parse_file(file_path)
        
        # Create epic
        epic = Epic(
            name=doc["title"],
            description=doc["description"]
        )
        
        # For each feature, create component and tasks
        for feature_text in doc["features"]:
            # Create feature
            feature = Feature(
                name=feature_text,
                description=f"Implement {feature_text}"
            )
            
            # Decompose into atomic tasks
            tasks = self.decomposer.decompose_feature(feature_text)
            for task in tasks:
                feature.add_task(task)
            
            # Create component (group related features)
            component = Component(
                name=f"{doc['title']} - {feature_text}",
                description=f"Component for {feature_text}",
                category=tasks[0].category if tasks else "backend"
            )
            component.add_feature(feature)
            epic.add_component(component)
        
        # Create tasks if requested
        if create_tasks:
            self._create_tasks(epic)
        
        return {
            "epic": epic.name,
            "components": len(epic.components),
            "features": sum(len(c.features) for c in epic.components),
            "tasks": sum(len(f.tasks) for c in epic.components for f in c.features)
        }
    
    def _create_tasks(self, epic: Epic):
        """Create tasks in Linear and Jira"""
        # Create epic in Jira
        jira_epic = self.jira.create_issue(epic.to_jira_format(self.jira_project_key))
        print(f"✅ Created Jira epic: {jira_epic['key']}")
        
        # Create components and tasks
        for component in epic.components:
            # Create component in Jira
            jira_component = self.jira.create_issue(component.to_jira_format(self.jira_project_key))
            print(f"  ✅ Created Jira component: {jira_component['key']}")
            
            for feature in component.features:
                # Create feature in Linear
                linear_feature = self.linear.create_issue(feature.to_linear_format(self.linear_team_id))
                print(f"    ✅ Created Linear feature: {linear_feature['identifier']}")
                
                # Create atomic tasks in Linear
                for task in feature.tasks:
                    linear_task = self.linear.create_issue(task.to_linear_format())
                    linear_task["teamId"] = self.linear_team_id
                    print(f"      ✅ Created Linear task: {linear_task['identifier']}")


def main():
    """Example usage"""
    converter = DocToPMConverter(
        linear_team_id="bec8f995-cc42-487e-becd-30e2c6cbf92b",
        jira_project_key="AKASHIC"
    )
    
    # Convert README
    result = converter.convert_file(
        "Akashic/README.md",
        create_tasks=False  # Set to True to actually create tasks
    )
    
    print(f"Converted: {result}")


if __name__ == "__main__":
    main()
