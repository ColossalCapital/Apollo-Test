// Apollo Delt Client
// Integrates with Delt for crypto trading, NFT operations, etc.

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};

/// Delt client for Apollo to execute crypto trades
pub struct DeltClient {
    base_url: String,
    api_key: String,
    client: Client,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CryptoOrder {
    pub user_id: String,
    pub symbol: String,
    pub side: String,
    pub amount_usd: f64,
    pub order_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CryptoPosition {
    pub symbol: String,
    pub quantity: f64,
    pub avg_entry_price: f64,
    pub current_price: f64,
    pub market_value: f64,
    pub unrealized_pnl: f64,
}

impl DeltClient {
    pub fn new(base_url: String, api_key: String) -> Self {
        Self {
            base_url,
            api_key,
            client: Client::new(),
        }
    }

    /// Get user's crypto portfolio
    pub async fn get_portfolio(&self, user_id: &str) -> Result<serde_json::Value> {
        let url = format!("{}/api/v1/portfolio/{}", self.base_url, user_id);

        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await?;

        let portfolio = response.json().await?;
        Ok(portfolio)
    }

    /// Get total portfolio value in USD
    pub async fn get_portfolio_value(&self, user_id: &str) -> Result<f64> {
        let portfolio = self.get_portfolio(user_id).await?;
        
        // Parse positions and sum values
        let positions = portfolio.get("positions")
            .and_then(|p| p.as_array())
            .context("No positions in portfolio")?;

        let total: f64 = positions.iter()
            .filter_map(|p| p.get("market_value")?.as_f64())
            .sum();

        Ok(total)
    }

    /// Place crypto order
    pub async fn place_order(&self, order: &serde_json::Value) -> Result<String> {
        let url = format!("{}/api/v1/orders", self.base_url);

        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(order)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct OrderResponse {
            tx_hash: String,
        }

        let result: OrderResponse = response.json().await?;
        Ok(result.tx_hash)
    }

    /// Breed NFT
    pub async fn breed_nft(&self, parent_ids: &str) -> Result<String> {
        let url = format!("{}/api/v1/nft/breed", self.base_url);

        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&serde_json::json!({
                "parent_ids": parent_ids,
                "payment_type": "WTF"
            }))
            .send()
            .await?;

        #[derive(Deserialize)]
        struct BreedResponse {
            token_id: String,
        }

        let result: BreedResponse = response.json().await?;
        Ok(result.token_id)
    }

    /// Buy NFT from marketplace
    pub async fn buy_nft(&self, token_id: &str, max_price: f64) -> Result<String> {
        let url = format!("{}/api/v1/nft/buy", self.base_url);

        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&serde_json::json!({
                "token_id": token_id,
                "max_price": max_price
            }))
            .send()
            .await?;

        #[derive(Deserialize)]
        struct BuyResponse {
            tx_hash: String,
        }

        let result: BuyResponse = response.json().await?;
        Ok(result.tx_hash)
    }

    /// Lock NFT as DELT collateral
    pub async fn lock_nft_collateral(&self, token_id: &str) -> Result<String> {
        let url = format!("{}/api/v1/stablecoin/lock-collateral", self.base_url);

        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&serde_json::json!({
                "nft_ids": [token_id],
                "wtf_amount": 0
            }))
            .send()
            .await?;

        #[derive(Deserialize)]
        struct CollateralResponse {
            position_id: String,
        }

        let result: CollateralResponse = response.json().await?;
        Ok(result.position_id)
    }
}


