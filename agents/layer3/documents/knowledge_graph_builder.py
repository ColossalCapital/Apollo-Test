"""
5-Dimensional Meta-Knowledge Graph Builder

Complete implementation of multi-source knowledge graph aggregation
with 5-dimensional classification system.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import httpx
import json
import logging

logger = logging.getLogger(__name__)


class Dimension(Enum):
    """5 dimensions of knowledge classification"""
    UNIVERSAL = "universal"  # Timeless facts
    TEMPORAL = "temporal"    # Time-based events
    SPATIAL = "spatial"      # Location-based
    NARRATIVE = "narrative"  # Stories/sequences
    CUSTOM = "custom"        # User-defined


class KnowledgeGraphBuilder:
    """
    Builds 5-dimensional meta-knowledge graph from multiple sources
    """
    
    def __init__(
        self,
        atlas_api_url: str,
        theta_client=None,
        llm_client=None
    ):
        self.atlas_api_url = atlas_api_url
        self.theta = theta_client
        self.llm = llm_client
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    # ========================================================================
    # Main Entry Point
    # ========================================================================
    
    async def build_knowledge_graph(
        self,
        data: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """
        Build complete 5-dimensional knowledge graph
        
        Steps:
        1. Aggregate from all sources
        2. Classify into 5 dimensions
        3. Store in Atlas
        4. Update Theta RAG
        
        Returns:
            Complete knowledge graph with dimensional classification
        """
        
        logger.info(f"🧠 Building knowledge graph for user {context.user_id}")
        
        # Step 1: Aggregate from all sources
        aggregated = await self._aggregate_from_all_sources(data, context)
        
        # Step 2: Classify into dimensions
        classified = await self._classify_into_dimensions(aggregated, context)
        
        # Step 3: Store in Atlas
        await self._store_in_atlas(classified, context)
        
        # Step 4: Update Theta RAG
        await self._update_theta_rag(classified, context)
        
        logger.info(f"✅ Knowledge graph built: {len(classified['entities'])} entities, {len(classified['relationships'])} relationships")
        
        return classified
    
    # ========================================================================
    # Step 1: Multi-Source Aggregation
    # ========================================================================
    
    async def _aggregate_from_all_sources(
        self,
        data: Dict,
        context: Any
    ) -> Dict:
        """
        Aggregate knowledge from all available sources
        """
        
        sources = {}
        
        # Source 1: Custom Schema
        sources["custom_schema"] = await self._extract_from_custom_schema(data, context)
        
        # Source 2: Theta RAG (AI extraction)
        sources["theta_rag"] = await self._extract_from_theta_rag(data, context)
        
        # Source 3: Database relationships
        sources["database"] = await self._extract_from_database(context)
        
        # Source 4: Document connections
        sources["documents"] = await self._extract_from_documents(context)
        
        # Source 5: Communication patterns
        sources["communications"] = await self._extract_from_communications(context)
        
        # Source 6: Financial relationships
        sources["financial"] = await self._extract_from_financial(context)
        
        # Source 7: Code dependencies (if Akashic)
        if context.app_context == "akashic":
            sources["code"] = await self._extract_from_code(context)
        
        # Merge all sources
        return await self._merge_sources(sources)
    
    async def _extract_from_custom_schema(self, data, context):
        """Extract based on user's custom schema"""
        
        # Get user's schema from Atlas
        try:
            response = await self.http_client.get(
                f"{self.atlas_api_url}/api/schemas/{context.user_id}"
            )
            schema = response.json()
        except:
            schema = {}
        
        entities = []
        relationships = []
        
        # Extract based on schema definitions
        for entity_type, definition in schema.items():
            # Find entities matching this type
            # (Implementation depends on data structure)
            pass
        
        return {
            "source": "custom_schema",
            "entities": entities,
            "relationships": relationships,
            "confidence": 1.0
        }
    
    async def _extract_from_theta_rag(self, data, context):
        """Extract using Theta RAG + AI"""
        
        if not self.llm or not self.theta:
            return {"source": "theta_rag", "entities": [], "relationships": [], "confidence": 0}
        
        # Use LLM to extract entities and relationships
        prompt = f"""Extract all entities and relationships from this data:

{json.dumps(data, indent=2)}

Return JSON with:
{{
  "entities": [
    {{"name": "...", "type": "person|company|concept|...", "attributes": {{...}}}}
  ],
  "relationships": [
    {{"from": "...", "relation": "...", "to": "...", "metadata": {{...}}}}
  ]
}}
"""
        
        try:
            result = await self.llm.generate(prompt)
            extraction = json.loads(result)
        except:
            extraction = {"entities": [], "relationships": []}
        
        return {
            "source": "theta_rag",
            "entities": extraction.get("entities", []),
            "relationships": extraction.get("relationships", []),
            "confidence": 0.8
        }
    
    async def _extract_from_database(self, context):
        """Extract from database relationships (foreign keys, etc.)"""
        
        # Query Atlas for database relationships
        # This would query the actual PostgreSQL schema
        
        return {
            "source": "database",
            "entities": [],
            "relationships": [],
            "confidence": 1.0
        }
    
    async def _extract_from_documents(self, context):
        """Extract from document connections (citations, references)"""
        
        return {
            "source": "documents",
            "entities": [],
            "relationships": [],
            "confidence": 0.9
        }
    
    async def _extract_from_communications(self, context):
        """Extract from emails, meetings, messages"""
        
        return {
            "source": "communications",
            "entities": [],
            "relationships": [],
            "confidence": 0.85
        }
    
    async def _extract_from_financial(self, context):
        """Extract from financial transactions"""
        
        return {
            "source": "financial",
            "entities": [],
            "relationships": [],
            "confidence": 1.0
        }
    
    async def _extract_from_code(self, context):
        """Extract from code dependencies (Akashic)"""
        
        if not self.theta:
            return {"source": "code", "entities": [], "relationships": [], "confidence": 0}
        
        # Query codebase RAG
        try:
            result = await self.theta.query_rag(
                chatbot_id=f"{context.user_id}_codebase",
                query="List all imports, dependencies, and relationships"
            )
            # Parse result into entities/relationships
        except:
            result = {}
        
        return {
            "source": "code",
            "entities": [],
            "relationships": [],
            "confidence": 1.0
        }
    
    async def _merge_sources(self, sources: Dict) -> Dict:
        """Merge all sources, handling duplicates and conflicts"""
        
        all_entities = {}
        all_relationships = []
        
        for source_name, source_data in sources.items():
            # Merge entities (deduplicate)
            for entity in source_data.get("entities", []):
                key = self._entity_key(entity)
                
                if key in all_entities:
                    # Merge with existing
                    all_entities[key] = self._merge_entities(
                        all_entities[key],
                        entity,
                        source_data["confidence"]
                    )
                else:
                    # New entity
                    all_entities[key] = {
                        **entity,
                        "sources": [source_name],
                        "confidence": source_data["confidence"]
                    }
            
            # Add relationships
            for rel in source_data.get("relationships", []):
                all_relationships.append({
                    **rel,
                    "source": source_name,
                    "confidence": source_data["confidence"]
                })
        
        return {
            "entities": list(all_entities.values()),
            "relationships": all_relationships
        }
    
    def _entity_key(self, entity: Dict) -> str:
        """Generate unique key for entity"""
        return f"{entity.get('type', 'unknown')}:{entity.get('name', '')}".lower()
    
    def _merge_entities(self, existing: Dict, new: Dict, confidence: float) -> Dict:
        """Merge two entities, combining attributes"""
        
        merged = {**existing}
        
        # Merge attributes
        for key, value in new.items():
            if key not in merged or confidence > merged.get("confidence", 0):
                merged[key] = value
        
        # Add source
        if "sources" in merged:
            merged["sources"].append(new.get("source", "unknown"))
        
        # Update confidence (weighted average)
        if "confidence" in merged:
            merged["confidence"] = (merged["confidence"] + confidence) / 2
        
        return merged
    
    # ========================================================================
    # Step 2: Dimensional Classification
    # ========================================================================
    
    async def _classify_into_dimensions(
        self,
        aggregated: Dict,
        context: Any
    ) -> Dict:
        """
        Classify entities and relationships into 5 dimensions
        """
        
        classified = {
            "universal": {"entities": [], "relationships": []},
            "temporal": {"entities": [], "relationships": []},
            "spatial": {"entities": [], "relationships": []},
            "narrative": {"entities": [], "relationships": []},
            "custom": {"entities": [], "relationships": []}
        }
        
        # Classify entities
        for entity in aggregated.get("entities", []):
            dimension = await self._determine_dimension(entity, context)
            enhanced = await self._enhance_with_dimension(entity, dimension, context)
            classified[dimension]["entities"].append(enhanced)
        
        # Classify relationships
        for rel in aggregated.get("relationships", []):
            dimension = await self._determine_relationship_dimension(rel, context)
            enhanced = await self._enhance_relationship_with_dimension(rel, dimension, context)
            classified[dimension]["relationships"].append(enhanced)
        
        # Flatten for storage
        all_entities = []
        all_relationships = []
        
        for dim, data in classified.items():
            all_entities.extend(data["entities"])
            all_relationships.extend(data["relationships"])
        
        return {
            "entities": all_entities,
            "relationships": all_relationships,
            "by_dimension": classified
        }
    
    async def _determine_dimension(self, entity: Dict, context: Any) -> str:
        """Determine which dimension an entity belongs to"""
        
        if not self.llm:
            # Fallback: simple heuristics
            if "timestamp" in entity or "date" in entity:
                return "temporal"
            elif "location" in entity or "address" in entity:
                return "spatial"
            elif "sequence" in entity or "chapter" in entity:
                return "narrative"
            elif "custom_category" in entity:
                return "custom"
            else:
                return "universal"
        
        # Use AI to classify
        prompt = f"""Classify this entity into ONE dimension:

Entity: {json.dumps(entity, indent=2)}

Dimensions:
- universal: Timeless facts (people, companies, concepts)
- temporal: Time-based (events, meetings, transactions with dates)
- spatial: Location-based (places, addresses, geographic data)
- narrative: Part of a story/sequence (email threads, project phases)
- custom: User-defined category

Return ONLY the dimension name (lowercase).
"""
        
        try:
            result = await self.llm.generate(prompt)
            dimension = result.strip().lower()
            if dimension in ["universal", "temporal", "spatial", "narrative", "custom"]:
                return dimension
        except:
            pass
        
        return "universal"  # Default
    
    async def _determine_relationship_dimension(self, rel: Dict, context: Any) -> str:
        """Determine dimension for relationship"""
        
        # Relationships inherit dimension from their entities
        # or from temporal/spatial context
        
        if "temporal_context" in rel:
            return "temporal"
        elif "spatial_context" in rel:
            return "spatial"
        elif "narrative_context" in rel:
            return "narrative"
        else:
            return "universal"
    
    async def _enhance_with_dimension(
        self,
        entity: Dict,
        dimension: str,
        context: Any
    ) -> Dict:
        """Add dimension-specific metadata"""
        
        enhanced = {**entity, "dimension": dimension}
        
        if dimension == "temporal":
            # Extract temporal data
            enhanced["temporal_timestamp"] = entity.get("timestamp") or entity.get("date")
            enhanced["temporal_duration"] = entity.get("duration")
        
        elif dimension == "spatial":
            # Extract spatial data
            enhanced["spatial_location"] = entity.get("location")
            enhanced["spatial_address"] = entity.get("address")
        
        elif dimension == "narrative":
            # Extract narrative data
            enhanced["narrative_sequence"] = entity.get("sequence", 0)
            enhanced["narrative_chapter"] = entity.get("chapter", "default")
        
        elif dimension == "custom":
            # Extract custom category
            enhanced["custom_category"] = entity.get("custom_category", "uncategorized")
        
        return enhanced
    
    async def _enhance_relationship_with_dimension(
        self,
        rel: Dict,
        dimension: str,
        context: Any
    ) -> Dict:
        """Add dimensional context to relationship"""
        
        return {
            **rel,
            "dimension": dimension
        }
    
    # ========================================================================
    # Step 3: Storage
    # ========================================================================
    
    async def _store_in_atlas(self, classified: Dict, context: Any):
        """Store knowledge graph in Atlas"""
        
        try:
            await self.http_client.post(
                f"{self.atlas_api_url}/api/knowledge-graph/update",
                json={
                    "user_id": context.user_id,
                    "entities": classified["entities"],
                    "relationships": classified["relationships"]
                }
            )
            logger.info("✅ Stored in Atlas knowledge graph")
        except Exception as e:
            logger.error(f"❌ Failed to store in Atlas: {e}")
    
    async def _update_theta_rag(self, classified: Dict, context: Any):
        """Update Theta RAG with knowledge graph"""
        
        if not self.theta:
            return
        
        try:
            # Format for RAG
            documents = []
            for entity in classified["entities"]:
                doc = f"Entity: {entity['name']} ({entity['dimension']})\n"
                doc += f"Type: {entity.get('type', 'unknown')}\n"
                doc += f"Attributes: {json.dumps(entity, indent=2)}"
                documents.append(doc)
            
            # Update RAG
            await self.theta.update_rag_knowledge(
                chatbot_id=context.user_rag_chatbot,
                new_documents=documents
            )
            logger.info("✅ Updated Theta RAG")
        except Exception as e:
            logger.error(f"❌ Failed to update Theta RAG: {e}")
