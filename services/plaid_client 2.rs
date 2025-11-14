// Apollo Plaid Client
// Banking integration for account linking, balances, transactions

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};
use chrono::{DateTime, Utc};

/// Plaid Banking Client
pub struct PlaidClient {
    client_id: String,
    secret: String,
    environment: PlaidEnvironment,
    client: Client,
}

#[derive(Debug, Clone)]
pub enum PlaidEnvironment {
    Sandbox,
    Development,
    Production,
}

impl PlaidEnvironment {
    fn base_url(&self) -> &str {
        match self {
            PlaidEnvironment::Sandbox => "https://sandbox.plaid.com",
            PlaidEnvironment::Development => "https://development.plaid.com",
            PlaidEnvironment::Production => "https://production.plaid.com",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LinkToken {
    pub link_token: String,
    pub expiration: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Account {
    pub account_id: String,
    pub name: String,
    pub official_name: Option<String>,
    pub account_type: String,
    pub account_subtype: String,
    pub balances: AccountBalances,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccountBalances {
    pub available: Option<f64>,
    pub current: f64,
    pub limit: Option<f64>,
    pub iso_currency_code: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub transaction_id: String,
    pub account_id: String,
    pub amount: f64,
    pub iso_currency_code: String,
    pub date: String,
    pub name: String,
    pub merchant_name: Option<String>,
    pub payment_channel: String,
    pub category: Vec<String>,
    pub pending: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Investment {
    pub account_id: String,
    pub security_id: String,
    pub institution_price: f64,
    pub institution_value: f64,
    pub quantity: f64,
    pub iso_currency_code: String,
}

impl PlaidClient {
    pub fn new(client_id: String, secret: String, environment: PlaidEnvironment) -> Self {
        Self {
            client_id,
            secret,
            environment,
            client: Client::new(),
        }
    }

    /// Create a Link token for user to connect their bank
    pub async fn create_link_token(&self, user_id: &str) -> Result<LinkToken> {
        let url = format!("{}/link/token/create", self.environment.base_url());

        #[derive(Serialize)]
        struct Request {
            client_id: String,
            secret: String,
            user: User,
            client_name: String,
            products: Vec<String>,
            country_codes: Vec<String>,
            language: String,
        }

        #[derive(Serialize)]
        struct User {
            client_user_id: String,
        }

        let request = Request {
            client_id: self.client_id.clone(),
            secret: self.secret.clone(),
            user: User {
                client_user_id: user_id.to_string(),
            },
            client_name: "Delt".to_string(),
            products: vec!["transactions".to_string(), "investments".to_string(), "auth".to_string()],
            country_codes: vec!["US".to_string()],
            language: "en".to_string(),
        };

        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await
            .context("Failed to create link token")?;

        let link_token: LinkToken = response.json().await?;
        Ok(link_token)
    }

    /// Exchange public token for access token
    pub async fn exchange_public_token(&self, public_token: &str) -> Result<String> {
        let url = format!("{}/item/public_token/exchange", self.environment.base_url());

        #[derive(Serialize)]
        struct Request {
            client_id: String,
            secret: String,
            public_token: String,
        }

        #[derive(Deserialize)]
        struct Response {
            access_token: String,
        }

        let request = Request {
            client_id: self.client_id.clone(),
            secret: self.secret.clone(),
            public_token: public_token.to_string(),
        };

        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        let result: Response = response.json().await?;
        Ok(result.access_token)
    }

    /// Get account balances
    pub async fn get_balances(&self, access_token: &str) -> Result<Vec<Account>> {
        let url = format!("{}/accounts/balance/get", self.environment.base_url());

        #[derive(Serialize)]
        struct Request {
            client_id: String,
            secret: String,
            access_token: String,
        }

        #[derive(Deserialize)]
        struct Response {
            accounts: Vec<Account>,
        }

        let request = Request {
            client_id: self.client_id.clone(),
            secret: self.secret.clone(),
            access_token: access_token.to_string(),
        };

        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        let result: Response = response.json().await?;
        Ok(result.accounts)
    }

    /// Get transactions
    pub async fn get_transactions(
        &self,
        access_token: &str,
        start_date: &str,
        end_date: &str,
    ) -> Result<Vec<Transaction>> {
        let url = format!("{}/transactions/get", self.environment.base_url());

        #[derive(Serialize)]
        struct Request {
            client_id: String,
            secret: String,
            access_token: String,
            start_date: String,
            end_date: String,
        }

        #[derive(Deserialize)]
        struct Response {
            transactions: Vec<Transaction>,
        }

        let request = Request {
            client_id: self.client_id.clone(),
            secret: self.secret.clone(),
            access_token: access_token.to_string(),
            start_date: start_date.to_string(),
            end_date: end_date.to_string(),
        };

        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        let result: Response = response.json().await?;
        Ok(result.transactions)
    }

    /// Get investment holdings
    pub async fn get_investments(&self, access_token: &str) -> Result<Vec<Investment>> {
        let url = format!("{}/investments/holdings/get", self.environment.base_url());

        #[derive(Serialize)]
        struct Request {
            client_id: String,
            secret: String,
            access_token: String,
        }

        #[derive(Deserialize)]
        struct Response {
            holdings: Vec<Investment>,
        }

        let request = Request {
            client_id: self.client_id.clone(),
            secret: self.secret.clone(),
            access_token: access_token.to_string(),
        };

        let response = self.client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        let result: Response = response.json().await?;
        Ok(result.holdings)
    }

    /// Calculate net worth from Plaid data
    pub async fn calculate_net_worth(&self, access_token: &str) -> Result<f64> {
        let accounts = self.get_balances(access_token).await?;
        let investments = self.get_investments(access_token).await?;

        // Sum all account balances
        let account_total: f64 = accounts.iter()
            .map(|a| a.balances.current)
            .sum();

        // Sum all investment values
        let investment_total: f64 = investments.iter()
            .map(|i| i.institution_value)
            .sum();

        Ok(account_total + investment_total)
    }
}

