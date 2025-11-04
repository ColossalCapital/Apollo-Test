"""
Tax Agent - LLM-Powered Tax Analysis and Planning

Layer 3 Domain Expert agent that uses LLM to provide tax analysis,
planning strategies, and optimization recommendations.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class TaxAgent(Layer3Agent):
    """
    Tax Agent - LLM-powered tax analysis and planning
    
    Provides:
    - Tax liability estimation
    - Tax optimization strategies
    - Deduction recommendations
    - Entity structure tax implications
    - Multi-state tax analysis
    - Estimated tax calculations
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="tax_agent",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered tax analysis, planning, and optimization",
            capabilities=["tax_estimation", "tax_optimization", "deduction_analysis", "multi_state_tax", "entity_tax"],
            dependencies=["turbotax_parser", "irs_form_parser", "state_tax_parser"]
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """
        Provide tax analysis and recommendations
        
        Args:
            domain_data: Financial data requiring tax analysis
            
        Returns:
            AgentResult with tax insights and strategies
        """
        
        analysis_type = domain_data.get('analysis_type', 'tax_estimation')
        
        if analysis_type == 'tax_estimation':
            return await self._estimate_tax_liability(domain_data)
        elif analysis_type == 'tax_optimization':
            return await self._optimize_tax_strategy(domain_data)
        elif analysis_type == 'entity_comparison':
            return await self._compare_entity_tax(domain_data)
        elif analysis_type == 'multi_state':
            return await self._analyze_multi_state_tax(domain_data)
        else:
            return await self._general_tax_analysis(domain_data)
    
    async def _estimate_tax_liability(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Estimate tax liability with LLM"""
        
        prompt = f"""You are an expert tax accountant (CPA). Estimate the tax liability for this taxpayer.

FINANCIAL DATA:
{json.dumps(domain_data, indent=2)}

CALCULATE:
1. Gross income (all sources)
2. Adjustments to income
3. Adjusted Gross Income (AGI)
4. Standard vs itemized deductions
5. Taxable income
6. Federal tax liability
7. State tax liability
8. Self-employment tax (if applicable)
9. Alternative Minimum Tax (AMT) check
10. Tax credits
11. Total tax liability
12. Estimated tax payments needed
13. Refund or amount owed

Return as JSON:
{{
    "tax_year": 2024,
    "filing_status": "married_filing_jointly",
    "income": {{
        "w2_wages": 150000,
        "business_income": 75000,
        "investment_income": 25000,
        "other_income": 5000,
        "total_gross_income": 255000
    }},
    "adjustments": {{
        "self_employment_tax_deduction": 5297,
        "retirement_contributions": 20000,
        "hsa_contributions": 7750,
        "total_adjustments": 33047
    }},
    "agi": 221953,
    "deductions": {{
        "standard_deduction": 29200,
        "itemized_deduction": 35000,
        "recommended": "itemized",
        "chosen_deduction": 35000
    }},
    "taxable_income": 186953,
    "federal_tax": {{
        "ordinary_income_tax": 32584,
        "capital_gains_tax": 3750,
        "self_employment_tax": 10594,
        "amt": 0,
        "total_before_credits": 46928
    }},
    "tax_credits": {{
        "child_tax_credit": 4000,
        "energy_credits": 2000,
        "total_credits": 6000
    }},
    "federal_tax_liability": 40928,
    "state_tax": {{
        "state": "CA",
        "taxable_income": 186953,
        "state_tax_liability": 14956
    }},
    "total_tax_liability": 55884,
    "estimated_payments": {{
        "q1": 13971,
        "q2": 13971,
        "q3": 13971,
        "q4": 13971,
        "total": 55884
    }},
    "withholding": {{
        "federal_withheld": 22500,
        "state_withheld": 9000,
        "total_withheld": 31500
    }},
    "balance": {{
        "federal": -18428,
        "state": -5956,
        "total_owed": 24384
    }},
    "effective_tax_rate": 0.219,
    "marginal_tax_rate": 0.24
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_tax_analysis_in_kg(analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'analysis_type': 'tax_estimation'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _optimize_tax_strategy(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Optimize tax strategy with LLM"""
        
        prompt = f"""You are an expert tax strategist. Analyze this taxpayer's situation and provide tax optimization strategies.

TAXPAYER DATA:
{json.dumps(domain_data, indent=2)}

PROVIDE:
1. Current tax situation analysis
2. Missed deductions and credits
3. Retirement contribution strategies
4. Business expense optimization
5. Income timing strategies
6. Entity structure recommendations
7. State tax optimization
8. Estimated tax savings for each strategy
9. Implementation timeline
10. Risk assessment

Return comprehensive tax optimization plan as JSON.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_tax_analysis_in_kg(analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'analysis_type': 'tax_optimization'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _compare_entity_tax(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Compare tax implications of different entity structures"""
        pass
    
    async def _analyze_multi_state_tax(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Analyze multi-state tax obligations"""
        pass
    
    async def _general_tax_analysis(self, domain_data: Dict[str, Any]) -> AgentResult:
        """General tax analysis"""
        pass
    
    async def _store_tax_analysis_in_kg(self, analysis: Dict[str, Any]):
        """Store tax analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="tax_analysis",
            data=analysis
        )
