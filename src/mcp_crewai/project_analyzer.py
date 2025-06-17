# Project Analysis Agent - Determines Optimal Team Composition
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PersonalityPreset(Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    COLLABORATIVE = "collaborative"
    DECISIVE = "decisive"

class ProjectComplexity(Enum):
    SIMPLE = "simple"        # 1-2 agents
    MODERATE = "moderate"    # 2-4 agents  
    COMPLEX = "complex"      # 3-6 agents
    ENTERPRISE = "enterprise"  # 4-8 agents

class ProjectDomain(Enum):
    SOFTWARE_DEVELOPMENT = "software_development"
    CONTENT_MARKETING = "content_marketing"
    DATA_ANALYSIS = "data_analysis"
    BUSINESS_STRATEGY = "business_strategy"
    CREATIVE_DESIGN = "creative_design"
    RESEARCH = "research"
    OPERATIONS = "operations"
    CUSTOMER_SERVICE = "customer_service"
    GENERAL = "general"

@dataclass
class ProjectAnalysis:
    """Results of project analysis"""
    complexity: ProjectComplexity
    domain: ProjectDomain
    estimated_duration: str
    required_skills: List[str]
    recommended_agent_count: int
    recommended_agents: List[Dict[str, Any]]
    reasoning: str
    confidence_score: float  # 0.0 to 1.0

@dataclass
class AgentRecommendation:
    """Recommendation for a specific agent"""
    role: str
    goal: str
    backstory: str
    personality_preset: PersonalityPreset
    required_skills: List[str]
    priority: int  # 1 = essential, 2 = important, 3 = nice-to-have

class ProjectAnalyzer:
    """
    Intelligent Project Analysis Agent that determines optimal team composition
    """
    
    def __init__(self):
        self.complexity_indicators = {
            # Technical indicators
            "api": 2, "integration": 2, "database": 2, "scalability": 2, "architecture": 2,
            "microservices": 3, "distributed": 3, "enterprise": 3, "security": 3,
            "ai": 2, "machine learning": 2, "blockchain": 2, "cloud": 2,
            
            # Scale indicators  
            "multiple": 1, "various": 1, "several": 1, "many": 1, "numerous": 1,
            "comprehensive": 2, "extensive": 2, "large-scale": 2,
            "complex": 2, "sophisticated": 2, "advanced": 2, "intricate": 2,
            
            # Domain indicators
            "research": 1, "analysis": 1, "strategy": 1, "planning": 1,
            "development": 2, "implementation": 2, "deployment": 2,
            "optimization": 2, "transformation": 2, "migration": 2
        }
        
        self.domain_keywords = {
            ProjectDomain.SOFTWARE_DEVELOPMENT: [
                "code", "development", "programming", "software", "application", 
                "api", "database", "frontend", "backend", "mobile", "web"
            ],
            ProjectDomain.CONTENT_MARKETING: [
                "content", "marketing", "social media", "blog", "copywriting",
                "seo", "campaigns", "branding", "advertising"
            ],
            ProjectDomain.DATA_ANALYSIS: [
                "data", "analytics", "insights", "reporting", "metrics",
                "visualization", "statistics", "machine learning", "ai"
            ],
            ProjectDomain.BUSINESS_STRATEGY: [
                "strategy", "business", "planning", "growth", "market",
                "competitive", "operations", "consulting", "transformation"
            ],
            ProjectDomain.CREATIVE_DESIGN: [
                "design", "creative", "visual", "graphics", "ui", "ux",
                "branding", "artwork", "video", "animation"
            ],
            ProjectDomain.RESEARCH: [
                "research", "investigation", "study", "analysis", "findings",
                "academic", "scientific", "literature", "survey"
            ]
        }
        
        self.role_templates = {
            ProjectDomain.SOFTWARE_DEVELOPMENT: [
                AgentRecommendation(
                    role="Technical Architect",
                    goal="Design robust and scalable technical solutions",
                    backstory="Senior software architect with 10+ years designing enterprise systems",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["system design", "architecture", "technical planning"],
                    priority=1
                ),
                AgentRecommendation(
                    role="Lead Developer", 
                    goal="Implement high-quality software solutions",
                    backstory="Expert developer skilled in multiple programming languages and frameworks",
                    personality_preset=PersonalityPreset.DECISIVE,
                    required_skills=["programming", "development", "debugging"],
                    priority=1
                ),
                AgentRecommendation(
                    role="DevOps Engineer",
                    goal="Ensure smooth deployment and infrastructure management",
                    backstory="DevOps specialist with expertise in CI/CD and cloud platforms",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["deployment", "infrastructure", "automation"],
                    priority=2
                ),
                AgentRecommendation(
                    role="QA Engineer",
                    goal="Ensure software quality and reliability",
                    backstory="Quality assurance expert with comprehensive testing experience",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["testing", "quality assurance", "validation"],
                    priority=2
                )
            ],
            ProjectDomain.CONTENT_MARKETING: [
                AgentRecommendation(
                    role="Content Strategist",
                    goal="Develop comprehensive content strategies that drive engagement",
                    backstory="Marketing strategist with 8+ years in content planning and audience analysis",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["strategy", "audience analysis", "content planning"],
                    priority=1
                ),
                AgentRecommendation(
                    role="Creative Writer",
                    goal="Create compelling and engaging content",
                    backstory="Talented copywriter with expertise in various content formats",
                    personality_preset=PersonalityPreset.CREATIVE,
                    required_skills=["writing", "creativity", "storytelling"],
                    priority=1
                ),
                AgentRecommendation(
                    role="SEO Specialist",
                    goal="Optimize content for search engines and visibility",
                    backstory="SEO expert with deep knowledge of search algorithms and optimization",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["seo", "keyword research", "optimization"],
                    priority=2
                ),
                AgentRecommendation(
                    role="Social Media Manager",
                    goal="Manage social media presence and engagement",
                    backstory="Social media expert with experience across all major platforms",
                    personality_preset=PersonalityPreset.COLLABORATIVE,
                    required_skills=["social media", "community management", "engagement"],
                    priority=2
                )
            ],
            ProjectDomain.DATA_ANALYSIS: [
                AgentRecommendation(
                    role="Data Scientist",
                    goal="Extract insights and patterns from complex datasets",
                    backstory="Data scientist with PhD in statistics and 6+ years industry experience",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["data analysis", "statistics", "machine learning"],
                    priority=1
                ),
                AgentRecommendation(
                    role="Data Engineer",
                    goal="Build and maintain data infrastructure and pipelines",
                    backstory="Data engineering specialist with expertise in ETL and data architecture",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["data engineering", "etl", "databases"],
                    priority=2
                ),
                AgentRecommendation(
                    role="Business Analyst",
                    goal="Translate data insights into business recommendations",
                    backstory="Business analyst with strong background in translating data to business value",
                    personality_preset=PersonalityPreset.COLLABORATIVE,
                    required_skills=["business analysis", "reporting", "communication"],
                    priority=1
                )
            ],
            ProjectDomain.BUSINESS_STRATEGY: [
                AgentRecommendation(
                    role="Strategy Consultant",
                    goal="Develop comprehensive business strategies and recommendations",
                    backstory="Senior strategy consultant with MBA and 12+ years experience",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["strategic planning", "market analysis", "consulting"],
                    priority=1
                ),
                AgentRecommendation(
                    role="Market Researcher",
                    goal="Conduct thorough market research and competitive analysis",
                    backstory="Market research specialist with expertise in industry analysis",
                    personality_preset=PersonalityPreset.ANALYTICAL,
                    required_skills=["market research", "competitive analysis", "data collection"],
                    priority=2
                ),
                AgentRecommendation(
                    role="Business Development Manager",
                    goal="Identify growth opportunities and partnership strategies",
                    backstory="Business development expert with proven track record in growth initiatives",
                    personality_preset=PersonalityPreset.DECISIVE,
                    required_skills=["business development", "partnerships", "growth strategy"],
                    priority=2
                )
            ]
        }

    async def analyze_project(self, project_description: str, 
                            project_goals: List[str] = None,
                            constraints: Dict[str, Any] = None) -> ProjectAnalysis:
        """
        Analyze project requirements and determine optimal team composition
        
        Args:
            project_description: Detailed description of the project
            project_goals: List of specific project goals (optional)
            constraints: Any constraints like budget, timeline, team size limits
            
        Returns:
            ProjectAnalysis with recommended team composition
        """
        logger.info(f"Analyzing project: {project_description[:100]}...")
        
        # Analyze project complexity
        complexity = self._assess_complexity(project_description, project_goals)
        
        # Determine project domain
        domain = self._identify_domain(project_description, project_goals)
        
        # Extract required skills
        required_skills = self._extract_required_skills(project_description, project_goals, domain)
        
        # Determine optimal agent count based on complexity and domain
        agent_count = self._calculate_optimal_agent_count(complexity, domain, constraints)
        
        # Generate agent recommendations
        recommended_agents = self._recommend_agents(domain, required_skills, agent_count, complexity)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(project_description, domain, complexity)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(complexity, domain, agent_count, required_skills)
        
        analysis = ProjectAnalysis(
            complexity=complexity,
            domain=domain,
            estimated_duration=self._estimate_duration(complexity, agent_count),
            required_skills=required_skills,
            recommended_agent_count=agent_count,
            recommended_agents=recommended_agents,
            reasoning=reasoning,
            confidence_score=confidence
        )
        
        logger.info(f"Analysis complete: {agent_count} agents recommended for {complexity.value} {domain.value} project")
        return analysis

    def _assess_complexity(self, description: str, goals: List[str] = None) -> ProjectComplexity:
        """Assess project complexity based on description and goals"""
        text = description.lower()
        if goals:
            text += " " + " ".join(goals).lower()
        
        complexity_score = 0
        word_count = len(text.split())
        
        # Base complexity from length
        if word_count > 200:
            complexity_score += 2
        elif word_count > 100:
            complexity_score += 1
            
        # Keyword-based complexity scoring
        for keyword, score in self.complexity_indicators.items():
            if keyword in text:
                complexity_score += score
        
        # Determine complexity level
        if complexity_score >= 10:
            return ProjectComplexity.ENTERPRISE
        elif complexity_score >= 6:
            return ProjectComplexity.COMPLEX
        elif complexity_score >= 3:
            return ProjectComplexity.MODERATE
        else:
            return ProjectComplexity.SIMPLE

    def _identify_domain(self, description: str, goals: List[str] = None) -> ProjectDomain:
        """Identify the primary project domain"""
        text = description.lower()
        if goals:
            text += " " + " ".join(goals).lower()
        
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += text.count(keyword)
            domain_scores[domain] = score
        
        # Return domain with highest score, or GENERAL if no clear match
        best_domain = max(domain_scores, key=domain_scores.get)
        return best_domain if domain_scores[best_domain] > 0 else ProjectDomain.GENERAL

    def _extract_required_skills(self, description: str, goals: List[str], domain: ProjectDomain) -> List[str]:
        """Extract required skills from project description"""
        text = description.lower()
        if goals:
            text += " " + " ".join(goals).lower()
        
        skills = set()
        
        # Domain-specific skill extraction
        skill_keywords = {
            "programming": ["code", "development", "programming", "software"],
            "design": ["design", "ui", "ux", "visual", "graphics"],
            "analysis": ["analysis", "data", "research", "insights"],
            "writing": ["content", "writing", "copywriting", "blog"],
            "strategy": ["strategy", "planning", "business", "consulting"],
            "marketing": ["marketing", "seo", "social", "campaigns"],
            "project management": ["management", "coordination", "planning", "timeline"],
            "testing": ["testing", "qa", "quality", "validation"],
            "deployment": ["deployment", "devops", "infrastructure", "cloud"]
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in text for keyword in keywords):
                skills.add(skill)
        
        return list(skills)

    def _calculate_optimal_agent_count(self, complexity: ProjectComplexity, 
                                     domain: ProjectDomain, 
                                     constraints: Dict[str, Any] = None) -> int:
        """Calculate optimal number of agents needed"""
        base_counts = {
            ProjectComplexity.SIMPLE: 2,
            ProjectComplexity.MODERATE: 3,
            ProjectComplexity.COMPLEX: 5,
            ProjectComplexity.ENTERPRISE: 7
        }
        
        agent_count = base_counts[complexity]
        
        # Domain-specific adjustments
        domain_adjustments = {
            ProjectDomain.SOFTWARE_DEVELOPMENT: 1,  # Often needs multiple specialists
            ProjectDomain.DATA_ANALYSIS: 0,         # Can be done with fewer agents
            ProjectDomain.CONTENT_MARKETING: 0,     # Standard team size
            ProjectDomain.BUSINESS_STRATEGY: -1,    # Often requires fewer, senior agents
            ProjectDomain.CREATIVE_DESIGN: 0        # Standard team size
        }
        
        agent_count += domain_adjustments.get(domain, 0)
        
        # Apply constraints
        if constraints:
            max_agents = constraints.get('max_agents', 10)
            min_agents = constraints.get('min_agents', 1)
            agent_count = max(min_agents, min(agent_count, max_agents))
        
        return max(1, min(agent_count, 10))  # Enforce system limits

    def _recommend_agents(self, domain: ProjectDomain, required_skills: List[str], 
                         agent_count: int, complexity: ProjectComplexity) -> List[Dict[str, Any]]:
        """Generate specific agent recommendations"""
        recommendations = []
        
        # Get domain-specific templates
        templates = self.role_templates.get(domain, [])
        
        if not templates:
            # Generate generic agents for unknown domains
            return self._generate_generic_agents(agent_count, required_skills)
        
        # Sort by priority and select best fit
        templates.sort(key=lambda x: x.priority)
        
        selected_agents = []
        used_roles = set()
        
        # First, add essential agents (priority 1)
        for template in templates:
            if template.priority == 1 and len(selected_agents) < agent_count:
                if template.role not in used_roles:
                    selected_agents.append(template)
                    used_roles.add(template.role)
        
        # Then add important agents (priority 2) if we have space
        for template in templates:
            if template.priority == 2 and len(selected_agents) < agent_count:
                if template.role not in used_roles:
                    selected_agents.append(template)
                    used_roles.add(template.role)
        
        # Convert to dict format
        for agent in selected_agents:
            recommendations.append({
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "personality_preset": agent.personality_preset.value,
                "required_skills": agent.required_skills,
                "priority": agent.priority
            })
        
        # Fill remaining slots with generic agents if needed
        while len(recommendations) < agent_count:
            generic_role = f"Specialist_{len(recommendations) + 1}"
            recommendations.append({
                "role": generic_role,
                "goal": f"Provide specialized expertise for project requirements",
                "backstory": f"Experienced professional with domain expertise",
                "personality_preset": PersonalityPreset.COLLABORATIVE.value,
                "required_skills": required_skills[:3] if required_skills else ["general"],
                "priority": 3
            })
        
        return recommendations[:agent_count]

    def _generate_generic_agents(self, agent_count: int, required_skills: List[str]) -> List[Dict[str, Any]]:
        """Generate generic agents when domain is unknown"""
        agents = []
        
        base_roles = [
            ("Project Lead", PersonalityPreset.DECISIVE, "Lead project execution and coordinate team efforts"),
            ("Analyst", PersonalityPreset.ANALYTICAL, "Analyze requirements and provide insights"),
            ("Specialist", PersonalityPreset.COLLABORATIVE, "Provide specialized expertise"),
            ("Coordinator", PersonalityPreset.COLLABORATIVE, "Coordinate tasks and communication")
        ]
        
        for i in range(agent_count):
            role_info = base_roles[i % len(base_roles)]
            role_name = f"{role_info[0]}_{i+1}" if i >= len(base_roles) else role_info[0]
            
            agents.append({
                "role": role_name,
                "goal": role_info[2],
                "backstory": f"Experienced professional with expertise in project requirements",
                "personality_preset": role_info[1].value,
                "required_skills": required_skills[:3] if required_skills else ["general"],
                "priority": 1 if i < 2 else 2
            })
        
        return agents

    def _calculate_confidence(self, description: str, domain: ProjectDomain, 
                            complexity: ProjectComplexity) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.7  # Base confidence
        
        # Increase confidence for longer, more detailed descriptions
        word_count = len(description.split())
        if word_count > 100:
            confidence += 0.1
        if word_count > 200:
            confidence += 0.1
        
        # Increase confidence for known domains
        if domain != ProjectDomain.GENERAL:
            confidence += 0.1
        
        # Slight penalty for very complex projects (more uncertainty)
        if complexity == ProjectComplexity.ENTERPRISE:
            confidence -= 0.05
        
        return min(1.0, confidence)

    def _generate_reasoning(self, complexity: ProjectComplexity, domain: ProjectDomain,
                          agent_count: int, required_skills: List[str]) -> str:
        """Generate human-readable reasoning for the recommendations"""
        reasoning = f"Based on the project analysis, this appears to be a {complexity.value} "
        reasoning += f"{domain.value.replace('_', ' ')} project. "
        
        reasoning += f"The recommended team of {agent_count} agents provides the optimal balance "
        reasoning += f"of skills and coordination for this complexity level. "
        
        if required_skills:
            reasoning += f"Key skills identified include: {', '.join(required_skills[:5])}. "
        
        reasoning += f"This team composition ensures efficient task distribution while maintaining "
        reasoning += f"effective communication and collaboration."
        
        return reasoning

    def _estimate_duration(self, complexity: ProjectComplexity, agent_count: int) -> str:
        """Estimate project duration based on complexity and team size"""
        base_durations = {
            ProjectComplexity.SIMPLE: "1-2 weeks",
            ProjectComplexity.MODERATE: "3-6 weeks", 
            ProjectComplexity.COMPLEX: "2-4 months",
            ProjectComplexity.ENTERPRISE: "4-12 months"
        }
        
        return base_durations[complexity]

# Factory function for creating project analyzer
def create_project_analyzer() -> ProjectAnalyzer:
    """Create and return a ProjectAnalyzer instance"""
    return ProjectAnalyzer()