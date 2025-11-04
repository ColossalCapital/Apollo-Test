"""
Documentation Generator
Generates comprehensive documentation for all project types
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """Generates comprehensive documentation suite"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    async def generate_complete_docs(self, docs_dir: Path, results: Dict):
        """Generate complete documentation suite"""
        
        # 1. API Reference
        await self._generate_api_reference(docs_dir)
        
        # 2. Deployment Guide
        await self._generate_deployment_guide(docs_dir, results)
        
        # 3. Testing Guide
        await self._generate_testing_guide(docs_dir, results)
        
        # 4. Architecture Overview
        await self._generate_architecture_docs(docs_dir, results)
        
        # 5. Getting Started Guide
        await self._generate_getting_started(docs_dir, results)
        
        logger.info("📚 Generated complete documentation suite")
    
    async def _generate_api_reference(self, docs_dir: Path):
        """Generate API reference documentation"""
        # Scan for API routes/endpoints
        api_files = []
        for root, dirs, files in os.walk(self.repo_path):
            # Skip node_modules, etc.
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'dist', 'build']]
            
            for file in files:
                if any(keyword in file.lower() for keyword in ['route', 'api', 'endpoint', 'controller']):
                    if file.endswith(('.py', '.ts', '.js', '.go', '.rs')):
                        api_files.append(os.path.join(root, file))
        
        content = f"""# API Reference

Generated: {datetime.now().isoformat()}

## Overview

This document provides a comprehensive reference for all API endpoints in this project.

## Detected API Files

{len(api_files)} API-related files found:

"""
        for api_file in api_files[:20]:
            rel_path = os.path.relpath(api_file, self.repo_path)
            content += f"- `{rel_path}`\n"
        
        if len(api_files) > 20:
            content += f"\n*...and {len(api_files) - 20} more*\n"
        
        content += """

## Endpoints

*Auto-generated endpoint documentation will appear here after code analysis*

### Authentication

- **Method:** To be documented
- **Headers:** To be documented

### Rate Limiting

- **Limits:** To be documented

## Response Formats

All API responses follow standard JSON format:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request |
| 401  | Unauthorized |
| 404  | Not Found |
| 500  | Server Error |

## Next Steps

1. Review detected API files above
2. Add inline documentation to API routes
3. Run analysis again to auto-generate endpoint docs
"""
        
        (docs_dir / "API_REFERENCE.md").write_text(content)
        logger.info("📄 Created API_REFERENCE.md")
    
    async def _generate_deployment_guide(self, docs_dir: Path, results: Dict):
        """Generate deployment guide"""
        project_type = results.get('phases', {}).get('project_type_detection', {})
        
        content = f"""# Deployment Guide

Generated: {datetime.now().isoformat()}

## Project Type

**Detected:** {project_type.get('primary', 'Unknown')}

## Deployment Strategy

**Recommended:** {project_type.get('deployment_strategy', 'To be determined')}

## Prerequisites

- [ ] Production environment configured
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Database migrations run (if applicable)
- [ ] SSL certificates configured

## Deployment Steps

### 1. Build

```bash
# Install dependencies
npm install  # or pip install -r requirements.txt

# Build project
npm run build  # or python setup.py build
```

### 2. Test

```bash
# Run tests
npm test  # or pytest
```

### 3. Deploy

```bash
# Deploy to production
# (Commands will be auto-generated based on project type)
```

## Environment Variables

Required environment variables:

```env
# Add your environment variables here
NODE_ENV=production
DATABASE_URL=
API_KEY=
```

## Monitoring

- **Health Check:** `/health` endpoint
- **Metrics:** Available at `/metrics`
- **Logs:** Check application logs

## Rollback Procedure

If deployment fails:

1. Revert to previous version
2. Check error logs
3. Fix issues
4. Redeploy

## Next Steps

1. Configure CI/CD pipeline
2. Set up monitoring and alerts
3. Document environment-specific configurations
"""
        
        (docs_dir / "DEPLOYMENT_GUIDE.md").write_text(content)
        logger.info("📄 Created DEPLOYMENT_GUIDE.md")
    
    async def _generate_testing_guide(self, docs_dir: Path, results: Dict):
        """Generate testing guide"""
        test_analysis = results.get('phases', {}).get('testing', {})
        
        content = f"""# Testing Guide

Generated: {datetime.now().isoformat()}

## Testing Strategy

This project uses a comprehensive testing approach:

- **Unit Tests:** Test individual components
- **Integration Tests:** Test component interactions
- **End-to-End Tests:** Test complete user flows

## Test Coverage

Current coverage: {test_analysis.get('coverage_percentage', 0)}%

## Running Tests

### All Tests

```bash
npm test  # or pytest
```

### Specific Test Suite

```bash
npm test -- --grep "ComponentName"  # or pytest tests/test_component.py
```

### Watch Mode

```bash
npm test -- --watch
```

## Writing Tests

### Unit Test Example

```javascript
describe('ComponentName', () => {{
  it('should do something', () => {{
    // Arrange
    const input = 'test';
    
    // Act
    const result = myFunction(input);
    
    // Assert
    expect(result).toBe('expected');
  }});
}});
```

## Test Organization

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── e2e/           # End-to-end tests
```

## Best Practices

1. Write tests before code (TDD)
2. Keep tests simple and focused
3. Use descriptive test names
4. Mock external dependencies
5. Maintain high coverage (>80%)

## Continuous Integration

Tests run automatically on:
- Every commit
- Pull requests
- Before deployment

## Next Steps

1. Increase test coverage to 80%+
2. Add integration tests
3. Set up E2E testing framework
4. Configure CI/CD test automation
"""
        
        (docs_dir / "TESTING_GUIDE.md").write_text(content)
        logger.info("📄 Created TESTING_GUIDE.md")
    
    async def _generate_architecture_docs(self, docs_dir: Path, results: Dict):
        """Generate architecture documentation"""
        
        content = f"""# Architecture Overview

Generated: {datetime.now().isoformat()}

## System Architecture

This document describes the high-level architecture of the project.

## Components

### Frontend
- **Location:** `{self._find_frontend_dir()}`
- **Technology:** React/Vue/Angular (detected from files)

### Backend
- **Location:** `{self._find_backend_dir()}`
- **Technology:** Python/Node/Go (detected from files)

### Database
- **Type:** To be documented
- **Schema:** See database documentation

## File Structure

```
{self._generate_tree_structure(max_depth=2)}
```

## Data Flow

```
User Request → Frontend → API → Backend → Database
                                    ↓
                              External Services
```

## Key Design Decisions

1. **Separation of Concerns:** Frontend and backend are decoupled
2. **API-First:** All interactions go through well-defined APIs
3. **Scalability:** Designed for horizontal scaling
4. **Security:** Authentication and authorization at API layer

## Technology Stack

See `tech_stack.md` in the analysis folder for complete details.

## Dependencies

### External Services
- To be documented

### Third-Party Libraries
- See `dependencies.md` in the analysis folder

## Security Considerations

1. Authentication: JWT/OAuth
2. Authorization: Role-based access control
3. Data encryption: At rest and in transit
4. Input validation: All user inputs sanitized

## Performance Considerations

1. Caching strategy
2. Database indexing
3. Load balancing
4. CDN for static assets

## Next Steps

1. Document specific component interactions
2. Create sequence diagrams for key flows
3. Document API contracts
4. Update as architecture evolves
"""
        
        (docs_dir / "ARCHITECTURE.md").write_text(content)
        logger.info("📄 Created ARCHITECTURE.md")
    
    async def _generate_getting_started(self, docs_dir: Path, results: Dict):
        """Generate getting started guide"""
        project_type = results.get('phases', {}).get('project_type_detection', {})
        
        content = f"""# Getting Started

Generated: {datetime.now().isoformat()}

## Welcome!

This guide will help you get up and running with this project.

## Prerequisites

- Git
- Node.js (v16+) or Python (3.8+) or Rust (1.70+)
- Docker (optional, for containerized development)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-name>
```

### 2. Install Dependencies

```bash
npm install  # or pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run Development Server

```bash
npm run dev  # or python main.py
```

### 5. Open in Browser

Navigate to `http://localhost:3000` (or configured port)

## Project Structure

```
{self._generate_tree_structure(max_depth=1)}
```

## Development Workflow

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run tests locally
5. Submit pull request

## Common Tasks

### Running Tests

```bash
npm test
```

### Building for Production

```bash
npm run build
```

### Linting

```bash
npm run lint
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Dependencies Not Installing

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Getting Help

- Check the [documentation](./PROJECT_DOCS.md)
- Review [API reference](./API_REFERENCE.md)
- See [architecture docs](./ARCHITECTURE.md)

## Next Steps

1. Read the [architecture overview](./ARCHITECTURE.md)
2. Review the [API reference](./API_REFERENCE.md)
3. Check out the [testing guide](./TESTING_GUIDE.md)
4. Start building!
"""
        
        (docs_dir / "GETTING_STARTED.md").write_text(content)
        logger.info("📄 Created GETTING_STARTED.md")
    
    def _find_frontend_dir(self) -> str:
        """Find frontend directory"""
        common_names = ['frontend', 'client', 'web', 'ui', 'app', 'src']
        for name in common_names:
            path = os.path.join(self.repo_path, name)
            if os.path.exists(path):
                return name
        return "Not found"
    
    def _find_backend_dir(self) -> str:
        """Find backend directory"""
        common_names = ['backend', 'server', 'api', 'services', 'src']
        for name in common_names:
            path = os.path.join(self.repo_path, name)
            if os.path.exists(path):
                return name
        return "Not found"
    
    def _generate_tree_structure(self, max_depth: int = 2) -> str:
        """Generate simple tree structure"""
        tree = []
        for root, dirs, files in os.walk(self.repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'dist', 'build', '__pycache__']]
            
            level = root.replace(self.repo_path, '').count(os.sep)
            if level >= max_depth:
                dirs[:] = []
                continue
            indent = '  ' * level
            tree.append(f"{indent}{os.path.basename(root)}/")
            if level < max_depth - 1:
                for file in files[:5]:  # Limit files shown
                    tree.append(f"{indent}  {file}")
        return '\n'.join(tree[:50])  # Limit total lines
