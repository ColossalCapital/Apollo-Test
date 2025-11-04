"""
Relationship Recognition Agent - LLM-Powered Relationship Extraction

Layer 2 Entity Recognition agent that uses LLM to identify and categorize
relationships between entities from parsed data.
"""

from typing import Dict, Any, List
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class RelationshipRecognitionAgent(Layer2Agent):
    """
    Relationship Recognition - LLM-powered relationship extraction
    
    Takes parsed data and identifies:
    - Entity relationships (works_for, owns, partners_with)
    - Temporal relationships (before, after, during)
    - Causal relationships (causes, results_in)
    - Hierarchical relationships (parent_of, reports_to)
    - Semantic relationships (similar_to, opposite_of)
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="relationship_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered relationship extraction and categorization",
            capabilities=["relationship_extraction", "relationship_typing", "graph_creation", "link_prediction"],
            dependencies=["person_recognition", "company_recognition"]
        )
    
    async def analyze(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """
        Identify relationships from parsed data
        
        Args:
            parsed_data: Parsed data from Layer 1 agents
            
        Returns:
            AgentResult with identified relationships
        """
        
        prompt = f"""You are an expert at identifying relationships between entities. Analyze this data and extract all relationships.

PARSED DATA:
{json.dumps(parsed_data, indent=2)}

IDENTIFY:
1. All entities mentioned (people, companies, locations, concepts)
2. Relationships between entities
3. Relationship types (works_for, owns, partners_with, located_in, etc.)
4. Relationship strength (strong, medium, weak)
5. Relationship directionality (one-way, bidirectional)
6. Temporal context (when did relationship start/end)
7. Confidence in relationship

Return as JSON:
{{
    "entities": [
        {{"id": "e1", "name": "John Smith", "type": "person"}},
        {{"id": "e2", "name": "Acme Corp", "type": "company"}},
        {{"id": "e3", "name": "San Francisco", "type": "location"}},
        {{"id": "e4", "name": "Jane Doe", "type": "person"}}
    ],
    "relationships": [
        {{
            "from_entity": "e1",
            "to_entity": "e2",
            "relationship_type": "works_for",
            "relationship_label": "CEO",
            "strength": "strong",
            "directionality": "one_way",
            "confidence": 0.95,
            "temporal": {{
                "start_date": "2020-01-15",
                "end_date": null,
                "current": true
            }},
            "properties": {{
                "title": "CEO",
                "department": "Executive",
                "salary_range": "high"
            }}
        }},
        {{
            "from_entity": "e2",
            "to_entity": "e3",
            "relationship_type": "located_in",
            "relationship_label": "headquarters",
            "strength": "strong",
            "directionality": "one_way",
            "confidence": 0.98,
            "temporal": {{
                "start_date": "2020-01-15",
                "end_date": null,
                "current": true
            }},
            "properties": {{
                "address": "123 Main St",
                "office_type": "headquarters"
            }}
        }},
        {{
            "from_entity": "e1",
            "to_entity": "e4",
            "relationship_type": "reports_to",
            "relationship_label": "manager",
            "strength": "medium",
            "directionality": "one_way",
            "confidence": 0.85,
            "temporal": {{
                "start_date": "2021-06-01",
                "end_date": null,
                "current": true
            }},
            "properties": {{
                "reporting_structure": "direct",
                "frequency": "weekly"
            }}
        }}
    ],
    "graph_metadata": {{
        "total_entities": 4,
        "total_relationships": 3,
        "graph_density": 0.25,
        "connected_components": 1
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            relationship_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_relationships_in_kg(relationship_data)
            
            return AgentResult(
                success=True,
                data=relationship_data,
                metadata={'agent': self.metadata.name, 'layer': 'recognition'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_relationships_in_kg(self, relationship_data: Dict[str, Any]):
        """Store relationships in knowledge graph"""
        if not self.kg_client:
            return
        
        # Create entities
        for entity in relationship_data.get('entities', []):
            await self.kg_client.create_entity(
                entity_type=entity['type'],
                data=entity
            )
        
        # Create relationships
        for rel in relationship_data.get('relationships', []):
            await self.kg_client.create_relationship(
                from_entity=rel['from_entity'],
                to_entity=rel['to_entity'],
                relationship_type=rel['relationship_type'],
                properties={
                    'label': rel['relationship_label'],
                    'strength': rel['strength'],
                    'confidence': rel['confidence'],
                    'temporal': rel['temporal'],
                    **rel.get('properties', {})
                }
            )
