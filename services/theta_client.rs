// Apollo Theta GPU Client
// Integration with Theta Edge Network for distributed GPU computing

use reqwest::Client;
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};
use tokio::time::{sleep, Duration};

/// Theta Edge Compute Client
pub struct ThetaClient {
    api_url: String,
    api_key: String,
    wallet_address: String,
    client: Client,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComputeJob {
    pub job_id: String,
    pub job_type: JobType,
    pub input_data: String,        // IPFS/Filecoin hash
    pub output_bucket: String,     // Where to store results
    pub gpu_requirements: GpuRequirements,
    pub max_cost: f64,             // Max TFUEL to spend
    pub timeout: u64,              // Seconds
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum JobType {
    ModelTraining,
    Backtesting,
    Inference,
    Rendering,
    VideoProcessing,
    Simulation,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuRequirements {
    pub min_vram: u64,             // GB
    pub min_compute_capability: String,  // e.g., "8.0" for A100
    pub preferred_gpu: Option<String>,   // "A100", "V100", "RTX4090", etc.
    pub num_gpus: u32,             // For multi-GPU jobs
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JobResult {
    pub job_id: String,
    pub status: JobStatus,
    pub result_hash: Option<String>,  // IPFS/Filecoin hash
    pub cost: f64,                    // Actual TFUEL spent
    pub compute_time: u64,            // Seconds
    pub gpu_used: String,             // "RTX4090", "A100", etc.
    pub node_location: String,        // Geographic location
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum JobStatus {
    Pending,
    Queued,
    Running,
    Completed,
    Failed,
    Timeout,
    Cancelled,
}

impl ThetaClient {
    pub fn new(api_url: String, api_key: String, wallet_address: String) -> Self {
        Self {
            api_url,
            api_key,
            wallet_address,
            client: Client::new(),
        }
    }

    /// Submit a compute job to Theta Edge Network
    pub async fn submit_job(&self, job: ComputeJob) -> Result<String> {
        let url = format!("{}/v1/compute/submit", self.api_url);

        let response = self.client
            .post(&url)
            .header("X-API-Key", &self.api_key)
            .header("X-Wallet-Address", &self.wallet_address)
            .json(&job)
            .send()
            .await
            .context("Failed to submit job to Theta")?;

        if !response.status().is_success() {
            return Err(anyhow::anyhow!(
                "Theta API error: {}",
                response.text().await?
            ));
        }

        #[derive(Deserialize)]
        struct SubmitResponse {
            job_id: String,
            estimated_cost: f64,
            queue_position: Option<u32>,
        }

        let result: SubmitResponse = response.json().await?;
        
        tracing::info!(
            "Job submitted to Theta: {} (estimated cost: {} TFUEL)",
            result.job_id,
            result.estimated_cost
        );

        Ok(result.job_id)
    }

    /// Check job status
    pub async fn get_job_status(&self, job_id: &str) -> Result<JobResult> {
        let url = format!("{}/v1/compute/status/{}", self.api_url, job_id);

        let response = self.client
            .get(&url)
            .header("X-API-Key", &self.api_key)
            .send()
            .await
            .context("Failed to get job status")?;

        let result: JobResult = response.json().await?;
        Ok(result)
    }

    /// Wait for job completion (with polling)
    pub async fn wait_for_completion(&self, job_id: &str, timeout: u64) -> Result<JobResult> {
        let start = std::time::Instant::now();
        let mut poll_interval = 5; // Start with 5 seconds
        
        loop {
            let result = self.get_job_status(job_id).await?;
            
            tracing::debug!(
                "Job {} status: {:?} (elapsed: {}s)",
                job_id,
                result.status,
                start.elapsed().as_secs()
            );
            
            match result.status {
                JobStatus::Completed => {
                    tracing::info!(
                        "Job {} completed! Cost: {} TFUEL, Time: {}s, GPU: {}",
                        job_id,
                        result.cost,
                        result.compute_time,
                        result.gpu_used
                    );
                    return Ok(result);
                }
                JobStatus::Failed => {
                    return Err(anyhow::anyhow!("Job failed: {}", job_id));
                }
                JobStatus::Timeout => {
                    return Err(anyhow::anyhow!("Job timed out: {}", job_id));
                }
                JobStatus::Cancelled => {
                    return Err(anyhow::anyhow!("Job cancelled: {}", job_id));
                }
                _ => {
                    // Still running, check timeout
                    if start.elapsed().as_secs() > timeout {
                        return Err(anyhow::anyhow!("Polling timeout for job: {}", job_id));
                    }
                    
                    // Exponential backoff (max 60s)
                    poll_interval = std::cmp::min(poll_interval * 2, 60);
                    sleep(Duration::from_secs(poll_interval)).await;
                }
            }
        }
    }

    /// Estimate job cost
    pub async fn estimate_cost(&self, job: &ComputeJob) -> Result<f64> {
        let url = format!("{}/v1/compute/estimate", self.api_url);

        let response = self.client
            .post(&url)
            .header("X-API-Key", &self.api_key)
            .json(job)
            .send()
            .await
            .context("Failed to estimate cost")?;

        #[derive(Deserialize)]
        struct EstimateResponse {
            estimated_cost: f64,
            estimated_time: u64,
            available_gpus: Vec<String>,
        }

        let result: EstimateResponse = response.json().await?;
        
        tracing::info!(
            "Estimated cost: {} TFUEL, time: {}s, GPUs: {:?}",
            result.estimated_cost,
            result.estimated_time,
            result.available_gpus
        );

        Ok(result.estimated_cost)
    }

    /// Cancel a running job
    pub async fn cancel_job(&self, job_id: &str) -> Result<()> {
        let url = format!("{}/v1/compute/cancel/{}", self.api_url, job_id);

        self.client
            .post(&url)
            .header("X-API-Key", &self.api_key)
            .send()
            .await
            .context("Failed to cancel job")?;

        tracing::info!("Job cancelled: {}", job_id);
        Ok(())
    }

    /// Get available GPU nodes
    pub async fn get_available_nodes(&self) -> Result<Vec<GpuNode>> {
        let url = format!("{}/v1/nodes/available", self.api_url);

        let response = self.client
            .get(&url)
            .header("X-API-Key", &self.api_key)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct NodesResponse {
            nodes: Vec<GpuNode>,
        }

        let result: NodesResponse = response.json().await?;
        Ok(result.nodes)
    }

    /// Get account TFUEL balance
    pub async fn get_balance(&self) -> Result<f64> {
        let url = format!("{}/v1/account/balance", self.api_url);

        let response = self.client
            .get(&url)
            .header("X-API-Key", &self.api_key)
            .header("X-Wallet-Address", &self.wallet_address)
            .send()
            .await?;

        #[derive(Deserialize)]
        struct BalanceResponse {
            tfuel_balance: f64,
        }

        let result: BalanceResponse = response.json().await?;
        Ok(result.tfuel_balance)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuNode {
    pub node_id: String,
    pub gpu_model: String,
    pub vram: u64,
    pub compute_capability: String,
    pub location: String,
    pub price_per_hour: f64,  // TFUEL
    pub available: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_theta_client() {
        // This would require actual Theta credentials
        // For now, just test that the client can be created
        let client = ThetaClient::new(
            "https://api.theta.network".to_string(),
            "test_api_key".to_string(),
            "0x1234...".to_string(),
        );

        assert_eq!(client.api_url, "https://api.theta.network");
    }
}

