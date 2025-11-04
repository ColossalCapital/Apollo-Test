// Apollo Strategy Generator
// AI-powered personalized investment strategy generation

use crate::services::atlas_integration::{
    AtlasClient, CompleteFinancialProfile, FinancialGoal, ApolloStrategy, StrategyAction
};
use crate::services::delt_client::DeltClient;
use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Strategy generator that creates personalized investment plans
pub struct StrategyGenerator {
    atlas: AtlasClient,
    delt: DeltClient,
    ai_endpoint: String,  // Ollama or OpenAI endpoint
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PortfolioAnalysis {
    pub current_allocation: AllocationBreakdown,
    pub target_allocation: AllocationBreakdown,
    pub gap: AllocationGap,
    pub required_return: f64,
    pub risk_assessment: RiskAssessment,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AllocationBreakdown {
    pub stocks: f64,
    pub crypto: f64,
    pub nfts: f64,
    pub cash: f64,
    pub total: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AllocationGap {
    pub stocks_diff: f64,
    pub crypto_diff: f64,
    pub nfts_diff: f64,
    pub cash_diff: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskAssessment {
    pub volatility: f64,
    pub sharpe_ratio: f64,
    pub max_drawdown: f64,
    pub var_95: f64,  // Value at Risk (95%)
    pub risk_score: f64,  // 0-10
}

impl StrategyGenerator {
    pub fn new(atlas: AtlasClient, delt: DeltClient, ai_endpoint: String) -> Self {
        Self {
            atlas,
            delt,
            ai_endpoint,
        }
    }

    /// Generate personalized strategy for a user
    pub async fn generate_strategy(&self, user_id: &str) -> Result<ApolloStrategy> {
        // 1. Get complete financial profile from Atlas
        let profile = self.atlas.get_complete_profile(user_id).await
            .context("Failed to get user profile from Atlas")?;

        // 2. Get current positions from Delt
        let delt_portfolio = self.delt.get_portfolio(user_id).await
            .context("Failed to get portfolio from Delt")?;

        // 3. Get brokerage positions (stocks)
        let stock_portfolio = self.get_stock_positions(user_id).await?;

        // 4. Analyze current vs target
        let analysis = self.analyze_portfolio(&profile, &delt_portfolio, &stock_portfolio)?;

        // 5. Generate strategy using AI
        let strategy = self.generate_ai_strategy(&profile, &analysis).await?;

        // 6. Save strategy to Atlas
        let saved_strategy = self.atlas.create_strategy(strategy).await?;

        Ok(saved_strategy)
    }

    /// Analyze portfolio and calculate gaps
    fn analyze_portfolio(
        &self,
        profile: &CompleteFinancialProfile,
        crypto_positions: &serde_json::Value,
        stock_positions: &serde_json::Value,
    ) -> Result<PortfolioAnalysis> {
        // Calculate current allocation
        let crypto_value = self.sum_position_values(crypto_positions)?;
        let stock_value = self.sum_position_values(stock_positions)?;
        let nft_value = 0.0; // TODO: Get from NFT service
        let cash_value = profile.financial_data.as_ref()
            .map(|d| d.emergency_fund)
            .unwrap_or(0.0);

        let total = crypto_value + stock_value + nft_value + cash_value;

        let current = AllocationBreakdown {
            stocks: stock_value,
            crypto: crypto_value,
            nfts: nft_value,
            cash: cash_value,
            total,
        };

        // Determine target allocation based on goals
        let target = self.determine_target_allocation(profile)?;

        // Calculate gap
        let gap = AllocationGap {
            stocks_diff: target.stocks - current.stocks,
            crypto_diff: target.crypto - current.crypto,
            nfts_diff: target.nfts - current.nfts,
            cash_diff: target.cash - current.cash,
        };

        // Calculate required return
        let required_return = self.calculate_required_return(profile)?;

        // Assess risk
        let risk_assessment = self.assess_risk(&current, &profile)?;

        Ok(PortfolioAnalysis {
            current_allocation: current,
            target_allocation: target,
            gap,
            required_return,
            risk_assessment,
        })
    }

    /// Determine target allocation based on user goals and risk tolerance
    fn determine_target_allocation(
        &self,
        profile: &CompleteFinancialProfile,
    ) -> Result<AllocationBreakdown> {
        // Get primary goal (or most important active goal)
        let primary_goal = profile.goals.iter()
            .find(|g| g.status == "active")
            .context("No active goals found")?;

        // Determine allocation based on risk tolerance
        let (stocks_pct, crypto_pct, nfts_pct, cash_pct) = match primary_goal.risk_tolerance.as_str() {
            "conservative" => (0.40, 0.10, 0.05, 0.45),
            "moderate" => (0.50, 0.30, 0.10, 0.10),
            "aggressive" => (0.40, 0.45, 0.10, 0.05),
            _ => (0.50, 0.30, 0.10, 0.10),
        };

        // Calculate total target value
        let total_target = profile.summary.total_goal_value;

        Ok(AllocationBreakdown {
            stocks: total_target * stocks_pct,
            crypto: total_target * crypto_pct,
            nfts: total_target * nfts_pct,
            cash: total_target * cash_pct,
            total: total_target,
        })
    }

    /// Calculate required annual return to reach goals
    fn calculate_required_return(&self, profile: &CompleteFinancialProfile) -> Result<f64> {
        let total_target = profile.summary.total_goal_value;
        let total_current = profile.summary.total_current_value;
        let gap = total_target - total_current;

        // Get primary goal for timeline
        let primary_goal = profile.goals.iter()
            .find(|g| g.status == "active")
            .context("No active goals")?;

        let years_remaining = self.years_until(primary_goal.target_date);

        if years_remaining <= 0.0 {
            return Ok(0.0);
        }

        // Simple calculation: gap / (years * monthly_contribution * 12)
        let monthly_contrib = primary_goal.monthly_contribution.unwrap_or(0.0);
        let total_contributions = monthly_contrib * 12.0 * years_remaining;

        let growth_needed = gap - total_contributions;

        if total_current > 0.0 {
            // FV = PV * (1 + r)^n
            // r = (FV/PV)^(1/n) - 1
            let required_return = (total_target / total_current).powf(1.0 / years_remaining) - 1.0;
            Ok(required_return)
        } else {
            Ok(0.08) // Default 8% if no current amount
        }
    }

    fn years_until(&self, target_date: DateTime<Utc>) -> f64 {
        let now = Utc::now();
        let duration = target_date.signed_duration_since(now);
        duration.num_days() as f64 / 365.0
    }

    fn sum_position_values(&self, positions: &serde_json::Value) -> Result<f64> {
        // Parse positions JSON and sum values
        // Simplified implementation
        Ok(0.0)
    }

    /// Assess portfolio risk
    fn assess_risk(
        &self,
        allocation: &AllocationBreakdown,
        profile: &CompleteFinancialProfile,
    ) -> Result<RiskAssessment> {
        // Simplified risk calculation
        // In production, would use historical returns, correlations, etc.

        let crypto_weight = allocation.crypto / allocation.total;
        let volatility = 0.20 + (crypto_weight * 0.60); // Higher crypto = higher volatility

        Ok(RiskAssessment {
            volatility,
            sharpe_ratio: 1.2,  // Placeholder
            max_drawdown: 0.30,
            var_95: 0.15,
            risk_score: crypto_weight * 10.0,
        })
    }

    /// Generate strategy using AI
    async fn generate_ai_strategy(
        &self,
        profile: &CompleteFinancialProfile,
        analysis: &PortfolioAnalysis,
    ) -> Result<ApolloStrategy> {
        // Generate actions to close the gap
        let mut actions = Vec::new();

        // Add rebalancing actions
        if analysis.gap.stocks_diff.abs() > 1000.0 {
            actions.push(StrategyAction {
                action_type: if analysis.gap.stocks_diff > 0.0 { "buy" } else { "sell" }.to_string(),
                asset_class: "stocks".to_string(),
                symbol: "SPY".to_string(),  // Default to S&P 500 ETF
                side: if analysis.gap.stocks_diff > 0.0 { "buy" } else { "sell" }.to_string(),
                amount: analysis.gap.stocks_diff.abs(),
                reason: format!("Rebalance to target allocation"),
                priority: 1,
            });
        }

        if analysis.gap.crypto_diff.abs() > 1000.0 {
            actions.push(StrategyAction {
                action_type: if analysis.gap.crypto_diff > 0.0 { "buy" } else { "sell" }.to_string(),
                asset_class: "crypto".to_string(),
                symbol: "BTC".to_string(),
                side: if analysis.gap.crypto_diff > 0.0 { "buy" } else { "sell" }.to_string(),
                amount: analysis.gap.crypto_diff.abs() * 0.6,
                reason: format!("Increase crypto exposure"),
                priority: 2,
            });

            actions.push(StrategyAction {
                action_type: "buy".to_string(),
                asset_class: "crypto".to_string(),
                symbol: "WTF".to_string(),
                side: "buy".to_string(),
                amount: analysis.gap.crypto_diff.abs() * 0.4,
                reason: "Platform token with high growth potential".to_string(),
                priority: 3,
            });
        }

        Ok(ApolloStrategy {
            id: 0,  // Will be set by Atlas
            strategy_id: Uuid::new_v4().to_string(),
            user_id: profile.user_id.clone(),
            goal_id: profile.goals.first().map(|g| g.id),
            name: "AI-Generated Portfolio Rebalancing".to_string(),
            description: format!(
                "Rebalance portfolio to achieve {}% annual return",
                (analysis.required_return * 100.0) as i32
            ),
            target_allocation: serde_json::to_value(&analysis.target_allocation)?,
            actions,
            expected_annual_return: analysis.required_return,
            risk_score: analysis.risk_assessment.risk_score,
            time_horizon: format!("{:.1} years", self.years_until(
                profile.goals.first().unwrap().target_date
            )),
            status: "generated".to_string(),
        })
    }

    async fn get_stock_positions(&self, user_id: &str) -> Result<serde_json::Value> {
        // TODO: Integrate with brokerage API
        Ok(serde_json::json!({}))
    }
}


