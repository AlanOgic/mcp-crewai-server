-- MCP CrewAI Server Database Initialization
-- PostgreSQL setup script

-- Create database if not exists (handled by Docker environment)
-- CREATE DATABASE IF NOT EXISTS crewai_db;

-- Switch to the database
\c crewai_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS mcp_crewai;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default schema
SET search_path TO mcp_crewai, public;

-- ===============================================
-- Agent Evolution Tables
-- ===============================================

-- Agent persistent memory
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL UNIQUE,
    memory_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent evolution history
CREATE TABLE IF NOT EXISTS agent_evolution_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    evolution_cycle INTEGER NOT NULL,
    previous_traits JSONB NOT NULL,
    new_traits JSONB NOT NULL,
    evolution_type VARCHAR(100) NOT NULL,
    evolution_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (agent_id) REFERENCES agent_memory(agent_id) ON DELETE CASCADE
);

-- Crew management
CREATE TABLE IF NOT EXISTS crews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crew_id VARCHAR(255) NOT NULL UNIQUE,
    crew_name VARCHAR(255) NOT NULL,
    configuration JSONB NOT NULL,
    autonomy_level DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crew execution history
CREATE TABLE IF NOT EXISTS crew_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crew_id VARCHAR(255) NOT NULL,
    execution_id VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    context_data JSONB,
    result_data JSONB,
    evolution_events JSONB DEFAULT '[]',
    
    FOREIGN KEY (crew_id) REFERENCES crews(crew_id) ON DELETE CASCADE
);

-- ===============================================
-- Dynamic Instructions Tables
-- ===============================================

-- Dynamic instructions
CREATE TABLE IF NOT EXISTS dynamic_instructions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instruction_id VARCHAR(255) NOT NULL UNIQUE,
    crew_id VARCHAR(255) NOT NULL,
    instruction_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 3,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (crew_id) REFERENCES crews(crew_id) ON DELETE CASCADE
);

-- ===============================================
-- MCP Integration Tables
-- ===============================================

-- MCP server connections
CREATE TABLE IF NOT EXISTS mcp_server_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    server_name VARCHAR(255) NOT NULL,
    server_config JSONB NOT NULL,
    connection_status VARCHAR(50) NOT NULL DEFAULT 'disconnected',
    last_connected TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(agent_id, server_name),
    FOREIGN KEY (agent_id) REFERENCES agent_memory(agent_id) ON DELETE CASCADE
);

-- Tool usage tracking
CREATE TABLE IF NOT EXISTS tool_usage_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    server_name VARCHAR(255) NOT NULL,
    usage_context TEXT,
    success BOOLEAN NOT NULL,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (agent_id) REFERENCES agent_memory(agent_id) ON DELETE CASCADE
);

-- ===============================================
-- Monitoring Schema
-- ===============================================

-- Server metrics
CREATE TABLE IF NOT EXISTS monitoring.server_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_labels JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System health logs
CREATE TABLE IF NOT EXISTS monitoring.health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    details JSONB,
    response_time_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================================
-- Audit Schema
-- ===============================================

-- API access logs
CREATE TABLE IF NOT EXISTS audit.api_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_ip INET NOT NULL,
    user_agent TEXT,
    api_key_hash VARCHAR(255),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    request_size INTEGER,
    response_size INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Configuration changes
CREATE TABLE IF NOT EXISTS audit.config_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component VARCHAR(255) NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    old_config JSONB,
    new_config JSONB NOT NULL,
    changed_by VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================================
-- Indexes for Performance
-- ===============================================

-- Agent memory indexes
CREATE INDEX IF NOT EXISTS idx_agent_memory_agent_id ON agent_memory(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_memory_updated_at ON agent_memory(updated_at);

-- Evolution history indexes
CREATE INDEX IF NOT EXISTS idx_evolution_history_agent_id ON agent_evolution_history(agent_id);
CREATE INDEX IF NOT EXISTS idx_evolution_history_created_at ON agent_evolution_history(created_at);

-- Crew indexes
CREATE INDEX IF NOT EXISTS idx_crews_crew_id ON crews(crew_id);
CREATE INDEX IF NOT EXISTS idx_crews_created_at ON crews(created_at);

-- Dynamic instructions indexes
CREATE INDEX IF NOT EXISTS idx_dynamic_instructions_crew_id ON dynamic_instructions(crew_id);
CREATE INDEX IF NOT EXISTS idx_dynamic_instructions_status ON dynamic_instructions(status);
CREATE INDEX IF NOT EXISTS idx_dynamic_instructions_priority ON dynamic_instructions(priority);

-- Tool usage indexes
CREATE INDEX IF NOT EXISTS idx_tool_usage_agent_id ON tool_usage_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_tool_usage_created_at ON tool_usage_log(created_at);
CREATE INDEX IF NOT EXISTS idx_tool_usage_success ON tool_usage_log(success);

-- Monitoring indexes
CREATE INDEX IF NOT EXISTS idx_server_metrics_name_timestamp ON monitoring.server_metrics(metric_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_health_checks_component_timestamp ON monitoring.health_checks(component, timestamp);

-- Audit indexes
CREATE INDEX IF NOT EXISTS idx_api_access_timestamp ON audit.api_access_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_access_client_ip ON audit.api_access_log(client_ip);

-- ===============================================
-- Functions and Triggers
-- ===============================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_agent_memory_updated_at 
    BEFORE UPDATE ON agent_memory 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crews_updated_at 
    BEFORE UPDATE ON crews 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===============================================
-- Initial Data
-- ===============================================

-- Insert default configuration
INSERT INTO monitoring.server_metrics (metric_name, metric_value, metric_labels) 
VALUES ('server_initialized', 1, '{"version": "1.0.0", "environment": "production"}')
ON CONFLICT DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mcp_crewai TO crewai;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO crewai;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO crewai;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA mcp_crewai TO crewai;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA monitoring TO crewai;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA audit TO crewai;

-- Create read-only user for monitoring
CREATE USER monitoring_user WITH PASSWORD 'monitoring_readonly_pass';
GRANT CONNECT ON DATABASE crewai_db TO monitoring_user;
GRANT USAGE ON SCHEMA monitoring TO monitoring_user;
GRANT SELECT ON ALL TABLES IN SCHEMA monitoring TO monitoring_user;

COMMIT;