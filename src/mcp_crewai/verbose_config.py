# Verbose Execution Configuration
# This enables maximum verbosity for ALL crew executions

VERBOSE_EXECUTION_CONFIG = {
    "enabled": True,
    "show_agent_creation": True,
    "show_agent_conversations": True,
    "show_task_assignments": True,
    "show_evolution_events": True,
    "show_decision_making": True,
    "show_collaboration": True,
    "show_dynamic_instructions": True,
    "show_performance_metrics": True,
    "show_agent_reflection": True,
    "real_time_monitoring": True,
    "monitoring_interval": 5,  # seconds
    "log_level": "DEBUG",
    "save_execution_logs": True,
    "show_agent_personalities": True,
    "show_workflow_progress": True
}

# Logging configuration for maximum visibility
VERBOSE_LOGGING_CONFIG = {
    "format": "%(asctime)s - 🤖 %(name)s - %(levelname)s - %(message)s",
    "level": "DEBUG",
    "show_agent_ids": True,
    "show_task_details": True,
    "show_evolution_details": True,
    "save_to_file": True,
    "console_output": True
}