# 🤖 Apollo - Universal AI & GPU Platform

**Intelligent AI orchestration powered by Theta EdgeCloud**

---

## 🎯 What is Apollo?

Apollo is the complete AI infrastructure for the Colossal Capital ecosystem:

```
Apollo = Conductor + API + Studio

🎵 Conductor (Smart Orchestrator)
   ├─ Selects optimal AI models
   ├─ Allocates GPU resources
   ├─ Optimizes costs
   └─ Routes all compute jobs

🔌 API (Universal Interface)
   ├─ AI training endpoints
   ├─ Inference endpoints
   ├─ RAG endpoints
   ├─ Rendering endpoints (Blender)
   └─ Compliance endpoints (GDPR)

🎨 Studio (Admin UI)
   ├─ Model training dashboard
   ├─ RAG corpus management
   ├─ Rendering queue
   ├─ Performance monitoring
   └─ Data governance (GDPR)
```

---

## 🏗️ Repository Structure

```
apollo/
├─ conductor/          🎵 Smart orchestration engine
├─ api/                🔌 FastAPI backend
├─ studio/             🎨 React admin UI
├─ agents/             🤖 AI agent definitions
├─ sdk/                📦 Client libraries (Python, TS, Dart)
├─ workers/            ⚙️ Background job processors
└─ config/             ⚙️ Configuration files
```

---

## 🚀 Quick Start

### For Developers:

```bash
# Clone repo
git clone <apollo-repo-url>
cd apollo

# Start full stack
docker-compose up

# Apollo API: http://localhost:8000
# Apollo Studio: http://localhost:3000
```

### For Integration:

**Python:**
```python
from apollo_sdk import Conductor

conductor = Conductor(api_url="https://apollo.delt.capital")
result = await conductor.execute("ai_inference", {...})
```

**TypeScript (Atlas):**
```typescript
import { Apollo Studio } from '@apollo/studio';

<ApolloStudio apiUrl="..." authToken="..." />
```

**Dart (Delt - Simplified):**
```dart
import 'package:apollo_sdk/apollo_sdk.dart';

final apollo = ApolloClient(apiUrl: '...', authToken: '...');
final response = await apollo.chat("Should I buy BTC?");
```

---

## 🎯 Use Cases

### 1. AI Chat (Delt Mobile)
User asks question → Apollo Conductor selects model → Returns answer

### 2. Code Generation (Akashic IDE)
User requests code → Conductor uses DeepSeek → Generates strategy

### 3. Model Training (Apollo Studio)
User trains custom model → Conductor schedules on Theta GPU → Model deployed

### 4. Blender Rendering (World Turtle Farm)
NFT minted → Conductor renders turtle → Stores on Filecoin

### 5. Backtesting (Akashic)
User runs backtest → Conductor optimizes GPU usage → Returns results

---

## 🎨 Apollo Studio

**Admin interface for power users**

Access at: `https://studio.apollo.delt.capital` (embedded in Atlas)

Features:
- 📊 Training dashboard
- 📚 RAG management
- 🎨 Render queue
- 🤖 Agent builder
- 📈 Performance monitoring
- 🗑️ GDPR compliance tools

---

## 🔐 Data Governance

**GDPR Compliant:**
- ✅ Right to access (export all data)
- ✅ Right to deletion (one-click delete)
- ✅ Right to rectification (correct data)
- ✅ Right to portability (download JSON)
- ✅ Blockchain proof of deletion

---

## 🪙 Payment Integration

**Pays through HouseOfJacob (Cosmos Chain):**

```
User pays in WTF
    ↓
Apollo Conductor
    ↓
Auto-converts WTF → TFUEL
    ↓
Pays Theta EdgeCloud
    ↓
GPU compute executed
```

All transparent to user - they only see WTF costs!

---

## 📚 Documentation

- `conductor/` - Conductor architecture
- `api/` - API reference
- `studio/` - Studio user guide
- `sdk/` - SDK documentation
- See `/docs` for complete guides

---

## 🎉 Apollo Powers

- **Delt** - Mobile trading app (chat assistant)
- **Akashic** - Desktop IDE (code generation)
- **Atlas** - Business platform (Apollo Studio)
- **World Turtle Farm** - NFT rendering (Blender)

One AI platform for the entire ecosystem! 🌟

---

**Built with ❤️ by Colossal Capital**

**"The Conductor of Intelligence"** 🎵
