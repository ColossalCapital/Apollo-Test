"""
Shopping Parser Agent - LLM-Powered Shopping Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse shopping data
from Amazon and subscription tracking.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ShoppingParserAgent(Layer1Agent):
    """
    Shopping Parser - LLM-powered shopping data parsing
    
    Takes shopping data and extracts:
    - Purchase patterns
    - Spending categories
    - Subscription analysis
    - Product preferences
    - Cost optimization opportunities
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="shopping_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered shopping and subscription data parsing",
            capabilities=[
                "purchase_analysis",
                "subscription_tracking",
                "spending_patterns",
                "product_preferences",
                "cost_optimization"
            ],
            dependencies=[
                "amazon_connector",
                "subscription_tracker"
            ]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Extract structured data from shopping sources"""
        
        prompt = f"""You are an expert at analyzing shopping and subscription data. Extract structured information from this data.

SHOPPING DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Purchase summary (total spending, item count, categories)
2. Spending patterns (frequency, seasonal trends)
3. Product categories (electronics, books, household, etc.)
4. Subscription analysis (active, unused, duplicates)
5. Business vs personal purchases
6. Product preferences and brands
7. Cost optimization opportunities
8. Unused subscriptions to cancel
9. Duplicate subscriptions
10. Recommendations for savings

Return as JSON with detailed shopping and subscription analysis.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_shopping_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'shopping'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_shopping_in_kg(self, shopping_data: Dict[str, Any]):
        """Store parsed shopping data in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="shopping",
            data=shopping_data,
            graph_type="personal"
        )
