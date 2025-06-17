#!/usr/bin/env python3
"""
🛡️ Input Validation Schemas for MCP CrewAI Server
Pydantic models for secure input validation
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
import re

class ToolPermission(str, Enum):
    """Tool permission levels"""
    ADMIN = "*"
    CREW_MANAGEMENT = "crew_management"
    AGENT_MANAGEMENT = "agent_management"
    EVOLUTION_CONTROL = "evolution_control"
    MEMORY_ACCESS = "memory_access"
    WEB_ACCESS = "web_access"
    FILE_ACCESS = "file_access"
    READ_ONLY = "read_only"


class AgentRole(str, Enum):
    """Predefined agent roles"""
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    CREATIVE = "creative"
    TECHNICAL = "technical"


class CrewAIRequestBase(BaseModel):
    """Base class for CrewAI requests"""
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"  # Reject unknown fields
    
    @field_validator('*', mode='before')
    @classmethod
    def validate_strings(cls, v):
        if isinstance(v, str):
            # Remove null bytes and excessive whitespace
            v = v.replace('\x00', '').strip()
            if len(v) > 10000:  # Max string length
                raise ValueError("String too long")
        return v


class AgentCreationRequest(CrewAIRequestBase):
    """Validate agent creation parameters"""
    role: str = Field(..., min_length=1, max_length=100)
    goal: str = Field(..., min_length=10, max_length=1000)
    backstory: str = Field(..., min_length=10, max_length=2000)
    tools: Optional[List[str]] = Field(default=[], max_items=20)
    allow_delegation: bool = Field(default=True)
    verbose: bool = Field(default=False)
    max_iter: int = Field(default=5, ge=1, le=20)
    max_execution_time: Optional[int] = Field(default=None, ge=10, le=3600)
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        # Allow alphanumeric, spaces, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError("Role contains invalid characters")
        return v
    
    @field_validator('tools')
    @classmethod
    def validate_tools(cls, v):
        if v:
            for tool in v:
                if not isinstance(tool, str) or len(tool) > 100:
                    raise ValueError("Invalid tool specification")
        return v


class TaskCreationRequest(CrewAIRequestBase):
    """Validate task creation parameters"""
    description: str = Field(..., min_length=20, max_length=5000)
    expected_output: str = Field(..., min_length=10, max_length=2000)
    agent: Optional[str] = Field(default=None, max_length=100)
    tools: Optional[List[str]] = Field(default=[], max_items=10)
    output_file: Optional[str] = Field(default=None, max_length=200)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        # Check for potentially dangerous instructions
        dangerous_patterns = [
            r'execute.*shell',
            r'run.*command',
            r'delete.*file',
            r'access.*system',
            r'install.*package'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v.lower()):
                raise ValueError("Task contains potentially dangerous instructions")
        return v
    
    @field_validator('output_file')
    @classmethod
    def validate_output_file(cls, v):
        if v:
            # Check for safe filename
            if not re.match(r'^[a-zA-Z0-9._-]+\.(txt|json|md|csv)$', v):
                raise ValueError("Invalid output filename")
        return v


class CrewCreationRequest(CrewAIRequestBase):
    """Validate crew creation parameters"""
    agents: List[Dict[str, Any]] = Field(..., min_items=1, max_items=10)
    tasks: List[Dict[str, Any]] = Field(..., min_items=1, max_items=20)
    process: str = Field(default="sequential", pattern="^(sequential|hierarchical)$")
    memory: bool = Field(default=True)
    cache: bool = Field(default=True)
    max_rpm: Optional[int] = Field(default=None, ge=1, le=1000)
    share_crew: bool = Field(default=False)
    
    @field_validator('agents')
    @classmethod
    def validate_agents(cls, v):
        for agent_data in v:
            # Validate each agent using AgentCreationRequest
            AgentCreationRequest(**agent_data)
        return v
    
    @field_validator('tasks')
    @classmethod
    def validate_tasks(cls, v):
        for task_data in v:
            # Validate each task using TaskCreationRequest
            TaskCreationRequest(**task_data)
        return v


class EvolutionRequest(CrewAIRequestBase):
    """Validate evolution parameters"""
    agent_id: str = Field(..., min_length=1, max_length=100)
    evolution_type: str = Field(..., pattern="^(personality|role|skills|autonomous)$")
    parameters: Dict[str, Any] = Field(default={})
    force_evolution: bool = Field(default=False)
    
    @field_validator('parameters')
    @classmethod
    def validate_parameters(cls, v):
        # Limit parameter complexity
        if len(str(v)) > 5000:
            raise ValueError("Evolution parameters too complex")
        return v


class WebSearchRequest(CrewAIRequestBase):
    """Validate web search parameters"""
    query: str = Field(..., min_length=3, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)
    search_type: str = Field(default="web", pattern="^(web|research|fact_check)$")
    agent_id: Optional[str] = Field(default=None, max_length=100)
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        # Remove potentially harmful query components
        if any(word in v.lower() for word in ['hack', 'exploit', 'bypass', 'crack']):
            raise ValueError("Search query contains inappropriate terms")
        return v


class FileOperationRequest(CrewAIRequestBase):
    """Validate file operation parameters"""
    operation: str = Field(..., pattern="^(read|write|create|list)$")
    file_path: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = Field(default=None, max_length=100000)
    encoding: str = Field(default="utf-8", pattern="^(utf-8|ascii)$")
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v):
        # Prevent path traversal
        if '..' in v or v.startswith('/') or '\\' in v:
            raise ValueError("Invalid file path")
        
        # Only allow safe characters
        if not re.match(r'^[a-zA-Z0-9._/-]+$', v):
            raise ValueError("File path contains unsafe characters")
        
        # Check extension
        allowed_extensions = {'.txt', '.json', '.md', '.csv', '.log'}
        if '.' in v and not any(v.endswith(ext) for ext in allowed_extensions):
            raise ValueError("File extension not allowed")
        
        return v
    
    @model_validator(mode='after')
    def validate_operation_content(self):
        if self.operation in ('write', 'create') and not self.content:
            raise ValueError("Content required for write operations")
        
        return self


class ConfigurationRequest(CrewAIRequestBase):
    """Validate configuration updates"""
    settings: Dict[str, Any] = Field(..., max_items=50)
    
    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v):
        # Define allowed configuration keys
        allowed_keys = {
            'log_level', 'max_agents', 'max_tasks', 'evolution_enabled',
            'memory_enabled', 'cache_enabled', 'monitoring_enabled',
            'rate_limit', 'max_execution_time'
        }
        
        for key, value in v.items():
            if key not in allowed_keys:
                raise ValueError(f"Configuration key '{key}' not allowed")
            
            # Validate specific settings
            if key == 'log_level' and value not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                raise ValueError("Invalid log level")
            
            if key in ['max_agents', 'max_tasks', 'rate_limit'] and not isinstance(value, int):
                raise ValueError(f"{key} must be integer")
            
            if key in ['evolution_enabled', 'memory_enabled', 'cache_enabled'] and not isinstance(value, bool):
                raise ValueError(f"{key} must be boolean")
        
        return v


class MemoryOperationRequest(CrewAIRequestBase):
    """Validate memory operations"""
    operation: str = Field(..., pattern="^(store|retrieve|update|delete|search)$")
    agent_id: str = Field(..., min_length=1, max_length=100)
    memory_type: str = Field(default="experience", pattern="^(experience|pattern|strategy|failure)$")
    data: Optional[Dict[str, Any]] = Field(default=None)
    query: Optional[str] = Field(default=None, max_length=500)
    
    @model_validator(mode='after')
    def validate_operation_params(self):
        if self.operation in ('store', 'update') and not self.data:
            raise ValueError("Data required for store/update operations")
        
        if self.operation == 'search' and not self.query:
            raise ValueError("Query required for search operations")
        
        return self


class ToolExecutionRequest(CrewAIRequestBase):
    """Validate tool execution requests"""
    tool_name: str = Field(..., min_length=1, max_length=100)
    arguments: Dict[str, Any] = Field(default={}, max_items=20)
    client_id: Optional[str] = Field(default=None, max_length=100)
    
    @field_validator('tool_name')
    @classmethod
    def validate_tool_name(cls, v):
        # Only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Invalid tool name format")
        return v
    
    @field_validator('arguments')
    @classmethod
    def validate_arguments(cls, v):
        # Limit argument complexity and size
        total_size = len(str(v))
        if total_size > 10000:
            raise ValueError("Arguments too large")
        
        # Check for nested complexity
        def check_depth(obj, depth=0):
            if depth > 5:
                raise ValueError("Arguments too deeply nested")
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1)
        
        check_depth(v)
        return v


class SecurityAuditRequest(CrewAIRequestBase):
    """Validate security audit requests"""
    audit_type: str = Field(..., pattern="^(access|performance|security|full)$")
    include_sensitive: bool = Field(default=False)
    time_range_hours: int = Field(default=24, ge=1, le=168)  # Max 1 week


def validate_request_data(request_type: str, data: Dict[str, Any]) -> BaseModel:
    """Factory function to validate request data based on type"""
    
    validation_map = {
        'agent_creation': AgentCreationRequest,
        'task_creation': TaskCreationRequest,
        'crew_creation': CrewCreationRequest,
        'evolution': EvolutionRequest,
        'web_search': WebSearchRequest,
        'file_operation': FileOperationRequest,
        'configuration': ConfigurationRequest,
        'memory_operation': MemoryOperationRequest,
        'tool_execution': ToolExecutionRequest,
        'security_audit': SecurityAuditRequest
    }
    
    if request_type not in validation_map:
        raise ValueError(f"Unknown request type: {request_type}")
    
    validator_class = validation_map[request_type]
    return validator_class(**data)


class ValidationErrorDetail(BaseModel):
    """Detailed validation error information"""
    field: str
    message: str
    input_value: Any
    error_type: str


def format_validation_error(error: Exception) -> Dict[str, Any]:
    """Format validation errors for client response"""
    if hasattr(error, 'errors'):
        # Pydantic validation error
        details = []
        for err in error.errors():
            details.append(ValidationErrorDetail(
                field='.'.join(str(x) for x in err['loc']),
                message=err['msg'],
                input_value=err.get('input', 'N/A'),
                error_type=err['type']
            ))
        
        return {
            'error_type': 'validation_error',
            'message': 'Input validation failed',
            'details': [detail.dict() for detail in details]
        }
    else:
        # Generic error
        return {
            'error_type': 'validation_error',
            'message': str(error),
            'details': []
        }