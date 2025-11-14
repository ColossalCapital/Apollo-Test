# 📧 Gmail OAuth Setup Guide

## Overview

Set up Gmail OAuth to enable:
- Email ingestion into knowledge base
- Entity extraction from emails
- Auto-categorization and tagging
- Multi-tenant email isolation

---

## 🔐 Step 1: Create Google Cloud Project

### **1.1 Go to Google Cloud Console**
```
https://console.cloud.google.com/
```

### **1.2 Create New Project**
1. Click "Select a project" → "New Project"
2. Name: "Apollo AI - Email Intelligence"
3. Click "Create"

### **1.3 Enable Gmail API**
1. Go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable"

---

## 🔑 Step 2: Create OAuth Credentials

### **2.1 Configure OAuth Consent Screen**
1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" (or "Internal" if G Suite)
3. Fill in:
   - App name: "Apollo AI"
   - User support email: your@email.com
   - Developer contact: your@email.com
4. Click "Save and Continue"

### **2.2 Add Scopes**
1. Click "Add or Remove Scopes"
2. Add these scopes:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.modify
   https://www.googleapis.com/auth/gmail.labels
   ```
3. Click "Save and Continue"

### **2.3 Add Test Users (if External)**
1. Add your email as test user
2. Click "Save and Continue"

### **2.4 Create OAuth Client ID**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Web application"
4. Name: "Apollo Gmail Connector"
5. Authorized redirect URIs:
   ```
   http://localhost:8002/api/gmail/oauth/callback
   https://your-domain.com/api/gmail/oauth/callback
   ```
6. Click "Create"
7. **Save the Client ID and Client Secret!**

---

## 🔧 Step 3: Configure Apollo

### **3.1 Add to .env**
```bash
# Gmail OAuth
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:8002/api/gmail/oauth/callback

# Theta RAG for email storage
THETA_API_KEY=your-theta-api-key
```

### **3.2 Install Dependencies**
```bash
cd Apollo
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 📊 Step 4: Intelligence Hub Configuration

### **4.1 Multi-Tenant Knowledge Base Structure**

```
Theta RAG Chatbots (per entity):
├── email_{entity_id}_{org_id}
│   ├── Emails (raw + parsed)
│   ├── Entities (people, companies)
│   ├── Topics (projects, deals)
│   └── Relationships
├── documents_{entity_id}_{org_id}
│   ├── PDFs
│   ├── Word docs
│   ├── Images (OCR)
│   └── Spreadsheets
└── codebase_{entity_id}_{org_id}
    ├── Source files
    ├── Functions/Classes
    ├── Dependencies
    └── Documentation
```

### **4.2 Privacy Isolation**

```python
# Each entity gets separate Theta RAG chatbot
entity_chatbots = {
    "user_123": {
        "email": "theta_rag_chatbot_abc123",
        "documents": "theta_rag_chatbot_def456",
        "codebase": "theta_rag_chatbot_ghi789"
    },
    "user_456": {
        "email": "theta_rag_chatbot_jkl012",
        "documents": "theta_rag_chatbot_mno345",
        "codebase": "theta_rag_chatbot_pqr678"
    }
}

# Data never mixes between entities
# Queries only access entity's own chatbots
```

---

## 🚀 Step 5: Test OAuth Flow

### **5.1 Start Apollo**
```bash
cd Apollo
python -m uvicorn api.main:app --reload --port 8002
```

### **5.2 Initiate OAuth**
```bash
# Open in browser
http://localhost:8002/api/gmail/oauth/authorize?entity_id=user_123
```

### **5.3 Grant Permissions**
1. Select your Google account
2. Click "Allow" for Gmail access
3. You'll be redirected back to Apollo
4. Access token saved for entity

### **5.4 Test Email Fetch**
```bash
curl http://localhost:8002/api/gmail/fetch?entity_id=user_123&max_results=10
```

---

## 📥 Step 6: Email Ingestion Flow

### **6.1 Automatic Ingestion**

```python
# Apollo automatically:
1. Fetches new emails every 5 minutes
2. Parses email content
3. Extracts entities (people, companies, dates)
4. Detects topics and categories
5. Creates embeddings
6. Stores in Theta RAG
7. Makes searchable via AI
```

### **6.2 Entity Extraction**

```python
Email: "Meeting with John Smith from Acme Corp on Tuesday"

Extracted:
- Person: John Smith
- Company: Acme Corp
- Date: Tuesday (next Tuesday)
- Intent: Meeting
- Action: Schedule

Stored in Knowledge Base:
- Entity: John Smith (works_at: Acme Corp)
- Event: Meeting (with: John Smith, when: Tuesday)
- Relationship: user ↔ John Smith ↔ Acme Corp
```

### **6.3 Query Examples**

```python
# Natural language queries to Theta RAG

"What emails did I get from Acme Corp?"
→ Returns all emails from Acme Corp employees

"When is my next meeting with John?"
→ Finds meeting in calendar + email context

"What projects am I working on?"
→ Analyzes email topics and extracts projects

"Who do I know at Acme Corp?"
→ Lists all people from Acme Corp in emails
```

---

## 🗄️ Step 7: Document Upload to Knowledge Base

### **7.1 Upload API**

```python
POST /api/intelligence/upload
{
  "entity_id": "user_123",
  "org_id": "org_1",
  "file": <binary>,
  "file_type": "pdf",
  "privacy": "personal"
}
```

### **7.2 Supported File Types**

```python
Documents:
- PDF → Text extraction + OCR
- Word (.docx) → Text extraction
- Excel (.xlsx) → Table parsing
- PowerPoint (.pptx) → Slide text

Images:
- PNG, JPG → OCR with Tesseract
- Screenshots → Text extraction

Code:
- Python, TypeScript, Rust, etc.
- Automatic syntax parsing
```

### **7.3 Processing Pipeline**

```python
File Upload
  ↓
Extract Text/Data
  ↓
Parse Entities
  ↓
Create Embeddings
  ↓
Store in Theta RAG
  ↓
Available for AI Queries
```

---

## 🔍 Step 8: Query Intelligence Hub

### **8.1 Unified Query API**

```python
POST /api/intelligence/query
{
  "entity_id": "user_123",
  "query": "What are the key points from the Acme Corp proposal?",
  "sources": ["email", "documents", "codebase"],
  "max_results": 5
}
```

### **8.2 Response**

```json
{
  "answer": "The Acme Corp proposal includes: 1) $500K contract, 2) 6-month timeline, 3) Integration with existing systems",
  "sources": [
    {
      "type": "email",
      "from": "john@acmecorp.com",
      "date": "2025-10-15",
      "snippet": "We're proposing a $500K contract..."
    },
    {
      "type": "document",
      "filename": "acme_proposal.pdf",
      "page": 3,
      "snippet": "Timeline: 6 months from contract signing..."
    }
  ],
  "confidence": 0.95
}
```

---

## 🎯 Step 9: Multi-Tenant Isolation

### **9.1 Entity Hierarchy**

```
Organization (org_1)
├── Team 1
│   ├── User 1 → email_chatbot_1, docs_chatbot_1
│   └── User 2 → email_chatbot_2, docs_chatbot_2
└── Team 2
    ├── User 3 → email_chatbot_3, docs_chatbot_3
    └── User 4 → email_chatbot_4, docs_chatbot_4
```

### **9.2 Access Control**

```python
# User can only query their own chatbots
user_1_query → email_chatbot_1 + docs_chatbot_1 ✅
user_1_query → email_chatbot_2 ❌ (different user)

# Org admin can query all org chatbots
org_admin_query → all org_1 chatbots ✅
org_admin_query → org_2 chatbots ❌ (different org)
```

### **9.3 Privacy Levels**

```python
Personal:
- Only user can access
- Not shared with team/org

Team:
- Team members can access
- Not shared with other teams

Org:
- All org members can access
- Not shared with other orgs

Public:
- Anyone can access
```

---

## ✅ Complete Setup Checklist

- [ ] Create Google Cloud Project
- [ ] Enable Gmail API
- [ ] Configure OAuth consent screen
- [ ] Create OAuth credentials
- [ ] Add credentials to Apollo .env
- [ ] Install Python dependencies
- [ ] Start Apollo server
- [ ] Test OAuth flow
- [ ] Verify email fetch
- [ ] Test entity extraction
- [ ] Upload test document
- [ ] Query knowledge base
- [ ] Verify multi-tenant isolation

---

## 🚀 Next Steps

Once Gmail OAuth is set up:

1. **Auto-ingestion:** Emails automatically indexed every 5 minutes
2. **Entity tracking:** People, companies, projects extracted
3. **Smart search:** Natural language queries across all data
4. **Workflow automation:** Auto-create tasks from emails
5. **Knowledge graph:** Relationships between entities

**Cost:** ~$0.05/month per user in TFUEL (Theta RAG storage)

---

**Your emails, documents, and code are now searchable with AI!** 📧🧠
