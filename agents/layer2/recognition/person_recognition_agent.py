"""
Person Recognition Agent - LLM-Powered Entity Recognition

Layer 2 Entity Recognition agent that uses LLM to identify and extract
person entities from parsed data.
"""

from typing import Dict, Any, List
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class PersonRecognitionAgent(Layer2Agent):
    """
    Person Recognition - LLM-powered person entity extraction
    
    Takes structured data from Layer 1 and identifies:
    - Person names and titles
    - Contact information
    - Company affiliations
    - Relationships to other entities
    - Historical context
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="person_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered person entity recognition and extraction",
            capabilities=["person_extraction", "relationship_detection", "contact_enrichment", "deduplication"],
            dependencies=[]
        )
    
    async def recognize(self, structured_data: Dict[str, Any]) -> AgentResult:
        """
        Recognize person entities from structured data
        
        Args:
            structured_data: Parsed data from Layer 1 agents
            
        Returns:
            AgentResult with recognized person entities
        """
        
        prompt = f"""You are an expert at recognizing and extracting person entities from data.

STRUCTURED DATA:
{json.dumps(structured_data, indent=2)}

EXTRACT all people mentioned:
1. Full name
2. Email address (if available)
3. Phone number (if available)
4. Title/role
5. Company affiliation
6. Relationships to other entities
7. Context (how they're mentioned)
8. Is this an existing contact or new person?

Also:
9. Deduplicate (merge if same person mentioned multiple times)
10. Enrich with any additional context from the data

Return as JSON:
{{
    "people": [
        {{
            "name": "...",
            "email": "...",
            "phone": "...",
            "title": "...",
            "company": "...",
            "relationships": [
                {{"type": "works_at", "target": "Company X"}},
                {{"type": "reports_to", "target": "Jane Doe"}}
            ],
            "context": "...",
            "is_new": true|false,
            "confidence": 0.95
        }}
    ],
    "insights": {{
        "total_people": 0,
        "new_contacts": 0,
        "key_relationships": []
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
                await self._store_people_in_kg(recognized_data)
            
            return AgentResult(
                success=True,
                data=recognized_data,
                metadata={
                    'agent': self.metadata.name,
                    'model': 'phi-3-medium',
                    'people_count': len(recognized_data.get('people', []))
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_people_in_kg(self, people_data: Dict[str, Any]):
        """Store recognized people in knowledge graph"""
        if not self.kg_client:
            return
        
        for person in people_data.get('people', []):
            # Create or update person entity
            entity_id = await self.kg_client.create_or_update_entity(
                entity_type="person",
                data={
                    'name': person['name'],
                    'email': person.get('email'),
                    'phone': person.get('phone'),
                    'title': person.get('title'),
                    'company': person.get('company')
                }
            )
            
            # Create relationships
            for rel in person.get('relationships', []):
                await self.kg_client.create_relationship(
                    from_entity=entity_id,
                    to_entity=rel['target'],
                    relationship_type=rel['type']
                )
