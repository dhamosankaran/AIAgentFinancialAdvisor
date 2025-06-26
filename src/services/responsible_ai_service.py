"""
Responsible AI Service
Provides content moderation, hallucination detection, PII protection, and safety checks
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from enum import Enum
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ModerationResult:
    def __init__(self, passed: bool, risk_level: RiskLevel, issues: List[str], sanitized_content: str = None):
        self.passed = passed
        self.risk_level = risk_level
        self.issues = issues
        self.sanitized_content = sanitized_content
        self.timestamp = datetime.now()

class HallucinationDetectionResult:
    def __init__(self, confidence_score: float, is_hallucination: bool, concerns: List[str]):
        self.confidence_score = confidence_score
        self.is_hallucination = is_hallucination
        self.concerns = concerns
        self.timestamp = datetime.now()

class ResponsibleAIService:
    """Service for responsible AI practices including content moderation and safety checks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize moderation LLM (using smaller model for efficiency)
        self.moderation_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=self.openai_api_key
        ) if self.openai_api_key else None
        
        # PII patterns
        self.pii_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'bank_account': r'\b\d{8,17}\b',
            'date_of_birth': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
        
        # Financial content safety keywords
        self.prohibited_keywords = [
            'guaranteed returns', 'risk-free investment', 'get rich quick',
            'insider information', 'pump and dump', 'ponzi scheme',
            'cryptocurrency scam', 'investment fraud', 'sure thing',
            'no risk', 'guaranteed profit', 'secret strategy'
        ]
        
        # Jailbreak attempt patterns
        self.jailbreak_patterns = [
            r'ignore.*previous.*instructions',
            r'forget.*you.*are.*financial.*advisor',
            r'pretend.*to.*be',
            r'roleplay.*as',
            r'act.*like.*different.*person',
            r'bypass.*safety.*guidelines',
            r'override.*restrictions'
        ]
    
    async def moderate_input(self, content: str, context: Dict[str, Any] = None) -> ModerationResult:
        """
        Moderate user input before sending to LLM
        """
        self.logger.info("Starting input content moderation")
        
        issues = []
        risk_level = RiskLevel.LOW
        sanitized_content = content
        
        # 1. PII Detection and Sanitization
        pii_issues, sanitized_content = self._detect_and_sanitize_pii(sanitized_content)
        if pii_issues:
            issues.extend(pii_issues)
            risk_level = RiskLevel.MEDIUM
        
        # 2. Jailbreak Detection
        jailbreak_detected = self._detect_jailbreak_attempts(content)
        if jailbreak_detected:
            issues.append("Potential jailbreak attempt detected")
            risk_level = RiskLevel.HIGH
        
        # 3. Prohibited Content Detection
        prohibited_content = self._detect_prohibited_content(content)
        if prohibited_content:
            issues.extend(prohibited_content)
            risk_level = RiskLevel.MEDIUM
        
        # 4. Financial Advice Compliance Check
        compliance_issues = await self._check_financial_compliance(content)
        if compliance_issues:
            issues.extend(compliance_issues)
            if any("investment advice" in issue.lower() for issue in compliance_issues):
                risk_level = RiskLevel.HIGH
        
        # Determine if content passes moderation
        passed = risk_level not in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        self.logger.info(f"Input moderation completed: passed={passed}, risk_level={risk_level.value}, issues={len(issues)}")
        
        return ModerationResult(passed, risk_level, issues, sanitized_content)
    
    async def moderate_output(self, content: str, original_input: str = None) -> ModerationResult:
        """
        Moderate LLM output before returning to user
        """
        self.logger.info("Starting output content moderation")
        
        issues = []
        risk_level = RiskLevel.LOW
        sanitized_content = content
        
        # 1. Financial Disclaimer Check
        if not self._has_financial_disclaimer(content):
            issues.append("Missing required financial disclaimer")
            risk_level = RiskLevel.MEDIUM
            sanitized_content = self._add_financial_disclaimer(sanitized_content)
        
        # 2. Inappropriate Investment Promises
        inappropriate_promises = self._detect_inappropriate_promises(content)
        if inappropriate_promises:
            issues.extend(inappropriate_promises)
            risk_level = RiskLevel.HIGH
        
        # 3. PII in Output
        pii_issues, sanitized_content = self._detect_and_sanitize_pii(sanitized_content)
        if pii_issues:
            issues.extend(pii_issues)
            risk_level = RiskLevel.MEDIUM
        
        # 4. Hallucination Detection
        if original_input:
            hallucination_result = await self._detect_hallucinations(content, original_input)
            if hallucination_result.is_hallucination:
                issues.extend(hallucination_result.concerns)
                risk_level = RiskLevel.HIGH
        
        passed = risk_level not in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        self.logger.info(f"Output moderation completed: passed={passed}, risk_level={risk_level.value}, issues={len(issues)}")
        
        return ModerationResult(passed, risk_level, issues, sanitized_content)
    
    async def detect_hallucinations(self, content: str, context: str = None) -> HallucinationDetectionResult:
        """
        Detect potential hallucinations in LLM output
        """
        self.logger.info("Starting hallucination detection")
        
        if not self.moderation_llm:
            self.logger.warning("OpenAI API key not available, skipping hallucination detection")
            return HallucinationDetectionResult(0.5, False, ["API key not available"])
        
        # 1. Factual Consistency Check
        factual_issues = await self._check_factual_consistency(content, context)
        
        # 2. Financial Accuracy Check
        financial_accuracy_issues = await self._check_financial_accuracy(content)
        
        # 3. Logical Consistency Check
        logical_issues = self._check_logical_consistency(content)
        
        all_concerns = factual_issues + financial_accuracy_issues + logical_issues
        
        # Calculate confidence score (0-1, where 1 is high confidence it's NOT a hallucination)
        confidence_score = max(0, 1 - (len(all_concerns) * 0.2))
        is_hallucination = confidence_score < 0.6 or len(all_concerns) >= 3
        
        self.logger.info(f"Hallucination detection completed: confidence={confidence_score:.2f}, is_hallucination={is_hallucination}")
        
        return HallucinationDetectionResult(confidence_score, is_hallucination, all_concerns)
    
    def _detect_and_sanitize_pii(self, content: str) -> Tuple[List[str], str]:
        """Detect and sanitize PII in content"""
        issues = []
        sanitized = content
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(f"Detected {pii_type.upper()}: {len(matches)} instances")
                # Sanitize by replacing with placeholder
                sanitized = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return issues, sanitized
    
    def _detect_jailbreak_attempts(self, content: str) -> bool:
        """Detect potential jailbreak attempts"""
        content_lower = content.lower()
        
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    def _detect_prohibited_content(self, content: str) -> List[str]:
        """Detect prohibited financial content"""
        issues = []
        content_lower = content.lower()
        
        for keyword in self.prohibited_keywords:
            if keyword.lower() in content_lower:
                issues.append(f"Prohibited content detected: '{keyword}'")
        
        return issues
    
    async def _check_financial_compliance(self, content: str) -> List[str]:
        """Check for financial compliance issues"""
        issues = []
        
        # Check for unlicensed investment advice
        if any(phrase in content.lower() for phrase in ['you should invest', 'i recommend buying', 'best investment']):
            if 'this is not financial advice' not in content.lower():
                issues.append("Potential unlicensed investment advice without disclaimer")
        
        # Check for unrealistic claims
        unrealistic_patterns = [
            r'\d+%.*guaranteed.*return',
            r'risk.*free.*\d+%',
            r'double.*your.*money',
            r'\d+x.*returns'
        ]
        
        for pattern in unrealistic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Unrealistic financial claim detected")
        
        return issues
    
    def _has_financial_disclaimer(self, content: str) -> bool:
        """Check if content has appropriate financial disclaimer"""
        disclaimer_phrases = [
            'not financial advice',
            'consult with a financial advisor',
            'past performance does not guarantee',
            'investment involves risk'
        ]
        
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in disclaimer_phrases)
    
    def _add_financial_disclaimer(self, content: str) -> str:
        """Add financial disclaimer to content"""
        disclaimer = "\n\n⚠️ **Disclaimer**: This information is for educational purposes only and should not be considered as personalized financial advice. Past performance does not guarantee future results. Please consult with a qualified financial advisor before making investment decisions."
        return content + disclaimer
    
    def _detect_inappropriate_promises(self, content: str) -> List[str]:
        """Detect inappropriate investment promises"""
        issues = []
        content_lower = content.lower()
        
        inappropriate_phrases = [
            'guaranteed to make money',
            'zero risk investment',
            'sure-fire way to',
            'cannot lose',
            'risk-free returns'
        ]
        
        for phrase in inappropriate_phrases:
            if phrase in content_lower:
                issues.append(f"Inappropriate investment promise: '{phrase}'")
        
        return issues
    
    async def _detect_hallucinations(self, content: str, original_input: str) -> HallucinationDetectionResult:
        """Internal hallucination detection with context"""
        if not self.moderation_llm:
            return HallucinationDetectionResult(0.5, False, ["Moderation LLM not available"])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial fact-checker. Analyze the AI response for potential hallucinations, inaccuracies, or made-up information.

Look for:
1. Specific financial data that seems fabricated
2. Company information that may not be real
3. Market predictions presented as facts
4. Investment products that don't exist
5. Regulatory information that seems incorrect

Respond with JSON format:
{
    "concerns": ["list of specific concerns"],
    "confidence_score": 0.0-1.0,
    "recommendation": "approve/review/reject"
}"""),
            ("human", f"Original Question: {original_input}\n\nAI Response to Check: {content}")
        ])
        
        try:
            response = await self.moderation_llm.ainvoke(prompt.format_messages())
            
            # Clean and parse JSON response
            content = response.content.strip()
            
            # Try to extract JSON from response if it's wrapped in markdown or other text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                result = json.loads(json_content)
            else:
                # If no JSON found, create a default response
                self.logger.warning(f"No valid JSON found in response: {content[:100]}...")
                result = {
                    "concerns": ["Unable to parse moderation response"],
                    "confidence_score": 0.5,
                    "recommendation": "review"
                }
            
            concerns = result.get("concerns", [])
            confidence = result.get("confidence_score", 0.5)
            is_hallucination = result.get("recommendation") in ["review", "reject"]
            
            return HallucinationDetectionResult(confidence, is_hallucination, concerns)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error in hallucination detection: {str(e)}")
            return HallucinationDetectionResult(0.5, False, [f"JSON parsing error: {str(e)}"])
        except Exception as e:
            self.logger.error(f"Error in hallucination detection: {str(e)}")
            return HallucinationDetectionResult(0.5, False, [f"Detection error: {str(e)}"])
    
    async def _check_factual_consistency(self, content: str, context: str = None) -> List[str]:
        """Check factual consistency"""
        issues = []
        
        # Simple heuristics for now
        if "100% guaranteed" in content:
            issues.append("Absolute guarantee claim detected")
        
        if re.search(r'\d{4}%.*return', content):
            issues.append("Unrealistic percentage return mentioned")
        
        return issues
    
    async def _check_financial_accuracy(self, content: str) -> List[str]:
        """Check financial information accuracy"""
        issues = []
        
        # Check for common financial inaccuracies
        if "stocks never go down" in content.lower():
            issues.append("Factually incorrect statement about stock market")
        
        if "bonds are risk-free" in content.lower():
            issues.append("Misleading statement about bond risks")
        
        return issues
    
    def _check_logical_consistency(self, content: str) -> List[str]:
        """Check logical consistency in content"""
        issues = []
        
        # Simple logical consistency checks
        if "low risk" in content.lower() and "high return" in content.lower():
            if "trade-off" not in content.lower():
                issues.append("Risk-return trade-off not acknowledged")
        
        return issues
    
    def get_moderation_stats(self) -> Dict[str, Any]:
        """Get moderation statistics"""
        # In a real implementation, this would track statistics
        return {
            "total_requests": 0,
            "blocked_requests": 0,
            "pii_detections": 0,
            "jailbreak_attempts": 0,
            "compliance_issues": 0
        } 