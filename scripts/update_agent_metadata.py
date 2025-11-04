"""
Script to update all agent metadata with comprehensive production-ready fields.

This script provides metadata templates for each agent category to ensure
consistency across all 139 agents.
"""

from typing import Dict, Any

# Metadata templates by agent category
METADATA_TEMPLATES = {
    "parser": {
        "estimated_tokens_per_call": 1500,
        "estimated_cost_per_call": 0.003,
        "rate_limit": "100/hour",
        "avg_response_time_ms": 500,
        "requires_gpu": False,
        "can_run_offline": False,
        "data_retention_days": 90,
        "privacy_level": "PrivacyLevel.PERSONAL",
        "pii_handling": True,
        "gdpr_compliant": True,
        "webhook_support": True,
        "real_time_sync": True,
        "sync_frequency": "real-time",
        "free_tier_limit": 100,
        "pro_tier_limit": 10000,
        "enterprise_only": False,
        "beta": False,
        "supports_continuous_learning": True,
        "training_cost_wtf": 100,
        "training_frequency": "after_100_interactions",
        "model_storage_location": "filecoin",
        "has_ui_component": True,
        "alert_on_failure": True,
    },
    
    "recognition": {
        "estimated_tokens_per_call": 800,
        "estimated_cost_per_call": 0.002,
        "rate_limit": "200/hour",
        "avg_response_time_ms": 300,
        "requires_gpu": False,
        "can_run_offline": False,
        "data_retention_days": 90,
        "privacy_level": "PrivacyLevel.PRIVATE",
        "pii_handling": True,
        "gdpr_compliant": True,
        "webhook_support": False,
        "real_time_sync": False,
        "sync_frequency": None,
        "free_tier_limit": 500,
        "pro_tier_limit": 50000,
        "enterprise_only": False,
        "beta": False,
        "supports_continuous_learning": True,
        "training_cost_wtf": 100,
        "training_frequency": "after_100_interactions",
        "model_storage_location": "filecoin",
        "has_ui_component": False,
        "alert_on_failure": False,
    },
    
    "domain_expert": {
        "estimated_tokens_per_call": 2500,
        "estimated_cost_per_call": 0.005,
        "rate_limit": "50/hour",
        "avg_response_time_ms": 1000,
        "requires_gpu": False,
        "can_run_offline": False,
        "data_retention_days": 180,
        "privacy_level": "PrivacyLevel.PRIVATE",
        "pii_handling": False,
        "gdpr_compliant": True,
        "webhook_support": False,
        "real_time_sync": False,
        "sync_frequency": None,
        "free_tier_limit": 50,
        "pro_tier_limit": 5000,
        "enterprise_only": False,
        "beta": False,
        "supports_continuous_learning": True,
        "training_cost_wtf": 200,
        "training_frequency": "after_50_interactions",
        "model_storage_location": "filecoin",
        "has_ui_component": True,
        "alert_on_failure": True,
    },
    
    "workflow": {
        "estimated_tokens_per_call": 3000,
        "estimated_cost_per_call": 0.006,
        "rate_limit": "20/hour",
        "avg_response_time_ms": 2000,
        "requires_gpu": False,
        "can_run_offline": False,
        "data_retention_days": 365,
        "privacy_level": "PrivacyLevel.ORG_PRIVATE",
        "pii_handling": True,
        "gdpr_compliant": True,
        "webhook_support": True,
        "real_time_sync": False,
        "sync_frequency": "hourly",
        "free_tier_limit": 20,
        "pro_tier_limit": 1000,
        "enterprise_only": False,
        "beta": False,
        "supports_continuous_learning": False,
        "training_cost_wtf": None,
        "training_frequency": None,
        "model_storage_location": None,
        "has_ui_component": True,
        "alert_on_failure": True,
    },
    
    "meta": {
        "estimated_tokens_per_call": 5000,
        "estimated_cost_per_call": 0.010,
        "rate_limit": "10/hour",
        "avg_response_time_ms": 3000,
        "requires_gpu": False,
        "can_run_offline": False,
        "data_retention_days": 365,
        "privacy_level": "PrivacyLevel.PRIVATE",
        "pii_handling": False,
        "gdpr_compliant": True,
        "webhook_support": False,
        "real_time_sync": False,
        "sync_frequency": None,
        "free_tier_limit": 10,
        "pro_tier_limit": 500,
        "enterprise_only": False,
        "beta": False,
        "supports_continuous_learning": True,
        "training_cost_wtf": 500,
        "training_frequency": "after_20_interactions",
        "model_storage_location": "filecoin",
        "has_ui_component": False,
        "alert_on_failure": True,
    },
    
    "connector": {
        "estimated_tokens_per_call": None,
        "estimated_cost_per_call": 0.001,
        "rate_limit": "100/hour",
        "avg_response_time_ms": 200,
        "requires_gpu": False,
        "can_run_offline": False,
        "data_retention_days": 30,
        "privacy_level": "PrivacyLevel.PERSONAL",
        "pii_handling": True,
        "gdpr_compliant": True,
        "webhook_support": True,
        "real_time_sync": True,
        "sync_frequency": "real-time",
        "free_tier_limit": 1000,
        "pro_tier_limit": 100000,
        "enterprise_only": False,
        "beta": False,
        "supports_continuous_learning": False,
        "training_cost_wtf": None,
        "training_frequency": None,
        "model_storage_location": None,
        "has_ui_component": True,
        "alert_on_failure": True,
    },
}

# Category mappings for agents
AGENT_CATEGORIES = {
    # Communication
    "gmail": "COMMUNICATION",
    "slack": "COMMUNICATION",
    "imessage": "COMMUNICATION",
    "telegram": "COMMUNICATION",
    "gcal": "COMMUNICATION",
    "contacts": "COMMUNICATION",
    
    # Finance
    "quickbooks": "FINANCE",
    "plaid": "FINANCE",
    "stripe": "FINANCE",
    "turbotax": "FINANCE",
    "invoice": "FINANCE",
    "trading": "FINANCE",
    "financial_analyst": "FINANCE",
    
    # Health
    "apple_health": "HEALTH",
    "strava": "HEALTH",
    "nike_run_club": "HEALTH",
    "myfitnesspal": "HEALTH",
    "health_fitness": "HEALTH",
    
    # Productivity
    "notion": "PRODUCTIVITY",
    "google_drive": "PRODUCTIVITY",
    "dropbox": "PRODUCTIVITY",
    "icloud": "PRODUCTIVITY",
    "github": "PRODUCTIVITY",
    
    # Social
    "twitter": "SOCIAL",
    "linkedin": "SOCIAL",
    
    # Travel
    "google_maps": "TRAVEL",
    "uber": "TRAVEL",
    "airbnb": "TRAVEL",
    "travel": "TRAVEL",
    
    # Shopping
    "amazon": "SHOPPING",
    "subscription_tracker": "SHOPPING",
    "shopping": "SHOPPING",
    
    # Media
    "spotify": "MEDIA",
    "youtube": "MEDIA",
    "audio": "MEDIA",
    "image": "MEDIA",
    "video": "MEDIA",
    "meme": "MEDIA",
    
    # Development
    "code_review": "DEVELOPMENT",
    "code_generation": "DEVELOPMENT",
    "architecture": "DEVELOPMENT",
    "performance": "DEVELOPMENT",
    "qa_testing": "DEVELOPMENT",
    "devops": "DEVELOPMENT",
    
    # Analytics
    "data_analyst": "ANALYTICS",
    "analytics": "ANALYTICS",
    
    # Marketing
    "marketing": "MARKETING",
    "content_creation": "MARKETING",
    "seo": "MARKETING",
    
    # Sales
    "sales": "SALES",
    
    # HR
    "hr": "HR",
    "recruiting": "HR",
    
    # Legal
    "legal": "LEGAL",
    
    # Operations
    "operations": "OPERATIONS",
    
    # Security
    "security": "SECURITY",
    
    # Infrastructure
    "deployment": "INFRASTRUCTURE",
    "incident_response": "INFRASTRUCTURE",
    
    # Knowledge
    "knowledge_graph": "KNOWLEDGE",
    
    # Workflow
    "meeting": "WORKFLOW",
    "project_manager": "WORKFLOW",
    "compliance": "WORKFLOW",
    "hiring": "WORKFLOW",
    "email_campaign": "WORKFLOW",
    "onboarding": "WORKFLOW",
    "content_workflow": "WORKFLOW",
    
    # Meta
    "meta_orchestrator": "META",
    "learning": "META",
    "optimization": "META",
}

# Icon mappings
AGENT_ICONS = {
    "gmail": "mail",
    "slack": "message-square",
    "imessage": "message-circle",
    "telegram": "send",
    "gcal": "calendar",
    "contacts": "users",
    "quickbooks": "dollar-sign",
    "plaid": "credit-card",
    "stripe": "credit-card",
    "trading": "trending-up",
    "apple_health": "heart",
    "strava": "activity",
    "notion": "file-text",
    "github": "github",
    "twitter": "twitter",
    "linkedin": "linkedin",
    "spotify": "music",
    "youtube": "youtube",
    "code_review": "code",
    "analytics": "bar-chart",
    "marketing": "megaphone",
    "sales": "shopping-cart",
    "hr": "users",
    "legal": "scale",
    "security": "shield",
}

# Color mappings (brand colors)
AGENT_COLORS = {
    "gmail": "#EA4335",
    "slack": "#4A154B",
    "telegram": "#0088CC",
    "quickbooks": "#2CA01C",
    "plaid": "#000000",
    "stripe": "#635BFF",
    "apple_health": "#FF2D55",
    "strava": "#FC4C02",
    "notion": "#000000",
    "github": "#181717",
    "twitter": "#1DA1F2",
    "linkedin": "#0A66C2",
    "spotify": "#1DB954",
    "youtube": "#FF0000",
}


def get_metadata_template(agent_type: str, agent_name: str) -> Dict[str, Any]:
    """Get metadata template for an agent"""
    template = METADATA_TEMPLATES.get(agent_type, {}).copy()
    
    # Add category
    for key, category in AGENT_CATEGORIES.items():
        if key in agent_name.lower():
            template["category"] = f"AgentCategory.{category}"
            break
    
    # Add icon
    for key, icon in AGENT_ICONS.items():
        if key in agent_name.lower():
            template["icon"] = icon
            break
    
    # Add color
    for key, color in AGENT_COLORS.items():
        if key in agent_name.lower():
            template["color"] = color
            break
    
    return template


# Example usage
if __name__ == "__main__":
    # Get template for Gmail parser
    template = get_metadata_template("parser", "gmail_parser")
    print("Gmail Parser Template:")
    for key, value in template.items():
        print(f"  {key}: {value}")
