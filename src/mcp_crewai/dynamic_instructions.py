"""
Dynamic Instructions System - Allow user input during crew execution
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import threading
import queue

logger = logging.getLogger(__name__)


class InstructionType(Enum):
    """Types of dynamic instructions"""
    GUIDANCE = "guidance"           # General guidance/direction
    CONSTRAINT = "constraint"       # Add constraints/limitations  
    RESOURCE = "resource"          # Provide additional resources
    PIVOT = "pivot"                # Change direction/strategy
    FEEDBACK = "feedback"          # Feedback on current progress
    EMERGENCY_STOP = "emergency_stop"  # Stop execution
    SKILL_BOOST = "skill_boost"    # Temporarily boost specific skills


@dataclass
class DynamicInstruction:
    """A dynamic instruction from user during execution"""
    instruction_id: str
    timestamp: datetime
    instruction_type: InstructionType
    content: str
    target: str  # 'crew', 'agent_id', or 'all'
    priority: int = 1  # 1=low, 5=critical
    processed: bool = False
    response: Optional[str] = None


class InstructionQueue:
    """Thread-safe queue for dynamic instructions"""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.active_instructions: Dict[str, DynamicInstruction] = {}
        self._lock = threading.Lock()
    
    def add_instruction(self, instruction: DynamicInstruction):
        """Add new instruction to queue"""
        with self._lock:
            self.queue.put(instruction)
            self.active_instructions[instruction.instruction_id] = instruction
            logger.info(f"📝 New dynamic instruction: {instruction.content}")
    
    def get_pending_instructions(self, target: Optional[str] = None) -> List[DynamicInstruction]:
        """Get pending instructions for specific target"""
        instructions = []
        
        with self._lock:
            # Process all queued instructions
            while not self.queue.empty():
                try:
                    instruction = self.queue.get_nowait()
                    if not instruction.processed:
                        if target is None or instruction.target == target or instruction.target == 'all':
                            instructions.append(instruction)
                except queue.Empty:
                    break
        
        # Sort by priority (highest first)
        return sorted(instructions, key=lambda x: x.priority, reverse=True)
    
    def mark_processed(self, instruction_id: str, response: str = ""):
        """Mark instruction as processed"""
        with self._lock:
            if instruction_id in self.active_instructions:
                self.active_instructions[instruction_id].processed = True
                self.active_instructions[instruction_id].response = response


class DynamicInstructionHandler:
    """Handles dynamic instructions during crew execution"""
    
    def __init__(self):
        self.instruction_queue = InstructionQueue()
        self.instruction_handlers = self._initialize_handlers()
        self.active_workflows: Dict[str, 'WorkflowContext'] = {}
    
    def _initialize_handlers(self) -> Dict[InstructionType, Callable]:
        """Initialize instruction type handlers"""
        return {
            InstructionType.GUIDANCE: self._handle_guidance,
            InstructionType.CONSTRAINT: self._handle_constraint,
            InstructionType.RESOURCE: self._handle_resource,
            InstructionType.PIVOT: self._handle_pivot,
            InstructionType.FEEDBACK: self._handle_feedback,
            InstructionType.EMERGENCY_STOP: self._handle_emergency_stop,
            InstructionType.SKILL_BOOST: self._handle_skill_boost
        }
    
    def add_instruction(self, content: str, instruction_type: str, target: str = "crew", priority: int = 1) -> str:
        """Add new dynamic instruction"""
        instruction_id = f"inst_{datetime.now().timestamp()}"
        
        instruction = DynamicInstruction(
            instruction_id=instruction_id,
            timestamp=datetime.now(),
            instruction_type=InstructionType(instruction_type),
            content=content,
            target=target,
            priority=priority
        )
        
        self.instruction_queue.add_instruction(instruction)
        return instruction_id
    
    async def process_instructions_for_crew(self, crew_id: str, crew) -> Dict[str, Any]:
        """Process pending instructions for a crew"""
        instructions = self.instruction_queue.get_pending_instructions(crew_id)
        results = []
        
        for instruction in instructions:
            try:
                handler = self.instruction_handlers[instruction.instruction_type]
                result = await handler(instruction, crew)
                
                self.instruction_queue.mark_processed(
                    instruction.instruction_id, 
                    json.dumps(result)
                )
                results.append({
                    "instruction_id": instruction.instruction_id,
                    "type": instruction.instruction_type.value,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error processing instruction {instruction.instruction_id}: {e}")
                results.append({
                    "instruction_id": instruction.instruction_id,
                    "error": str(e)
                })
        
        return {"processed_instructions": results}
    
    async def _handle_guidance(self, instruction: DynamicInstruction, crew) -> Dict[str, Any]:
        """Handle general guidance instruction"""
        # Add guidance to all agents' context
        guidance_context = {
            "user_guidance": instruction.content,
            "timestamp": instruction.timestamp.isoformat(),
            "priority": instruction.priority
        }
        
        # Store in crew's collective memory
        if not hasattr(crew, 'user_guidance'):
            crew.user_guidance = []
        crew.user_guidance.append(guidance_context)
        
        # Notify all agents
        for agent in crew.agents:
            if hasattr(agent, 'memory'):
                agent.memory.experiences.append({
                    "event": "user_guidance",
                    "content": instruction.content,
                    "timestamp": instruction.timestamp.isoformat()
                })
        
        return {
            "action": "guidance_applied",
            "message": f"Guidance shared with {len(crew.agents)} agents",
            "guidance": instruction.content
        }
    
    async def _handle_constraint(self, instruction: DynamicInstruction, crew) -> Dict[str, Any]:
        """Handle constraint instruction"""
        constraint = {
            "constraint": instruction.content,
            "timestamp": instruction.timestamp.isoformat(),
            "active": True
        }
        
        # Add to crew constraints
        if not hasattr(crew, 'active_constraints'):
            crew.active_constraints = []
        crew.active_constraints.append(constraint)
        
        return {
            "action": "constraint_added",
            "message": f"Constraint applied: {instruction.content}",
            "total_constraints": len(crew.active_constraints)
        }
    
    async def _handle_resource(self, instruction: DynamicInstruction, crew) -> Dict[str, Any]:
        """Handle resource provision instruction"""
        resource_info = {
            "resource": instruction.content,
            "provided_at": instruction.timestamp.isoformat(),
            "available": True
        }
        
        # Add to crew resources
        if not hasattr(crew, 'dynamic_resources'):
            crew.dynamic_resources = []
        crew.dynamic_resources.append(resource_info)
        
        # Notify agents of new resource
        for agent in crew.agents:
            if hasattr(agent, 'memory'):
                agent.memory.experiences.append({
                    "event": "resource_provided",
                    "resource": instruction.content,
                    "timestamp": instruction.timestamp.isoformat()
                })
        
        return {
            "action": "resource_provided",
            "message": f"Resource provided: {instruction.content}",
            "total_resources": len(crew.dynamic_resources)
        }
    
    async def _handle_pivot(self, instruction: DynamicInstruction, crew) -> Dict[str, Any]:
        """Handle pivot/strategy change instruction"""
        pivot_info = {
            "old_strategy": getattr(crew, 'current_strategy', 'unknown'),
            "new_direction": instruction.content,
            "pivot_time": instruction.timestamp.isoformat()
        }
        
        # Record strategy change
        if not hasattr(crew, 'strategy_pivots'):
            crew.strategy_pivots = []
        crew.strategy_pivots.append(pivot_info)
        
        # Update crew strategy
        crew.current_strategy = instruction.content
        
        # Inform all agents about pivot
        for agent in crew.agents:
            if hasattr(agent, 'memory'):
                agent.memory.experiences.append({
                    "event": "strategy_pivot",
                    "new_direction": instruction.content,
                    "timestamp": instruction.timestamp.isoformat()
                })
        
        return {
            "action": "strategy_pivoted",
            "message": f"Strategy changed: {instruction.content}",
            "pivot_info": pivot_info
        }
    
    async def _handle_feedback(self, instruction: DynamicInstruction, crew) -> Dict[str, Any]:
        """Handle feedback instruction"""
        feedback = {
            "feedback": instruction.content,
            "timestamp": instruction.timestamp.isoformat(),
            "acknowledged": True
        }
        
        # Store feedback
        if not hasattr(crew, 'user_feedback'):
            crew.user_feedback = []
        crew.user_feedback.append(feedback)
        
        # Share with agents for learning
        for agent in crew.agents:
            if hasattr(agent, 'memory'):
                agent.memory.experiences.append({
                    "event": "user_feedback",
                    "feedback": instruction.content,
                    "timestamp": instruction.timestamp.isoformat()
                })
                
                # If positive feedback, mark recent strategies as successful
                if any(word in instruction.content.lower() for word in ['good', 'great', 'excellent', 'perfect', 'right']):
                    if hasattr(agent.memory, 'successful_strategies'):
                        recent_strategy = f"approach_at_{instruction.timestamp.strftime('%H:%M')}"
                        agent.memory.successful_strategies.append(recent_strategy)
        
        return {
            "action": "feedback_processed",
            "message": f"Feedback acknowledged: {instruction.content}",
            "total_feedback": len(crew.user_feedback)
        }
    
    async def _handle_emergency_stop(self, instruction: DynamicInstruction, crew) -> Dict[str, Any]:
        """Handle emergency stop instruction"""
        # Set stop flag on crew
        crew.emergency_stop = True
        crew.stop_reason = instruction.content
        crew.stopped_at = instruction.timestamp
        
        logger.warning(f"🚨 Emergency stop triggered for crew: {instruction.content}")
        
        return {
            "action": "emergency_stop",
            "message": f"Execution stopped: {instruction.content}",
            "stopped_at": instruction.timestamp.isoformat()
        }
    
    async def _handle_skill_boost(self, instruction: DynamicInstruction, crew) -> Dict[str, Any]:
        """Handle temporary skill boost instruction"""
        # Parse skill boost instruction (e.g., "boost creativity for next 2 tasks")
        boost_info = self._parse_skill_boost(instruction.content)
        
        # Apply temporary skill boosts
        affected_agents = []
        for agent in crew.agents:
            if hasattr(agent, 'personality_traits'):
                skill = boost_info.get('skill')
                boost_amount = boost_info.get('amount', 0.2)
                
                if skill in agent.personality_traits:
                    # Store original value
                    if not hasattr(agent, 'temp_boosts'):
                        agent.temp_boosts = {}
                    agent.temp_boosts[skill] = {
                        'original_value': agent.personality_traits[skill].value,
                        'boost_amount': boost_amount,
                        'expires_after_tasks': boost_info.get('duration', 1)
                    }
                    
                    # Apply boost
                    new_value = min(agent.personality_traits[skill].value + boost_amount, 1.0)
                    agent.personality_traits[skill].value = new_value
                    affected_agents.append(agent.agent_id)
        
        return {
            "action": "skill_boost_applied",
            "message": f"Temporary {boost_info.get('skill', 'skill')} boost applied",
            "affected_agents": affected_agents,
            "boost_info": boost_info
        }
    
    def _parse_skill_boost(self, content: str) -> Dict[str, Any]:
        """Parse skill boost instruction"""
        content_lower = content.lower()
        
        # Extract skill type
        skills = ['creativity', 'analytical', 'collaborative', 'decisive', 'adaptable']
        skill = next((s for s in skills if s in content_lower), 'adaptable')
        
        # Extract duration
        duration = 1  # default
        if 'task' in content_lower:
            import re
            numbers = re.findall(r'\d+', content)
            if numbers:
                duration = int(numbers[0])
        
        # Extract boost amount
        amount = 0.2  # default
        if 'strong' in content_lower or 'major' in content_lower:
            amount = 0.3
        elif 'slight' in content_lower or 'minor' in content_lower:
            amount = 0.1
        
        return {
            'skill': skill,
            'amount': amount,
            'duration': duration
        }
    
    def get_instruction_status(self, instruction_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific instruction"""
        if instruction_id in self.instruction_queue.active_instructions:
            instruction = self.instruction_queue.active_instructions[instruction_id]
            return {
                "instruction_id": instruction_id,
                "type": instruction.instruction_type.value,
                "content": instruction.content,
                "processed": instruction.processed,
                "response": instruction.response,
                "timestamp": instruction.timestamp.isoformat()
            }
        return None
    
    def get_all_instructions(self, crew_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all instructions for crew or all crews"""
        instructions = []
        
        for instruction in self.instruction_queue.active_instructions.values():
            if crew_id is None or instruction.target == crew_id or instruction.target == 'all':
                instructions.append({
                    "instruction_id": instruction.instruction_id,
                    "type": instruction.instruction_type.value,
                    "content": instruction.content,
                    "target": instruction.target,
                    "priority": instruction.priority,
                    "processed": instruction.processed,
                    "timestamp": instruction.timestamp.isoformat()
                })
        
        return sorted(instructions, key=lambda x: x['timestamp'], reverse=True)
    
    def cleanup_crew_instructions(self, crew_id: str):
        """Clean up all instructions for a specific crew"""
        instructions_to_remove = []
        
        for instruction_id, instruction in self.instruction_queue.active_instructions.items():
            if instruction.target == crew_id:
                instructions_to_remove.append(instruction_id)
        
        # Remove crew-specific instructions
        for instruction_id in instructions_to_remove:
            del self.instruction_queue.active_instructions[instruction_id]
        
        logger.info(f"Cleaned up {len(instructions_to_remove)} instructions for crew {crew_id}")


class WorkflowContext:
    """Context for ongoing workflow that can receive dynamic instructions"""
    
    def __init__(self, workflow_id: str, crew):
        self.workflow_id = workflow_id
        self.crew = crew
        self.start_time = datetime.now()
        self.status = "running"
        self.last_instruction_check = datetime.now()
        self.instruction_check_interval = 5  # seconds
    
    async def check_for_instructions(self, instruction_handler: DynamicInstructionHandler) -> bool:
        """Check for and process new instructions"""
        now = datetime.now()
        if (now - self.last_instruction_check).seconds >= self.instruction_check_interval:
            self.last_instruction_check = now
            
            # Process any pending instructions
            results = await instruction_handler.process_instructions_for_crew(
                self.workflow_id, self.crew
            )
            
            # Check for emergency stop
            if hasattr(self.crew, 'emergency_stop') and self.crew.emergency_stop:
                self.status = "stopped"
                return False  # Stop execution
            
            return True  # Continue execution
        
        return True  # No check needed, continue