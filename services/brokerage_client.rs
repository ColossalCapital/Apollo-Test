// Apollo Brokerage Client
// Integrate with traditional brokerages (E*TRADE, IBKR, Schwab, Alpaca, etc.)

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};
use std::collections::HashMap;

/// Supported brokerage providers
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BrokerageProvider {
    Alpaca,
    InteractiveBrokers,
    ETrade,
    CharlesSchwab,
    TDAmeritrade,
    Fidelity,
    Robinhood,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StockOrder {
    pub symbol: String,
    pub side: String,        // "buy" or "sell"
    pub quantity: f64,
    pub order_type: String,  // "market", "limit", "stop", "stop_limit"
    pub limit_price: Option<f64>,
    pub stop_price: Option<f64>,
    pub time_in_force: String, // "day", "gtc", "ioc", "fok"
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StockPosition {
    pub symbol: String,
    pub quantity: f64,
    pub avg_entry_price: f64,
    pub current_price: f64,
    pub market_value: f64,
    pub unrealized_pnl: f64,
    pub unrealized_pnl_percent: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderStatus {
    pub id: String,
    pub status: String,  // "new", "filled", "partially_filled", "canceled", "rejected"
    pub filled_qty: f64,
    pub filled_avg_price: f64,
    pub created_at: String,
    pub updated_at: String,
}

/// Alpaca Brokerage Client (easiest to integrate)
pub struct AlpacaClient {
    api_key: String,
    api_secret: String,
    base_url: String,
    client: Client,
}

impl AlpacaClient {
    pub fn new(api_key: String, api_secret: String, paper: bool) -> Self {
        let base_url = if paper {
            "https://paper-api.alpaca.markets".to_string()
        } else {
            "https://api.alpaca.markets".to_string()
        };

        Self {
            api_key,
            api_secret,
            base_url,
            client: Client::new(),
        }
    }

    /// Get account info
    pub async fn get_account(&self) -> Result<serde_json::Value> {
        let url = format!("{}/v2/account", self.base_url);

        let response = self.client
            .get(&url)
            .header("APCA-API-KEY-ID", &self.api_key)
            .header("APCA-API-SECRET-KEY", &self.api_secret)
            .send()
            .await?;

        let account = response.json().await?;
        Ok(account)
    }

    /// Get all positions
    pub async fn get_positions(&self) -> Result<Vec<StockPosition>> {
        let url = format!("{}/v2/positions", self.base_url);

        let response = self.client
            .get(&url)
            .header("APCA-API-KEY-ID", &self.api_key)
            .header("APCA-API-SECRET-KEY", &self.api_secret)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct AlpacaPosition {
            symbol: String,
            qty: String,
            avg_entry_price: String,
            current_price: String,
            market_value: String,
            unrealized_pl: String,
            unrealized_plpc: String,
        }

        let positions: Vec<AlpacaPosition> = response.json().await?;

        Ok(positions.into_iter().map(|p| StockPosition {
            symbol: p.symbol,
            quantity: p.qty.parse().unwrap_or(0.0),
            avg_entry_price: p.avg_entry_price.parse().unwrap_or(0.0),
            current_price: p.current_price.parse().unwrap_or(0.0),
            market_value: p.market_value.parse().unwrap_or(0.0),
            unrealized_pnl: p.unrealized_pl.parse().unwrap_or(0.0),
            unrealized_pnl_percent: p.unrealized_plpc.parse().unwrap_or(0.0),
        }).collect())
    }

    /// Place stock order
    pub async fn place_order(&self, order: StockOrder) -> Result<String> {
        let url = format!("{}/v2/orders", self.base_url);

        #[derive(Serialize)]
        struct AlpacaOrder {
            symbol: String,
            qty: String,
            side: String,
            #[serde(rename = "type")]
            order_type: String,
            time_in_force: String,
            limit_price: Option<String>,
            stop_price: Option<String>,
        }

        let alpaca_order = AlpacaOrder {
            symbol: order.symbol,
            qty: order.quantity.to_string(),
            side: order.side,
            order_type: order.order_type,
            time_in_force: order.time_in_force,
            limit_price: order.limit_price.map(|p| p.to_string()),
            stop_price: order.stop_price.map(|p| p.to_string()),
        };

        let response = self.client
            .post(&url)
            .header("APCA-API-KEY-ID", &self.api_key)
            .header("APCA-API-SECRET-KEY", &self.api_secret)
            .json(&alpaca_order)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct OrderResponse {
            id: String,
        }

        let result: OrderResponse = response.json().await?;
        Ok(result.id)
    }

    /// Get order status
    pub async fn get_order(&self, order_id: &str) -> Result<OrderStatus> {
        let url = format!("{}/v2/orders/{}", self.base_url, order_id);

        let response = self.client
            .get(&url)
            .header("APCA-API-KEY-ID", &self.api_key)
            .header("APCA-API-SECRET-KEY", &self.api_secret)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct AlpacaOrderStatus {
            id: String,
            status: String,
            filled_qty: String,
            filled_avg_price: Option<String>,
            created_at: String,
            updated_at: String,
        }

        let status: AlpacaOrderStatus = response.json().await?;

        Ok(OrderStatus {
            id: status.id,
            status: status.status,
            filled_qty: status.filled_qty.parse().unwrap_or(0.0),
            filled_avg_price: status.filled_avg_price
                .and_then(|p| p.parse().ok())
                .unwrap_or(0.0),
            created_at: status.created_at,
            updated_at: status.updated_at,
        })
    }

    /// Cancel order
    pub async fn cancel_order(&self, order_id: &str) -> Result<()> {
        let url = format!("{}/v2/orders/{}", self.base_url, order_id);

        self.client
            .delete(&url)
            .header("APCA-API-KEY-ID", &self.api_key)
            .header("APCA-API-SECRET-KEY", &self.api_secret)
            .send()
            .await?;

        Ok(())
    }

    /// Get market data
    pub async fn get_quote(&self, symbol: &str) -> Result<Quote> {
        let url = format!("{}/v2/stocks/{}/quotes/latest", self.base_url, symbol);

        let response = self.client
            .get(&url)
            .header("APCA-API-KEY-ID", &self.api_key)
            .header("APCA-API-SECRET-KEY", &self.api_secret)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct AlpacaQuote {
            quote: QuoteData,
        }

        #[derive(Deserialize)]
        struct QuoteData {
            ap: f64,  // Ask price
            bp: f64,  // Bid price
            #[serde(rename = "as")]
            ask_size: f64,
            #[serde(rename = "bs")]
            bid_size: f64,
        }

        let data: AlpacaQuote = response.json().await?;

        Ok(Quote {
            symbol: symbol.to_string(),
            bid: data.quote.bp,
            ask: data.quote.ap,
            last: (data.quote.bp + data.quote.ap) / 2.0,
            bid_size: data.quote.bid_size,
            ask_size: data.quote.ask_size,
        })
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quote {
    pub symbol: String,
    pub bid: f64,
    pub ask: f64,
    pub last: f64,
    pub bid_size: f64,
    pub ask_size: f64,
}

/// Unified brokerage client (supports multiple providers)
pub struct UnifiedBrokerageClient {
    providers: HashMap<String, BrokerageProvider>,
    alpaca: Option<AlpacaClient>,
    // Add other brokerages as needed
}

impl UnifiedBrokerageClient {
    pub fn new() -> Self {
        Self {
            providers: HashMap::new(),
            alpaca: None,
        }
    }

    pub fn add_alpaca(&mut self, api_key: String, api_secret: String, paper: bool) {
        self.alpaca = Some(AlpacaClient::new(api_key, api_secret, paper));
        self.providers.insert(
            "alpaca".to_string(),
            BrokerageProvider::Alpaca,
        );
    }

    /// Get all positions across all connected brokerages
    pub async fn get_all_positions(&self) -> Result<Vec<StockPosition>> {
        let mut all_positions = Vec::new();

        if let Some(alpaca) = &self.alpaca {
            let positions = alpaca.get_positions().await?;
            all_positions.extend(positions);
        }

        // Add other brokerages...

        Ok(all_positions)
    }

    /// Place order on best brokerage (based on fees, speed, etc.)
    pub async fn place_order(&self, order: StockOrder) -> Result<String> {
        // For now, default to Alpaca
        if let Some(alpaca) = &self.alpaca {
            return alpaca.place_order(order).await;
        }

        Err(anyhow::anyhow!("No brokerage connected"))
    }

    /// Calculate total portfolio value
    pub async fn get_total_value(&self) -> Result<f64> {
        let positions = self.get_all_positions().await?;
        Ok(positions.iter().map(|p| p.market_value).sum())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_alpaca_client() {
        // Integration test - requires Alpaca API keys
        let api_key = std::env::var("ALPACA_API_KEY").unwrap_or_default();
        let api_secret = std::env::var("ALPACA_API_SECRET").unwrap_or_default();

        if api_key.is_empty() || api_secret.is_empty() {
            println!("Skipping test: No Alpaca credentials");
            return;
        }

        let client = AlpacaClient::new(api_key, api_secret, true);
        let account = client.get_account().await;
        
        assert!(account.is_ok());
    }
}


