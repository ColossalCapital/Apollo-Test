# 🪙 Web3 Wallet & Token Rewards System

**Users earn tokens for their data and AI usage**

---

## 🎯 **Vision:**

**Users should OWN and PROFIT from their data and AI models**

Instead of paying for storage and compute, users EARN tokens:
- 💾 **Filecoin (FIL)** - For storing their data
- ⚡ **TFUEL** - For GPU compute on Theta
- 🐢 **WTF Coin** - Platform utility token (auto-convert option)

---

## 🔄 **User Journey:**

### **Step 1: Sign Up for Atlas**

```
┌─────────────────────────────────────────────────┐
│          Welcome to Atlas! 🎉                   │
│                                                 │
│  Atlas uses Web3 for data ownership.           │
│  You'll earn tokens for your data & AI usage!  │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  🆕 Create New Web3 Wallet            │    │
│  │     (We'll set it up for you)         │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  🔗 Connect Existing Wallet           │    │
│  │     (MetaMask, WalletConnect, etc.)   │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  ⏭️  Skip for Now                     │    │
│  │     (You can add later)               │    │
│  └───────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

### **Step 2: Wallet Setup**

#### **Option A: Create New Wallet (Recommended)**

```
┌─────────────────────────────────────────────────┐
│     Creating Your Web3 Wallet 🔐               │
│                                                 │
│  We're generating a secure wallet for you...   │
│                                                 │
│  ✅ Wallet created!                            │
│  Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb │
│                                                 │
│  🔑 IMPORTANT: Save your recovery phrase       │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  1. ocean    2. forest   3. mountain  │    │
│  │  4. river    5. sunset   6. breeze    │    │
│  │  7. thunder  8. crystal  9. phoenix   │    │
│  │  10. dragon  11. wisdom  12. harmony  │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ⚠️  Write this down! You'll need it to       │
│     recover your wallet if you lose access.   │
│                                                 │
│  ☑️ I've saved my recovery phrase              │
│                                                 │
│  [Continue] →                                  │
└─────────────────────────────────────────────────┘
```

#### **Option B: Connect Existing Wallet**

```
┌─────────────────────────────────────────────────┐
│     Connect Your Wallet 🔗                     │
│                                                 │
│  Choose your wallet:                           │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  🦊 MetaMask                          │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  🌈 Rainbow Wallet                    │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  🔗 WalletConnect                     │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  💼 Coinbase Wallet                   │    │
│  └───────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

### **Step 3: Token Rewards Dashboard**

```
┌─────────────────────────────────────────────────┐
│          Your Token Rewards 🪙                  │
│                                                 │
│  Wallet: 0x742d...0bEb                         │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  💾 Filecoin (FIL)                    │    │
│  │  Balance: 0.0234 FIL ($5.67)          │    │
│  │  Earned this month: +0.0015 FIL       │    │
│  │  Source: Data storage rewards         │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  ⚡ TFUEL                              │    │
│  │  Balance: 12.45 TFUEL ($3.12)         │    │
│  │  Earned this month: +2.5 TFUEL        │    │
│  │  Source: GPU compute rewards          │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  🐢 WTF Coin                          │    │
│  │  Balance: 150 WTF ($15.00)            │    │
│  │  Earned this month: +25 WTF           │    │
│  │  Source: Auto-converted from rewards  │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  Total Value: $23.79                           │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │  ⚙️ Auto-Convert Settings             │    │
│  │  ☑️ Convert FIL to WTF automatically  │    │
│  │  ☑️ Convert TFUEL to WTF automatically│    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  [Claim Rewards] [Withdraw] [Settings]        │
└─────────────────────────────────────────────────┘
```

---

## 💰 **How Users Earn Tokens:**

### **1. Filecoin (FIL) - Storage Rewards**

**What:** Users earn FIL for storing their data on Filecoin network

**How it works:**
```python
# User uploads document to Atlas
document = upload_document("Q3_Strategy.pdf")

# Atlas stores on Filecoin
cid = await filecoin.upload(document)

# Filecoin network pays storage rewards
# Rewards go to user's wallet (not platform)
reward = {
    "token": "FIL",
    "amount": 0.0001,  # ~$0.024
    "reason": "storage_provider_reward",
    "cid": cid,
    "size_mb": 5
}

# Credit user's wallet
await wallet.credit(user_wallet_address, reward)
```

**Earning rate:**
- Storage: ~$0.005 per GB per month
- User stores 10GB: ~$0.05/month in FIL
- Platform subsidizes first 10GB

---

### **2. TFUEL - GPU Compute Rewards**

**What:** Users earn TFUEL for using Theta EdgeCloud for AI training

**How it works:**
```python
# User's model trains on Theta GPU
training_job = await theta.submit_training(
    model_id="atlas:email:user123",
    training_data_cid="QmXxxx...",
    gpu_hours=2
)

# Theta network pays compute rewards
# Rewards go to user's wallet
reward = {
    "token": "TFUEL",
    "amount": 0.5,  # ~$0.125
    "reason": "edge_compute_reward",
    "job_id": training_job.id,
    "gpu_hours": 2
}

# Credit user's wallet
await wallet.credit(user_wallet_address, reward)
```

**Earning rate:**
- Compute: ~0.25 TFUEL per GPU hour
- User trains 4x/month: ~1 TFUEL/month (~$0.25)
- Platform subsidizes training costs

---

### **3. WTF Coin - Platform Utility Token**

**What:** Platform's native token, earned through auto-conversion or platform usage

**How it works:**
```python
# Option 1: Auto-convert from FIL/TFUEL
if user.settings.auto_convert_to_wtf:
    # Convert FIL to WTF
    fil_balance = await wallet.get_balance(user, "FIL")
    wtf_amount = await delt.swap(
        from_token="FIL",
        to_token="WTF",
        amount=fil_balance
    )
    
    # Credit WTF
    await wallet.credit(user_wallet_address, {
        "token": "WTF",
        "amount": wtf_amount,
        "reason": "auto_convert_from_FIL"
    })

# Option 2: Earn directly through platform usage
# - Referrals: 10 WTF per referral
# - Contributions: WTF for sharing knowledge
# - Staking: Earn yield on staked WTF
```

**WTF Utility:**
- Trading fee discounts on Delt (50% off with WTF)
- Premium features unlock
- Governance voting rights
- Staking rewards (5% APY)

---

## 🔧 **Technical Implementation:**

### **Backend: Wallet Service**

```python
# Apollo/wallet/wallet_service.py

class WalletService:
    """Manages user Web3 wallets and token rewards"""
    
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(ETHEREUM_RPC))
        self.filecoin_client = FilecoinClient()
        self.theta_client = ThetaClient()
        self.delt_exchange = DeltExchange()
    
    async def create_wallet(self, user_id: str) -> Dict:
        """Create new Web3 wallet for user"""
        
        # Generate new wallet
        account = self.web3.eth.account.create()
        
        # Encrypt private key
        encrypted_key = encrypt(
            account.key,
            user_password  # User's password
        )
        
        # Store encrypted key
        await self.db.store({
            "user_id": user_id,
            "wallet_address": account.address,
            "encrypted_key": encrypted_key,
            "created_at": datetime.utcnow()
        })
        
        return {
            "address": account.address,
            "mnemonic": account.mnemonic  # Show once, user must save
        }
    
    async def connect_wallet(
        self,
        user_id: str,
        wallet_address: str,
        signature: str
    ) -> bool:
        """Connect existing wallet via signature verification"""
        
        # Verify signature
        message = f"Connect wallet to Atlas: {user_id}"
        recovered_address = self.web3.eth.account.recover_message(
            message,
            signature=signature
        )
        
        if recovered_address.lower() != wallet_address.lower():
            raise ValueError("Invalid signature")
        
        # Store wallet connection
        await self.db.store({
            "user_id": user_id,
            "wallet_address": wallet_address,
            "connected_at": datetime.utcnow()
        })
        
        return True
    
    async def credit_storage_reward(
        self,
        user_id: str,
        cid: str,
        size_mb: float
    ):
        """Credit FIL for data storage"""
        
        # Calculate reward
        # Filecoin pays ~$0.005 per GB per month
        reward_fil = (size_mb / 1000) * 0.005 / 30  # Daily rate
        
        # Get user's wallet
        wallet = await self.get_user_wallet(user_id)
        
        # Credit FIL
        await self.credit_token(
            wallet_address=wallet.address,
            token="FIL",
            amount=reward_fil,
            metadata={
                "reason": "storage_reward",
                "cid": cid,
                "size_mb": size_mb
            }
        )
        
        # Auto-convert if enabled
        if wallet.auto_convert_fil:
            await self.auto_convert_to_wtf(wallet, "FIL", reward_fil)
    
    async def credit_compute_reward(
        self,
        user_id: str,
        job_id: str,
        gpu_hours: float
    ):
        """Credit TFUEL for GPU compute"""
        
        # Calculate reward
        # Theta pays ~0.25 TFUEL per GPU hour
        reward_tfuel = gpu_hours * 0.25
        
        # Get user's wallet
        wallet = await self.get_user_wallet(user_id)
        
        # Credit TFUEL
        await self.credit_token(
            wallet_address=wallet.address,
            token="TFUEL",
            amount=reward_tfuel,
            metadata={
                "reason": "compute_reward",
                "job_id": job_id,
                "gpu_hours": gpu_hours
            }
        )
        
        # Auto-convert if enabled
        if wallet.auto_convert_tfuel:
            await self.auto_convert_to_wtf(wallet, "TFUEL", reward_tfuel)
    
    async def auto_convert_to_wtf(
        self,
        wallet: Wallet,
        from_token: str,
        amount: float
    ):
        """Auto-convert tokens to WTF on Delt"""
        
        # Swap on Delt exchange
        wtf_amount = await self.delt_exchange.swap(
            from_token=from_token,
            to_token="WTF",
            amount=amount,
            wallet_address=wallet.address
        )
        
        # Credit WTF
        await self.credit_token(
            wallet_address=wallet.address,
            token="WTF",
            amount=wtf_amount,
            metadata={
                "reason": "auto_convert",
                "from_token": from_token,
                "from_amount": amount
            }
        )
        
        return wtf_amount
    
    async def get_balance(
        self,
        user_id: str,
        token: str
    ) -> float:
        """Get user's token balance"""
        
        wallet = await self.get_user_wallet(user_id)
        
        if token == "FIL":
            return await self.filecoin_client.get_balance(wallet.address)
        elif token == "TFUEL":
            return await self.theta_client.get_balance(wallet.address)
        elif token == "WTF":
            return await self.delt_exchange.get_balance(wallet.address, "WTF")
        else:
            raise ValueError(f"Unsupported token: {token}")
```

---

### **Frontend: Wallet Integration**

```typescript
// Atlas/frontend/mobile/hooks/useWallet.ts

export function useWallet() {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [balances, setBalances] = useState<TokenBalances>({});
  
  // Create new wallet
  const createWallet = async () => {
    const response = await fetch('/api/wallet/create', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    // Show mnemonic to user (ONCE)
    Alert.alert(
      'Save Your Recovery Phrase',
      data.mnemonic,
      [{ text: 'I\'ve Saved It', onPress: () => setWallet(data) }]
    );
  };
  
  // Connect existing wallet
  const connectWallet = async (provider: 'metamask' | 'walletconnect') => {
    if (provider === 'metamask') {
      // MetaMask integration
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });
      
      const address = accounts[0];
      
      // Sign message to verify ownership
      const message = `Connect wallet to Atlas: ${userId}`;
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, address]
      });
      
      // Verify on backend
      await fetch('/api/wallet/connect', {
        method: 'POST',
        body: JSON.stringify({ address, signature })
      });
      
      setWallet({ address });
    }
  };
  
  // Get balances
  const refreshBalances = async () => {
    const response = await fetch('/api/wallet/balances');
    const data = await response.json();
    setBalances(data);
  };
  
  // Auto-convert settings
  const setAutoConvert = async (token: string, enabled: boolean) => {
    await fetch('/api/wallet/settings', {
      method: 'PUT',
      body: JSON.stringify({
        [`auto_convert_${token.toLowerCase()}`]: enabled
      })
    });
  };
  
  return {
    wallet,
    balances,
    createWallet,
    connectWallet,
    refreshBalances,
    setAutoConvert
  };
}
```

---

## 📊 **Reward Economics:**

### **Monthly Earnings Example:**

**Active User (Personal Tier):**
```
Storage (10GB data):
├─ Filecoin rewards: 0.002 FIL (~$0.05)
└─ Auto-convert to WTF: 5 WTF

AI Training (4x/month):
├─ Theta rewards: 1 TFUEL (~$0.25)
└─ Auto-convert to WTF: 25 WTF

Platform Usage:
├─ Referral bonus: 10 WTF
└─ Knowledge sharing: 10 WTF

Total: 50 WTF (~$5.00/month)
```

**Team User (Team Tier):**
```
Storage (50GB team data):
├─ Filecoin rewards: 0.01 FIL (~$0.25)
└─ Auto-convert to WTF: 25 WTF

AI Training (8x/month):
├─ Theta rewards: 2 TFUEL (~$0.50)
└─ Auto-convert to WTF: 50 WTF

Platform Usage:
├─ Team referrals: 50 WTF
└─ Knowledge contributions: 25 WTF

Total: 150 WTF (~$15.00/month)
```

---

## 🎯 **User Benefits:**

### **1. Data Ownership**
- ✅ User owns their wallet
- ✅ User owns their data (on Filecoin)
- ✅ User owns their models
- ✅ User can export everything

### **2. Earn While You Use**
- ✅ Get paid for data storage
- ✅ Get paid for AI compute
- ✅ Passive income from platform usage

### **3. WTF Utility**
- ✅ 50% trading fee discount on Delt
- ✅ Premium features unlock
- ✅ Governance voting
- ✅ Staking rewards (5% APY)

### **4. True Web3**
- ✅ Non-custodial (user controls keys)
- ✅ Decentralized storage (Filecoin)
- ✅ Decentralized compute (Theta)
- ✅ User sovereignty

---

## ✅ **Implementation Checklist:**

- [ ] Create wallet service (backend)
- [ ] Integrate MetaMask/WalletConnect
- [ ] Filecoin reward tracking
- [ ] Theta reward tracking
- [ ] WTF token contract
- [ ] Delt exchange integration
- [ ] Auto-convert functionality
- [ ] Rewards dashboard UI
- [ ] Wallet onboarding flow
- [ ] Recovery phrase backup
- [ ] Token withdrawal
- [ ] Staking system

---

**Created:** October 27, 2025  
**Version:** 1.0.0  
**Status:** WEB3 REWARDS SYSTEM DESIGNED ✅
