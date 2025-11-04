# 🕷️ Web Scraping Connector Architecture

**Goal:** Create Rust-based web scraping connectors in AckwardRootsInc for sites without APIs

---

## 🎯 **Architecture Overview**

### **Current System:**
```
API-based:
Atlas → Apollo Connector Agent → AckwardRootsInc Rust Connector → API → Data
                                                                      ↓
                                                            Apollo Parser Agent
```

### **New Web Scraping System:**
```
Web Scraping:
Atlas → Apollo Scraper Agent → AckwardRootsInc Rust Scraper → Website → HTML
                                                                          ↓
                                                              Apollo Parser Agent
```

---

## 🛠️ **Rust Scraping Stack**

### **Core Libraries:**
```rust
[dependencies]
reqwest = "0.11"           # HTTP client
scraper = "0.17"           # HTML parsing (CSS selectors)
select = "0.6"             # Alternative HTML parser
headless_chrome = "1.0"    # For JavaScript-heavy sites
tokio = "1.0"              # Async runtime
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

### **Features:**
- **Headless browser** for JS-rendered content
- **Rate limiting** to respect robots.txt
- **Retry logic** with exponential backoff
- **Caching** to minimize requests
- **User-agent rotation** to avoid blocking
- **Proxy support** for distributed scraping

---

## 📋 **Priority Web Scraping Targets**

### **1. IRS.gov (Tax Information)**
**Why:** No API, critical tax data
**What to scrape:**
- Tax forms (PDF downloads)
- Tax publications
- Tax guidance and FAQs
- Tax rate tables
- Filing deadlines

**Rust Connector:** `irs_scraper`
**Apollo Agent:** `IRSScraperAgent` + `IRSFormParserAgent`

```rust
// AckwardRootsInc/src/scrapers/irs_scraper.rs
pub struct IRSScraper {
    client: reqwest::Client,
    base_url: String,
}

impl IRSScraper {
    pub async fn scrape_form(&self, form_number: &str) -> Result<Vec<u8>> {
        // Download PDF form
        let url = format!("{}/pub/irs-pdf/f{}.pdf", self.base_url, form_number);
        let response = self.client.get(&url).send().await?;
        Ok(response.bytes().await?.to_vec())
    }
    
    pub async fn scrape_tax_rates(&self, year: u32) -> Result<TaxRates> {
        // Scrape tax rate tables
    }
}
```

---

### **2. SEC EDGAR (Company Filings)**
**Why:** API exists but limited, scraping provides more flexibility
**What to scrape:**
- 10-K annual reports
- 10-Q quarterly reports
- 8-K current reports
- Proxy statements (DEF 14A)
- Insider trading (Form 4)

**Rust Connector:** `sec_edgar_scraper`
**Apollo Agent:** `SECScraperAgent` + `SECFilingParserAgent`

```rust
// AckwardRootsInc/src/scrapers/sec_edgar_scraper.rs
pub struct SECEdgarScraper {
    client: reqwest::Client,
    base_url: String,
}

impl SECEdgarScraper {
    pub async fn scrape_10k(&self, cik: &str, year: u32) -> Result<Filing> {
        // Scrape 10-K filing
        let url = format!("{}/cgi-bin/browse-edgar", self.base_url);
        // Parse HTML, extract filing data
    }
    
    pub async fn scrape_insider_trades(&self, cik: &str) -> Result<Vec<InsiderTrade>> {
        // Scrape Form 4 insider trading data
    }
}
```

---

### **3. State Tax Agencies**
**Why:** No unified API, each state different
**What to scrape:**
- State tax forms
- State tax rates
- State filing requirements
- State-specific deductions

**Rust Connector:** `state_tax_scraper`
**Apollo Agent:** `StateTaxScraperAgent` + `StateTaxParserAgent`

---

### **4. Court Records (PACER, State Courts)**
**Why:** Critical for legal research, no comprehensive API
**What to scrape:**
- Federal court dockets (PACER)
- State court records
- Case filings and decisions
- Judgments and liens

**Rust Connector:** `court_records_scraper`
**Apollo Agent:** `CourtRecordsScraperAgent` + `CourtRecordsParserAgent`

---

### **5. Property Records**
**Why:** County assessor sites, no APIs
**What to scrape:**
- Property valuations
- Tax assessments
- Ownership history
- Liens and encumbrances

**Rust Connector:** `property_records_scraper`
**Apollo Agent:** `PropertyScraperAgent` + `PropertyParserAgent`

---

### **6. Business Registries**
**Why:** Secretary of State sites, limited APIs
**What to scrape:**
- Business entity information
- Registered agents
- Annual reports
- Good standing status

**Rust Connector:** `business_registry_scraper`
**Apollo Agent:** `BusinessRegistryScraperAgent` + `BusinessRegistryParserAgent`

---

## 🏗️ **Implementation Pattern**

### **Step 1: Create Rust Scraper (AckwardRootsInc)**
```rust
// AckwardRootsInc/src/scrapers/irs_scraper.rs
pub struct IRSScraper {
    client: reqwest::Client,
    cache: Cache,
    rate_limiter: RateLimiter,
}

impl IRSScraper {
    pub async fn scrape(&self, target: &str) -> Result<ScrapedData> {
        // Check cache
        if let Some(cached) = self.cache.get(target) {
            return Ok(cached);
        }
        
        // Rate limit
        self.rate_limiter.wait().await;
        
        // Scrape
        let response = self.client.get(target).send().await?;
        let html = response.text().await?;
        
        // Parse HTML
        let document = scraper::Html::parse_document(&html);
        
        // Extract data
        let data = self.extract_data(&document)?;
        
        // Cache
        self.cache.set(target, &data);
        
        Ok(data)
    }
}
```

### **Step 2: Create Apollo Scraper Agent**
```python
# Apollo/agents/connectors/scrapers/irs_scraper_agent.py
class IRSScraperAgent(Layer1Agent):
    """IRS.gov web scraper maintenance agent"""
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.rust_scraper_url = "http://localhost:8091/scrapers/irs"
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Trigger Rust scraper and return raw HTML/data"""
        target = raw_data.get('target')  # e.g., "form/1040"
        
        # Call Rust scraper
        response = await self.client.post(
            f"{self.rust_scraper_url}/scrape",
            json={"target": target}
        )
        
        scraped_data = response.json()
        
        return AgentResult(
            success=True,
            data=scraped_data,
            metadata={'agent': self.metadata.name, 'source': 'irs.gov'}
        )
```

### **Step 3: Create Apollo Parser Agent**
```python
# Apollo/agents/layer1/parsers/irs_scraped_parser_agent.py
class IRSScrapedParserAgent(Layer1Agent):
    """Parse scraped IRS.gov data with LLM"""
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        """Parse scraped HTML/PDF with LLM"""
        
        prompt = f"""Extract structured information from this IRS document.
        
        RAW DATA:
        {json.dumps(raw_data, indent=2)}
        
        EXTRACT: [specific fields based on document type]
        """
        
        # LLM parsing logic...
```

---

## 🔒 **Legal & Ethical Considerations**

### **Must Follow:**
1. **robots.txt** - Always respect robots.txt
2. **Rate limiting** - Don't overload servers
3. **Terms of Service** - Check each site's ToS
4. **User-Agent** - Identify ourselves properly
5. **Caching** - Cache aggressively to minimize requests

### **Best Practices:**
- Scrape during off-peak hours
- Use exponential backoff on errors
- Respect `Crawl-delay` directives
- Don't scrape personal data without consent
- Public data only (IRS forms, SEC filings, etc.)

---

## 📊 **Scraper Priority List**

**High Priority (Immediate):**
1. ✅ IRS.gov - Tax forms and guidance
2. ✅ SEC EDGAR - Company filings
3. ✅ State Tax Agencies - State-specific tax info

**Medium Priority (Next):**
4. ⏳ PACER - Federal court records
5. ⏳ Property Records - County assessor sites
6. ⏳ Business Registries - Secretary of State

**Low Priority (Future):**
7. ⏳ USPTO - Patent/trademark data
8. ⏳ BLS - Labor statistics
9. ⏳ Census - Demographic data

---

## 🚀 **Implementation Steps**

### **Phase 1: IRS Scraper (Week 1)**
1. Create `irs_scraper.rs` in AckwardRootsInc
2. Implement form download logic
3. Add caching and rate limiting
4. Create `IRSScraperAgent` in Apollo
5. Create `IRSScrapedParserAgent` with LLM
6. Test with common forms (1040, W-2, etc.)

### **Phase 2: SEC EDGAR Scraper (Week 2)**
1. Create `sec_edgar_scraper.rs`
2. Implement 10-K/10-Q scraping
3. Add insider trading scraper
4. Create Apollo agents
5. Test with major companies

### **Phase 3: State Tax Scrapers (Week 3)**
1. Create `state_tax_scraper.rs`
2. Implement state-by-state logic
3. Handle different site structures
4. Create Apollo agents
5. Test with CA, NY, TX, FL

---

## 💡 **Key Benefits**

**Why Rust for Scraping:**
- **Performance** - Fast, concurrent scraping
- **Memory safety** - No crashes from bad HTML
- **Async** - Handle many requests simultaneously
- **Reliability** - Production-ready error handling

**Why LLM for Parsing:**
- **Flexibility** - Handles varying HTML structures
- **Intelligence** - Understands context and relationships
- **Adaptability** - Works even when sites change layout
- **Extraction** - Pulls out relevant data automatically

---

## 🎯 **Success Metrics**

- **Coverage:** % of target sites successfully scraped
- **Reliability:** Uptime and success rate
- **Speed:** Time to scrape and parse
- **Accuracy:** LLM parsing accuracy
- **Cost:** Requests per month, caching hit rate

---

**This architecture enables Apollo to access ANY public data source, not just APIs!** 🚀✨
