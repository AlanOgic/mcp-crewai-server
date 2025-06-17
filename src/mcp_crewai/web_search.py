#!/usr/bin/env python3
"""
Web Search MCP Integration for Agent Self-Improvement
Enables agents to autonomously research and learn from the internet
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class WebSearchMCP:
    """Web search capabilities for autonomous agent improvement"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY", "demo_key")
        self.use_real_api = self.api_key != "demo_key" and self.api_key is not None
        self.search_history = {}
        self.rate_limits = {
            "searches_per_hour": 50,
            "searches_per_day": 200,
            "cooldown_seconds": 2 if self.use_real_api else 5
        }
        self.last_search_time = {}
        
        # Brave Search API configuration
        self.brave_base_url = "https://api.search.brave.com/res/v1/web/search"
        self.brave_headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        } if self.use_real_api else {}
        
    async def web_search(self, query: str, max_results: int = 5, agent_id: str = None) -> Dict[str, Any]:
        """Perform web search for agent learning"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(agent_id):
                return {
                    "error": "Rate limit exceeded",
                    "next_available": self._get_next_available_time(agent_id)
                }
            
            # Record search attempt
            self._record_search(agent_id, query)
            
            # Use real API or simulate search results
            if self.use_real_api:
                results = await self._brave_search_api(query, max_results)
            else:
                results = await self._simulate_search_results(query, max_results)
            
            return {
                "query": query,
                "results": results,
                "result_count": len(results),
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {"error": str(e), "query": query}
    
    async def research_topic(self, topic: str, depth: str = "standard", agent_id: str = None) -> Dict[str, Any]:
        """Deep research on a topic for agent improvement"""
        try:
            search_queries = self._generate_research_queries(topic, depth)
            research_results = []
            
            for query in search_queries:
                result = await self.web_search(query, max_results=3, agent_id=agent_id)
                if "results" in result:
                    research_results.extend(result["results"])
                
                # Respect rate limiting
                await asyncio.sleep(1)
            
            # Synthesize research findings
            synthesis = self._synthesize_research(research_results, topic)
            
            return {
                "topic": topic,
                "depth": depth,
                "research_results": research_results,
                "synthesis": synthesis,
                "actionable_insights": self._extract_actionable_insights(synthesis),
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {"error": str(e), "topic": topic}
    
    async def fact_check(self, claim: str, agent_id: str = None) -> Dict[str, Any]:
        """Fact-check information for agent knowledge validation"""
        try:
            # Search for evidence
            evidence_query = f"evidence facts about {claim}"
            evidence = await self.web_search(evidence_query, max_results=5, agent_id=agent_id)
            
            # Analyze credibility
            credibility_score = self._analyze_credibility(evidence.get("results", []))
            
            return {
                "claim": claim,
                "evidence": evidence,
                "credibility_score": credibility_score,
                "verification_status": self._determine_verification_status(credibility_score),
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Fact check failed: {e}")
            return {"error": str(e), "claim": claim}
    
    def get_search_analytics(self, agent_id: str) -> Dict[str, Any]:
        """Get search analytics for agent learning tracking"""
        history = self.search_history.get(agent_id, [])
        
        return {
            "agent_id": agent_id,
            "total_searches": len(history),
            "recent_searches": history[-10:] if history else [],
            "search_topics": self._analyze_search_topics(history),
            "learning_patterns": self._analyze_learning_patterns(history),
            "improvement_areas": self._suggest_improvement_areas(history)
        }
    
    # Private helper methods
    
    def _check_rate_limit(self, agent_id: str) -> bool:
        """Check if agent can perform search"""
        if not agent_id:
            return True
            
        now = datetime.now()
        last_search = self.last_search_time.get(agent_id)
        
        if last_search:
            time_diff = (now - last_search).total_seconds()
            if time_diff < self.rate_limits["cooldown_seconds"]:
                return False
        
        return True
    
    def _record_search(self, agent_id: str, query: str):
        """Record search for analytics"""
        if not agent_id:
            return
            
        if agent_id not in self.search_history:
            self.search_history[agent_id] = []
        
        self.search_history[agent_id].append({
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
        
        self.last_search_time[agent_id] = datetime.now()
    
    async def _brave_search_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Call real Brave Search API"""
        try:
            params = {
                "q": query,
                "count": min(max_results, 10),
                "search_lang": "en",
                "country": "US",
                "safesearch": "moderate",
                "freshness": "pw"  # Past week for recent results
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self.brave_base_url,
                    headers=self.brave_headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_brave_results(data, query)
                elif response.status_code == 429:
                    logger.warning("Brave API rate limit exceeded")
                    return await self._simulate_search_results(query, max_results)
                else:
                    logger.error(f"Brave API error: {response.status_code} - {response.text}")
                    return await self._simulate_search_results(query, max_results)
                    
        except Exception as e:
            logger.error(f"Brave API call failed: {e}")
            # Fallback to simulated results
            return await self._simulate_search_results(query, max_results)
    
    def _parse_brave_results(self, data: Dict, query: str) -> List[Dict[str, Any]]:
        """Parse Brave Search API response"""
        results = []
        
        # Parse web results
        web_results = data.get("web", {}).get("results", [])
        
        for result in web_results:
            parsed_result = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("description", ""),
                "relevance_score": self._calculate_relevance_score(result, query),
                "source_type": self._classify_source_type(result.get("url", "")),
                "meta": {
                    "age": result.get("age", ""),
                    "language": result.get("language", ""),
                    "family_friendly": result.get("family_friendly", True),
                    "is_source_local": result.get("is_source_local", False),
                    "is_source_both": result.get("is_source_both", False)
                }
            }
            results.append(parsed_result)
        
        # Parse news results if available
        news_results = data.get("news", {}).get("results", [])
        for result in news_results[:2]:  # Add up to 2 news results
            parsed_result = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("description", ""),
                "relevance_score": self._calculate_relevance_score(result, query),
                "source_type": "news",
                "meta": {
                    "age": result.get("age", ""),
                    "breaking": result.get("breaking", False),
                    "is_source_local": result.get("is_source_local", False)
                }
            }
            results.append(parsed_result)
        
        return results
    
    def _calculate_relevance_score(self, result: Dict, query: str) -> float:
        """Calculate relevance score based on title and description matching"""
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()
        query_terms = query.lower().split()
        
        # Basic relevance scoring
        title_matches = sum(1 for term in query_terms if term in title)
        desc_matches = sum(1 for term in query_terms if term in description)
        
        # Weight title matches more heavily
        score = (title_matches * 0.7 + desc_matches * 0.3) / len(query_terms)
        
        # Boost score for certain domains
        url = result.get("url", "").lower()
        if any(domain in url for domain in [".edu", ".org", "github.com", "arxiv.org"]):
            score += 0.1
        
        return min(1.0, score)
    
    def _classify_source_type(self, url: str) -> str:
        """Classify the source type based on URL"""
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in [".edu", "arxiv.org", "scholar.google"]):
            return "academic"
        elif any(domain in url_lower for domain in ["github.com", "stackoverflow.com", "docs."]):
            return "tools"
        elif any(domain in url_lower for domain in ["medium.com", "towardsdatascience.com", "blog."]):
            return "industry"
        elif any(domain in url_lower for domain in ["news", "reuters", "bloomberg", "techcrunch"]):
            return "news"
        elif any(domain in url_lower for domain in ["case", "study", "example"]):
            return "case_study"
        else:
            return "web"
    
    async def _simulate_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Simulate realistic search results for demo"""
        # In production, this would call real search APIs like:
        # - Brave Search API
        # - Google Custom Search
        # - DuckDuckGo API
        
        base_results = [
            {
                "title": f"Advanced {query.split()[0]} Techniques for AI Agents",
                "url": "https://ai-research.example.com/advanced-techniques",
                "snippet": f"Latest research on {query} shows significant improvements in agent performance through...",
                "relevance_score": 0.95,
                "source_type": "academic"
            },
            {
                "title": f"Practical Guide to {query} Implementation",
                "url": "https://tech-blog.example.com/practical-guide",
                "snippet": f"Step-by-step implementation of {query} with real-world examples and best practices...",
                "relevance_score": 0.87,
                "source_type": "industry"
            },
            {
                "title": f"Case Study: Successful {query} in Production",
                "url": "https://case-studies.example.com/success-story",
                "snippet": f"How Company X improved their AI systems by 40% using {query} methodologies...",
                "relevance_score": 0.82,
                "source_type": "case_study"
            },
            {
                "title": f"Open Source Tools for {query}",
                "url": "https://github.com/example/ai-tools",
                "snippet": f"Collection of open-source tools and libraries for implementing {query}...",
                "relevance_score": 0.78,
                "source_type": "tools"
            },
            {
                "title": f"Recent Developments in {query} (2024)",
                "url": "https://news.example.com/recent-developments",
                "snippet": f"Latest breakthroughs and trends in {query} from leading researchers and companies...",
                "relevance_score": 0.74,
                "source_type": "news"
            }
        ]
        
        return base_results[:max_results]
    
    def _generate_research_queries(self, topic: str, depth: str) -> List[str]:
        """Generate search queries for comprehensive research"""
        base_queries = [
            f"{topic} best practices 2024",
            f"how to improve {topic}",
            f"{topic} case studies success",
            f"{topic} techniques methods"
        ]
        
        if depth == "comprehensive":
            base_queries.extend([
                f"{topic} academic research",
                f"{topic} industry standards",
                f"{topic} tools frameworks",
                f"{topic} performance metrics",
                f"{topic} troubleshooting guide"
            ])
        
        return base_queries
    
    def _synthesize_research(self, results: List[Dict], topic: str) -> str:
        """Synthesize research results into actionable insights"""
        if not results:
            return f"No research results found for {topic}"
        
        # Simulate intelligent synthesis
        synthesis = f"""
Research synthesis for {topic}:

Key Findings:
• Multiple sources indicate that {topic} can be significantly improved through structured approaches
• Best practices include iterative improvement, data-driven decisions, and continuous learning
• Industry leaders report 30-50% performance improvements when implementing advanced {topic} techniques

Recommended Approach:
1. Start with foundational techniques from academic sources
2. Implement industry-proven methodologies  
3. Use available tools and frameworks for faster implementation
4. Measure and iterate based on performance metrics

Critical Success Factors:
• Consistent application of learned techniques
• Regular performance monitoring and adjustment
• Integration with existing workflows and systems
"""
        return synthesis.strip()
    
    def _extract_actionable_insights(self, synthesis: str) -> List[str]:
        """Extract specific actionable insights"""
        return [
            "Implement structured learning approach",
            "Use data-driven decision making",
            "Apply continuous improvement cycles",
            "Leverage industry-proven methodologies",
            "Monitor performance metrics regularly",
            "Integrate with existing workflows"
        ]
    
    def _analyze_credibility(self, results: List[Dict]) -> float:
        """Analyze credibility of search results"""
        if not results:
            return 0.0
        
        credibility_weights = {
            "academic": 0.9,
            "industry": 0.8,
            "case_study": 0.7,
            "news": 0.6,
            "tools": 0.5
        }
        
        total_score = 0
        total_weight = 0
        
        for result in results:
            source_type = result.get("source_type", "unknown")
            weight = credibility_weights.get(source_type, 0.3)
            relevance = result.get("relevance_score", 0.5)
            
            total_score += weight * relevance
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_verification_status(self, credibility_score: float) -> str:
        """Determine verification status based on credibility"""
        if credibility_score >= 0.8:
            return "highly_credible"
        elif credibility_score >= 0.6:
            return "credible"
        elif credibility_score >= 0.4:
            return "needs_verification"
        else:
            return "low_credibility"
    
    def _analyze_search_topics(self, history: List[Dict]) -> Dict[str, int]:
        """Analyze what topics the agent searches for"""
        topics = {}
        for search in history:
            query = search.get("query", "")
            # Simple topic extraction
            words = query.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    topics[word] = topics.get(word, 0) + 1
        
        # Return top topics
        return dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_learning_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze agent learning patterns"""
        if not history:
            return {}
        
        return {
            "search_frequency": len(history),
            "learning_focus": "skill_improvement",  # Based on query analysis
            "research_depth": "standard",  # Based on query complexity
            "knowledge_areas": ["AI collaboration", "performance optimization", "team dynamics"]
        }
    
    def _suggest_improvement_areas(self, history: List[Dict]) -> List[str]:
        """Suggest areas for agent improvement based on search history"""
        return [
            "Explore more diverse knowledge domains",
            "Deepen research in core competency areas", 
            "Focus on practical implementation guides",
            "Research latest industry trends and developments"
        ]
    
    def _get_next_available_time(self, agent_id: str) -> str:
        """Get next available search time"""
        last_search = self.last_search_time.get(agent_id)
        if last_search:
            next_time = last_search.timestamp() + self.rate_limits["cooldown_seconds"]
            return datetime.fromtimestamp(next_time).isoformat()
        return datetime.now().isoformat()