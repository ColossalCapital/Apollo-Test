// Apollo Stripe Client
// Payment processing for platform subscriptions and deposits

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};

/// Stripe Payment Client
pub struct StripeClient {
    api_key: String,
    client: Client,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaymentIntent {
    pub id: String,
    pub amount: i64,
    pub currency: String,
    pub status: String,
    pub client_secret: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Subscription {
    pub id: String,
    pub customer_id: String,
    pub status: String,
    pub plan: String,
    pub amount: i64,
    pub interval: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Customer {
    pub id: String,
    pub email: String,
    pub name: Option<String>,
}

impl StripeClient {
    pub fn new(api_key: String) -> Self {
        Self {
            api_key,
            client: Client::new(),
        }
    }

    /// Create payment intent
    pub async fn create_payment_intent(&self, amount: i64, currency: &str) -> Result<PaymentIntent> {
        let url = "https://api.stripe.com/v1/payment_intents";

        let params = [
            ("amount", amount.to_string()),
            ("currency", currency.to_string()),
        ];

        let response = self.client
            .post(url)
            .bearer_auth(&self.api_key)
            .form(&params)
            .send()
            .await?;

        let intent: PaymentIntent = response.json().await?;
        Ok(intent)
    }

    /// Create customer
    pub async fn create_customer(&self, email: &str, name: Option<&str>) -> Result<Customer> {
        let url = "https://api.stripe.com/v1/customers";

        let mut params = vec![("email", email.to_string())];
        if let Some(n) = name {
            params.push(("name", n.to_string()));
        }

        let response = self.client
            .post(url)
            .bearer_auth(&self.api_key)
            .form(&params)
            .send()
            .await?;

        let customer: Customer = response.json().await?;
        Ok(customer)
    }

    /// Create subscription
    pub async fn create_subscription(
        &self,
        customer_id: &str,
        price_id: &str,
    ) -> Result<Subscription> {
        let url = "https://api.stripe.com/v1/subscriptions";

        let params = [
            ("customer", customer_id.to_string()),
            ("items[0][price]", price_id.to_string()),
        ];

        let response = self.client
            .post(url)
            .bearer_auth(&self.api_key)
            .form(&params)
            .send()
            .await?;

        let subscription: Subscription = response.json().await?;
        Ok(subscription)
    }

    /// Cancel subscription
    pub async fn cancel_subscription(&self, subscription_id: &str) -> Result<()> {
        let url = format!("https://api.stripe.com/v1/subscriptions/{}", subscription_id);

        self.client
            .delete(&url)
            .bearer_auth(&self.api_key)
            .send()
            .await?;

        Ok(())
    }
}

