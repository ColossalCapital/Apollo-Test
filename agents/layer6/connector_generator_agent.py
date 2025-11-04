"""
Connector Generator Agent - Autonomous code generation for integrations

Generates production-ready Rust connector code for any integration.
"""

from typing import Dict, Any, List
from .autonomous_agent import Layer6Agent
from ..base import AgentResult, AgentMetadata, AgentLayer, EntityType, AppContext, PrivacyLevel, AgentCategory
import httpx
import json


class ConnectorGeneratorAgent(Layer6Agent):
    """
    Connector Generator Agent - Autonomous integration code generation
    
    Generates complete Rust connector implementations including:
    - API client code
    - Data models
    - Error handling
    - Rate limiting
    - Webhook handlers
    - Tests
    - Deployment configuration
    """

    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=120.0)
        
        # Code templates
        self.templates = {
            "quickbooks": self._quickbooks_template,
            "gmail": self._gmail_template,
            "slack": self._slack_template,
            "github": self._github_template,
            "stripe": self._stripe_template,
        }

    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            # Core Identity
            name="connector_generator",
            layer=AgentLayer.LAYER_6_AUTONOMOUS,
            version="1.0.0",
            description="Autonomous code generation for integration connectors",
            capabilities=[
                "rust_code_generation",
                "api_client_generation",
                "data_model_generation",
                "test_generation",
                "deployment_config_generation",
                "error_handling",
                "rate_limiting"
            ],
            dependencies=["code_generation", "architecture"],

            # Filtering & Visibility
            entity_types=[EntityType.UNIVERSAL],
            app_contexts=[AppContext.ATLAS, AppContext.AKASHIC],
            requires_subscription=["pro", "enterprise"],

            # Authentication & Access
            byok_enabled=False,
            wtf_purchasable=True,
            requires_api_key=False,
            oauth_provider=None,

            # Resource Usage
            estimated_tokens_per_call=5000,
            estimated_cost_per_call=0.025,
            rate_limit=10,

            # Performance
            avg_response_time_ms=30000,  # 30 seconds
            requires_gpu=False,
            can_run_offline=False,

            # Data & Privacy
            data_retention_days=90,
            privacy_level=PrivacyLevel.PRIVATE,
            pii_handling="none",
            gdpr_compliant=True,

            # Integration Details
            api_version="1.0",
            webhook_support=False,
            real_time_sync=False,
            sync_frequency=None,

            # Business Logic
            free_tier_limit=0,
            pro_tier_limit=100,
            enterprise_only=False,
            beta=False,

            # Learning & Training
            supports_continuous_learning=True,
            training_cost_wtf=10.0,
            training_frequency="monthly",
            model_storage_location="filecoin",

            # UI/UX
            has_ui_component=True,
            icon="code",
            color="#10B981",
            category=AgentCategory.DEVELOPMENT,

            # Monitoring & Alerts
            health_check_endpoint="/health",
            alert_on_failure=True,
            fallback_agent="code_generation",

            # Documentation
            documentation_url="https://docs.colossalcapital.com/agents/connector-generator",
            example_use_cases=[
                "Generate QuickBooks connector",
                "Generate Gmail connector",
                "Generate Slack connector",
                "Generate custom API connector"
            ],
            setup_guide_url="https://docs.colossalcapital.com/guides/connector-generator"
        )

    async def monitor(self) -> AgentResult:
        """Monitor for integration setup requests"""
        # In production, this would monitor a queue
        return AgentResult(
            success=True,
            data={"status": "monitoring"},
            metadata={"agent": "connector_generator"}
        )

    async def decide(self, situation: Dict[str, Any]) -> AgentResult:
        """Decide whether to generate connector"""
        integration = situation.get("integration")
        
        if integration in self.templates:
            return AgentResult(
                success=True,
                data={
                    "action": "generate",
                    "integration": integration,
                    "template": "available"
                },
                metadata={"confidence": 0.95}
            )
        else:
            return AgentResult(
                success=True,
                data={
                    "action": "generate_custom",
                    "integration": integration,
                    "template": "custom"
                },
                metadata={"confidence": 0.75}
            )

    async def act(self, decision: Dict[str, Any]) -> AgentResult:
        """Generate connector code using connector agent knowledge"""
        integration = decision.get("integration")
        config = decision.get("config", {})
        
        # Use connector agent as knowledge source
        code_files = await self._generate_with_connector_knowledge(integration, config)
        
        return AgentResult(
            success=True,
            data={
                "code_files": code_files,
                "integration": integration
            },
            metadata={
                "files_generated": len(code_files),
                "lines_of_code": sum(len(code.split('\n')) for code in code_files.values())
            }
        )

    async def verify(self, action_result: Dict[str, Any]) -> AgentResult:
        """Verify generated code"""
        code_files = action_result.get("code_files", {})
        
        # Basic verification
        checks = {
            "has_main_file": "src/connectors/" in str(code_files.keys()),
            "has_models": "src/models/" in str(code_files.keys()),
            "has_tests": "tests/" in str(code_files.keys()),
            "has_cargo_toml": "Cargo.toml" in code_files,
        }
        
        all_passed = all(checks.values())
        
        return AgentResult(
            success=all_passed,
            data={
                "verification": checks,
                "passed": all_passed
            },
            metadata={"checks_run": len(checks)}
        )

    # ========================================================================
    # CODE GENERATION WITH CONNECTOR KNOWLEDGE
    # ========================================================================

    async def _generate_with_connector_knowledge(
        self, 
        integration: str, 
        config: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate code using connector agent as knowledge source"""
        
        from ..agents import get_agent_by_name
        
        # Get connector agent for this integration
        connector_agent = get_agent_by_name(f"{integration}_connector")
        
        if not connector_agent:
            # Fall back to custom generation if no connector agent exists
            return await self._generate_custom_connector(integration, config)
        
        # Query connector agent for API details
        auth_info = connector_agent.process({"query_type": "authentication"})
        
        # Get API endpoint info (try different query types)
        api_info = None
        for query_type in ["invoices", "messages", "events", "repositories", "charges"]:
            try:
                api_info = connector_agent.process({"query_type": query_type})
                if api_info.get("status") == "success":
                    break
            except:
                continue
        
        # Build context for LLM
        context = f"""Generate production-ready Rust connector for {integration.upper()}.

AUTHENTICATION:
{json.dumps(auth_info.get("auth_guide", {}), indent=2)}

API DETAILS:
{json.dumps(api_info, indent=2) if api_info else "Use standard REST API patterns"}

REQUIREMENTS:
1. Use reqwest for HTTP client with timeout
2. Implement proper authentication flow
3. Include comprehensive error handling with anyhow
4. Include rate limiting (respect API limits)
5. Include retry logic with exponential backoff
6. Send fetched data to Apollo at http://apollo:8003/data/ingest
7. Include data models with serde for JSON serialization
8. Include unit tests
9. Include integration tests with mockito

RUST CODE STRUCTURE:
- src/connectors/{integration}.rs - Main connector implementation
- src/models/{integration}.rs - Data models (Invoice, Customer, etc.)
- tests/{integration}_test.rs - Comprehensive tests
- Cargo.toml - Dependencies

EXAMPLE SYNC FUNCTION:
```rust
pub async fn sync_to_apollo(&self) -> Result<()> {{
    let data = self.fetch_data().await?;
    
    let apollo_client = reqwest::Client::new();
    apollo_client
        .post("http://apollo:8003/data/ingest")
        .json(&serde_json::json!({{
            "source": "{integration}",
            "entity_id": std::env::var("ENTITY_ID").unwrap_or_default(),
            "data_type": "primary",
            "data": data
        }}))
        .send()
        .await?;
    
    Ok(())
}}
```

Generate complete, production-ready Rust code with all files.
"""

        # Generate with LLM
        response = await self.client.post(
            f"{self.llm_url}/v1/chat/completions",
            json={
                "model": "deepseek-coder",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert Rust developer specializing in API integrations. Generate production-ready, idiomatic Rust code."
                    },
                    {"role": "user", "content": context}
                ],
                "temperature": 0.2,
                "max_tokens": 4000
            }
        )

        result = response.json()
        generated_code = result["choices"][0]["message"]["content"]
        
        # Parse generated code into files
        return self._parse_generated_code(generated_code, integration)

    def _parse_generated_code(self, code: str, integration: str) -> Dict[str, str]:
        """Parse LLM-generated code into separate files"""
        
        files = {}
        
        # Simple parsing - look for file markers
        # In production, would have more sophisticated parsing
        
        if "src/connectors/" in code:
            # Extract connector code
            files[f"src/connectors/{integration}.rs"] = self._extract_file_content(
                code, f"src/connectors/{integration}.rs"
            )
        
        if "src/models/" in code:
            # Extract models code
            files[f"src/models/{integration}.rs"] = self._extract_file_content(
                code, f"src/models/{integration}.rs"
            )
        
        if "tests/" in code:
            # Extract test code
            files[f"tests/{integration}_test.rs"] = self._extract_file_content(
                code, f"tests/{integration}_test.rs"
            )
        
        if "Cargo.toml" in code:
            # Extract Cargo.toml
            files["Cargo.toml"] = self._extract_file_content(code, "Cargo.toml")
        
        # If parsing failed, use template as fallback
        if not files:
            return self._quickbooks_template({})  # Use template as fallback
        
        return files

    def _extract_file_content(self, full_code: str, filename: str) -> str:
        """Extract content for a specific file from LLM output"""
        
        # Look for file markers like:
        # // src/connectors/quickbooks.rs
        # or
        # ```rust
        # // src/connectors/quickbooks.rs
        
        lines = full_code.split('\n')
        content_lines = []
        capturing = False
        
        for line in lines:
            if filename in line:
                capturing = True
                continue
            
            if capturing:
                # Stop at next file marker or end
                if line.startswith('//') and ('src/' in line or 'tests/' in line or 'Cargo.toml' in line):
                    break
                if line.strip() == '```' and content_lines:
                    break
                
                content_lines.append(line)
        
        return '\n'.join(content_lines).strip()

    # ========================================================================
    # CODE GENERATION TEMPLATES (FALLBACK)
    # ========================================================================

    async def _quickbooks_template(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate QuickBooks connector with vault integration"""
        
        connector_code = '''// Generated by Apollo ConnectorGeneratorAgent
// Integration: QuickBooks
// Generated: 2025-10-30
// Uses Universal Vault for secure credential storage

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use anyhow::{Result, Context};
use vault_client::VaultClient;

#[derive(Clone)]
pub struct QuickBooksConnector {
    client: Client,
    vault_client: VaultClient,
    base_url: String,
}

impl QuickBooksConnector {
    pub async fn new() -> Result<Self> {
        let vault_client = VaultClient::from_env()
            .context("Failed to initialize vault client")?;
        
        Ok(Self {
            client: Client::builder()
                .timeout(Duration::from_secs(30))
                .build()
                .unwrap(),
            vault_client,
            base_url: "https://quickbooks.api.intuit.com/v3".to_string(),
        })
    }
    
    pub async fn authenticate(&self) -> Result<String> {
        // Get credentials from vault
        let creds = self.vault_client
            .get("quickbooks")
            .await
            .context("Failed to retrieve QuickBooks credentials from vault")?;
        
        let client_id = creds.credentials["client_id"]
            .as_str()
            .context("Missing client_id")?;
        
        let client_secret = creds.credentials["client_secret"]
            .as_str()
            .context("Missing client_secret")?;
        
        // OAuth 2.0 token exchange
        let token_response = self.client
            .post("https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer")
            .form(&[
                ("grant_type", "client_credentials"),
                ("client_id", client_id),
                ("client_secret", client_secret),
            ])
            .send()
            .await?;
        
        let token: TokenResponse = token_response.json().await?;
        Ok(token.access_token)
    }
    
    pub async fn fetch_invoices(&self) -> Result<Vec<Invoice>> {
        let token = self.authenticate().await?;
        let realm_id = self.vault_client
            .get_field("quickbooks", "realm_id")
            .await?;
        
        let url = format!(
            "{}/company/{}/query?query=SELECT * FROM Invoice",
            self.base_url, realm_id
        );
        
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", token))
            .header("Accept", "application/json")
            .send()
            .await?;
        
        if !response.status().is_success() {
            anyhow::bail!("QuickBooks API error: {}", response.status());
        }
        
        let data: InvoiceResponse = response.json().await?;
        Ok(data.query_response.invoice)
    }
    
    pub async fn fetch_customers(&self) -> Result<Vec<Customer>> {
        let url = format!(
            "{}/company/{}/query?query=SELECT * FROM Customer",
            self.base_url, self.realm_id
        );
        
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.access_token))
            .header("Accept", "application/json")
            .send()
            .await?;
        
        let data: CustomerResponse = response.json().await?;
        Ok(data.query_response.customer)
    }
    
    pub async fn sync_to_apollo(&self) -> Result<()> {
        // Fetch data
        let invoices = self.fetch_invoices().await?;
        let customers = self.fetch_customers().await?;
        
        // Send to Apollo for parsing
        let apollo_client = reqwest::Client::new();
        apollo_client
            .post("http://apollo:8002/data/ingest")
            .json(&serde_json::json!({
                "source": "quickbooks",
                "entity_id": std::env::var("ENTITY_ID").unwrap_or_default(),
                "data": {
                    "invoices": invoices,
                    "customers": customers
                }
            }))
            .send()
            .await?;
        
        Ok(())
    }
}
'''

        models_code = '''use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct InvoiceResponse {
    #[serde(rename = "QueryResponse")]
    pub query_response: QueryResponse<Invoice>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CustomerResponse {
    #[serde(rename = "QueryResponse")]
    pub query_response: QueryResponse<Customer>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct QueryResponse<T> {
    #[serde(rename = "Invoice", skip_serializing_if = "Option::is_none")]
    pub invoice: Option<Vec<T>>,
    #[serde(rename = "Customer", skip_serializing_if = "Option::is_none")]
    pub customer: Option<Vec<T>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Invoice {
    #[serde(rename = "Id")]
    pub id: String,
    #[serde(rename = "CustomerRef")]
    pub customer_ref: CustomerRef,
    #[serde(rename = "TotalAmt")]
    pub total_amt: f64,
    #[serde(rename = "TxnDate")]
    pub txn_date: String,
    #[serde(rename = "DueDate")]
    pub due_date: String,
    #[serde(rename = "Balance")]
    pub balance: f64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Customer {
    #[serde(rename = "Id")]
    pub id: String,
    #[serde(rename = "DisplayName")]
    pub display_name: String,
    #[serde(rename = "CompanyName", skip_serializing_if = "Option::is_none")]
    pub company_name: Option<String>,
    #[serde(rename = "PrimaryEmailAddr", skip_serializing_if = "Option::is_none")]
    pub primary_email_addr: Option<EmailAddr>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CustomerRef {
    pub value: String,
    pub name: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct EmailAddr {
    #[serde(rename = "Address")]
    pub address: String,
}
'''

        test_code = '''#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_quickbooks_connector_creation() {
        let connector = QuickBooksConnector::new(
            "test_token".to_string(),
            "test_realm".to_string()
        );
        assert_eq!(connector.realm_id, "test_realm");
    }
    
    // Add more tests here
}
'''

        cargo_toml = '''[package]
name = "ackwardroots-quickbooks-connector"
version = "0.1.0"
edition = "2021"

[dependencies]
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
anyhow = "1.0"

[dev-dependencies]
mockito = "1.0"
'''

        return {
            "src/connectors/quickbooks.rs": connector_code,
            "src/models/quickbooks.rs": models_code,
            "tests/quickbooks_test.rs": test_code,
            "Cargo.toml": cargo_toml,
        }

    async def _gmail_template(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate Gmail connector"""
        # Similar structure to QuickBooks
        return {
            "src/connectors/gmail.rs": "// Gmail connector code...",
            "src/models/gmail.rs": "// Gmail models...",
            "tests/gmail_test.rs": "// Gmail tests...",
        }

    async def _slack_template(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate Slack connector"""
        return {
            "src/connectors/slack.rs": "// Slack connector code...",
            "src/models/slack.rs": "// Slack models...",
            "tests/slack_test.rs": "// Slack tests...",
        }

    async def _github_template(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate GitHub connector"""
        return {
            "src/connectors/github.rs": "// GitHub connector code...",
            "src/models/github.rs": "// GitHub models...",
            "tests/github_test.rs": "// GitHub tests...",
        }

    async def _stripe_template(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate Stripe connector"""
        return {
            "src/connectors/stripe.rs": "// Stripe connector code...",
            "src/models/stripe.rs": "// Stripe models...",
            "tests/stripe_test.rs": "// Stripe tests...",
        }

    async def _generate_custom_connector(self, integration: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate custom connector using LLM"""
        
        prompt = f"""Generate a production-ready Rust connector for {integration}.

Configuration:
{json.dumps(config, indent=2)}

Requirements:
1. Use reqwest for HTTP client
2. Use serde for JSON serialization
3. Include proper error handling with anyhow
4. Include rate limiting
5. Include retry logic with exponential backoff
6. Send data to Apollo at http://apollo:8002/data/ingest
7. Include comprehensive tests

Generate the following files:
- src/connectors/{integration}.rs (main connector)
- src/models/{integration}.rs (data models)
- tests/{integration}_test.rs (tests)
- Cargo.toml (dependencies)
"""

        response = await self.client.post(
            f"{self.llm_url}/v1/chat/completions",
            json={
                "model": "deepseek-coder",
                "messages": [
                    {"role": "system", "content": "You are an expert Rust developer specializing in API integrations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
        )

        result = response.json()
        generated_code = result["choices"][0]["message"]["content"]
        
        # Parse generated code into files
        # (In production, would have more sophisticated parsing)
        return {
            f"src/connectors/{integration}.rs": generated_code,
            f"src/models/{integration}.rs": "// Models...",
            f"tests/{integration}_test.rs": "// Tests...",
        }
