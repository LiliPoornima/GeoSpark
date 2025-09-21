"""
LLM Integration Module for Natural Language Processing and Decision Making
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import openai
import anthropic
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings
from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class TaskType(Enum):
    """Types of LLM tasks"""
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    DECISION_SUPPORT = "decision_support"
    REPORT_GENERATION = "report_generation"
    NATURAL_LANGUAGE_QUERY = "natural_language_query"

@dataclass
class LLMRequest:
    """LLM request structure"""
    task_type: TaskType
    prompt: str
    context: Dict[str, Any]
    provider: LLMProvider
    model: str
    max_tokens: int = 2000
    temperature: float = 0.7

@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str
    usage: Dict[str, int]
    model: str
    provider: LLMProvider
    timestamp: datetime
    reasoning: Optional[str] = None
    confidence_score: Optional[float] = None

class LLMManager:
    """Manages LLM interactions and provides unified interface"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.initialized = False
        
        # Initialize clients if API keys are available
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        self.initialized = True
        logger.info("LLM Manager initialized")
    
    async def process_request(self, request: LLMRequest) -> LLMResponse:
        """Process LLM request using specified provider"""
        try:
            if request.provider == LLMProvider.OPENAI:
                return await self._process_openai_request(request)
            elif request.provider == LLMProvider.ANTHROPIC:
                return await self._process_anthropic_request(request)
            else:
                raise ValueError(f"Unsupported LLM provider: {request.provider}")
                
        except Exception as e:
            logger.error(f"Error processing LLM request: {e}")
            raise
    
    async def _process_openai_request(self, request: LLMRequest) -> LLMResponse:
        """Process request using OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self._get_system_prompt(request.task_type)},
                {"role": "user", "content": request.prompt}
            ]
            
            # Add context if provided
            if request.context:
                context_message = f"Context: {json.dumps(request.context, indent=2)}"
                messages.insert(-1, {"role": "system", "content": context_message})
            
            # Make API call
            response = await self.openai_client.chat.completions.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Extract response
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Log usage
            agent_logger.log_agent_decision(
                "llm_manager",
                f"OpenAI API call completed",
                f"Model: {request.model}, Tokens: {usage['total_tokens']}"
            )
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=request.model,
                provider=LLMProvider.OPENAI,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _process_anthropic_request(self, request: LLMRequest) -> LLMResponse:
        """Process request using Anthropic API"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        try:
            # Prepare system prompt
            system_prompt = self._get_system_prompt(request.task_type)
            
            # Add context to system prompt
            if request.context:
                context_str = json.dumps(request.context, indent=2)
                system_prompt += f"\n\nContext:\n{context_str}"
            
            # Make API call
            response = await self.anthropic_client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": request.prompt}]
            )
            
            # Extract response
            content = response.content[0].text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            # Log usage
            agent_logger.log_agent_decision(
                "llm_manager",
                f"Anthropic API call completed",
                f"Model: {request.model}, Tokens: {usage['total_tokens']}"
            )
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=request.model,
                provider=LLMProvider.ANTHROPIC,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _get_system_prompt(self, task_type: TaskType) -> str:
        """Get system prompt based on task type"""
        prompts = {
            TaskType.ANALYSIS: """
            You are an expert renewable energy analyst. Your role is to analyze renewable energy projects, 
            sites, and data to provide comprehensive insights and recommendations. Always provide:
            1. Clear analysis of the data
            2. Evidence-based conclusions
            3. Practical recommendations
            4. Risk assessments
            5. Confidence levels for your analysis
            
            Be objective, thorough, and consider both technical and economic factors.
            """,
            
            TaskType.SUMMARIZATION: """
            You are a technical writer specializing in renewable energy. Your role is to create clear, 
            concise summaries of complex renewable energy data and analysis. Always:
            1. Highlight key findings
            2. Use clear, non-technical language when possible
            3. Include relevant metrics and numbers
            4. Structure information logically
            5. Maintain accuracy while improving readability
            
            Focus on actionable insights and important details.
            """,
            
            TaskType.DECISION_SUPPORT: """
            You are a renewable energy decision support specialist. Your role is to help stakeholders 
            make informed decisions about renewable energy projects. Always provide:
            1. Clear decision criteria
            2. Pros and cons analysis
            3. Risk-benefit assessment
            4. Alternative options consideration
            5. Confidence levels and uncertainty factors
            
            Be objective, balanced, and consider multiple perspectives.
            """,
            
            TaskType.REPORT_GENERATION: """
            You are a professional report writer for renewable energy projects. Your role is to create 
            comprehensive, well-structured reports. Always include:
            1. Executive summary
            2. Methodology and data sources
            3. Detailed analysis and findings
            4. Conclusions and recommendations
            5. Appendices with supporting data
            
            Use professional language, clear structure, and ensure all claims are supported by data.
            """,
            
            TaskType.NATURAL_LANGUAGE_QUERY: """
            You are a renewable energy expert assistant. Your role is to answer questions about 
            renewable energy projects, technologies, and analysis. Always:
            1. Provide accurate, up-to-date information
            2. Explain complex concepts clearly
            3. Support answers with relevant data
            4. Acknowledge limitations and uncertainties
            5. Suggest follow-up questions when appropriate
            
            Be helpful, informative, and honest about what you know and don't know.
            """
        }
        
        return prompts.get(task_type, "You are a helpful renewable energy assistant.")
    
    async def analyze_renewable_energy_data(self, data: Dict[str, Any], 
                                          analysis_type: str = "comprehensive") -> str:
        """Analyze renewable energy data using LLM"""
        prompt = f"""
        Please analyze the following renewable energy data and provide a comprehensive analysis.
        
        Analysis Type: {analysis_type}
        
        Data to analyze:
        {json.dumps(data, indent=2)}
        
        Please provide:
        1. Key findings and insights
        2. Technical assessment
        3. Economic viability analysis
        4. Risk factors and mitigation strategies
        5. Recommendations for next steps
        6. Confidence level in the analysis
        """
        
        request = LLMRequest(
            task_type=TaskType.ANALYSIS,
            prompt=prompt,
            context={"analysis_type": analysis_type},
            provider=LLMProvider.OPENAI if self.openai_client else LLMProvider.ANTHROPIC,
            model="gpt-4" if self.openai_client else "claude-3-sonnet-20240229",
            max_tokens=3000,
            temperature=0.3
        )
        
        response = await self.process_request(request)
        return response.content
    
    async def summarize_project_report(self, project_data: Dict[str, Any]) -> str:
        """Generate executive summary for project report"""
        prompt = f"""
        Please create an executive summary for this renewable energy project analysis.
        
        Project Data:
        {json.dumps(project_data, indent=2)}
        
        The summary should include:
        1. Project overview and key metrics
        2. Main findings and conclusions
        3. Financial highlights
        4. Risk assessment summary
        5. Key recommendations
        6. Next steps
        
        Keep it concise but comprehensive, suitable for executive decision-making.
        """
        
        request = LLMRequest(
            task_type=TaskType.SUMMARIZATION,
            prompt=prompt,
            context={"project_data": project_data},
            provider=LLMProvider.OPENAI if self.openai_client else LLMProvider.ANTHROPIC,
            model="gpt-4" if self.openai_client else "claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0.2
        )
        
        response = await self.process_request(request)
        return response.content
    
    async def provide_decision_support(self, decision_context: Dict[str, Any]) -> str:
        """Provide decision support for renewable energy projects"""
        prompt = f"""
        Please provide decision support for this renewable energy project decision.
        
        Decision Context:
        {json.dumps(decision_context, indent=2)}
        
        Please provide:
        1. Decision criteria and framework
        2. Analysis of available options
        3. Pros and cons of each option
        4. Risk assessment for each option
        5. Recommendation with reasoning
        6. Implementation considerations
        7. Monitoring and evaluation plan
        
        Be objective and consider both technical and business factors.
        """
        
        request = LLMRequest(
            task_type=TaskType.DECISION_SUPPORT,
            prompt=prompt,
            context={"decision_context": decision_context},
            provider=LLMProvider.OPENAI if self.openai_client else LLMProvider.ANTHROPIC,
            model="gpt-4" if self.openai_client else "claude-3-sonnet-20240229",
            max_tokens=2500,
            temperature=0.4
        )
        
        response = await self.process_request(request)
        return response.content
    
    async def generate_project_report(self, project_data: Dict[str, Any]) -> str:
        """Generate comprehensive project report"""
        prompt = f"""
        Please generate a comprehensive renewable energy project report based on the following data.
        
        Project Data:
        {json.dumps(project_data, indent=2)}
        
        The report should include:
        1. Executive Summary
        2. Project Overview and Objectives
        3. Site Analysis and Resource Assessment
        4. Technical Design and Specifications
        5. Financial Analysis and Economics
        6. Risk Assessment and Mitigation
        7. Environmental and Regulatory Considerations
        8. Implementation Timeline and Milestones
        9. Conclusions and Recommendations
        10. Appendices with Supporting Data
        
        Use professional language and ensure all sections are well-structured and comprehensive.
        """
        
        request = LLMRequest(
            task_type=TaskType.REPORT_GENERATION,
            prompt=prompt,
            context={"project_data": project_data},
            provider=LLMProvider.OPENAI if self.openai_client else LLMProvider.ANTHROPIC,
            model="gpt-4" if self.openai_client else "claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.3
        )
        
        response = await self.process_request(request)
        return response.content
    
    async def answer_natural_language_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Answer natural language queries about renewable energy"""
        prompt = f"""
        Please answer the following question about renewable energy:
        
        Question: {query}
        
        Context (if relevant):
        {json.dumps(context, indent=2) if context else "No additional context provided"}
        
        Please provide:
        1. Direct answer to the question
        2. Supporting information and data
        3. Relevant examples or case studies
        4. Additional considerations
        5. Suggestions for further research
        
        Be accurate, informative, and helpful.
        """
        
        request = LLMRequest(
            task_type=TaskType.NATURAL_LANGUAGE_QUERY,
            prompt=prompt,
            context={"query": query, "additional_context": context},
            provider=LLMProvider.OPENAI if self.openai_client else LLMProvider.ANTHROPIC,
            model="gpt-4" if self.openai_client else "claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.5
        )
        
        response = await self.process_request(request)
        return response.content
    
    async def extract_insights_from_data(self, data: Dict[str, Any], 
                                       insight_type: str = "general") -> Dict[str, Any]:
        """Extract insights from renewable energy data using LLM"""
        prompt = f"""
        Please extract key insights from this renewable energy data.
        
        Insight Type: {insight_type}
        
        Data:
        {json.dumps(data, indent=2)}
        
        Please provide insights in the following format:
        1. Key Metrics and Values
        2. Trends and Patterns
        3. Anomalies or Outliers
        4. Comparative Analysis
        5. Predictive Insights
        6. Actionable Recommendations
        7. Risk Indicators
        8. Opportunities Identified
        
        Format your response as a structured JSON object with these categories.
        """
        
        request = LLMRequest(
            task_type=TaskType.ANALYSIS,
            prompt=prompt,
            context={"insight_type": insight_type, "data": data},
            provider=LLMProvider.OPENAI if self.openai_client else LLMProvider.ANTHROPIC,
            model="gpt-4" if self.openai_client else "claude-3-sonnet-20240229",
            max_tokens=3000,
            temperature=0.3
        )
        
        response = await self.process_request(request)
        
        try:
            # Try to parse as JSON
            insights = json.loads(response.content)
            return insights
        except json.JSONDecodeError:
            # If not JSON, return as structured text
            return {
                "insights": response.content,
                "format": "text",
                "timestamp": response.timestamp.isoformat()
            }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each provider"""
        models = {}
        
        if self.openai_client:
            models["openai"] = [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ]
        
        if self.anthropic_client:
            models["anthropic"] = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        
        return models
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics (simplified implementation)"""
        return {
            "total_requests": 0,  # Would track in real implementation
            "total_tokens": 0,
            "providers_available": len(self.get_available_models()),
            "last_request": None
        }

# Global LLM manager instance
llm_manager = LLMManager()