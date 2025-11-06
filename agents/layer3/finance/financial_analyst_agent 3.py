"""
Financial Analyst Agent - LLM-Powered Financial Analysis

Layer 3 Domain Expert agent that uses LLM to provide deep financial
analysis and recommendations.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class FinancialAnalystAgent(Layer3Agent):
    """
    Financial Analyst - LLM-powered financial analysis and recommendations
    
    Provides deep analysis of:
    - Invoice impact on cash flow
    - Expense categorization and optimization
    - Revenue forecasting
    - Budget variance analysis
    - Tax implications
    - Financial health metrics
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="financial_analyst",
            layer=AgentLayer.LAYER_3_DOMAIN,
            version="1.0.0",
            description="LLM-powered financial analysis and recommendations",
            capabilities=["financial_analysis", "cash_flow", "tax_planning", "budget_analysis", "forecasting"],
            dependencies=["quickbooks_parser", "plaid_parser"]
        )
    
    async def analyze(self, entities, context=None) -> AgentResult:
        """
        Analyze financial data and provide recommendations
        
        Args:
            entities: List of financial entities (invoices, expenses, etc.)
            context: Optional context with historical data
            
        Returns:
            AgentResult with financial analysis
        """
        
        data = context if context else {}
        analysis_type = data.get("type", "invoice")
        
        if analysis_type == "invoice":
            return await self._analyze_invoice(data)
        elif analysis_type == "expense":
            return await self._analyze_expense(data)
        elif analysis_type == "cash_flow":
            return await self._analyze_cash_flow(data)
        elif analysis_type == "budget":
            return await self._analyze_budget(data)
        else:
            return await self._general_analysis(data)
    
    async def _analyze_invoice(self, data: Dict[str, Any]) -> AgentResult:
        """Analyze invoice with LLM"""
        
        prompt = f"""You are a financial analyst. Analyze this invoice and provide recommendations.

INVOICE DATA:
{json.dumps(data, indent=2)}

ANALYZE:
1. Cash flow impact (when is payment due? do we have funds?)
2. Urgency (how critical is this payment?)
3. Negotiation opportunities (can we negotiate terms/price?)
4. Tax implications (is this deductible? what category?)
5. Budget impact (does this fit our budget?)
6. Vendor relationship (trusted vendor? payment history?)

PROVIDE RECOMMENDATIONS:
- Should we approve immediately or review?
- Can we negotiate better terms?
- Any red flags or concerns?
- Optimal payment timing?

Return as JSON:
{{
    "analysis": {{
        "cash_flow_impact": "low|medium|high",
        "urgency": "low|medium|high|urgent",
        "amount": 5000,
        "due_date": "2025-11-15",
        "days_until_due": 17,
        "available_cash": 50000,
        "cash_after_payment": 45000
    }},
    "tax": {{
        "deductible": true,
        "category": "Office Supplies",
        "estimated_tax_savings": 1250
    }},
    "recommendations": [
        "Approve - trusted vendor, within budget",
        "Schedule payment for Nov 14 (1 day before due)",
        "Consider negotiating net-60 terms for future invoices"
    ],
    "red_flags": [],
    "confidence": 0.95
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store analysis in knowledge graph
            if self.kg_client:
                await self._store_analysis_in_kg(analysis, "invoice")
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'type': 'invoice'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _analyze_expense(self, data: Dict[str, Any]) -> AgentResult:
        """Analyze expense with LLM"""
        
        prompt = f"""Analyze this expense and categorize it for tax purposes.

EXPENSE DATA:
{json.dumps(data, indent=2)}

ANALYZE:
1. Proper tax category
2. Deductibility (100%, 50%, or non-deductible)
3. Documentation requirements
4. Budget impact
5. Spending patterns (is this unusual?)

Return as JSON with analysis and recommendations.
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
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_analysis_in_kg(analysis, "expense")
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'type': 'expense'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _analyze_cash_flow(self, data: Dict[str, Any]) -> AgentResult:
        """Analyze cash flow with LLM"""
        pass
    
    async def _analyze_budget(self, data: Dict[str, Any]) -> AgentResult:
        """Analyze budget variance with LLM"""
        pass
    
    async def _general_analysis(self, data: Dict[str, Any]) -> AgentResult:
        """General financial analysis"""
        pass
    
    async def _store_analysis_in_kg(self, analysis: Dict[str, Any], analysis_type: str):
        """Store financial analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="financial_analysis",
            data={
                'type': analysis_type,
                'analysis': analysis,
                'timestamp': 'now'
            }
        )
