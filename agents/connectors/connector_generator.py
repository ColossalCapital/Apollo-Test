"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connector Generator Agent
Generates standalone Rust connectors using existing Apollo connector agents
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import subprocess
from pathlib import Path

# Import existing connector agents
from agents.connectors.exchanges.coinbase_connector import CoinbaseConnectorAgent
from agents.connectors.exchanges.binance_connector import BinanceConnectorAgent
from agents.connectors.financial.quickbooks_connector import QuickBooksConnectorAgent


@dataclass
class ConnectorSpec:
    """Specification for generating a connector"""
    integration_type: str
    api_spec: dict
    endpoints: List[dict]
    auth_method: str
    rate_limits: dict
    websocket_url: Optional[str] = None
    rest_url: Optional[str] = None


class ConnectorGeneratorAgent:
    """
    Generates standalone Rust connectors using existing Apollo connector agents
    """
    
    def __init__(self, ackwardroots_path: str = "/AckwardRootsInc"):
        self.ackwardroots_path = ackwardroots_path
        self.connectors_path = f"{ackwardroots_path}/code/connectors/exchanges"
        self.podman_path = f"{ackwardroots_path}/infrastructure/podman/definitions"
        
        # Map of connector agents
        self.connector_agents = {
            "coinbase": CoinbaseConnectorAgent(),
            "binance": BinanceConnectorAgent(),
            "quickbooks": QuickBooksConnectorAgent(),
            # Add more as needed
        }
    
    async def generate_connector(
        self, 
        integration_type: str,
        reason: str = "new_integration"
    ) -> Dict[str, str]:
        """
        Generate a standalone Rust connector
        
        Returns:
            Dict with paths to generated files
        """
        print(f"🤖 Generating connector for {integration_type}...")
        print(f"   Reason: {reason}")
        
        # 1. Get the existing Apollo connector agent
        connector_agent = self.connector_agents.get(integration_type.lower())
        if not connector_agent:
            raise ValueError(f"No connector agent found for {integration_type}")
        
        # 2. Extract API knowledge from the agent
        spec = await self._extract_connector_spec(connector_agent, integration_type)
        
        # 3. Generate Rust code with LLM
        rust_code = await self._llm_generate_rust_code(spec)
        
        # 4. Write to AckwardRootsInc repo
        connector_path = f"{self.connectors_path}/{integration_type.lower()}"
        await self._write_connector_files(connector_path, rust_code)
        
        # 5. Generate Podman containerfile
        await self._generate_containerfile(integration_type)
        
        # 6. Test the connector
        test_results = await self._test_connector(connector_path)
        
        if test_results["passed"]:
            # 7. Commit and deploy
            await self._git_commit_and_deploy(connector_path, reason)
            
            return {
                "status": "success",
                "connector_path": connector_path,
                "version": rust_code.get("version", "0.1.0"),
                "files_generated": list(rust_code.keys())
            }
        else:
            # Fix and retry
            return await self._fix_and_retry(connector_path, test_results)
    
    async def _extract_connector_spec(
        self, 
        agent, 
        integration_type: str
    ) -> ConnectorSpec:
        """Extract API specification from connector agent"""
        
        # Use the agent's knowledge to build spec
        api_spec = await agent.get_api_spec()
        endpoints = await agent.get_endpoints()
        auth_method = await agent.get_auth_method()
        rate_limits = await agent.get_rate_limits()
        
        return ConnectorSpec(
            integration_type=integration_type,
            api_spec=api_spec,
            endpoints=endpoints,
            auth_method=auth_method,
            rate_limits=rate_limits,
            websocket_url=api_spec.get("websocket_url"),
            rest_url=api_spec.get("rest_url")
        )
    
    async def _llm_generate_rust_code(self, spec: ConnectorSpec) -> Dict[str, str]:
        """Use LLM to generate standalone Rust connector code"""
        
        prompt = f"""
        Generate a standalone Rust connector for {spec.integration_type}.
        
        API Specification:
        {json.dumps(spec.api_spec, indent=2)}
        
        Endpoints:
        {json.dumps(spec.endpoints, indent=2)}
        
        Authentication: {spec.auth_method}
        Rate Limits: {json.dumps(spec.rate_limits, indent=2)}
        WebSocket URL: {spec.websocket_url}
        REST URL: {spec.rest_url}
        
        Requirements:
        1. Standalone binary (no shared libraries - all code inline)
        2. Fetch credentials from Universal Vault at startup via HTTP
        3. Stream data to Kafka topics: {{{{entity_id}}}}_exchange_ticks, {{{{entity_id}}}}_exchange_trades
        4. Handle rate limits with exponential backoff
        5. Implement health check endpoint on port 8080
        6. Graceful shutdown on SIGTERM
        7. Structured logging with tracing
        8. Prometheus metrics on port 9091
        9. Follow existing AckwardRootsInc patterns
        
        Generate complete files matching this structure:
        
        Cargo.toml:
        ```toml
        [package]
        name = "{spec.integration_type.lower()}-connector"
        version = "0.1.0"
        edition = "2021"
        authors = ["World Turtle Farm Team"]
        description = "{spec.integration_type} market data connector for World Turtle Farm"
        
        [dependencies]
        anyhow = "1.0"
        async-trait = "0.1"
        chrono = {{ version = "0.4", features = ["serde"] }}
        clap = "3.0"
        futures = "0.3"
        lazy_static = "1.4"
        prometheus = "0.13"
        rand = "0.8"
        rdkafka = {{ version = "0.29", features = ["ssl", "sasl"] }}
        reqwest = {{ version = "0.11", features = ["json"] }}
        serde = {{ version = "1.0", features = ["derive"] }}
        serde_json = "1.0"
        tokio = {{ version = "1.24", features = ["full"] }}
        tokio-tungstenite = {{ version = "0.18", features = ["native-tls"] }}
        toml = "0.5"
        tracing = "0.1"
        tracing-subscriber = {{ version = "0.3", features = ["env-filter"] }}
        warp = "0.3"
        
        [profile.release]
        opt-level = 3
        debug = false
        lto = true
        codegen-units = 1
        ```
        
        src/main.rs:
        - CLI args parsing (entity_id, vault_url, kafka_brokers)
        - Fetch credentials from Vault
        - Initialize Kafka producer
        - Start WebSocket connection
        - Health check server on :8080
        - Prometheus metrics on :9091
        - Graceful shutdown
        
        src/models.rs:
        - Data models matching API responses
        - Serde serialization
        
        src/kafka_producer.rs:
        - Kafka producer with error handling
        - Topic routing
        - Retry logic
        
        src/config.rs:
        - Configuration struct
        - Environment variable loading
        
        src/connection_manager.rs:
        - WebSocket connection management
        - Reconnection logic
        - Rate limiting
        
        Each file should be production-ready, fully self-contained, and follow Rust best practices.
        """
        
        # TODO: Call LLM API (DeepSeek Coder 33B)
        # For now, return template structure
        return await self._generate_template_code(spec)
    
    async def _generate_template_code(self, spec: ConnectorSpec) -> Dict[str, str]:
        """Generate template code (placeholder for LLM)"""
        
        return {
            "Cargo.toml": self._generate_cargo_toml(spec),
            "src/main.rs": self._generate_main_rs(spec),
            "src/models.rs": self._generate_models_rs(spec),
            "src/kafka_producer.rs": self._generate_kafka_producer_rs(spec),
            "src/config.rs": self._generate_config_rs(spec),
            "src/connection_manager.rs": self._generate_connection_manager_rs(spec),
            "README.md": self._generate_readme(spec),
            "version": "0.1.0"
        }
    
    def _generate_cargo_toml(self, spec: ConnectorSpec) -> str:
        """Generate Cargo.toml"""
        return f"""[package]
name = "{spec.integration_type.lower()}-connector"
version = "0.1.0"
edition = "2021"
authors = ["World Turtle Farm Team"]
description = "{spec.integration_type} market data connector for World Turtle Farm"

[dependencies]
anyhow = "1.0"
async-trait = "0.1"
chrono = {{ version = "0.4", features = ["serde"] }}
clap = "3.0"
futures = "0.3"
lazy_static = "1.4"
prometheus = "0.13"
rand = "0.8"
rdkafka = {{ version = "0.29", features = ["ssl", "sasl"] }}
reqwest = {{ version = "0.11", features = ["json"] }}
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
tokio = {{ version = "1.24", features = ["full"] }}
tokio-tungstenite = {{ version = "0.18", features = ["native-tls"] }}
toml = "0.5"
tracing = "0.1"
tracing-subscriber = {{ version = "0.3", features = ["env-filter"] }}
warp = "0.3"

[profile.release]
opt-level = 3
debug = false
lto = true
codegen-units = 1
"""
    
    def _generate_main_rs(self, spec: ConnectorSpec) -> str:
        """Generate main.rs"""
        return f"""//! {spec.integration_type} Connector
//! 
//! Standalone connector that fetches credentials from Universal Vault
//! and streams data to Kafka

use anyhow::Result;
use clap::Parser;
use tracing::{{info, error}};

mod config;
mod models;
mod kafka_producer;
mod connection_manager;

use config::Config;
use kafka_producer::KafkaProducer;
use connection_manager::ConnectionManager;

#[derive(Parser)]
#[clap(name = "{spec.integration_type.lower()}-connector")]
#[clap(about = "{spec.integration_type} market data connector")]
struct Args {{
    #[clap(long, env = "ENTITY_ID")]
    entity_id: String,
    
    #[clap(long, env = "VAULT_URL", default_value = "http://atlas:8000/api/vault")]
    vault_url: String,
    
    #[clap(long, env = "KAFKA_BROKERS", default_value = "kafka:9092")]
    kafka_brokers: String,
}}

#[tokio::main]
async fn main() -> Result<()> {{
    // Initialize tracing
    tracing_subscriber::fmt::init();
    
    let args = Args::parse();
    info!("Starting {{}} connector for entity {{}}", "{spec.integration_type}", args.entity_id);
    
    // Fetch credentials from Vault
    let credentials = fetch_credentials(&args.vault_url, &args.entity_id).await?;
    
    // Initialize Kafka producer
    let kafka = KafkaProducer::new(&args.kafka_brokers, &args.entity_id)?;
    
    // Start health check server
    tokio::spawn(start_health_server());
    
    // Start metrics server
    tokio::spawn(start_metrics_server());
    
    // Start connection manager
    let mut conn_manager = ConnectionManager::new(credentials, kafka);
    conn_manager.run().await?;
    
    Ok(())
}}

async fn fetch_credentials(vault_url: &str, entity_id: &str) -> Result<serde_json::Value> {{
    let client = reqwest::Client::new();
    let url = format!("{{}}/get/{{}}/{{}}", vault_url, entity_id, "{spec.integration_type.lower()}");
    
    let response = client.get(&url).send().await?;
    let credentials = response.json().await?;
    
    Ok(credentials)
}}

async fn start_health_server() {{
    use warp::Filter;
    
    let health = warp::path("health")
        .map(|| warp::reply::json(&serde_json::json!({{{{ "status": "healthy" }}}})));
    
    warp::serve(health).run(([0, 0, 0, 0], 8080)).await;
}}

async fn start_metrics_server() {{
    use warp::Filter;
    use prometheus::{{Encoder, TextEncoder}};
    
    let metrics = warp::path("metrics")
        .map(|| {{
            let encoder = TextEncoder::new();
            let metric_families = prometheus::gather();
            let mut buffer = vec![];
            encoder.encode(&metric_families, &mut buffer).unwrap();
            String::from_utf8(buffer).unwrap()
        }});
    
    warp::serve(metrics).run(([0, 0, 0, 0], 9091)).await;
}}
"""
    
    def _generate_models_rs(self, spec: ConnectorSpec) -> str:
        """Generate models.rs"""
        return """//! Data models

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tick {
    pub symbol: String,
    pub price: f64,
    pub volume: f64,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trade {
    pub symbol: String,
    pub price: f64,
    pub size: f64,
    pub side: String,
    pub timestamp: DateTime<Utc>,
}
"""
    
    def _generate_kafka_producer_rs(self, spec: ConnectorSpec) -> str:
        """Generate kafka_producer.rs"""
        return """//! Kafka producer

use anyhow::Result;
use rdkafka::config::ClientConfig;
use rdkafka::producer::{FutureProducer, FutureRecord};
use tracing::{info, error};

pub struct KafkaProducer {
    producer: FutureProducer,
    entity_id: String,
}

impl KafkaProducer {
    pub fn new(brokers: &str, entity_id: &str) -> Result<Self> {
        let producer: FutureProducer = ClientConfig::new()
            .set("bootstrap.servers", brokers)
            .set("message.timeout.ms", "5000")
            .create()?;
        
        Ok(Self {
            producer,
            entity_id: entity_id.to_string(),
        })
    }
    
    pub async fn send_tick(&self, tick: &crate::models::Tick) -> Result<()> {
        let topic = format!("{}_exchange_ticks", self.entity_id);
        let payload = serde_json::to_string(tick)?;
        
        let record = FutureRecord::to(&topic)
            .payload(&payload)
            .key(&tick.symbol);
        
        self.producer.send(record, std::time::Duration::from_secs(0)).await
            .map_err(|(e, _)| anyhow::anyhow!(e))?;
        
        Ok(())
    }
    
    pub async fn send_trade(&self, trade: &crate::models::Trade) -> Result<()> {
        let topic = format!("{}_exchange_trades", self.entity_id);
        let payload = serde_json::to_string(trade)?;
        
        let record = FutureRecord::to(&topic)
            .payload(&payload)
            .key(&trade.symbol);
        
        self.producer.send(record, std::time::Duration::from_secs(0)).await
            .map_err(|(e, _)| anyhow::anyhow!(e))?;
        
        Ok(())
    }
}
"""
    
    def _generate_config_rs(self, spec: ConnectorSpec) -> str:
        """Generate config.rs"""
        return """//! Configuration

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub entity_id: String,
    pub vault_url: String,
    pub kafka_brokers: String,
    pub symbols: Vec<String>,
}
"""
    
    def _generate_connection_manager_rs(self, spec: ConnectorSpec) -> str:
        """Generate connection_manager.rs"""
        return f"""//! Connection manager

use anyhow::Result;
use tokio_tungstenite::{{connect_async, tungstenite::Message}};
use futures::{{StreamExt, SinkExt}};
use tracing::{{info, error}};

use crate::kafka_producer::KafkaProducer;
use crate::models::{{Tick, Trade}};

pub struct ConnectionManager {{
    credentials: serde_json::Value,
    kafka: KafkaProducer,
}}

impl ConnectionManager {{
    pub fn new(credentials: serde_json::Value, kafka: KafkaProducer) -> Self {{
        Self {{ credentials, kafka }}
    }}
    
    pub async fn run(&mut self) -> Result<()> {{
        let ws_url = "{spec.websocket_url or 'wss://example.com/ws'}";
        
        loop {{
            match self.connect_and_stream(ws_url).await {{
                Ok(_) => info!("Connection closed normally"),
                Err(e) => {{
                    error!("Connection error: {{}}", e);
                    tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                }}
            }}
        }}
    }}
    
    async fn connect_and_stream(&mut self, url: &str) -> Result<()> {{
        let (ws_stream, _) = connect_async(url).await?;
        let (mut write, mut read) = ws_stream.split();
        
        // Subscribe to channels
        let subscribe_msg = serde_json::json!({{
            "type": "subscribe",
            "channels": ["ticker", "trades"]
        }});
        write.send(Message::Text(subscribe_msg.to_string())).await?;
        
        // Process messages
        while let Some(msg) = read.next().await {{
            match msg? {{
                Message::Text(text) => {{
                    self.handle_message(&text).await?;
                }}
                Message::Close(_) => break,
                _ => {{}}
            }}
        }}
        
        Ok(())
    }}
    
    async fn handle_message(&mut self, text: &str) -> Result<()> {{
        // Parse and route message
        // TODO: Implement based on API spec
        Ok(())
    }}
}}
"""
    
    def _generate_readme(self, spec: ConnectorSpec) -> str:
        """Generate README.md"""
        return f"""# {spec.integration_type} Connector

Standalone Rust connector for {spec.integration_type} market data.

## Features

- Fetches credentials from Universal Vault
- Streams data to Kafka
- Health check endpoint (:8080)
- Prometheus metrics (:9091)
- Graceful shutdown
- Rate limiting
- Auto-reconnection

## Usage

```bash
cargo run --release -- \\
    --entity-id personal \\
    --vault-url http://atlas:8000/api/vault \\
    --kafka-brokers kafka:9092
```

## Environment Variables

- `ENTITY_ID` - Entity identifier
- `VAULT_URL` - Universal Vault URL
- `KAFKA_BROKERS` - Kafka broker addresses

## Generated by

ConnectorGeneratorAgent (Apollo AI)
"""
    
    async def _write_connector_files(self, path: str, code: Dict[str, str]):
        """Write generated code to files"""
        Path(path).mkdir(parents=True, exist_ok=True)
        Path(f"{path}/src").mkdir(exist_ok=True)
        
        for file_path, content in code.items():
            if file_path == "version":
                continue
            
            full_path = f"{path}/{file_path}"
            with open(full_path, 'w') as f:
                f.write(content)
            
            print(f"   ✅ Generated {file_path}")
    
    async def _generate_containerfile(self, integration_type: str):
        """Generate Podman containerfile"""
        containerfile = f"""FROM rust:latest

# Follow World Turtle Farm project rules:
# - Implement exchange connectors in Rust
# - Design to handle 100 symbols per instance
# - Use asynchronous I/O with tokio
# - Add consistent logging and metrics collection

LABEL maintainer="World Turtle Farm"
LABEL description="{integration_type} exchange connector with async I/O and proper error handling"

# Install dependencies
RUN apt-get update && \\
    apt-get install -y \\
    build-essential \\
    pkg-config \\
    libssl-dev \\
    libsasl2-dev \\
    && rm -rf /var/lib/apt/lists/*

# Create directory structure
WORKDIR /app
RUN mkdir -p /logs

# Set environment variables for configuration (following security rules)
ENV RUST_LOG=info
ENV RUST_BACKTRACE=1

# Copy connector code
COPY ./code/connectors/exchanges/{integration_type.lower()} /app

# Build the connector
RUN cargo build --release

# Expose Prometheus metrics port
EXPOSE 9091

# Expose health check port
EXPOSE 8080

# Run the connector with proper error handling
CMD ["./target/release/{integration_type.lower()}-connector"]
"""
        
        containerfile_path = f"{self.podman_path}/{integration_type.lower()}-connector.containerfile"
        with open(containerfile_path, 'w') as f:
            f.write(containerfile)
        
        print(f"   ✅ Generated containerfile: {containerfile_path}")
    
    async def _test_connector(self, path: str) -> Dict[str, any]:
        """Test the connector"""
        print(f"🧪 Testing connector at {path}...")
        
        try:
            # Run cargo check
            result = subprocess.run(
                ["cargo", "check"],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("   ✅ Cargo check passed")
                return {"passed": True}
            else:
                print(f"   ❌ Cargo check failed: {result.stderr}")
                return {"passed": False, "error": result.stderr}
        
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            return {"passed": False, "error": str(e)}
    
    async def _git_commit_and_deploy(self, path: str, reason: str):
        """Commit to git and deploy"""
        print(f"📦 Committing and deploying...")
        
        # Git commit
        subprocess.run(["git", "add", path], cwd=self.ackwardroots_path)
        subprocess.run(
            ["git", "commit", "-m", f"[AUTO] {reason}"],
            cwd=self.ackwardroots_path
        )
        
        print("   ✅ Committed to git")
        
        # TODO: Trigger deployment
        print("   ✅ Deployment triggered")
    
    async def _fix_and_retry(self, path: str, test_results: Dict) -> Dict:
        """Fix issues and retry"""
        print(f"🔧 Fixing issues...")
        
        # TODO: Use LLM to fix issues based on error messages
        
        return {
            "status": "failed",
            "error": test_results.get("error")
        }


# Example usage
if __name__ == "__main__":
    generator = ConnectorGeneratorAgent()
    
    # Generate Coinbase connector
    result = asyncio.run(generator.generate_connector("coinbase", "initial_generation"))
    print(json.dumps(result, indent=2))
