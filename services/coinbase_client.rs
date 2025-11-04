// Apollo Coinbase Pro Client
// Crypto exchange integration for trading

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};
use hmac::{Hmac, Mac};
use sha2::Sha256;
use base64::{Engine as _, engine::general_purpose};

type HmacSha256 = Hmac<Sha256>;

/// Coinbase Pro Trading Client
pub struct CoinbaseClient {
    api_key: String,
    api_secret: String,
    passphrase: String,
    base_url: String,
    client: Client,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoinbaseAccount {
    pub id: String,
    pub currency: String,
    pub balance: f64,
    pub available: f64,
    pub hold: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoinbaseOrder {
    pub id: String,
    pub product_id: String,
    pub side: String,
    pub order_type: String,
    pub size: f64,
    pub price: Option<f64>,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoinbaseTicker {
    pub product_id: String,
    pub price: f64,
    pub volume_24h: f64,
    pub bid: f64,
    pub ask: f64,
}

impl CoinbaseClient {
    pub fn new(api_key: String, api_secret: String, passphrase: String) -> Self {
        Self {
            api_key,
            api_secret,
            passphrase,
            base_url: "https://api.pro.coinbase.com".to_string(),
            client: Client::new(),
        }
    }

    /// Generate authentication headers
    fn auth_headers(&self, timestamp: &str, method: &str, path: &str, body: &str) -> Result<(String, String)> {
        let what = format!("{}{}{}{}", timestamp, method, path, body);
        
        let secret_decoded = general_purpose::STANDARD.decode(&self.api_secret)?;
        let mut mac = HmacSha256::new_from_slice(&secret_decoded)?;
        mac.update(what.as_bytes());
        
        let signature = general_purpose::STANDARD.encode(mac.finalize().into_bytes());
        
        Ok((timestamp.to_string(), signature))
    }

    /// Get all accounts
    pub async fn get_accounts(&self) -> Result<Vec<CoinbaseAccount>> {
        let path = "/accounts";
        let url = format!("{}{}", self.base_url, path);
        let timestamp = chrono::Utc::now().timestamp().to_string();
        
        let (ts, sig) = self.auth_headers(&timestamp, "GET", path, "")?;

        let response = self.client
            .get(&url)
            .header("CB-ACCESS-KEY", &self.api_key)
            .header("CB-ACCESS-SIGN", sig)
            .header("CB-ACCESS-TIMESTAMP", ts)
            .header("CB-ACCESS-PASSPHRASE", &self.passphrase)
            .send()
            .await?;

        let accounts: Vec<CoinbaseAccount> = response.json().await?;
        Ok(accounts)
    }

    /// Place market order
    pub async fn place_market_order(&self, product_id: &str, side: &str, size: f64) -> Result<CoinbaseOrder> {
        let path = "/orders";
        let url = format!("{}{}", self.base_url, path);
        
        #[derive(Serialize)]
        struct OrderRequest {
            product_id: String,
            side: String,
            #[serde(rename = "type")]
            order_type: String,
            size: String,
        }

        let request = OrderRequest {
            product_id: product_id.to_string(),
            side: side.to_string(),
            order_type: "market".to_string(),
            size: size.to_string(),
        };

        let body = serde_json::to_string(&request)?;
        let timestamp = chrono::Utc::now().timestamp().to_string();
        let (ts, sig) = self.auth_headers(&timestamp, "POST", path, &body)?;

        let response = self.client
            .post(&url)
            .header("CB-ACCESS-KEY", &self.api_key)
            .header("CB-ACCESS-SIGN", sig)
            .header("CB-ACCESS-TIMESTAMP", ts)
            .header("CB-ACCESS-PASSPHRASE", &self.passphrase)
            .json(&request)
            .send()
            .await?;

        let order: CoinbaseOrder = response.json().await?;
        Ok(order)
    }

    /// Get ticker
    pub async fn get_ticker(&self, product_id: &str) -> Result<CoinbaseTicker> {
        let url = format!("{}/products/{}/ticker", self.base_url, product_id);

        let response = self.client
            .get(&url)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct TickerResponse {
            price: String,
            volume: String,
            bid: String,
            ask: String,
        }

        let ticker: TickerResponse = response.json().await?;

        Ok(CoinbaseTicker {
            product_id: product_id.to_string(),
            price: ticker.price.parse().unwrap_or(0.0),
            volume_24h: ticker.volume.parse().unwrap_or(0.0),
            bid: ticker.bid.parse().unwrap_or(0.0),
            ask: ticker.ask.parse().unwrap_or(0.0),
        })
    }

    /// Get order status
    pub async fn get_order(&self, order_id: &str) -> Result<CoinbaseOrder> {
        let path = format!("/orders/{}", order_id);
        let url = format!("{}{}", self.base_url, path);
        let timestamp = chrono::Utc::now().timestamp().to_string();
        
        let (ts, sig) = self.auth_headers(&timestamp, "GET", &path, "")?;

        let response = self.client
            .get(&url)
            .header("CB-ACCESS-KEY", &self.api_key)
            .header("CB-ACCESS-SIGN", sig)
            .header("CB-ACCESS-TIMESTAMP", ts)
            .header("CB-ACCESS-PASSPHRASE", &self.passphrase)
            .send()
            .await?;

        let order: CoinbaseOrder = response.json().await?;
        Ok(order)
    }
}

