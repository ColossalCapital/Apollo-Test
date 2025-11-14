# 🏛️ State Tax Scraping Architecture

**Goal:** Comprehensive tax intelligence for all 50 states across personal, business, and corporate taxes

---

## 📊 **State Tax Landscape**

### **Tax Types by State:**

**Personal Income Tax:**
- 43 states + DC have income tax
- 7 states have NO income tax: AK, FL, NV, SD, TN, TX, WY
- 2 states tax only dividends/interest: NH, WA

**Corporate Income Tax:**
- 44 states + DC have corporate tax
- 6 states have NO corporate tax: NV, OH (gross receipts), SD, TX (franchise), WA (B&O), WY

**Sales Tax:**
- 45 states + DC have sales tax
- 5 states have NO sales tax: AK, DE, MT, NH, OR

**Business Taxes:**
- Franchise tax (TX, DE, etc.)
- Gross receipts tax (OH, WA, etc.)
- Business & Occupation tax (WA)
- LLC fees (CA $800/year)

---

## 🎯 **Scraping Strategy**

### **Tier 1: High-Priority States (Top 10 by GDP)**
1. **California** - Complex, high rates, $800 LLC fee
2. **Texas** - No income tax, franchise tax
3. **New York** - High rates, NYC separate
4. **Florida** - No income tax
5. **Illinois** - Flat income tax
6. **Pennsylvania** - Flat income tax
7. **Ohio** - Graduated income tax
8. **Georgia** - Graduated income tax
9. **Washington** - No income tax, B&O tax
10. **New Jersey** - High rates, complex

### **Tier 2: Medium-Priority States (11-30)**
11-30. Remaining states by business activity

### **Tier 3: Low-Priority States (31-50)**
31-50. Smaller states, less business activity

---

## 🏗️ **Architecture Design**

### **State Tax Scraper Structure:**

```rust
// AckwardRootsInc/src/scrapers/state_tax/mod.rs
pub struct StateTaxScraper {
    state: StateCode,
    client: reqwest::Client,
    cache: Cache,
}

pub enum StateCode {
    CA, TX, NY, FL, IL, PA, OH, GA, WA, NJ,
    // ... all 50 states
}

pub enum TaxType {
    Personal,
    Corporate,
    Business,
    Sales,
    Property,
}

impl StateTaxScraper {
    pub async fn scrape_tax_forms(&self, tax_type: TaxType) -> Result<Vec<TaxForm>> {
        match self.state {
            StateCode::CA => self.scrape_california(tax_type).await,
            StateCode::TX => self.scrape_texas(tax_type).await,
            StateCode::NY => self.scrape_new_york(tax_type).await,
            // ... per-state implementations
        }
    }
}
```

---

## 📋 **Per-State Implementation**

### **California (Highest Priority)**

**Personal Income Tax:**
- Forms: 540, 540NR, 540-ES
- Rates: 1% - 13.3% (highest in US)
- Website: https://www.ftb.ca.gov/

**Corporate Tax:**
- Forms: 100, 100S, 100W
- Rate: 8.84%
- Minimum: $800/year

**Business Taxes:**
- LLC fee: $800/year minimum
- Franchise tax
- Forms: 568, 3522

**Scraper Implementation:**
```rust
// AckwardRootsInc/src/scrapers/state_tax/california.rs
pub struct CaliforniaTaxScraper {
    base_url: String,
}

impl CaliforniaTaxScraper {
    pub async fn scrape_personal_forms(&self) -> Result<Vec<TaxForm>> {
        // Scrape from https://www.ftb.ca.gov/forms/
        let forms = vec!["540", "540nr", "540es"];
        for form in forms {
            let url = format!("{}/forms/{}.pdf", self.base_url, form);
            // Download and cache
        }
    }
    
    pub async fn scrape_corporate_forms(&self) -> Result<Vec<TaxForm>> {
        // Scrape corporate forms
    }
    
    pub async fn scrape_tax_rates(&self, year: u32) -> Result<TaxRates> {
        // Scrape current tax rates
    }
}
```

**Apollo Agents:**
- `CaliforniaPersonalTaxScraperAgent`
- `CaliforniaCorporateTaxScraperAgent`
- `CaliforniaBusinessTaxScraperAgent`
- `CaliforniaTaxParserAgent` (LLM-powered)

---

### **Texas (2nd Priority)**

**Personal Income Tax:**
- NONE! No state income tax

**Corporate Tax:**
- Franchise tax (margin tax)
- Rate: 0.375% - 0.75%
- Threshold: $1.23M revenue
- Forms: 05-158, 05-163

**Business Taxes:**
- Franchise tax applies to LLCs
- Website: https://comptroller.texas.gov/

**Scraper Implementation:**
```rust
// AckwardRootsInc/src/scrapers/state_tax/texas.rs
pub struct TexasTaxScraper {
    base_url: String,
}

impl TexasTaxScraper {
    pub async fn scrape_franchise_tax_forms(&self) -> Result<Vec<TaxForm>> {
        // Scrape franchise tax forms
    }
    
    pub async fn scrape_sales_tax_info(&self) -> Result<SalesTaxInfo> {
        // Texas has sales tax
    }
}
```

---

### **New York (3rd Priority)**

**Personal Income Tax:**
- Forms: IT-201, IT-203, IT-2105
- Rates: 4% - 10.9%
- NYC separate: 3.078% - 3.876%
- Website: https://www.tax.ny.gov/

**Corporate Tax:**
- Forms: CT-3, CT-3-S, CT-4
- Rate: 6.5% - 7.25%

**Business Taxes:**
- LLC filing fee: $25
- Biennial statement: $9

---

### **Florida (4th Priority)**

**Personal Income Tax:**
- NONE! No state income tax

**Corporate Tax:**
- Corporate income tax: 5.5%
- Forms: F-1120, F-1120A
- Website: https://floridarevenue.com/

**Business Taxes:**
- Annual report fee: $138.75 (LLC)
- No franchise tax

---

## 🗂️ **Data Structure**

### **State Tax Information:**
```json
{
  "state": "CA",
  "state_name": "California",
  "tax_authority": "Franchise Tax Board",
  "website": "https://www.ftb.ca.gov/",
  "personal_income_tax": {
    "has_tax": true,
    "rates": [
      {"bracket": 0, "rate": 0.01},
      {"bracket": 10099, "rate": 0.02},
      {"bracket": 23942, "rate": 0.04},
      {"bracket": 37788, "rate": 0.06},
      {"bracket": 52455, "rate": 0.08},
      {"bracket": 66295, "rate": 0.093},
      {"bracket": 338639, "rate": 0.103},
      {"bracket": 406364, "rate": 0.113},
      {"bracket": 677275, "rate": 0.123},
      {"bracket": 1000000, "rate": 0.133}
    ],
    "forms": [
      {"form_number": "540", "name": "California Resident Income Tax Return"},
      {"form_number": "540NR", "name": "California Nonresident Income Tax Return"},
      {"form_number": "540-ES", "name": "Estimated Tax"}
    ]
  },
  "corporate_tax": {
    "has_tax": true,
    "rate": 0.0884,
    "minimum": 800,
    "forms": [
      {"form_number": "100", "name": "California Corporation Franchise or Income Tax Return"},
      {"form_number": "100S", "name": "California S Corporation Franchise or Income Tax Return"}
    ]
  },
  "business_taxes": {
    "llc_fee": 800,
    "franchise_tax": true,
    "forms": [
      {"form_number": "568", "name": "Limited Liability Company Return of Income"}
    ]
  },
  "sales_tax": {
    "has_tax": true,
    "base_rate": 0.0725,
    "local_rates": "varies by county"
  }
}
```

---

## 🚀 **Implementation Plan**

### **Phase 1: Top 5 States (Week 1-2)**
1. ✅ California - Most complex, highest priority
2. ✅ Texas - Franchise tax, no income tax
3. ✅ New York - High rates, NYC separate
4. ✅ Florida - No income tax, corporate tax
5. ✅ Illinois - Flat tax, simpler

### **Phase 2: States 6-15 (Week 3-4)**
6. Pennsylvania
7. Ohio
8. Georgia
9. Washington
10. New Jersey
11. Massachusetts
12. Virginia
13. North Carolina
14. Michigan
15. Tennessee

### **Phase 3: States 16-30 (Week 5-6)**
16-30. Medium-priority states

### **Phase 4: States 31-50 (Week 7-8)**
31-50. Remaining states

---

## 🎯 **Apollo Agent Structure**

### **Per-State Agents:**

**California Example:**
```python
# Scraper Agents (maintain Rust scrapers)
- CaliforniaPersonalTaxScraperAgent
- CaliforniaCorporateTaxScraperAgent
- CaliforniaBusinessTaxScraperAgent

# Parser Agents (LLM-powered parsing)
- CaliforniaPersonalTaxParserAgent
- CaliforniaCorporateTaxParserAgent
- CaliforniaBusinessTaxParserAgent
```

**Unified State Tax Agent:**
```python
# Apollo/agents/connectors/scrapers/state_tax_scraper_agent.py
class StateTaxScraperAgent(Layer1Agent):
    """
    Unified state tax scraper - routes to state-specific scrapers
    """
    
    async def extract(self, raw_data: Dict[str, Any]) -> AgentResult:
        state = raw_data.get('state')  # e.g., "CA", "TX"
        tax_type = raw_data.get('tax_type')  # personal, corporate, business
        
        # Route to state-specific scraper
        scraper = self.get_state_scraper(state)
        return await scraper.scrape(tax_type)
```

---

## 📊 **Coverage Matrix**

| State | Personal | Corporate | Business | Sales | Priority |
|-------|----------|-----------|----------|-------|----------|
| CA    | ✅       | ✅        | ✅       | ✅    | 1        |
| TX    | N/A      | ✅        | ✅       | ✅    | 2        |
| NY    | ✅       | ✅        | ✅       | ✅    | 3        |
| FL    | N/A      | ✅        | ✅       | ✅    | 4        |
| IL    | ✅       | ✅        | ✅       | ✅    | 5        |
| ...   | ...      | ...       | ...      | ...   | ...      |

---

## 💡 **Key Features**

### **1. Multi-Entity Support**
- Personal taxes (individuals)
- Corporate taxes (C-corps)
- S-corp taxes (pass-through)
- LLC taxes (varies by state)
- Partnership taxes

### **2. Multi-Jurisdiction**
- State-level taxes
- County-level taxes (property, sales)
- City-level taxes (NYC, SF, etc.)

### **3. Tax Optimization**
- Compare rates across states
- Identify deductions by state
- Calculate total tax burden
- Recommend optimal entity structure

### **4. Compliance Tracking**
- Filing deadlines by state
- Required forms by entity type
- Estimated tax payments
- Annual report requirements

---

## 🎯 **Success Metrics**

**Coverage:**
- 50 states + DC = 51 jurisdictions
- 3 tax types per state = 153 scrapers
- ~500 unique tax forms

**Accuracy:**
- 99%+ form download success
- 95%+ LLM parsing accuracy
- Real-time rate updates

**Performance:**
- < 5 sec per form download
- < 10 sec per LLM parse
- 90%+ cache hit rate

---

## 🚀 **Next Steps**

1. **Create California scrapers** (highest priority)
2. **Create Texas scrapers** (no income tax, franchise tax)
3. **Create New York scrapers** (complex, NYC separate)
4. **Create unified StateTaxScraperAgent**
5. **Create state-specific parser agents**
6. **Build tax comparison tool**
7. **Add compliance calendar**

---

**This will give us COMPLETE tax intelligence across all 50 states!** 🎯✨
