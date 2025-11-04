"""
Recruiting Agent - LLM-Powered Talent Acquisition

Layer 3 Domain Expert agent that assists with recruiting and talent acquisition.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class RecruitingAgent(Layer3Agent):
    """
    Recruiting Agent - LLM-powered talent acquisition
    
    Provides:
    - Resume screening
    - Job description creation
    - Candidate matching
    - Interview question generation
    - Offer letter creation
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="recruiting",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered recruiting and talent acquisition",
            capabilities=[
                "resume_screening",
                "job_description_creation",
                "candidate_matching",
                "interview_questions",
                "offer_letter_generation"
            ],
            dependencies=["knowledge_graph", "hr"],
            
            # Metadata for filtering
            entity_types=[EntityType.BUSINESS],
            app_contexts=[AppContext.ATLAS],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Provide recruiting assistance"""
        
        task_type = domain_data.get('task', 'screen_resume')
        
        if task_type == 'screen_resume':
            return await self._screen_resume(domain_data)
        elif task_type == 'create_job_description':
            return await self._create_job_description(domain_data)
        elif task_type == 'generate_interview_questions':
            return await self._generate_interview_questions(domain_data)
        else:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': 'Unknown task type'}
            )
    
    async def _screen_resume(self, data: Dict[str, Any]) -> AgentResult:
        """Screen a resume against job requirements"""
        
        resume = data.get('resume', '')
        job_requirements = data.get('requirements', [])
        
        prompt = f"""You are an expert recruiter. Screen this resume against the job requirements.

RESUME:
{resume}

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

ANALYZE:
1. Skills match (technical and soft skills)
2. Experience level match
3. Education requirements
4. Cultural fit indicators
5. Red flags or concerns
6. Strengths and unique qualifications
7. Overall recommendation (Strong Yes, Yes, Maybe, No)
8. Interview focus areas
9. Questions to ask candidate
10. Salary range recommendation

Return as JSON with detailed screening analysis.
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
            screening = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_recruiting_in_kg(screening)
            
            return AgentResult(
                success=True,
                data=screening,
                metadata={'agent': self.metadata.name, 'task': 'screen_resume'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _create_job_description(self, data: Dict[str, Any]) -> AgentResult:
        """Create a job description"""
        
        role = data.get('role', '')
        company = data.get('company', '')
        
        prompt = f"""You are an expert recruiter. Create a compelling job description.

ROLE: {role}
COMPANY: {company}

CREATE JOB DESCRIPTION WITH:
1. Engaging role summary
2. Key responsibilities
3. Required qualifications
4. Preferred qualifications
5. Company culture and benefits
6. Growth opportunities
7. Salary range (if provided)
8. Application instructions

Return as JSON with complete job description.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            job_description = json.loads(llm_response['choices'][0]['message']['content'])
            
            return AgentResult(
                success=True,
                data=job_description,
                metadata={'agent': self.metadata.name, 'task': 'create_job_description'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _generate_interview_questions(self, data: Dict[str, Any]) -> AgentResult:
        """Generate interview questions"""
        
        role = data.get('role', '')
        level = data.get('level', 'mid')
        
        prompt = f"""You are an expert recruiter. Generate interview questions.

ROLE: {role}
LEVEL: {level}

GENERATE:
1. Technical questions (5-7)
2. Behavioral questions (5-7)
3. Situational questions (3-5)
4. Culture fit questions (3-5)
5. Questions for candidate to ask
6. Evaluation criteria for each question

Return as JSON with complete interview guide.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            questions = json.loads(llm_response['choices'][0]['message']['content'])
            
            return AgentResult(
                success=True,
                data=questions,
                metadata={'agent': self.metadata.name, 'task': 'generate_interview_questions'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_recruiting_in_kg(self, recruiting: Dict[str, Any]):
        """Store recruiting data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="recruiting_analysis",
            data=recruiting,
            graph_type="business"
        )
