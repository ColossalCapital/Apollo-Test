"""
Money Recognition Agent - LLM-Powered Money Entity Recognition

Layer 2 Entity Recognition agent that identifies and extracts monetary entities.
"""

from typing import Dict, Any
from ...base import Layer2Agent, AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext
import httpx
import json


class MoneyRecognitionAgent(Layer2Agent):
    """
    Money Recognition - Identifies monetary entities
    
    Extracts:
    - Currency amounts
    - Financial instruments
    - Prices and valuations
    - Salaries and compensation
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="money_recognition",
            layer=AgentLayer.LAYER_2_RECOGNITION,
            version="1.0.0",
            description="LLM-powered monetary entity recognition",
            capabilities=["currency_extraction", "price_parsing", "valuation_detection"],
            dependencies=["document_parser"],
            
            # Metadata for filtering
            entity_types=[EntityType.UNIVERSAL],
            app_contexts=[AppContext.ATLAS, AppContext.DELT, AppContext.AKASHIC],
            requires_subscription=[],
            byok_enabled=False,
            wtf_purchasable=False
        )
    
    async def recognize(self, parsed_data: Dict[str, Any]) -> AgentResult:
        """Recognize money entities from parsed data"""
        
        text = parsed_data.get('text', '')
        
        prompt = f"""Extract all monetary entities from this text.

TEXT:
{text}

Extract:
1. Currency amounts (e.g., "$100", "€50", "¥1000")
2. Prices (e.g., "$29.99", "£19.99")
3. Salaries (e.g., "$120,000/year", "$50/hour")
4. Valuations (e.g., "$1.5M valuation", "$10B market cap")
5. Financial instruments (e.g., "100 shares", "0.5 BTC")
6. Percentages (e.g., "15% discount", "3.5% interest")

Return as JSON with monetary entities, amounts, and currencies.
"""
        
        try:
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
            money_entities = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_money_in_kg(money_entities)
            
            return AgentResult(
                success=True,
                data=money_entities,
                metadata={'agent': self.metadata.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_money_in_kg(self, money_entities: Dict[str, Any]):
        """Store money entities in knowledge graph"""
        if not self.kg_client:
            return
        
        for entity in money_entities.get('monetary_entities', []):
            await self.kg_client.create_entity(
                entity_type="money",
                data=entity,
                graph_type="financial"
            )
