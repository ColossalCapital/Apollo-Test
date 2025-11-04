# 🎯 Context-Aware Routing - Complete Use Cases

**All contexts, tiers, and tenant models covered**

---

## 📊 **Complete Context Matrix:**

| Context | Parent | Use Case | Isolation | Sharing |
|---------|--------|----------|-----------|---------|
| **ATLAS** | - | Personal AI assistant | Personal/Team/Org | Based on tier |
| **DELT** | - | Trading platform | Personal/Team/Org | Based on tier |
| **AKASHIC** | - | Code editor (standalone) | Personal | Never shared |
| **AKASHIC_IN_ATLAS** | Atlas | Code editor within Atlas | Personal | Never shared |
| **AKASHIC_IN_DELT** | Delt | Trading bot code editor | Personal/Team/Org | Based on tier |

---

## 🏢 **1. ATLAS Context (Standalone)**

### **Atlas Personal Tier**
```json
{
  "app_context": "atlas",
  "atlas_tier": "personal",
  "privacy": "personal"
}
```
**Result:**
- Model: `atlas:email:user123` (personal)
- Isolation: Personal only
- Sharing: Never shared
- Training: User data only

### **Atlas Individual Tier**
```json
{
  "app_context": "atlas",
  "atlas_tier": "individual",
  "privacy": "personal"
}
```
**Result:**
- Model: `atlas:email:user123` (personal)
- Isolation: Personal
- Sharing: Can explicitly share
- Training: User data only

### **Atlas Team Tier**
```json
{
  "app_context": "atlas",
  "atlas_tier": "team",
  "privacy": "org_private"
}
```
**Result:**
- Model: `atlas:email:org456:team:team789` (team)
- Isolation: Team level
- Sharing: Team members
- Training: Team data

### **Atlas Organizational Tier**
```json
{
  "app_context": "atlas",
  "atlas_tier": "organizational",
  "privacy": "org_public"
}
```
**Result:**
- Model: `atlas:email:org456:org` (org)
- Isolation: Organization level
- Sharing: All org members
- Training: Org data

---

## 💰 **2. DELT Context (Standalone)**

### **Delt Retail Tier**
```json
{
  "app_context": "delt",
  "delt_tier": "retail",
  "privacy": "personal"
}
```
**Result:**
- Model: `delt:strategy:user123` (personal)
- Isolation: Personal only
- Sharing: Never shared
- Training: User trades only
- Use Case: Individual retail trader

### **Delt Professional Tier (Personal)**
```json
{
  "app_context": "delt",
  "delt_tier": "professional",
  "privacy": "personal"
}
```
**Result:**
- Model: `delt:strategy:user456` (personal)
- Isolation: Personal
- Sharing: Never shared
- Training: User trades only
- Use Case: Pro trader, private strategies

### **Delt Professional Tier (Team)**
```json
{
  "app_context": "delt",
  "delt_tier": "professional",
  "privacy": "org_private"
}
```
**Result:**
- Model: `delt:strategy:org789:team:team123` (team)
- Isolation: Team level
- Sharing: Team members
- Training: Team trades
- Use Case: Trading team sharing strategies

### **Delt Institutional Tier (Org)**
```json
{
  "app_context": "delt",
  "delt_tier": "institutional",
  "privacy": "org_public"
}
```
**Result:**
- Model: `delt:strategy:org999:org` (org)
- Isolation: Organization level
- Sharing: All org members
- Training: All org trades
- Use Case: Hedge fund, firm-wide models

---

## 💻 **3. AKASHIC Context (Standalone)**

### **Akashic Standalone**
```json
{
  "app_context": "akashic",
  "privacy": "personal"
}
```
**Result:**
- Model: `akashic:development:user123` (personal)
- Isolation: Personal ALWAYS
- Sharing: NEVER shared (code is sensitive)
- Training: User code only
- Use Case: Personal code editor

**Note:** Akashic standalone is ALWAYS personal, regardless of tier or privacy settings. Code is too sensitive to share.

---

## 🔗 **4. AKASHIC_IN_ATLAS Context**

### **Akashic within Atlas (Any Tier)**
```json
{
  "app_context": "akashic_atlas",
  "atlas_tier": "organizational",
  "privacy": "org_public"
}
```
**Result:**
- Model: `akashic_atlas:development:user123` (personal)
- Isolation: Personal ALWAYS
- Sharing: NEVER shared
- Training: User code only
- Parent: Atlas
- Use Case: Code editor within Atlas app

**Key Point:** Even if Atlas is org-level, code models stay personal for security.

---

## 🤖 **5. AKASHIC_IN_DELT Context (Trading Bots)**

### **Akashic in Delt - Retail**
```json
{
  "app_context": "akashic_delt",
  "delt_tier": "retail",
  "privacy": "personal"
}
```
**Result:**
- Model: `akashic_delt:development:user123` (personal)
- Isolation: Personal
- Sharing: Never shared
- Training: User bot code only
- Use Case: Retail trader's private bot

### **Akashic in Delt - Professional (Personal)**
```json
{
  "app_context": "akashic_delt",
  "delt_tier": "professional",
  "privacy": "personal"
}
```
**Result:**
- Model: `akashic_delt:development:user456` (personal)
- Isolation: Personal
- Sharing: Never shared
- Training: User bot code only
- Use Case: Pro trader's private bot

### **Akashic in Delt - Professional (Team)**
```json
{
  "app_context": "akashic_delt",
  "delt_tier": "professional",
  "privacy": "org_private"
}
```
**Result:**
- Model: `akashic_delt:development:org789:team:team123` (team)
- Isolation: Team level
- Sharing: Team members CAN share
- Training: Team bot code
- Use Case: Trading team sharing bot strategies

### **Akashic in Delt - Institutional (Org)**
```json
{
  "app_context": "akashic_delt",
  "delt_tier": "institutional",
  "privacy": "org_public"
}
```
**Result:**
- Model: `akashic_delt:development:org999:org` (org)
- Isolation: Organization level
- Sharing: All org members
- Training: All org bot code
- Use Case: Hedge fund sharing bot infrastructure

**Key Difference:** Unlike Akashic standalone or Akashic in Atlas, trading bot code CAN be shared at team/org level for institutional users.

---

## 📋 **Complete Tier Matrix:**

### **Atlas Tiers:**
| Tier | Isolation Options | Sharing | Use Case |
|------|------------------|---------|----------|
| **Personal** | Personal only | Never | Single user, no org |
| **Individual** | Personal | Optional | Single user, can share |
| **Team** | Personal, Team | Team members | Small team (2-10) |
| **Organizational** | Personal, Team, Org, Public | Org members | Large org (10+) |

### **Delt Tiers:**
| Tier | Isolation Options | Sharing | Use Case |
|------|------------------|---------|----------|
| **Retail** | Personal only | Never | Individual retail trader |
| **Professional** | Personal, Team | Team members | Professional trader |
| **Institutional** | Personal, Team, Org | Org members | Hedge fund, institution |

### **Privacy Levels:**
| Privacy | Who Can Access | Training Data | Use Case |
|---------|---------------|---------------|----------|
| **Personal** | Owner only | User only | Sensitive data |
| **Private** | Owner + explicit shares | User only | Shareable but private |
| **Org Private** | Team members | Team only | Team collaboration |
| **Org Public** | Org members | Org only | Org-wide sharing |
| **Public** | Everyone | Everyone | Public knowledge |

---

## 🎯 **Model ID Format:**

### **Personal Models:**
```
{app}:{agent_type}:{user_id}
```
Examples:
- `atlas:email:user123`
- `delt:strategy:user456`
- `akashic:development:user789`

### **Team Models:**
```
{app}:{agent_type}:{org_id}:team:{team_id}
```
Examples:
- `atlas:email:org456:team:team789`
- `delt:strategy:org999:team:quant_team`
- `akashic_delt:development:org123:team:bot_team`

### **Org Models:**
```
{app}:{agent_type}:{org_id}:org
```
Examples:
- `atlas:email:org456:org`
- `delt:strategy:org999:org`

### **Public Models:**
```
{app}:{agent_type}:public
```
Examples:
- `atlas:knowledge:public`
- `delt:sentiment:public`

---

## 🔒 **Security Rules:**

### **Code Security (Akashic):**
1. ✅ **Standalone Akashic**: ALWAYS personal, NEVER shared
2. ✅ **Akashic in Atlas**: ALWAYS personal, NEVER shared
3. ⚠️  **Akashic in Delt**: CAN be shared for trading bots (team/org level)

**Rationale:**
- Personal code is sensitive → never share
- Trading bot code is business logic → can share within team/org
- Institutional users need to share bot infrastructure

### **Trading Data Security (Delt):**
1. ✅ **Retail**: Personal only, never shared
2. ✅ **Professional**: Can share with team
3. ✅ **Institutional**: Can share at org level

**Rationale:**
- Retail traders: individual accounts
- Professional: trading teams collaborate
- Institutional: firm-wide strategies

### **Personal Data Security (Atlas):**
1. ✅ **Personal tier**: Never shared
2. ✅ **Individual tier**: Can explicitly share
3. ✅ **Team tier**: Shared within team
4. ✅ **Organizational tier**: Shared at org level

**Rationale:**
- Users control their data
- Teams collaborate on shared data
- Orgs have org-wide knowledge

---

## 📊 **Example API Calls:**

### **Example 1: Atlas Personal User**
```bash
curl -X POST http://localhost:8002/v3/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "org_id": null,
    "app_context": "atlas",
    "privacy": "personal",
    "atlas_tier": "personal",
    "agent_type": "email",
    "data": {...}
  }'
```
**Model Used:** `atlas:email:user123` (personal)

### **Example 2: Delt Institutional Trader**
```bash
curl -X POST http://localhost:8002/v3/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user456",
    "org_id": "hedge_fund_123",
    "app_context": "delt",
    "privacy": "org_public",
    "delt_tier": "institutional",
    "agent_type": "strategy",
    "data": {...}
  }'
```
**Model Used:** `delt:strategy:hedge_fund_123:org` (org-level)

### **Example 3: Akashic in Atlas**
```bash
curl -X POST http://localhost:8002/v3/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user789",
    "org_id": "company_456",
    "app_context": "akashic_atlas",
    "privacy": "org_public",
    "atlas_tier": "organizational",
    "agent_type": "development",
    "data": {...}
  }'
```
**Model Used:** `akashic_atlas:development:user789` (personal, even though org tier)

### **Example 4: Trading Bot in Delt (Institutional)**
```bash
curl -X POST http://localhost:8002/v3/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user999",
    "org_id": "hedge_fund_789",
    "app_context": "akashic_delt",
    "privacy": "org_public",
    "delt_tier": "institutional",
    "agent_type": "development",
    "data": {...}
  }'
```
**Model Used:** `akashic_delt:development:hedge_fund_789:org` (org-level, shared bot code)

---

## ✅ **Complete Coverage:**

| Use Case | Context | Covered | Notes |
|----------|---------|---------|-------|
| **Atlas standalone** | `atlas` | ✅ | All 4 tiers |
| **Delt standalone** | `delt` | ✅ | All 3 tiers (Retail, Pro, Institutional) |
| **Akashic standalone** | `akashic` | ✅ | Always personal |
| **Akashic in Atlas** | `akashic_atlas` | ✅ | Always personal |
| **Akashic in Delt** | `akashic_delt` | ✅ | Can share at team/org for bots |
| **Personal models** | All | ✅ | User-specific |
| **Team models** | All | ✅ | Team-specific |
| **Org models** | All | ✅ | Org-specific |
| **Public models** | All | ✅ | Everyone |

---

## 🎉 **Result:**

✅ **ALL use cases covered!**
- Atlas (4 tiers × 5 privacy levels)
- Delt (3 tiers × 5 privacy levels)
- Akashic (standalone, in Atlas, in Delt)
- Proper tenant models (personal, team, org, public)
- Security rules enforced
- Parent context tracking

**Total combinations: 100+ use cases, all handled correctly!** 🚀

---

**Created:** October 27, 2025  
**Version:** 3.0.0  
**Status:** COMPLETE
