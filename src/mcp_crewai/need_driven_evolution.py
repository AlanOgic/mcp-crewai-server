#!/usr/bin/env python3
"""
Need-Driven Evolution System
Agents only improve when they encounter real user challenges and fail to meet requirements
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class UserRequest:
    """Represents a user request that triggers potential evolution"""
    request_id: str
    user_query: str
    required_skills: List[str]
    complexity_level: str
    timestamp: datetime
    crew_id: str

@dataclass
class TaskFailure:
    """Represents a failure that triggers need-based improvement"""
    task_id: str
    user_request: UserRequest
    failure_reason: str
    missing_capabilities: List[str]
    agent_id: str
    timestamp: datetime

@dataclass
class ImprovementNeed:
    """Identifies specific improvement needs based on user requests"""
    need_id: str
    skill_gap: str
    user_context: str
    priority: int  # 1-5, 5 being critical
    evidence: List[str]
    timestamp: datetime

class NeedDrivenEvolution:
    """Evolution engine that responds to actual user needs"""
    
    def __init__(self):
        self.task_failures: List[TaskFailure] = []
        self.improvement_needs: List[ImprovementNeed] = []
        self.user_requests: List[UserRequest] = []
        
    def analyze_user_request(self, user_query: str, crew_id: str) -> UserRequest:
        """Analyze user request to identify required capabilities"""
        request_id = f"req_{int(datetime.now().timestamp())}"
        
        # Analyze what skills are needed for this request
        required_skills = self._extract_required_skills(user_query)
        complexity_level = self._assess_complexity(user_query)
        
        user_request = UserRequest(
            request_id=request_id,
            user_query=user_query,
            required_skills=required_skills,
            complexity_level=complexity_level,
            timestamp=datetime.now(),
            crew_id=crew_id
        )
        
        self.user_requests.append(user_request)
        logger.info(f"Analyzed user request: {required_skills} skills needed")
        
        return user_request
    
    def check_capability_gaps(self, user_request: UserRequest, agent_capabilities: Dict[str, float]) -> List[str]:
        """Check if agent has required capabilities for user request"""
        gaps = []
        
        for required_skill in user_request.required_skills:
            agent_skill_level = agent_capabilities.get(required_skill, 0.0)
            
            # Define minimum thresholds based on complexity
            min_threshold = {
                "simple": 0.4,
                "moderate": 0.6,
                "complex": 0.8,
                "expert": 0.9
            }.get(user_request.complexity_level, 0.6)
            
            if agent_skill_level < min_threshold:
                gaps.append(f"{required_skill} (has {agent_skill_level:.2f}, needs {min_threshold:.2f})")
        
        return gaps
    
    def record_task_failure(self, user_request: UserRequest, agent_id: str, failure_reason: str, missing_capabilities: List[str]) -> TaskFailure:
        """Record a task failure that triggers improvement needs"""
        task_failure = TaskFailure(
            task_id=f"task_{int(datetime.now().timestamp())}",
            user_request=user_request,
            failure_reason=failure_reason,
            missing_capabilities=missing_capabilities,
            agent_id=agent_id,
            timestamp=datetime.now()
        )
        
        self.task_failures.append(task_failure)
        
        # Generate improvement need based on failure
        improvement_need = self._generate_improvement_need(task_failure)
        self.improvement_needs.append(improvement_need)
        
        logger.info(f"Task failure recorded: {failure_reason}")
        logger.info(f"Improvement need identified: {improvement_need.skill_gap}")
        
        return task_failure
    
    def should_trigger_research(self, agent_id: str) -> Optional[ImprovementNeed]:
        """Check if agent should research improvements based on recent failures"""
        # Look for recent improvement needs for this agent
        from datetime import timedelta
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        recent_needs = [
            need for need in self.improvement_needs 
            if need.timestamp > twenty_four_hours_ago
        ]
        
        # Find highest priority need
        if recent_needs:
            highest_priority = max(recent_needs, key=lambda x: x.priority)
            if highest_priority.priority >= 3:  # Priority 3+ triggers research
                return highest_priority
        
        return None
    
    def get_research_query_for_need(self, improvement_need: ImprovementNeed) -> str:
        """Generate web search query based on improvement need"""
        skill_gap = improvement_need.skill_gap
        user_context = improvement_need.user_context
        
        # Create contextual search query
        if "creative" in skill_gap.lower():
            return f"improve creative thinking skills for {user_context}"
        elif "analytical" in skill_gap.lower():
            return f"enhance analytical abilities for {user_context}"
        elif "collaborative" in skill_gap.lower():
            return f"develop collaboration skills for {user_context}"
        elif "technical" in skill_gap.lower():
            return f"build technical expertise for {user_context}"
        else:
            return f"improve {skill_gap} skills for {user_context}"
    
    def validate_improvement_impact(self, agent_id: str, improvement_need: ImprovementNeed, 
                                  research_results: Dict[str, Any]) -> bool:
        """Validate if research results address the actual user need"""
        
        # Check if research provides actionable insights for the specific skill gap
        actionable_insights = research_results.get('actionable_insights', [])
        skill_gap = improvement_need.skill_gap.lower()
        
        relevant_insights = [
            insight for insight in actionable_insights 
            if any(keyword in insight.lower() for keyword in skill_gap.split())
        ]
        
        # Research is valid if it provides at least 2 relevant insights
        is_valid = len(relevant_insights) >= 2
        
        if is_valid:
            logger.info(f"Research validated: {len(relevant_insights)} relevant insights found")
        else:
            logger.warning(f"Research insufficient: only {len(relevant_insights)} relevant insights")
        
        return is_valid
    
    def create_evolution_plan(self, improvement_need: ImprovementNeed, 
                            research_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create specific evolution plan based on user need and research"""
        
        skill_gap = improvement_need.skill_gap
        actionable_insights = research_results.get('actionable_insights', [])
        
        # Map skill gaps to personality traits
        trait_mapping = {
            "creative": "creative",
            "analytical": "analytical", 
            "collaborative": "collaborative",
            "decisive": "decisive",
            "adaptable": "adaptable",
            "risk_taking": "risk_taking"
        }
        
        target_trait = None
        for gap_word, trait in trait_mapping.items():
            if gap_word in skill_gap.lower():
                target_trait = trait
                break
        
        if not target_trait:
            target_trait = "adaptable"  # Default fallback
        
        evolution_plan = {
            "trigger_reason": f"User need: {improvement_need.user_context}",
            "target_trait": target_trait,
            "improvement_goal": improvement_need.skill_gap,
            "research_evidence": actionable_insights[:3],  # Top 3 insights
            "priority": improvement_need.priority,
            "user_request_context": improvement_need.user_context,
            "expected_improvement": 0.1 + (improvement_need.priority * 0.05),  # 0.15-0.35 based on priority
            "evolution_type": "need_driven_research_based"
        }
        
        return evolution_plan
    
    def _extract_required_skills(self, user_query: str) -> List[str]:
        """Extract required skills from user query"""
        query_lower = user_query.lower()
        skills = []
        
        # Skill detection patterns
        skill_patterns = {
            "creative": ["creative", "design", "brainstorm", "innovative", "artistic", "imaginative"],
            "analytical": ["analyze", "data", "research", "evaluate", "assess", "calculate", "logical"],
            "collaborative": ["team", "collaborate", "coordinate", "communicate", "together", "group"],
            "technical": ["code", "program", "technical", "engineering", "development", "system"],
            "decisive": ["decide", "choose", "select", "recommend", "conclude", "determine"],
            "leadership": ["lead", "manage", "direct", "guide", "supervise", "organize"]
        }
        
        for skill, keywords in skill_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                skills.append(skill)
        
        # If no specific skills detected, assume general problem-solving
        if not skills:
            skills = ["analytical", "collaborative"]
        
        return skills
    
    def _assess_complexity(self, user_query: str) -> str:
        """Assess complexity level of user request"""
        query_lower = user_query.lower()
        
        # Complexity indicators
        complex_indicators = ["complex", "advanced", "expert", "comprehensive", "detailed", "thorough"]
        moderate_indicators = ["analyze", "research", "develop", "create", "design", "plan"]
        simple_indicators = ["simple", "basic", "quick", "easy", "summarize", "list"]
        
        if any(indicator in query_lower for indicator in complex_indicators):
            return "complex"
        elif any(indicator in query_lower for indicator in moderate_indicators):
            return "moderate"
        elif any(indicator in query_lower for indicator in simple_indicators):
            return "simple"
        else:
            return "moderate"  # Default
    
    def _generate_improvement_need(self, task_failure: TaskFailure) -> ImprovementNeed:
        """Generate improvement need from task failure"""
        
        # Determine priority based on failure severity and user context
        priority = 3  # Default medium priority
        
        if task_failure.user_request.complexity_level == "complex":
            priority = 5  # High priority for complex requests
        elif task_failure.user_request.complexity_level == "simple":
            priority = 2  # Lower priority for simple requests
        
        # Extract primary skill gap
        primary_gap = task_failure.missing_capabilities[0] if task_failure.missing_capabilities else "general capability"
        
        improvement_need = ImprovementNeed(
            need_id=f"need_{int(datetime.now().timestamp())}",
            skill_gap=primary_gap,
            user_context=task_failure.user_request.user_query[:100] + "...",
            priority=priority,
            evidence=task_failure.missing_capabilities,
            timestamp=datetime.now()
        )
        
        return improvement_need
    
    def get_improvement_history(self, agent_id: str) -> Dict[str, Any]:
        """Get history of improvements for specific agent"""
        agent_failures = [f for f in self.task_failures if f.agent_id == agent_id]
        agent_needs = [n for n in self.improvement_needs if any(f.agent_id == agent_id for f in self.task_failures if f.task_id in str(n.need_id))]
        
        return {
            "total_failures": len(agent_failures),
            "improvement_needs": len(agent_needs),
            "recent_failures": [f.failure_reason for f in agent_failures[-3:]],
            "active_needs": [n.skill_gap for n in agent_needs if n.priority >= 3],
            "learning_focus": self._get_learning_focus(agent_failures)
        }
    
    def _get_learning_focus(self, failures: List[TaskFailure]) -> List[str]:
        """Identify learning focus areas based on failure patterns"""
        skill_gaps = []
        for failure in failures:
            skill_gaps.extend(failure.missing_capabilities)
        
        # Count occurrences and return most common gaps
        gap_counts = {}
        for gap in skill_gaps:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1
        
        # Return top 3 most common gaps
        return sorted(gap_counts.keys(), key=lambda x: gap_counts[x], reverse=True)[:3]