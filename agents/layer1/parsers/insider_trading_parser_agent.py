"""
Insider Trading Parser Agent - LLM-Powered Insider Trading Analysis

Layer 1 Data Extraction agent that uses LLM to parse insider trading
data and extract actionable intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class InsiderTradingParserAgent(Layer1Agent):
    """
    Insider Trading Parser - LLM-powered insider activity analysis
    
    Takes raw insider trading data and extracts:
    - Insider buy/sell patterns
    - Cluster buying signals
    - Insider sentiment
    - Unusual activity
    - Trading patterns
    - Price impact predictions
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="insider_trading_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered insider trading analysis with sentiment and signals",
            capabilities=["insider_analysis", "cluster_detection", "sentiment_analysis", "signal_generation"],
            dependencies=["openinsider_connector", "sec_edgar_scraper"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured insights from raw insider trading data
        
        Args:
            raw_data: Raw insider trading data
            
        Returns:
            AgentResult with structured insider intelligence
        """
        
        return await self._parse_insider_activity(raw_data)
    
    async def _parse_insider_activity(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse insider trading activity with LLM"""
        
        prompt = f"""You are an expert at analyzing insider trading patterns. Extract actionable intelligence from this insider trading data.

RAW INSIDER TRADING DATA:
{json.dumps(raw_data, indent=2)}

ANALYZE:
1. Transaction details (buy/sell, shares, price, value)
2. Insider information (name, title, relationship to company)
3. Company information (ticker, sector, market cap)
4. Transaction timing and context
5. Insider sentiment (bullish, bearish, neutral)
6. Pattern analysis (cluster buying, unusual activity)
7. Historical context (insider's track record)
8. Price impact prediction
9. Trading signals (buy, sell, hold)
10. Risk assessment
11. Confidence level

Return as JSON:
{{
    "transaction_id": "...",
    "transaction_date": "2025-10-29",
    "filing_date": "2025-10-30",
    "company": {{
        "ticker": "AAPL",
        "name": "Apple Inc",
        "sector": "Technology",
        "market_cap": 3000000000000
    }},
    "insider": {{
        "name": "Tim Cook",
        "title": "CEO",
        "relationship": "officer",
        "ownership_percent": 0.02,
        "track_record": {{
            "total_transactions": 45,
            "successful_trades": 38,
            "success_rate": 0.84
        }}
    }},
    "transaction": {{
        "type": "purchase",
        "shares": 50000,
        "price_per_share": 180.50,
        "total_value": 9025000,
        "transaction_code": "P",
        "direct_indirect": "direct"
    }},
    "context": {{
        "recent_stock_performance": "down_15_percent_from_high",
        "recent_news": ["Q3 earnings miss", "iPhone sales weak"],
        "sector_performance": "underperforming",
        "market_conditions": "volatile"
    }},
    "sentiment_analysis": {{
        "insider_sentiment": "bullish",
        "confidence": 0.85,
        "reasoning": "CEO buying at 52-week low signals confidence",
        "contrarian_indicator": true
    }},
    "pattern_analysis": {{
        "is_cluster_buy": true,
        "cluster_size": 5,
        "other_insiders": ["CFO", "COO", "Board Member", "VP Engineering"],
        "unusual_activity": true,
        "activity_level": "high"
    }},
    "price_impact": {{
        "predicted_impact": "positive",
        "magnitude": "medium",
        "timeframe": "1_to_3_months",
        "historical_correlation": 0.72
    }},
    "trading_signal": {{
        "signal": "buy",
        "strength": "strong",
        "entry_price": 175.00,
        "target_price": 200.00,
        "stop_loss": 165.00,
        "risk_reward_ratio": 5.0
    }},
    "risk_assessment": {{
        "risk_level": "medium",
        "risk_factors": [
            "Sector headwinds",
            "Macro uncertainty"
        ],
        "mitigating_factors": [
            "Strong balance sheet",
            "Insider confidence",
            "Cluster buying"
        ]
    }},
    "actionable_insights": [
        "Strong insider buying at support level",
        "Multiple insiders buying suggests bottom",
        "Consider accumulating on weakness",
        "Watch for follow-through buying"
    ],
    "source": "openinsider"
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_insider_activity_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'insider_trading'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_insider_activity_in_kg(self, insider_data: Dict[str, Any]):
        """Store parsed insider activity in knowledge graph"""
        if not self.kg_client:
            return
        
        # Create insider transaction entity
        await self.kg_client.create_entity(
            entity_type="insider_transaction",
            data=insider_data
        )
        
        # Create trading signal entity
        if insider_data.get('trading_signal'):
            await self.kg_client.create_entity(
                entity_type="trading_signal",
                data={
                    **insider_data['trading_signal'],
                    'source': 'insider_trading',
                    'ticker': insider_data['company']['ticker'],
                    'signal_date': insider_data['transaction_date']
                }
            )
        
        # Create insider entity
        await self.kg_client.create_entity(
            entity_type="insider",
            data=insider_data['insider']
        )
