// Apollo AI Service
// Central AI orchestrator for the ColossalCapital ecosystem

mod orchestrator;

use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_cors::Cors;
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use orchestrator::ApolloOrchestrator;

/// API request for Apollo query
#[derive(Debug, Deserialize)]
struct QueryRequest {
    question: String,
    user_id: String,
    conversation_id: Option<String>,
    context: Option<String>,
}

/// API response
#[derive(Debug, Serialize)]
struct QueryResponse {
    answer: String,
    sources: Vec<orchestrator::Source>,
    confidence: f32,
    follow_up_questions: Vec<String>,
}

/// Health check endpoint
async fn health() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy",
        "service": "apollo-ai",
        "version": "1.0.0"
    }))
}

/// Main query endpoint
async fn query(
    orchestrator: web::Data<Arc<ApolloOrchestrator>>,
    req: web::Json<QueryRequest>,
) -> impl Responder {
    match orchestrator.handle_query(
        &req.question,
        &req.user_id,
        req.conversation_id.as_deref(),
    ).await {
        Ok(response) => HttpResponse::Ok().json(QueryResponse {
            answer: response.answer,
            sources: response.sources,
            confidence: response.confidence,
            follow_up_questions: response.follow_up_questions,
        }),
        Err(e) => HttpResponse::InternalServerError().json(serde_json::json!({
            "error": format!("Query failed: {}", e)
        })),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    // Configuration from environment
    let hermes_url = std::env::var("HERMES_URL")
        .unwrap_or_else(|_| "http://hermes-api:8080".to_string());
    let ollama_url = std::env::var("OLLAMA_URL")
        .unwrap_or_else(|_| "http://ollama:11434".to_string());
    let port = std::env::var("PORT")
        .unwrap_or_else(|_| "8090".to_string())
        .parse::<u16>()
        .unwrap_or(8090);

    log::info!("Starting Apollo AI service");
    log::info!("Hermes URL: {}", hermes_url);
    log::info!("Ollama URL: {}", ollama_url);
    log::info!("Port: {}", port);

    // Initialize orchestrator
    let orchestrator = Arc::new(
        ApolloOrchestrator::new(&hermes_url, &ollama_url)
            .expect("Failed to initialize Apollo orchestrator")
    );

    log::info!("Apollo AI ready to serve requests");

    // Start HTTP server
    HttpServer::new(move || {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header();

        App::new()
            .wrap(cors)
            .app_data(web::Data::new(orchestrator.clone()))
            .route("/health", web::get().to(health))
            .route("/api/query", web::post().to(query))
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
