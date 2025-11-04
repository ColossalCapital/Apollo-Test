"""
QuickBooks Parser Agent - LLM-Powered Invoice & Accounting Data Parsing

Layer 1 Data Extraction agent that uses LLM to parse raw QuickBooks API
responses into structured accounting data.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class QuickBooksParserAgent(Layer1Agent):
    """
    QuickBooks Parser - LLM-powered accounting data parsing
    
    Takes raw QuickBooks API responses and extracts:
    - Invoice details (amount, due date, line items)
    - Expense categorization
    - P&L insights
    - Tax implications
    - Payment status
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="quickbooks_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered QuickBooks invoice and accounting data parsing",
            capabilities=["invoice_parsing", "expense_categorization", "tax_analysis", "pl_extraction"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured accounting data from raw QuickBooks API response
        
        Args:
            raw_data: Raw QuickBooks API response (invoice, expense, etc.)
            
        Returns:
            AgentResult with structured accounting data
        """
        
        data_type = raw_data.get('type', 'invoice')
        
        if data_type == 'invoice':
            return await self._parse_invoice(raw_data)
        elif data_type == 'expense':
            return await self._parse_expense(raw_data)
        elif data_type == 'pl_report':
            return await self._parse_pl_report(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_invoice(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse invoice with LLM"""
        
        prompt = f"""You are an expert accounting data parser. Extract structured information from this QuickBooks invoice.

RAW INVOICE DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Invoice number and date
2. Customer information (name, email, company)
3. Line items (description, quantity, rate, amount)
4. Subtotal, tax, and total
5. Due date and payment terms
6. Payment status (paid, unpaid, overdue)
7. Tax implications
8. Expense categories for each line item

Return as JSON:
{{
    "invoice_number": "...",
    "invoice_date": "...",
    "customer": {{"name": "...", "email": "...", "company": "..."}},
    "line_items": [
        {{"description": "...", "quantity": 0, "rate": 0, "amount": 0, "category": "..."}}
    ],
    "subtotal": 0,
    "tax": 0,
    "total": 0,
    "due_date": "...",
    "payment_terms": "...",
    "status": "...",
    "tax_implications": "...",
    "urgency": "low|medium|high"
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
                await self._store_invoice_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={
                    'agent': self.metadata.name,
                    'type': 'invoice',
                    'model': 'phi-3-medium'
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_expense(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse expense with LLM"""
        
        prompt = f"""Extract structured expense data from this QuickBooks expense.

RAW EXPENSE DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Vendor information
2. Expense amount and date
3. Category (office supplies, travel, meals, etc.)
4. Tax deductibility
5. Receipt/documentation status
6. Payment method

Return as JSON with these fields.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_expense_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'expense'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_pl_report(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse P&L report with LLM"""
        # Similar structure to above
        pass
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic parsing for unknown QuickBooks data types"""
        pass
    
    async def _store_invoice_in_kg(self, invoice_data: Dict[str, Any]):
        """Store parsed invoice in knowledge graph"""
        if not self.kg_client:
            return
        
        # Create invoice entity
        await self.kg_client.create_entity(
            entity_type="invoice",
            data=invoice_data
        )
        
        # Create customer entity if new
        await self.kg_client.create_entity(
            entity_type="customer",
            data=invoice_data['customer']
        )
        
        # Create relationships
        await self.kg_client.create_relationship(
            from_entity="customer",
            to_entity="invoice",
            relationship_type="has_invoice"
        )
    
    async def _store_expense_in_kg(self, expense_data: Dict[str, Any]):
        """Store parsed expense in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="expense",
            data=expense_data
        )
