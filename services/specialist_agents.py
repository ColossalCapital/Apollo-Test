"""
Specialist Agents with PR Templates
Each agent has expertise, PR template, and test requirements
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class AgentSpecialty(Enum):
    """Specialist agent types"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    ML = "ml"
    DATABASE = "database"
    API = "api"
    MOBILE = "mobile"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"


@dataclass
class PRTemplate:
    """PR template for specialist agent"""
    title_format: str
    sections: List[str]
    required_tests: List[str]
    required_checks: List[str]
    reviewers: List[str]
    labels: List[str]


@dataclass
class SpecialistAgent:
    """Specialist agent configuration"""
    name: str
    specialty: AgentSpecialty
    expertise: List[str]
    file_patterns: List[str]
    keywords: List[str]
    pr_template: PRTemplate
    llm_model: str
    context_size: int


class SpecialistAgentRegistry:
    """Registry of all specialist agents"""
    
    AGENTS = {
        AgentSpecialty.FRONTEND: SpecialistAgent(
            name="Frontend Specialist",
            specialty=AgentSpecialty.FRONTEND,
            expertise=[
                "React", "Vue", "Angular", "TypeScript", "JavaScript",
                "CSS", "HTML", "UI/UX", "Responsive Design", "Accessibility"
            ],
            file_patterns=[
                "*.tsx", "*.jsx", "*.vue", "*.css", "*.scss",
                "*.html", "components/**/*", "pages/**/*"
            ],
            keywords=[
                "ui", "frontend", "component", "page", "style",
                "layout", "responsive", "mobile", "design"
            ],
            pr_template=PRTemplate(
                title_format="[Frontend] {ticket_title}",
                sections=[
                    "## Ticket\nCloses #{ticket_id}\n\n{ticket_url}",
                    "## Changes\n{changes_summary}",
                    "## UI Changes\n{screenshots}",
                    "## Component Updates\n{component_list}",
                    "## Testing\n- [ ] Unit tests pass\n- [ ] Component tests pass\n- [ ] Visual regression tests pass\n- [ ] Accessibility tests pass\n- [ ] Cross-browser tested",
                    "## Accessibility\n- [ ] ARIA labels added\n- [ ] Keyboard navigation works\n- [ ] Screen reader tested\n- [ ] Color contrast verified",
                    "## Performance\n- [ ] Bundle size impact: {bundle_size}\n- [ ] Lighthouse score: {lighthouse_score}",
                    "## Browser Support\n- [ ] Chrome\n- [ ] Firefox\n- [ ] Safari\n- [ ] Edge",
                    "## Agent Info\nCompleted by: Frontend Specialist\nBranch: {branch}\nCommits: {commit_count}"
                ],
                required_tests=[
                    "npm test -- components",
                    "npm run test:visual",
                    "npm run test:a11y"
                ],
                required_checks=[
                    "lint",
                    "type-check",
                    "build",
                    "bundle-size"
                ],
                reviewers=["frontend-team"],
                labels=["frontend", "ui", "component"]
            ),
            llm_model="deepseek-coder-33b",
            context_size=16000
        ),
        
        AgentSpecialty.BACKEND: SpecialistAgent(
            name="Backend Specialist",
            specialty=AgentSpecialty.BACKEND,
            expertise=[
                "Python", "Node.js", "Go", "Rust", "API Design",
                "Database", "Authentication", "Performance", "Scalability"
            ],
            file_patterns=[
                "*.py", "*.js", "*.ts", "*.go", "*.rs",
                "api/**/*", "routes/**/*", "controllers/**/*",
                "services/**/*", "models/**/*"
            ],
            keywords=[
                "api", "backend", "server", "database", "auth",
                "endpoint", "service", "controller", "model"
            ],
            pr_template=PRTemplate(
                title_format="[Backend] {ticket_title}",
                sections=[
                    "## Ticket\nCloses #{ticket_id}\n\n{ticket_url}",
                    "## Changes\n{changes_summary}",
                    "## API Changes\n{api_changes}",
                    "## Database Changes\n{db_migrations}",
                    "## Testing\n- [ ] Unit tests pass\n- [ ] Integration tests pass\n- [ ] API tests pass\n- [ ] Load tests pass",
                    "## Security\n- [ ] Authentication verified\n- [ ] Authorization checked\n- [ ] Input validation added\n- [ ] SQL injection prevented\n- [ ] XSS prevention verified",
                    "## Performance\n- [ ] Query optimization done\n- [ ] Caching implemented\n- [ ] Response time: {response_time}ms\n- [ ] Memory usage: {memory_usage}",
                    "## Breaking Changes\n{breaking_changes}",
                    "## Migration Steps\n{migration_steps}",
                    "## Agent Info\nCompleted by: Backend Specialist\nBranch: {branch}\nCommits: {commit_count}"
                ],
                required_tests=[
                    "pytest tests/",
                    "pytest tests/integration/",
                    "pytest tests/api/"
                ],
                required_checks=[
                    "lint",
                    "type-check",
                    "security-scan",
                    "api-docs"
                ],
                reviewers=["backend-team"],
                labels=["backend", "api", "server"]
            ),
            llm_model="deepseek-coder-33b",
            context_size=16000
        ),
        
        AgentSpecialty.DEVOPS: SpecialistAgent(
            name="DevOps Specialist",
            specialty=AgentSpecialty.DEVOPS,
            expertise=[
                "Docker", "Kubernetes", "CI/CD", "AWS", "GCP",
                "Terraform", "Ansible", "Monitoring", "Deployment"
            ],
            file_patterns=[
                "Dockerfile", "docker-compose.yml", "*.yaml", "*.yml",
                ".github/workflows/*", "terraform/**/*", "k8s/**/*"
            ],
            keywords=[
                "docker", "kubernetes", "deployment", "ci/cd",
                "infrastructure", "devops", "pipeline", "monitoring"
            ],
            pr_template=PRTemplate(
                title_format="[DevOps] {ticket_title}",
                sections=[
                    "## Ticket\nCloses #{ticket_id}\n\n{ticket_url}",
                    "## Changes\n{changes_summary}",
                    "## Infrastructure Changes\n{infra_changes}",
                    "## Deployment Impact\n{deployment_impact}",
                    "## Testing\n- [ ] Build succeeds\n- [ ] Deployment test passes\n- [ ] Rollback tested\n- [ ] Monitoring verified",
                    "## Security\n- [ ] Secrets managed properly\n- [ ] Network policies updated\n- [ ] Access controls verified\n- [ ] Vulnerability scan passed",
                    "## Monitoring\n- [ ] Metrics added\n- [ ] Alerts configured\n- [ ] Dashboards updated\n- [ ] Logs verified",
                    "## Rollout Plan\n{rollout_plan}",
                    "## Rollback Plan\n{rollback_plan}",
                    "## Agent Info\nCompleted by: DevOps Specialist\nBranch: {branch}\nCommits: {commit_count}"
                ],
                required_tests=[
                    "docker build .",
                    "docker-compose up -d",
                    "kubectl apply --dry-run"
                ],
                required_checks=[
                    "lint",
                    "security-scan",
                    "terraform-validate"
                ],
                reviewers=["devops-team"],
                labels=["devops", "infrastructure", "deployment"]
            ),
            llm_model="deepseek-coder-33b",
            context_size=16000
        ),
        
        AgentSpecialty.TESTING: SpecialistAgent(
            name="Testing Specialist",
            specialty=AgentSpecialty.TESTING,
            expertise=[
                "Unit Testing", "Integration Testing", "E2E Testing",
                "Test Automation", "Jest", "Pytest", "Playwright"
            ],
            file_patterns=[
                "*.test.ts", "*.test.js", "*.spec.ts", "*.spec.js",
                "*_test.py", "test_*.py", "tests/**/*", "e2e/**/*"
            ],
            keywords=[
                "test", "testing", "unit test", "integration test",
                "e2e", "coverage", "automation"
            ],
            pr_template=PRTemplate(
                title_format="[Testing] {ticket_title}",
                sections=[
                    "## Ticket\nCloses #{ticket_id}\n\n{ticket_url}",
                    "## Changes\n{changes_summary}",
                    "## Tests Added\n{test_list}",
                    "## Coverage\n- Before: {coverage_before}%\n- After: {coverage_after}%\n- Increase: +{coverage_increase}%",
                    "## Testing\n- [ ] All tests pass\n- [ ] New tests added\n- [ ] Edge cases covered\n- [ ] Error cases covered",
                    "## Test Types\n- [ ] Unit tests\n- [ ] Integration tests\n- [ ] E2E tests\n- [ ] Performance tests",
                    "## Test Results\n{test_results}",
                    "## Agent Info\nCompleted by: Testing Specialist\nBranch: {branch}\nCommits: {commit_count}"
                ],
                required_tests=[
                    "npm test",
                    "npm run test:coverage",
                    "npm run test:e2e"
                ],
                required_checks=[
                    "lint",
                    "coverage-check"
                ],
                reviewers=["testing-team"],
                labels=["testing", "quality", "coverage"]
            ),
            llm_model="deepseek-coder-33b",
            context_size=16000
        ),
        
        AgentSpecialty.DOCUMENTATION: SpecialistAgent(
            name="Documentation Specialist",
            specialty=AgentSpecialty.DOCUMENTATION,
            expertise=[
                "Technical Writing", "API Documentation", "Guides",
                "README", "Markdown", "Documentation Sites"
            ],
            file_patterns=[
                "*.md", "docs/**/*", "README*", "CHANGELOG*",
                "*.mdx", "docusaurus/**/*"
            ],
            keywords=[
                "documentation", "docs", "readme", "guide",
                "tutorial", "api docs", "changelog"
            ],
            pr_template=PRTemplate(
                title_format="[Docs] {ticket_title}",
                sections=[
                    "## Ticket\nCloses #{ticket_id}\n\n{ticket_url}",
                    "## Changes\n{changes_summary}",
                    "## Documentation Updates\n{doc_list}",
                    "## Testing\n- [ ] Links verified\n- [ ] Code examples tested\n- [ ] Spelling checked\n- [ ] Grammar checked",
                    "## Completeness\n- [ ] All sections complete\n- [ ] Examples provided\n- [ ] Screenshots added (if needed)\n- [ ] API reference updated",
                    "## Accessibility\n- [ ] Alt text for images\n- [ ] Clear headings\n- [ ] Simple language\n- [ ] Code examples accessible",
                    "## Agent Info\nCompleted by: Documentation Specialist\nBranch: {branch}\nCommits: {commit_count}"
                ],
                required_tests=[
                    "npm run docs:build",
                    "npm run docs:lint"
                ],
                required_checks=[
                    "spell-check",
                    "link-check",
                    "markdown-lint"
                ],
                reviewers=["docs-team"],
                labels=["documentation", "docs"]
            ),
            llm_model="gpt-4",
            context_size=8000
        ),
        
        AgentSpecialty.SECURITY: SpecialistAgent(
            name="Security Specialist",
            specialty=AgentSpecialty.SECURITY,
            expertise=[
                "Security", "Authentication", "Authorization", "Encryption",
                "Vulnerability Scanning", "Penetration Testing", "OWASP"
            ],
            file_patterns=[
                "*auth*", "*security*", "*crypto*", "*encrypt*",
                "*.key", "*.pem", "*.cert"
            ],
            keywords=[
                "security", "auth", "authentication", "authorization",
                "encryption", "vulnerability", "penetration", "owasp"
            ],
            pr_template=PRTemplate(
                title_format="[Security] {ticket_title}",
                sections=[
                    "## Ticket\nCloses #{ticket_id}\n\n{ticket_url}",
                    "## Changes\n{changes_summary}",
                    "## Security Impact\n{security_impact}",
                    "## Testing\n- [ ] Security tests pass\n- [ ] Vulnerability scan clean\n- [ ] Penetration test passed\n- [ ] OWASP Top 10 checked",
                    "## Security Checklist\n- [ ] Input validation\n- [ ] Output encoding\n- [ ] Authentication verified\n- [ ] Authorization checked\n- [ ] Encryption used\n- [ ] Secrets managed properly\n- [ ] SQL injection prevented\n- [ ] XSS prevented\n- [ ] CSRF protection\n- [ ] Rate limiting",
                    "## Threat Model\n{threat_model}",
                    "## Mitigation\n{mitigation_steps}",
                    "## Agent Info\nCompleted by: Security Specialist\nBranch: {branch}\nCommits: {commit_count}"
                ],
                required_tests=[
                    "npm run test:security",
                    "npm run scan:vulnerabilities"
                ],
                required_checks=[
                    "security-scan",
                    "dependency-check",
                    "secret-scan"
                ],
                reviewers=["security-team"],
                labels=["security", "critical"]
            ),
            llm_model="deepseek-coder-33b",
            context_size=16000
        ),
        
        AgentSpecialty.DATABASE: SpecialistAgent(
            name="Database Specialist",
            specialty=AgentSpecialty.DATABASE,
            expertise=[
                "SQL", "PostgreSQL", "MongoDB", "Redis", "Database Design",
                "Migrations", "Indexing", "Query Optimization"
            ],
            file_patterns=[
                "migrations/**/*", "*.sql", "models/**/*",
                "schema/**/*", "db/**/*"
            ],
            keywords=[
                "database", "sql", "migration", "schema",
                "query", "index", "optimization"
            ],
            pr_template=PRTemplate(
                title_format="[Database] {ticket_title}",
                sections=[
                    "## Ticket\nCloses #{ticket_id}\n\n{ticket_url}",
                    "## Changes\n{changes_summary}",
                    "## Database Changes\n{db_changes}",
                    "## Migrations\n{migrations}",
                    "## Testing\n- [ ] Migration up succeeds\n- [ ] Migration down succeeds\n- [ ] Data integrity verified\n- [ ] Performance tested",
                    "## Performance\n- [ ] Indexes added\n- [ ] Query optimization done\n- [ ] Query time: {query_time}ms\n- [ ] Explain plan reviewed",
                    "## Data Safety\n- [ ] Backup taken\n- [ ] Rollback plan ready\n- [ ] Data validation added\n- [ ] Constraints verified",
                    "## Breaking Changes\n{breaking_changes}",
                    "## Migration Steps\n{migration_steps}",
                    "## Agent Info\nCompleted by: Database Specialist\nBranch: {branch}\nCommits: {commit_count}"
                ],
                required_tests=[
                    "pytest tests/db/",
                    "npm run db:test"
                ],
                required_checks=[
                    "migration-check",
                    "schema-validate"
                ],
                reviewers=["database-team"],
                labels=["database", "migration"]
            ),
            llm_model="deepseek-coder-33b",
            context_size=16000
        ),
    }
    
    @classmethod
    def get_agent(cls, specialty: AgentSpecialty) -> SpecialistAgent:
        """Get agent by specialty"""
        return cls.AGENTS[specialty]
    
    @classmethod
    def match_agent(cls, ticket: Dict) -> SpecialistAgent:
        """
        Match ticket to best specialist agent
        
        Scoring based on:
        - File patterns in affected files
        - Keywords in title/description
        - Labels/tags
        """
        scores = {}
        
        for specialty, agent in cls.AGENTS.items():
            score = 0
            
            # Check file patterns
            affected_files = ticket.get('affected_files', [])
            for file_path in affected_files:
                for pattern in agent.file_patterns:
                    if cls._matches_pattern(file_path, pattern):
                        score += 10
            
            # Check keywords
            text = f"{ticket.get('title', '')} {ticket.get('description', '')}".lower()
            for keyword in agent.keywords:
                if keyword in text:
                    score += 5
            
            # Check labels
            labels = ticket.get('labels', [])
            for label in labels:
                if label.lower() in agent.keywords:
                    score += 15
            
            scores[specialty] = score
        
        # Return agent with highest score
        best_specialty = max(scores, key=scores.get)
        return cls.AGENTS[best_specialty]
    
    @staticmethod
    def _matches_pattern(file_path: str, pattern: str) -> bool:
        """Check if file matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)


class PRGenerator:
    """Generate PR from template and context"""
    
    def __init__(self, agent: SpecialistAgent):
        self.agent = agent
    
    def generate_pr(
        self, 
        ticket: Dict,
        branch: str,
        changes: Dict,
        test_results: Dict
    ) -> Dict:
        """
        Generate PR from template
        
        Returns:
        {
            "title": "...",
            "body": "...",
            "labels": [...],
            "reviewers": [...],
            "required_checks": [...]
        }
        """
        template = self.agent.pr_template
        
        # Format title
        title = template.title_format.format(
            ticket_title=ticket['title']
        )
        
        # Build body from sections
        body_parts = []
        for section in template.sections:
            formatted = self._format_section(
                section,
                ticket=ticket,
                branch=branch,
                changes=changes,
                test_results=test_results
            )
            body_parts.append(formatted)
        
        body = "\n\n".join(body_parts)
        
        return {
            "title": title,
            "body": body,
            "labels": template.labels,
            "reviewers": template.reviewers,
            "required_checks": template.required_checks,
            "required_tests": template.required_tests
        }
    
    def _format_section(
        self,
        section: str,
        ticket: Dict,
        branch: str,
        changes: Dict,
        test_results: Dict
    ) -> str:
        """Format section with context"""
        return section.format(
            ticket_id=ticket.get('id', ''),
            ticket_url=ticket.get('url', ''),
            ticket_title=ticket.get('title', ''),
            changes_summary=self._summarize_changes(changes),
            branch=branch,
            commit_count=changes.get('commit_count', 0),
            screenshots=self._format_screenshots(changes),
            component_list=self._format_components(changes),
            bundle_size=changes.get('bundle_size', 'N/A'),
            lighthouse_score=changes.get('lighthouse_score', 'N/A'),
            api_changes=self._format_api_changes(changes),
            db_migrations=self._format_migrations(changes),
            response_time=changes.get('response_time', 'N/A'),
            memory_usage=changes.get('memory_usage', 'N/A'),
            breaking_changes=self._format_breaking_changes(changes),
            migration_steps=self._format_migration_steps(changes),
            infra_changes=self._format_infra_changes(changes),
            deployment_impact=self._format_deployment_impact(changes),
            rollout_plan=self._format_rollout_plan(changes),
            rollback_plan=self._format_rollback_plan(changes),
            test_list=self._format_test_list(test_results),
            coverage_before=test_results.get('coverage_before', 0),
            coverage_after=test_results.get('coverage_after', 0),
            coverage_increase=test_results.get('coverage_increase', 0),
            test_results=self._format_test_results(test_results),
            doc_list=self._format_doc_list(changes),
            security_impact=self._format_security_impact(changes),
            threat_model=self._format_threat_model(changes),
            mitigation_steps=self._format_mitigation(changes),
            db_changes=self._format_db_changes(changes),
            migrations=self._format_migrations(changes),
            query_time=changes.get('query_time', 'N/A')
        )
    
    def _summarize_changes(self, changes: Dict) -> str:
        """Summarize code changes"""
        files = changes.get('files', [])
        summary = []
        for file in files:
            summary.append(f"- `{file['path']}`: {file['summary']}")
        return "\n".join(summary) if summary else "No changes"
    
    def _format_screenshots(self, changes: Dict) -> str:
        """Format screenshots"""
        screenshots = changes.get('screenshots', [])
        if not screenshots:
            return "No UI changes"
        return "\n".join([f"![{s['title']}]({s['url']})" for s in screenshots])
    
    def _format_components(self, changes: Dict) -> str:
        """Format component list"""
        components = changes.get('components', [])
        if not components:
            return "No component changes"
        return "\n".join([f"- {c}" for c in components])
    
    def _format_api_changes(self, changes: Dict) -> str:
        """Format API changes"""
        api_changes = changes.get('api_changes', [])
        if not api_changes:
            return "No API changes"
        return "\n".join([f"- {c}" for c in api_changes])
    
    def _format_migrations(self, changes: Dict) -> str:
        """Format database migrations"""
        migrations = changes.get('migrations', [])
        if not migrations:
            return "No migrations"
        return "\n".join([f"- {m}" for m in migrations])
    
    def _format_breaking_changes(self, changes: Dict) -> str:
        """Format breaking changes"""
        breaking = changes.get('breaking_changes', [])
        if not breaking:
            return "No breaking changes"
        return "\n".join([f"- {b}" for b in breaking])
    
    def _format_migration_steps(self, changes: Dict) -> str:
        """Format migration steps"""
        steps = changes.get('migration_steps', [])
        if not steps:
            return "No migration needed"
        return "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
    
    def _format_infra_changes(self, changes: Dict) -> str:
        """Format infrastructure changes"""
        infra = changes.get('infra_changes', [])
        if not infra:
            return "No infrastructure changes"
        return "\n".join([f"- {i}" for i in infra])
    
    def _format_deployment_impact(self, changes: Dict) -> str:
        """Format deployment impact"""
        impact = changes.get('deployment_impact', '')
        return impact if impact else "No deployment impact"
    
    def _format_rollout_plan(self, changes: Dict) -> str:
        """Format rollout plan"""
        plan = changes.get('rollout_plan', [])
        if not plan:
            return "Standard rollout"
        return "\n".join([f"{i+1}. {s}" for i, s in enumerate(plan)])
    
    def _format_rollback_plan(self, changes: Dict) -> str:
        """Format rollback plan"""
        plan = changes.get('rollback_plan', [])
        if not plan:
            return "Standard rollback"
        return "\n".join([f"{i+1}. {s}" for i, s in enumerate(plan)])
    
    def _format_test_list(self, test_results: Dict) -> str:
        """Format test list"""
        tests = test_results.get('tests_added', [])
        if not tests:
            return "No tests added"
        return "\n".join([f"- {t}" for t in tests])
    
    def _format_test_results(self, test_results: Dict) -> str:
        """Format test results"""
        return f"""
- Total: {test_results.get('total', 0)}
- Passed: {test_results.get('passed', 0)}
- Failed: {test_results.get('failed', 0)}
- Duration: {test_results.get('duration', 0)}s
"""
    
    def _format_doc_list(self, changes: Dict) -> str:
        """Format documentation list"""
        docs = changes.get('docs', [])
        if not docs:
            return "No documentation changes"
        return "\n".join([f"- {d}" for d in docs])
    
    def _format_security_impact(self, changes: Dict) -> str:
        """Format security impact"""
        impact = changes.get('security_impact', '')
        return impact if impact else "No security impact"
    
    def _format_threat_model(self, changes: Dict) -> str:
        """Format threat model"""
        threats = changes.get('threats', [])
        if not threats:
            return "No threats identified"
        return "\n".join([f"- {t}" for t in threats])
    
    def _format_mitigation(self, changes: Dict) -> str:
        """Format mitigation steps"""
        steps = changes.get('mitigation', [])
        if not steps:
            return "No mitigation needed"
        return "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
    
    def _format_db_changes(self, changes: Dict) -> str:
        """Format database changes"""
        db_changes = changes.get('db_changes', [])
        if not db_changes:
            return "No database changes"
        return "\n".join([f"- {c}" for c in db_changes])


# Example usage
if __name__ == "__main__":
    # Match agent to ticket
    ticket = {
        "id": "123",
        "title": "Add user authentication",
        "description": "Implement JWT authentication for API endpoints",
        "affected_files": ["api/auth.py", "api/routes/users.py"],
        "labels": ["backend", "security"]
    }
    
    agent = SpecialistAgentRegistry.match_agent(ticket)
    print(f"Matched agent: {agent.name}")
    print(f"Specialty: {agent.specialty.value}")
    
    # Generate PR
    pr_gen = PRGenerator(agent)
    pr = pr_gen.generate_pr(
        ticket=ticket,
        branch="feature/ticket-123-add-user-auth",
        changes={
            "files": [
                {"path": "api/auth.py", "summary": "Added JWT authentication"},
                {"path": "api/routes/users.py", "summary": "Added auth middleware"}
            ],
            "api_changes": ["POST /api/auth/login", "POST /api/auth/refresh"],
            "commit_count": 3
        },
        test_results={
            "total": 15,
            "passed": 15,
            "failed": 0,
            "duration": 2.5
        }
    )
    
    print("\nGenerated PR:")
    print(f"Title: {pr['title']}")
    print(f"\nBody:\n{pr['body']}")
    print(f"\nLabels: {pr['labels']}")
    print(f"Reviewers: {pr['reviewers']}")
