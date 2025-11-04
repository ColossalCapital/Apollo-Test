// Apollo Atlas Integration
// Reads user financial goals and data from Atlas API

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};
use chrono::{DateTime, Utc};

/// Atlas client for reading user financial data
pub struct AtlasClient {
    base_url: String,
    api_key: String,
    client: Client,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FinancialGoal {
    pub id: i32,
    pub user_id: String,
    pub goal_type: String,
    pub name: String,
    pub description: Option<String>,
    pub target_amount: f64,
    pub current_amount: f64,
    pub monthly_contribution: Option<f64>,
    pub target_date: DateTime<Utc>,
    pub risk_tolerance: String,
    pub constraints: Option<serde_json::Value>,
    pub investment_preferences: Option<serde_json::Value>,
    pub progress_percent: f64,
    pub on_track: bool,
    pub auto_execute: bool,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserFinancialData {
    pub user_id: String,
    pub monthly_income: Option<f64>,
    pub annual_income: Option<f64>,
    pub income_sources: Option<Vec<IncomeSource>>,
    pub monthly_expenses: Option<f64>,
    pub expense_categories: Option<serde_json::Value>,
    pub total_debt: f64,
    pub debt_breakdown: Option<Vec<DebtItem>>,
    pub home_value: Option<f64>,
    pub home_mortgage: Option<f64>,
    pub other_assets: Option<Vec<Asset>>,
    pub emergency_fund: f64,
    pub emergency_fund_target: Option<f64>,
    pub tax_bracket: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IncomeSource {
    pub source: String,
    pub amount: f64,
    pub frequency: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DebtItem {
    pub debt_type: String,
    pub balance: f64,
    pub interest_rate: f64,
    pub minimum_payment: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Asset {
    pub asset_type: String,
    pub value: f64,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompleteFinancialProfile {
    pub user_id: String,
    pub timestamp: String,
    pub summary: FinancialSummary,
    pub goals: Vec<FinancialGoal>,
    pub financial_data: Option<UserFinancialData>,
    pub active_strategies: Vec<ApolloStrategy>,
    pub needs_attention: Vec<FinancialGoal>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FinancialSummary {
    pub total_goal_value: f64,
    pub total_current_value: f64,
    pub overall_progress: f64,
    pub goals_on_track: usize,
    pub goals_off_track: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApolloStrategy {
    pub id: i32,
    pub strategy_id: String,
    pub user_id: String,
    pub goal_id: Option<i32>,
    pub name: String,
    pub description: String,
    pub target_allocation: serde_json::Value,
    pub actions: Vec<StrategyAction>,
    pub expected_annual_return: f64,
    pub risk_score: f64,
    pub time_horizon: String,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategyAction {
    #[serde(rename = "type")]
    pub action_type: String,  // "buy", "sell", "rebalance", "breed_nft"
    pub asset_class: String,  // "crypto", "stocks", "nft"
    pub symbol: String,
    pub side: String,         // "buy", "sell"
    pub amount: f64,
    pub reason: String,
    pub priority: i32,
}

impl AtlasClient {
    /// Create a new Atlas client
    pub fn new(base_url: String, api_key: String) -> Self {
        Self {
            base_url,
            api_key,
            client: Client::new(),
        }
    }

    /// Get complete financial profile for a user
    pub async fn get_complete_profile(&self, user_id: &str) -> Result<CompleteFinancialProfile> {
        let url = format!(
            "{}/api/v1/financial/user-data/{}/complete-profile",
            self.base_url, user_id
        );

        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await
            .context("Failed to fetch complete profile from Atlas")?;

        if !response.status().is_success() {
            return Err(anyhow::anyhow!(
                "Atlas API error: {}",
                response.status()
            ));
        }

        let profile = response.json::<CompleteFinancialProfile>()
            .await
            .context("Failed to parse Atlas response")?;

        Ok(profile)
    }

    /// Get user's financial goals
    pub async fn get_user_goals(&self, user_id: &str) -> Result<Vec<FinancialGoal>> {
        let url = format!(
            "{}/api/v1/financial/goals/{}",
            self.base_url, user_id
        );

        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await?;

        #[derive(Deserialize)]
        struct GoalsResponse {
            goals: Vec<FinancialGoal>,
        }

        let data = response.json::<GoalsResponse>().await?;
        Ok(data.goals)
    }

    /// Get user's financial data
    pub async fn get_financial_data(&self, user_id: &str) -> Result<Option<UserFinancialData>> {
        let url = format!(
            "{}/api/v1/financial/user-data/{}",
            self.base_url, user_id
        );

        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await?;

        #[derive(Deserialize)]
        struct DataResponse {
            has_data: bool,
            financial_data: Option<UserFinancialData>,
        }

        let data = response.json::<DataResponse>().await?;
        Ok(data.financial_data)
    }

    /// Create a new strategy (Apollo writes to Atlas)
    pub async fn create_strategy(&self, strategy: ApolloStrategy) -> Result<ApolloStrategy> {
        let url = format!("{}/api/v1/financial/strategies", self.base_url);

        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&strategy)
            .send()
            .await?;

        let created = response.json::<ApolloStrategy>().await?;
        Ok(created)
    }

    /// Update goal progress (Apollo reports back)
    pub async fn update_goal_progress(
        &self,
        goal_id: i32,
        amount: f64,
        progress_percent: f64,
        on_track: bool,
        apollo_actions: Option<serde_json::Value>,
    ) -> Result<()> {
        let url = format!(
            "{}/api/v1/financial/goals/{}/progress",
            self.base_url, goal_id
        );

        #[derive(Serialize)]
        struct ProgressUpdate {
            amount: f64,
            progress_percent: f64,
            on_track: bool,
            change_source: String,
            apollo_actions: Option<serde_json::Value>,
        }

        let update = ProgressUpdate {
            amount,
            progress_percent,
            on_track,
            change_source: "apollo_execution".to_string(),
            apollo_actions,
        };

        self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&update)
            .send()
            .await?;

        Ok(())
    }

    /// Mark strategy as executing
    pub async fn mark_strategy_executing(&self, strategy_id: &str) -> Result<()> {
        let url = format!(
            "{}/api/v1/financial/strategies/{}/execute",
            self.base_url, strategy_id
        );

        self.client
            .put(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await?;

        Ok(())
    }

    /// Report strategy completion
    pub async fn complete_strategy(
        &self,
        strategy_id: &str,
        results: serde_json::Value,
    ) -> Result<()> {
        let url = format!(
            "{}/api/v1/financial/strategies/{}/complete",
            self.base_url, strategy_id
        );

        #[derive(Serialize)]
        struct CompletionRequest {
            execution_results: serde_json::Value,
        }

        self.client
            .put(&url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&CompletionRequest { execution_results: results })
            .send()
            .await?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_atlas_client() {
        let client = AtlasClient::new(
            "http://localhost:8000".to_string(),
            "test_api_key".to_string(),
        );

        // This would fail without a running Atlas instance
        // In production, use integration tests with real Atlas
    }
}


