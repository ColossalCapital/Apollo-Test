# 🧠 Atlas Knowledge Graph API Specification

**Complete API spec for 5-dimensional meta-knowledge graph**

---

## 📊 **Database Schema (PostgreSQL):**

```sql
-- Entities with 5-dimensional classification
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- person, company, concept, event, etc.
    
    -- 5-Dimensional Classification
    dimension TEXT NOT NULL CHECK (dimension IN ('universal', 'temporal', 'spatial', 'narrative', 'custom')),
    
    -- UNIVERSAL dimension
    universal_category TEXT,  -- person, company, concept
    
    -- TEMPORAL dimension
    temporal_timestamp TIMESTAMP,
    temporal_duration INTERVAL,
    temporal_end_time TIMESTAMP,
    
    -- SPATIAL dimension
    spatial_location GEOGRAPHY(POINT, 4326),  -- PostGIS
    spatial_address TEXT,
    spatial_radius_km FLOAT,
    
    -- NARRATIVE dimension
    narrative_sequence INT,
    narrative_chapter TEXT,
    narrative_thread_id UUID,
    
    -- CUSTOM dimension
    custom_category TEXT,
    custom_metadata JSONB,
    
    -- Multi-source tracking
    sources TEXT[],  -- ['custom_schema', 'theta_rag', 'database', ...]
    confidence FLOAT DEFAULT 0.8,
    
    -- General metadata
    attributes JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, name, type)
);

-- Relationships with dimensional context
CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    from_entity TEXT NOT NULL,
    from_entity_id UUID,
    relation TEXT NOT NULL,
    to_entity TEXT NOT NULL,
    to_entity_id UUID,
    
    -- Dimensional context
    dimension TEXT,
    temporal_context TIMESTAMP,
    spatial_context GEOGRAPHY(POINT, 4326),
    narrative_context TEXT,
    
    -- Multi-source tracking
    source TEXT,
    confidence FLOAT DEFAULT 0.8,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Custom schemas (user-defined)
CREATE TABLE custom_schemas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    schema_name TEXT NOT NULL,
    definition JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, schema_name)
);

-- Indices for fast queries
CREATE INDEX idx_entities_user ON entities(user_id);
CREATE INDEX idx_entities_dimension ON entities(dimension);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_temporal ON entities(temporal_timestamp) WHERE dimension = 'temporal';
CREATE INDEX idx_entities_spatial ON entities USING GIST(spatial_location) WHERE dimension = 'spatial';
CREATE INDEX idx_entities_narrative ON entities(narrative_sequence, narrative_chapter) WHERE dimension = 'narrative';
CREATE INDEX idx_entities_custom ON entities(custom_category) WHERE dimension = 'custom';

CREATE INDEX idx_relationships_user ON relationships(user_id);
CREATE INDEX idx_relationships_from ON relationships(from_entity);
CREATE INDEX idx_relationships_to ON relationships(to_entity);
CREATE INDEX idx_relationships_dimension ON relationships(dimension);
```

---

## 🔌 **API Endpoints:**

### **1. Update Knowledge Graph**

```rust
POST /api/knowledge-graph/update

Request:
{
  "user_id": "uuid",
  "entities": [
    {
      "name": "John Doe",
      "type": "person",
      "dimension": "universal",
      "universal_category": "person",
      "attributes": {
        "email": "john@acme.com",
        "title": "CEO"
      },
      "sources": ["custom_schema", "theta_rag"],
      "confidence": 0.95
    },
    {
      "name": "Q3 Product Launch",
      "type": "event",
      "dimension": "temporal",
      "temporal_timestamp": "2024-09-15T00:00:00Z",
      "temporal_duration": "3 months",
      "narrative_chapter": "product_launch",
      "narrative_sequence": 1,
      "sources": ["theta_rag", "documents"],
      "confidence": 0.9
    }
  ],
  "relationships": [
    {
      "from_entity": "John Doe",
      "relation": "leads",
      "to_entity": "Q3 Product Launch",
      "dimension": "narrative",
      "narrative_context": "product_launch",
      "source": "theta_rag",
      "confidence": 0.85
    }
  ]
}

Response:
{
  "success": true,
  "entities_created": 2,
  "relationships_created": 1,
  "entities_updated": 0
}
```

---

### **2. Query by Dimension**

```rust
POST /api/knowledge-graph/query

Request:
{
  "user_id": "uuid",
  "dimension": "temporal",  // or "universal", "spatial", "narrative", "custom"
  "filters": {
    // For temporal:
    "start_time": "2024-07-01T00:00:00Z",
    "end_time": "2024-09-30T23:59:59Z",
    
    // For spatial:
    "location": {"lat": 37.7749, "lng": -122.4194},
    "radius_km": 10,
    
    // For narrative:
    "chapter": "product_launch",
    
    // For custom:
    "category": "VIP_clients"
  },
  "limit": 100
}

Response:
{
  "dimension": "temporal",
  "entities": [
    {
      "name": "Q3 Product Launch",
      "type": "event",
      "temporal_timestamp": "2024-09-15T00:00:00Z",
      "relationships": [
        {"relation": "led_by", "entity": "John Doe"}
      ]
    }
  ],
  "count": 1
}
```

---

### **3. Cross-Dimensional Query**

```rust
POST /api/knowledge-graph/query/cross-dimensional

Request:
{
  "user_id": "uuid",
  "query": "Who met in San Francisco during Q3 as part of the product launch?",
  "dimensions": {
    "universal": {"entity_types": ["person"]},
    "temporal": {"start": "2024-07-01", "end": "2024-09-30"},
    "spatial": {"location": "San Francisco", "radius_km": 10},
    "narrative": {"chapter": "product_launch"}
  }
}

Response:
{
  "query": "Who met in San Francisco during Q3 as part of the product launch?",
  "results": {
    "people": ["John Doe", "Jane Smith"],
    "events": [
      {
        "name": "Product Launch Kickoff",
        "date": "2024-08-15",
        "location": "San Francisco",
        "attendees": ["John Doe", "Jane Smith"]
      }
    ]
  }
}
```

---

### **4. Get Custom Schema**

```rust
GET /api/schemas/{user_id}

Response:
{
  "schemas": [
    {
      "schema_name": "business_entities",
      "definition": {
        "Person": {
          "fields": ["name", "email", "title", "company"],
          "relationships": ["works_at", "reports_to", "knows"]
        },
        "Company": {
          "fields": ["name", "industry", "size", "location"],
          "relationships": ["owns", "partners_with", "competes_with"]
        }
      }
    }
  ]
}
```

---

### **5. Create/Update Custom Schema**

```rust
POST /api/schemas

Request:
{
  "user_id": "uuid",
  "schema_name": "business_entities",
  "definition": {
    "Person": {
      "fields": ["name", "email", "title"],
      "relationships": ["works_at", "knows"]
    }
  }
}

Response:
{
  "success": true,
  "schema_id": "uuid"
}
```

---

### **6. Graph Visualization Data**

```rust
GET /api/knowledge-graph/visualize/{user_id}?dimension=all&limit=100

Response:
{
  "nodes": [
    {
      "id": "uuid",
      "name": "John Doe",
      "type": "person",
      "dimension": "universal",
      "color": "#3498db"  // Color by dimension
    },
    {
      "id": "uuid",
      "name": "Q3 Product Launch",
      "type": "event",
      "dimension": "temporal",
      "color": "#e74c3c"
    }
  ],
  "edges": [
    {
      "from": "uuid",
      "to": "uuid",
      "relation": "leads",
      "dimension": "narrative"
    }
  ]
}
```

---

## 🎨 **Dimension Colors (for UI):**

```
universal: #3498db (blue)
temporal: #e74c3c (red)
spatial: #2ecc71 (green)
narrative: #9b59b6 (purple)
custom: #f39c12 (orange)
```

---

## 📝 **Example Rust Implementation:**

```rust
// Atlas/backend/src/knowledge_graph/mod.rs

use actix_web::{post, get, web, HttpResponse, Result};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use uuid::Uuid;

#[derive(Deserialize)]
pub struct KnowledgeGraphUpdate {
    user_id: Uuid,
    entities: Vec<Entity>,
    relationships: Vec<Relationship>,
}

#[derive(Deserialize, Serialize)]
pub struct Entity {
    name: String,
    r#type: String,
    dimension: String,
    
    // Dimension-specific fields
    universal_category: Option<String>,
    temporal_timestamp: Option<chrono::DateTime<chrono::Utc>>,
    temporal_duration: Option<String>,
    spatial_location: Option<(f64, f64)>,  // (lat, lng)
    spatial_address: Option<String>,
    narrative_sequence: Option<i32>,
    narrative_chapter: Option<String>,
    custom_category: Option<String>,
    
    // Metadata
    attributes: Option<serde_json::Value>,
    sources: Vec<String>,
    confidence: f32,
}

#[post("/api/knowledge-graph/update")]
pub async fn update_knowledge_graph(
    pool: web::Data<PgPool>,
    data: web::Json<KnowledgeGraphUpdate>,
) -> Result<HttpResponse> {
    
    let mut entities_created = 0;
    let mut entities_updated = 0;
    
    // Insert/update entities
    for entity in &data.entities {
        let result = sqlx::query!(
            r#"
            INSERT INTO entities (
                user_id, name, type, dimension,
                universal_category, temporal_timestamp, temporal_duration,
                spatial_location, spatial_address,
                narrative_sequence, narrative_chapter,
                custom_category, attributes, sources, confidence
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, 
                    ST_SetSRID(ST_MakePoint($8, $9), 4326), $10,
                    $11, $12, $13, $14, $15, $16)
            ON CONFLICT (user_id, name, type) 
            DO UPDATE SET
                dimension = EXCLUDED.dimension,
                attributes = EXCLUDED.attributes,
                sources = EXCLUDED.sources,
                confidence = EXCLUDED.confidence,
                updated_at = NOW()
            RETURNING id
            "#,
            data.user_id,
            entity.name,
            entity.r#type,
            entity.dimension,
            entity.universal_category,
            entity.temporal_timestamp,
            entity.temporal_duration,
            entity.spatial_location.map(|(lat, _)| lat),
            entity.spatial_location.map(|(_, lng)| lng),
            entity.spatial_address,
            entity.narrative_sequence,
            entity.narrative_chapter,
            entity.custom_category,
            entity.attributes,
            &entity.sources,
            entity.confidence
        )
        .fetch_one(pool.get_ref())
        .await;
        
        match result {
            Ok(_) => entities_created += 1,
            Err(_) => entities_updated += 1,
        }
    }
    
    // Insert relationships
    let mut relationships_created = 0;
    for rel in &data.relationships {
        sqlx::query!(
            r#"
            INSERT INTO relationships (
                user_id, from_entity, relation, to_entity,
                dimension, source, confidence, metadata
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            "#,
            data.user_id,
            rel.from_entity,
            rel.relation,
            rel.to_entity,
            rel.dimension,
            rel.source,
            rel.confidence,
            rel.metadata
        )
        .execute(pool.get_ref())
        .await?;
        
        relationships_created += 1;
    }
    
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "success": true,
        "entities_created": entities_created,
        "entities_updated": entities_updated,
        "relationships_created": relationships_created
    })))
}
```

---

## ✅ **Implementation Checklist:**

### **Atlas Backend:**
- [ ] Create PostgreSQL schema (entities, relationships, custom_schemas)
- [ ] Implement `/api/knowledge-graph/update` endpoint
- [ ] Implement `/api/knowledge-graph/query` endpoint
- [ ] Implement `/api/knowledge-graph/query/cross-dimensional` endpoint
- [ ] Implement `/api/schemas` endpoints
- [ ] Implement `/api/knowledge-graph/visualize` endpoint

### **Apollo:**
- [x] Create `KnowledgeGraphBuilder` class
- [x] Implement multi-source aggregation
- [x] Implement 5-dimensional classification
- [x] Integrate with Theta RAG
- [ ] Add to KnowledgeAgent

### **Frontend:**
- [ ] Knowledge graph visualization component
- [ ] Dimensional filters UI
- [ ] Custom schema editor
- [ ] Cross-dimensional query builder

---

**Created:** October 27, 2025  
**Status:** READY FOR IMPLEMENTATION ✅
