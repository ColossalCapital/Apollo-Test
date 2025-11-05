# 🧠 Context-Aware Agents - COMPLETE IMPLEMENTATION

**Agents now understand their context and adapt accordingly**

---

## ✅ **What We Just Built:**

### **1. Correct Atlas Tiers**
```python
class AtlasTier(Enum):
    FREE = "free"                  # $0/mo - Try before buy
    PERSONAL = "personal"          # $29/mo - 1 entity
    INDIVIDUAL = "individual"      # Individual with sharing
    TEAM = "team"                  # $99/mo - 5 entities
    ENTERPRISE = "enterprise"      # Custom - Unlimited
```

### **2. Privacy-Controlled Akashic Isolation**
- ❌ OLD: ALWAYS personal (no sharing)
- ✅ NEW: User chooses via privacy settings
- Free/Personal tier → Always personal
- Individual/Team/Enterprise → Can share if privacy allows

### **3. Context-Aware Agents**
```python
class AgentContext:
    """Full context passed to every agent"""
    app_context: str          # atlas, delt, akashic, etc.
    user_id: str
    org_id: Optional[str]
    team_id: Optional[str]
    atlas_tier: Optional[str]
    delt_tier: Optional[str]
    privacy: str
    isolation_level: str      # personal, team, org, public
    can_share: bool
    can_train: bool
    model_path: Optional[str]  # Where trained model is stored
    storage_path: Optional[str]  # Where to save training data
    parent_context: Optional[str]
    conflict_resolution: str
```

### **4. Smart Model Routing**
The API now uses context to:
- ✅ Find the right trained model (personal/team/org)
- ✅ Store training data in correct location
- ✅ Give tier-appropriate recommendations
- ✅ Respect privacy boundaries

---

## 🎯 **How It Works:**

### **Step 1: API Receives Request**
```json
{
  "user_id": "user123",
  "org_id": "company456",
  "team_id": "engineering",
  "app_context": "atlas",
  "atlas_tier": "enterprise",
  "privacy": "org_private",
  "agent_type": "email",
  "data": {...}
}
```

### **Step 2: Smart Router Determines Context**
```python
# Router analyzes request and determines:
model_config = {
    "isolation_level": "team",
    "can_share": True,
    "can_train": True,
    "model_path": "filecoin://atlas/team/company456/engineering/email",
    "storage_path": "atlas/team/company456/engineering/email/",
    "conflict_resolution": "last_write_wins"
}
```

### **Step 3: Router Builds AgentContext**
```python
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
    parent_context=None,
    conflict_resolution="last_write_wins"
}
```

### **Step 4: Agent Receives Context**
```python
class EmailAgent(BaseAgent):
    async def analyze(self, data, context: AgentContext = None):
        # Agent now knows:
        # - Which model to use (context.model_path)
        # - Where to store data (context.storage_path)
        # - What tier user is on (context.atlas_tier)
        # - What can be shared (context.can_share)
        
        if context and context.model_path:
            # Use trained model
            result = await self.query_llm(
                prompt=self._build_prompt(data),
                agent_context=context  # Pass context to LLM
            )
        else:
            # Use base model
            result = await self.query_llm(
                prompt=self._build_prompt(data)
            )
        
        # Give tier-appropriate recommendations
        if context and context.atlas_tier == "enterprise":
            result["suggestions"].append("Share with team via org_private")
        elif context and context.atlas_tier == "personal":
            result["suggestions"].append("Upgrade to Team for collaboration")
        
        return result
```

---

## 📊 **Context-Aware Benefits:**

### **1. Smart Model Selection**
```python
# Personal tier user
context.model_path = "filecoin://atlas/personal/user123/email"
# → Uses personal trained model

# Team tier user (team privacy)
context.model_path = "filecoin://atlas/team/company456/engineering/email"
# → Uses team trained model

# Enterprise tier user (org privacy)
context.model_path = "filecoin://atlas/org/company456/email"
# → Uses org trained model
```

### **2. Correct Storage Locations**
```python
# Personal tier
context.storage_path = "atlas/personal/user123/email/"
# → Training data stored privately

# Team tier
context.storage_path = "atlas/team/company456/engineering/email/"
# → Training data shared with team

# Enterprise tier
context.storage_path = "atlas/org/company456/email/"
# → Training data shared with org
```

### **3. Tier-Appropriate Recommendations**

**Free Tier:**
```python
{
  "urgency": "high",
  "category": "work",
  "suggestions": [
    "Upgrade to Personal tier for AI learning",
    "Get custom recommendations with paid plan"
  ]
}
```

**Personal Tier:**
```python
{
  "urgency": "high",
  "category": "work",
  "suggestions": [
    "Reply within 2 hours",
    "Upgrade to Team for collaboration features"
  ]
}
```

**Team Tier:**
```python
{
  "urgency": "high",
  "category": "work",
  "suggestions": [
    "Reply within 2 hours",
    "Forward to @john (team member)",
    "Share with engineering team"
  ]
}
```

**Enterprise Tier:**
```python
{
  "urgency": "high",
  "category": "work",
  "compliance": "GDPR compliant",
  "suggestions": [
    "Reply within 2 hours",
    "Forward to @john (team member)",
    "Escalate to legal department",
    "Company policy: Requires approval"
  ]
}
```

### **4. Privacy-Aware Responses**

**Personal Privacy:**
```python
{
  "can_share": False,
  "recommendations": [
    "Keep this email private",
    "Don't forward to team"
  ]
}
```

**Org Private:**
```python
{
  "can_share": True,
  "recommendations": [
    "Share with engineering team",
    "Collaborate on response"
  ]
}
```

---

## 🔄 **Training Data Flow:**

### **1. User Interacts with Agent**
```
User → API → Smart Router → Agent (with context)
```

### **2. Agent Analyzes with Context**
```python
result = await agent.analyze(data, context=agent_context)
# Agent uses: context.model_path (trained model)
```

### **3. Interaction Logged**
```python
# Stored at: context.storage_path
await learner.log_interaction(
    user_id=context.user_id,
    org_id=context.org_id,
    team_id=context.team_id,
    app_context=context.app_context,
    agent_type="email",
    query=data,
    response=result,
    privacy=context.privacy
)
```

### **4. Training Triggered (100 interactions)**
```python
# Training data location: context.storage_path
# Model output location: context.model_path
await trainer.train_model(
    model_id=context.model_path,
    training_data_path=context.storage_path,
    base_model="mistral-7b-instruct-v0.2"
)
```

### **5. New Model Deployed**
```python
# Next API call uses trained model
context.model_path = "filecoin://atlas/team/company456/engineering/email"
# Agent automatically uses team's trained model
```

---

## 🎯 **Use Case Examples:**

### **Example 1: Personal User (No Sharing)**
```json
{
  "user_id": "user123",
  "app_context": "atlas",
  "atlas_tier": "personal",
  "privacy": "personal",
  "agent_type": "email"
}
```
**Result:**
- Model: `atlas/personal/user123/email`
- Storage: `atlas/personal/user123/email/`
- Can share: `false`
- Recommendations: Personal productivity tips

---

### **Example 2: Team User (Team Collaboration)**
```json
{
  "user_id": "user456",
  "org_id": "startup123",
  "team_id": "engineering",
  "app_context": "atlas",
  "atlas_tier": "team",
  "privacy": "org_private",
  "agent_type": "email"
}
```
**Result:**
- Model: `atlas/team/startup123/engineering/email`
- Storage: `atlas/team/startup123/engineering/email/`
- Can share: `true`
- Recommendations: Team collaboration suggestions

---

### **Example 3: Enterprise User (Org-Wide)**
```json
{
  "user_id": "user789",
  "org_id": "bigcorp456",
  "app_context": "atlas",
  "atlas_tier": "enterprise",
  "privacy": "org_public",
  "agent_type": "email"
}
```
**Result:**
- Model: `atlas/org/bigcorp456/email`
- Storage: `atlas/org/bigcorp456/email/`
- Can share: `true`
- Recommendations: Enterprise compliance, org policies

---

### **Example 4: Akashic in Atlas (Code Editor)**
```json
{
  "user_id": "user999",
  "org_id": "company789",
  "app_context": "akashic_atlas",
  "atlas_tier": "enterprise",
  "privacy": "personal",
  "agent_type": "development"
}
```
**Result:**
- Model: `akashic_atlas/personal/user999/development`
- Storage: `akashic_atlas/personal/user999/development/`
- Can share: `false` (user chose personal)
- Recommendations: Personal code patterns

---

### **Example 5: Trading Bot in Delt (Shared)**
```json
{
  "user_id": "trader123",
  "org_id": "hedgefund456",
  "team_id": "quant_team",
  "app_context": "akashic_delt",
  "delt_tier": "institutional",
  "privacy": "org_private",
  "agent_type": "development"
}
```
**Result:**
- Model: `akashic_delt/team/hedgefund456/quant_team/development`
- Storage: `akashic_delt/team/hedgefund456/quant_team/development/`
- Can share: `true`
- Recommendations: Team bot strategies

---

## 📁 **Files Updated:**

1. ✅ **`config/model_config.py`**
   - Updated Atlas tiers (Free/Personal/Individual/Team/Enterprise)
   - Changed Akashic isolation to privacy-controlled
   - Added conflict_resolution to isolation config

2. ✅ **`agents/base_agent.py`**
   - Added `AgentContext` class
   - Updated `analyze()` signature to accept context
   - Updated `query_llm()` to use context for model selection

3. ✅ **`api/smart_router.py`**
   - Builds `AgentContext` from request
   - Passes context to agents
   - Added `_get_storage_path()` method
   - Logs context in requests

---

## 🎉 **Benefits:**

### **For Users:**
- ✅ Right model for their tier
- ✅ Appropriate recommendations
- ✅ Privacy respected
- ✅ Seamless collaboration (if allowed)

### **For System:**
- ✅ Correct model routing
- ✅ Organized storage
- ✅ Efficient training
- ✅ Clear isolation boundaries

### **For Developers:**
- ✅ Context available in agents
- ✅ Easy to add tier-specific features
- ✅ Clear data flow
- ✅ Debuggable with context logging

---

## 🚀 **What This Enables:**

1. **Smart Workflows**
   - API constructs workflows based on context
   - Agents adapt to user's tier and privacy
   - Recommendations match user's needs

2. **Efficient Training**
   - Training data stored in right location
   - Models trained at right isolation level
   - No data leakage across boundaries

3. **Scalable Architecture**
   - Clear separation of concerns
   - Easy to add new tiers
   - Easy to add new contexts

4. **Better User Experience**
   - Personalized recommendations
   - Tier-appropriate features
   - Privacy-first by default

---

## ✅ **Complete Checklist:**

- [x] Update Atlas tiers to Free/Personal/Individual/Team/Enterprise
- [x] Change Akashic isolation to privacy-controlled
- [x] Add AgentContext class
- [x] Update BaseAgent to accept context
- [x] Update SmartRouter to build and pass context
- [x] Add storage_path determination
- [x] Add model_path to context
- [x] Add conflict_resolution strategy
- [x] Document all changes

---

**Created:** October 27, 2025  
**Version:** 3.1.0  
**Status:** COMPLETE ✅
