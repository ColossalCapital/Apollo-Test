"""
Apollo Neo4j Knowledge Graph Client

Connects Apollo AI agents to Neo4j knowledge graphs for:
- Context discovery
- Workflow pattern learning
- Relationship traversal
- Decision making
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
import os

logger = logging.getLogger(__name__)


@dataclass
class GraphEntity:
    """Entity from knowledge graph"""
    id: str
    name: str
    type: str
    graph: str  # business, personal, technical, narrative
    properties: Dict[str, Any]


@dataclass
class GraphRelationship:
    """Relationship from knowledge graph"""
    from_entity: str
    to_entity: str
    type: str
    properties: Dict[str, Any]


@dataclass
class WorkflowPattern:
    """Discovered workflow pattern"""
    id: str
    name: str
    trigger: str
    steps: List[str]
    success_rate: float
    usage_count: int


class Neo4jKnowledgeGraph:
    """
    Neo4j Knowledge Graph Client for Apollo AI Agents
    
    Usage:
        kg = Neo4jKnowledgeGraph()
        await kg.connect()
        
        # Discover workflow
        workflow = await kg.discover_workflow("meeting request")
        
        # Find context
        context = await kg.find_entity_context("Jacob", max_depth=3)
        
        # Query graph
        results = await kg.query_graph("business", 
            "MATCH (p:Person)-[:WORKS_ON]->(proj) RETURN p, proj")
    """
    
    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None
    ):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "atlas_dev_password")
        self.driver: Optional[AsyncDriver] = None
        
    async def connect(self):
        """Connect to Neo4j"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Test connection
            async with self.driver.session() as session:
                result = await session.run("RETURN 1")
                await result.single()
            logger.info(f"✅ Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    async def close(self):
        """Close connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WORKFLOW DISCOVERY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def discover_workflow(self, trigger: str) -> Optional[WorkflowPattern]:
        """
        Discover best workflow pattern for a trigger
        
        Args:
            trigger: Trigger description (e.g., "meeting request")
            
        Returns:
            Best matching workflow pattern or None
            
        Example:
            workflow = await kg.discover_workflow("meeting request")
            # Returns: WorkflowPattern(
            #   name="Meeting Request Handler",
            #   steps=["parse_email", "check_calendar", "propose_times", ...]
            # )
        """
        query = """
        MATCH (w:WorkflowPattern)
        WHERE w.trigger CONTAINS $trigger
        RETURN w
        ORDER BY w.success_rate DESC, w.usage_count DESC
        LIMIT 1
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, trigger=trigger.lower())
            record = await result.single()
            
            if not record:
                logger.info(f"No workflow found for trigger: {trigger}")
                return None
            
            w = record["w"]
            return WorkflowPattern(
                id=w["id"],
                name=w["name"],
                trigger=w["trigger"],
                steps=w["steps"],
                success_rate=w["success_rate"],
                usage_count=w["usage_count"]
            )
    
    async def learn_workflow_success(self, workflow_id: str, success: bool):
        """
        Update workflow pattern based on execution result
        
        Args:
            workflow_id: Workflow pattern ID
            success: Whether execution was successful
        """
        query = """
        MATCH (w:WorkflowPattern {id: $workflow_id})
        SET w.usage_count = w.usage_count + 1
        SET w.success_rate = (w.success_rate * w.usage_count + $success_value) / (w.usage_count + 1)
        RETURN w
        """
        
        async with self.driver.session() as session:
            await session.run(
                query,
                workflow_id=workflow_id,
                success_value=1.0 if success else 0.0
            )
            logger.info(f"Updated workflow {workflow_id} success: {success}")
    
    async def create_workflow_pattern(
        self,
        name: str,
        trigger: str,
        steps: List[str],
        initial_success_rate: float = 0.5
    ) -> str:
        """
        Create new workflow pattern from successful execution
        
        Args:
            name: Workflow name
            trigger: Trigger description
            steps: List of step names
            initial_success_rate: Initial success rate (default 0.5)
            
        Returns:
            Workflow ID
        """
        import uuid
        workflow_id = f"workflow-{uuid.uuid4()}"
        
        query = """
        CREATE (w:WorkflowPattern {
            id: $id,
            name: $name,
            trigger: $trigger,
            steps: $steps,
            success_rate: $success_rate,
            usage_count: 0,
            created_at: datetime()
        })
        RETURN w.id as id
        """
        
        async with self.driver.session() as session:
            result = await session.run(
                query,
                id=workflow_id,
                name=name,
                trigger=trigger,
                steps=steps,
                success_rate=initial_success_rate
            )
            record = await result.single()
            logger.info(f"Created workflow pattern: {name} ({workflow_id})")
            return record["id"]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ENTITY & CONTEXT DISCOVERY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def find_entity(
        self,
        name: str,
        graph: Optional[str] = None
    ) -> Optional[GraphEntity]:
        """
        Find entity by name in knowledge graph
        
        Args:
            name: Entity name
            graph: Graph type (business, personal, technical, narrative) or None for all
            
        Returns:
            GraphEntity or None
        """
        if graph:
            query = """
            MATCH (e:Entity {name: $name, graph: $graph})
            RETURN e
            LIMIT 1
            """
            params = {"name": name, "graph": graph}
        else:
            query = """
            MATCH (e:Entity {name: $name})
            RETURN e
            LIMIT 1
            """
            params = {"name": name}
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            record = await result.single()
            
            if not record:
                return None
            
            e = record["e"]
            return GraphEntity(
                id=e["id"],
                name=e["name"],
                type=e.get("entity_type", "unknown"),
                graph=e.get("graph", "unknown"),
                properties=dict(e)
            )
    
    async def find_entity_context(
        self,
        entity_name: str,
        max_depth: int = 3,
        graph: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find all context around an entity (relationships, connected entities)
        
        Args:
            entity_name: Entity name
            max_depth: Maximum relationship depth to traverse
            graph: Graph type filter or None for all
            
        Returns:
            Dict with entities, relationships, and context
            
        Example:
            context = await kg.find_entity_context("Jacob", max_depth=3)
            # Returns: {
            #   "entity": GraphEntity(...),
            #   "related_entities": [GraphEntity(...), ...],
            #   "relationships": [GraphRelationship(...), ...],
            #   "projects": [...],
            #   "technologies": [...],
            #   "events": [...]
            # }
        """
        graph_filter = f"AND e.graph = '{graph}'" if graph else ""
        
        query = f"""
        MATCH (e:Entity {{name: $name}})
        {graph_filter}
        OPTIONAL MATCH (e)-[r*1..{max_depth}]-(related)
        RETURN e, collect(DISTINCT related) as related_entities, 
               collect(DISTINCT r) as relationships
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, name=entity_name)
            record = await result.single()
            
            if not record:
                return {"error": f"Entity '{entity_name}' not found"}
            
            e = record["e"]
            entity = GraphEntity(
                id=e["id"],
                name=e["name"],
                type=e.get("entity_type", "unknown"),
                graph=e.get("graph", "unknown"),
                properties=dict(e)
            )
            
            related = []
            for rel_node in record["related_entities"]:
                if rel_node:
                    related.append(GraphEntity(
                        id=rel_node["id"],
                        name=rel_node.get("name", "unknown"),
                        type=rel_node.get("entity_type", "unknown"),
                        graph=rel_node.get("graph", "unknown"),
                        properties=dict(rel_node)
                    ))
            
            return {
                "entity": entity,
                "related_entities": related,
                "total_connections": len(related),
                "graph": graph or "all"
            }
    
    async def find_shortest_path(
        self,
        from_entity: str,
        to_entity: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """
        Find shortest path between two entities
        
        Args:
            from_entity: Starting entity name
            to_entity: Target entity name
            max_depth: Maximum path length
            
        Returns:
            List of entity names in path or None
        """
        query = f"""
        MATCH (start:Entity {{name: $from}}), (end:Entity {{name: $to}})
        MATCH path = shortestPath((start)-[*..{max_depth}]-(end))
        RETURN [node in nodes(path) | node.name] as path
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, **{"from": from_entity, "to": to_entity})
            record = await result.single()
            
            if not record:
                return None
            
            return record["path"]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GRAPH QUERIES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def query_graph(
        self,
        graph: str,
        cypher_query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute custom Cypher query on specific graph
        
        Args:
            graph: Graph type (business, personal, technical, narrative)
            cypher_query: Cypher query string
            params: Query parameters
            
        Returns:
            List of result records
        """
        async with self.driver.session() as session:
            result = await session.run(cypher_query, **(params or {}))
            records = await result.data()
            return records
    
    async def find_patterns(
        self,
        pattern_type: str,
        graph: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find common patterns in knowledge graph
        
        Args:
            pattern_type: Type of pattern (e.g., "meeting_request", "project_update")
            graph: Graph type filter
            
        Returns:
            List of matching patterns
        """
        graph_filter = f"AND n.graph = '{graph}'" if graph else ""
        
        query = f"""
        MATCH (n)
        WHERE n.pattern_type = $pattern_type {graph_filter}
        RETURN n
        ORDER BY n.frequency DESC
        LIMIT 10
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, pattern_type=pattern_type)
            return await result.data()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RECOMMENDATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def recommend_next_actions(
        self,
        current_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Recommend next actions based on current context
        
        Args:
            current_context: Current situation context
            
        Returns:
            List of recommended actions with confidence scores
        """
        # Find similar past situations
        query = """
        MATCH (situation:Situation)-[:LED_TO]->(action:Action)
        WHERE situation.type = $situation_type
        RETURN action, COUNT(*) as frequency, AVG(action.success_rate) as avg_success
        ORDER BY frequency DESC, avg_success DESC
        LIMIT 5
        """
        
        async with self.driver.session() as session:
            result = await session.run(
                query,
                situation_type=current_context.get("type", "unknown")
            )
            return await result.data()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SINGLETON INSTANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_kg_instance: Optional[Neo4jKnowledgeGraph] = None


async def get_knowledge_graph() -> Neo4jKnowledgeGraph:
    """Get singleton knowledge graph instance"""
    global _kg_instance
    if _kg_instance is None:
        _kg_instance = Neo4jKnowledgeGraph()
        await _kg_instance.connect()
    return _kg_instance
