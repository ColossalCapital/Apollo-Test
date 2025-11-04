# 🔄 Model Retraining Triggers - How & When

**Apollo uses BOTH interaction count AND time-based triggers**

---

## 🎯 **Current Implementation:**

### **Dual Trigger System:**

```python
class ContinuousLearner:
    def __init__(
        self,
        min_interactions: int = 100,      # ← Interaction threshold
        training_interval_days: int = 7   # ← Time threshold
    ):
```

**Training is triggered when BOTH conditions are met:**
1. ✅ **Interaction Count:** >= 100 interactions logged
2. ✅ **Time Interval:** >= 7 days since last training

---

## 📊 **How It Works:**

### **Step 1: User Interacts with Agent**

```python
# User sends email, Apollo analyzes
response = await apollo.analyze(email)

# Interaction is logged
await continuous_learner.log_interaction(
    user_id="user123",
    agent_type="email",
    query=email,
    response=response
)
```

### **Step 2: Interaction Added to Buffer**

```python
# Buffer key: "atlas:email:user123"
interaction_buffers["atlas:email:user123"].append(interaction)

# Current count: 95 interactions
```

### **Step 3: Check Triggers**

```python
# After 100th interaction
if len(buffer) >= 100:  # ✅ Threshold met
    last_training = get_last_training_time()
    
    if (now - last_training) >= 7 days:  # ✅ Time interval met
        trigger_training()  # 🚀 Start training!
    else:
        wait_for_time_interval()  # ⏳ Wait
```

### **Step 4: Training Triggered**

```python
# Upload training data to Filecoin
training_data = interaction_buffers["atlas:email:user123"]
cid = await upload_to_filecoin(training_data)

# Submit training job to Theta GPU
job = await theta_trainer.submit_training(
    model_id="atlas:email:user123",
    training_data_cid=cid,
    base_model="mistral-7b-instruct-v0.2"
)

# Training takes ~2 hours, costs ~$1
```

### **Step 5: New Model Deployed**

```python
# After training completes
new_model = await download_from_theta(job_id)

# Upload to Filecoin
model_cid = await upload_to_filecoin(new_model)

# Update model registry
update_model_path("atlas:email:user123", model_cid)

# Next API call uses new model automatically!
```

---

## ⚙️ **Configurable Triggers:**

### **Default Settings:**

```python
# Default (conservative)
min_interactions = 100      # 100 interactions
training_interval_days = 7  # 1 week
```

### **Aggressive Learning:**

```python
# For power users who want frequent updates
min_interactions = 50       # 50 interactions
training_interval_days = 3  # 3 days
```

### **Conservative Learning:**

```python
# For cost-conscious or stable environments
min_interactions = 200      # 200 interactions
training_interval_days = 14 # 2 weeks
```

### **Enterprise Custom:**

```python
# Per-org configuration
org_config = {
    "org_id": "company456",
    "min_interactions": 150,
    "training_interval_days": 10,
    "training_schedule": "weekends_only",  # Only train on weekends
    "max_training_cost": 10  # Max $10/month per model
}
```

---

## 📈 **Trigger Scenarios:**

### **Scenario 1: Active User**

```
Day 1-7: User sends 150 emails
  ├─ 100 interactions logged ✅
  ├─ 7 days passed ✅
  └─ Training triggered! 🚀

Day 8-14: Training completes, new model deployed
  ├─ User continues using (50 more interactions)
  └─ Buffer: 50 interactions

Day 15-21: User sends 60 more emails
  ├─ 110 interactions logged ✅
  ├─ 7 days since last training ✅
  └─ Training triggered again! 🚀
```

**Result:** Model updates every ~2 weeks for active users

---

### **Scenario 2: Moderate User**

```
Day 1-30: User sends 80 emails
  ├─ 80 interactions logged ❌ (need 100)
  ├─ 30 days passed ✅
  └─ No training (need more data)

Day 31-60: User sends 30 more emails
  ├─ 110 interactions logged ✅
  ├─ 7 days passed ✅
  └─ Training triggered! 🚀
```

**Result:** Model updates when enough data accumulated

---

### **Scenario 3: Team Model**

```
Team of 5 people:
  ├─ Person A: 30 interactions
  ├─ Person B: 25 interactions
  ├─ Person C: 20 interactions
  ├─ Person D: 15 interactions
  └─ Person E: 20 interactions
  
Total: 110 interactions ✅
Time: 7 days ✅
Training triggered for team model! 🚀
```

**Result:** Team models train faster (more data)

---

## 🎛️ **Advanced Triggers:**

### **1. Feedback-Based Trigger**

```python
# If user gives negative feedback, trigger retraining sooner
if feedback_score < 0.5:
    min_interactions = 50  # Lower threshold
    training_interval_days = 3  # Sooner retraining
```

### **2. Drift Detection**

```python
# If model performance degrades, trigger retraining
if model_accuracy < 0.7:
    trigger_immediate_retraining()
```

### **3. Scheduled Training**

```python
# Train on specific schedule (e.g., every Sunday at 2am)
@cron("0 2 * * 0")  # Every Sunday at 2am
async def scheduled_training():
    for model in models_needing_update:
        if has_enough_data(model):
            trigger_training(model)
```

### **4. Cost-Based Trigger**

```python
# Only train if cost is acceptable
if training_cost < budget:
    trigger_training()
else:
    wait_for_budget_reset()
```

---

## 💰 **Cost Considerations:**

### **Training Costs:**

| Frequency | Interactions | Cost/Month | Use Case |
|-----------|-------------|------------|----------|
| **Weekly** | 100/week | ~$4/month | Active users |
| **Bi-weekly** | 200/2 weeks | ~$2/month | Moderate users |
| **Monthly** | 400/month | ~$1/month | Light users |

**Calculation:**
- Training cost: ~$1 per job (Theta GPU)
- 4 trainings/month = $4/month per model

---

## 🎯 **Recommended Settings:**

### **For Atlas (Personal AI):**

```python
# Personal tier
min_interactions = 100
training_interval_days = 7

# Team tier
min_interactions = 150  # More data from team
training_interval_days = 7

# Enterprise tier
min_interactions = 200  # Even more data
training_interval_days = 7
```

### **For Delt (Trading):**

```python
# Retail tier
min_interactions = 50   # Faster learning for traders
training_interval_days = 3

# Professional tier
min_interactions = 100
training_interval_days = 7

# Institutional tier
min_interactions = 200  # More conservative
training_interval_days = 14  # Bi-weekly
```

---

## 🔄 **Hierarchical Training Triggers:**

### **For Hierarchical Models:**

```python
# Org model: Train monthly
org_min_interactions = 1000  # Lots of data
org_training_interval = 30 days

# Team model: Train bi-weekly
team_min_interactions = 200
team_training_interval = 14 days

# Personal model: Train weekly
personal_min_interactions = 100
personal_training_interval = 7 days
```

**Why different intervals?**
- Org models: Stable, don't change often
- Team models: Moderate changes
- Personal models: Frequent updates needed

---

## 📊 **Monitoring & Metrics:**

### **Track Training Metrics:**

```python
{
    "model_id": "atlas:email:user123",
    "last_training": "2024-10-20T02:00:00Z",
    "interactions_since_last": 45,
    "interactions_needed": 55,
    "days_since_last": 5,
    "days_until_eligible": 2,
    "estimated_next_training": "2024-10-27T02:00:00Z"
}
```

### **User Dashboard:**

```
Your Email AI:
  ├─ Last updated: 5 days ago
  ├─ Interactions logged: 45/100
  ├─ Next update: In 2 days (when 100 interactions reached)
  └─ Model version: v3 (trained Oct 20)
```

---

## ✅ **Summary:**

**Training is triggered when:**

1. ✅ **Interaction threshold met** (default: 100 interactions)
2. ✅ **Time interval met** (default: 7 days since last training)
3. ✅ **No training already in progress**

**Benefits of dual trigger:**
- Prevents too-frequent training (cost control)
- Ensures enough data for meaningful training
- Balances freshness vs stability
- Configurable per tier/org

**Configurable settings:**
- `min_interactions` - How many interactions needed
- `training_interval_days` - Minimum days between trainings
- Can be customized per tier, org, or user

---

**Created:** October 27, 2025  
**Version:** 1.0.0  
**Status:** DOCUMENTED
