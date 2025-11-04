# Enable Theta GPU - Quick Start

## 🎯 Current Status

**Apollo is using mock responses** because Theta GPU isn't active yet.

### **Health Check:**
```json
{
  "status": "healthy",
  "available_llms": [
    {
      "priority": 3,
      "provider": "mock",
      "model": "Fallback Responses",
      "status": "available"
    }
  ]
}
```

**Issue:** Theta GPU not showing in available LLMs

---

## ✅ Solution: Restart Apollo

Apollo needs to be restarted to load the updated `.env` file with Theta GPU configuration.

### **Option 1: Restart Docker Container**

```bash
cd /Users/leonard/Documents/repos/Jacob\ Aaron\ Leonard\ LLC/ColossalCapital/Infrastructure

# Restart Apollo container
docker-compose -f docker-compose.complete-system.yml restart apollo

# Check logs
docker-compose -f docker-compose.complete-system.yml logs -f apollo
```

### **Option 2: Full Rebuild (if restart doesn't work)**

```bash
cd /Users/leonard/Documents/repos/Jacob\ Aaron\ Leonard\ LLC/ColossalCapital/Infrastructure

# Stop Apollo
docker-compose -f docker-compose.complete-system.yml stop apollo

# Remove container
docker-compose -f docker-compose.complete-system.yml rm -f apollo

# Rebuild and start
docker-compose -f docker-compose.complete-system.yml up -d apollo

# Check logs
docker-compose -f docker-compose.complete-system.yml logs -f apollo
```

---

## 🧪 Verify Theta GPU is Active

### **1. Check Health Endpoint:**

```bash
curl http://localhost:8002/api/chat/health | jq .
```

**Expected Response:**
```json
{
  "status": "healthy",
  "available_llms": [
    {
      "priority": 1,
      "provider": "theta_gpu",
      "model": "Qwen2.5-Coder-32B",
      "status": "configured",
      "cost": "$0.003 per query",
      "note": "API integration pending"
    },
    {
      "priority": 3,
      "provider": "mock",
      "model": "Fallback Responses",
      "status": "available",
      "cost": "free"
    }
  ]
}
```

### **2. Test Chat:**

```bash
curl -X POST http://localhost:8002/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Are you smart yet?",
    "entity_id": "user_123"
  }' | jq .
```

**Expected Response:**
```json
{
  "response": "I'm getting smarter! I now have access to...",
  "model": "Qwen2.5-Coder-32B",
  "provider": "theta_gpu",
  "cost_tfuel": 0.001
}
```

---

## 📋 Current Configuration

### **Apollo/.env:**
```bash
# Theta GPU - ALL INFERENCE + TRAINING + RAG
THETA_API_KEY=pabffgfv706n79tup47u3hrdmcvxf2fj
THETA_GPU_URL=https://api.thetaedgecloud.com/gpu/v1
THETA_MODEL_API_URL=https://api.thetaedgecloud.com/models/v1

USE_THETA_GPU=true
USE_THETA_RAG=true

DEEPSEEK_DEVICE=theta
LOCAL_MODEL_PATH=none
```

**Status:** ✅ Configuration is correct, just needs restart

---

## ⚠️ Known Issue: API Integration Pending

Even after restart, Theta GPU will show as "configured" but the actual API call isn't implemented yet.

**Current behavior:**
1. Apollo tries Theta GPU API
2. Placeholder raises exception: "Theta GPU integration pending"
3. Falls back to mock responses

**To fully enable:**
1. ✅ Restart Apollo (loads Theta GPU config)
2. ⚠️ Implement Theta GPU API call in `chat_endpoints.py` line 132-173
3. ✅ Test with real API key

---

## 🔧 Implement Theta GPU API (Next Step)

**File:** `Apollo/api/chat_endpoints.py`

**Function:** `_query_theta_gpu()` (line 132-173)

**Current:**
```python
async def _query_theta_gpu(...):
    # TODO: Implement actual Theta GPU API call
    raise Exception("Theta GPU integration pending")
```

**Need to implement:**
```python
async def _query_theta_gpu(
    message: str,
    codebase_path: Optional[str],
    api_key: str,
    model: str
) -> str:
    """Query Theta GPU EdgeCloud"""
    
    prompt = f"""You are Apollo, an AI coding assistant.

User question: {message}
{f'Current codebase: {codebase_path}' if codebase_path else ''}

Provide a helpful, concise response."""
    
    async with aiohttp.ClientSession() as session:
        url = f"{os.getenv('THETA_GPU_URL')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are Apollo, an AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                error = await response.text()
                raise Exception(f"Theta GPU error: {response.status} - {error}")
```

---

## ✅ Quick Start Checklist

- [ ] **Restart Apollo container**
- [ ] **Verify Theta GPU shows in health check**
- [ ] **Test chat - should show "configured" status**
- [ ] **Implement Theta GPU API call** (optional - for real AI)
- [ ] **Test with real API key** (optional)

---

## 🎯 Expected Behavior After Restart

### **Before Restart:**
```
You: "Are you smart yet?"
Apollo: "⚠️ This is a fallback response..."
Provider: mock
```

### **After Restart (API not implemented):**
```
You: "Are you smart yet?"
Apollo: "⚠️ This is a fallback response..."
Provider: mock
Note: Theta GPU configured but API integration pending
```

### **After API Implementation:**
```
You: "Are you smart yet?"
Apollo: "Yes! I'm now powered by Qwen2.5-Coder 32B on Theta GPU..."
Provider: theta_gpu
Model: Qwen2.5-Coder-32B
Cost: $0.003
```

---

## 📝 Summary

**Current Issue:** Apollo using mock responses

**Root Cause:** Container needs restart to load Theta GPU config

**Solution:** 
```bash
docker-compose -f docker-compose.complete-system.yml restart apollo
```

**After Restart:** Theta GPU will show as "configured" (but still needs API implementation for real AI)

**Status:** 🟡 Configuration ready, API implementation pending
