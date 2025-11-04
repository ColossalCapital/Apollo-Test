"""
TurboTax Parser Agent - LLM-Powered Tax Document Parsing

Layer 1 Data Extraction agent that uses LLM to parse TurboTax documents
and extract structured tax intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class TurboTaxParserAgent(Layer1Agent):
    """
    TurboTax Parser - LLM-powered tax document parsing
    
    Takes raw TurboTax documents and extracts:
    - Income sources (W-2, 1099, etc.)
    - Deductions and credits
    - Tax liability estimates
    - Refund/payment amounts
    - Filing status
    - Dependent information
    - Business expenses
    - Investment income/losses
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="turbotax_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered TurboTax document parsing with tax intelligence",
            capabilities=["tax_document_parsing", "deduction_extraction", "income_analysis", "tax_optimization"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw TurboTax document
        
        Args:
            raw_data: Raw TurboTax document (W-2, 1099, 1040, etc.)
            
        Returns:
            AgentResult with structured tax data
        """
        
        document_type = raw_data.get('document_type', 'unknown')
        
        if document_type == 'w2':
            return await self._parse_w2(raw_data)
        elif document_type == '1099':
            return await self._parse_1099(raw_data)
        elif document_type == '1040':
            return await self._parse_1040(raw_data)
        elif document_type == 'deductions':
            return await self._parse_deductions(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_w2(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse W-2 form with LLM"""
        
        prompt = f"""You are an expert tax accountant. Extract structured information from this W-2 form.

RAW W-2 DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Employer information (name, EIN, address)
2. Employee information (name, SSN, address)
3. Wages, tips, and compensation (Box 1)
4. Federal income tax withheld (Box 2)
5. Social Security wages and tax (Boxes 3-4)
6. Medicare wages and tax (Boxes 5-6)
7. State and local tax information
8. Retirement plan contributions
9. Other compensation and benefits
10. Tax year

Return as JSON:
{{
    "document_type": "w2",
    "tax_year": 2024,
    "employer": {{
        "name": "Acme Corporation",
        "ein": "12-3456789",
        "address": "123 Main St, City, ST 12345"
    }},
    "employee": {{
        "name": "John Smith",
        "ssn": "XXX-XX-1234",
        "address": "456 Oak Ave, City, ST 12345"
    }},
    "income": {{
        "wages_tips_compensation": 85000.00,
        "federal_tax_withheld": 12750.00,
        "social_security_wages": 85000.00,
        "social_security_tax": 5270.00,
        "medicare_wages": 85000.00,
        "medicare_tax": 1232.50
    }},
    "retirement": {{
        "has_retirement_plan": true,
        "contributions": 8500.00
    }},
    "state_local": [
        {{
            "state": "CA",
            "wages": 85000.00,
            "tax_withheld": 4250.00
        }}
    ],
    "other_compensation": {{
        "dependent_care_benefits": 0,
        "other": 0
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
                    "max_tokens": 2000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_tax_document_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'document_type': 'w2'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_1099(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse 1099 form with LLM"""
        
        prompt = f"""Extract information from this 1099 form (various types: MISC, NEC, INT, DIV, B, etc.).

RAW 1099 DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. 1099 type (MISC, NEC, INT, DIV, B, etc.)
2. Payer information
3. Recipient information
4. Income amounts by category
5. Tax withholding
6. Tax year

Return as JSON with appropriate fields for the 1099 type.
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
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_tax_document_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'document_type': '1099'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_1040(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse 1040 tax return with LLM"""
        
        prompt = f"""Extract comprehensive information from this 1040 Individual Tax Return.

RAW 1040 DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Filing status (single, married, head of household)
2. Personal information and dependents
3. Total income (all sources)
4. Adjustments to income
5. Adjusted Gross Income (AGI)
6. Standard or itemized deductions
7. Taxable income
8. Tax liability
9. Credits
10. Payments and withholding
11. Refund or amount owed
12. Tax optimization opportunities

Return as comprehensive JSON.
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
                await self._store_tax_document_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'document_type': '1040'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_deductions(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse deduction records with LLM"""
        
        prompt = f"""Analyze these deduction records and categorize them for tax purposes.

RAW DEDUCTION DATA:
{json.dumps(raw_data, indent=2)}

CATEGORIZE:
1. Business expenses (Schedule C)
2. Home office deduction
3. Charitable contributions
4. Medical expenses
5. State and local taxes
6. Mortgage interest
7. Education expenses
8. Retirement contributions
9. Other deductions

For each category, provide:
- Total amount
- Number of transactions
- Eligibility status
- Required documentation
- Potential audit risk

Return as JSON.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_deductions_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'document_type': 'deductions'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic tax document parsing"""
        pass
    
    async def _store_tax_document_in_kg(self, tax_data: Dict[str, Any]):
        """Store parsed tax document in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="tax_document",
            data=tax_data
        )
    
    async def _store_deductions_in_kg(self, deduction_data: Dict[str, Any]):
        """Store parsed deductions in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="tax_deductions",
            data=deduction_data
        )
