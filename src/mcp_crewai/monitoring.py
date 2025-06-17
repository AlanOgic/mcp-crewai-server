"""
Real-time monitoring system for MCP CrewAI Server
Provides APIs and utilities for live monitoring of agents, crews, and evolution
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque
import threading
import queue

@dataclass
class MonitoringEvent:
    """Event structure for monitoring"""
    timestamp: str
    event_type: str  # evolution, task, instruction, error, system
    agent_id: Optional[str]
    crew_id: Optional[str] 
    message: str
    details: Dict[str, Any]
    severity: str  # info, warning, error, critical

@dataclass
class AgentStatus:
    """Current status of an agent"""
    agent_id: str
    role: str
    status: str  # working, idle, evolving, error
    current_task: Optional[str]
    task_progress: float  # 0.0 to 1.0
    task_eta: Optional[int]  # seconds
    personality_traits: Dict[str, float]
    evolution_cycles: int
    success_rate: float
    tasks_completed: int
    last_activity: str

@dataclass
class CrewStatus:
    """Current status of a crew"""
    crew_id: str
    crew_name: str
    status: str  # running, idle, completed, error
    agents_count: int
    active_agents: int
    autonomy_level: float
    tasks_queue: int
    last_execution: Optional[str]

@dataclass
class SystemStatus:
    """Overall system status"""
    server_status: str  # healthy, warning, error
    uptime: str
    memory_usage: str
    active_agents: int
    active_crews: int
    total_evolutions: int
    background_tasks: bool
    connections: int

class MonitoringManager:
    """Manages real-time monitoring data"""
    
    def __init__(self, max_events: int = 1000):
        self.events: deque = deque(maxlen=max_events)
        self.agent_statuses: Dict[str, AgentStatus] = {}
        self.crew_statuses: Dict[str, CrewStatus] = {}
        self.system_status: Optional[SystemStatus] = None
        self.start_time = datetime.now()
        
        # Event queue for real-time streaming
        self.event_queue = queue.Queue()
        self.subscribers = set()
        
        # Performance metrics
        self.metrics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'total_evolutions': 0,
            'avg_task_duration': 0,
            'evolution_rate': 0,
            'system_load': 0
        }
    
    def add_event(self, event_type: str, message: str, agent_id: str = None, 
                  crew_id: str = None, details: Dict = None, severity: str = "info"):
        """Add a monitoring event"""
        event = MonitoringEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            agent_id=agent_id,
            crew_id=crew_id,
            message=message,
            details=details or {},
            severity=severity
        )
        
        self.events.append(event)
        self.event_queue.put(event)
        
        # Update metrics based on event
        self._update_metrics(event)
    
    def update_agent_status(self, agent_id: str, **kwargs):
        """Update agent status"""
        if agent_id in self.agent_statuses:
            current = self.agent_statuses[agent_id]
            # Update fields that are provided
            for key, value in kwargs.items():
                if hasattr(current, key):
                    setattr(current, key, value)
        else:
            # Create new status if not exists
            self.agent_statuses[agent_id] = AgentStatus(
                agent_id=agent_id,
                role=kwargs.get('role', 'Unknown'),
                status=kwargs.get('status', 'idle'),
                current_task=kwargs.get('current_task'),
                task_progress=kwargs.get('task_progress', 0.0),
                task_eta=kwargs.get('task_eta'),
                personality_traits=kwargs.get('personality_traits', {}),
                evolution_cycles=kwargs.get('evolution_cycles', 0),
                success_rate=kwargs.get('success_rate', 0.0),
                tasks_completed=kwargs.get('tasks_completed', 0),
                last_activity=datetime.now().isoformat()
            )
    
    def update_crew_status(self, crew_id: str, **kwargs):
        """Update crew status"""
        if crew_id in self.crew_statuses:
            current = self.crew_statuses[crew_id]
            for key, value in kwargs.items():
                if hasattr(current, key):
                    setattr(current, key, value)
        else:
            self.crew_statuses[crew_id] = CrewStatus(
                crew_id=crew_id,
                crew_name=kwargs.get('crew_name', crew_id),
                status=kwargs.get('status', 'idle'),
                agents_count=kwargs.get('agents_count', 0),
                active_agents=kwargs.get('active_agents', 0),
                autonomy_level=kwargs.get('autonomy_level', 0.5),
                tasks_queue=kwargs.get('tasks_queue', 0),
                last_execution=kwargs.get('last_execution')
            )
    
    def update_system_status(self, **kwargs):
        """Update system status"""
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        
        self.system_status = SystemStatus(
            server_status=kwargs.get('server_status', 'healthy'),
            uptime=uptime,
            memory_usage=kwargs.get('memory_usage', '0MB'),
            active_agents=len([a for a in self.agent_statuses.values() if a.status != 'idle']),
            active_crews=len([c for c in self.crew_statuses.values() if c.status == 'running']),
            total_evolutions=self.metrics['total_evolutions'],
            background_tasks=kwargs.get('background_tasks', True),
            connections=kwargs.get('connections', 0)
        )
    
    def get_recent_events(self, count: int = 50, event_type: str = None) -> List[MonitoringEvent]:
        """Get recent events, optionally filtered by type"""
        events = list(self.events)
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-count:]
    
    def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an agent"""
        if agent_id not in self.agent_statuses:
            return None
        
        status = self.agent_statuses[agent_id]
        
        # Get agent's recent events
        agent_events = [e for e in self.events if e.agent_id == agent_id][-10:]
        
        return {
            'status': asdict(status),
            'recent_events': [asdict(e) for e in agent_events],
            'evolution_history': self._get_evolution_history(agent_id),
            'performance_metrics': self._get_agent_metrics(agent_id)
        }
    
    def get_crew_details(self, crew_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a crew"""
        if crew_id not in self.crew_statuses:
            return None
        
        status = self.crew_statuses[crew_id]
        
        # Get crew's agents
        crew_agents = [a for a in self.agent_statuses.values() 
                      if any(e.crew_id == crew_id for e in self.events if e.agent_id == a.agent_id)]
        
        # Get crew's recent events
        crew_events = [e for e in self.events if e.crew_id == crew_id][-10:]
        
        return {
            'status': asdict(status),
            'agents': [asdict(a) for a in crew_agents],
            'recent_events': [asdict(e) for e in crew_events],
            'performance_metrics': self._get_crew_metrics(crew_id)
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data for dashboard display"""
        return {
            'system_status': asdict(self.system_status) if self.system_status else None,
            'agents': [asdict(a) for a in self.agent_statuses.values()],
            'crews': [asdict(c) for c in self.crew_statuses.values()],
            'recent_events': [asdict(e) for e in self.get_recent_events(20)],
            'metrics': self.metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """Get summary of evolution activity"""
        evolution_events = [e for e in self.events if e.event_type == 'evolution']
        
        return {
            'total_evolutions': len(evolution_events),
            'recent_evolutions': [asdict(e) for e in evolution_events[-10:]],
            'evolution_rate': len(evolution_events) / max(1, (datetime.now() - self.start_time).days or 1),
            'agents_evolved': len(set(e.agent_id for e in evolution_events if e.agent_id)),
            'evolution_types': self._count_evolution_types(evolution_events)
        }
    
    def _update_metrics(self, event: MonitoringEvent):
        """Update system metrics based on event"""
        if event.event_type == 'evolution':
            self.metrics['total_evolutions'] += 1
        elif event.event_type == 'task':
            if 'completed' in event.message.lower():
                self.metrics['total_tasks'] += 1
                if 'success' in event.details.get('status', '').lower():
                    self.metrics['successful_tasks'] += 1
    
    def _get_evolution_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get evolution history for an agent"""
        evolution_events = [e for e in self.events 
                          if e.agent_id == agent_id and e.event_type == 'evolution']
        return [asdict(e) for e in evolution_events]
    
    def _get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for an agent"""
        agent_events = [e for e in self.events if e.agent_id == agent_id]
        
        task_events = [e for e in agent_events if e.event_type == 'task']
        successful_tasks = len([e for e in task_events if 'success' in e.details.get('status', '').lower()])
        
        return {
            'total_events': len(agent_events),
            'task_events': len(task_events),
            'success_rate': successful_tasks / max(1, len(task_events)),
            'evolution_count': len([e for e in agent_events if e.event_type == 'evolution']),
            'last_activity': max([e.timestamp for e in agent_events]) if agent_events else None
        }
    
    def _get_crew_metrics(self, crew_id: str) -> Dict[str, Any]:
        """Get performance metrics for a crew"""
        crew_events = [e for e in self.events if e.crew_id == crew_id]
        
        return {
            'total_events': len(crew_events),
            'execution_count': len([e for e in crew_events if 'execution' in e.event_type]),
            'instruction_count': len([e for e in crew_events if e.event_type == 'instruction']),
            'last_activity': max([e.timestamp for e in crew_events]) if crew_events else None
        }
    
    def _count_evolution_types(self, evolution_events: List[MonitoringEvent]) -> Dict[str, int]:
        """Count evolution types from events"""
        types = {}
        for event in evolution_events:
            evo_type = event.details.get('evolution_type', 'unknown')
            types[evo_type] = types.get(evo_type, 0) + 1
        return types


# Global monitoring manager instance
monitoring_manager = MonitoringManager()


def log_event(event_type: str, message: str, agent_id: str = None, 
              crew_id: str = None, details: Dict = None, severity: str = "info"):
    """Convenience function to log monitoring events"""
    monitoring_manager.add_event(event_type, message, agent_id, crew_id, details, severity)


def update_agent(agent_id: str, **kwargs):
    """Convenience function to update agent status"""
    monitoring_manager.update_agent_status(agent_id, **kwargs)


def update_crew(crew_id: str, **kwargs):
    """Convenience function to update crew status"""
    monitoring_manager.update_crew_status(crew_id, **kwargs)


def update_system(**kwargs):
    """Convenience function to update system status"""
    monitoring_manager.update_system_status(**kwargs)