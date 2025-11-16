// Apollo Executor
// Main orchestration service that reads from Atlas and executes via Delt + Brokerages

use crate::services::atlas_integration::{AtlasClient, ApolloStrategy, StrategyAction};
use crate::services::delt_client::DeltClient;
use crate::services::brokerage_client::{UnifiedBrokerageClient, StockOrder};
use crate::services::strategy_generator::StrategyGenerator;
use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::time::{sleep, Duration};
use tracing::{info, warn, error};

/// Apollo Executor - the brain of the AI agent
pub struct ApolloExecutor {
    atlas: Arc<AtlasClient>,
    delt: Arc<DeltClient>,
    brokerage: Arc<UnifiedBrokerageClient>,
    strategy_gen: Arc<StrategyGenerator>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResult {
    pub strategy_id: String,
    pub user_id: String,
    pub executed: Vec<ExecutedAction>,
    pub failed: Vec<FailedAction>,
    pub total_executed: usize,
    pub total_failed: usize,
    pub execution_time_seconds: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutedAction {
    pub action: StrategyAction,
    pub result_id: String,  // Order ID or TX hash
    pub executed_at: String,
    pub executed_price: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FailedAction {
    pub action: StrategyAction,
    pub error: String,
    pub failed_at: String,
}

impl ApolloExecutor {
    pub fn new(
        atlas: Arc<AtlasClient>,
        delt: Arc<DeltClient>,
        brokerage: Arc<UnifiedBrokerageClient>,
        strategy_gen: Arc<StrategyGenerator>,
    ) -> Self {
        Self {
            atlas,
            delt,
            brokerage,
            strategy_gen,
        }
    }

    /// Main execution loop - runs continuously
    pub async fn run(&self) -> Result<()> {
        info!("Apollo Executor started");

        loop {
            // Check all users with auto-execute enabled
            // For now, we'll process one user at a time
            
            // Sleep for 1 minute between checks
            sleep(Duration::from_secs(60)).await;
        }
    }

    /// Generate and execute strategy for a user
    pub async fn process_user(&self, user_id: &str) -> Result<ExecutionResult> {
        info!("Processing user: {}", user_id);

        // 1. Generate strategy
        let strategy = self.strategy_gen.generate_strategy(user_id).await
            .context("Failed to generate strategy")?;

        info!("Generated strategy: {} with {} actions", strategy.name, strategy.actions.len());

        // 2. Wait for user approval (or auto-approve if auto_execute is enabled)
        // For now, we'll assume manual approval
        info!("Waiting for user approval...");
        
        // In production, this would poll Atlas for approval status
        // For demo, we'll skip this step

        // 3. Execute strategy
        let result = self.execute_strategy(&strategy).await?;

        // 4. Report results back to Atlas
        self.report_results(&strategy, &result).await?;

        Ok(result)
    }

    /// Execute a strategy
    async fn execute_strategy(&self, strategy: &ApolloStrategy) -> Result<ExecutionResult> {
        let start_time = std::time::Instant::now();
        let mut executed = Vec::new();
        let mut failed = Vec::new();

        // Mark as executing in Atlas
        self.atlas.mark_strategy_executing(&strategy.strategy_id).await?;

        // Execute each action
        for action in &strategy.actions {
            match self.execute_action(action).await {
                Ok(result_id) => {
                    info!("Executed action: {:?} -> {}", action, result_id);
                    
                    executed.push(ExecutedAction {
                        action: action.clone(),
                        result_id,
                        executed_at: chrono::Utc::now().to_rfc3339(),
                        executed_price: None, // TODO: Get actual price
                    });
                }
                Err(e) => {
                    warn!("Failed to execute action: {:?} -> {}", action, e);
                    
                    failed.push(FailedAction {
                        action: action.clone(),
                        error: e.to_string(),
                        failed_at: chrono::Utc::now().to_rfc3339(),
                    });
                }
            }

            // Small delay between orders
            sleep(Duration::from_millis(500)).await;
        }

        let execution_time = start_time.elapsed().as_secs_f64();

        Ok(ExecutionResult {
            strategy_id: strategy.strategy_id.clone(),
            user_id: strategy.user_id.clone(),
            executed: executed.clone(),
            failed: failed.clone(),
            total_executed: executed.len(),
            total_failed: failed.len(),
            execution_time_seconds: execution_time,
        })
    }

    /// Execute a single action
    async fn execute_action(&self, action: &StrategyAction) -> Result<String> {
        match action.asset_class.as_str() {
            "crypto" => self.execute_crypto_action(action).await,
            "stocks" => self.execute_stock_action(action).await,
            "nft" => self.execute_nft_action(action).await,
            _ => Err(anyhow::anyhow!("Unknown asset class: {}", action.asset_class)),
        }
    }

    /// Execute crypto action via Delt
    async fn execute_crypto_action(&self, action: &StrategyAction) -> Result<String> {
        info!("Executing crypto action: {} {} {}", action.side, action.amount, action.symbol);

        let order = serde_json::json!({
            "user_id": "user123", // TODO: Get from action
            "symbol": action.symbol,
            "side": action.side,
            "amount_usd": action.amount,
            "order_type": "market",
        });

        let tx_hash = self.delt.place_order(&order).await
            .context("Failed to place crypto order")?;

        Ok(tx_hash)
    }

    /// Execute stock action via brokerage
    async fn execute_stock_action(&self, action: &StrategyAction) -> Result<String> {
        info!("Executing stock action: {} {} {}", action.side, action.amount, action.symbol);

        // Calculate quantity (amount in USD / current price)
        // For simplicity, we'll use amount directly
        let quantity = action.amount / 100.0; // Assume $100/share avg

        let order = StockOrder {
            symbol: action.symbol.clone(),
            side: action.side.clone(),
            quantity,
            order_type: "market".to_string(),
            limit_price: None,
            stop_price: None,
            time_in_force: "day".to_string(),
        };

        let order_id = self.brokerage.place_order(order).await
            .context("Failed to place stock order")?;

        Ok(order_id)
    }

    /// Execute NFT action via Delt
    async fn execute_nft_action(&self, action: &StrategyAction) -> Result<String> {
        info!("Executing NFT action: {}", action.action_type);

        match action.action_type.as_str() {
            "breed" => {
                // Call Delt NFT breeding endpoint
                let result = self.delt.breed_nft(&action.symbol).await?;
                Ok(result)
            }
            "buy" => {
                // Buy NFT from marketplace
                let result = self.delt.buy_nft(&action.symbol, action.amount).await?;
                Ok(result)
            }
            "lock_collateral" => {
                // Lock NFT as DELT collateral
                let result = self.delt.lock_nft_collateral(&action.symbol).await?;
                Ok(result)
            }
            _ => Err(anyhow::anyhow!("Unknown NFT action: {}", action.action_type)),
        }
    }

    /// Report execution results back to Atlas
    async fn report_results(
        &self,
        strategy: &ApolloStrategy,
        result: &ExecutionResult,
    ) -> Result<()> {
        info!("Reporting results to Atlas for strategy: {}", strategy.strategy_id);

        // Complete strategy in Atlas
        let results_json = serde_json::to_value(result)?;
        self.atlas.complete_strategy(&strategy.strategy_id, results_json).await?;

        // Update goal progress for each related goal
        if let Some(goal_id) = strategy.goal_id {
            // Calculate new portfolio value
            let new_value = self.calculate_new_portfolio_value(result).await?;

            // Update goal
            self.atlas.update_goal_progress(
                goal_id,
                new_value,
                (new_value / strategy.target_allocation.get("total").unwrap_or(&serde_json::json!(1000000)).as_f64().unwrap_or(1000000.0)) * 100.0,
                true, // Simplified - should calculate if on track
                Some(results_json),
            ).await?;
        }

        Ok(())
    }

    async fn calculate_new_portfolio_value(&self, result: &ExecutionResult) -> Result<f64> {
        // TODO: Query actual portfolio value from Delt + brokerages
        // For now, return placeholder
        Ok(150000.0)
    }

    /// Monitor and rebalance (run periodically)
    pub async fn monitor_and_rebalance(&self, user_id: &str) -> Result<()> {
        info!("Monitoring portfolio for user: {}", user_id);

        // 1. Get current allocation
        let crypto_value = self.delt.get_portfolio_value(user_id).await?;
        let stock_value = self.brokerage.get_total_value().await?;
        let total = crypto_value + stock_value;

        let current_allocation = serde_json::json!({
            "crypto": crypto_value / total,
            "stocks": stock_value / total,
        });

        // 2. Get target allocation from active strategy
        let profile = self.atlas.get_complete_profile(user_id).await?;
        
        if let Some(active_strategy) = profile.active_strategies.first() {
            let target_allocation = &active_strategy.target_allocation;

            // 3. Calculate drift
            let drift = self.calculate_drift(&current_allocation, target_allocation);

            // 4. If drift > 5%, trigger rebalance
            if drift > 0.05 {
                info!("Portfolio drift detected: {:.2}%. Rebalancing...", drift * 100.0);
                
                // Generate rebalance strategy
                let rebalance_strategy = self.strategy_gen.generate_strategy(user_id).await?;
                
                // Execute if auto_execute enabled
                if profile.goals.iter().any(|g| g.auto_execute) {
                    self.execute_strategy(&rebalance_strategy).await?;
                } else {
                    // Just notify user
                    info!("Rebalance needed but auto_execute disabled. Notifying user.");
                }
            }
        }

        Ok(())
    }

    fn calculate_drift(&self, current: &serde_json::Value, target: &serde_json::Value) -> f64 {
        // Calculate total drift across all allocations
        let current_crypto = current.get("crypto").and_then(|v| v.as_f64()).unwrap_or(0.0);
        let target_crypto = target.get("crypto").and_then(|v| v.as_f64()).unwrap_or(0.0);
        
        (current_crypto - target_crypto).abs()
    }
}

/// Background task runner
pub async fn start_apollo_background_tasks(executor: Arc<ApolloExecutor>) {
    tokio::spawn(async move {
        loop {
            info!("Apollo background task tick");

            // Get all users with auto_execute enabled
            // For now, hardcode a test user
            let user_id = "test_user_123";

            match executor.monitor_and_rebalance(user_id).await {
                Ok(_) => info!("Successfully monitored user: {}", user_id),
                Err(e) => error!("Error monitoring user {}: {}", user_id, e),
            }

            // Sleep for 24 hours
            sleep(Duration::from_secs(24 * 60 * 60)).await;
        }
    });
}


