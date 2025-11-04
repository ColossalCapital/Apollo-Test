# 🔄 Apollo Integration Flow - Complete Guide

**How services call Apollo and what happens**

---

## 📊 **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER APPLICATIONS                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  Atlas   │    │   Delt   │    │ Akashic  │             │
│  │ (Data)   │    │(Trading) │    │  (Code)  │             │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘             │
└───────┼───────────────┼───────────────┼────────────────────┘
        │               │               │
        │ HTTP API      │ HTTP API      │ HTTP API
        │               │               │
        └───────────────┴───────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              APOLLO AI SYSTEM (Port 8002)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Server (main.py)                 │  │
│  │  • /v3/analyze  - Multi-tenant analysis              │  │
│  │  • /v3/query    - Natural language queries           │  │
│  │  • /v3/train    - Submit training jobs               │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│                       ↓                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Smart Router (smart_router.py)                │  │
│  │  1. Parse context                                     │  │
│  │  2. Determine model path                              │  │
│  │  3. Build AgentContext                                │  │
│  │  4. Route to agent                                    │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│         ┌─────────────┴─────────────┐                       │
│         ↓                           ↓                       │
│  ┌─────────────┐            ┌──────────────────┐           │
│  │ 62 Agents   │            │ Meta-Orchestrator│           │
│  │ (Tier 2 LLM)│            │  (Agentic AI)    │           │
│  └─────────────┘            └──────────────────┘           │
│         │                           │                       │
│         ↓                           ↓                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Continuous Learner                            │  │
│  │  • Log interactions                                   │  │
│  │  • Trigger training (100 interactions)                │  │
│  │  • Deploy personalized models                         │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│         ┌─────────────┴─────────────┐                       │
│         ↓                           ↓                       │
│  ┌──────────────┐           ┌──────────────┐               │
│  │ Unified GPU  │           │ Unified      │               │
│  │ Trainer      │           │ Storage      │               │
│  │ (Theta +     │           │ (Filecoin +  │               │
│  │  JarvisLabs) │           │  Multi)      │               │
│  └──────────────┘           └──────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 **Complete Request Flow**

### **Step 1: Service Makes API Call**

```python
# Example: Atlas analyzing an email
response = await apollo_client.post(
    "http://apollo:8002/v3/analyze",
    json={
        "user_id": "user123",
        "org_id": "company456",
        "team_id": "engineering",
        "app_context": "atlas",
        "atlas_tier": "enterprise",
        "privacy": "org_private",
        "agent_type": "email",
        "process_name": "inbox_analysis",
        "data": {
            "sender": "boss@company.com",
            "subject": "Urgent: Q4 Report",
            "body": "..."
        }
    }
)
```

---

### **Step 2: Smart Router Parses Context**

```python
# Smart Router extracts context
context = RequestContext(
    user_id="user123",
    org_id="company456",
    team_id="engineering",
    app_context="atlas",
    atlas_tier="enterprise",
    privacy="org_private"
)

# Router determines model configuration
model_config = ModelIsolationStrategy.get_model_path(
    user_id="user123",
    org_id="company456",
    atlas_tier=AtlasTier.ENTERPRISE,
    privacy_schema=PrivacySchema.ORG_PRIVATE,
    app_context=AppContext.ATLAS,
    agent_type="email"
)

# Result:
{
    "model_type": "team_finetuned",
    "model_path": "filecoin://atlas/team/company456/engineering/email",
    "isolation_level": "team",
    "can_share": True,
    "can_train": True
}
```

---

### **Step 3: Router Builds AgentContext**

```python
# Router creates context for agent
agent_context = AgentContext(
    app_context="atlas",
    user_id="user123",
    org_id="company456",
    team_id="engineering",
    atlas_tier="enterprise",
    privacy="org_private",
    isolation_level="team",
    can_share=True,
    can_train=True,
    model_path="filecoin://atlas/team/company456/engineering/email",
    storage_path="atlas/team/company456/engineering/email/",
    conflict_resolution="last_write_wins"
)
```

**Key Insight:** This context tells the agent:
- ✅ Which trained model to use
- ✅ Where to store training data
- ✅ What tier user is on
- ✅ What can be shared
- ✅ How to handle conflicts

---

### **Step 4: Agent Receives Context & Analyzes**

```python
# Email Agent receives context
class EmailAgent(BaseAgent):
    async def analyze(self, data, context: AgentContext = None):
        # Agent knows everything about the request
        logger.info(f"Using model: {context.model_path}")
        logger.info(f"Isolation: {context.isolation_level}")
        logger.info(f"Can share: {context.can_share}")
        
        # Use trained model if available
        if context and context.model_path:
            # Load team's trained model from Filecoin
            result = await self.query_llm(
                prompt=self._build_prompt(data),
                agent_context=context
            )
        else:
            # Use base model
            result = await self.query_llm(
                prompt=self._build_prompt(data)
            )
        
        # Give tier-appropriate recommendations
        if context.atlas_tier == "enterprise":
            result["suggestions"].append("Share with team")
            result["compliance"] = self._check_compliance(data)
        
        return result
```

---

### **Step 5: Agent Returns Intelligence**

```python
# Agent returns analysis
{
    "urgency": "high",
    "category": "work",
    "sentiment": "urgent_request",
    "summary": "Your boss needs Q4 report by EOD",
    "suggested_action": "reply_within_2_hours",
    "suggested_response": "I'll have the Q4 report ready by 3pm...",
    "compliance": {
        "gdpr": "compliant",
        "sox": "requires_review"
    },
    "suggestions": [
        "Reply within 2 hours",
        "Share with team",
        "Escalate to finance"
    ],
    "model_used": "team_trained",
    "confidence": 0.92
}
```

---

### **Step 6: Continuous Learner Logs Interaction**

```python
# If log_interaction=True, learner stores data
await continuous_learner.log_interaction(
    user_id="user123",
    org_id="company456",
    team_id="engineering",
    app_context=AppContext.ATLAS,
    agent_type="email",
    query=data,
    response=result,
    privacy=PrivacySchema.ORG_PRIVATE
)

# Stored at: atlas/team/company456/engineering/email/
# Filename: interaction_20241027_110000.json
```

---

### **Step 7: Training Triggered (After 100 Interactions)**

```python
# When buffer reaches 100 interactions
if len(interaction_buffer) >= 100:
    # Submit training job
    job = await unified_trainer.submit_training(
        model_id="atlas/team/company456/engineering/email",
        training_data_path="atlas/team/company456/engineering/email/",
        base_model="mistral-7b-instruct-v0.2",
        hyperparameters={
            "epochs": 3,
            "learning_rate": 2e-5,
            "batch_size": 4
        }
    )
    
    # Training happens on Theta GPU or JarvisLabs
    # Takes ~2 hours, costs ~$1
    
    # New model deployed to Filecoin
    # Next API call uses trained model automatically
```

---

## 🎯 **Context-Aware Model Selection**

### **Personal Tier User:**
```
Request → Smart Router → Determines:
  model_path: "filecoin://atlas/personal/user123/email"
  storage_path: "atlas/personal/user123/email/"
  isolation: "personal"
  can_share: False

Agent → Uses personal trained model
      → Stores data in personal location
      → Gives personal recommendations
```

### **Team Tier User:**
```
Request → Smart Router → Determines:
  model_path: "filecoin://atlas/team/company456/engineering/email"
  storage_path: "atlas/team/company456/engineering/email/"
  isolation: "team"
  can_share: True

Agent → Uses team trained model
      → Stores data in team location
      → Gives team collaboration suggestions
```

### **Enterprise Tier User:**
```
Request → Smart Router → Determines:
  model_path: "filecoin://atlas/org/company456/email"
  storage_path: "atlas/org/company456/email/"
  isolation: "org"
  can_share: True

Agent → Uses org trained model
      → Stores data in org location
      → Gives enterprise recommendations (compliance, policies)
```

---

## 📊 **Storage & Training Paths**

### **Personal User:**
```
Training Data: filecoin://atlas/personal/user123/email/
  ├── interaction_001.json
  ├── interaction_002.json
  └── ...

Trained Model: filecoin://atlas/personal/user123/email/model_v1.gguf
```

### **Team User:**
```
Training Data: filecoin://atlas/team/company456/engineering/email/
  ├── interaction_001.json (from user1)
  ├── interaction_002.json (from user2)
  └── ...

Trained Model: filecoin://atlas/team/company456/engineering/email/model_v1.gguf
```

### **Enterprise User:**
```
Training Data: filecoin://atlas/org/company456/email/
  ├── interaction_001.json (from any user in org)
  ├── interaction_002.json
  └── ...

Trained Model: filecoin://atlas/org/company456/email/model_v1.gguf
```

---

## 🚀 **Real-World Example: Email Analysis**

### **1. Atlas Fetches Email**
```python
email = gmail_client.fetch_email(email_id="msg_123")
```

### **2. Atlas Calls Apollo**
```python
response = await apollo_client.analyze(
    user_id="user123",
    org_id="company456",
    app_context="atlas",
    atlas_tier="enterprise",
    privacy="org_private",
    agent_type="email",
    data=email
)
```

### **3. Apollo Routes to Email Agent**
- Smart Router determines: Use team model
- Builds AgentContext with model path
- Passes to Email Agent

### **4. Email Agent Analyzes**
- Loads team's trained model from Filecoin
- Analyzes email with team's patterns
- Returns enterprise-level recommendations

### **5. Atlas Receives Intelligence**
```python
{
    "urgency": "high",
    "category": "work",
    "summary": "Boss needs Q4 report",
    "suggested_response": "...",
    "model_used": "team_trained"
}
```

### **6. Atlas Stores Enriched Email**
```python
email.urgency = response.urgency
email.category = response.category
email.ai_summary = response.summary
atlas.store_email(email)
```

### **7. User Sees Smart Inbox**
- Emails sorted by urgency
- AI summaries for quick scanning
- One-click suggested responses
- Team patterns applied

---

## 💡 **Key Benefits of This Architecture**

### **1. Automatic Model Selection**
- Service doesn't need to know which model to use
- Apollo figures it out from context
- Right model for right user/team/org

### **2. Correct Storage Locations**
- Training data stored in right place automatically
- No manual path management
- Privacy boundaries enforced

### **3. Tier-Appropriate Features**
- Free tier: Basic analysis
- Personal tier: Personal recommendations
- Team tier: Team collaboration
- Enterprise tier: Compliance, policies

### **4. Continuous Learning**
- Models improve automatically
- No manual training triggers
- Privacy-isolated training

### **5. Scalable**
- Add new tiers easily
- Add new contexts easily
- Add new agents easily

---

## 📚 **API Documentation**

Full API docs available at:
- **Swagger UI:** http://apollo:8002/docs
- **ReDoc:** http://apollo:8002/redoc

---

**Created:** October 27, 2025  
**Version:** 3.1.0  
**Status:** COMPLETE
