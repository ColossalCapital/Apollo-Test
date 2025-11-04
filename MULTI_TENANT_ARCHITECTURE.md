# 🏢 Apollo Multi-Tenant Architecture

## **Overview**

Apollo supports multi-tenancy with separate instances for:
- **Personal** (individual users)
- **Business Entities** (companies, LLCs, C-Corps)

Each tenant gets:
- ✅ Isolated fine-tuned models
- ✅ Separate training data
- ✅ Independent model versions
- ✅ Privacy-preserving architecture

---

## **Architecture**

### **Shared Layer (Apollo Master)**
```
Apollo Master
├── Base Models (Filecoin)
│   ├── DeepSeek-6.7B (code)
│   ├── Mistral-7B (email, web)
│   ├── Phi-3-medium (documents)
│   ├── Phi-3-mini (calendar)
│   ├── Florence-2 (vision)
│   ├── Whisper (audio)
│   ├── BGE-large (embeddings)
│   └── MiniLM (text)
│
├── Agent Framework
│   ├── 45 agent implementations
│   ├── Meta-Orchestrator
│   ├── Workflow Engine
│   └── Base agent classes
│
└── Infrastructure
    ├── API (FastAPI)
    ├── Model Manager
    ├── Filecoin Client
    └── Theta Integration
```

### **Tenant Layer (Per User/Entity)**
```
Apollo Tenant (user_123 / entity_456)
├── Fine-tuned Models (Filecoin)
│   ├── email_agent_v2.gguf
│   ├── code_assistant_v3.gguf
│   ├── document_parser_v1.gguf
│   └── calendar_agent_v1.gguf
│
├── Training Data (Filecoin)
│   ├── email_patterns.jsonl
│   ├── code_patterns.jsonl
│   ├── document_templates.jsonl
│   └── calendar_preferences.json
│
├── Model Registry
│   ├── Model versions
│   ├── Training history
│   └── Performance metrics
│
└── Context
    ├── User/Entity ID
    ├── Permissions
    └── Data access rules
```

---

## **Tenant Types**

### **1. Personal Tenant**
```
User: john@example.com
Tenant ID: user_123

Models:
- Email agent (personal email style)
- Calendar agent (personal scheduling)
- Code assistant (personal coding patterns)
- Document parser (personal docs)

Data Sources:
- Personal Gmail
- Personal Google Calendar
- Personal GitHub repos
- Personal documents

Privacy: Maximum (only user can access)
```

### **2. Business Entity Tenant**
```
Entity: ACME Corp (C-Corp)
Tenant ID: entity_456
Members: [john@acme.com, jane@acme.com, bob@acme.com]

Models:
- Legal agent (ACME's contracts)
- Compliance agent (C-Corp requirements)
- Tax agent (corporate tax patterns)
- Invoice agent (ACME's invoicing style)

Data Sources:
- Corporate Gmail
- Corporate calendar
- Corporate GitHub
- Corporate documents
- Corporate financials

Privacy: Shared (all members can access)
```

### **3. Multi-Entity User**
```
User: john@example.com

Personal:
- Tenant ID: user_123
- Personal models
- Personal data

Business 1 (ACME Corp):
- Tenant ID: entity_456
- Role: CEO
- Access: Full

Business 2 (XYZ LLC):
- Tenant ID: entity_789
- Role: Advisor
- Access: Limited

Apollo switches context based on:
- Which app (Atlas personal vs Atlas business)
- Which entity is selected
- User's role in entity
```

---

## **API Design**

### **Tenant Context**
```python
# Every API call includes tenant context
POST /query
{
  "query": "Analyze my Q4 finances",
  "user_id": "user_123",
  "entity_id": "entity_456",  # Optional
  "context": {
    "tenant_type": "business",
    "role": "ceo",
    "permissions": ["read", "write", "admin"]
  }
}
```

### **Model Loading**
```python
# Apollo loads appropriate models based on tenant
async def load_model(agent_name: str, tenant_context: TenantContext):
    # Check for fine-tuned model
    fine_tuned_path = await filecoin.download_fine_tuned_model(
        user_id=tenant_context.user_id,
        entity_id=tenant_context.entity_id,
        model_name=agent_name
    )
    
    if fine_tuned_path:
        # Use tenant's fine-tuned model
        return load_gguf(fine_tuned_path)
    else:
        # Fall back to base model
        return load_base_model(agent_name)
```

### **Data Isolation**
```python
# Training data is isolated per tenant
async def get_training_data(tenant_context: TenantContext):
    if tenant_context.entity_id:
        # Business entity data
        return await filecoin.download_training_data(
            entity_id=tenant_context.entity_id,
            data_type="email_patterns"
        )
    else:
        # Personal data
        return await filecoin.download_training_data(
            user_id=tenant_context.user_id,
            data_type="email_patterns"
        )
```

---

## **Integration with Apps**

### **Atlas (Personal)**
```typescript
// Atlas personal mode
const apolloService = new ApolloService({
  url: 'http://localhost:8002',
  tenantContext: {
    userId: 'user_123',
    entityId: null,  // Personal mode
    tenantType: 'personal'
  }
});

// Uses personal fine-tuned models
await apolloService.analyzeEmail(email);
```

### **Atlas (Business)**
```typescript
// Atlas business mode
const apolloService = new ApolloService({
  url: 'http://localhost:8002',
  tenantContext: {
    userId: 'user_123',
    entityId: 'entity_456',  // ACME Corp
    tenantType: 'business',
    role: 'ceo'
  }
});

// Uses ACME Corp's fine-tuned models
await apolloService.analyzeContract(contract);
```

### **Delt (Trading)**
```dart
// Delt uses trading-specific models
final apolloService = ApolloService(
  url: 'http://localhost:8002',
  tenantContext: TenantContext(
    userId: 'user_123',
    entityId: 'entity_456',  // Trading entity
    tenantType: 'trading',
  ),
);

// Uses trading-specific fine-tuned models
await apolloService.analyzeMarket(marketData);
```

### **Akashic (Code Editor)**
```typescript
// Akashic uses code-specific models
const apolloService = new ApolloCodeService({
  url: 'http://localhost:8002',
  tenantContext: {
    userId: 'user_123',
    entityId: null,  // Personal coding
    tenantType: 'development'
  }
});

// Uses personal code patterns
await apolloService.generateCode(prompt, context);
```

---

## **Deployment**

### **Single Apollo Instance (Recommended)**
```
Apollo (Port 8002)
├── Handles all tenants
├── Loads models dynamically
├── Isolates data per tenant
└── Scales horizontally

Benefits:
✅ Simpler deployment
✅ Shared base models
✅ Efficient resource usage
✅ Easy to scale
```

### **Multiple Apollo Instances (Optional)**
```
Apollo Personal (Port 8002)
├── Only personal tenants
└── Optimized for personal use

Apollo Business (Port 8003)
├── Only business tenants
└── Optimized for business use

Apollo Trading (Port 8004)
├── Only trading tenants
└── Optimized for trading

Benefits:
✅ Complete isolation
✅ Specialized optimization
✅ Independent scaling

Drawbacks:
❌ More complex deployment
❌ Duplicate base models
❌ Higher resource usage
```

**Recommendation: Start with single instance, split later if needed**

---

## **Privacy & Security**

### **Data Isolation**
```
✅ Each tenant's data stored separately on Filecoin
✅ Encrypted with tenant-specific keys
✅ No cross-tenant data access
✅ Audit logs per tenant
```

### **Model Isolation**
```
✅ Fine-tuned models stored per tenant
✅ Training data never shared
✅ Model versions tracked per tenant
✅ No model contamination
```

### **Access Control**
```
✅ Role-based access (owner, admin, member, viewer)
✅ Permission checks on every API call
✅ Entity membership verified
✅ User can revoke access anytime
```

---

## **Cost Model**

### **Per-Tenant Costs**
```
Personal Tenant:
- Training data: ~500 MB → $0.002/month (Filecoin)
- Fine-tuned models: ~2 GB → $0.008/month (Filecoin)
- Training: ~10 hours/year → $1/year (Theta)
Total: ~$0.12/year per personal user

Business Tenant:
- Training data: ~5 GB → $0.02/month (Filecoin)
- Fine-tuned models: ~10 GB → $0.04/month (Filecoin)
- Training: ~100 hours/year → $10/year (Theta)
Total: ~$10.72/year per business entity

Shared Infrastructure:
- Base models: ~17 GB → $0.07/month (Filecoin)
- Apollo API: $50/month (server)
Total: ~$50.84/month for entire platform

1000 users + 100 businesses:
- Personal: 1000 × $0.12/year = $120/year
- Business: 100 × $10.72/year = $1,072/year
- Shared: $50.84/month × 12 = $610/year
Total: $1,802/year

vs AWS (same scale):
- Storage: $3,450/month × 12 = $41,400/year
- Training: $500/month × 12 = $6,000/year
Total: $47,400/year

Savings: 96% cheaper! 🎉
```

---

## **Summary**

**Apollo Multi-Tenant Architecture:**
- ✅ Single Apollo instance serves all tenants
- ✅ Dynamic model loading per tenant
- ✅ Complete data isolation (Filecoin)
- ✅ Fine-tuned models per tenant
- ✅ Works with Atlas, Delt, Akashic
- ✅ 96% cheaper than AWS
- ✅ User-owned AI models

**Each tenant gets their own AI, trained on their data, stored on their Filecoin!** 🚀
