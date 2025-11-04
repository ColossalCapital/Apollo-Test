"""
Business Registration Parser Agent - LLM-Powered Business Entity Parsing

Layer 1 Data Extraction agent that uses LLM to parse scraped business
registration data from Secretary of State websites.
"""

from typing import Dict, Any
from ....base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class BusinessRegistrationParserAgent(Layer1Agent):
    """
    Business Registration Parser - LLM-powered entity data parsing
    
    Takes scraped Secretary of State data and extracts:
    - Entity information (name, type, status)
    - Formation and registration dates
    - Registered agent details
    - Principal office address
    - Officers and directors
    - Annual report status
    - Good standing status
    - UCC filings and liens
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="business_registration_parser",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="LLM-powered business registration parsing from Secretary of State data",
            capabilities=["entity_parsing", "compliance_status", "officer_extraction", "agent_parsing"],
            dependencies=["secretary_of_state_scraper"]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Extract structured data from scraped business registration
        
        Args:
            raw_data: Scraped Secretary of State HTML/data
            
        Returns:
            AgentResult with structured business entity data
        """
        
        return await self._parse_business_entity(raw_data)
    
    async def _parse_business_entity(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse business entity with LLM"""
        
        prompt = f"""You are an expert at parsing business registration data. Extract structured information from this Secretary of State record.

RAW BUSINESS REGISTRATION DATA:
{json.dumps(raw_data, indent=2)}

EXTRACT:
1. Entity identification (name, ID, type)
2. Formation and registration dates
3. Current status (active, dissolved, suspended, etc.)
4. Good standing status
5. Registered agent (name, address)
6. Principal office address
7. Officers and directors (names, titles)
8. Annual report status (last filed, next due)
9. UCC filings count
10. Liens or judgments
11. Business purpose (if stated)
12. Authorized shares (if corporation)

Return as JSON:
{{
    "entity_id": "C1234567",
    "entity_name": "Acme Corporation",
    "entity_type": "C-Corporation",
    "state_of_formation": "DE",
    "formation_date": "2020-01-15",
    "registration_date": "2020-01-15",
    "status": "active",
    "good_standing": true,
    "registered_agent": {{
        "name": "Corporation Service Company",
        "address": {{
            "street": "251 Little Falls Drive",
            "city": "Wilmington",
            "state": "DE",
            "zip": "19808"
        }},
        "phone": "302-555-0100"
    }},
    "principal_office": {{
        "address": {{
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102"
        }}
    }},
    "officers": [
        {{
            "name": "John Smith",
            "title": "CEO",
            "address": "123 Main St, San Francisco, CA 94102"
        }},
        {{
            "name": "Jane Doe",
            "title": "CFO",
            "address": "123 Main St, San Francisco, CA 94102"
        }},
        {{
            "name": "Bob Johnson",
            "title": "Secretary",
            "address": "123 Main St, San Francisco, CA 94102"
        }}
    ],
    "annual_report": {{
        "required": true,
        "last_filed": "2024-03-01",
        "next_due": "2025-03-01",
        "status": "current",
        "days_until_due": 123
    }},
    "ucc_filings": {{
        "count": 3,
        "active_filings": 2,
        "terminated_filings": 1
    }},
    "liens_judgments": {{
        "count": 0,
        "details": []
    }},
    "business_purpose": "Software development and technology services",
    "authorized_shares": {{
        "common": 10000000,
        "preferred": 1000000
    }},
    "compliance_alerts": [
        {{
            "type": "annual_report_due",
            "due_date": "2025-03-01",
            "days_remaining": 123,
            "severity": "medium"
        }}
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
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            parsed_data = json.loads(llm_response['choices'][0]['message']['content'])
            
            # Store in knowledge graph
            if self.kg_client:
                await self._store_business_entity_in_kg(parsed_data)
            
            return AgentResult(
                success=True,
                data=parsed_data,
                metadata={'agent': self.metadata.name, 'source': 'secretary_of_state'}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_business_entity_in_kg(self, entity_data: Dict[str, Any]):
        """Store parsed business entity in knowledge graph"""
        if not self.kg_client:
            return
        
        # Create business entity
        await self.kg_client.create_entity(
            entity_type="business_entity",
            data=entity_data
        )
        
        # Create officer entities
        for officer in entity_data.get('officers', []):
            await self.kg_client.create_entity(
                entity_type="officer",
                data=officer
            )
            
            # Create relationship
            await self.kg_client.create_relationship(
                from_entity=officer['name'],
                to_entity=entity_data['entity_name'],
                relationship_type='officer_of',
                properties={'title': officer['title']}
            )
        
        # Create compliance alerts
        for alert in entity_data.get('compliance_alerts', []):
            await self.kg_client.create_entity(
                entity_type="compliance_alert",
                data={
                    **alert,
                    'entity_id': entity_data['entity_id'],
                    'entity_name': entity_data['entity_name']
                }
            )
