"""
LangSmith Integration Service
Provides comprehensive observability, evaluation, and traceability for Financial Investment Advisor Agent
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from functools import wraps
import asyncio

from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai
from langsmith.evaluation import evaluate, EvaluationResult
from langchain.callbacks.tracers import LangChainTracer
from langchain_core.tracers.context import tracing_v2_enabled
from openai import OpenAI
from pydantic import BaseModel, Field
import re

# Configure logging
logger = logging.getLogger(__name__)

class LangSmithConfig(BaseModel):
    """Configuration for LangSmith integration"""
    api_key: str
    project_name: str = "financial-advisor-agent"
    endpoint: str = "https://api.smith.langchain.com"
    tracing_enabled: bool = True
    evaluation_enabled: bool = True
    sample_rate: float = 1.0
    session_name: str = "faa-session"
    sanitize_pii: bool = True
    track_performance: bool = True
    auto_eval_threshold: float = 0.8

class FinancialAdviceEvaluator(BaseModel):
    """Evaluation criteria for financial advice quality"""
    accuracy_score: float = Field(ge=0.0, le=1.0, description="Factual accuracy of financial information")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance to user's financial situation")
    safety_score: float = Field(ge=0.0, le=1.0, description="Safety and appropriateness of advice")
    completeness_score: float = Field(ge=0.0, le=1.0, description="Completeness of financial analysis")
    compliance_score: float = Field(ge=0.0, le=1.0, description="Regulatory compliance adherence")
    explanation: str = "Evaluation reasoning"

class PortfolioEvaluator(BaseModel):
    """Evaluation criteria for portfolio recommendations"""
    diversification_score: float = Field(ge=0.0, le=1.0, description="Portfolio diversification quality")
    risk_alignment_score: float = Field(ge=0.0, le=1.0, description="Alignment with user risk tolerance")
    allocation_logic_score: float = Field(ge=0.0, le=1.0, description="Soundness of allocation strategy")
    cost_efficiency_score: float = Field(ge=0.0, le=1.0, description="Cost efficiency of recommendations")
    explanation: str = "Portfolio evaluation reasoning"

class LangSmithService:
    """
    Comprehensive LangSmith integration service for Financial Investment Advisor Agent
    
    Features:
    - End-to-end tracing of financial analysis pipelines
    - Custom evaluation of financial advice quality
    - Performance monitoring and alerting
    - PII sanitization and data privacy
    - Compliance tracking
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.client = None
        self.tracer = None
        self.wrapped_openai_client = None
        self._initialize_client()
        
    def _load_config(self) -> LangSmithConfig:
        """Load LangSmith configuration from environment variables"""
        return LangSmithConfig(
            api_key=os.getenv("LANGSMITH_API_KEY", ""),
            project_name=os.getenv("LANGSMITH_PROJECT", "financial-advisor-agent"),
            endpoint=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
            tracing_enabled=os.getenv("LANGSMITH_TRACING", "true").lower() == "true",
            evaluation_enabled=os.getenv("LANGSMITH_ENABLE_EVALUATION", "true").lower() == "true",
            sample_rate=float(os.getenv("LANGSMITH_SAMPLE_RATE", "1.0")),
            session_name=os.getenv("LANGSMITH_SESSION_NAME", "faa-session"),
            sanitize_pii=os.getenv("LANGSMITH_SANITIZE_PII", "true").lower() == "true",
            track_performance=os.getenv("LANGSMITH_TRACK_PERFORMANCE", "true").lower() == "true",
            auto_eval_threshold=float(os.getenv("LANGSMITH_AUTO_EVAL_THRESHOLD", "0.8"))
        )
    
    def _initialize_client(self):
        """Initialize LangSmith client and related components"""
        if not self.config.api_key:
            logger.warning("⚠️ LangSmith API key not provided. Observability features disabled.")
            return
            
        try:
            # Initialize LangSmith client
            self.client = Client(
                api_url=self.config.endpoint,
                api_key=self.config.api_key
            )
            
            # Initialize tracer
            self.tracer = LangChainTracer(
                client=self.client,
                project_name=self.config.project_name
            )
            
            # Wrap OpenAI client for automatic tracing
            if self.config.tracing_enabled:
                self.wrapped_openai_client = wrap_openai(OpenAI())
                
            # Set environment variables for automatic tracing
            os.environ["LANGCHAIN_TRACING_V2"] = str(self.config.tracing_enabled).lower()
            os.environ["LANGCHAIN_API_KEY"] = self.config.api_key
            os.environ["LANGCHAIN_PROJECT"] = self.config.project_name
            
            logger.info(f"✅ LangSmith initialized for project: {self.config.project_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LangSmith: {str(e)}")
    
    def get_wrapped_openai_client(self) -> Optional[OpenAI]:
        """Get OpenAI client wrapped with LangSmith tracing"""
        return self.wrapped_openai_client
    
    def sanitize_pii(self, text: str) -> str:
        """Remove or mask PII from text before sending to LangSmith"""
        if not self.config.sanitize_pii:
            return text
            
        # Remove common PII patterns
        patterns = {
            r'\b\d{3}-\d{2}-\d{4}\b': '[SSN]',  # Social Security Numbers
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b': '[CARD_NUMBER]',  # Credit card numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL]',  # Email addresses
            r'\b\d{3}-\d{3}-\d{4}\b': '[PHONE]',  # Phone numbers
            r'\$[\d,]+(?:\.\d{2})?': '[AMOUNT]',  # Dollar amounts (optional)
        }
        
        sanitized_text = text
        for pattern, replacement in patterns.items():
            sanitized_text = re.sub(pattern, replacement, sanitized_text)
            
        return sanitized_text
    
    def trace_fap_pipeline(self, func: Callable) -> Callable:
        """Decorator to trace Financial Analysis Pipeline (FAP) execution"""
        @wraps(func)
        @traceable(
            name=f"fap_pipeline_{func.__name__}",
            project_name=self.config.project_name,
            tags=["fap", "financial_analysis", "pipeline"]
        )
        async def wrapper(*args, **kwargs):
            # Add metadata for better tracing
            metadata = {
                "component": "fap_pipeline",
                "function": func.__name__,
                "timestamp": datetime.now().isoformat(),
                "session": self.config.session_name
            }
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Add success metadata
                metadata.update({
                    "status": "success",
                    "result_type": type(result).__name__
                })
                
                return result
                
            except Exception as e:
                # Add error metadata
                metadata.update({
                    "status": "error",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })
                raise
                
        return wrapper
    
    def trace_agent_execution(self, agent_name: str, func: Callable) -> Callable:
        """Decorator to trace individual agent execution"""
        @wraps(func)
        @traceable(
            name=f"agent_{agent_name}",
            project_name=self.config.project_name,
            tags=["agent", agent_name, "execution"]
        )
        async def wrapper(*args, **kwargs):
            metadata = {
                "agent": agent_name,
                "component": "agent_execution",
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                result = await func(*args, **kwargs)
                metadata["status"] = "success"
                return result
            except Exception as e:
                metadata.update({
                    "status": "error",
                    "error": str(e)
                })
                raise
                
        return wrapper
    
    def trace_api_endpoint(self, endpoint_name: str, func: Callable) -> Callable:
        """Decorator to trace FastAPI endpoint calls"""
        @wraps(func)
        @traceable(
            name=f"api_{endpoint_name}",
            project_name=self.config.project_name,
            tags=["api", "endpoint", endpoint_name]
        )
        async def wrapper(*args, **kwargs):
            metadata = {
                "endpoint": endpoint_name,
                "component": "api",
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                result = await func(*args, **kwargs)
                metadata["status"] = "success"
                return result
            except Exception as e:
                metadata.update({
                    "status": "error",
                    "error": str(e)
                })
                raise
                
        return wrapper
    
    def trace_llm_call(self, operation_name: str) -> Callable:
        """Decorator to trace individual LLM calls with detailed metrics"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            @traceable(
                name=f"llm_{operation_name}",
                project_name=self.config.project_name,
                tags=["llm", "openai", operation_name]
            )
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                metadata = {
                    "operation": operation_name,
                    "component": "llm",
                    "model": kwargs.get("model", "gpt-4-turbo-preview"),
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    # Capture input details
                    if args:
                        input_text = str(args[0])[:500]  # Truncate for safety
                        metadata["input_preview"] = self.sanitize_pii(input_text)
                        metadata["input_length"] = len(str(args[0]))
                    
                    # Execute LLM call
                    result = await func(*args, **kwargs)
                    
                    # Capture output details
                    duration = (time.time() - start_time) * 1000
                    
                    if hasattr(result, 'content'):
                        output_text = str(result.content)[:500]
                        metadata["output_preview"] = self.sanitize_pii(output_text)
                        metadata["output_length"] = len(str(result.content))
                    
                    metadata.update({
                        "status": "success",
                        "duration_ms": duration,
                        "tokens_estimated": len(str(args[0]).split()) if args else 0
                    })
                    
                    # Track performance
                    await self.track_performance_metrics(
                        operation_name=f"llm_{operation_name}",
                        duration_ms=duration,
                        token_usage={"estimated_tokens": metadata["tokens_estimated"]},
                        success=True,
                        metadata=metadata
                    )
                    
                    return result
                    
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    metadata.update({
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "duration_ms": duration
                    })
                    
                    await self.track_performance_metrics(
                        operation_name=f"llm_{operation_name}_failed",
                        duration_ms=duration,
                        token_usage={"estimated_tokens": 0},
                        success=False,
                        metadata=metadata
                    )
                    raise
                    
            return wrapper
        return decorator
    
    def trace_tool_call(self, tool_name: str) -> Callable:
        """Decorator to trace tool invocations with input/output capture"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            @traceable(
                name=f"tool_{tool_name}",
                project_name=self.config.project_name,
                tags=["tool", "execution", tool_name]
            )
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                metadata = {
                    "tool_name": tool_name,
                    "component": "tool",
                    "timestamp": datetime.now().isoformat(),
                    "arguments": self.sanitize_pii(str(kwargs)[:200])
                }
                
                try:
                    result = await func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    
                    metadata.update({
                        "status": "success",
                        "duration_ms": duration,
                        "result_type": type(result).__name__,
                        "result_preview": self.sanitize_pii(str(result)[:200])
                    })
                    
                    await self.track_performance_metrics(
                        operation_name=f"tool_{tool_name}",
                        duration_ms=duration,
                        token_usage={"input_tokens": 0, "output_tokens": 0},
                        success=True,
                        metadata=metadata
                    )
                    
                    return result
                    
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    metadata.update({
                        "status": "error",
                        "error": str(e),
                        "duration_ms": duration
                    })
                    
                    await self.track_performance_metrics(
                        operation_name=f"tool_{tool_name}_failed",
                        duration_ms=duration,
                        token_usage={"input_tokens": 0, "output_tokens": 0},
                        success=False,
                        metadata=metadata
                    )
                    raise
                    
            return wrapper
        return decorator
    
    def trace_mcp_request(self, server_type: str, tool_name: str) -> Callable:
        """Decorator to trace MCP request/response cycles"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            @traceable(
                name=f"mcp_{server_type}_{tool_name}",
                project_name=self.config.project_name,
                tags=["mcp", "request", server_type, tool_name]
            )
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                metadata = {
                    "server_type": server_type,
                    "tool_name": tool_name,
                    "component": "mcp",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Capture request details
                if args:
                    metadata["request_args"] = self.sanitize_pii(str(args)[:300])
                if kwargs:
                    metadata["request_kwargs"] = self.sanitize_pii(str(kwargs)[:300])
                
                try:
                    result = await func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    
                    # Capture response details
                    metadata.update({
                        "status": "success",
                        "duration_ms": duration,
                        "response_type": type(result).__name__,
                        "response_preview": self.sanitize_pii(str(result)[:300])
                    })
                    
                    # Special handling for different result types
                    if isinstance(result, dict):
                        if "error" in result:
                            metadata["contains_error"] = True
                            metadata["error_details"] = result["error"]
                        if "api_call_successful" in result:
                            metadata["api_success"] = result["api_call_successful"]
                        if "source" in result:
                            metadata["data_source"] = result["source"]
                    
                    await self.track_performance_metrics(
                        operation_name=f"mcp_{server_type}_{tool_name}",
                        duration_ms=duration,
                        token_usage={"input_tokens": 0, "output_tokens": 0},
                        success=True,
                        metadata=metadata
                    )
                    
                    return result
                    
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    metadata.update({
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "duration_ms": duration
                    })
                    
                    await self.track_performance_metrics(
                        operation_name=f"mcp_{server_type}_{tool_name}_failed",
                        duration_ms=duration,
                        token_usage={"input_tokens": 0, "output_tokens": 0},
                        success=False,
                        metadata=metadata
                    )
                    raise
                    
            return wrapper
        return decorator
    
    async def evaluate_financial_advice(
        self,
        user_input: str,
        advice_output: str,
        reference_output: Optional[str] = None
    ) -> FinancialAdviceEvaluator:
        """Evaluate the quality of financial advice using custom evaluators"""
        
        if not self.config.evaluation_enabled or not self.wrapped_openai_client:
            # Return default scores if evaluation is disabled
            return FinancialAdviceEvaluator(
                accuracy_score=0.8,
                relevance_score=0.8,
                safety_score=0.8,
                completeness_score=0.8,
                compliance_score=0.8,
                explanation="Evaluation disabled or client unavailable"
            )
        
        evaluation_prompt = f"""
        Evaluate the following financial advice on multiple criteria:
        
        User Input: {self.sanitize_pii(user_input)}
        Financial Advice: {self.sanitize_pii(advice_output)}
        
        Rate each aspect from 0.0 to 1.0:
        1. Accuracy: Is the financial information factually correct?
        2. Relevance: Does it address the user's specific situation?
        3. Safety: Is the advice safe and appropriate?
        4. Completeness: Does it provide comprehensive analysis?
        5. Compliance: Does it follow regulatory guidelines?
        
        Respond in JSON format with scores and explanation.
        """
        
        try:
            response = await self.wrapped_openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial advice evaluator. Provide scores as JSON."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            evaluation_data = json.loads(response.choices[0].message.content)
            
            return FinancialAdviceEvaluator(
                accuracy_score=evaluation_data.get("accuracy", 0.8),
                relevance_score=evaluation_data.get("relevance", 0.8),
                safety_score=evaluation_data.get("safety", 0.8),
                completeness_score=evaluation_data.get("completeness", 0.8),
                compliance_score=evaluation_data.get("compliance", 0.8),
                explanation=evaluation_data.get("explanation", "Auto-generated evaluation")
            )
            
        except Exception as e:
            logger.error(f"❌ Financial advice evaluation failed: {str(e)}")
            return FinancialAdviceEvaluator(
                accuracy_score=0.5,
                relevance_score=0.5,
                safety_score=0.5,
                completeness_score=0.5,
                compliance_score=0.5,
                explanation=f"Evaluation failed: {str(e)}"
            )
    
    async def evaluate_portfolio_recommendation(
        self,
        user_profile: Dict[str, Any],
        portfolio_allocation: Dict[str, float],
        analysis_text: str
    ) -> PortfolioEvaluator:
        """Evaluate portfolio recommendations using domain-specific criteria"""
        
        if not self.config.evaluation_enabled or not self.wrapped_openai_client:
            return PortfolioEvaluator(
                diversification_score=0.8,
                risk_alignment_score=0.8,
                allocation_logic_score=0.8,
                cost_efficiency_score=0.8,
                explanation="Evaluation disabled"
            )
        
        evaluation_prompt = f"""
        Evaluate this portfolio recommendation:
        
        User Profile: {json.dumps(user_profile, indent=2)}
        Portfolio Allocation: {json.dumps(portfolio_allocation, indent=2)}
        Analysis: {self.sanitize_pii(analysis_text)}
        
        Rate each aspect from 0.0 to 1.0:
        1. Diversification: How well diversified is the portfolio?
        2. Risk Alignment: Does it match the user's risk tolerance?
        3. Allocation Logic: Is the allocation strategy sound?
        4. Cost Efficiency: Are the recommendations cost-effective?
        
        Respond in JSON format with scores and explanation.
        """
        
        try:
            response = await self.wrapped_openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a portfolio recommendation evaluator. Provide scores as JSON."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            evaluation_data = json.loads(response.choices[0].message.content)
            
            return PortfolioEvaluator(
                diversification_score=evaluation_data.get("diversification", 0.8),
                risk_alignment_score=evaluation_data.get("risk_alignment", 0.8),
                allocation_logic_score=evaluation_data.get("allocation_logic", 0.8),
                cost_efficiency_score=evaluation_data.get("cost_efficiency", 0.8),
                explanation=evaluation_data.get("explanation", "Auto-generated portfolio evaluation")
            )
            
        except Exception as e:
            logger.error(f"❌ Portfolio evaluation failed: {str(e)}")
            return PortfolioEvaluator(
                diversification_score=0.5,
                risk_alignment_score=0.5,
                allocation_logic_score=0.5,
                cost_efficiency_score=0.5,
                explanation=f"Evaluation failed: {str(e)}"
            )
    
    async def create_evaluation_dataset(
        self,
        dataset_name: str,
        examples: List[Dict[str, Any]],
        description: str = "Financial advice evaluation dataset"
    ) -> Optional[str]:
        """Create a dataset for evaluation purposes"""
        
        if not self.client:
            logger.warning("⚠️ LangSmith client not available. Cannot create dataset.")
            return None
            
        try:
            # Create dataset
            dataset = self.client.create_dataset(
                dataset_name=dataset_name,
                description=description
            )
            
            # Add examples to dataset
            inputs = [{"question": ex.get("input", "")} for ex in examples]
            outputs = [{"answer": ex.get("output", "")} for ex in examples]
            
            self.client.create_examples(
                inputs=inputs,
                outputs=outputs,
                dataset_id=dataset.id
            )
            
            logger.info(f"✅ Created evaluation dataset: {dataset_name} with {len(examples)} examples")
            return dataset.id
            
        except Exception as e:
            logger.error(f"❌ Failed to create evaluation dataset: {str(e)}")
            return None
    
    async def run_evaluation_experiment(
        self,
        dataset_id: str,
        target_function: Callable,
        evaluators: List[Callable],
        experiment_name: str
    ) -> Optional[Dict[str, Any]]:
        """Run an evaluation experiment on a dataset"""
        
        if not self.client:
            logger.warning("⚠️ LangSmith client not available. Cannot run evaluation.")
            return None
            
        try:
            results = self.client.evaluate(
                target_function,
                data=dataset_id,
                evaluators=evaluators,
                experiment_prefix=experiment_name,
                max_concurrency=2
            )
            
            logger.info(f"✅ Completed evaluation experiment: {experiment_name}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Evaluation experiment failed: {str(e)}")
            return None
    
    async def track_performance_metrics(
        self,
        operation_name: str,
        duration_ms: float,
        token_usage: Dict[str, int],
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track performance metrics for operations"""
        
        if not self.config.track_performance:
            return
            
        metrics = {
            "operation": operation_name,
            "duration_ms": duration_ms,
            "token_usage": token_usage,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Log performance metrics
        logger.info(f"📊 Performance: {operation_name} - {duration_ms:.2f}ms - {'✅' if success else '❌'}")
        
        # Check for performance alerts
        if duration_ms > float(os.getenv("LANGSMITH_LATENCY_THRESHOLD_MS", "5000")):
            logger.warning(f"⚠️ Performance alert: {operation_name} took {duration_ms:.2f}ms")
    
    def get_tracing_context(self) -> Optional[Dict[str, Any]]:
        """Get current tracing context for distributed tracing"""
        try:
            # This would be implemented for distributed tracing scenarios
            return {
                "project": self.config.project_name,
                "session": self.config.session_name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to get tracing context: {str(e)}")
            return None
    
    async def log_compliance_event(
        self,
        event_type: str,
        content: str,
        compliance_result: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Log compliance-related events for audit trail"""
        
        compliance_log = {
            "event_type": event_type,
            "content": self.sanitize_pii(content),
            "compliance_result": compliance_result,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "project": self.config.project_name
        }
        
        logger.info(f"📋 Compliance Event: {event_type} - {compliance_result.get('status', 'unknown')}")
        
        # In a production environment, this could be sent to a compliance system
        # For now, we log it for audit purposes
    
    def is_enabled(self) -> bool:
        """Check if LangSmith integration is properly enabled"""
        return bool(self.client and self.config.api_key and self.config.tracing_enabled)
    
    def get_dashboard_url(self) -> str:
        """Get URL to LangSmith dashboard for this project"""
        if self.client:
            return f"{self.config.endpoint}/projects/{self.config.project_name}"
        return ""

# Global instance
langsmith_service = LangSmithService() 