"""
State Tax Parser Agent - LLM-Powered State Tax Document Parsing

Layer 1 Data Extraction agent that uses LLM to parse scraped state tax
documents and extract structured tax intelligence.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class StateTaxParserAgent(Layer1Agent):
    """
    State Tax Parser - LLM-powered state tax document parsing
    
    Takes scraped state tax documents and extracts:
    - Tax rates and brackets
    - Deductions and credits
    - Filing requirements
    - Deadlines and due dates
    - Form instructions
    - Entity-specific rules
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="state_tax_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered state tax document parsing for all 50 states",
            capabilities=["state_tax_parsing", "rate_extraction", "form_parsing", "deadline_tracking"],
            dependencies=["state_tax_scraper"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from scraped state tax document
        
        Args:
            raw_data: Scraped state tax HTML/PDF data
            
        Returns:
            AgentResult with structured state tax data
        """
        
        state = raw_data.get('state')
        tax_type = raw_data.get('tax_type')
        document_type = raw_data.get('document_type', 'rates')
        
        if document_type == 'rates':
            return await self._parse_tax_rates(state, tax_type, raw_data)
        elif document_type == 'forms':
            return await self._parse_tax_forms(state, tax_type, raw_data)
        elif document_type == 'deductions':
            return await self._parse_deductions(state, tax_type, raw_data)
        elif document_type == 'deadlines':
            return await self._parse_deadlines(state, tax_type, raw_data)
        else:
            return await self._generic_parse(state, tax_type, raw_data)
    
    async def _parse_tax_rates(self, state: str, tax_type: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse state tax rates with LLM"""
        
        prompt = f"""You are an expert tax accountant. Extract tax rate information from this {state} {tax_type} tax document.

SCRAPED DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Tax rate structure (flat, graduated, etc.)
2. Tax brackets (if graduated)
3. Rates for each bracket
4. Standard deduction amounts
5. Personal exemptions
6. Filing status variations (single, married, etc.)
7. Tax year
8. Effective date

For {tax_type} tax, extract relevant rates:
- Personal: Individual income tax rates
- Corporate: Corporate income tax rates
- Business: Franchise tax, LLC fees, etc.
- Sales: Sales tax rates (state + local)

Return as JSON:
{{
    "state": "{state}",
    "tax_type": "{tax_type}",
    "tax_year": 2024,
    "rate_structure": "graduated",
    "brackets": [
        {{"min": 0, "max": 10000, "rate": 0.01}},
        {{"min": 10001, "max": 25000, "rate": 0.02}},
        {{"min": 25001, "max": 50000, "rate": 0.04}}
    ],
    "standard_deduction": {{
        "single": 5000,
        "married_joint": 10000,
        "married_separate": 5000,
        "head_of_household": 7500
    }},
    "personal_exemption": 150,
    "effective_date": "2024-01-01",
    "notes": ["Additional notes about rates"]
}}
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_tax_rates_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'state': state, 'tax_type': tax_type}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_tax_forms(self, state: str, tax_type: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse state tax forms with LLM"""
        
        prompt = f"""Extract information about {state} {tax_type} tax forms.

SCRAPED DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Form numbers and names
2. Form purposes
3. Who must file
4. Filing deadlines
5. Required attachments
6. Instructions summary
7. Common mistakes to avoid

Return as JSON with list of forms.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_tax_forms_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'state': state, 'tax_type': tax_type}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_deductions(self, state: str, tax_type: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse state tax deductions with LLM"""
        
        prompt = f"""Extract deduction information from this {state} {tax_type} tax document.

SCRAPED DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Available deductions
2. Eligibility requirements
3. Deduction amounts or limits
4. Phase-out thresholds
5. Required documentation
6. State-specific deductions
7. Differences from federal deductions

Return as JSON with categorized deductions.
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
                metadata={'agent': self.metadata.name, 'state': state, 'tax_type': tax_type}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_deadlines(self, state: str, tax_type: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse state tax deadlines with LLM"""
        pass
    
    async def _generic_parse(self, state: str, tax_type: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic state tax document parsing"""
        pass
    
    async def _store_tax_rates_in_kg(self, rate_data: Dict[str, Any]):
        """Store parsed tax rates in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="state_tax_rates",
            data=rate_data
        )
    
    async def _store_tax_forms_in_kg(self, form_data: Dict[str, Any]):
        """Store parsed tax forms in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="state_tax_forms",
            data=form_data
        )
    
    async def _store_deductions_in_kg(self, deduction_data: Dict[str, Any]):
        """Store parsed deductions in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="state_tax_deductions",
            data=deduction_data
        )
