"""
Forbes Parser Agent - LLM-Powered Forbes News Parsing

Layer 1 Data Extraction agent that uses LLM to parse Forbes news
articles and extract structured business intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ForbesParserAgent(Layer1Agent):
    """
    Forbes Parser - LLM-powered business news parsing
    
    Takes raw Forbes news articles and extracts:
    - Business insights and analysis
    - Executive profiles
    - Company valuations
    - Market trends
    - Investment opportunities
    - Billionaire rankings
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="forbes_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered Forbes news parsing with business intelligence",
            capabilities=["news_parsing", "business_analysis", "executive_tracking", "valuation_analysis"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw Forbes news article
        
        Args:
            raw_data: Raw Forbes news article
            
        Returns:
            AgentResult with structured news data
        """
        
        return await self._parse_article(raw_data)
    
    async def _parse_article(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Forbes article with LLM"""
        
        prompt = f"""You are an expert business analyst. Extract structured information from this Forbes article.

RAW FORBES ARTICLE:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Headline and summary
2. Publication date and time
3. Author and credentials
4. Article category (business, investing, billionaires, technology, leadership)
5. Featured companies and valuations
6. Featured executives and their roles
7. Key business insights
8. Market implications
9. Investment opportunities or risks
10. Competitive analysis
11. Industry trends
12. Financial metrics mentioned
13. Expert opinions and quotes
14. Actionable takeaways

Return as JSON:
{{
    "article_id": "...",
    "headline": "...",
    "summary": "...",
    "published_at": "2025-10-29T22:40:00Z",
    "author": {{
        "name": "John Forbes",
        "credentials": "Senior Business Editor",
        "expertise": ["technology", "startups"]
    }},
    "category": "business",
    "companies": [
        {{
            "name": "Apple Inc",
            "ticker": "AAPL",
            "valuation": 3000000000000,
            "mention_context": "Reached $3T market cap",
            "sentiment": "positive"
        }}
    ],
    "executives": [
        {{
            "name": "Tim Cook",
            "title": "CEO",
            "company": "Apple Inc",
            "mention_context": "Announced new AI strategy",
            "net_worth": 2000000000
        }}
    ],
    "business_insights": [
        "AI integration driving growth",
        "Services revenue exceeding hardware",
        "Ecosystem lock-in strengthening"
    ],
    "market_implications": {{
        "sectors_affected": ["technology", "consumer_electronics"],
        "market_sentiment": "bullish",
        "impact_level": "high"
    }},
    "investment_opportunities": [
        {{
            "type": "long_term_growth",
            "description": "AI-driven services expansion",
            "risk_level": "medium"
        }}
    ],
    "competitive_analysis": {{
        "competitors": ["Microsoft", "Google", "Amazon"],
        "competitive_advantage": "Ecosystem integration",
        "market_position": "leader"
    }},
    "industry_trends": [
        "AI integration in consumer products",
        "Shift to services revenue",
        "Privacy-focused computing"
    ],
    "financial_metrics": {{
        "revenue": 383000000000,
        "profit_margin": 0.25,
        "pe_ratio": 28.5,
        "growth_rate": 0.08
    }},
    "expert_opinions": [
        {{
            "expert": "Jane Analyst",
            "firm": "Goldman Sachs",
            "opinion": "Strong buy",
            "reasoning": "AI momentum and services growth"
        }}
    ],
    "actionable_takeaways": [
        "Consider long-term position in AAPL",
        "Watch for AI product announcements",
        "Monitor services revenue growth"
    ],
    "urgency": "important",
    "source": "Forbes"
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
                await self._store_article_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'forbes'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_article_in_kg(self, article_data: Dict[str, Any]):
        """Store parsed article in knowledge graph"""
        if not self.kg_client:
            return
        
        # Create news article entity
        await self.kg_client.create_entity(
            entity_type="news_article",
            data=article_data
        )
        
        # Create company entities
        for company in article_data.get('companies', []):
            await self.kg_client.create_entity(
                entity_type="company",
                data=company
            )
        
        # Create executive entities
        for executive in article_data.get('executives', []):
            await self.kg_client.create_entity(
                entity_type="executive",
                data=executive
            )
        
        # Create investment opportunity entities
        for opportunity in article_data.get('investment_opportunities', []):
            await self.kg_client.create_entity(
                entity_type="investment_opportunity",
                data={
                    **opportunity,
                    'source_article': article_data['article_id'],
                    'source': 'forbes'
                }
            )
