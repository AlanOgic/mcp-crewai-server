"""
Evolution Engine - Core intelligence for autonomous agent evolution
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import sqlite3
import os

logger = logging.getLogger(__name__)


@dataclass
class EvolutionEvent:
    """Record of an evolution event"""
    agent_id: str
    timestamp: datetime
    evolution_type: str
    changes: Dict[str, Any]
    performance_before: Dict[str, float]
    performance_after: Dict[str, float]
    success: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }


class EvolutionEngine:
    """
    🧠 CORE EVOLUTION INTELLIGENCE
    
    Manages autonomous evolution of agents and crews:
    - Analyzes performance patterns
    - Triggers appropriate evolutions
    - Learns from evolution outcomes
    - Optimizes evolution strategies
    """
    
    def __init__(self, db_path: str = "evolution_history.db"):
        self.db_path = db_path
        self.evolution_history: List[EvolutionEvent] = []
        self.evolution_strategies = self._initialize_strategies()
        self._setup_database()
    
    def _setup_database(self):
        """Setup SQLite database for persistent evolution tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                evolution_type TEXT NOT NULL,
                changes TEXT NOT NULL,
                performance_before TEXT NOT NULL,
                performance_after TEXT NOT NULL,
                success BOOLEAN NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_memories (
                agent_id TEXT PRIMARY KEY,
                memory_data TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _initialize_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize evolution strategies"""
        return {
            "personality_drift": {
                "description": "Gradual personality trait adjustments",
                "trigger_conditions": ["low_performance", "repeated_failures"],
                "success_rate": 0.7,
                "risk_level": "low"
            },
            "role_specialization": {
                "description": "Evolve towards specialized role",
                "trigger_conditions": ["skill_pattern_detected", "team_gap_identified"],
                "success_rate": 0.6,
                "risk_level": "medium"
            },
            "radical_transformation": {
                "description": "Complete personality/role overhaul",
                "trigger_conditions": ["critical_failure", "major_mismatch"],
                "success_rate": 0.4,
                "risk_level": "high"
            },
            "collaborative_adaptation": {
                "description": "Adapt to improve team dynamics",
                "trigger_conditions": ["team_conflict", "poor_collaboration"],
                "success_rate": 0.8,
                "risk_level": "low"
            }
        }
    
    def analyze_evolution_readiness(self, agent) -> Dict[str, Any]:
        """Analyze if and how an agent should evolve"""
        analysis = {
            "should_evolve": False,
            "recommended_strategy": None,
            "confidence": 0.0,
            "reasoning": [],
            "risk_assessment": "low"
        }
        
        # Performance analysis
        performance_score = self._calculate_performance_score(agent)
        
        # Pattern analysis
        patterns = self._analyze_agent_patterns(agent)
        
        # Determine evolution need
        if performance_score < 0.6:
            analysis["should_evolve"] = True
            analysis["reasoning"].append(f"Low performance score: {performance_score:.2f}")
        
        if len(agent.memory.failed_approaches) > 3:
            analysis["should_evolve"] = True
            analysis["reasoning"].append("Too many failed approaches")
        
        if agent.age_in_weeks() > 4 and agent.evolution_cycles == 0:
            analysis["should_evolve"] = True
            analysis["reasoning"].append("Agent has never evolved despite age")
        
        # Recommend strategy
        if analysis["should_evolve"]:
            strategy = self._recommend_evolution_strategy(agent, patterns)
            analysis["recommended_strategy"] = strategy
            analysis["confidence"] = self._calculate_evolution_confidence(agent, strategy)
            analysis["risk_assessment"] = self.evolution_strategies[strategy]["risk_level"]
        
        return analysis
    
    def _calculate_performance_score(self, agent) -> float:
        """Calculate overall performance score for agent"""
        metrics = agent.evolution_metrics
        
        # Weighted performance calculation
        score = (
            metrics.success_rate * 0.4 +
            (1.0 - min(metrics.task_completion_time / 100, 1.0)) * 0.2 +
            metrics.collaboration_score * 0.3 +
            metrics.adaptability_index * 0.1
        )
        
        return max(0.0, min(score, 1.0))
    
    def _analyze_agent_patterns(self, agent) -> Dict[str, Any]:
        """Analyze behavioral patterns in agent"""
        patterns = {
            "dominant_traits": [],
            "weak_traits": [],
            "success_patterns": [],
            "failure_patterns": [],
            "collaboration_style": "unknown"
        }
        
        # Identify dominant and weak traits
        for trait_name, trait in agent.personality_traits.items():
            if trait.value > 0.7:
                patterns["dominant_traits"].append(trait_name)
            elif trait.value < 0.3:
                patterns["weak_traits"].append(trait_name)
        
        # Analyze success/failure patterns from memory
        if agent.memory.successful_strategies:
            patterns["success_patterns"] = agent.memory.successful_strategies[-3:]  # Last 3
        
        if agent.memory.failed_approaches:
            patterns["failure_patterns"] = agent.memory.failed_approaches[-3:]  # Last 3
        
        # Determine collaboration style
        collab_score = agent.personality_traits.get("collaborative", None)
        if collab_score:
            if collab_score.value > 0.7:
                patterns["collaboration_style"] = "highly_collaborative"
            elif collab_score.value < 0.3:
                patterns["collaboration_style"] = "independent"
            else:
                patterns["collaboration_style"] = "moderately_collaborative"
        
        return patterns
    
    def _recommend_evolution_strategy(self, agent, patterns: Dict[str, Any]) -> str:
        """Recommend best evolution strategy for agent"""
        
        # Strategy selection logic
        performance_score = self._calculate_performance_score(agent)
        
        if performance_score < 0.3:
            return "radical_transformation"
        
        if len(patterns["weak_traits"]) > 2:
            return "personality_drift"
        
        if patterns["collaboration_style"] == "independent" and agent.evolution_metrics.collaboration_score < 0.4:
            return "collaborative_adaptation"
        
        if len(patterns["dominant_traits"]) >= 2:
            return "role_specialization"
        
        return "personality_drift"  # Default safe option
    
    def _calculate_evolution_confidence(self, agent, strategy: str) -> float:
        """Calculate confidence in evolution strategy"""
        base_confidence = self.evolution_strategies[strategy]["success_rate"]
        
        # Adjust based on agent characteristics
        if agent.age_in_weeks() < 2:
            base_confidence *= 0.8  # Less confident with young agents
        
        if agent.evolution_cycles > 3:
            base_confidence *= 0.9  # Diminishing returns
        
        if agent.evolution_metrics.adaptability_index > 0.7:
            base_confidence *= 1.1  # More confident with adaptable agents
        
        return max(0.0, min(base_confidence, 1.0))
    
    def execute_evolution(self, agent, strategy: str, custom_parameters: Optional[Dict[str, Any]] = None) -> EvolutionEvent:
        """Execute evolution strategy on agent"""
        
        # Record pre-evolution state
        pre_performance = {
            "success_rate": agent.evolution_metrics.success_rate,
            "collaboration_score": agent.evolution_metrics.collaboration_score,
            "adaptability_index": agent.evolution_metrics.adaptability_index
        }
        
        # Execute strategy
        try:
            changes = self._apply_evolution_strategy(agent, strategy, custom_parameters)
            success = True
            
            # Update agent
            agent.evolve(changes)
            
        except Exception as e:
            logger.error(f"Evolution failed for agent {agent.agent_id}: {e}")
            changes = {"error": str(e)}
            success = False
        
        # Record post-evolution state
        post_performance = {
            "success_rate": agent.evolution_metrics.success_rate,
            "collaboration_score": agent.evolution_metrics.collaboration_score,
            "adaptability_index": agent.evolution_metrics.adaptability_index
        }
        
        # Create evolution event
        event = EvolutionEvent(
            agent_id=agent.agent_id,
            timestamp=datetime.now(),
            evolution_type=strategy,
            changes=changes,
            performance_before=pre_performance,
            performance_after=post_performance,
            success=success
        )
        
        # Store event
        self._store_evolution_event(event)
        self.evolution_history.append(event)
        
        return event
    
    def _apply_evolution_strategy(self, agent, strategy: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply specific evolution strategy"""
        
        if strategy == "personality_drift":
            return self._apply_personality_drift(agent, custom_params)
        
        elif strategy == "role_specialization":
            return self._apply_role_specialization(agent, custom_params)
        
        elif strategy == "radical_transformation":
            return self._apply_radical_transformation(agent, custom_params)
        
        elif strategy == "collaborative_adaptation":
            return self._apply_collaborative_adaptation(agent, custom_params)
        
        else:
            raise ValueError(f"Unknown evolution strategy: {strategy}")
    
    def _apply_personality_drift(self, agent, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply gradual personality trait adjustments"""
        changes = {"personality_adjustments": {}}
        
        # Identify traits to adjust
        for trait_name, trait in agent.personality_traits.items():
            if agent.evolution_metrics.success_rate < 0.6:
                # Boost helpful traits
                if trait_name in ["adaptable", "collaborative", "analytical"]:
                    new_value = min(trait.value + 0.15, 1.0)
                    changes["personality_adjustments"][trait_name] = new_value
                
                # Moderate risky traits if they're too high
                elif trait_name == "risk_taking" and trait.value > 0.7:
                    new_value = max(trait.value - 0.1, 0.0)
                    changes["personality_adjustments"][trait_name] = new_value
        
        return changes
    
    def _apply_role_specialization(self, agent, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evolve agent towards role specialization"""
        changes = {"personality_adjustments": {}, "role_changes": []}
        
        # Determine specialization direction based on dominant traits
        patterns = self._analyze_agent_patterns(agent)
        
        if "analytical" in patterns["dominant_traits"]:
            changes["personality_adjustments"]["analytical"] = 0.9
            changes["personality_adjustments"]["creative"] = max(agent.personality_traits["creative"].value - 0.1, 0.2)
            changes["role_changes"].append("data_analyst_specialist")
        
        elif "creative" in patterns["dominant_traits"]:
            changes["personality_adjustments"]["creative"] = 0.9
            changes["personality_adjustments"]["analytical"] = max(agent.personality_traits["analytical"].value - 0.1, 0.3)
            changes["role_changes"].append("creative_strategist")
        
        elif "collaborative" in patterns["dominant_traits"]:
            changes["personality_adjustments"]["collaborative"] = 0.9
            changes["personality_adjustments"]["decisive"] = max(agent.personality_traits["decisive"].value - 0.1, 0.4)
            changes["role_changes"].append("team_coordinator")
        
        return changes
    
    def _apply_radical_transformation(self, agent, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply radical transformation to agent"""
        changes = {"personality_adjustments": {}, "radical_changes": ["complete_personality_overhaul"]}
        
        # Invert weak traits and moderate strong ones
        for trait_name, trait in agent.personality_traits.items():
            if trait.value < 0.3:
                # Boost very weak traits significantly
                changes["personality_adjustments"][trait_name] = min(trait.value + 0.5, 0.8)
            elif trait.value > 0.8:
                # Moderate very strong traits
                changes["personality_adjustments"][trait_name] = max(trait.value - 0.3, 0.5)
        
        return changes
    
    def _apply_collaborative_adaptation(self, agent, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Adapt agent for better collaboration"""
        changes = {"personality_adjustments": {}}
        
        # Boost collaboration-related traits
        changes["personality_adjustments"]["collaborative"] = min(agent.personality_traits["collaborative"].value + 0.2, 0.9)
        changes["personality_adjustments"]["adaptable"] = min(agent.personality_traits["adaptable"].value + 0.15, 0.8)
        
        # Moderate traits that might hinder collaboration
        if agent.personality_traits["risk_taking"].value > 0.6:
            changes["personality_adjustments"]["risk_taking"] = max(agent.personality_traits["risk_taking"].value - 0.1, 0.4)
        
        return changes
    
    def _store_evolution_event(self, event: EvolutionEvent):
        """Store evolution event in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO evolution_events 
            (agent_id, timestamp, evolution_type, changes, performance_before, performance_after, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.agent_id,
            event.timestamp.isoformat(),
            event.evolution_type,
            json.dumps(event.changes),
            json.dumps(event.performance_before),
            json.dumps(event.performance_after),
            event.success
        ))
        
        conn.commit()
        conn.close()
    
    def get_evolution_history(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get evolution history for agent or all agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if agent_id:
            cursor.execute(
                "SELECT * FROM evolution_events WHERE agent_id = ? ORDER BY timestamp DESC",
                (agent_id,)
            )
        else:
            cursor.execute("SELECT * FROM evolution_events ORDER BY timestamp DESC")
        
        events = []
        for row in cursor.fetchall():
            events.append({
                "id": row[0],
                "agent_id": row[1],
                "timestamp": row[2],
                "evolution_type": row[3],
                "changes": json.loads(row[4]),
                "performance_before": json.loads(row[5]),
                "performance_after": json.loads(row[6]),
                "success": bool(row[7])
            })
        
        conn.close()
        return events
    
    def get_evolution_statistics(self) -> Dict[str, Any]:
        """Get overall evolution statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM evolution_events")
        total_evolutions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evolution_events WHERE success = 1")
        successful_evolutions = cursor.fetchone()[0]
        
        # Strategy success rates
        strategy_stats = {}
        for strategy in self.evolution_strategies.keys():
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM evolution_events 
                WHERE evolution_type = ?
            """, (strategy,))
            
            result = cursor.fetchone()
            strategy_stats[strategy] = {
                "total": result[0],
                "successful": result[1],
                "success_rate": result[1] / result[0] if result[0] > 0 else 0
            }
        
        conn.close()
        
        return {
            "total_evolutions": total_evolutions,
            "successful_evolutions": successful_evolutions,
            "overall_success_rate": successful_evolutions / total_evolutions if total_evolutions > 0 else 0,
            "strategy_statistics": strategy_stats,
            "active_agents": len(set(event.agent_id for event in self.evolution_history))
        }
    
    def save_agent_memory(self, agent):
        """Save agent memory to persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_memories (agent_id, memory_data, last_updated)
            VALUES (?, ?, ?)
        """, (
            agent.agent_id,
            json.dumps(agent.memory.dict()),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def load_agent_memory(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent memory from persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT memory_data FROM agent_memories WHERE agent_id = ?",
            (agent_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None