# Provider Setup Guide - BYOK + Multi-tenant

Apollo supports **two modes** for external providers:

1. **🔑 BYOK (Bring Your Own Key)** - Users provide their own API keys
2. **🏢 Shared Multi-tenant** - We provide infrastructure with isolation

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Atlas User Request                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Apollo API Layer                       │
│  • Checks for user-provided keys (BYOK)                 │
│  • Falls back to shared infrastructure                  │
│  • Applies multi-tenant isolation                       │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
    ┌───────────────────┐   ┌───────────────────┐
    │   BYOK Mode       │   │  Shared Mode      │
    │                   │   │                   │
    │ User's Keys       │   │ Our Keys          │
    │ User's Namespace  │   │ Isolated Namespace│
    │ No Limits         │   │ Resource Limits   │
    └───────────────────┘   └───────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
            ┌───────────────────────────┐
            │   External Providers      │
            │  • Filecoin               │
            │  • Theta GPU              │
            │  • JarvisLabs GPU         │
            └───────────────────────────┘
```

---

## 📦 1. Filecoin Storage Setup

### Option A: Shared Multi-tenant (Recommended for most users)

**We provide:**
- Filecoin account and API keys
- Multi-tenant isolation by org/user
- Automatic namespace management
- Cost included in subscription

**Setup:**
```bash
# 1. Get Filecoin API keys from web3.storage
# Sign up at: https://web3.storage

# 2. Add to .env
FILECOIN_API_KEY=your_key_here
FILECOIN_API_SECRET=your_secret_here

# 3. Users automatically get isolated storage:
# colossalcapital/org_123/user_456/
```

**Namespace Structure:**
```
colossalcapital/                    # Our root
├── org_acme/                       # Organization isolation
│   ├── user_alice/                 # User isolation
│   │   ├── documents/
│   │   ├── training_data/
│   │   └── models/
│   └── user_bob/
│       └── ...
└── org_widgets/
    └── ...
```

### Option B: BYOK (Bring Your Own Key)

**User provides:**
- Their own Filecoin account
- Their own API keys
- Full control and ownership
- They pay Filecoin directly

**Atlas UI Flow:**
```typescript
// User settings page
<FilecoinSettings>
  <Toggle>Use my own Filecoin account</Toggle>
  <Input placeholder="API Key" />
  <Input placeholder="API Secret" />
  <Input placeholder="Endpoint (optional)" />
  <Button>Save Keys</Button>
</FilecoinSettings>
```

**API Request:**
```typescript
// When user has BYOK enabled
const response = await apolloClient.uploadFile(file, {
  user_id: "user_456",
  org_id: "org_123",
  byok_keys: {
    filecoin: {
      api_key: "user_provided_key",
      api_secret: "user_provided_secret"
    }
  }
});
```

---

## 🎮 2. Theta GPU Training Setup

### Option A: Shared Multi-tenant

**We provide:**
- Theta GPU account
- Resource limits per user (10 GPU hours/month)
- Multi-tenant job isolation
- Cost included in subscription

**Setup:**
```bash
# 1. Get Theta API keys
# Sign up at: https://www.thetaedgecloud.com

# 2. Add to .env
THETA_API_KEY=your_key_here
THETA_WALLET=your_wallet_address_here

# 3. Configure limits
MAX_GPU_HOURS_PER_USER=10
MAX_CONCURRENT_JOBS=2
```

**Resource Limits (Shared Mode):**
| Tier | GPU Hours/Month | Concurrent Jobs | Cost |
|------|-----------------|-----------------|------|
| Free | 2 | 1 | $0 |
| Pro | 10 | 2 | Included |
| Enterprise | 50 | 5 | Included |

### Option B: BYOK

**User provides:**
- Their own Theta account
- Unlimited GPU hours (they pay)
- No concurrent job limits

**Atlas UI:**
```typescript
<ThetaSettings>
  <Toggle>Use my own Theta account</Toggle>
  <Input placeholder="API Key" />
  <Input placeholder="Wallet Address" />
  <Alert>
    You'll be charged directly by Theta (~$1/training job)
  </Alert>
</ThetaSettings>
```

---

## 🔬 3. JarvisLabs GPU Training Setup

### Option A: Shared Multi-tenant

**We provide:**
- JarvisLabs account
- Resource limits per user
- Alternative to Theta
- Cost included in subscription

**Setup:**
```bash
# 1. Get JarvisLabs API key
# Sign up at: https://jarvislabs.ai

# 2. Add to .env
JARVISLABS_API_KEY=your_key_here
```

### Option B: BYOK

**User provides:**
- Their own JarvisLabs account
- Unlimited resources

---

## 🔐 4. Multi-tenant Isolation

### How It Works

**Shared Mode Isolation:**
```python
# Automatic namespace generation
namespace = f"colossalcapital/org_{org_id}/user_{user_id}"

# Example:
# "colossalcapital/org_acme/user_alice"
# "colossalcapital/org_acme/user_bob"
# "colossalcapital/org_widgets/user_charlie"
```

**Data Isolation:**
- ✅ Users can only access their own data
- ✅ Organizations can share data within org (if configured)
- ✅ No cross-org data leakage
- ✅ Audit logs for all access

**Resource Isolation:**
- ✅ GPU hours tracked per user
- ✅ Concurrent job limits per user
- ✅ Storage quotas per user/org
- ✅ Rate limiting per user

---

## 🚀 5. Implementation in Atlas

### Backend (Rust)

```rust
// atlas/backend/src/apollo_client.rs

pub struct ApolloRequest {
    pub user_id: String,
    pub org_id: String,
    pub byok_keys: Option<BYOKKeys>,
}

pub struct BYOKKeys {
    pub filecoin: Option<FilecoinKeys>,
    pub theta: Option<ThetaKeys>,
    pub jarvislabs: Option<JarvisLabsKeys>,
}

impl ApolloClient {
    pub async fn upload_file(
        &self,
        file: Vec<u8>,
        request: ApolloRequest,
    ) -> Result<UploadResponse> {
        // Apollo will check for BYOK keys first
        // Falls back to shared infrastructure
        self.post("/storage/upload", json!({
            "user_id": request.user_id,
            "org_id": request.org_id,
            "byok_keys": request.byok_keys,
            "file": base64::encode(file),
        })).await
    }
}
```

### Frontend (React Native)

```typescript
// Atlas/frontend/mobile/src/screens/SettingsScreen.tsx

export const ProviderSettings = () => {
  const [byokEnabled, setBYOKEnabled] = useState(false);
  const [filecoinKeys, setFilecoinKeys] = useState({
    apiKey: '',
    apiSecret: '',
  });

  const saveKeys = async () => {
    await apolloClient.updateProviderKeys({
      filecoin: byokEnabled ? filecoinKeys : null,
    });
  };

  return (
    <View>
      <Text>Storage Provider</Text>
      <Switch
        value={byokEnabled}
        onValueChange={setBYOKEnabled}
        label="Use my own Filecoin account"
      />
      
      {byokEnabled && (
        <>
          <TextInput
            placeholder="Filecoin API Key"
            value={filecoinKeys.apiKey}
            onChangeText={(text) => 
              setFilecoinKeys({...filecoinKeys, apiKey: text})
            }
            secureTextEntry
          />
          <TextInput
            placeholder="Filecoin API Secret"
            value={filecoinKeys.apiSecret}
            onChangeText={(text) => 
              setFilecoinKeys({...filecoinKeys, apiSecret: text})
            }
            secureTextEntry
          />
          <Button title="Save Keys" onPress={saveKeys} />
        </>
      )}
      
      <Text style={{marginTop: 10, color: 'gray'}}>
        {byokEnabled 
          ? "You'll be charged directly by Filecoin"
          : "Storage included in your subscription"}
      </Text>
    </View>
  );
};
```

---

## 💰 6. Cost Comparison

### Shared Mode (We Pay)
| Provider | Our Cost | User Cost | Included In |
|----------|----------|-----------|-------------|
| Filecoin | $0.01/GB/month | $0 | All tiers |
| Theta GPU | $1/job | $0 | Pro+ tiers |
| JarvisLabs | $1.50/job | $0 | Enterprise |

### BYOK Mode (User Pays)
| Provider | Our Cost | User Cost | Benefit |
|----------|----------|-----------|---------|
| Filecoin | $0 | $0.01/GB/month | Unlimited storage |
| Theta GPU | $0 | $1/job | Unlimited training |
| JarvisLabs | $0 | $1.50/job | Unlimited training |

---

## 🔧 7. Quick Start

### For Development (Shared Mode)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your shared keys
nano .env

# 3. Start Apollo
python3 -m uvicorn api.main:app --reload --port 8002

# 4. Test
curl http://localhost:8002/health
```

### For Production

```bash
# 1. Set up all three providers
# - Filecoin: https://web3.storage
# - Theta: https://www.thetaedgecloud.com
# - JarvisLabs: https://jarvislabs.ai

# 2. Configure environment
export FILECOIN_API_KEY="..."
export THETA_API_KEY="..."
export JARVISLABS_API_KEY="..."

# 3. Enable BYOK
export ALLOW_BYOK=true

# 4. Deploy
docker-compose up -d
```

---

## 📊 8. Monitoring & Limits

### Track Usage (Shared Mode)

```python
# Apollo tracks usage per user
from config.provider_config import get_theta_config

config = get_theta_config("user_123", "org_456")

if config["mode"] == "shared":
    limits = config["limits"]
    # Check: max_gpu_hours, max_concurrent
    # Enforce limits before starting job
```

### BYOK Mode

```python
# No limits - user pays directly
config = get_theta_config("user_123", "org_456", user_keys)

if config["mode"] == "byok":
    # No limits to enforce
    # User is billed directly by provider
```

---

## ✅ Next Steps

1. **Set up shared infrastructure:**
   - [ ] Create Filecoin account
   - [ ] Create Theta account
   - [ ] Create JarvisLabs account
   - [ ] Add keys to `.env`

2. **Implement BYOK UI in Atlas:**
   - [ ] Settings page for provider keys
   - [ ] Secure key storage (encrypted)
   - [ ] Key validation

3. **Add usage tracking:**
   - [ ] Track GPU hours per user
   - [ ] Track storage per user
   - [ ] Alert when approaching limits

4. **Documentation:**
   - [ ] User guide for BYOK setup
   - [ ] Pricing page
   - [ ] FAQ

---

**Status:** Ready to implement! 🚀
