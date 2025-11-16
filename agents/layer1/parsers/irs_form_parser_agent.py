"""
IRS Form Parser Agent - LLM-Powered IRS Tax Form Parsing

Layer 1 Data Extraction agent that uses LLM to parse various IRS forms
beyond what TurboTax provides (K-1, 1120, 1065, etc.).
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class IRSFormParserAgent(Layer1Agent):
    """
    IRS Form Parser - LLM-powered parsing of complex IRS forms
    
    Takes raw IRS forms and extracts:
    - Schedule K-1 (Partnership/S-Corp income)
    - Form 1120 (Corporate tax return)
    - Form 1065 (Partnership return)
    - Form 5471 (Foreign corporation)
    - Form 8949 (Capital gains/losses)
    - Schedule D (Capital gains summary)
    - Form 4562 (Depreciation)
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="irs_form_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered IRS form parsing for complex business and investment forms",
            capabilities=["k1_parsing", "corporate_returns", "partnership_returns", "capital_gains"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw IRS form
        
        Args:
            raw_data: Raw IRS form data
            
        Returns:
            AgentResult with structured tax data
        """
        
        form_type = raw_data.get('form_type', 'unknown')
        
        if form_type == 'k1':
            return await self._parse_k1(raw_data)
        elif form_type == '1120':
            return await self._parse_1120(raw_data)
        elif form_type == '8949':
            return await self._parse_8949(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_k1(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Schedule K-1 with LLM"""
        
        prompt = f"""You are an expert tax accountant. Extract structured information from this Schedule K-1.

RAW K-1 DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Entity information (Partnership/S-Corp name, EIN)
2. Partner/shareholder information (name, SSN, ownership %)
3. Ordinary business income/loss
4. Net rental real estate income/loss
5. Other net rental income/loss
6. Guaranteed payments
7. Interest income
8. Dividend income
9. Royalties
10. Net short-term capital gain/loss
11. Net long-term capital gain/loss
12. Section 179 deduction
13. Other deductions
14. Self-employment earnings
15. Credits
16. Foreign transactions
17. Alternative minimum tax items

Return as JSON:
{{
    "form_type": "k1",
    "entity_type": "partnership",
    "tax_year": 2024,
    "entity": {{
        "name": "ABC Partners LLC",
        "ein": "12-3456789",
        "address": "123 Main St, City, ST 12345"
    }},
    "partner": {{
        "name": "John Smith",
        "ssn": "XXX-XX-1234",
        "ownership_percent": 25.0,
        "partner_type": "general"
    }},
    "income": {{
        "ordinary_business_income": 50000.00,
        "net_rental_real_estate": 12000.00,
        "other_rental": 0,
        "guaranteed_payments": 0,
        "interest": 500.00,
        "dividends": 1000.00,
        "royalties": 0
    }},
    "capital_gains": {{
        "short_term": 2000.00,
        "long_term": 5000.00,
        "section_1231": 0
    }},
    "deductions": {{
        "section_179": 10000.00,
        "charitable": 1000.00,
        "other": 500.00
    }},
    "self_employment": {{
        "earnings": 50000.00,
        "subject_to_se_tax": true
    }},
    "credits": {{
        "low_income_housing": 0,
        "other": 0
    }},
    "foreign": {{
        "foreign_transactions": false,
        "foreign_taxes_paid": 0
    }},
    "amt_items": {{
        "adjustments": 0,
        "preferences": 0
    }}
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_tax_form_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'form_type': 'k1'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_1120(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Form 1120 (Corporate Tax Return) with LLM"""
        pass
    
    async def _parse_8949(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse Form 8949 (Capital Gains/Losses) with LLM"""
        
        prompt = f"""Extract all capital gains and losses from this Form 8949.

RAW 8949 DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Short-term vs long-term transactions
2. For each transaction:
   - Description of property
   - Date acquired
   - Date sold
   - Proceeds
   - Cost basis
   - Adjustments
   - Gain or loss
3. Wash sale adjustments
4. Total gains/losses by category

Return as JSON.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_tax_form_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'form_type': '8949'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic IRS form parsing"""
        pass
    
    async def _store_tax_form_in_kg(self, form_data: Dict[str, Any]):
        """Store parsed IRS form in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="irs_form",
            data=form_data
        )
