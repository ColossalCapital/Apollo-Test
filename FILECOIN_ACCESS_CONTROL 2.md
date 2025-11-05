# 🔐 Filecoin Access Control & Privacy

**How to control who can see and download files on Filecoin**

---

## 🎯 **The Challenge:**

Filecoin/IPFS is **public by default** - anyone with a CID (Content Identifier) can access the file.

**Problem:**
- User's personal data stored on Filecoin
- User's trained models stored on Filecoin
- Need to keep them private!

**Solution:**
- ✅ Encryption
- ✅ Access control via encryption keys
- ✅ Private IPFS networks
- ✅ Signed URLs with expiration

---

## 🔒 **Access Control Methods:**

### **Method 1: Encryption (Recommended)**

**How it works:**
1. Encrypt file before uploading to Filecoin
2. Only users with decryption key can read it
3. File is public on Filecoin, but encrypted

**Pros:**
- ✅ Simple to implement
- ✅ Works with any IPFS node
- ✅ User controls keys
- ✅ Can share by sharing key

**Cons:**
- ❌ File metadata visible (size, CID)
- ❌ Must decrypt to use

**Implementation:**
```python
import nacl.secret
import nacl.utils

class EncryptedFilecoinStorage:
    def __init__(self, filecoin_client):
        self.client = filecoin_client
    
    def generate_user_key(self, user_id: str) -> bytes:
        """Generate encryption key for user"""
        # Derive key from user_id + master secret
        # Store in secure key management system
        key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        return key
    
    async def upload_encrypted(
        self,
        user_id: str,
        file_path: str,
        data: bytes
    ) -> str:
        """Upload encrypted file to Filecoin"""
        
        # Get user's encryption key
        key = self.get_user_key(user_id)
        box = nacl.secret.SecretBox(key)
        
        # Encrypt data
        encrypted = box.encrypt(data)
        
        # Upload to Filecoin
        cid = await self.client.upload(encrypted)
        
        return cid
    
    async def download_encrypted(
        self,
        user_id: str,
        cid: str
    ) -> bytes:
        """Download and decrypt file from Filecoin"""
        
        # Download encrypted data
        encrypted = await self.client.download(cid)
        
        # Get user's encryption key
        key = self.get_user_key(user_id)
        box = nacl.secret.SecretBox(key)
        
        # Decrypt
        decrypted = box.decrypt(encrypted)
        
        return decrypted
```

---

### **Method 2: Private IPFS Network**

**How it works:**
1. Run private IPFS nodes (not public network)
2. Only authorized nodes can join
3. Files only accessible within private network

**Pros:**
- ✅ True privacy (not on public network)
- ✅ No encryption needed
- ✅ Fast access within network

**Cons:**
- ❌ Must run own IPFS nodes
- ❌ More complex infrastructure
- ❌ Less decentralized

**Implementation:**
```bash
# Create private IPFS network
ipfs init
ipfs bootstrap rm --all  # Remove public bootstrap nodes

# Generate swarm key
echo -e "/key/swarm/psk/1.0.0/\n/base16/\n$(tr -dc 'a-f0-9' < /dev/urandom | head -c64)" > ~/.ipfs/swarm.key

# Only nodes with this key can connect
```

---

### **Method 3: Signed URLs with Expiration**

**How it works:**
1. Store files on Filecoin
2. Apollo acts as gateway
3. Generate signed URLs with expiration
4. Only valid URLs can download

**Pros:**
- ✅ Fine-grained access control
- ✅ Time-limited access
- ✅ Can revoke access
- ✅ Audit trail

**Cons:**
- ❌ Apollo must be online (gateway)
- ❌ Not truly decentralized
- ❌ Single point of failure

**Implementation:**
```python
import jwt
from datetime import datetime, timedelta

class SignedURLManager:
    def __init__(self, secret_key: str):
        self.secret = secret_key
    
    def generate_signed_url(
        self,
        user_id: str,
        cid: str,
        expires_in: int = 3600  # 1 hour
    ) -> str:
        """Generate signed URL for file download"""
        
        # Create JWT token
        payload = {
            "user_id": user_id,
            "cid": cid,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        token = jwt.encode(payload, self.secret, algorithm="HS256")
        
        # Return signed URL
        return f"https://apollo.ai/download/{cid}?token={token}"
    
    def verify_token(self, token: str) -> dict:
        """Verify signed URL token"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise PermissionError("Token expired")
        except jwt.InvalidTokenError:
            raise PermissionError("Invalid token")

# Usage:
@app.get("/download/{cid}")
async def download_file(cid: str, token: str):
    # Verify token
    payload = signed_url_manager.verify_token(token)
    
    # Check user has access to this CID
    if not user_has_access(payload["user_id"], cid):
        raise HTTPException(403, "Access denied")
    
    # Download from Filecoin
    data = await filecoin_client.download(cid)
    
    return Response(content=data)
```

---

### **Method 4: Hybrid (Encryption + Signed URLs)**

**Best of both worlds:**
1. Encrypt files before upload (privacy)
2. Use signed URLs for access control (security)
3. Apollo decrypts and serves (convenience)

**Implementation:**
```python
class HybridStorage:
    async def upload_private(
        self,
        user_id: str,
        data: bytes
    ) -> dict:
        """Upload encrypted file with access control"""
        
        # 1. Encrypt
        encrypted = self.encrypt(user_id, data)
        
        # 2. Upload to Filecoin
        cid = await self.filecoin.upload(encrypted)
        
        # 3. Store metadata
        metadata = {
            "user_id": user_id,
            "cid": cid,
            "encrypted": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await self.db.store_metadata(user_id, cid, metadata)
        
        return {"cid": cid, "encrypted": True}
    
    async def generate_download_url(
        self,
        user_id: str,
        cid: str,
        expires_in: int = 3600
    ) -> str:
        """Generate signed URL for download"""
        
        # Verify user owns this file
        metadata = await self.db.get_metadata(cid)
        if metadata["user_id"] != user_id:
            raise PermissionError("Not your file")
        
        # Generate signed URL
        token = self.sign_url(user_id, cid, expires_in)
        
        return f"https://apollo.ai/download/{cid}?token={token}"
    
    @app.get("/download/{cid}")
    async def download(cid: str, token: str):
        # 1. Verify token
        payload = verify_token(token)
        
        # 2. Download encrypted from Filecoin
        encrypted = await filecoin.download(cid)
        
        # 3. Decrypt
        decrypted = decrypt(payload["user_id"], encrypted)
        
        # 4. Return file
        return Response(content=decrypted)
```

---

## 📥 **Model Download Feature:**

### **Let Users Download Their Trained Models:**

```python
# Add to gdpr_compliance.py

class GDPRComplianceManager:
    async def download_user_model(
        self,
        user_id: str,
        model_id: str,
        format: str = "gguf"
    ) -> dict:
        """
        Download user's trained model for offline use
        
        User can download their personalized models to:
        - Run locally on their machine
        - Use offline
        - Backup their models
        - Port to other platforms
        
        Args:
            user_id: User ID
            model_id: Model identifier (e.g., "atlas:email:user123")
            format: Model format (gguf, pytorch, onnx)
        
        Returns:
            Download URL and metadata
        """
        
        logger.info(f"📥 Model download request: user_id={user_id}, model_id={model_id}")
        
        # Verify user owns this model
        if not self._verify_model_ownership(user_id, model_id):
            raise PermissionError("You don't own this model")
        
        # Get model from Filecoin
        model_cid = await self._get_model_cid(model_id)
        
        # Generate signed download URL (expires in 1 hour)
        download_url = await self._generate_signed_url(
            user_id=user_id,
            cid=model_cid,
            expires_in=3600
        )
        
        # Get model metadata
        metadata = await self._get_model_metadata(model_id)
        
        # Log download
        await self.audit.log_event(
            event_type="model_download",
            user_id=user_id,
            details={"model_id": model_id, "format": format}
        )
        
        return {
            "model_id": model_id,
            "download_url": download_url,
            "expires_in": 3600,
            "format": format,
            "size_mb": metadata.get("size_mb"),
            "created_at": metadata.get("created_at"),
            "training_interactions": metadata.get("training_interactions"),
            "base_model": metadata.get("base_model"),
            "instructions": {
                "usage": "Download and run with llama.cpp or your preferred inference engine",
                "example": "llama-cli -m model.gguf -p 'Your prompt here'"
            }
        }
    
    async def list_user_models(
        self,
        user_id: str
    ) -> List[dict]:
        """List all models user can download"""
        
        models = []
        
        # Find all models for user
        contexts = ["atlas", "delt", "akashic", "akashic_atlas", "akashic_delt"]
        agents = ["email", "calendar", "strategy", "portfolio", "development"]  # All 62
        
        for context in contexts:
            for agent in agents:
                model_id = f"{context}:{agent}:{user_id}"
                
                # Check if model exists
                if await self._model_exists(model_id):
                    metadata = await self._get_model_metadata(model_id)
                    models.append({
                        "model_id": model_id,
                        "context": context,
                        "agent": agent,
                        "size_mb": metadata.get("size_mb"),
                        "created_at": metadata.get("created_at"),
                        "can_download": True
                    })
        
        return models
```

---

## 🔐 **API Endpoints for Model Download:**

### **1. List User's Models**

```bash
GET /v3/models/list/{user_id}
```

**Response:**
```json
{
  "user_id": "user123",
  "models": [
    {
      "model_id": "atlas:email:user123",
      "context": "atlas",
      "agent": "email",
      "size_mb": 234.5,
      "created_at": "2024-09-01T00:00:00Z",
      "can_download": true
    },
    {
      "model_id": "delt:strategy:user123",
      "context": "delt",
      "agent": "strategy",
      "size_mb": 456.7,
      "created_at": "2024-09-15T00:00:00Z",
      "can_download": true
    }
  ]
}
```

---

### **2. Download Model**

```bash
POST /v3/models/download
```

**Request:**
```json
{
  "user_id": "user123",
  "model_id": "atlas:email:user123",
  "format": "gguf"
}
```

**Response:**
```json
{
  "model_id": "atlas:email:user123",
  "download_url": "https://apollo.ai/download/QmXxx...?token=eyJhbGc...",
  "expires_in": 3600,
  "format": "gguf",
  "size_mb": 234.5,
  "instructions": {
    "usage": "Download and run with llama.cpp",
    "example": "llama-cli -m model.gguf -p 'Your prompt here'"
  }
}
```

---

### **3. Download Endpoint (with token)**

```bash
GET /download/{cid}?token={signed_token}
```

**Response:**
- Binary file download
- Content-Type: application/octet-stream
- Content-Disposition: attachment; filename="atlas_email_user123.gguf"

---

## 🔒 **Security Best Practices:**

### **1. Encryption Keys:**

```python
# Store encryption keys securely
class KeyManagement:
    def __init__(self):
        self.kms = AWS_KMS()  # Or HashiCorp Vault, etc.
    
    def get_user_key(self, user_id: str) -> bytes:
        """Get user's encryption key from KMS"""
        # Never store keys in database
        # Use key management service
        return self.kms.get_key(f"user_{user_id}")
    
    def rotate_key(self, user_id: str):
        """Rotate user's encryption key"""
        # Generate new key
        new_key = self.kms.generate_key()
        
        # Re-encrypt all files with new key
        # (Background job)
```

---

### **2. Access Control:**

```python
class AccessControl:
    async def can_download(
        self,
        user_id: str,
        model_id: str
    ) -> bool:
        """Check if user can download model"""
        
        # Parse model_id: "atlas:email:user123"
        parts = model_id.split(":")
        owner_id = parts[2]
        
        # User can only download their own models
        if user_id != owner_id:
            return False
        
        # Check if model exists
        if not await self.model_exists(model_id):
            return False
        
        # Check if user's subscription is active
        if not await self.subscription_active(user_id):
            return False
        
        return True
```

---

### **3. Rate Limiting:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v3/models/download")
@limiter.limit("10/hour")  # Max 10 downloads per hour
async def download_model(request: Request, ...):
    # Download logic
    pass
```

---

## 📊 **Comparison of Methods:**

| Method | Privacy | Decentralization | Complexity | Cost |
|--------|---------|------------------|------------|------|
| **Encryption** | ✅ High | ✅ High | 🟡 Medium | 💰 Low |
| **Private IPFS** | ✅ High | 🟡 Medium | 🔴 High | 💰💰 High |
| **Signed URLs** | 🟡 Medium | 🔴 Low | 🟢 Low | 💰 Low |
| **Hybrid** | ✅ High | 🟡 Medium | 🟡 Medium | 💰 Low |

---

## 💡 **Recommended Approach:**

### **Use Hybrid Method:**

1. **Encrypt all files** before uploading to Filecoin
   - User data is private
   - Models are private
   - Even if someone gets CID, they can't read it

2. **Use signed URLs** for access control
   - Time-limited access
   - Can revoke access
   - Audit trail

3. **Apollo acts as gateway**
   - Decrypts files
   - Verifies permissions
   - Logs downloads

**Benefits:**
- ✅ Privacy (encryption)
- ✅ Security (signed URLs)
- ✅ Convenience (Apollo handles decryption)
- ✅ Decentralized (Filecoin storage)
- ✅ User control (can download models)

---

## 🚀 **Implementation:**

```python
# Complete implementation

class SecureFilecoinStorage:
    def __init__(self, filecoin_client, kms):
        self.filecoin = filecoin_client
        self.kms = kms
        self.url_signer = SignedURLManager(secret_key="...")
    
    async def upload_private_file(
        self,
        user_id: str,
        file_path: str,
        data: bytes
    ) -> str:
        """Upload encrypted file to Filecoin"""
        
        # 1. Get user's encryption key
        key = self.kms.get_user_key(user_id)
        
        # 2. Encrypt data
        encrypted = self.encrypt(key, data)
        
        # 3. Upload to Filecoin
        cid = await self.filecoin.upload(encrypted)
        
        # 4. Store metadata
        await self.db.store({
            "user_id": user_id,
            "file_path": file_path,
            "cid": cid,
            "encrypted": True,
            "size": len(data)
        })
        
        return cid
    
    async def download_private_file(
        self,
        user_id: str,
        cid: str
    ) -> bytes:
        """Download and decrypt file"""
        
        # 1. Verify ownership
        metadata = await self.db.get_metadata(cid)
        if metadata["user_id"] != user_id:
            raise PermissionError("Not your file")
        
        # 2. Download encrypted from Filecoin
        encrypted = await self.filecoin.download(cid)
        
        # 3. Get user's key and decrypt
        key = self.kms.get_user_key(user_id)
        decrypted = self.decrypt(key, encrypted)
        
        return decrypted
    
    async def generate_download_link(
        self,
        user_id: str,
        cid: str,
        expires_in: int = 3600
    ) -> str:
        """Generate signed download URL"""
        
        # Verify ownership
        metadata = await self.db.get_metadata(cid)
        if metadata["user_id"] != user_id:
            raise PermissionError("Not your file")
        
        # Generate signed URL
        return self.url_signer.generate_signed_url(
            user_id, cid, expires_in
        )
```

---

**Created:** October 27, 2025  
**Version:** 1.0.0  
**Status:** ARCHITECTURE GUIDE
