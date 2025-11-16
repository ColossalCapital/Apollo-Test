// Apollo API - REST endpoints for Atlas integration

use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
    Router,
    routing::{get, post},
};
use std::sync::Arc;

use crate::router::{ApolloRouter, QueryRequest, ApolloResponse, AgentType};

pub struct ApiState {
    router: Arc<ApolloRouter>,
}

/// POST /apollo/query - Execute a query
pub async fn query(
    State(state): State<Arc<ApiState>>,
    Json(request): Json<QueryRequest>,
) -> Result<impl IntoResponse, StatusCode> {
    let response = state.router
        .route_query(request)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(response))
}

/// GET /apollo/agents - List all 42 agents
pub async fn list_agents() -> Result<impl IntoResponse, StatusCode> {
    let agents = vec![
        // Development (2)
        agent_info(AgentType::CodeAssistant, "Software development assistance"),
        agent_info(AgentType::CodeEditor, "Embedded code editing with AI (Akashic)"),
        
        // Communication (2)
        agent_info(AgentType::EmailAgent, "Email processing and analysis"),
        agent_info(AgentType::CalendarAgent, "Calendar and scheduling"),
        
        // Documents & Knowledge (3)
        agent_info(AgentType::DocumentParser, "Document extraction and parsing"),
        agent_info(AgentType::KnowledgeAgent, "Semantic search and knowledge retrieval"),
        agent_info(AgentType::Sage, "Research and learning assistant"),
        
        // Analysis (2)
        agent_info(AgentType::TextAnalyzer, "NLP and text analysis"),
        agent_info(AgentType::Quant, "Data analysis and SQL queries"),
        
        // Media (4)
        agent_info(AgentType::VisionAgent, "Image understanding and analysis"),
        agent_info(AgentType::AudioAgent, "Speech-to-text and audio processing"),
        agent_info(AgentType::Reel, "Video intelligence and analysis"),
        agent_info(AgentType::Harmonia, "Music intelligence and analysis"),
        
        // Finance (2)
        agent_info(AgentType::LedgerAgent, "Financial analysis and bookkeeping"),
        agent_info(AgentType::Deduct, "Tax preparation and optimization"),
        
        // Legal (2)
        agent_info(AgentType::Juris, "Legal document analysis"),
        agent_info(AgentType::Accord, "Contract analysis and review"),
        
        // Business (4)
        agent_info(AgentType::Closer, "Sales and CRM assistance"),
        agent_info(AgentType::Amplify, "Marketing and growth"),
        agent_info(AgentType::Talent, "HR and recruitment"),
        agent_info(AgentType::GrantAgent, "Grant discovery and applications"),
        
        // Insurance & Compliance (2)
        agent_info(AgentType::Shield, "Insurance analysis and recommendations"),
        agent_info(AgentType::Sentinel, "Regulatory compliance monitoring"),
        
        // Web & Translation (2)
        agent_info(AgentType::WebScraper, "Web content extraction"),
        agent_info(AgentType::Polyglot, "Language translation"),
        
        // Modern Communication (2)
        agent_info(AgentType::Lexicon, "Slang and modern language understanding"),
        agent_info(AgentType::CulturePulse, "Meme culture and trends"),
        
        // Infrastructure (2)
        agent_info(AgentType::SchemaAgent, "Data structuring and schemas"),
        agent_info(AgentType::RouterAgent, "Content routing and classification"),
        
        // Trading & Finance (6)
        agent_info(AgentType::TradingAgent, "Trading execution (Delt integration)"),
        agent_info(AgentType::PortfolioAnalyzer, "Portfolio analysis and optimization"),
        agent_info(AgentType::RiskManager, "Risk assessment and management"),
        agent_info(AgentType::MarketAnalyzer, "Market analysis and insights"),
        agent_info(AgentType::StrategyGenerator, "Trading strategy generation"),
        agent_info(AgentType::ExecutionAgent, "Trade execution and monitoring"),
        
        // Health & Wellness (6)
        agent_info(AgentType::HealthAgent, "Health tracking and analysis"),
        agent_info(AgentType::TravelAgent, "Travel planning and booking"),
        agent_info(AgentType::FitnessAgent, "Fitness tracking and coaching"),
        agent_info(AgentType::NutritionAgent, "Nutrition analysis and meal planning"),
        agent_info(AgentType::SleepAgent, "Sleep tracking and optimization"),
        agent_info(AgentType::MentalHealthAgent, "Mental wellness and mindfulness"),
    ];

    Ok(Json(serde_json::json!({
        "total_agents": agents.len(),
        "agents": agents
    })))
}

fn agent_info(agent_type: AgentType, description: &str) -> serde_json::Value {
    serde_json::json!({
        "type": agent_type,
        "description": description
    })
}

/// GET /apollo/health - Health check
pub async fn health() -> Result<impl IntoResponse, StatusCode> {
    Ok(Json(serde_json::json!({
        "status": "healthy",
        "service": "Apollo AI Router",
        "version": "1.0.0",
        "agents": 42
    })))
}

/// Create Apollo API router
pub fn create_router() -> Router {
    let state = Arc::new(ApiState {
        router: Arc::new(ApolloRouter::new()),
    });

    Router::new()
        .route("/query", post(query))
        .route("/agents", get(list_agents))
        .route("/health", get(health))
        .with_state(state)
}
