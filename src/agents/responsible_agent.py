"""
Responsible AI-Enhanced Financial Agent
Integrates Responsible AI layer with existing financial agents
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory

from .base_agent import BaseFinancialAgent
from ..services.responsible_ai_service import ResponsibleAIService, RiskLevel

class ResponsibleFinancialAgent(BaseFinancialAgent):
    """Financial agent enhanced with Responsible AI capabilities"""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[Tool]] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[ConversationBufferMemory] = None,
        enable_input_moderation: bool = True,
        enable_output_moderation: bool = True,
        enable_hallucination_detection: bool = True,
        block_high_risk: bool = True
    ):
        """Initialize responsible AI-enhanced agent"""
        self.responsible_ai = ResponsibleAIService()
        self.enable_input_moderation = enable_input_moderation
        self.enable_output_moderation = enable_output_moderation
        self.enable_hallucination_detection = enable_hallucination_detection
        self.block_high_risk = block_high_risk
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize base agent
        super().__init__(llm=llm, tools=tools, system_prompt=system_prompt, memory=memory)
    
    async def process_message(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Process message with responsible AI safeguards"""
        self.logger.info(f"Processing message with responsible AI safeguards: {message[:100]}...")
        
        original_message = message
        
        try:
            # 1. Input Moderation
            if self.enable_input_moderation:
                self.logger.info("Starting input moderation")
                input_moderation = await self.responsible_ai.moderate_input(message)
                
                if not input_moderation.passed and self.block_high_risk:
                    self.logger.warning(f"Input blocked due to moderation: {input_moderation.issues}")
                    return self._generate_blocked_response(input_moderation.issues)
                
                # Use sanitized content if available
                if input_moderation.sanitized_content:
                    message = input_moderation.sanitized_content
                    self.logger.info("Using sanitized input content")
            
            # 2. Process with base agent
            self.logger.info("Processing with base agent")
            response = await super().process_message(message, chat_history)
            
            # 3. Output Moderation
            if self.enable_output_moderation:
                self.logger.info("Starting output moderation")
                output_moderation = await self.responsible_ai.moderate_output(response, original_message)
                
                if not output_moderation.passed and self.block_high_risk:
                    self.logger.warning(f"Output blocked due to moderation: {output_moderation.issues}")
                    return self._generate_fallback_response()
                
                # Use sanitized content (includes disclaimers)
                if output_moderation.sanitized_content:
                    response = output_moderation.sanitized_content
                    self.logger.info("Using sanitized output content")
            
            # 4. Hallucination Detection (if enabled)
            if self.enable_hallucination_detection:
                self.logger.info("Starting hallucination detection")
                hallucination_result = await self.responsible_ai.detect_hallucinations(response, original_message)
                
                if hallucination_result.is_hallucination and self.block_high_risk:
                    self.logger.warning(f"Potential hallucination detected: {hallucination_result.concerns}")
                    return self._generate_hallucination_response(hallucination_result.concerns)
            
            self.logger.info("Responsible AI processing completed successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in responsible AI processing: {str(e)}")
            return self._generate_error_response(str(e))
    
    def _generate_blocked_response(self, issues: List[str]) -> str:
        """Generate response when input is blocked"""
        return (
            "I'm sorry, but I cannot process your request as it contains content that violates our safety guidelines. "
            "Please rephrase your question and I'll be happy to help you with your financial planning needs.\n\n"
            f"Issues detected: {', '.join(issues[:3])}..."  # Show first 3 issues
        )
    
    def _generate_fallback_response(self) -> str:
        """Generate fallback response when output is blocked"""
        return (
            "I apologize, but I cannot provide a response to your question at this time. "
            "For personalized financial advice, I recommend consulting with a qualified financial advisor.\n\n"
            "⚠️ **Disclaimer**: This information is for educational purposes only and should not be considered as "
            "personalized financial advice. Past performance does not guarantee future results. Please consult "
            "with a qualified financial advisor before making investment decisions."
        )
    
    def _generate_hallucination_response(self, concerns: List[str]) -> str:
        """Generate response when hallucination is detected"""
        return (
            "I apologize, but I may not have accurate information to fully answer your question. "
            "For reliable financial information, I recommend:\n\n"
            "• Consulting with a licensed financial advisor\n"
            "• Checking official financial data sources\n"
            "• Reviewing current market reports from reputable sources\n\n"
            "⚠️ **Disclaimer**: This information is for educational purposes only and should not be considered as "
            "personalized financial advice. Past performance does not guarantee future results."
        )
    
    def _generate_error_response(self, error: str) -> str:
        """Generate response when processing error occurs"""
        return (
            "I encountered an error while processing your request. Please try rephrasing your question or "
            "contact support if the issue persists.\n\n"
            "⚠️ **Disclaimer**: This information is for educational purposes only and should not be considered as "
            "personalized financial advice. Past performance does not guarantee future results."
        )
    
    async def get_moderation_report(self, message: str) -> Dict[str, Any]:
        """Get detailed moderation report for a message (for debugging/monitoring)"""
        report = {
            "input_moderation": None,
            "output_moderation": None,
            "hallucination_detection": None,
            "timestamp": None
        }
        
        try:
            # Input moderation
            if self.enable_input_moderation:
                input_result = await self.responsible_ai.moderate_input(message)
                report["input_moderation"] = {
                    "passed": input_result.passed,
                    "risk_level": input_result.risk_level.value,
                    "issues": input_result.issues,
                    "timestamp": input_result.timestamp.isoformat()
                }
            
            # Process message to get output
            response = await super().process_message(message)
            
            # Output moderation
            if self.enable_output_moderation:
                output_result = await self.responsible_ai.moderate_output(response, message)
                report["output_moderation"] = {
                    "passed": output_result.passed,
                    "risk_level": output_result.risk_level.value,
                    "issues": output_result.issues,
                    "timestamp": output_result.timestamp.isoformat()
                }
            
            # Hallucination detection
            if self.enable_hallucination_detection:
                hallucination_result = await self.responsible_ai.detect_hallucinations(response, message)
                report["hallucination_detection"] = {
                    "confidence_score": hallucination_result.confidence_score,
                    "is_hallucination": hallucination_result.is_hallucination,
                    "concerns": hallucination_result.concerns,
                    "timestamp": hallucination_result.timestamp.isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"Error generating moderation report: {str(e)}")
            report["error"] = str(e)
        
        return report 