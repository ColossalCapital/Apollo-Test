"""
Code Review Agent - LLM-Powered Autonomous Code Analysis

Layer 3 Domain Expert agent that uses LLM to provide autonomous code review,
quality analysis, and improvement suggestions.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class CodeReviewAgent(Layer3Agent):
    """
    Code Review Agent - LLM-powered autonomous code analysis
    
    Provides:
    - Automated code review
    - Security vulnerability detection
    - Performance optimization suggestions
    - Code quality metrics
    - Best practice recommendations
    - Refactoring suggestions
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="code_review_agent",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered autonomous code review with security and quality analysis",
            capabilities=[
                "code_review",
                "security_analysis",
                "performance_optimization",
                "quality_metrics",
                "refactoring_suggestions"
            ],
            dependencies=["github_connector"]
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """
        Provide autonomous code analysis
        
        Args:
            domain_data: Code requiring review
            
        Returns:
            AgentResult with code review insights
        """
        
        analysis_type = domain_data.get('analysis_type', 'full_review')
        
        if analysis_type == 'full_review':
            return await self._full_code_review(domain_data)
        elif analysis_type == 'security':
            return await self._security_analysis(domain_data)
        elif analysis_type == 'performance':
            return await self._performance_analysis(domain_data)
        elif analysis_type == 'quality':
            return await self._quality_analysis(domain_data)
        else:
            return await self._general_code_analysis(domain_data)
    
    async def _full_code_review(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Full autonomous code review with LLM"""
        
        prompt = f"""You are an expert code reviewer. Perform a comprehensive code review.

CODE TO REVIEW:
{json.dumps(domain_data, indent=2)}

ANALYZE:
1. Code quality and readability
2. Security vulnerabilities
3. Performance issues
4. Best practice violations
5. Potential bugs
6. Test coverage
7. Documentation quality
8. Architecture patterns
9. Error handling
10. Refactoring opportunities

Return as JSON:
{{
    "overall_score": 8.5,
    "summary": "Good code quality with minor improvements needed",
    "security": {{
        "score": 9.0,
        "issues": [
            {{
                "severity": "medium",
                "type": "SQL Injection",
                "location": "line 45",
                "description": "User input not sanitized before SQL query",
                "recommendation": "Use parameterized queries or ORM"
            }}
        ]
    }},
    "performance": {{
        "score": 7.5,
        "issues": [
            {{
                "severity": "low",
                "type": "N+1 Query",
                "location": "line 120-135",
                "description": "Loop making database queries",
                "recommendation": "Use eager loading or batch queries",
                "estimated_improvement": "50% faster"
            }}
        ]
    }},
    "quality": {{
        "score": 8.0,
        "metrics": {{
            "cyclomatic_complexity": 12,
            "lines_of_code": 250,
            "comment_ratio": 0.15,
            "test_coverage": 0.75
        }},
        "issues": [
            {{
                "severity": "low",
                "type": "Long Function",
                "location": "line 50-150",
                "description": "Function exceeds 100 lines",
                "recommendation": "Break into smaller functions"
            }}
        ]
    }},
    "bugs": [
        {{
            "severity": "high",
            "type": "Null Pointer",
            "location": "line 78",
            "description": "Potential null reference without check",
            "recommendation": "Add null check or use optional chaining"
        }}
    ],
    "best_practices": [
        {{
            "violated": "DRY Principle",
            "location": "lines 100-120, 200-220",
            "description": "Duplicate code in two functions",
            "recommendation": "Extract common logic into shared function"
        }}
    ],
    "refactoring": [
        {{
            "priority": "high",
            "type": "Extract Method",
            "location": "line 50-150",
            "description": "Long function with multiple responsibilities",
            "estimated_effort": "2 hours"
        }},
        {{
            "priority": "medium",
            "type": "Introduce Parameter Object",
            "location": "line 25",
            "description": "Function has 8 parameters",
            "estimated_effort": "1 hour"
        }}
    ],
    "documentation": {{
        "score": 6.0,
        "missing": ["API documentation", "Complex algorithm explanation"],
        "recommendation": "Add JSDoc/docstrings for public methods"
    }},
    "testing": {{
        "coverage": 0.75,
        "missing_tests": ["Error handling paths", "Edge cases"],
        "recommendation": "Add tests for error scenarios"
    }},
    "action_items": [
        {{
            "priority": "critical",
            "item": "Fix SQL injection vulnerability",
            "estimated_effort": "30 minutes"
        }},
        {{
            "priority": "high",
            "item": "Add null check on line 78",
            "estimated_effort": "5 minutes"
        }},
        {{
            "priority": "medium",
            "item": "Refactor long function",
            "estimated_effort": "2 hours"
        }}
    ]
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "deepseek-coder-6.7b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            review_result = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_code_review_in_kg(review_result)
            
            return AgentResult(
                success=True,
                data=review_result,
                metadata={'agent': self.metadata.name, 'analysis_type': 'full_review'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _security_analysis(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Security-focused code analysis"""
        pass
    
    async def _performance_analysis(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Performance-focused code analysis"""
        pass
    
    async def _quality_analysis(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Quality-focused code analysis"""
        pass
    
    async def _general_code_analysis(self, domain_data: Dict[str, Any]) -> AgentResult:
        """General code analysis"""
        pass
    
    async def _store_code_review_in_kg(self, review_result: Dict[str, Any]):
        """Store code review in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="code_review",
            data=review_result,
            graph_type="technical"
        )
