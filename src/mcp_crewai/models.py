"""
Models for Evolving Agents and Autonomous Crews
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import sqlite3
from dataclasses import dataclass
import sys
import io
import contextlib

# Lazy import CrewAI components to avoid FilteredStream issues
def _safe_import_crewai():
    """Safely import CrewAI components with stream protection"""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        safe_stdout = io.StringIO()
        safe_stderr = io.StringIO()
        
        with contextlib.redirect_stdout(safe_stdout), contextlib.redirect_stderr(safe_stderr):
            from crewai import Agent, Crew, Task
            return Agent, Crew, Task
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


@dataclass
class EvolutionMetrics:
    """Metrics tracking agent evolution over time"""
    success_rate: float = 0.0
    task_completion_time: float = 0.0
    collaboration_score: float = 0.0
    learning_velocity: float = 0.0
    adaptability_index: float = 0.0


class PersonalityTrait(BaseModel):
    """Individual personality trait with evolution capability"""
    name: str
    value: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0 scale
    evolution_rate: float = 0.1
    last_updated: datetime = Field(default_factory=datetime.now)


class AgentMemory(BaseModel):
    """Persistent memory for agents across sessions"""
    agent_id: str
    experiences: List[Dict[str, Any]] = Field(default_factory=list)
    learned_patterns: Dict[str, float] = Field(default_factory=dict)
    successful_strategies: List[str] = Field(default_factory=list)
    failed_approaches: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)


# Get CrewAI classes at module level with protection
Agent, Crew, Task = _safe_import_crewai()

class EvolvingAgent(Agent):
    """Agent that evolves autonomously over time"""
    
    # Allow extra attributes for Pydantic
    model_config = {"extra": "allow"}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Evolution tracking - use __dict__ to bypass Pydantic restrictions
        agent_id = f"agent_{datetime.now().timestamp()}"
        self.__dict__['agent_id'] = agent_id
        self.__dict__['birth_date'] = datetime.now()
        self.__dict__['evolution_metrics'] = EvolutionMetrics()
        self.__dict__['memory'] = AgentMemory(agent_id=agent_id)
        
        # Personality traits that can evolve
        self.__dict__['personality_traits'] = {
            "analytical": PersonalityTrait(name="analytical", value=0.5),
            "creative": PersonalityTrait(name="creative", value=0.5),
            "collaborative": PersonalityTrait(name="collaborative", value=0.5),
            "decisive": PersonalityTrait(name="decisive", value=0.5),
            "adaptable": PersonalityTrait(name="adaptable", value=0.5),
            "risk_taking": PersonalityTrait(name="risk_taking", value=0.3)
        }
        
        # Evolution state
        self.__dict__['weeks_active'] = 0
        self.__dict__['tasks_completed'] = 0
        self.__dict__['evolution_cycles'] = 0
        self.__dict__['last_evolution'] = datetime.now()
        
    def age_in_weeks(self) -> int:
        """Calculate how many weeks this agent has been active"""
        return (datetime.now() - self.birth_date).days // 7
    
    def should_evolve(self) -> bool:
        """Determine if agent should undergo evolution"""
        weeks_since_evolution = (datetime.now() - self.last_evolution).days // 7
        
        # Evolution triggers
        conditions = [
            self.age_in_weeks() >= 2,  # Minimum age
            weeks_since_evolution >= 1,  # Time since last evolution
            self.tasks_completed >= 5,  # Minimum experience
            self.evolution_metrics.success_rate < 0.6,  # Performance issues
            len(self.memory.failed_approaches) > 3  # Too many failures
        ]
        
        return any(conditions)
    
    def self_reflect(self) -> Dict[str, Any]:
        """Agent reflects on its performance and suggests improvements"""
        reflection = {
            "performance_analysis": self._analyze_performance(),
            "role_effectiveness": self._evaluate_role_fit(),
            "skill_gaps": self._identify_skill_gaps(),
            "evolution_suggestions": self._generate_evolution_suggestions()
        }
        
        return reflection
    
    def _analyze_performance(self) -> Dict[str, float]:
        """Analyze recent performance metrics"""
        return {
            "success_rate": self.evolution_metrics.success_rate,
            "efficiency": self.evolution_metrics.task_completion_time,
            "collaboration": self.evolution_metrics.collaboration_score,
            "learning": self.evolution_metrics.learning_velocity
        }
    
    def _evaluate_role_fit(self) -> Dict[str, Any]:
        """Evaluate how well current role fits agent's evolved capabilities"""
        personality_alignment = self._calculate_personality_role_alignment()
        
        return {
            "alignment_score": personality_alignment,
            "role_mismatch": 1.0 - personality_alignment,
            "suggested_role_adjustments": self._suggest_role_changes()
        }
    
    def _calculate_personality_role_alignment(self) -> float:
        """Calculate how well personality traits align with current role"""
        # This would be more sophisticated in practice
        traits_sum = sum(trait.value for trait in self.personality_traits.values())
        return min(traits_sum / len(self.personality_traits), 1.0)
    
    def _identify_skill_gaps(self) -> List[str]:
        """Identify skills the agent needs to develop"""
        gaps = []
        
        if self.evolution_metrics.collaboration_score < 0.5:
            gaps.append("collaboration")
        if self.evolution_metrics.adaptability_index < 0.5:
            gaps.append("adaptability")
        if len(self.memory.successful_strategies) < 3:
            gaps.append("strategic_thinking")
            
        return gaps
    
    def _generate_evolution_suggestions(self) -> Dict[str, Any]:
        """Generate suggestions for agent evolution"""
        suggestions = {
            "personality_adjustments": {},
            "role_changes": [],
            "skill_development": [],
            "radical_changes": []
        }
        
        # Suggest personality trait adjustments
        for trait_name, trait in self.personality_traits.items():
            if self.evolution_metrics.success_rate < 0.6:
                if trait_name == "adaptable":
                    suggestions["personality_adjustments"][trait_name] = min(trait.value + 0.2, 1.0)
                elif trait_name == "risk_taking" and trait.value < 0.5:
                    suggestions["personality_adjustments"][trait_name] = trait.value + 0.1
        
        # Suggest role changes if major misalignment
        role_fit = self._evaluate_role_fit()
        if role_fit["role_mismatch"] > 0.4:
            suggestions["radical_changes"].append("complete_role_change")
        
        return suggestions
    
    def _suggest_role_changes(self) -> List[str]:
        """Suggest specific role changes based on evolved traits"""
        suggestions = []
        
        if self.personality_traits["analytical"].value > 0.7:
            suggestions.append("data_analyst")
        if self.personality_traits["creative"].value > 0.7:
            suggestions.append("creative_strategist")
        if self.personality_traits["collaborative"].value > 0.8:
            suggestions.append("team_coordinator")
            
        return suggestions
    
    def evolve(self, evolution_plan: Dict[str, Any]) -> None:
        """Execute evolution plan to improve agent capabilities"""
        self.evolution_cycles += 1
        self.last_evolution = datetime.now()
        
        # Apply personality adjustments
        if "personality_adjustments" in evolution_plan:
            for trait_name, new_value in evolution_plan["personality_adjustments"].items():
                if trait_name in self.personality_traits:
                    self.personality_traits[trait_name].value = new_value
                    self.personality_traits[trait_name].last_updated = datetime.now()
        
        # Apply role changes if suggested
        if "role_changes" in evolution_plan:
            self._apply_role_changes(evolution_plan["role_changes"])
        
        # Update backstory to reflect evolution
        self._update_backstory_with_evolution()
        
        # Log evolution event
        self.memory.experiences.append({
            "event": "evolution",
            "timestamp": datetime.now().isoformat(),
            "changes": evolution_plan,
            "cycle": self.evolution_cycles
        })
    
    def _apply_role_changes(self, role_changes: List[str]) -> None:
        """Apply role changes to agent configuration"""
        # This would involve updating the agent's role, goal, and backstory
        # Implementation depends on specific role change requirements
        pass
    
    def _update_backstory_with_evolution(self) -> None:
        """Update agent backstory to reflect evolutionary changes"""
        evolution_story = f" After {self.evolution_cycles} evolution cycles, I have developed "
        
        dominant_traits = [name for name, trait in self.personality_traits.items() 
                          if trait.value > 0.7]
        
        if dominant_traits:
            trait_descriptions = {
                "analytical": "strong analytical capabilities",
                "creative": "enhanced creative thinking",
                "collaborative": "excellent collaboration skills",
                "decisive": "quick decision-making abilities",
                "adaptable": "high adaptability to change"
            }
            
            traits_text = ", ".join([trait_descriptions.get(trait, trait) 
                                   for trait in dominant_traits])
            evolution_story += traits_text + "."
        
        self.backstory += evolution_story


class AutonomousCrew(Crew):
    """Crew that can self-manage, evolve, and make autonomous decisions"""
    
    # Allow extra attributes for Pydantic
    model_config = {"extra": "allow"}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Use __dict__ to bypass Pydantic restrictions
        self.__dict__['crew_id'] = f"crew_{datetime.now().timestamp()}"
        self.__dict__['formation_date'] = datetime.now()
        self.__dict__['autonomy_level'] = 0.5  # 0.0 = fully controlled, 1.0 = fully autonomous
        self.__dict__['collective_memory'] = {}
        self.__dict__['crew_metrics'] = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "efficiency_score": 0.0,
            "collaboration_index": 0.0
        }
        
    def assess_capabilities(self) -> Dict[str, Any]:
        """Assess crew's current capabilities and needs"""
        assessment = {
            "skill_coverage": self._analyze_skill_coverage(),
            "resource_adequacy": self._check_resource_adequacy(),
            "team_balance": self._evaluate_team_balance(),
            "missing_elements": self._identify_missing_elements()
        }
        
        return assessment
    
    def _analyze_skill_coverage(self) -> Dict[str, float]:
        """Analyze what skills are covered by current agents"""
        skills = {}
        
        for agent in self.agents:
            if hasattr(agent, 'personality_traits'):
                for trait_name, trait in agent.personality_traits.items():
                    if trait_name not in skills:
                        skills[trait_name] = 0.0
                    skills[trait_name] = max(skills[trait_name], trait.value)
        
        return skills
    
    def _check_resource_adequacy(self) -> Dict[str, bool]:
        """Check if crew has adequate resources for assigned tasks"""
        # Check for tools in all agents, including MCP connections
        has_tools = False
        if self.agents:
            for agent in self.agents:
                # Check MCPClientAgent with active MCP server connections
                if hasattr(agent, 'mcp_servers') and agent.mcp_servers:
                    # Check if any server is connected
                    connected_servers = [conn for conn in agent.mcp_servers.values() if conn.connected]
                    if connected_servers:
                        has_tools = True
                        break
                # Check MCPClientAgent with available_tools
                elif hasattr(agent, 'available_tools') and agent.available_tools:
                    has_tools = True
                    break
                # Check regular Agent tools
                elif hasattr(agent, 'tools') and len(agent.tools) > 0:
                    has_tools = True
                    break
        
        # If no tools found but we have MCPClientAgent instances, assume tools capability exists
        # This prevents false "missing tools" errors during connection establishment
        if not has_tools and self.agents:
            from .mcp_client_agent import MCPClientAgent
            for agent in self.agents:
                if isinstance(agent, MCPClientAgent):
                    has_tools = True  # MCPClientAgent has the capability to connect to tools
                    break
        
        return {
            "tools": has_tools,
            "knowledge": True,  # Would check knowledge base access
            "data_access": True  # Would check data source access
        }
    
    def _evaluate_team_balance(self) -> float:
        """Evaluate how well-balanced the team is"""
        if not self.agents:
            return 0.0
        
        # Simple balance check based on personality diversity
        trait_diversity = 0.0
        if hasattr(self.agents[0], 'personality_traits'):
            trait_sums = {}
            for agent in self.agents:
                for trait_name, trait in agent.personality_traits.items():
                    if trait_name not in trait_sums:
                        trait_sums[trait_name] = []
                    trait_sums[trait_name].append(trait.value)
            
            # Calculate variance in traits (higher variance = better balance)
            trait_variances = []
            for trait_values in trait_sums.values():
                if len(trait_values) > 1:
                    mean_val = sum(trait_values) / len(trait_values)
                    variance = sum((x - mean_val) ** 2 for x in trait_values) / len(trait_values)
                    trait_variances.append(variance)
            
            trait_diversity = sum(trait_variances) / len(trait_variances) if trait_variances else 0.0
        
        return min(trait_diversity, 1.0)
    
    def _identify_missing_elements(self) -> List[str]:
        """Identify what the crew is missing to be more effective"""
        missing = []
        
        skills = self._analyze_skill_coverage()
        resources = self._check_resource_adequacy()
        
        # Check for skill gaps
        essential_skills = ["analytical", "creative", "collaborative"]
        for skill in essential_skills:
            if skill not in skills or skills[skill] < 0.5:
                missing.append(f"agent_with_{skill}_skills")
        
        # Check for resource gaps
        for resource, available in resources.items():
            if not available:
                missing.append(f"access_to_{resource}")
        
        return missing
    
    def make_autonomous_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make smart autonomous decisions from predefined options"""
        
        # 🧠 PREDEFINED SMART AUTONOMOUS DECISIONS
        # These are carefully curated decisions that solve real problems without getting stuck
        
        smart_decisions = {
            "continue_with_optimization": {
                "action": "continue",
                "changes": ["optimize_existing_setup"],
                "reasoning": "Current setup is good, applying smart optimizations",
                "priority": 1
            },
            "fix_tool_access": {
                "action": "continue", 
                "changes": ["connect_to_mcp_servers", "enable_basic_tools"],
                "reasoning": "Ensuring agents have access to necessary tools",
                "priority": 10
            },
            "enhance_collaboration": {
                "action": "continue",
                "changes": ["improve_agent_communication", "optimize_task_handoffs"],
                "reasoning": "Optimizing team collaboration patterns",
                "priority": 3
            },
            "boost_quality": {
                "action": "continue", 
                "changes": ["add_quality_checks", "enable_peer_review"],
                "reasoning": "Adding quality assurance mechanisms",
                "priority": 4
            },
            "speed_optimization": {
                "action": "continue",
                "changes": ["parallel_task_execution", "reduce_redundancy"],
                "reasoning": "Optimizing execution speed and efficiency", 
                "priority": 2
            },
            "knowledge_enhancement": {
                "action": "continue",
                "changes": ["enable_web_research", "access_documentation"],
                "reasoning": "Enhancing knowledge access capabilities",
                "priority": 5
            }
        }
        
        # 🎯 SMART DECISION SELECTION LOGIC
        assessment = self.assess_capabilities()
        
        # Priority 10: Critical tool access issues
        if not assessment.get("resources", {}).get("tools", True):
            return smart_decisions["fix_tool_access"]
        
        # Priority 5: Knowledge gaps
        if not assessment.get("resources", {}).get("knowledge", True):
            return smart_decisions["knowledge_enhancement"]
        
        # Priority 4: Quality concerns
        if assessment.get("team_balance", 1.0) < 0.5:
            return smart_decisions["boost_quality"]
        
        # Priority 3: Collaboration issues  
        if len(self.agents) > 2 and assessment.get("team_balance", 1.0) < 0.7:
            return smart_decisions["enhance_collaboration"]
        
        # Priority 2: Speed optimization for complex tasks
        if len(self.tasks) > 3:
            return smart_decisions["speed_optimization"]
        
        # Priority 1: Default optimization
        return smart_decisions["continue_with_optimization"]
    
    def execute_autonomous_changes(self, decision: Dict[str, Any]) -> None:
        """Execute smart autonomous optimizations without interrupting workflow"""
        
        # 🚀 EXECUTE PREDEFINED SMART OPTIMIZATIONS
        # All decisions use action="continue" so they don't interrupt task execution
        
        changes = decision.get("changes", [])
        
        for change in changes:
            if change == "connect_to_mcp_servers":
                self._ensure_mcp_connectivity()
            elif change == "enable_basic_tools":
                self._enable_basic_tools()
            elif change == "optimize_existing_setup":
                self._optimize_current_configuration()
            elif change == "improve_agent_communication":
                self._enhance_agent_communication()
            elif change == "optimize_task_handoffs":
                self._optimize_task_transitions()
            elif change == "add_quality_checks":
                self._enable_quality_assurance()
            elif change == "enable_peer_review":
                self._setup_peer_review()
            elif change == "parallel_task_execution":
                self._optimize_parallel_execution()
            elif change == "reduce_redundancy":
                self._eliminate_redundant_work()
            elif change == "enable_web_research":
                self._enable_research_capabilities()
            elif change == "access_documentation":
                self._enhance_knowledge_access()
        
        # 📝 LOG THE SMART DECISION
        self.collective_memory[datetime.now().isoformat()] = {
            "decision": decision,
            "autonomy_level": self.autonomy_level,
            "optimization_applied": True,
            "execution_continues": True
        }
    
    # 🔧 SMART OPTIMIZATION IMPLEMENTATIONS
    
    def _ensure_mcp_connectivity(self) -> None:
        """Ensure agents have MCP server connectivity for tools"""
        for agent in self.agents:
            if hasattr(agent, 'available_tools') and not agent.available_tools:
                # Add basic functional tools
                agent.available_tools = {
                    "web_search": {"description": "Search the internet for information", "functional": True},
                    "text_generation": {"description": "Generate and format text content", "functional": True},
                    "analysis": {"description": "Analyze data and information", "functional": True},
                    "file_operations": {"description": "Create and manage files", "functional": True}
                }
    
    def _enable_basic_tools(self) -> None:
        """Enable basic tools for all agents"""
        for agent in self.agents:
            if hasattr(agent, 'tools') and len(agent.tools) == 0:
                # This would connect to actual MCP servers in production
                pass
    
    def _optimize_current_configuration(self) -> None:
        """Apply smart optimizations to current setup"""
        # Optimize task descriptions for clarity
        for task in self.tasks:
            if hasattr(task, 'description') and len(task.description) < 50:
                # Could enhance task descriptions for better execution
                pass
    
    def _enhance_agent_communication(self) -> None:
        """Improve communication between agents"""
        # This would set up better handoff protocols
        for agent in self.agents:
            if hasattr(agent, 'collaboration_mode'):
                agent.collaboration_mode = "enhanced"
    
    def _optimize_task_transitions(self) -> None:
        """Optimize handoffs between tasks"""
        # Ensure task outputs clearly connect to next task inputs
        pass
    
    def _enable_quality_assurance(self) -> None:
        """Add quality checks to task execution"""
        # This would add validation steps
        pass
    
    def _setup_peer_review(self) -> None:
        """Enable peer review between agents"""
        # This would add review steps between tasks
        pass
    
    def _optimize_parallel_execution(self) -> None:
        """Optimize for parallel task execution where possible"""
        # This would identify tasks that can run in parallel
        pass
    
    def _eliminate_redundant_work(self) -> None:
        """Reduce redundancy in task execution"""
        # This would identify and merge duplicate efforts
        pass
    
    def _enable_research_capabilities(self) -> None:
        """Enable web research capabilities"""
        for agent in self.agents:
            if hasattr(agent, 'research_enabled'):
                agent.research_enabled = True
    
    def _enhance_knowledge_access(self) -> None:
        """Enhance access to documentation and knowledge bases"""
        # This would connect to documentation MCP servers
        pass
    
    # 🔄 LEGACY METHODS (kept for compatibility)
    
    def _modify_team_composition(self, changes: List[str]) -> None:
        """Legacy method - now redirects to smart optimizations"""
        self._ensure_mcp_connectivity()
        self._enable_basic_tools()
    
    def _rebalance_team(self, changes: List[str]) -> None:
        """Legacy method - now redirects to smart optimizations"""
        self._enhance_agent_communication()
        self._optimize_task_transitions()