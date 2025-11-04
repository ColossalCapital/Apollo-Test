# 📱 ATLAS + Apollo Use Cases

## **Use Case 1: Smart Email Management**

**Scenario:** User receives 50 emails overnight

```python
# Atlas fetches emails
emails = atlas.fetch_emails(user_id="user123")

# Apollo analyzes each email
for email in emails:
    response = await apollo_client.analyze(
        user_id="user123",
        app_context="atlas",
        atlas_tier="personal",
        privacy="personal",
        agent_type="email",
        data={
            "sender": email.sender,
            "subject": email.subject,
            "body": email.body
        }
    )
    
    # Apollo returns intelligence
    email.urgency = response.urgency
    email.category = response.category
    email.summary = response.summary
```

**Apollo Response:**
```json
{
  "urgency": "high",
  "category": "work",
  "summary": "Your boss needs Q4 report by EOD",
  "suggested_action": "reply_within_2_hours",
  "suggested_response": "I'll have the Q4 report ready by 3pm...",
  "model_used": "personal_trained"
}
```

## **Use Case 2: Calendar Optimization**

**Scenario:** User has 10 meeting invites

```python
response = await apollo_client.analyze(
    user_id="user123",
    app_context="atlas",
    atlas_tier="team",
    agent_type="calendar",
    data={
        "events": events,
        "preferences": user_preferences
    }
)
```

**Apollo Response:**
```json
{
  "conflicts": [
    {"event1": "Team standup", "event2": "1-on-1", "suggestion": "Move 1-on-1 to Tuesday"}
  ],
  "suggestions": [
    "Block 9am-11am for deep work",
    "Decline 'Optional sync' - low priority"
  ]
}
```

## **Use Case 3: Document Intelligence**

**Scenario:** User uploads 100-page contract

```python
response = await apollo_client.analyze(
    user_id="user123",
    app_context="atlas",
    atlas_tier="enterprise",
    agent_type="legal",
    data={"document": contract}
)
```

**Apollo Response:**
```json
{
  "summary": "5-year SaaS contract, $500K/year",
  "risks": [
    {"risk": "Auto-renewal", "severity": "high"},
    {"risk": "Unlimited liability", "severity": "critical"}
  ],
  "action_items": ["Review with legal", "Set renewal reminder"]
}
```

## **Use Case 4: Team Knowledge Base**

**Scenario:** Enterprise team searching company knowledge

```python
response = await apollo_client.query(
    user_id="user123",
    org_id="bigcorp456",
    app_context="atlas",
    atlas_tier="enterprise",
    privacy="org_public",
    query="How do we handle customer refunds?"
)
```

**Apollo Response:**
```json
{
  "answer": "Refunds processed within 5-7 business days...",
  "sources": [
    {"doc": "Customer Service Handbook", "page": 23},
    {"doc": "Refund Policy 2024", "page": 1}
  ],
  "company_policy": {
    "standard_refund": "Full refund within 30 days",
    "escalation_threshold": "$10,000"
  },
  "model_used": "org_trained"
}
```
