"""
GitHub Projects Parser Agent - LLM-Powered GitHub Projects Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse GitHub Projects data
and extract project intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class GitHubProjectsParserAgent(Layer1Agent):
    """
    GitHub Projects Parser - LLM-powered GitHub Projects parsing
    
    Takes GitHub Projects data and extracts:
    - Development workflow patterns
    - Issue and PR relationships
    - Project velocity metrics
    - Code-to-task mapping
    - CI/CD integration insights
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="github_projects_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered GitHub Projects parsing with developer workflow intelligence",
            capabilities=["project_parsing", "workflow_analysis", "velocity_tracking", "code_task_mapping"],
            dependencies=["github_projects_connector"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from GitHub Projects"""
        
        prompt = f"""You are an expert at analyzing developer workflows. Extract structured information from this GitHub Projects data.

GITHUB PROJECTS DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Project structure and organization
2. Issue and PR relationships
3. Development velocity metrics
4. Code commit patterns
5. CI/CD integration status
6. Milestone progress
7. Label usage and categorization
8. Developer contributions
9. Blockers and dependencies
10. Automation opportunities

Return as JSON with detailed GitHub Projects analysis including developer workflow patterns, velocity metrics, and code-to-task mapping.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_github_projects_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'github_projects'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_github_projects_in_kg(self, projects_data: Dict[str, Any]):
        """Store parsed GitHub Projects data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="github_project",
            data=projects_data,
            graph_type="technical"
        )
