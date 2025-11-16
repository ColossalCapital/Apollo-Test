-- Model Management Schema
-- Multi-entity support for local LLM models

-- Model configurations per entity
CREATE TABLE IF NOT EXISTS model_configs (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(255) NOT NULL,
    org_id VARCHAR(255),
    team_id VARCHAR(255),
    
    -- Model settings
    model_name VARCHAR(255) NOT NULL,
    use_case VARCHAR(50) NOT NULL,  -- code_generation, email_analysis, general
    
    -- Model parameters
    max_tokens INTEGER DEFAULT 4000,
    temperature FLOAT DEFAULT 0.2,
    top_p FLOAT DEFAULT 0.95,
    
    -- Quotas (optional)
    max_requests_per_day INTEGER,
    max_tokens_per_day INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Multi-tenant isolation
    UNIQUE(entity_id, org_id, use_case)
);

CREATE INDEX idx_model_configs_entity ON model_configs(entity_id);
CREATE INDEX idx_model_configs_org ON model_configs(org_id);

-- Model downloads tracking
CREATE TABLE IF NOT EXISTS model_downloads (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(255) NOT NULL,
    org_id VARCHAR(255),
    
    -- Model info
    model_name VARCHAR(255) NOT NULL,
    model_size_bytes BIGINT,
    
    -- Download status
    status VARCHAR(50) NOT NULL,  -- queued, downloading, complete, failed
    progress FLOAT DEFAULT 0.0,
    downloaded_bytes BIGINT DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Error tracking
    error_message TEXT
);

CREATE INDEX idx_model_downloads_entity ON model_downloads(entity_id);
CREATE INDEX idx_model_downloads_status ON model_downloads(status);

-- Model usage tracking (summary table, detailed in QuestDB)
CREATE TABLE IF NOT EXISTS model_usage_summary (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(255) NOT NULL,
    org_id VARCHAR(255),
    model_name VARCHAR(255) NOT NULL,
    
    -- Usage stats
    date DATE NOT NULL,
    total_requests INTEGER DEFAULT 0,
    total_tokens BIGINT DEFAULT 0,
    total_response_time_ms BIGINT DEFAULT 0,
    
    -- Cost savings
    estimated_api_cost_usd DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(entity_id, org_id, model_name, date)
);

CREATE INDEX idx_model_usage_entity ON model_usage_summary(entity_id);
CREATE INDEX idx_model_usage_date ON model_usage_summary(date);

-- Available models catalog
CREATE TABLE IF NOT EXISTS available_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    
    -- Model info
    size_gb FLOAT NOT NULL,
    quantization VARCHAR(50),
    description TEXT,
    
    -- Capabilities
    use_cases TEXT[],  -- Array of use cases
    
    -- Requirements
    min_ram_gb INTEGER,
    min_vram_gb INTEGER,
    recommended_gpu VARCHAR(255),
    
    -- Metadata
    added_at TIMESTAMP DEFAULT NOW(),
    is_available BOOLEAN DEFAULT true
);

-- Insert default models
INSERT INTO available_models (model_name, size_gb, quantization, description, use_cases, min_ram_gb) VALUES
('deepseek-coder:33b', 20, 'Q4_K_M', 'DeepSeek Coder 33B - Best for code generation', 
 ARRAY['code_generation', 'code_review', 'documentation'], 24),
('deepseek-coder:6.7b', 4, 'Q4_K_M', 'DeepSeek Coder 6.7B - Faster, smaller model',
 ARRAY['code_completion', 'quick_analysis'], 8),
('llama3:8b', 4.7, 'Q4_0', 'Llama 3 8B - General purpose',
 ARRAY['email_analysis', 'summarization', 'general'], 8),
('mistral:7b', 4.1, 'Q4_0', 'Mistral 7B - Fast and efficient',
 ARRAY['quick_tasks', 'classification'], 8)
ON CONFLICT (model_name) DO NOTHING;
