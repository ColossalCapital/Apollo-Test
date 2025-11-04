"""
Code Generation Agent - LLM-Powered Autonomous Code Generation

Layer 3 Domain Expert agent that uses LLM to autonomously generate code,
tests, and documentation.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class CodeGenerationAgent(Layer3Agent):
    """
    Code Generation Agent - LLM-powered autonomous code generation
    
    Provides:
    - Autonomous code generation from specs
    - Test generation
    - Documentation generation
    - Boilerplate generation
    - Code completion
    - Refactoring automation
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=180.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="code_generation_agent",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered autonomous code generation with tests and docs",
            capabilities=[
                "code_generation",
                "test_generation",
                "documentation_generation",
                "boilerplate_generation",
                "refactoring_automation"
            ],
            dependencies=["code_review_agent", "github_connector"]
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """
        Generate code autonomously
        
        Args:
            domain_data: Code generation requirements
            
        Returns:
            AgentResult with generated code
        """
        
        generation_type = domain_data.get('generation_type', 'full_implementation')
        
        if generation_type == 'full_implementation':
            return await self._generate_full_implementation(domain_data)
        elif generation_type == 'tests':
            return await self._generate_tests(domain_data)
        elif generation_type == 'documentation':
            return await self._generate_documentation(domain_data)
        elif generation_type == 'refactoring':
            return await self._generate_refactoring(domain_data)
        else:
            return await self._general_code_generation(domain_data)
    
    async def _generate_full_implementation(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Generate full implementation from specification"""
        
        prompt = f"""You are an expert software engineer. Generate a complete implementation from this specification.

SPECIFICATION:
{json.dumps(domain_data, indent=2)}

GENERATE:
1. Complete implementation code
2. Unit tests
3. Integration tests
4. API documentation
5. Usage examples
6. Error handling
7. Type definitions
8. Configuration

Return as JSON:
{{
    "implementation": {{
        "language": "python",
        "files": [
            {{
                "path": "src/user_service.py",
                "content": "class UserService:\\n    def __init__(self, db):\\n        self.db = db\\n\\n    async def create_user(self, user_data: dict) -> User:\\n        # Validate input\\n        if not user_data.get('email'):\\n            raise ValueError('Email is required')\\n        \\n        # Check if user exists\\n        existing = await self.db.users.find_one({{'email': user_data['email']}})\\n        if existing:\\n            raise ValueError('User already exists')\\n        \\n        # Create user\\n        user = User(**user_data)\\n        await self.db.users.insert_one(user.dict())\\n        return user"
            }}
        ]
    }},
    "tests": {{
        "files": [
            {{
                "path": "tests/test_user_service.py",
                "content": "import pytest\\nfrom src.user_service import UserService\\n\\n@pytest.mark.asyncio\\nasync def test_create_user_success(mock_db):\\n    service = UserService(mock_db)\\n    user_data = {{'email': 'test@example.com', 'name': 'Test User'}}\\n    \\n    user = await service.create_user(user_data)\\n    \\n    assert user.email == 'test@example.com'\\n    assert user.name == 'Test User'\\n\\n@pytest.mark.asyncio\\nasync def test_create_user_duplicate_email(mock_db):\\n    service = UserService(mock_db)\\n    mock_db.users.find_one.return_value = {{'email': 'test@example.com'}}\\n    \\n    with pytest.raises(ValueError, match='User already exists'):\\n        await service.create_user({{'email': 'test@example.com'}})"
            }}
        ]
    }},
    "documentation": {{
        "api_docs": "# User Service API\\n\\n## create_user\\n\\nCreates a new user in the system.\\n\\n**Parameters:**\\n- user_data (dict): User information including email and name\\n\\n**Returns:**\\n- User: Created user object\\n\\n**Raises:**\\n- ValueError: If email is missing or user already exists",
        "usage_examples": "# Create a user\\nservice = UserService(db)\\nuser = await service.create_user({\\n    'email': 'user@example.com',\\n    'name': 'John Doe'\\n})"
    }},
    "type_definitions": {{
        "files": [
            {{
                "path": "src/models.py",
                "content": "from pydantic import BaseModel, EmailStr\\nfrom typing import Optional\\n\\nclass User(BaseModel):\\n    email: EmailStr\\n    name: str\\n    created_at: Optional[datetime] = None"
            }}
        ]
    }},
    "configuration": {{
        "dependencies": ["pydantic", "pytest", "pytest-asyncio"],
        "environment_variables": ["DATABASE_URL"],
        "setup_instructions": "1. Install dependencies: pip install -r requirements.txt\\n2. Set DATABASE_URL environment variable\\n3. Run tests: pytest"
    }},
    "quality_metrics": {{
        "estimated_test_coverage": 0.85,
        "cyclomatic_complexity": 5,
        "maintainability_index": 75
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "deepseek-coder-6.7b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 6000
                }
            )
            
            llm_response = response.json()
            generated_code = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_generated_code_in_kg(generated_code)
            
            return AgentResult(
                success=True,
                data=generated_code,
                metadata={'agent': self.metadata.name, 'generation_type': 'full_implementation'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _generate_tests(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Generate tests for existing code"""
        pass
    
    async def _generate_documentation(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Generate documentation for existing code"""
        pass
    
    async def _generate_refactoring(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Generate refactored code"""
        pass
    
    async def _general_code_generation(self, domain_data: Dict[str, Any]) -> AgentResult:
        """General code generation"""
        pass
    
    async def _store_generated_code_in_kg(self, generated_code: Dict[str, Any]):
        """Store generated code in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="generated_code",
            data=generated_code,
            graph_type="technical"
        )
