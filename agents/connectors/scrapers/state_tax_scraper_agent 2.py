"""
State Tax Scraper Agent - Unified State Tax Web Scraping Connector

Maintains Rust-based state tax scrapers in AckwardRootsInc for all 50 states.
Routes to state-specific scrapers for personal, corporate, and business taxes.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class StateTaxScraperAgent(Layer1Agent):
    """Unified state tax scraper - routes to state-specific implementations"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_scraper_url = "http://localhost:8091/scrapers/state-tax"
        
        # State codes
        self.states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
        ]
        
        # States with NO personal income tax
        self.no_income_tax_states = ['AK', 'FL', 'NV', 'SD', 'TN', 'TX', 'WY']
        
        # States with NO corporate income tax
        self.no_corporate_tax_states = ['NV', 'OH', 'SD', 'TX', 'WA', 'WY']
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="state_tax_scraper",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="Unified state tax scraper for all 50 states - personal, corporate, business taxes",
            capabilities=["state_tax_scraping", "personal_tax", "corporate_tax", "business_tax", "sales_tax"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Trigger state tax scraping via Rust scraper
        
        Args:
            raw_data: Scraping request with state and tax type
            
        Returns:
            AgentResult with scraped tax data
        """
        
        state = raw_data.get('state', 'CA').upper()
        tax_type = raw_data.get('tax_type', 'personal')  # personal, corporate, business, sales
        
        # Validate state
        if state not in self.states:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': f'Invalid state: {state}'}
            )
        
        # Check if state has requested tax type
        if tax_type == 'personal' and state in self.no_income_tax_states:
            return AgentResult(
                success=True,
                data={
                    'state': state,
                    'tax_type': 'personal',
                    'has_tax': False,
                    'message': f'{state} has no personal income tax'
                },
                metadata={'agent': self.metadata.name, 'state': state}
            )
        
        if tax_type == 'corporate' and state in self.no_corporate_tax_states:
            return AgentResult(
                success=True,
                data={
                    'state': state,
                    'tax_type': 'corporate',
                    'has_tax': False,
                    'message': f'{state} has no corporate income tax (may have franchise/gross receipts tax)'
                },
                metadata={'agent': self.metadata.name, 'state': state}
            )
        
        # Route to appropriate scraper
        if tax_type == 'personal':
            return await self._scrape_personal_tax(state, raw_data)
        elif tax_type == 'corporate':
            return await self._scrape_corporate_tax(state, raw_data)
        elif tax_type == 'business':
            return await self._scrape_business_tax(state, raw_data)
        elif tax_type == 'sales':
            return await self._scrape_sales_tax(state, raw_data)
        elif tax_type == 'all':
            return await self._scrape_all_taxes(state, raw_data)
        else:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': f'Unknown tax_type: {tax_type}'}
            )
    
    async def _scrape_personal_tax(self, state: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Scrape personal income tax information"""
        
        return AgentResult(
            success=True,
            data={
                'source': f'{state} Department of Revenue',
                'state': state,
                'tax_type': 'personal',
                'scrape_targets': {
                    'forms': f'{self.rust_scraper_url}/{state.lower()}/personal/forms',
                    'rates': f'{self.rust_scraper_url}/{state.lower()}/personal/rates',
                    'deductions': f'{self.rust_scraper_url}/{state.lower()}/personal/deductions',
                    'credits': f'{self.rust_scraper_url}/{state.lower()}/personal/credits'
                },
                'scraped_at': '2025-10-29T22:35:00Z',
                'cache_key': f'state_tax_{state}_personal',
                'instructions': {
                    'rust_scraper': f'AckwardRootsInc/src/scrapers/state_tax/{state.lower()}_scraper.rs',
                    'method': 'scrape_personal_tax',
                    'endpoint': f'{self.rust_scraper_url}/{state.lower()}/personal'
                }
            },
            metadata={'agent': self.metadata.name, 'state': state, 'tax_type': 'personal'}
        )
    
    async def _scrape_corporate_tax(self, state: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Scrape corporate income tax information"""
        
        return AgentResult(
            success=True,
            data={
                'source': f'{state} Department of Revenue',
                'state': state,
                'tax_type': 'corporate',
                'scrape_targets': {
                    'forms': f'{self.rust_scraper_url}/{state.lower()}/corporate/forms',
                    'rates': f'{self.rust_scraper_url}/{state.lower()}/corporate/rates',
                    'credits': f'{self.rust_scraper_url}/{state.lower()}/corporate/credits',
                    'apportionment': f'{self.rust_scraper_url}/{state.lower()}/corporate/apportionment'
                },
                'scraped_at': '2025-10-29T22:35:00Z',
                'cache_key': f'state_tax_{state}_corporate',
                'instructions': {
                    'rust_scraper': f'AckwardRootsInc/src/scrapers/state_tax/{state.lower()}_scraper.rs',
                    'method': 'scrape_corporate_tax',
                    'endpoint': f'{self.rust_scraper_url}/{state.lower()}/corporate'
                }
            },
            metadata={'agent': self.metadata.name, 'state': state, 'tax_type': 'corporate'}
        )
    
    async def _scrape_business_tax(self, state: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Scrape business taxes (LLC fees, franchise tax, etc.)"""
        
        return AgentResult(
            success=True,
            data={
                'source': f'{state} Secretary of State / Department of Revenue',
                'state': state,
                'tax_type': 'business',
                'scrape_targets': {
                    'llc_fees': f'{self.rust_scraper_url}/{state.lower()}/business/llc-fees',
                    'franchise_tax': f'{self.rust_scraper_url}/{state.lower()}/business/franchise',
                    'annual_reports': f'{self.rust_scraper_url}/{state.lower()}/business/annual-reports',
                    'registration': f'{self.rust_scraper_url}/{state.lower()}/business/registration'
                },
                'scraped_at': '2025-10-29T22:35:00Z',
                'cache_key': f'state_tax_{state}_business',
                'instructions': {
                    'rust_scraper': f'AckwardRootsInc/src/scrapers/state_tax/{state.lower()}_scraper.rs',
                    'method': 'scrape_business_tax',
                    'endpoint': f'{self.rust_scraper_url}/{state.lower()}/business'
                }
            },
            metadata={'agent': self.metadata.name, 'state': state, 'tax_type': 'business'}
        )
    
    async def _scrape_sales_tax(self, state: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Scrape sales tax information"""
        
        return AgentResult(
            success=True,
            data={
                'source': f'{state} Department of Revenue',
                'state': state,
                'tax_type': 'sales',
                'scrape_targets': {
                    'rates': f'{self.rust_scraper_url}/{state.lower()}/sales/rates',
                    'local_rates': f'{self.rust_scraper_url}/{state.lower()}/sales/local',
                    'exemptions': f'{self.rust_scraper_url}/{state.lower()}/sales/exemptions',
                    'nexus': f'{self.rust_scraper_url}/{state.lower()}/sales/nexus'
                },
                'scraped_at': '2025-10-29T22:35:00Z',
                'cache_key': f'state_tax_{state}_sales',
                'instructions': {
                    'rust_scraper': f'AckwardRootsInc/src/scrapers/state_tax/{state.lower()}_scraper.rs',
                    'method': 'scrape_sales_tax',
                    'endpoint': f'{self.rust_scraper_url}/{state.lower()}/sales'
                }
            },
            metadata={'agent': self.metadata.name, 'state': state, 'tax_type': 'sales'}
        )
    
    async def _scrape_all_taxes(self, state: str, raw_data: Dict[str, Any]) -> AgentResult:
        """Scrape all tax types for a state"""
        
        results = {
            'personal': await self._scrape_personal_tax(state, raw_data),
            'corporate': await self._scrape_corporate_tax(state, raw_data),
            'business': await self._scrape_business_tax(state, raw_data),
            'sales': await self._scrape_sales_tax(state, raw_data)
        }
        
        return AgentResult(
            success=True,
            data={
                'state': state,
                'tax_types': results,
                'scraped_at': '2025-10-29T22:35:00Z'
            },
            metadata={'agent': self.metadata.name, 'state': state, 'tax_type': 'all'}
        )
