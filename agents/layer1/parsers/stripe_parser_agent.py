"""
Stripe Parser Agent - LLM-Powered Payment & Subscription Parsing

Layer 1 Data Extraction agent that uses LLM to parse raw Stripe API
responses into structured payment data.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class StripeParserAgent(Layer1Agent):
    """
    Stripe Parser - LLM-powered payment and subscription parsing
    
    Takes raw Stripe API responses and extracts:
    - Payment details (amount, status, customer)
    - Subscription information
    - Customer data
    - Revenue metrics
    - Churn analysis
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="stripe_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Stripe payment and subscription parsing",
            capabilities=["payment_parsing", "subscription_analysis", "revenue_tracking", "churn_detection"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw Stripe API response
        
        Args:
            raw_data: Raw Stripe API response (payment, subscription, etc.)
            
        Returns:
            AgentResult with structured payment data
        """
        
        data_type = raw_data.get('type', 'payment')
        
        if data_type == 'payment':
            return await self._parse_payment(raw_data)
        elif data_type == 'subscription':
            return await self._parse_subscription(raw_data)
        elif data_type == 'customer':
            return await self._parse_customer(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_payment(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse payment with LLM"""
        
        prompt = f"""You are an expert payment data parser. Extract structured information from this Stripe payment.

RAW PAYMENT DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Payment ID and status
2. Amount and currency
3. Customer information
4. Payment method
5. Description/purpose
6. Fees and net amount
7. Refund status
8. Risk indicators

Return as JSON:
{{
    "payment_id": "pi_...",
    "status": "succeeded",
    "amount": 5000,
    "currency": "usd",
    "net_amount": 4855,
    "fees": 145,
    "customer": {{
        "id": "cus_...",
        "email": "customer@example.com",
        "name": "John Smith"
    }},
    "payment_method": "card",
    "card_brand": "visa",
    "card_last4": "4242",
    "description": "Monthly subscription",
    "created": "2025-10-29",
    "refunded": false,
    "risk_level": "normal",
    "metadata": {{}}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 1500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_payment_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'payment'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_subscription(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse subscription with LLM"""
        
        prompt = f"""Extract subscription information from this Stripe data.

RAW SUBSCRIPTION DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Subscription ID and status
2. Customer information
3. Plan details (name, amount, interval)
4. Current period (start, end)
5. Next billing date
6. Trial information
7. Cancellation status
8. MRR (Monthly Recurring Revenue)

Return as JSON with these fields.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 1500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_subscription_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'subscription'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_customer(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse customer data with LLM"""
        pass
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic Stripe data parsing"""
        pass
    
    async def _store_payment_in_kg(self, payment_data: Dict[str, Any]):
        """Store parsed payment in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="payment",
            data=payment_data
        )
        
        # Create customer entity
        await self.kg_client.create_entity(
            entity_type="customer",
            data=payment_data.get('customer', {})
        )
    
    async def _store_subscription_in_kg(self, subscription_data: Dict[str, Any]):
        """Store parsed subscription in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="subscription",
            data=subscription_data
        )
