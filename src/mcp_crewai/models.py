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
        return {
            "tools": len(self.agents[0].tools) > 0 if self.agents else False,
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
        """Make autonomous decisions about crew composition and actions"""
        assessment = self.assess_capabilities()
        
        decision = {
            "action": "continue",
            "changes": [],
            "reasoning": "Current setup is adequate"
        }
        
        # Decision logic based on assessment
        if assessment["missing_elements"]:
            decision["action"] = "modify_team"
            decision["changes"] = [
                f"add_{element}" for element in assessment["missing_elements"]
            ]
            decision["reasoning"] = f"Missing critical elements: {assessment['missing_elements']}"
        
        elif assessment["team_balance"] < 0.3:
            decision["action"] = "rebalance_team"
            decision["changes"] = ["redistribute_roles", "adjust_personalities"]
            decision["reasoning"] = "Team lacks diversity and balance"
        
        return decision
    
    def execute_autonomous_changes(self, decision: Dict[str, Any]) -> None:
        """Execute autonomous changes based on decisions"""
        if decision["action"] == "modify_team":
            self._modify_team_composition(decision["changes"])
        elif decision["action"] == "rebalance_team":
            self._rebalance_team(decision["changes"])
        
        # Log the autonomous decision
        self.collective_memory[datetime.now().isoformat()] = {
            "decision": decision,
            "autonomy_level": self.autonomy_level
        }
    
    def _modify_team_composition(self, changes: List[str]) -> None:
        """Modify team composition based on identified needs"""
        # Implementation would add/remove agents based on needs
        pass
    
    def _rebalance_team(self, changes: List[str]) -> None:
        """Rebalance existing team members"""
        # Implementation would adjust existing agents' roles and traits
        pass