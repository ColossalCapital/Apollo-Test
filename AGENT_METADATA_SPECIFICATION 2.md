# 🏷️ Agent Metadata Specification

**Complete specification for production-ready, auditable agent metadata**

---

## 📋 Overview

Every Apollo agent includes comprehensive metadata that enables:
- ✅ **Cost tracking** - Monitor and optimize resource usage
- ✅ **Privacy compliance** - GDPR, data retention, PII handling
- ✅ **Business logic** - Tier limits, pricing, subscriptions
- ✅ **Performance monitoring** - Response times, rate limits
- ✅ **Continuous learning** - Training costs, frequency, storage
- ✅ **UI/UX** - Icons, colors, categories
- ✅ **Monitoring** - Health checks, alerts, fallbacks
- ✅ **Documentation** - Setup guides, examples, API docs

---

## 🎯 Metadata Categories

### **1. Core Identity**

```python
name: str  # Unique agent identifier
layer: AgentLayer  # LAYER_1_EXTRACTION, LAYER_2_RECOGNITION, etc.
version: str  # Semantic version (e.g., "1.0.0")
description: str  # Human-readable description
capabilities: List[str]  # What the agent can do
dependencies: List[str]  # Other agents this depends on
```

**Example:**
```python
name="gmail_parser"
layer=AgentLayer.LAYER_1_EXTRACTION
version="1.0.0"
description="LLM-powered Gmail parsing for email intelligence"
capabilities=["email_parsing", "thread_analysis", "attachment_extraction"]
dependencies=["gmail_connector"]
```

---

### **2. Filtering & Visibility**

```python
entity_types: List[EntityType]  # Who can see this agent
app_contexts: List[AppContext]  # Where agent is available
requires_subscription: List[str]  # Required subscriptions
```

**Entity Types:**
- `PERSONAL` - Individual users
- `BUSINESS` - Companies and organizations
- `TRADING_FIRM` - Investment/trading firms
- `UNIVERSAL` - Everyone

**App Contexts:**
- `ATLAS` - Personal/business management
- `DELT` - Trading UI
- `AKASHIC` - Development terminal
- `ALL` - Available everywhere

**Example:**
```python
entity_types=[EntityType.PERSONAL, EntityType.BUSINESS]
app_contexts=[AppContext.ATLAS]
requires_subscription=[]  # Free for all
```

---

### **3. Authentication & Access**

```python
byok_enabled: bool  # Bring Your Own Keys
wtf_purchasable: bool  # Purchasable with WTF coin
required_credentials: List[str]  # Needed credentials
wtf_price_monthly: Optional[int]  # WTF coins per month
```

**BYOK (Bring Your Own Keys):**
- User provides their own API keys
- Full control and ownership
- Unlimited resources
- No platform costs

**WTF Purchasable:**
- User pays with WTF utility token
- Premium data streams
- Advanced features
- Platform-managed

**Example:**
```python
# External API connector
byok_enabled=True
wtf_purchasable=False
required_credentials=["api_key", "secret_key"]
wtf_price_monthly=None

# Premium data stream
byok_enabled=False
wtf_purchasable=True
required_credentials=[]
wtf_price_monthly=100  # 100 WTF/month
```

---

### **4. Resource Usage**

```python
estimated_tokens_per_call: Optional[int]  # LLM token usage
estimated_cost_per_call: Optional[float]  # USD cost
rate_limit: Optional[str]  # API rate limits
```

**Purpose:**
- Cost tracking and optimization
- Budget forecasting
- Resource allocation
- Rate limit management

**Example:**
```python
estimated_tokens_per_call=1500  # Average tokens
estimated_cost_per_call=0.003  # $0.003 per call
rate_limit="100/hour"  # 100 calls per hour
```

**Cost Calculation:**
```
Monthly cost = calls_per_month * estimated_cost_per_call
Example: 10,000 calls/month * $0.003 = $30/month
```

---

### **5. Performance**

```python
avg_response_time_ms: Optional[int]  # Average response time
requires_gpu: bool  # Needs GPU for processing
can_run_offline: bool  # Works without internet
```

**Purpose:**
- Performance monitoring
- SLA compliance
- Infrastructure planning
- Offline capability

**Example:**
```python
avg_response_time_ms=500  # 500ms average
requires_gpu=False  # CPU only
can_run_offline=False  # Needs internet
```

**Performance Tiers:**
- **Fast:** < 100ms (real-time)
- **Normal:** 100-1000ms (interactive)
- **Slow:** 1-5s (batch processing)
- **Very Slow:** > 5s (heavy computation)

---

### **6. Data & Privacy**

```python
data_retention_days: Optional[int]  # How long data is kept
privacy_level: PrivacyLevel  # Privacy classification
pii_handling: bool  # Handles PII
gdpr_compliant: bool  # GDPR compliance
```

**Privacy Levels:**
- `PERSONAL` - Only user can access
- `PRIVATE` - User + explicit shares
- `ORG_PRIVATE` - Organization members only
- `ORG_PUBLIC` - Organization + public profile
- `PUBLIC` - Fully public

**Example:**
```python
data_retention_days=90  # Keep for 90 days
privacy_level=PrivacyLevel.PERSONAL  # User-only
pii_handling=True  # Handles email addresses, names
gdpr_compliant=True  # GDPR compliant
```

**GDPR Requirements:**
- ✅ Right to access
- ✅ Right to deletion
- ✅ Right to portability
- ✅ Data minimization
- ✅ Purpose limitation

---

### **7. Integration Details**

```python
api_version: Optional[str]  # API version
webhook_support: bool  # Supports webhooks
real_time_sync: bool  # Real-time vs batch
sync_frequency: Optional[str]  # Sync frequency
```

**Purpose:**
- API compatibility
- Real-time updates
- Sync scheduling
- Webhook configuration

**Example:**
```python
api_version="v2"  # Using API v2
webhook_support=True  # Supports webhooks
real_time_sync=True  # Real-time updates
sync_frequency="real-time"  # Continuous sync
```

**Sync Frequencies:**
- `real-time` - Immediate (webhooks)
- `hourly` - Every hour
- `daily` - Once per day
- `weekly` - Once per week
- `manual` - User-triggered

---

### **8. Business Logic**

```python
free_tier_limit: Optional[int]  # Free tier limit
pro_tier_limit: Optional[int]  # Pro tier limit
enterprise_only: bool  # Enterprise only
beta: bool  # Beta status
```

**Purpose:**
- Subscription tiers
- Usage limits
- Feature gating
- Beta testing

**Example:**
```python
free_tier_limit=100  # 100 calls/month free
pro_tier_limit=10000  # 10,000 calls/month pro
enterprise_only=False  # Available to all
beta=False  # Production ready
```

**Tier Structure:**
- **Free:** Basic features, limited usage
- **Pro:** Advanced features, higher limits
- **Enterprise:** All features, unlimited usage

---

### **9. Learning & Training**

```python
supports_continuous_learning: bool  # Can train on user data
training_cost_wtf: Optional[int]  # WTF cost to train
training_frequency: Optional[str]  # Training frequency
model_storage_location: Optional[str]  # Where models are stored
```

**Purpose:**
- Personalized models
- Continuous improvement
- Cost transparency
- Data sovereignty

**Example:**
```python
supports_continuous_learning=True  # Learns from usage
training_cost_wtf=100  # 100 WTF per training
training_frequency="after_100_interactions"  # Auto-trigger
model_storage_location="filecoin"  # Stored on Filecoin
```

**Training Flow:**
1. User interacts with agent (100 times)
2. Auto-trigger training job
3. Upload data to Filecoin (privacy-isolated)
4. Train on Theta GPU ($1, ~2 hours)
5. Deploy personalized model
6. Agent gets smarter over time

---

### **10. UI/UX**

```python
has_ui_component: bool  # Has dedicated UI
icon: Optional[str]  # Icon name or URL
color: Optional[str]  # Brand color
category: Optional[AgentCategory]  # Category
```

**Purpose:**
- Visual identity
- Organization
- User experience
- Branding

**Example:**
```python
has_ui_component=True  # Has UI in Atlas
icon="mail"  # Lucide icon name
color="#EA4335"  # Gmail red
category=AgentCategory.COMMUNICATION  # Communication category
```

**Categories:**
- `COMMUNICATION` - Email, chat, calendar
- `FINANCE` - Banking, accounting, trading
- `HEALTH` - Fitness, nutrition, wellness
- `PRODUCTIVITY` - Tasks, notes, documents
- `SOCIAL` - Twitter, LinkedIn, contacts
- `TRAVEL` - Maps, rides, accommodations
- `SHOPPING` - E-commerce, subscriptions
- `MEDIA` - Music, videos, images
- `DEVELOPMENT` - Code, DevOps, architecture
- `ANALYTICS` - Data analysis, reporting
- `MARKETING` - Campaigns, SEO, content
- `SALES` - CRM, pipeline, forecasting
- `HR` - Recruiting, payroll, benefits
- `LEGAL` - Contracts, compliance, IP
- `OPERATIONS` - Processes, workflows
- `SECURITY` - Auth, encryption, auditing
- `INFRASTRUCTURE` - Servers, databases, monitoring
- `KNOWLEDGE` - Knowledge graphs, learning
- `WORKFLOW` - Orchestration, automation
- `META` - System-level, optimization

---

### **11. Monitoring & Alerts**

```python
health_check_endpoint: Optional[str]  # Health check URL
alert_on_failure: bool  # Send alerts
fallback_agent: Optional[str]  # Fallback agent
```

**Purpose:**
- System reliability
- Incident response
- Graceful degradation
- Uptime monitoring

**Example:**
```python
health_check_endpoint="/health/gmail_parser"  # Health check
alert_on_failure=True  # Alert on failure
fallback_agent="email_parser"  # Fallback to generic parser
```

**Health Check Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 86400,
  "last_success": "2025-10-30T10:00:00Z",
  "error_rate": 0.001,
  "avg_response_time_ms": 450
}
```

---

### **12. Documentation**

```python
documentation_url: Optional[str]  # Link to docs
example_use_cases: List[str]  # Example scenarios
setup_guide_url: Optional[str]  # Setup instructions
```

**Purpose:**
- User onboarding
- Developer experience
- Self-service support
- Best practices

**Example:**
```python
documentation_url="https://docs.colossalcapital.com/agents/gmail-parser"
example_use_cases=[
    "Extract action items from emails",
    "Analyze email sentiment",
    "Track email response times"
]
setup_guide_url="https://docs.colossalcapital.com/setup/gmail"
```

---

## 🎯 Complete Example

```python
from agents.base import (
    AgentMetadata, AgentLayer, EntityType, AppContext,
    PrivacyLevel, AgentCategory
)

metadata = AgentMetadata(
    # Core Identity
    name="gmail_parser",
    layer=AgentLayer.LAYER_1_EXTRACTION,
    version="1.0.0",
    description="LLM-powered Gmail parsing for email intelligence",
    capabilities=["email_parsing", "thread_analysis", "attachment_extraction"],
    dependencies=["gmail_connector"],
    
    # Filtering & Visibility
    entity_types=[EntityType.UNIVERSAL],
    app_contexts=[AppContext.ATLAS],
    requires_subscription=[],
    
    # Authentication & Access
    byok_enabled=False,
    wtf_purchasable=False,
    required_credentials=[],
    wtf_price_monthly=None,
    
    # Resource Usage
    estimated_tokens_per_call=1500,
    estimated_cost_per_call=0.003,
    rate_limit="100/hour",
    
    # Performance
    avg_response_time_ms=500,
    requires_gpu=False,
    can_run_offline=False,
    
    # Data & Privacy
    data_retention_days=90,
    privacy_level=PrivacyLevel.PERSONAL,
    pii_handling=True,
    gdpr_compliant=True,
    
    # Integration Details
    api_version="v1",
    webhook_support=True,
    real_time_sync=True,
    sync_frequency="real-time",
    
    # Business Logic
    free_tier_limit=100,
    pro_tier_limit=10000,
    enterprise_only=False,
    beta=False,
    
    # Learning & Training
    supports_continuous_learning=True,
    training_cost_wtf=100,
    training_frequency="after_100_interactions",
    model_storage_location="filecoin",
    
    # UI/UX
    has_ui_component=True,
    icon="mail",
    color="#EA4335",
    category=AgentCategory.COMMUNICATION,
    
    # Monitoring & Alerts
    health_check_endpoint="/health/gmail_parser",
    alert_on_failure=True,
    fallback_agent="email_parser",
    
    # Documentation
    documentation_url="https://docs.colossalcapital.com/agents/gmail-parser",
    example_use_cases=[
        "Extract action items from emails",
        "Analyze email sentiment",
        "Track email response times"
    ],
    setup_guide_url="https://docs.colossalcapital.com/setup/gmail"
)
```

---

## 📊 Metadata Benefits

### **For Users:**
- ✅ Transparent pricing
- ✅ Clear privacy policies
- ✅ Easy setup guides
- ✅ Performance expectations

### **For Developers:**
- ✅ Complete API documentation
- ✅ Integration examples
- ✅ Health monitoring
- ✅ Error handling

### **For Business:**
- ✅ Cost tracking
- ✅ Usage analytics
- ✅ Tier management
- ✅ Compliance auditing

### **For Operations:**
- ✅ Performance monitoring
- ✅ Incident response
- ✅ Capacity planning
- ✅ SLA compliance

---

## 🚀 Next Steps

1. ✅ **Base class updated** - All enums and fields added
2. 🔄 **Update all 139 agents** - Add comprehensive metadata
3. 🔄 **Create API endpoints** - Query agents by metadata
4. 🔄 **Build UI components** - Display metadata in Atlas
5. 🔄 **Add monitoring** - Track health and performance
6. 🔄 **Generate documentation** - Auto-generate from metadata

---

**Status:** Metadata specification complete, ready for implementation  
**Created:** October 30, 2025  
**Owner:** Apollo AI System
