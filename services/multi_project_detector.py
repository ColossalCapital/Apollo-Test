"""
Multi-Project Detector for Akashic
Detects and manages multiple .akashic projects in a directory tree
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime


class MultiProjectDetector:
    """Detects and manages multiple .akashic projects"""
    
    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)
        self.projects: Dict[str, dict] = {}
    
    def scan_for_projects(self) -> Dict[str, dict]:
        """
        Scan directory tree for .akashic folders
        
        Returns:
        {
            "/path/to/root": {
                "type": "root",
                "akashic_path": "/path/to/root/.akashic",
                "name": "ProjectName",
                "sub_projects": ["/path/to/sub1", "/path/to/sub2"],
                "parent": None
            },
            "/path/to/root/Atlas": {
                "type": "sub_project",
                "akashic_path": "/path/to/root/Atlas/.akashic",
                "name": "Atlas",
                "sub_projects": [],
                "parent": "/path/to/root"
            }
        }
        """
        projects = {}
        
        print(f"🔍 Scanning for .akashic projects in: {self.root_path}")
        
        # Find all .akashic directories
        for root, dirs, files in os.walk(self.root_path):
            # Skip hidden directories and common excludes
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'dist', 'build']]
            
            if '.akashic' in dirs:
                akashic_path = os.path.join(root, '.akashic')
                
                # Determine if root or sub-project
                is_root = root == self.root_path
                
                projects[root] = {
                    'type': 'root' if is_root else 'sub_project',
                    'akashic_path': akashic_path,
                    'name': os.path.basename(root) if not is_root else 'Root',
                    'parent': None,  # Will be set later
                    'sub_projects': [],
                    'depth': self._calculate_depth(root),
                    'exists': os.path.exists(akashic_path)
                }
                
                print(f"  {'📁' if is_root else '  📂'} Found: {projects[root]['name']} ({projects[root]['type']})")
        
        # Build hierarchy
        for path in sorted(projects.keys(), key=lambda p: projects[p]['depth']):
            project = projects[path]
            
            if project['type'] != 'root':
                parent_path = self._find_parent_project(path, projects)
                if parent_path:
                    project['parent'] = parent_path
                    projects[parent_path]['sub_projects'].append(path)
        
        self.projects = projects
        
        print(f"✅ Found {len(projects)} projects:")
        print(f"   - Root projects: {sum(1 for p in projects.values() if p['type'] == 'root')}")
        print(f"   - Sub-projects: {sum(1 for p in projects.values() if p['type'] == 'sub_project')}")
        
        return projects
    
    def _calculate_depth(self, path: str) -> int:
        """Calculate depth from root"""
        rel_path = os.path.relpath(path, self.root_path)
        if rel_path == '.':
            return 0
        return len(Path(rel_path).parts)
    
    def _find_parent_project(self, path: str, projects: Dict) -> Optional[str]:
        """Find the nearest parent with .akashic"""
        parent = os.path.dirname(path)
        
        # Walk up the tree
        while parent and parent != self.root_path:
            if parent in projects:
                return parent
            parent = os.path.dirname(parent)
        
        # Check if root has .akashic
        if self.root_path in projects:
            return self.root_path
        
        return None
    
    def get_project_hierarchy(self) -> dict:
        """Get hierarchical representation of projects"""
        
        def build_tree(project_path: str) -> dict:
            project = self.projects[project_path]
            
            return {
                'path': project_path,
                'name': project['name'],
                'type': project['type'],
                'akashic_path': project['akashic_path'],
                'children': [
                    build_tree(sub_path) 
                    for sub_path in project['sub_projects']
                ]
            }
        
        # Find root projects
        roots = [
            path for path, proj in self.projects.items() 
            if proj['type'] == 'root'
        ]
        
        if not roots:
            return {}
        
        # Build tree from first root (usually only one)
        return build_tree(roots[0])
    
    def get_project_for_file(self, file_path: str) -> Optional[dict]:
        """Find which .akashic project owns this file"""
        
        file_path = os.path.abspath(file_path)
        
        # Find the closest .akashic parent (deepest match)
        matches = []
        for project_path, project_info in self.projects.items():
            if file_path.startswith(project_path):
                matches.append((project_path, project_info))
        
        if not matches:
            return None
        
        # Return deepest match (longest path)
        project_path, project_info = max(matches, key=lambda x: len(x[0]))
        
        return {
            'path': project_path,
            **project_info
        }
    
    def save_project_registry(self):
        """Save project registry to root .akashic"""
        
        root_projects = [
            path for path, proj in self.projects.items() 
            if proj['type'] == 'root'
        ]
        
        if not root_projects:
            return
        
        root_path = root_projects[0]
        registry_path = os.path.join(
            self.projects[root_path]['akashic_path'],
            'project_registry.json'
        )
        
        registry = {
            'generated_at': datetime.now().isoformat(),
            'root_path': self.root_path,
            'total_projects': len(self.projects),
            'hierarchy': self.get_project_hierarchy(),
            'projects': {
                path: {
                    'name': info['name'],
                    'type': info['type'],
                    'parent': info['parent'],
                    'sub_projects': info['sub_projects']
                }
                for path, info in self.projects.items()
            }
        }
        
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"💾 Saved project registry to: {registry_path}")
    
    def create_missing_akashic_dirs(self):
        """Create .akashic directories for detected projects if they don't exist"""
        
        for project_path, project_info in self.projects.items():
            akashic_path = project_info['akashic_path']
            
            if not os.path.exists(akashic_path):
                print(f"📁 Creating .akashic for: {project_info['name']}")
                
                # Create directory structure
                os.makedirs(os.path.join(akashic_path, 'analysis'), exist_ok=True)
                os.makedirs(os.path.join(akashic_path, 'docs'), exist_ok=True)
                os.makedirs(os.path.join(akashic_path, 'restructuring'), exist_ok=True)
                os.makedirs(os.path.join(akashic_path, 'pm'), exist_ok=True)
                os.makedirs(os.path.join(akashic_path, 'diagrams'), exist_ok=True)
                os.makedirs(os.path.join(akashic_path, 'planning'), exist_ok=True)
                
                # Create initial config
                config = {
                    'project_name': project_info['name'],
                    'project_type': project_info['type'],
                    'created_at': datetime.now().isoformat(),
                    'parent_project': project_info['parent']
                }
                
                config_path = os.path.join(akashic_path, 'config.json')
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"  ✅ Created: {akashic_path}")


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = os.getcwd()
    
    detector = MultiProjectDetector(root_path)
    projects = detector.scan_for_projects()
    
    print("\n📊 Project Hierarchy:")
    hierarchy = detector.get_project_hierarchy()
    
    def print_tree(node, indent=0):
        print(f"{'  ' * indent}{'📁' if node['type'] == 'root' else '📂'} {node['name']}")
        for child in node.get('children', []):
            print_tree(child, indent + 1)
    
    if hierarchy:
        print_tree(hierarchy)
    
    # Save registry
    detector.save_project_registry()
    
    # Create missing directories
    detector.create_missing_akashic_dirs()
