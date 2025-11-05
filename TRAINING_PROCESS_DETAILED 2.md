# 🎓 Training Process - Complete Flow with Theta GPU

**Example: Document Agent Training for a User**

---

## 🎯 **Scenario:**

**User:** Sarah (Enterprise tier, Marketing team)
**Agent:** Document Agent
**Use Case:** Sarah uploads and analyzes 100+ marketing documents

---

## 📊 **Step-by-Step Training Process:**

### **Phase 1: Data Collection (Days 1-7)**

#### **Day 1: Sarah uploads first document**

```python
# Sarah uses Atlas to upload a document
document = {
    "file": "Q3_Marketing_Strategy.pdf",
    "content": "Our Q3 strategy focuses on...",
    "metadata": {
        "type": "strategy",
        "department": "marketing",
        "date": "2024-10-01"
    }
}

# Atlas calls Apollo
response = await apollo_client.post("/v3/analyze", json={
    "user_id": "sarah123",
    "org_id": "company456",
    "team_id": "marketing",
    "app_context": "atlas",
    "atlas_tier": "enterprise",
    "privacy": "org_private",
    "agent_type": "document",
    "data": document
})

# Document Agent analyzes
result = await document_agent.analyze(document, context=agent_context)
# Returns: {
#   "summary": "Q3 marketing strategy document...",
#   "key_points": [...],
#   "action_items": [...]
# }
```

#### **Interaction Logged:**

```python
# Continuous learner logs this interaction
interaction = {
    "user_id": "sarah123",
    "org_id": "company456",
    "team_id": "marketing",
    "app_context": "atlas",
    "agent_type": "document",
    "timestamp": "2024-10-01T10:30:00Z",
    
    # Input (what user provided)
    "query": {
        "file": "Q3_Marketing_Strategy.pdf",
        "content": "Our Q3 strategy focuses on...",
        "action": "analyze"
    },
    
    # Output (what agent returned)
    "response": {
        "summary": "Q3 marketing strategy document...",
        "key_points": ["Focus on digital channels", "Budget: $500K", ...],
        "action_items": ["Launch campaign by Oct 15", ...]
    },
    
    # User feedback (optional)
    "feedback": 0.9,  # Sarah rated it 9/10
    
    # Privacy & context
    "privacy": "org_private",
    "atlas_tier": "enterprise"
}

# Stored in buffer
buffer_key = "atlas:document:company456:team:marketing"
interaction_buffers[buffer_key].append(interaction)
```

#### **Storage Location (Filecoin):**

```
Filecoin Path: atlas/team/company456/marketing/document/interactions/

Files:
├── interaction_001_20241001_103000.json
├── interaction_002_20241001_143000.json
├── interaction_003_20241002_090000.json
└── ...
```

---

#### **Days 2-7: Sarah continues using**

```python
# Sarah analyzes 100+ documents
- Marketing strategies (20 docs)
- Campaign reports (30 docs)
- Competitor analysis (25 docs)
- Budget documents (15 docs)
- Presentations (10 docs)

# Each interaction logged
Total interactions: 105
Buffer: atlas:document:company456:team:marketing
```

---

### **Phase 2: Training Trigger (Day 7)**

#### **Trigger Check:**

```python
# After 100th interaction
buffer_key = "atlas:document:company456:team:marketing"
interactions = interaction_buffers[buffer_key]

# Check conditions
if len(interactions) >= 100:  # ✅ 105 interactions
    last_training = get_last_training_time(buffer_key)
    
    if (now - last_training) >= 7 days:  # ✅ 7 days passed
        # TRIGGER TRAINING!
        await trigger_training(buffer_key)
```

---

### **Phase 3: Data Preparation**

#### **Step 1: Collect Training Data**

```python
# Get all interactions from buffer
training_data = []

for interaction in interaction_buffers[buffer_key]:
    # Convert to training format
    training_example = {
        "instruction": "Analyze this document and provide insights",
        
        "input": f"""
        Document: {interaction['query']['file']}
        Content: {interaction['query']['content']}
        Type: {interaction['query'].get('type', 'unknown')}
        """,
        
        "output": f"""
        Summary: {interaction['response']['summary']}
        Key Points: {', '.join(interaction['response']['key_points'])}
        Action Items: {', '.join(interaction['response']['action_items'])}
        """,
        
        # Metadata
        "feedback": interaction.get('feedback', 1.0),
        "timestamp": interaction['timestamp']
    }
    
    training_data.append(training_example)

# Result: 105 training examples
```

#### **Step 2: Upload to Filecoin**

```python
# Package training data
training_package = {
    "model_id": "atlas:document:company456:team:marketing",
    "base_model": "mistral-7b-instruct-v0.2",
    "training_data": training_data,
    "metadata": {
        "user_count": 5,  # 5 team members contributed
        "interaction_count": 105,
        "date_range": "2024-10-01 to 2024-10-07",
        "privacy": "org_private",
        "team": "marketing"
    }
}

# Upload to Filecoin
cid = await filecoin_client.upload(
    data=training_package,
    path="atlas/team/company456/marketing/document/training/"
)

# CID: QmXxxx... (content identifier)
```

**Filecoin Storage:**

```
Path: atlas/team/company456/marketing/document/training/

Files:
├── training_data_20241007.json (CID: QmXxxx...)
│   ├── 105 training examples
│   ├── Metadata
│   └── Base model info
└── previous_trainings/
    └── training_data_20240930.json (previous version)
```

---

### **Phase 4: Theta GPU Training**

#### **Step 1: Submit Training Job**

```python
# Submit to Theta EdgeCloud
job = await theta_trainer.submit_training(
    model_id="atlas:document:company456:team:marketing",
    training_data_cid="QmXxxx...",  # Filecoin CID
    base_model="mistral-7b-instruct-v0.2",
    hyperparameters={
        "epochs": 3,
        "learning_rate": 2e-5,
        "batch_size": 4,
        "max_length": 2048
    }
)

# Job submitted to Theta network
# Cost: ~$1 for 2 hours of GPU time
```

#### **Step 2: Theta GPU Training**

```python
# On Theta EdgeCloud GPU node:

1. Download base model (Mistral-7B)
   ├─ Model size: 7B parameters
   └─ Download time: ~5 minutes

2. Download training data from Filecoin
   ├─ CID: QmXxxx...
   ├─ Size: ~10MB (105 examples)
   └─ Download time: ~1 minute

3. Fine-tune model
   ├─ Method: LoRA (Low-Rank Adaptation)
   ├─ Epochs: 3
   ├─ Batch size: 4
   ├─ Training time: ~2 hours
   └─ GPU: NVIDIA A100 (Theta EdgeCloud)

4. Model learns:
   ├─ Marketing team's document patterns
   ├─ How to summarize marketing docs
   ├─ Key points team cares about
   ├─ Action items format team uses
   └─ Team's communication style

5. Save trained model
   ├─ Format: GGUF (for llama.cpp)
   ├─ Size: ~500MB (LoRA adapters + base)
   └─ Compression: Quantized to 4-bit
```

#### **Step 3: Upload Trained Model to Filecoin**

```python
# Training complete, upload model
model_cid = await filecoin_client.upload(
    data=trained_model,
    path="atlas/team/company456/marketing/document/models/"
)

# Model CID: QmYyyy...
```

**Filecoin Storage (After Training):**

```
Path: atlas/team/company456/marketing/document/

Structure:
├── interactions/
│   ├── interaction_001.json
│   ├── interaction_002.json
│   └── ... (105 files)
│
├── training/
│   ├── training_data_20241007.json (CID: QmXxxx...)
│   └── previous_trainings/
│
└── models/
    ├── model_v1_20241007.gguf (CID: QmYyyy...) ← NEW!
    │   ├── Size: 500MB
    │   ├─ Base: Mistral-7B
    │   └─ Trained on: 105 marketing docs
    └── previous_models/
        └── model_v0_base.gguf (base model)
```

---

### **Phase 5: Model Deployment**

#### **Step 1: Update Model Registry**

```python
# Update model registry
model_registry["atlas:document:company456:team:marketing"] = {
    "model_cid": "QmYyyy...",
    "version": "v1",
    "created_at": "2024-10-07T04:00:00Z",
    "base_model": "mistral-7b-instruct-v0.2",
    "training_interactions": 105,
    "team": "marketing",
    "lineage": [
        "mistral-7b-instruct-v0.2",  # Base
        "atlas:document:company456:org",  # Org model (if exists)
        "atlas:document:company456:team:marketing"  # Team model
    ]
}
```

#### **Step 2: Model Ready for Use**

```python
# Next API call automatically uses new model

# Sarah uploads another document
response = await apollo_client.post("/v3/analyze", json={
    "user_id": "sarah123",
    "org_id": "company456",
    "team_id": "marketing",
    "app_context": "atlas",
    "atlas_tier": "enterprise",
    "privacy": "org_private",
    "agent_type": "document",
    "data": new_document
})

# Smart router determines model
model_path = "filecoin://QmYyyy..."  # Uses trained model!

# Document Agent uses trained model
result = await document_agent.analyze(
    data=new_document,
    context=AgentContext(
        model_path="filecoin://QmYyyy...",  # ← Trained model
        # ... other context
    )
)

# Result: Better analysis because model learned team's patterns!
```

---

## 📊 **What Data is Stored Where:**

### **Filecoin Storage Structure:**

```
atlas/team/company456/marketing/document/

1. Interactions (Raw data)
   ├── Location: interactions/
   ├── Format: JSON files
   ├── Size: ~10MB (105 files)
   ├── Privacy: Encrypted (team key)
   └── Purpose: Training data

2. Training Datasets (Processed)
   ├── Location: training/
   ├── Format: JSON (instruction-input-output)
   ├── Size: ~10MB
   ├── Privacy: Encrypted (team key)
   └── Purpose: Theta GPU training

3. Trained Models (AI models)
   ├── Location: models/
   ├── Format: GGUF (quantized)
   ├── Size: ~500MB per model
   ├── Privacy: Encrypted (team key)
   └── Purpose: Inference

4. Metadata (Model info)
   ├── Location: metadata/
   ├── Format: JSON
   ├── Size: ~1KB
   ├── Privacy: Encrypted (team key)
   └── Purpose: Model registry
```

---

## 🔐 **Privacy & Encryption:**

### **Data Encryption:**

```python
# Before uploading to Filecoin
def encrypt_training_data(data, team_id):
    # Get team's encryption key
    key = key_management.get_team_key(team_id)
    
    # Encrypt data
    encrypted = encrypt(data, key)
    
    # Upload encrypted data
    cid = filecoin.upload(encrypted)
    
    return cid

# Only team members can decrypt
def decrypt_training_data(cid, team_id):
    # Download encrypted data
    encrypted = filecoin.download(cid)
    
    # Get team's key
    key = key_management.get_team_key(team_id)
    
    # Decrypt
    data = decrypt(encrypted, key)
    
    return data
```

**Result:** Even though data is on public Filecoin network, only team members with the key can read it!

---

## 💰 **Cost Breakdown:**

### **Per Training Job:**

```
Storage (Filecoin):
├── Interactions: 10MB × $0.000001/MB = $0.00001
├── Training data: 10MB × $0.000001/MB = $0.00001
├── Trained model: 500MB × $0.000001/MB = $0.0005
└── Total storage: $0.00052 (~$0.001)

Training (Theta GPU):
├── GPU time: 2 hours
├── Cost: $0.50/hour
└── Total training: $1.00

Total per training: $1.001 (~$1)
```

### **Per User Per Month:**

```
Active user (4 trainings/month):
├── Training: 4 × $1 = $4
├── Storage: 4 × $0.001 = $0.004
└── Total: $4.004

Moderate user (2 trainings/month):
├── Training: 2 × $1 = $2
├── Storage: 2 × $0.001 = $0.002
└── Total: $2.002

Light user (1 training/month):
├── Training: 1 × $1 = $1
├── Storage: 1 × $0.001 = $0.001
└── Total: $1.001
```

**vs AWS:**
- AWS GPU (p3.2xlarge): $3.06/hour × 2 hours = $6.12
- AWS S3 storage: $0.023/GB × 0.5GB = $0.0115
- **Total: $6.13 per training**

**Theta savings: 84% cheaper!** 🎉

---

## 🔄 **Training Data Examples:**

### **Example 1: Marketing Document**

```json
{
  "instruction": "Analyze this marketing document and provide insights",
  
  "input": "Document: Q3_Marketing_Strategy.pdf\nContent: Our Q3 strategy focuses on digital channels with a budget of $500K. Key initiatives include social media campaigns, influencer partnerships, and content marketing. Target: 50% increase in leads.",
  
  "output": "Summary: Q3 marketing strategy focusing on digital channels with $500K budget.\n\nKey Points:\n- Digital channel focus\n- Budget: $500K\n- Social media campaigns\n- Influencer partnerships\n- Content marketing\n- Target: 50% lead increase\n\nAction Items:\n- Launch social media campaign by Oct 15\n- Identify influencer partners by Oct 20\n- Create content calendar by Oct 25",
  
  "feedback": 0.9
}
```

### **Example 2: Budget Document**

```json
{
  "instruction": "Analyze this budget document and provide insights",
  
  "input": "Document: Marketing_Budget_Q3.xlsx\nContent: Total budget $500K allocated across: Social media ($200K), Influencers ($150K), Content ($100K), Tools ($50K).",
  
  "output": "Summary: Q3 marketing budget of $500K with clear allocation.\n\nKey Points:\n- Total budget: $500K\n- Social media: $200K (40%)\n- Influencers: $150K (30%)\n- Content: $100K (20%)\n- Tools: $50K (10%)\n\nAction Items:\n- Approve budget by Oct 10\n- Set up tracking for each category\n- Review spend monthly",
  
  "feedback": 0.95
}
```

### **After 105 Examples:**

**Model learns:**
- ✅ Marketing team's document structure
- ✅ Key points they care about (budget, timelines, targets)
- ✅ Action item format they prefer
- ✅ Summary style they like
- ✅ Industry-specific terminology

---

## 🎯 **Summary:**

### **Training Process:**

1. **Data Collection (7 days)**
   - User interactions logged
   - Stored on Filecoin (encrypted)
   - 100+ examples collected

2. **Training Trigger**
   - 100 interactions + 7 days
   - Data packaged for training
   - Uploaded to Filecoin

3. **Theta GPU Training (2 hours)**
   - Download base model
   - Download training data from Filecoin
   - Fine-tune on Theta GPU
   - Cost: $1

4. **Model Deployment**
   - Upload trained model to Filecoin
   - Update model registry
   - Ready for use immediately

5. **Continuous Improvement**
   - Model used for next 100 interactions
   - Process repeats
   - Model gets better over time

### **Storage:**

- **Interactions:** Filecoin (encrypted, team-only)
- **Training Data:** Filecoin (encrypted, team-only)
- **Trained Models:** Filecoin (encrypted, team-only)
- **Metadata:** Filecoin (model registry)

### **Cost:**

- **Training:** $1 per job (Theta GPU)
- **Storage:** $0.001 per job (Filecoin)
- **Total:** ~$1 per training
- **Savings:** 84% vs AWS

---

**Created:** October 27, 2025  
**Version:** 1.0.0  
**Status:** COMPLETE TRAINING FLOW DOCUMENTED
