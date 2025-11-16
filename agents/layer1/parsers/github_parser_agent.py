"""
GitHub Parser Agent - LLM-Powered GitHub Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse GitHub API
responses into structured development intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class GitHubParserAgent(Layer1Agent):
    """
    GitHub Parser - LLM-powered repository and code activity parsing
    
    Takes raw GitHub API responses and extracts:
    - Pull request analysis
    - Issue tracking and sentiment
    - Code review insights
    - Contributor activity
    - Project health metrics
    - Development velocity
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="github_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered GitHub activity parsing and project analysis",
            capabilities=["pr_analysis", "issue_tracking", "code_review", "contributor_metrics"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw GitHub API response
        
        Args:
            raw_data: Raw GitHub API response (PR, issue, commit, etc.)
            
        Returns:
            AgentResult with structured development data
        """
        
        data_type = raw_data.get('type', 'pull_request')
        
        if data_type == 'pull_request':
            return await self._parse_pull_request(raw_data)
        elif data_type == 'issue':
            return await self._parse_issue(raw_data)
        elif data_type == 'commit':
            return await self._parse_commit(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_pull_request(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse pull request with LLM"""
        
        prompt = f"""You are an expert at analyzing pull requests. Extract structured information from this GitHub PR.

RAW PULL REQUEST DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. PR title and description
2. Author and reviewers
3. Branch information (source → target)
4. Changes summary (files changed, additions, deletions)
5. Purpose/intent of PR
6. Code quality assessment
7. Review comments and feedback
8. Merge status and conflicts
9. CI/CD status
10. Estimated complexity
11. Risk level
12. Action items

Return as JSON:
{{
    "pr_number": 123,
    "title": "...",
    "description": "...",
    "author": {{
        "username": "johndoe",
        "name": "John Doe"
    }},
    "reviewers": ["janedoe", "bobsmith"],
    "branches": {{
        "source": "feature/new-api",
        "target": "main"
    }},
    "changes": {{
        "files_changed": 12,
        "additions": 450,
        "deletions": 120,
        "net_change": 330
    }},
    "intent": "Add new REST API endpoints for user management",
    "quality_assessment": {{
        "code_quality": "good",
        "test_coverage": "adequate",
        "documentation": "needs_improvement"
    }},
    "review_feedback": [
        {{"reviewer": "janedoe", "status": "approved", "comments": 3}},
        {{"reviewer": "bobsmith", "status": "changes_requested", "comments": 5}}
    ],
    "merge_status": "mergeable",
    "conflicts": false,
    "ci_status": "passed",
    "complexity": "medium",
    "risk_level": "low",
    "action_items": [
        "Add documentation for new endpoints",
        "Address Bob's security concerns"
    ],
    "created_at": "2025-10-29T20:00:00Z",
    "updated_at": "2025-10-29T22:00:00Z"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_pr_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'pull_request'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_issue(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse GitHub issue with LLM"""
        
        prompt = f"""Analyze this GitHub issue and extract key information.

RAW ISSUE DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Issue title and description
2. Author and assignees
3. Labels and milestone
4. Issue type (bug, feature, enhancement, etc.)
5. Priority and severity
6. Steps to reproduce (if bug)
7. Expected vs actual behavior
8. Sentiment (frustrated, neutral, constructive)
9. Complexity estimate
10. Related issues
11. Action items

Return as JSON with these fields.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_issue_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'issue'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_commit(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse commit data"""
        pass
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic GitHub data parsing"""
        pass
    
    async def _store_pr_in_kg(self, pr_data: Dict[str, Any]):
        """Store parsed PR in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="pull_request",
            data=pr_data
        )
        
        # Create action items as tasks
        for action_item in pr_data.get('action_items', []):
            await self.kg_client.create_entity(
                entity_type="task",
                data={'description': action_item, 'source': 'github_pr'}
            )
    
    async def _store_issue_in_kg(self, issue_data: Dict[str, Any]):
        """Store parsed issue in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="github_issue",
            data=issue_data
        )
