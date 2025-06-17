"""
Configuration management for MCP CrewAI Server
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class MCPServerConfig(BaseSettings):
    """Configuration for MCP CrewAI Server with environment variables support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ===============================================
    # 🤖 AI MODEL API KEYS
    # ===============================================
    
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    crewai_api_key: Optional[str] = Field(default=None, description="CrewAI API key")
    
    # ===============================================
    # 🚀 MCP SERVER CONFIGURATION
    # ===============================================
    
    default_llm_provider: str = Field(default="openai", description="Default LLM provider")
    default_model: str = Field(default="gpt-4-turbo-preview", description="Default model")
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=8765, description="MCP server port")
    
    # ===============================================
    # 🔧 ADVANCED CONFIGURATION
    # ===============================================
    
    evolution_enabled: bool = Field(default=True, description="Enable agent evolution")
    evolution_frequency_hours: int = Field(default=24, description="Evolution check frequency")
    auto_evolution_threshold: float = Field(default=0.6, description="Auto evolution threshold")
    
    dynamic_instructions_enabled: bool = Field(default=True, description="Enable dynamic instructions")
    max_pending_instructions: int = Field(default=50, description="Max pending instructions")
    
    memory_enabled: bool = Field(default=True, description="Enable persistent memory")
    
    # ===============================================
    # 👁️ VERBOSE EXECUTION SETTINGS
    # ===============================================
    
    verbose_execution: bool = Field(default=True, description="Enable maximum verbose execution - ALWAYS SHOW CREW WORKING")
    show_agent_details: bool = Field(default=True, description="Show detailed agent information - ALWAYS ON")
    show_agent_conversations: bool = Field(default=True, description="Show agent conversations - ALWAYS ON")
    show_evolution_events: bool = Field(default=True, description="Show evolution events in real-time")
    show_task_assignments: bool = Field(default=True, description="Show task distribution details")
    show_decision_making: bool = Field(default=True, description="Show agent decision processes")
    real_time_monitoring: bool = Field(default=True, description="Enable real-time crew monitoring")
    monitoring_interval: int = Field(default=5, description="Monitoring update interval in seconds")
    save_execution_logs: bool = Field(default=True, description="Save detailed execution logs")
    execution_log_level: str = Field(default="DEBUG", description="Execution logging level")
    memory_database_path: str = Field(default=None, description="Memory database path")
    
    log_level: str = Field(default="INFO", description="Logging level")
    
    background_tasks_enabled: bool = Field(default=True, description="Enable background tasks")
    evolution_check_interval: int = Field(default=3600, description="Evolution check interval in seconds")
    
    # ===============================================
    # 🌐 EXTERNAL MCP SERVERS
    # ===============================================
    
    filesystem_mcp_enabled: bool = Field(default=False, description="Enable filesystem MCP")
    filesystem_mcp_root_path: str = Field(default="/tmp", description="Filesystem MCP root path")
    
    web_mcp_enabled: bool = Field(default=False, description="Enable web MCP")
    web_mcp_allowed_domains: str = Field(default="", description="Web MCP allowed domains")
    
    database_mcp_enabled: bool = Field(default=False, description="Enable database MCP")
    database_mcp_connection_string: str = Field(default="", description="Database MCP connection string")
    
    # ===============================================
    # 🔒 SECURITY CONFIGURATION  
    # ===============================================
    
    agent_sandboxing: bool = Field(default=True, description="Enable agent sandboxing")
    max_agent_execution_time: int = Field(default=0, description="Max agent execution time in seconds (0 = no timeout, use task termination instead)")
    max_agent_memory_mb: int = Field(default=512, description="Max agent memory in MB")
    validate_instructions: bool = Field(default=True, description="Enable instruction validation")
    
    # Rate limiting
    enable_rate_limiting: bool = Field(default=True, description="Enable API rate limiting")
    rate_limit_per_hour: int = Field(default=100, description="Requests per hour per client")
    burst_limit_per_minute: int = Field(default=10, description="Burst requests per minute")
    
    # Authentication
    require_authentication: bool = Field(default=True, description="Require API key authentication")
    jwt_secret_key: Optional[str] = Field(default=None, description="JWT secret key")
    api_key_expiration_hours: int = Field(default=24, description="API key session expiration")
    
    # File security
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    allowed_file_extensions: str = Field(default=".txt,.json,.md,.csv,.log", description="Allowed file extensions")
    secure_file_operations: bool = Field(default=True, description="Enable secure file operations")
    
    # ===============================================
    # 📊 MONITORING & ANALYTICS
    # ===============================================
    
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    analytics_enabled: bool = Field(default=False, description="Enable analytics")
    metrics_export_path: str = Field(default=None, description="Metrics export path")
    health_check_interval: int = Field(default=60, description="Health check interval in seconds")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_data_directory()
        self._validate_configuration()
    
    def get_data_directory(self) -> Path:
        """Get the data directory path"""
        # Use a writable directory in the project root or user home
        import os
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        
        # If project data dir doesn't exist or isn't writable, use temp dir
        try:
            data_dir.mkdir(exist_ok=True)
            return data_dir
        except (OSError, PermissionError):
            import tempfile
            data_dir = Path(tempfile.gettempdir()) / "mcp_crewai_data"
            data_dir.mkdir(exist_ok=True)
            return data_dir

    def _ensure_data_directory(self):
        """Ensure data directory exists and set paths"""
        data_dir = self.get_data_directory()
        
        # Set paths to use proper data directory
        self.memory_database_path = str(data_dir / "agent_memory.db")
        self.metrics_export_path = str(data_dir / "metrics.json")
    
    def _validate_configuration(self):
        """Validate configuration settings"""
        # Validate API keys if LLM provider is configured
        if self.default_llm_provider == "openai" and not self.openai_api_key:
            print("⚠️  Warning: OpenAI provider selected but no API key provided")
        
        if self.default_llm_provider == "anthropic" and not self.anthropic_api_key:
            print("⚠️  Warning: Anthropic provider selected but no API key provided")
        
        # Validate paths
        memory_dir = Path(self.memory_database_path).parent
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        if self.metrics_export_path:
            metrics_dir = Path(self.metrics_export_path).parent
            metrics_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def web_allowed_domains_list(self) -> List[str]:
        """Get web allowed domains as a list"""
        if not self.web_mcp_allowed_domains:
            return []
        return [domain.strip() for domain in self.web_mcp_allowed_domains.split(",")]
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration for agents"""
        config = {
            "provider": self.default_llm_provider,
            "model": self.default_model
        }
        
        if self.default_llm_provider == "openai" and self.openai_api_key:
            config["api_key"] = self.openai_api_key
        elif self.default_llm_provider == "anthropic" and self.anthropic_api_key:
            config["api_key"] = self.anthropic_api_key
        
        return config
    
    def get_mcp_servers_config(self) -> List[dict]:
        """Get configuration for external MCP servers"""
        servers = []
        
        if self.filesystem_mcp_enabled:
            servers.append({
                "name": "filesystem",
                "command": ["mcp-filesystem", self.filesystem_mcp_root_path],
                "description": "File system operations",
                "capabilities": ["read", "write", "search"]
            })
        
        if self.web_mcp_enabled:
            servers.append({
                "name": "web",
                "command": ["mcp-web"],
                "description": "Web scraping and HTTP operations",
                "capabilities": ["fetch", "search", "parse"],
                "allowed_domains": self.web_allowed_domains_list
            })
        
        if self.database_mcp_enabled and self.database_mcp_connection_string:
            servers.append({
                "name": "database",
                "command": ["mcp-database", self.database_mcp_connection_string],
                "description": "Database operations and queries",
                "capabilities": ["query", "insert", "analyze"]
            })
        
        return servers
    
    def is_production_ready(self) -> tuple[bool, List[str]]:
        """Check if configuration is production ready"""
        issues = []
        
        # Check for required API keys
        if not self.openai_api_key and not self.anthropic_api_key:
            issues.append("No LLM API keys configured")
        
        # Check security settings
        if not self.agent_sandboxing:
            issues.append("Agent sandboxing is disabled (security risk)")
        
        if not self.validate_instructions:
            issues.append("Instruction validation is disabled (security risk)")
            
        if not self.require_authentication:
            issues.append("Authentication is disabled (critical security risk)")
            
        if not self.enable_rate_limiting:
            issues.append("Rate limiting is disabled (security risk)")
            
        if not self.secure_file_operations:
            issues.append("Secure file operations disabled (security risk)")
        
        # Check monitoring
        if not self.monitoring_enabled:
            issues.append("Monitoring is disabled (observability risk)")
        
        # Check paths exist
        if not Path(self.memory_database_path).parent.exists():
            issues.append("Memory database directory does not exist")
        
        return len(issues) == 0, issues
    
    def get_summary(self) -> dict:
        """Get configuration summary"""
        is_ready, issues = self.is_production_ready()
        
        return {
            "server": {
                "host": self.mcp_server_host,
                "port": self.mcp_server_port,
                "production_ready": is_ready
            },
            "llm": {
                "provider": self.default_llm_provider,
                "model": self.default_model,
                "api_key_configured": bool(
                    (self.default_llm_provider == "openai" and self.openai_api_key) or
                    (self.default_llm_provider == "anthropic" and self.anthropic_api_key)
                )
            },
            "features": {
                "evolution": self.evolution_enabled,
                "dynamic_instructions": self.dynamic_instructions_enabled,
                "memory": self.memory_enabled,
                "background_tasks": self.background_tasks_enabled
            },
            "security": {
                "sandboxing": self.agent_sandboxing,
                "instruction_validation": self.validate_instructions,
                "max_execution_time": self.max_agent_execution_time
            },
            "external_mcp_servers": len(self.get_mcp_servers_config()),
            "issues": issues if not is_ready else []
        }


# Global configuration instance
config = MCPServerConfig()


def get_config() -> MCPServerConfig:
    """Get the global configuration instance"""
    return config


def reload_config() -> MCPServerConfig:
    """Reload configuration from environment"""
    global config
    config = MCPServerConfig()
    return config