# 🔌 WebSocket Monitoring Guide

## Overview

The APIDocsWatcherAgent now monitors **both REST APIs and WebSocket APIs** for all exchange connectors. This is critical because all AckwardRootsInc connectors subscribe to WebSocket data feeds for real-time market data.

---

## 🎯 Why WebSocket Monitoring Matters

### **Real-Time Data Feeds**
All exchange connectors use WebSocket connections for:
- **Ticker data** - Real-time price updates
- **Trade executions** - Live trade feed
- **Order book updates** - Bid/ask changes
- **Liquidations** - Liquidation events
- **Funding rates** - Perpetual funding rates

### **Breaking Changes**
WebSocket APIs change frequently:
- New channels added (e.g., "liquidations_v2")
- Old channels deprecated
- Message formats change (new fields, type changes)
- Authentication methods updated
- Rate limits adjusted

---

## 📊 What We Monitor

### **1. Channel Changes**
```python
changes = {
    "new_ws_channels": ["liquidations", "funding_rate"],
    "removed_ws_channels": ["depth_old"],
    "modified_ws_channels": ["orderbook"]
}
```

**Example:**
- Binance adds new "liquidations" channel
- Watcher detects it
- Regenerates connector with new channel support
- Users automatically get liquidation data

### **2. Message Format Changes**
```python
changes = {
    "ws_message_format_changes": ["ticker", "trades"]
}
```

**Example:**
```json
// Old ticker format
{
  "symbol": "BTC-USD",
  "price": 50000
}

// New ticker format (added volume)
{
  "symbol": "BTC-USD",
  "price": 50000,
  "volume": 1.5  // NEW FIELD
}
```

### **3. Authentication Changes**
```python
changes = {
    "auth_changes": True
}
```

**Example:**
- Coinbase switches from API key to JWT tokens
- Watcher detects auth change
- Regenerates connector with new auth
- Users' connections continue working

### **4. Rate Limit Changes**
```python
changes = {
    "rate_limit_changes": True
}
```

**Example:**
- Kraken reduces WebSocket message rate from 100/sec to 50/sec
- Watcher detects change
- Regenerates connector with new rate limiting
- Prevents connection drops

### **5. Subscription Pattern Changes**
```python
# Old subscription
{
  "type": "subscribe",
  "channels": ["ticker"]
}

# New subscription (added product_ids)
{
  "type": "subscribe",
  "channels": ["ticker"],
  "product_ids": ["BTC-USD"]  // NEW REQUIRED FIELD
}
```

---

## 🔄 Auto-Update Flow

```
1. Exchange updates WebSocket API docs
   ↓
2. APIDocsWatcherAgent detects change (hourly check)
   ↓
3. Compares old vs new WebSocket spec
   ↓
4. Detects: 2 new channels, 1 message format change
   ↓
5. Triggers ConnectorGeneratorAgent
   ↓
6. Generates new Rust code with updated WebSocket handling
   ↓
7. Tests with cargo check
   ↓
8. Commits to /AckwardRootsInc/code/connectors/exchanges/{exchange}/
   ↓
9. Deploys new version
   ↓
10. Notifies users: "Coinbase connector updated: 2 new WS channels"
   ↓
11. Users' containers auto-restart with new version
   ↓
12. New data starts flowing immediately
```

---

## 📡 WebSocket Spec Structure

### **Connector Agent Method**
```python
async def get_websocket_spec(self) -> dict:
    """Fetch WebSocket API specification"""
    return {
        "url": "wss://ws-feed.exchange.com",
        "channels": {
            "ticker": {
                "description": "Real-time price updates",
                "subscription": {
                    "type": "subscribe",
                    "channels": ["ticker"],
                    "product_ids": ["BTC-USD"]
                },
                "message_format": {
                    "type": "ticker",
                    "product_id": "string",
                    "price": "number",
                    "volume": "number",
                    "time": "timestamp"
                }
            },
            "trades": {
                "description": "Live trade feed",
                "subscription": {
                    "type": "subscribe",
                    "channels": ["trades"]
                },
                "message_format": {
                    "type": "trade",
                    "product_id": "string",
                    "price": "number",
                    "size": "number",
                    "side": "buy|sell",
                    "time": "timestamp"
                }
            }
        },
        "auth": {
            "method": "api_key",
            "fields": ["api_key", "api_secret", "passphrase"]
        },
        "rate_limits": {
            "connections_per_ip": 10,
            "messages_per_second": 100,
            "subscriptions_per_connection": 50
        }
    }
```

---

## 🎯 Real-World Examples

### **Example 1: Binance Adds Liquidations Channel**

**Before:**
```python
channels = {
    "ticker": {...},
    "trades": {...},
    "orderbook": {...}
}
```

**After:**
```python
channels = {
    "ticker": {...},
    "trades": {...},
    "orderbook": {...},
    "liquidations": {  # NEW!
        "description": "Liquidation events",
        "subscription": {
            "type": "subscribe",
            "channels": ["liquidations"]
        },
        "message_format": {
            "type": "liquidation",
            "symbol": "string",
            "side": "buy|sell",
            "price": "number",
            "quantity": "number",
            "time": "timestamp"
        }
    }
}
```

**Watcher Output:**
```
🔍 Checking binance API...
   🚨 API changes detected for binance!
      1 new WS channels
   🤖 Triggering connector regeneration...
      REST changes: [] new, [] modified
      WebSocket changes: ['liquidations'] new, [] modified
   ✅ Connector regenerated successfully
      Version: 0.2.0
      Files: Cargo.toml, src/main.rs, src/models.rs, ...
   📧 Notifying users of binance update to v0.2.0
```

### **Example 2: Coinbase Changes Ticker Format**

**Old Format:**
```json
{
  "type": "ticker",
  "product_id": "BTC-USD",
  "price": "50000.00",
  "time": "2024-01-15T10:30:00Z"
}
```

**New Format:**
```json
{
  "type": "ticker",
  "product_id": "BTC-USD",
  "price": "50000.00",
  "volume_24h": "1234.56",  // NEW
  "best_bid": "49999.99",   // NEW
  "best_ask": "50000.01",   // NEW
  "time": "2024-01-15T10:30:00Z"
}
```

**Watcher Output:**
```
🔍 Checking coinbase API...
   🚨 API changes detected for coinbase!
      1 WS message format changes
   🤖 Triggering connector regeneration...
      REST changes: [] new, [] modified
      WebSocket changes: [] new, ['ticker'] modified
   ✅ Connector regenerated successfully
```

---

## 🚀 Benefits

### **1. Zero Downtime**
- Connectors auto-update without manual intervention
- Users never lose data

### **2. Always Current**
- Connectors always use latest API features
- No manual code updates needed

### **3. New Features Automatically**
- Exchange adds liquidation data → Users get it automatically
- Exchange adds funding rates → Users get it automatically

### **4. Breaking Changes Handled**
- Old channel deprecated → Connector switches to new channel
- Message format changes → Connector adapts automatically

### **5. World Turtle Farm Benefits**
- Real-time market data for NFT generation
- Multi-exchange aggregation
- Historical data in QuestDB
- Turtle metadata in MongoDB
- Autonomous connector updates
- Per-user data isolation

---

## 📊 Monitoring Dashboard

### **IntegrationDetailScreen Shows:**
```
┌─────────────────────────────────────────┐
│ Coinbase Connector                      │
├─────────────────────────────────────────┤
│ Status: ✅ Streaming                    │
│ Version: 0.2.0 (updated 2h ago)        │
│                                         │
│ WebSocket Channels:                     │
│ ✅ ticker       (15.3 msg/sec)         │
│ ✅ trades       (8.7 msg/sec)          │
│ ✅ orderbook    (12.1 msg/sec)         │
│ ✅ liquidations (0.3 msg/sec) NEW!     │
│                                         │
│ Data Flow:                              │
│ AckwardRootsInc → 36.4 msg/sec ✅      │
│ Kafka → 1,234 messages queued          │
│ Apollo → Processing 35.8 msg/sec ✅    │
│ Atlas → 127 entities created ✅        │
└─────────────────────────────────────────┘
```

---

## 🎉 Status

**100% COMPLETE!**

✅ REST API monitoring
✅ WebSocket channel monitoring
✅ WebSocket message format monitoring
✅ Auth change detection (REST + WebSocket)
✅ Rate limit change detection (REST + WebSocket)
✅ Autonomous regeneration
✅ User notifications
✅ World Turtle Farm integration

**The ultimate autonomous connector system with full WebSocket support!** 🚀
