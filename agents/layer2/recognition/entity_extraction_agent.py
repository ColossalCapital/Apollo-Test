"""
Entity Extraction Agent - LLM-Powered Entity Extraction for Knowledge Graphs

Layer 2 Entity Recognition agent that extracts entities and prepares them
for knowledge graph storage across all 19 graphs.
"""

from typing import Dict, Any, List
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class EntityExtractionAgent(Layer2Agent):
    """
    Entity Extraction - LLM-powered entity extraction for knowledge graphs
    
    Extracts entities for all 19 knowledge graphs:
    - Business Graph (clients, projects, revenue)
    - Personal Graph (friends, family, events)
    - Technical Graph (code, tech stack, architecture)
    - Financial Graph (stocks, trades, portfolios)
    - And 15 more specialized graphs
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # 19 Knowledge Graphs
        self.graph_types = [
            'business', 'personal', 'technical', 'narrative',  # Tier 1: User
            'financial', 'scientific', 'geographic', 'social', 'literary',  # Tier 2: Domain
            'workflow', 'semantic', 'temporal',  # Tier 3: Meta
            'slang', 'memes', 'music', 'humor',  # Tier 4: Communication
            'news', 'community', 'firstperson'  # Tier 5: Real-time
        ]
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="entity_extraction",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered entity extraction for all 19 knowledge graphs",
            capabilities=["entity_extraction", "multi_graph_classification", "entity_linking", "graph_routing"],
            dependencies=["person_recognition", "company_recognition", "topic_recognition"]
        )
    
    async def analyze(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """
        Extract entities and route to appropriate knowledge graphs
        
        Args:
            parsed_data: Parsed data from Layer 1 agents
            
        Returns:
            AgentResult with entities categorized by graph type
        """
        
        prompt = f"""You are an expert at extracting entities for knowledge graphs. Analyze this data and extract entities for ALL relevant graphs.

PARSED DATA:
{json.dumps(parsed_data, indent=2)}

EXTRACT ENTITIES FOR THESE 19 GRAPHS:

**Tier 1: User Graphs**
1. Business Graph - Work entities (clients, projects, revenue, meetings)
2. Personal Graph - Personal entities (friends, family, life events)
3. Technical Graph - Tech entities (code, frameworks, architecture, bugs)
4. Narrative Graph - Story entities (metaphors, narratives, meanings)

**Tier 2: Domain Graphs**
5. Financial Graph - Finance entities (stocks, trades, portfolios, markets)
6. Scientific Graph - Science entities (papers, experiments, formulas)
7. Geographic Graph - Location entities (places, routes, regions)
8. Social Graph - Public entities (figures, organizations, events)
9. Literary Graph - Literature entities (books, authors, characters)

**Tier 3: Meta Graphs**
10. Workflow Graph - Workflow entities (tasks, processes, patterns)
11. Semantic Graph - Concept entities (meanings, relationships)
12. Temporal Graph - Time entities (events, sequences, timelines)

**Tier 4: Communication Graphs**
13. Slang Graph - Slang entities (abbreviations, neologisms)
14. Memes Graph - Meme entities (references, formats, context)
15. Music Graph - Music entities (songs, artists, lyrics)
16. Humor Graph - Humor entities (wordplay, puns, innuendo)

**Tier 5: Real-time Graphs**
17. News Graph - News entities (articles, sources, topics)
18. Community Graph - Community entities (forums, tribes, groups)
19. FirstPerson Graph - Personal expression (posts, multimedia)

Return as JSON with entities categorized by graph:
{{
    "business_graph": [
        {{
            "entity_id": "b1",
            "entity_type": "client",
            "name": "Acme Corp",
            "properties": {{
                "industry": "technology",
                "revenue": 1000000,
                "status": "active"
            }},
            "confidence": 0.95
        }},
        {{
            "entity_id": "b2",
            "entity_type": "project",
            "name": "Q4 Integration",
            "properties": {{
                "status": "in_progress",
                "deadline": "2025-12-31",
                "budget": 50000
            }},
            "confidence": 0.90
        }}
    ],
    "personal_graph": [
        {{
            "entity_id": "p1",
            "entity_type": "friend",
            "name": "John Smith",
            "properties": {{
                "relationship": "close_friend",
                "known_since": "2015",
                "interests": ["technology", "hiking"]
            }},
            "confidence": 0.98
        }}
    ],
    "financial_graph": [
        {{
            "entity_id": "f1",
            "entity_type": "stock",
            "name": "AAPL",
            "properties": {{
                "sector": "technology",
                "market_cap": 3000000000000,
                "owned": true
            }},
            "confidence": 1.0
        }}
    ],
    "technical_graph": [
        {{
            "entity_id": "t1",
            "entity_type": "framework",
            "name": "React",
            "properties": {{
                "language": "JavaScript",
                "version": "18.0",
                "used_in": ["project1", "project2"]
            }},
            "confidence": 1.0
        }}
    ],
    "graph_routing": {{
        "primary_graphs": ["business", "technical"],
        "secondary_graphs": ["personal", "financial"],
        "cross_graph_links": [
            {{"from": "business.b1", "to": "personal.p1", "relationship": "client_is_friend"}}
        ]
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
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            entity_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graphs
            if self.kg_client:
                await self._store_entities_in_graphs(entity_data)
            
            return AgentResult(
                success=True,
                data=entity_data,
                metadata={'agent': self.metadata.name, 'layer': 'recognition'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_entities_in_graphs(self, entity_data: Dict[str, Any]):
        """Store entities in appropriate knowledge graphs"""
        if not self.kg_client:
            return
        
        # Store entities in each graph
        for graph_type in self.graph_types:
            graph_key = f'{graph_type}_graph'
            entities = entity_data.get(graph_key, [])
            
            for entity in entities:
                await self.kg_client.create_entity(
                    entity_type=entity['entity_type'],
                    data=entity,
                    graph_type=graph_type
                )
        
        # Create cross-graph links
        for link in entity_data.get('graph_routing', {}).get('cross_graph_links', []):
            await self.kg_client.create_cross_graph_link(
                from_entity=link['from'],
                to_entity=link['to'],
                relationship=link['relationship']
            )
