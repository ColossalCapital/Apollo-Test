"""
Gmail Parser Agent - LLM-Powered Email Parsing

Layer 1 Data Extraction agent that uses LLM to parse raw Gmail API
responses into structured data.
"""

from typing import Dict, Any
from ...base import (
    Layer1Agent, AgentResult, AgentMetadata, AgentLayer,
    EntityType, AppContext, PrivacyLevel, AgentCategory
)
import httpx
import json


class GmailParserAgent(Layer1Agent):
    """
    Gmail Parser - LLM-powered email parsing
    
    Takes raw Gmail API responses and extracts:
    - Sender information
    - Subject and body
    - Intent and urgency
    - Attachments
    - Action items
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"  # Local LLM endpoint
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            # Core Identity
            name="gmail_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered email parsing and extraction",
            capabilities=["email_parsing", "intent_detection", "attachment_extraction", "action_items"],
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
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw Gmail API response
        
        Args:
            raw_data: Raw Gmail API message object
            
        Returns:
            AgentResult with structured email data
        """
        
        # Quick mode: Basic extraction without LLM
        if raw_data.get('quick_mode'):
            return await self._basic_extraction(raw_data)
        
        # Full mode: LLM-powered deep parsing
        return await self._llm_extraction(raw_data)
    
    async def _basic_extraction(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Basic extraction without LLM (fast, for simple cases)
        """
        headers = raw_data.get('payload', {}).get('headers', [])
        
        # Extract basic fields
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        return AgentResult(
            success=True,
            data={
                'sender': sender,
                'subject': subject,
                'date': date,
                'mode': 'basic'
            },
            metadata={'agent': self.metadata.name, 'mode': 'basic'}
        )
    
    async def _llm_extraction(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        LLM-powered deep extraction (smart, comprehensive)
        """
        
        # Build prompt for LLM
        prompt = f"""You are an expert email parser. Extract structured information from this Gmail API response.

RAW EMAIL DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Sender (name and email)
2. Recipients (to, cc, bcc)
3. Subject
4. Body (plain text summary)
5. Intent (what does the sender want?)
6. Urgency (low, medium, high, urgent)
7. Action items (list of tasks)
8. Attachments (names and types)
9. Key entities (people, companies, dates, amounts)
10. Sentiment (positive, neutral, negative)

Return as JSON with these exact fields:
{{
    "sender": {{"name": "...", "email": "..."}},
    "recipients": {{"to": [...], "cc": [...], "bcc": [...]}},
    "subject": "...",
    "body_summary": "...",
    "intent": "...",
    "urgency": "...",
    "action_items": [...],
    "attachments": [...],
    "entities": {{"people": [...], "companies": [...], "dates": [...], "amounts": [...]}},
    "sentiment": "..."
}}
"""
        
        try:
            # Call LLM
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={
                    'agent': self.metadata.name,
                    'mode': 'llm',
                    'model': 'phi-3-medium',
                    'confidence': 0.9
                }
            )
            
        except Exception as e:
            # Fallback to basic extraction if LLM fails
            return await self._basic_extraction(raw_data)
