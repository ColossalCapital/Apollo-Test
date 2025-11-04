// Apollo AI Orchestrator
// Central AI coordinator that routes queries to domain-specific agents via Hermes

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Main Apollo orchestrator
pub struct ApolloOrchestrator {
    hermes_client: HermesClient,
    ollama_client: OllamaClient,
    context_store: ContextStore,
}

/// Query intent analysis result
#[derive(Debug, Clone)]
pub struct QueryIntent {
    pub domains: Vec<Domain>,
    pub query_type: QueryType,
    pub entities: Vec<Entity>,
    pub context: HashMap<String, String>,
}

/// Domain that can handle queries
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Domain {
    Trading,    // Delt agent
    Documents,  // Atlas agent
    NFT,        // WTF agent
    Code,       // Akashic agent
    General,    // No specific domain
}

/// Type of query
#[derive(Debug, Clone)]
pub enum QueryType {
    DataRetrieval,      // Simple data query
    Analysis,           // Requires AI analysis
    CrossDomain,        // Needs multiple domains
    Action,             // Execute an action
    Conversation,       // Chat/Q&A
}

/// Extracted entity from query
#[derive(Debug, Clone)]
pub struct Entity {
    pub entity_type: String,
    pub value: String,
    pub confidence: f32,
}

/// Result from a domain agent
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentResult {
    pub domain: Domain,
    pub data: serde_json::Value,
    pub confidence: f32,
    pub sources: Vec<Source>,
}

/// Source of information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Source {
    pub source_type: String,
    pub title: String,
    pub url: Option<String>,
    pub relevance: f32,
}

/// Final response to user
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApolloResponse {
    pub answer: String,
    pub sources: Vec<Source>,
    pub confidence: f32,
    pub follow_up_questions: Vec<String>,
    pub domain_results: Vec<AgentResult>,
}

impl ApolloOrchestrator {
    pub fn new(
        hermes_url: &str,
        ollama_url: &str,
    ) -> Result<Self> {
        Ok(Self {
            hermes_client: HermesClient::new(hermes_url)?,
            ollama_client: OllamaClient::new(ollama_url)?,
            context_store: ContextStore::new(),
        })
    }

    /// Main entry point - handle any user query
    pub async fn handle_query(
        &self,
        query: &str,
        user_id: &str,
        conversation_id: Option<&str>,
    ) -> Result<ApolloResponse> {
        // 1. Load conversation context if exists
        let context = if let Some(conv_id) = conversation_id {
            self.context_store.get(conv_id).await?
        } else {
            ConversationContext::new(user_id)
        };

        // 2. Analyze query intent
        let intent = self.analyze_intent(query, &context).await?;

        // 3. Route to appropriate agents
        let agent_results = self.route_to_agents(query, &intent, user_id).await?;

        // 4. Synthesize results
        let response = self.synthesize_results(query, agent_results, &intent).await?;

        // 5. Save context
        if let Some(conv_id) = conversation_id {
            self.context_store.update(conv_id, query, &response).await?;
        }

        Ok(response)
    }

    /// Analyze query to determine intent and required domains
    async fn analyze_intent(
        &self,
        query: &str,
        context: &ConversationContext,
    ) -> Result<QueryIntent> {
        // Use Ollama to analyze the query
        let prompt = format!(
            r#"Analyze this user query and determine:
1. Which domains are needed (trading, documents, nft, code, general)
2. What type of query it is (data_retrieval, analysis, cross_domain, action, conversation)
3. Extract any entities (symbols, dates, document types, etc.)

Previous context: {}
User query: {}

Respond in JSON format:
{{
    "domains": ["trading", "documents"],
    "query_type": "cross_domain",
    "entities": [
        {{"type": "symbol", "value": "BTC-USD", "confidence": 0.95}},
        {{"type": "document_type", "value": "invoice", "confidence": 0.9}}
    ]
}}"#,
            context.summary(),
            query
        );

        let analysis = self.ollama_client
            .generate(&prompt, "llama3.1:8b")
            .await?;

        // Parse JSON response
        let intent: QueryIntent = serde_json::from_str(&analysis)
            .context("Failed to parse intent analysis")?;

        Ok(intent)
    }

    /// Route query to appropriate domain agents via Hermes
    async fn route_to_agents(
        &self,
        query: &str,
        intent: &QueryIntent,
        user_id: &str,
    ) -> Result<Vec<AgentResult>> {
        let mut results = Vec::new();

        // Execute agent calls in parallel
        let mut tasks = Vec::new();

        for domain in &intent.domains {
            match domain {
                Domain::Trading => {
                    tasks.push(self.query_trading_agent(query, intent, user_id));
                }
                Domain::Documents => {
                    tasks.push(self.query_documents_agent(query, intent, user_id));
                }
                Domain::NFT => {
                    tasks.push(self.query_nft_agent(query, intent, user_id));
                }
                Domain::Code => {
                    tasks.push(self.query_code_agent(query, intent, user_id));
                }
                Domain::General => {
                    // Handle with Ollama directly
                    continue;
                }
            }
        }

        // Wait for all agent responses
        let agent_responses = futures::future::join_all(tasks).await;

        for response in agent_responses {
            if let Ok(result) = response {
                results.push(result);
            }
        }

        Ok(results)
    }

    /// Query trading agent (Delt) via Hermes
    async fn query_trading_agent(
        &self,
        query: &str,
        intent: &QueryIntent,
        user_id: &str,
    ) -> Result<AgentResult> {
        // Extract trading-specific entities
        let symbols: Vec<&str> = intent.entities
            .iter()
            .filter(|e| e.entity_type == "symbol")
            .map(|e| e.value.as_str())
            .collect();

        // Call Hermes GraphQL to get trading data
        let graphql_query = if symbols.is_empty() {
            // General market analysis
            r#"
            query MarketOverview {
                marketAnalysis(symbol: "BTC-USD") {
                    trend
                    signals
                    recommendation
                    confidence
                }
            }
            "#
        } else {
            // Specific symbol analysis
            format!(
                r#"
                query SymbolAnalysis {{
                    marketAnalysis(symbol: "{}") {{
                        trend
                        signals
                        recommendation
                        confidence
                    }}
                    currentPrice(symbol: "{}") {{
                        price
                        change24h
                        volume
                    }}
                }}
                "#,
                symbols[0], symbols[0]
            )
        };

        let response = self.hermes_client
            .graphql_query(&graphql_query)
            .await?;

        Ok(AgentResult {
            domain: Domain::Trading,
            data: response,
            confidence: 0.9,
            sources: vec![Source {
                source_type: "market_data".to_string(),
                title: "Real-time market analysis".to_string(),
                url: None,
                relevance: 1.0,
            }],
        })
    }

    /// Query documents agent (Atlas) via Hermes
    async fn query_documents_agent(
        &self,
        query: &str,
        intent: &QueryIntent,
        user_id: &str,
    ) -> Result<AgentResult> {
        // Extract document-specific entities
        let doc_types: Vec<&str> = intent.entities
            .iter()
            .filter(|e| e.entity_type == "document_type")
            .map(|e| e.value.as_str())
            .collect();

        // Call Hermes GraphQL to search documents
        let graphql_query = format!(
            r#"
            query SearchDocuments {{
                searchDocuments(query: "{}") {{
                    id
                    title
                    content
                    relevance
                    metadata {{
                        type
                        createdAt
                    }}
                }}
            }}
            "#,
            query.replace('"', "\\\"")
        );

        let response = self.hermes_client
            .graphql_query(&graphql_query)
            .await?;

        // Extract sources from documents
        let sources = if let Some(docs) = response["data"]["searchDocuments"].as_array() {
            docs.iter()
                .map(|doc| Source {
                    source_type: "document".to_string(),
                    title: doc["title"].as_str().unwrap_or("Untitled").to_string(),
                    url: Some(format!("/documents/{}", doc["id"].as_str().unwrap_or(""))),
                    relevance: doc["relevance"].as_f64().unwrap_or(0.5) as f32,
                })
                .collect()
        } else {
            vec![]
        };

        Ok(AgentResult {
            domain: Domain::Documents,
            data: response,
            confidence: 0.85,
            sources,
        })
    }

    /// Query NFT agent (WTF) via Hermes
    async fn query_nft_agent(
        &self,
        query: &str,
        intent: &QueryIntent,
        user_id: &str,
    ) -> Result<AgentResult> {
        let graphql_query = format!(
            r#"
            query NFTQuery {{
                nfts(userId: "{}") {{
                    id
                    name
                    traits
                    imageUrl
                }}
            }}
            "#,
            user_id
        );

        let response = self.hermes_client
            .graphql_query(&graphql_query)
            .await?;

        Ok(AgentResult {
            domain: Domain::NFT,
            data: response,
            confidence: 0.8,
            sources: vec![],
        })
    }

    /// Query code agent (Akashic) via Hermes
    async fn query_code_agent(
        &self,
        query: &str,
        intent: &QueryIntent,
        user_id: &str,
    ) -> Result<AgentResult> {
        let graphql_query = format!(
            r#"
            query CodeQuery {{
                strategies(userId: "{}") {{
                    id
                    name
                    code
                    performance
                }}
            }}
            "#,
            user_id
        );

        let response = self.hermes_client
            .graphql_query(&graphql_query)
            .await?;

        Ok(AgentResult {
            domain: Domain::Code,
            data: response,
            confidence: 0.85,
            sources: vec![],
        })
    }

    /// Synthesize results from multiple agents into coherent answer
    async fn synthesize_results(
        &self,
        query: &str,
        agent_results: Vec<AgentResult>,
        intent: &QueryIntent,
    ) -> Result<ApolloResponse> {
        if agent_results.is_empty() {
            // No agent results, use Ollama directly
            let answer = self.ollama_client
                .generate(query, "llama3.1:8b")
                .await?;

            return Ok(ApolloResponse {
                answer,
                sources: vec![],
                confidence: 0.7,
                follow_up_questions: vec![],
                domain_results: vec![],
            });
        }

        // Build context from all agent results
        let mut context = String::new();
        context.push_str("Based on the following information:\n\n");

        for result in &agent_results {
            context.push_str(&format!(
                "From {} domain:\n{}\n\n",
                format!("{:?}", result.domain),
                serde_json::to_string_pretty(&result.data)?
            ));
        }

        // Ask Ollama to synthesize
        let synthesis_prompt = format!(
            r#"You are Apollo AI, an intelligent assistant for the ColossalCapital platform.

User question: {}

{}

Provide a clear, concise answer that:
1. Directly answers the user's question
2. Cites specific data from the sources
3. Explains any insights or patterns
4. Suggests 2-3 relevant follow-up questions

Format your response as JSON:
{{
    "answer": "Your synthesized answer here...",
    "follow_up_questions": [
        "Question 1?",
        "Question 2?",
        "Question 3?"
    ]
}}"#,
            query, context
        );

        let synthesis = self.ollama_client
            .generate(&synthesis_prompt, "llama3.1:8b")
            .await?;

        // Parse synthesis
        let parsed: serde_json::Value = serde_json::from_str(&synthesis)
            .unwrap_or_else(|_| serde_json::json!({
                "answer": synthesis,
                "follow_up_questions": []
            }));

        // Collect all sources
        let sources: Vec<Source> = agent_results
            .iter()
            .flat_map(|r| r.sources.clone())
            .collect();

        // Calculate overall confidence
        let confidence = if agent_results.is_empty() {
            0.7
        } else {
            agent_results.iter().map(|r| r.confidence).sum::<f32>() / agent_results.len() as f32
        };

        Ok(ApolloResponse {
            answer: parsed["answer"].as_str().unwrap_or(&synthesis).to_string(),
            sources,
            confidence,
            follow_up_questions: parsed["follow_up_questions"]
                .as_array()
                .map(|arr| {
                    arr.iter()
                        .filter_map(|q| q.as_str().map(String::from))
                        .collect()
                })
                .unwrap_or_default(),
            domain_results: agent_results,
        })
    }
}

// ============================================================================
// Supporting Types
// ============================================================================

/// Hermes API client
pub struct HermesClient {
    base_url: String,
    client: reqwest::Client,
}

impl HermesClient {
    pub fn new(base_url: &str) -> Result<Self> {
        Ok(Self {
            base_url: base_url.to_string(),
            client: reqwest::Client::new(),
        })
    }

    pub async fn graphql_query(&self, query: &str) -> Result<serde_json::Value> {
        let response = self.client
            .post(&format!("{}/graphql", self.base_url))
            .json(&serde_json::json!({ "query": query }))
            .send()
            .await?
            .json()
            .await?;

        Ok(response)
    }
}

/// Ollama client for LLM inference
pub struct OllamaClient {
    base_url: String,
    client: reqwest::Client,
}

impl OllamaClient {
    pub fn new(base_url: &str) -> Result<Self> {
        Ok(Self {
            base_url: base_url.to_string(),
            client: reqwest::Client::new(),
        })
    }

    pub async fn generate(&self, prompt: &str, model: &str) -> Result<String> {
        let response: serde_json::Value = self.client
            .post(&format!("{}/api/generate", self.base_url))
            .json(&serde_json::json!({
                "model": model,
                "prompt": prompt,
                "stream": false
            }))
            .send()
            .await?
            .json()
            .await?;

        Ok(response["response"]
            .as_str()
            .unwrap_or("")
            .to_string())
    }

    pub async fn embed(&self, text: &str, model: &str) -> Result<Vec<f32>> {
        let response: serde_json::Value = self.client
            .post(&format!("{}/api/embeddings", self.base_url))
            .json(&serde_json::json!({
                "model": model,
                "prompt": text
            }))
            .send()
            .await?
            .json()
            .await?;

        let embedding: Vec<f32> = response["embedding"]
            .as_array()
            .unwrap_or(&vec![])
            .iter()
            .filter_map(|v| v.as_f64().map(|f| f as f32))
            .collect();

        Ok(embedding)
    }
}

/// Conversation context store
pub struct ContextStore {
    // In production, this would be Redis or a database
    contexts: std::sync::Arc<tokio::sync::RwLock<HashMap<String, ConversationContext>>>,
}

impl ContextStore {
    pub fn new() -> Self {
        Self {
            contexts: std::sync::Arc::new(tokio::sync::RwLock::new(HashMap::new())),
        }
    }

    pub async fn get(&self, conversation_id: &str) -> Result<ConversationContext> {
        let contexts = self.contexts.read().await;
        Ok(contexts
            .get(conversation_id)
            .cloned()
            .unwrap_or_else(|| ConversationContext::new("")))
    }

    pub async fn update(
        &self,
        conversation_id: &str,
        query: &str,
        response: &ApolloResponse,
    ) -> Result<()> {
        let mut contexts = self.contexts.write().await;
        let context = contexts
            .entry(conversation_id.to_string())
            .or_insert_with(|| ConversationContext::new(""));

        context.add_turn(query, &response.answer);
        Ok(())
    }
}

/// Conversation context
#[derive(Debug, Clone)]
pub struct ConversationContext {
    pub user_id: String,
    pub turns: Vec<ConversationTurn>,
}

#[derive(Debug, Clone)]
pub struct ConversationTurn {
    pub query: String,
    pub response: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

impl ConversationContext {
    pub fn new(user_id: &str) -> Self {
        Self {
            user_id: user_id.to_string(),
            turns: Vec::new(),
        }
    }

    pub fn add_turn(&mut self, query: &str, response: &str) {
        self.turns.push(ConversationTurn {
            query: query.to_string(),
            response: response.to_string(),
            timestamp: chrono::Utc::now(),
        });
    }

    pub fn summary(&self) -> String {
        if self.turns.is_empty() {
            return "No previous conversation".to_string();
        }

        let recent: Vec<String> = self.turns
            .iter()
            .rev()
            .take(3)
            .map(|turn| format!("Q: {}\nA: {}", turn.query, turn.response))
            .collect();

        recent.join("\n\n")
    }
}
