// Apollo Charles Schwab Client
// Trading integration with Schwab's API

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};

/// Charles Schwab Trading Client
pub struct SchwabClient {
    api_key: String,
    api_secret: String,
    access_token: Option<String>,
    base_url: String,
    client: Client,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchwabAccount {
    pub account_number: String,
    pub account_type: String,
    pub cash_balance: f64,
    pub equity_value: f64,
    pub total_value: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchwabPosition {
    pub symbol: String,
    pub quantity: f64,
    pub average_price: f64,
    pub current_price: f64,
    pub market_value: f64,
    pub unrealized_pnl: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchwabOrder {
    pub symbol: String,
    pub side: String,           // "BUY" or "SELL"
    pub quantity: f64,
    pub order_type: String,     // "MARKET", "LIMIT", "STOP"
    pub time_in_force: String,  // "DAY", "GTC"
    pub limit_price: Option<f64>,
}

impl SchwabClient {
    pub fn new(api_key: String, api_secret: String) -> Self {
        Self {
            api_key,
            api_secret,
            access_token: None,
            base_url: "https://api.schwabapi.com/trader/v1".to_string(),
            client: Client::new(),
        }
    }

    /// Authenticate with Schwab API
    pub async fn authenticate(&mut self) -> Result<()> {
        let url = "https://api.schwabapi.com/v1/oauth/token";

        #[derive(Serialize)]
        struct AuthRequest {
            grant_type: String,
            client_id: String,
            client_secret: String,
        }

        #[derive(Deserialize)]
        struct AuthResponse {
            access_token: String,
        }

        let request = AuthRequest {
            grant_type: "client_credentials".to_string(),
            client_id: self.api_key.clone(),
            client_secret: self.api_secret.clone(),
        };

        let response = self.client
            .post(url)
            .form(&request)
            .send()
            .await?;

        let result: AuthResponse = response.json().await?;
        self.access_token = Some(result.access_token);

        Ok(())
    }

    /// Get account information
    pub async fn get_accounts(&self) -> Result<Vec<SchwabAccount>> {
        let url = format!("{}/accounts", self.base_url);

        let response = self.client
            .get(&url)
            .bearer_auth(self.access_token.as_ref().unwrap())
            .send()
            .await?;

        let accounts: Vec<SchwabAccount> = response.json().await?;
        Ok(accounts)
    }

    /// Get positions
    pub async fn get_positions(&self, account_number: &str) -> Result<Vec<SchwabPosition>> {
        let url = format!("{}/accounts/{}/positions", self.base_url, account_number);

        let response = self.client
            .get(&url)
            .bearer_auth(self.access_token.as_ref().unwrap())
            .send()
            .await?;

        let positions: Vec<SchwabPosition> = response.json().await?;
        Ok(positions)
    }

    /// Place order
    pub async fn place_order(&self, account_number: &str, order: SchwabOrder) -> Result<String> {
        let url = format!("{}/accounts/{}/orders", self.base_url, account_number);

        let response = self.client
            .post(&url)
            .bearer_auth(self.access_token.as_ref().unwrap())
            .json(&order)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct OrderResponse {
            order_id: String,
        }

        let result: OrderResponse = response.json().await?;
        Ok(result.order_id)
    }

    /// Get quote
    pub async fn get_quote(&self, symbol: &str) -> Result<Quote> {
        let url = format!("{}/marketdata/quotes/{}", self.base_url, symbol);

        let response = self.client
            .get(&url)
            .bearer_auth(self.access_token.as_ref().unwrap())
            .send()
            .await?;

        let quote: Quote = response.json().await?;
        Ok(quote)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quote {
    pub symbol: String,
    pub bid: f64,
    pub ask: f64,
    pub last: f64,
    pub volume: u64,
}

