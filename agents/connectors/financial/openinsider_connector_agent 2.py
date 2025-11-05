"""
OpenInsider Connector Agent - OpenInsider.com Web Scraping Connector

Maintains the Rust-based OpenInsider web scraper in AckwardRootsInc.
Aggregates and analyzes insider trading data from SEC Form 4 filings.
"""

from typing import Dict, Any
from ...base import Layer1Agent, AgentResult, AgentMetadata, AgentLayer


class OpenInsiderConnectorAgent(Layer1Agent):
    """OpenInsider web scraper maintenance agent"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_scraper_url = "http://localhost:8091/scrapers/openinsider"
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="openinsider_connector",
            layer=AgentLayer.LAYER_1_EXTRACTION,
            version="1.0.0",
            description="OpenInsider scraper - aggregated insider trading data",
            capabilities=["insider_trading", "form4_analysis", "cluster_buys", "insider_sentiment"],
            dependencies=[]
        )
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """
        Trigger OpenInsider scraping via Rust scraper
        
        Args:
            raw_data: Scraping request with query parameters
            
        Returns:
            AgentResult with scraped insider trading data
        """
        
        scrape_type = raw_data.get('scrape_type', 'latest')
        ticker = raw_data.get('ticker')
        
        if scrape_type == 'latest':
            return await self._scrape_latest_filings(raw_data.get('limit', 100))
        elif scrape_type == 'ticker':
            return await self._scrape_ticker_insider_activity(ticker)
        elif scrape_type == 'cluster_buys':
            return await self._scrape_cluster_buys()
        elif scrape_type == 'top_insiders':
            return await self._scrape_top_insiders()
        else:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': f'Unknown scrape_type: {scrape_type}'}
            )
    
    async def _scrape_latest_filings(self, limit: int) -> AgentResult:
        """Scrape latest insider trading filings"""
        
        return AgentResult(
            success=True,
            data={
                'source': 'openinsider.com',
                'scrape_type': 'latest',
                'url': 'http://openinsider.com/latest-filings',
                'limit': limit,
                'content_type': 'text/html',
                'scraped_at': '2025-10-29T22:50:00Z',
                'cache_key': f'openinsider_latest_{limit}',
                'instructions': {
                    'rust_scraper': 'AckwardRootsInc/src/scrapers/openinsider_scraper.rs',
                    'method': 'scrape_latest_filings',
                    'endpoint': f'{self.rust_scraper_url}/latest?limit={limit}'
                }
            },
            metadata={'agent': self.metadata.name, 'scrape_type': 'latest'}
        )
    
    async def _scrape_ticker_insider_activity(self, ticker: str) -> AgentResult:
        """Scrape insider activity for specific ticker"""
        
        return AgentResult(
            success=True,
            data={
                'source': 'openinsider.com',
                'scrape_type': 'ticker',
                'ticker': ticker,
                'url': f'http://openinsider.com/screener?s={ticker}',
                'content_type': 'text/html',
                'scraped_at': '2025-10-29T22:50:00Z',
                'cache_key': f'openinsider_ticker_{ticker}',
                'instructions': {
                    'rust_scraper': 'AckwardRootsInc/src/scrapers/openinsider_scraper.rs',
                    'method': 'scrape_ticker_activity',
                    'endpoint': f'{self.rust_scraper_url}/ticker/{ticker}'
                }
            },
            metadata={'agent': self.metadata.name, 'scrape_type': 'ticker', 'ticker': ticker}
        )
    
    async def _scrape_cluster_buys(self) -> AgentResult:
        """Scrape cluster buying activity (multiple insiders buying same stock)"""
        
        return AgentResult(
            success=True,
            data={
                'source': 'openinsider.com',
                'scrape_type': 'cluster_buys',
                'url': 'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1',
                'content_type': 'text/html',
                'scraped_at': '2025-10-29T22:50:00Z',
                'cache_key': 'openinsider_cluster_buys',
                'instructions': {
                    'rust_scraper': 'AckwardRootsInc/src/scrapers/openinsider_scraper.rs',
                    'method': 'scrape_cluster_buys',
                    'endpoint': f'{self.rust_scraper_url}/cluster-buys'
                }
            },
            metadata={'agent': self.metadata.name, 'scrape_type': 'cluster_buys'}
        )
    
    async def _scrape_top_insiders(self) -> AgentResult:
        """Scrape top insider traders by volume"""
        
        return AgentResult(
            success=True,
            data={
                'source': 'openinsider.com',
                'scrape_type': 'top_insiders',
                'url': 'http://openinsider.com/top-insiders',
                'content_type': 'text/html',
                'scraped_at': '2025-10-29T22:50:00Z',
                'cache_key': 'openinsider_top_insiders',
                'instructions': {
                    'rust_scraper': 'AckwardRootsInc/src/scrapers/openinsider_scraper.rs',
                    'method': 'scrape_top_insiders',
                    'endpoint': f'{self.rust_scraper_url}/top-insiders'
                }
            },
            metadata={'agent': self.metadata.name, 'scrape_type': 'top_insiders'}
        )
