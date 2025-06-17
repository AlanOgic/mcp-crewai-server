"""
Task Termination System - Replace timeouts with intelligent task completion
"""

import asyncio
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TaskTerminator:
    """
    Intelligent task termination system that replaces hard timeouts.
    Instead of killing tasks, it signals completion and passes partial results.
    """
    
    def __init__(self):
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.termination_callbacks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
    
    def register_task(self, task_id: str, task_context: Dict[str, Any], 
                     completion_callback: Optional[Callable] = None):
        """Register a task for potential termination"""
        with self._lock:
            self.active_tasks[task_id] = {
                'context': task_context,
                'start_time': time.time(),
                'partial_results': [],
                'current_step': 'initialization',
                'progress': 0.0,
                'can_terminate': False,
                'termination_requested': False
            }
            
            if completion_callback:
                self.termination_callbacks[task_id] = completion_callback
        
        logger.info(f"🔧 Task registered for termination management: {task_id}")
    
    def update_task_progress(self, task_id: str, step: str, progress: float, 
                           partial_result: Any = None, can_terminate: bool = True):
        """Update task progress and mark if it can be safely terminated"""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task['current_step'] = step
                task['progress'] = progress
                task['can_terminate'] = can_terminate
                
                if partial_result is not None:
                    task['partial_results'].append({
                        'step': step,
                        'result': partial_result,
                        'timestamp': datetime.now().isoformat()
                    })
        
        logger.debug(f"📊 Task {task_id} progress: {progress:.1%} - Step: {step}")
    
    def request_termination(self, task_id: str, reason: str = "User requested termination"):
        """Request graceful termination of a task"""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task['termination_requested'] = True
                task['termination_reason'] = reason
                
                logger.info(f"🛑 Termination requested for task {task_id}: {reason}")
                
                # If task can be terminated safely, trigger callback
                if task['can_terminate'] and task_id in self.termination_callbacks:
                    callback = self.termination_callbacks[task_id]
                    threading.Thread(target=self._execute_termination_callback, 
                                   args=(callback, task_id)).start()
                
                return True
        return False
    
    def _execute_termination_callback(self, callback: Callable, task_id: str):
        """Execute termination callback safely"""
        try:
            partial_results = self.get_partial_results(task_id)
            callback(task_id, partial_results)
        except Exception as e:
            logger.error(f"❌ Error in termination callback for {task_id}: {e}")
    
    def should_terminate(self, task_id: str) -> bool:
        """Check if task should terminate gracefully"""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return task['termination_requested'] and task['can_terminate']
        return False
    
    def get_partial_results(self, task_id: str) -> Dict[str, Any]:
        """Get partial results from a task"""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return {
                    'task_id': task_id,
                    'progress': task['progress'],
                    'current_step': task['current_step'],
                    'partial_results': task['partial_results'],
                    'execution_time': time.time() - task['start_time'],
                    'termination_reason': task.get('termination_reason', 'Completed normally')
                }
        return {}
    
    def complete_task(self, task_id: str, final_result: Any = None):
        """Mark task as completed and clean up"""
        with self._lock:
            if task_id in self.active_tasks:
                if final_result is not None:
                    self.active_tasks[task_id]['partial_results'].append({
                        'step': 'final_result',
                        'result': final_result,
                        'timestamp': datetime.now().isoformat()
                    })
                
                del self.active_tasks[task_id]
                
                if task_id in self.termination_callbacks:
                    del self.termination_callbacks[task_id]
        
        logger.info(f"✅ Task completed and cleaned up: {task_id}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a task"""
        with self._lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return {
                    'task_id': task_id,
                    'current_step': task['current_step'],
                    'progress': task['progress'],
                    'can_terminate': task['can_terminate'],
                    'termination_requested': task['termination_requested'],
                    'execution_time': time.time() - task['start_time'],
                    'partial_results_count': len(task['partial_results'])
                }
        return None
    
    def list_active_tasks(self) -> List[Dict[str, Any]]:
        """List all active tasks"""
        with self._lock:
            return [self.get_task_status(task_id) for task_id in self.active_tasks.keys()]


# Global task terminator instance
task_terminator = TaskTerminator()


class TerminableTask:
    """Context manager for tasks that can be terminated gracefully"""
    
    def __init__(self, task_id: str, context: Dict[str, Any], 
                 completion_callback: Optional[Callable] = None):
        self.task_id = task_id
        self.context = context
        self.completion_callback = completion_callback
    
    def __enter__(self):
        task_terminator.register_task(self.task_id, self.context, self.completion_callback)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        task_terminator.complete_task(self.task_id)
    
    def update_progress(self, step: str, progress: float, partial_result: Any = None, 
                       can_terminate: bool = True):
        """Update task progress"""
        task_terminator.update_task_progress(self.task_id, step, progress, 
                                           partial_result, can_terminate)
    
    def should_terminate(self) -> bool:
        """Check if task should terminate"""
        return task_terminator.should_terminate(self.task_id)
    
    def get_partial_results(self) -> Dict[str, Any]:
        """Get current partial results"""
        return task_terminator.get_partial_results(self.task_id)


def terminate_current_task(task_id: str, reason: str = "User requested termination") -> bool:
    """Terminate a currently running task and pass partial results to next step"""
    return task_terminator.request_termination(task_id, reason)


def get_active_tasks() -> List[Dict[str, Any]]:
    """Get list of all active tasks"""
    return task_terminator.list_active_tasks()


# Decorator for making functions terminable
def terminable_task(task_id: str = None):
    """Decorator to make a function terminable"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            actual_task_id = task_id or f"{func.__name__}_{int(time.time())}"
            
            with TerminableTask(actual_task_id, {'function': func.__name__}) as task:
                task.update_progress("starting", 0.0, can_terminate=False)
                
                try:
                    result = func(*args, **kwargs, _task=task)
                    task.update_progress("completed", 1.0, result)
                    return result
                except Exception as e:
                    task.update_progress("error", 0.0, str(e))
                    raise
        
        return wrapper
    return decorator