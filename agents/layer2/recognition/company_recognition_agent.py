"""
Company Recognition Agent - LLM-Powered Company Entity Recognition

Layer 2 Entity Recognition agent that uses LLM to identify and extract
company entities from parsed data.
"""

from typing import Dict, Any, List
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class CompanyRecognitionAgent(Layer2Agent):
    """
    Company Recognition - LLM-powered company entity extraction
    
    Takes structured data from Layer 1 and identifies:
    - Company names and aliases
    - Industry and sector
    - Relationships to other entities
    - Business context
    - Historical interactions
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="company_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered company entity recognition and extraction",
            capabilities=["company_extraction", "industry_classification", "relationship_detection", "deduplication"],
            dependencies=[]
        )
    
    async def recognize(self, structured_data: Dict[str, Any]) -> AgentResult:
        """
        Recognize company entities from structured data
        
        Args:
            structured_data: Parsed data from Layer 1 agents
            
        Returns:
            AgentResult with recognized company entities
        """
        
        prompt = f"""You are an expert at recognizing and extracting company entities from data.

STRUCTURED DATA:
{json.dumps(structured_data, indent=2)}

EXTRACT all companies mentioned:
1. Full company name
2. Common aliases/abbreviations
3. Industry/sector
4. Size (startup, SMB, enterprise)
5. Relationship type (vendor, client, partner, competitor)
6. Contact information (if available)
7. Context (how they're mentioned)
8. Is this an existing company in our system?

Also:
9. Deduplicate (merge if same company mentioned multiple times)
10. Identify parent/subsidiary relationships
11. Detect industry connections

Return as JSON:
{{
    "companies": [
        {{
            "name": "Acme Corporation",
            "aliases": ["Acme Corp", "Acme Inc"],
            "industry": "Technology",
            "sector": "SaaS",
            "size": "enterprise",
            "relationship": "vendor",
            "contacts": [
                {{"name": "John Smith", "role": "Account Manager", "email": "..."}}
            ],
            "context": "Invoice for cloud services",
            "is_existing": true,
            "confidence": 0.95
        }}
    ],
    "relationships": [
        {{
            "from": "Acme Corporation",
            "to": "TechCorp",
            "type": "parent_company"
        }}
    ],
    "insights": {{
        "total_companies": 2,
        "new_companies": 0,
        "key_relationships": ["vendor", "partner"]
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            recognized_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_companies_in_kg(recognized_data)
            
            return AgentResult(
                success=True,
                data=recognized_data,
                metadata={
                    'agent': self.metadata.name,
                    'model': 'phi-3-medium',
                    'company_count': len(recognized_data.get('companies', []))
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_companies_in_kg(self, company_data: Dict[str, Any]):
        """Store recognized companies in knowledge graph"""
        if not self.kg_client:
            return
        
        for company in company_data.get('companies', []):
            # Create or update company entity
            entity_id = await self.kg_client.create_or_update_entity(
                entity_type="company",
                data={
                    'name': company['name'],
                    'aliases': company.get('aliases', []),
                    'industry': company.get('industry'),
                    'sector': company.get('sector'),
                    'size': company.get('size'),
                    'relationship': company.get('relationship')
                }
            )
            
            # Create relationships
            for contact in company.get('contacts', []):
                await self.kg_client.create_relationship(
                    from_entity=contact['name'],
                    to_entity=entity_id,
                    relationship_type="works_at"
                )
        
        # Store company-to-company relationships
        for rel in company_data.get('relationships', []):
            await self.kg_client.create_relationship(
                from_entity=rel['from'],
                to_entity=rel['to'],
                relationship_type=rel['type']
            )
