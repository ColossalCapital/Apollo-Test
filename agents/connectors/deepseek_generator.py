"""
DeepSeek Code Generator for Rust Connectors

Generates complete Rust connector code using DeepSeek Coder 33B.
"""

import os
import json
from typing import Dict, List, Optional
import aiohttp
from dataclasses import dataclass


@dataclass
class APIEndpoint:
    """Represents an API endpoint"""
    method: str
    path: str
    description: str
    parameters: List[Dict]
    response_schema: Dict


@dataclass
class GeneratedCode:
    """Container for all generated code files"""
    cargo_toml: str
    main_rs: str
    models_rs: str
    kafka_producer_rs: str
    config_rs: str
    connection_manager_rs: str
    readme_md: str


class DeepSeekCodeGenerator:
    """Generates Rust connector code using DeepSeek Coder"""
    
    def __init__(self):
        # Local Ollama (preferred)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Theta EdgeCloud (fallback if not enough RAM)
        self.theta_api_key = os.getenv("THETA_API_KEY", "")
        self.theta_endpoint = os.getenv("THETA_DEEPSEEK_ENDPOINT", "")  # Deployed model endpoint
        
        # Cloud API (last resort)
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-coder"
        
    async def generate_rust_connector(
        self,
        integration_type: str,
        api_docs: Dict,
        endpoints: List[APIEndpoint],
        auth_method: str,
    ) -> GeneratedCode:
        """Generate complete Rust connector code"""
        
        # Generate each file
        cargo_toml = await self.generate_cargo_toml(integration_type)
        main_rs = await self.generate_main_rs(integration_type, auth_method)
        models_rs = await self.generate_models_rs(integration_type, endpoints)
        kafka_producer_rs = await self.generate_kafka_producer()
        config_rs = await self.generate_config(integration_type, auth_method)
        connection_manager_rs = await self.generate_connection_manager(
            integration_type, endpoints, auth_method
        )
        readme_md = await self.generate_readme(integration_type)
        
        return GeneratedCode(
            cargo_toml=cargo_toml,
            main_rs=main_rs,
            models_rs=models_rs,
            kafka_producer_rs=kafka_producer_rs,
            config_rs=config_rs,
            connection_manager_rs=connection_manager_rs,
            readme_md=readme_md,
        )
    
    async def call_deepseek(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Call DeepSeek with intelligent routing:
        1. Try local Ollama first (free, private)
        2. Fallback to Theta EdgeCloud if not enough RAM (pay with TFUEL)
        3. Last resort: Cloud API (most expensive)
        """
        
        # Try local Ollama first
        try:
            return await self._call_ollama(prompt, max_tokens)
        except Exception as e:
            print(f"⚠️ Local Ollama failed: {e}")
        
        # Try Theta EdgeCloud
        if self.theta_endpoint:
            try:
                return await self._call_theta(prompt, max_tokens)
            except Exception as e:
                print(f"⚠️ Theta EdgeCloud failed: {e}")
        
        # Fallback to cloud API
        return await self._call_cloud_api(prompt, max_tokens)
    
    async def _call_ollama(self, prompt: str, max_tokens: int) -> str:
        """Call local Ollama instance"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "deepseek-coder:33b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.2,
                    }
                },
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                result = await response.json()
                return result["response"]
    
    async def _call_theta(self, prompt: str, max_tokens: int) -> str:
        """Call Theta EdgeCloud deployed model"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.theta_endpoint,
                headers={"Authorization": f"Bearer {self.theta_api_key}"},
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.2,
                },
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                result = await response.json()
                return result["output"]
    
    async def _call_cloud_api(self, prompt: str, max_tokens: int) -> str:
        """Call cloud API (fallback)"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert Rust developer specializing in building data connectors. Generate production-ready, idiomatic Rust code with proper error handling, async/await, and comprehensive documentation."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.2,
                }
            ) as response:
                result = await response.json()
                return result["choices"][0]["message"]["content"]
    
    async def generate_cargo_toml(self, integration_type: str) -> str:
        """Generate Cargo.toml"""
        prompt = f"""
Generate a Cargo.toml file for a Rust connector named "{integration_type}-connector".

Requirements:
- Use tokio for async runtime
- Use reqwest for HTTP requests
- Use rdkafka for Kafka streaming
- Use serde for serialization
- Use anyhow for error handling
- Use tracing for logging
- Include health check dependencies (axum)
- Include metrics dependencies (prometheus)

Output ONLY the Cargo.toml content, no explanations.
"""
        return await self.call_deepseek(prompt, max_tokens=1000)
    
    async def generate_main_rs(self, integration_type: str, auth_method: str) -> str:
        """Generate main.rs with CLI and main loop"""
        prompt = f"""
Generate a main.rs file for a Rust connector for {integration_type}.

Requirements:
- CLI with clap for configuration
- Tokio async main function
- Health check endpoint on :8080
- Metrics endpoint on :9091
- Main loop that:
  1. Connects to {integration_type} API using {auth_method}
  2. Fetches data continuously
  3. Streams to Kafka topic "{integration_type}_raw"
  4. Handles rate limiting with exponential backoff
  5. Reconnects on connection loss
- Graceful shutdown on SIGTERM
- Comprehensive error handling
- Structured logging with tracing

Output ONLY the Rust code, no explanations.
"""
        return await self.call_deepseek(prompt, max_tokens=4000)
    
    async def generate_models_rs(
        self,
        integration_type: str,
        endpoints: List[APIEndpoint]
    ) -> str:
        """Generate models.rs with data structures"""
        endpoints_desc = "\n".join([
            f"- {ep.method} {ep.path}: {ep.description}"
            for ep in endpoints[:5]  # Limit to first 5 endpoints
        ])
        
        prompt = f"""
Generate a models.rs file with Rust data structures for {integration_type} API.

API Endpoints:
{endpoints_desc}

Requirements:
- Derive Serialize, Deserialize for all structs
- Use serde_json for JSON handling
- Include proper field types (String, i64, f64, bool, Option<T>)
- Add documentation comments
- Include error types
- Use chrono for timestamps

Output ONLY the Rust code, no explanations.
"""
        return await self.call_deepseek(prompt, max_tokens=4000)
    
    async def generate_kafka_producer(self) -> str:
        """Generate kafka_producer.rs"""
        prompt = """
Generate a kafka_producer.rs file for streaming data to Kafka.

Requirements:
- Use rdkafka FutureProducer
- Async send_message function
- Proper error handling
- Configurable topic
- Serialization to JSON
- Retry logic with exponential backoff
- Metrics tracking (messages sent, errors)

Output ONLY the Rust code, no explanations.
"""
        return await self.call_deepseek(prompt, max_tokens=2000)
    
    async def generate_config(self, integration_type: str, auth_method: str) -> str:
        """Generate config.rs"""
        prompt = f"""
Generate a config.rs file for {integration_type} connector configuration.

Requirements:
- Load from environment variables
- Support for {auth_method} authentication
- Kafka broker configuration
- API endpoint URLs
- Rate limiting configuration
- Retry configuration
- Use serde for deserialization
- Validation of required fields

Output ONLY the Rust code, no explanations.
"""
        return await self.call_deepseek(prompt, max_tokens=2000)
    
    async def generate_connection_manager(
        self,
        integration_type: str,
        endpoints: List[APIEndpoint],
        auth_method: str
    ) -> str:
        """Generate connection_manager.rs"""
        endpoints_desc = "\n".join([
            f"- {ep.method} {ep.path}: {ep.description}"
            for ep in endpoints[:5]
        ])
        
        prompt = f"""
Generate a connection_manager.rs file for managing {integration_type} API connections.

Authentication: {auth_method}

API Endpoints to implement:
{endpoints_desc}

Requirements:
- Async HTTP client with reqwest
- {auth_method} authentication implementation
- Rate limiting (respect API limits)
- Exponential backoff on errors
- Connection pooling
- Request/response logging
- Metrics tracking
- Error handling with anyhow

Output ONLY the Rust code, no explanations.
"""
        return await self.call_deepseek(prompt, max_tokens=4000)
    
    async def generate_readme(self, integration_type: str) -> str:
        """Generate README.md"""
        return f"""# {integration_type.title()} Connector

Rust connector for streaming {integration_type} data to Kafka.

## Features

- Async/await with Tokio
- Kafka streaming with rdkafka
- Health check endpoint (:8080)
- Metrics endpoint (:9091)
- Exponential backoff on errors
- Graceful shutdown
- Comprehensive logging

## Configuration

Set the following environment variables:

```bash
# API Configuration
{integration_type.upper()}_API_KEY=your_api_key
{integration_type.upper()}_API_URL=https://api.{integration_type}.com

# Kafka Configuration
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC={integration_type}_raw

# Optional
LOG_LEVEL=info
RATE_LIMIT_PER_SECOND=10
```

## Usage

```bash
# Build
cargo build --release

# Run
./target/release/{integration_type}-connector

# With custom config
{integration_type.upper()}_API_KEY=xxx ./target/release/{integration_type}-connector
```

## Health Check

```bash
curl http://localhost:8080/health
```

## Metrics

```bash
curl http://localhost:9091/metrics
```

## Development

```bash
# Run tests
cargo test

# Run with logging
RUST_LOG=debug cargo run

# Format code
cargo fmt

# Lint
cargo clippy
```

## Generated by Apollo

This connector was automatically generated by the Apollo AI system.
"""


# Example usage
async def main():
    generator = DeepSeekCodeGenerator()
    
    # Example: Generate Gmail connector
    code = await generator.generate_rust_connector(
        integration_type="gmail",
        api_docs={"base_url": "https://gmail.googleapis.com"},
        endpoints=[
            APIEndpoint(
                method="GET",
                path="/gmail/v1/users/me/messages",
                description="List messages",
                parameters=[],
                response_schema={}
            )
        ],
        auth_method="OAuth2"
    )
    
    print("Generated Cargo.toml:")
    print(code.cargo_toml)
    print("\nGenerated main.rs:")
    print(code.main_rs[:500])  # First 500 chars


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
