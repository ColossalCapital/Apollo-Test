"""
Document Parser Agent - LLM-Powered Document Parsing

Layer 1 Data Extraction agent that uses LLM to parse raw documents
(PDFs, Word docs, etc.) into structured data.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class DocumentParserAgent(Layer1Agent):
    """
    Document Parser - LLM-powered document parsing
    
    Takes raw document data and extracts:
    - Document type (contract, invoice, report, etc.)
    - Key information (parties, dates, amounts)
    - Structured content
    - Action items
    - Important clauses
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="document_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered document parsing and extraction",
            capabilities=["document_parsing", "contract_analysis", "pdf_extraction", "content_structuring"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from raw document
        
        Args:
            raw_data: Raw document data (text, OCR output, etc.)
            
        Returns:
            AgentResult with structured document data
        """
        
        document_type = raw_data.get('type', 'unknown')
        
        if document_type == 'contract':
            return await self._parse_contract(raw_data)
        elif document_type == 'invoice':
            return await self._parse_invoice(raw_data)
        elif document_type == 'report':
            return await self._parse_report(raw_data)
        else:
            return await self._generic_parse(raw_data)
    
    async def _parse_contract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse contract with LLM"""
        
        prompt = f"""You are an expert contract parser. Extract structured information from this contract.

RAW CONTRACT TEXT:
{raw_data.get('text', '')[:4000]}  # Limit to 4000 chars

EXTRACT:
1. Contract type (NDA, service agreement, employment, etc.)
2. Parties involved (names, roles)
3. Effective date and term
4. Key obligations for each party
5. Payment terms (if applicable)
6. Termination clauses
7. Important deadlines
8. Renewal terms
9. Liability limitations
10. Governing law

Return as JSON:
{{
    "contract_type": "Service Agreement",
    "parties": [
        {{"name": "Acme Corp", "role": "Client"}},
        {{"name": "Our Company", "role": "Service Provider"}}
    ],
    "effective_date": "2025-11-01",
    "term": "12 months",
    "auto_renewal": true,
    "payment_terms": {{
        "amount": 10000,
        "frequency": "monthly",
        "due_date": "1st of month"
    }},
    "key_obligations": {{
        "client": ["Pay monthly fee", "Provide access to systems"],
        "provider": ["Deliver services", "Maintain confidentiality"]
    }},
    "termination": {{
        "notice_period": "30 days",
        "conditions": ["Material breach", "Non-payment"]
    }},
    "important_dates": [
        {{"date": "2025-11-01", "event": "Contract start"}},
        {{"date": "2026-11-01", "event": "Renewal decision"}}
    ],
    "red_flags": [],
    "action_items": [
        "Set reminder 60 days before renewal",
        "Schedule monthly invoicing"
    ]
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
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_contract_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'contract'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _parse_invoice(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse invoice document with LLM"""
        # Similar to contract parsing but for invoices
        pass
    
    async def _parse_report(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse report document with LLM"""
        pass
    
    async def _generic_parse(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Generic document parsing"""
        
        prompt = f"""Parse this document and extract key information.

DOCUMENT TEXT:
{raw_data.get('text', '')[:4000]}

EXTRACT:
1. Document type
2. Main topic/subject
3. Key entities (people, companies, dates, amounts)
4. Summary (2-3 sentences)
5. Action items
6. Important dates

Return as JSON.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1500
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_document_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'type': 'generic'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_contract_in_kg(self, contract_data: Dict[str, Any]):
        """Store parsed contract in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="contract",
            data=contract_data
        )
        
        # Create entities for parties
        for party in contract_data.get('parties', []):
            await self.kg_client.create_entity(
                entity_type="company",
                data={'name': party['name'], 'role': party['role']}
            )
    
    async def _store_document_in_kg(self, document_data: Dict[str, Any]):
        """Store parsed document in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="document",
            data=document_data
        )
