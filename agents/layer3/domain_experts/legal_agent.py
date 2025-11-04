"""
Legal Agent - LLM-Powered Legal Analysis and Compliance

Layer 3 Domain Expert agent that uses LLM to provide legal analysis,
contract review, and compliance guidance.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class LegalAgent(Layer3Agent):
    """
    Legal Agent - LLM-powered legal analysis
    
    Provides:
    - Contract review and analysis
    - Legal risk assessment
    - Compliance guidance
    - Entity structure recommendations
    - Regulatory analysis
    - IP protection strategies
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="legal_agent",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered legal analysis, contract review, and compliance guidance",
            capabilities=["contract_review", "legal_risk", "compliance", "entity_structure", "ip_protection"],
            dependencies=["document_parser", "company_recognition"]
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """
        Provide legal analysis and guidance
        
        Args:
            domain_data: Data requiring legal analysis
            
        Returns:
            AgentResult with legal insights and recommendations
        """
        
        analysis_type = domain_data.get('analysis_type', 'contract_review')
        
        if analysis_type == 'contract_review':
            return await self._review_contract(domain_data)
        elif analysis_type == 'entity_structure':
            return await self._analyze_entity_structure(domain_data)
        elif analysis_type == 'compliance':
            return await self._assess_compliance(domain_data)
        elif analysis_type == 'ip_protection':
            return await self._analyze_ip_protection(domain_data)
        else:
            return await self._general_legal_analysis(domain_data)
    
    async def _review_contract(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Review and analyze contract with LLM"""
        
        prompt = f"""You are an expert corporate attorney. Review this contract and provide comprehensive legal analysis.

CONTRACT DATA:
{json.dumps(domain_data, indent=2)}

ANALYZE:
1. Contract type and parties
2. Key terms and obligations
3. Payment terms and conditions
4. Termination clauses
5. Liability and indemnification
6. Intellectual property rights
7. Confidentiality provisions
8. Dispute resolution mechanisms
9. Legal risks and red flags
10. Missing or weak clauses
11. Negotiation recommendations
12. Overall risk assessment

Return as JSON:
{{
    "contract_id": "...",
    "contract_type": "service_agreement",
    "parties": [
        {{"name": "Company A", "role": "service_provider"}},
        {{"name": "Company B", "role": "client"}}
    ],
    "key_terms": {{
        "scope_of_work": "Software development services",
        "duration": "12 months",
        "auto_renewal": true,
        "notice_period": "90 days"
    }},
    "payment_terms": {{
        "structure": "monthly_retainer",
        "amount": 50000,
        "currency": "USD",
        "payment_schedule": "net_30",
        "late_fees": "1.5% per month"
    }},
    "termination": {{
        "for_cause": true,
        "for_convenience": true,
        "notice_required": "30 days",
        "termination_fee": 0
    }},
    "liability": {{
        "cap": "12_months_fees",
        "exclusions": ["indirect_damages", "lost_profits"],
        "indemnification": "mutual"
    }},
    "ip_rights": {{
        "work_product_ownership": "client",
        "pre_existing_ip": "provider_retains",
        "license_grant": "perpetual_non_exclusive"
    }},
    "confidentiality": {{
        "duration": "5 years post-termination",
        "exceptions": ["public_domain", "independently_developed"],
        "return_of_materials": true
    }},
    "dispute_resolution": {{
        "method": "arbitration",
        "venue": "Delaware",
        "governing_law": "Delaware"
    }},
    "legal_risks": [
        {{
            "risk": "Unlimited liability for IP infringement",
            "severity": "high",
            "recommendation": "Add IP indemnification cap"
        }},
        {{
            "risk": "Weak termination rights",
            "severity": "medium",
            "recommendation": "Add performance-based termination clause"
        }}
    ],
    "missing_clauses": [
        "Force majeure",
        "Assignment restrictions",
        "Warranty disclaimers"
    ],
    "negotiation_points": [
        "Reduce liability cap to 6 months fees",
        "Add performance metrics for termination",
        "Include force majeure clause",
        "Clarify IP ownership for derivative works"
    ],
    "risk_assessment": {{
        "overall_risk": "medium",
        "enforceability": "high",
        "fairness": "slightly_favors_provider",
        "recommendation": "Negotiate key terms before signing"
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
                    "max_tokens": 4000
                }
            )
            
            llm_response = response.json()
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_legal_analysis_in_kg(analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'analysis_type': 'contract_review'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _analyze_entity_structure(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Analyze optimal entity structure with LLM"""
        
        prompt = f"""You are an expert business attorney specializing in entity formation. Analyze the optimal entity structure for this business.

BUSINESS DATA:
{json.dumps(domain_data, indent=2)}

ANALYZE:
1. Business type and industry
2. Number of owners and roles
3. Revenue projections
4. Liability concerns
5. Tax considerations
6. Funding plans
7. Exit strategy
8. Recommended entity types (LLC, S-Corp, C-Corp, Partnership)
9. State of formation recommendation
10. Governance structure
11. Operating agreement key terms
12. Compliance requirements

Provide detailed recommendations with pros/cons for each option.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 3500
                }
            )
            
            llm_response = response.json()
            analysis = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_legal_analysis_in_kg(analysis)
            
            return AgentResult(
                success=True,
                data=analysis,
                metadata={'agent': self.metadata.name, 'analysis_type': 'entity_structure'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _assess_compliance(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Assess regulatory compliance with LLM"""
        pass
    
    async def _analyze_ip_protection(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Analyze IP protection strategy with LLM"""
        pass
    
    async def _general_legal_analysis(self, domain_data: Dict[str, Any]) -> AgentResult:
        """General legal analysis with LLM"""
        pass
    
    async def _store_legal_analysis_in_kg(self, analysis: Dict[str, Any]):
        """Store legal analysis in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="legal_analysis",
            data=analysis
        )
