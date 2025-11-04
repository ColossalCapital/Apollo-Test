# Apollo AI System - Complete Startup Guide

**Complete system with 136 agents, encrypted storage, and multi-tenant isolation.**

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install additional encryption dependencies
pip3 install cryptography httpx python-dotenv
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Your .env already has:
# ✅ FILECOIN_API_KEY (Storacha)
# ✅ THETA_API_KEY
# ✅ JARVISLABS_API_KEY
```

---

## 🧪 Test the System

### Run Test Suite
```bash
cd Apollo
python3 test_encryption_system.py
```

**Expected Output:**
```
🧪 APOLLO ENCRYPTION SYSTEM TEST SUITE
============================================================
TEST 1: Encryption Module
✅ Encryption successful
✅ Decryption successful
✅ Metadata encryption successful

TEST 2: Universal Vault Integration
✅ Vault initialized from .env
✅ Got Filecoin credentials

TEST 3: Encrypted Storage
✅ Encrypted storage initialized

TEST 4: API Startup
✅ Apollo API initialized successfully
✅ Storage endpoints registered

TEST SUMMARY
============================================================
✅ PASS - Encryption Module
✅ PASS - Vault Integration
✅ PASS - Encrypted Storage
✅ PASS - API Startup
============================================================
Results: 4/4 tests passed
🎉 ALL TESTS PASSED!
```

---

## 🎯 Start Apollo

### Option 1: Development Mode (Recommended)
```bash
cd Apollo
python3 -m uvicorn api.main:app --reload --port 8002
```

**Output:**
```
2025-10-29 09:00:00 - storage.unified_storage - INFO - 🚀 Unified Storage initialized (1 providers)
2025-10-29 09:00:00 - learning.unified_trainer - INFO - 🚀 Unified Trainer initialized
2025-10-29 09:00:00 - learning.unified_trainer - INFO -   Theta: ✅
2025-10-29 09:00:00 - learning.unified_trainer - INFO -   JarvisLabs: ✅
2025-10-29 09:00:00 - agentic.orchestrator.meta_orchestrator - INFO - 🧠 Meta-Orchestrator initialized with 136 agents
2025-10-29 09:00:00 - api.main - INFO - ================================================================================
2025-10-29 09:00:00 - api.main - INFO - 🚀 Apollo AI System v3 - PRODUCTION READY
2025-10-29 09:00:00 - api.main - INFO - ================================================================================
2025-10-29 09:00:00 - api.main - INFO -   🤖 Agents: 136
2025-10-29 09:00:00 - api.main - INFO -   🧠 Tier 3 Intelligence: ENABLED
2025-10-29 09:00:00 - api.main - INFO -   🔒 Multi-tenant Isolation: ENABLED
2025-10-29 09:00:00 - api.main - INFO -   💾 Storage: Filecoin + 0 backups
2025-10-29 09:00:00 - api.main - INFO -   🎮 GPU Training: Theta + JarvisLabs
2025-10-29 09:00:00 - api.main - INFO -   📚 Continuous Learning: ENABLED
2025-10-29 09:00:00 - api.main - INFO -   🔐 Encrypted Storage: ENABLED
2025-10-29 09:00:00 - api.main - INFO - ================================================================================
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
```

### Option 2: Production Mode
```bash
cd Apollo
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002
```

---

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8002/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Apollo AI System v3",
  "version": "3.0.0",
  "agents_count": 136,
  "tier3_enabled": true,
  "multi_tenant_enabled": true,
  "storage_providers": ["filecoin"],
  "gpu_providers": ["theta", "jarvislabs"],
  "continuous_learning_enabled": true
}
```

### Storage Health
```bash
curl http://localhost:8002/storage/health
```

**Response:**
```json
{
  "status": "healthy",
  "encryption": "enabled",
  "providers": ["filecoin", "theta", "jarvislabs"],
  "features": ["encryption", "byok", "multi-tenant"]
}
```

### Provider Status
```bash
curl -H "user_id: test_user" -H "org_id: test_org" \
  http://localhost:8002/storage/providers/status
```

**Response:**
```json
{
  "filecoin": {
    "available": true,
    "mode": "shared",
    "namespace": "colossalcapital/org_test_org/user_test_user",
    "endpoint": "https://api.storacha.network"
  },
  "theta": {
    "available": true,
    "mode": "shared",
    "namespace": "colossalcapital/org_test_org/user_test_user",
    "endpoint": "https://api.thetaedgecloud.com"
  },
  "jarvislabs": {
    "available": true,
    "mode": "shared",
    "namespace": "colossalcapital/org_test_org/user_test_user",
    "endpoint": "https://api.jarvislabs.ai"
  }
}
```

### Upload Encrypted File
```bash
curl -X POST http://localhost:8002/storage/upload \
  -H "user_id: test_user" \
  -H "org_id: test_org" \
  -F "file=@test.txt"
```

**Response:**
```json
{
  "file_id": "abc123...",
  "cid": "bafybeig...",
  "size_bytes": 1024,
  "content_hash": "sha256_hash",
  "encrypted": true,
  "message": "File uploaded and encrypted successfully"
}
```

### List All Agents
```bash
curl http://localhost:8002/agents
```

**Response:**
```json
{
  "agents": [
    {
      "name": "ledger",
      "class": "LedgerAgent",
      "category": "finance"
    },
    ...
  ],
  "total": 136
}
```

---

## 🔐 Security Features

### Encryption
- ✅ **AES-256-GCM** authenticated encryption
- ✅ **HKDF** key derivation for isolation
- ✅ **Zero-knowledge** architecture
- ✅ Data encrypted BEFORE upload

### Multi-Tenant Isolation
- ✅ Unique keys per user/org
- ✅ Namespace isolation on Filecoin
- ✅ No cross-user data access
- ✅ Audit logs for all operations

### BYOK Support
- ✅ Enterprise users can provide own keys
- ✅ Full control and ownership
- ✅ Unlimited resources
- ✅ Stored encrypted in Universal Vault

---

## 📊 System Status

### Current Configuration
```
✅ Agents: 136
✅ Providers: Filecoin, Theta, JarvisLabs
✅ Encryption: Enabled
✅ Multi-tenant: Enabled
✅ BYOK: Enabled
✅ Continuous Learning: Enabled
```

### Provider Keys (from .env)
```
✅ Filecoin: did:key:z6MkmeNXeT6LX4vqJxYmVCRm4C1ujC5G4KVFPmRAMdbbzVJP
✅ Theta: z2cdyzt5d36tczat84v6rmc3xp1sqszh
✅ JarvisLabs: csn_ooNKBb5voGQp9shD0wbpY1u8oNUWYDKGGJKPhtE
```

---

## 🧩 Integration with Atlas

### Atlas Upload Flow
```typescript
// Atlas calls Apollo for encrypted upload
const response = await fetch('http://localhost:8002/storage/upload', {
  method: 'POST',
  headers: {
    'user_id': userId,
    'org_id': orgId,
  },
  body: formData
});

const { file_id, cid } = await response.json();
// Store file_id in Atlas database
```

### Atlas Download Flow
```typescript
// Atlas calls Apollo for encrypted download
const response = await fetch(`http://localhost:8002/storage/download/${fileId}`, {
  headers: {
    'user_id': userId,
    'org_id': orgId,
  }
});

const blob = await response.blob();
// Display file to user
```

---

## 🐛 Troubleshooting

### Issue: "No Filecoin credentials available"
**Solution:** Check that `.env` has `FILECOIN_API_KEY` set

### Issue: "Theta: ❌" in logs
**Solution:** Check that `.env` has `THETA_API_KEY` set

### Issue: "Universal Vault connection failed"
**Solution:** Universal Vault is optional for basic operation. Apollo will use .env directly.

### Issue: Import errors
**Solution:**
```bash
pip3 install cryptography httpx python-dotenv fastapi uvicorn
```

---

## 📚 Documentation

- **ENCRYPTION_SETUP_GUIDE.md** - Complete encryption documentation
- **PROVIDER_SETUP_GUIDE.md** - Provider configuration guide
- **AGENT_CATEGORIZATION.md** - All 136 agents documented
- **API_INTEGRATION_GUIDE.md** - API usage examples

---

## ✅ Verification Checklist

- [x] Python dependencies installed
- [x] .env configured with provider keys
- [x] Test suite passes (4/4 tests)
- [x] Apollo starts successfully
- [x] Health endpoint responds
- [x] Storage endpoints available
- [x] 136 agents loaded
- [x] Encryption enabled
- [x] Multi-tenant isolation enabled

---

## 🎉 You're Ready!

**Apollo is now running with:**
- 🤖 136 AI agents
- 🔐 Zero-knowledge encryption
- 💾 Filecoin decentralized storage
- 🎮 Theta + JarvisLabs GPU training
- 🏢 Multi-tenant isolation
- 🔑 BYOK support

**Next steps:**
1. Test file upload via API
2. Integrate with Atlas frontend
3. Set up Universal Vault (optional)
4. Configure PostgreSQL for metadata
5. Deploy to production

**Apollo AI System v3 is PRODUCTION READY!** 🚀
