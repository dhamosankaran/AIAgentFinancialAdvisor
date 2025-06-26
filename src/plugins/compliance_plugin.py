"""
Example Compliance Plugin
Demonstrates plugin architecture for financial compliance checking
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_core.tools import Tool
import re
from datetime import datetime

from ..services.plugin_registry import BasePlugin, PluginMetadata, PluginCategory

class CompliancePlugin(BasePlugin):
    """Plugin for financial compliance checking and regulatory guidance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.regulatory_keywords = [
            'sec', 'finra', 'investment advisor', 'securities', 'regulation',
            'compliance', 'fiduciary', 'suitability', 'know your customer'
        ]
        
    async def initialize(self) -> bool:
        """Initialize the compliance plugin"""
        try:
            self.logger.info("Initializing Compliance Plugin")
            # In a real implementation, you might load regulatory databases,
            # connect to compliance APIs, etc.
            self.status = 'active'
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize compliance plugin: {str(e)}")
            return False
    
    def get_tools(self) -> List[Tool]:
        """Get available compliance tools"""
        return [
            Tool(
                name="check_compliance",
                func=self._check_compliance,
                description="Check if investment advice or content complies with financial regulations"
            ),
            Tool(
                name="get_regulatory_guidance",
                func=self._get_regulatory_guidance,
                description="Get regulatory guidance for specific financial topics"
            ),
            Tool(
                name="validate_investment_suitability",
                func=self._validate_investment_suitability,
                description="Validate if an investment recommendation is suitable for a client profile"
            ),
            Tool(
                name="check_disclosure_requirements",
                func=self._check_disclosure_requirements,
                description="Check what disclosures are required for specific financial advice"
            )
        ]
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return PluginMetadata(
            name="compliance_plugin",
            version="1.0.0",
            description="Financial compliance checking and regulatory guidance plugin",
            category=PluginCategory.COMPLIANCE,
            author="AgenticAI Team",
            dependencies=[],
            config_schema={
                "strict_mode": {"type": "boolean", "default": True},
                "regulatory_jurisdiction": {"type": "string", "default": "US"}
            },
            api_requirements=[]
        )
    
    def _check_compliance(self, content: str) -> str:
        """Check compliance of financial content"""
        issues = []
        
        # Check for required disclaimers
        if not self._has_required_disclaimers(content):
            issues.append("Missing required financial disclaimers")
        
        # Check for inappropriate language
        inappropriate_terms = self._check_inappropriate_terms(content)
        if inappropriate_terms:
            issues.extend(inappropriate_terms)
        
        # Check for regulatory violations
        violations = self._check_regulatory_violations(content)
        if violations:
            issues.extend(violations)
        
        if issues:
            return f"Compliance Issues Found:\n" + "\n".join(f"- {issue}" for issue in issues)
        else:
            return "Content appears to be compliant with financial regulations."
    
    def _get_regulatory_guidance(self, topic: str) -> str:
        """Get regulatory guidance for a topic"""
        guidance_map = {
            "investment advice": {
                "guidance": "Investment advice must include appropriate disclaimers and suitability assessments",
                "requirements": ["Suitability determination", "Risk disclosure", "Fiduciary duty consideration"],
                "references": ["Investment Advisers Act of 1940", "SEC Release IA-1092"]
            },
            "securities": {
                "guidance": "Securities recommendations must comply with FINRA rules and SEC regulations",
                "requirements": ["Know Your Customer", "Suitability", "Best execution"],
                "references": ["FINRA Rule 2111", "Securities Act of 1933"]
            },
            "portfolio management": {
                "guidance": "Portfolio management services require proper registration and disclosure",
                "requirements": ["ADV filing", "Client agreements", "Performance reporting"],
                "references": ["Investment Advisers Act", "SEC Form ADV"]
            }
        }
        
        topic_lower = topic.lower()
        for key, info in guidance_map.items():
            if key in topic_lower:
                return f"""Regulatory Guidance for '{topic}':

{info['guidance']}

Requirements:
{chr(10).join(f"- {req}" for req in info['requirements'])}

Relevant Regulations:
{chr(10).join(f"- {ref}" for ref in info['references'])}"""
        
        return f"No specific regulatory guidance found for '{topic}'. Consult with a compliance officer for detailed requirements."
    
    def _validate_investment_suitability(self, client_profile: str, investment_recommendation: str) -> str:
        """Validate investment suitability"""
        # Parse client profile for key factors
        suitability_factors = {
            'age': self._extract_age(client_profile),
            'risk_tolerance': self._extract_risk_tolerance(client_profile),
            'investment_horizon': self._extract_investment_horizon(client_profile),
            'financial_situation': self._extract_financial_situation(client_profile)
        }
        
        # Analyze investment recommendation
        investment_analysis = self._analyze_investment_risk(investment_recommendation)
        
        # Check suitability
        suitability_assessment = self._assess_suitability(suitability_factors, investment_analysis)
        
        return f"""Suitability Assessment:

Client Profile Analysis:
- Age: {suitability_factors['age'] or 'Not specified'}
- Risk Tolerance: {suitability_factors['risk_tolerance'] or 'Not specified'}
- Investment Horizon: {suitability_factors['investment_horizon'] or 'Not specified'}
- Financial Situation: {suitability_factors['financial_situation'] or 'Not specified'}

Investment Analysis:
- Risk Level: {investment_analysis.get('risk_level', 'Unknown')}
- Liquidity: {investment_analysis.get('liquidity', 'Unknown')}
- Complexity: {investment_analysis.get('complexity', 'Unknown')}

Suitability Determination: {suitability_assessment['determination']}

Rationale: {suitability_assessment['rationale']}

Recommendations:
{chr(10).join(f"- {rec}" for rec in suitability_assessment['recommendations'])}"""
    
    def _check_disclosure_requirements(self, advice_type: str) -> str:
        """Check required disclosures for financial advice"""
        disclosure_requirements = {
            "investment recommendation": [
                "Investment involves risk and may result in loss of principal",
                "Past performance does not guarantee future results",
                "This is not personalized investment advice",
                "Consult with a qualified financial advisor"
            ],
            "portfolio allocation": [
                "Asset allocation does not guarantee profit or protection against loss",
                "Diversification does not eliminate risk",
                "Consider your risk tolerance and investment objectives",
                "Rebalancing may have tax consequences"
            ],
            "market analysis": [
                "Market analysis is based on current conditions which may change",
                "Forecasts are not guaranteed and should not be relied upon",
                "Economic factors may impact investment performance",
                "Past market performance does not predict future results"
            ]
        }
        
        advice_lower = advice_type.lower()
        required_disclosures = []
        
        for key, disclosures in disclosure_requirements.items():
            if key in advice_lower:
                required_disclosures.extend(disclosures)
        
        if not required_disclosures:
            required_disclosures = disclosure_requirements["investment recommendation"]  # Default
        
        return f"""Required Disclosures for '{advice_type}':

{chr(10).join(f"- {disclosure}" for disclosure in required_disclosures)}

Note: Additional disclosures may be required based on specific circumstances and regulatory jurisdiction."""
    
    def _has_required_disclaimers(self, content: str) -> bool:
        """Check if content has required disclaimers"""
        disclaimer_phrases = [
            'not financial advice',
            'not investment advice',
            'consult with a financial advisor',
            'past performance',
            'investment involves risk'
        ]
        
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in disclaimer_phrases)
    
    def _check_inappropriate_terms(self, content: str) -> List[str]:
        """Check for inappropriate financial terms"""
        inappropriate_terms = [
            'guaranteed profit',
            'risk-free investment',
            'sure thing',
            'cannot lose',
            'guaranteed returns'
        ]
        
        issues = []
        content_lower = content.lower()
        
        for term in inappropriate_terms:
            if term in content_lower:
                issues.append(f"Inappropriate term detected: '{term}'")
        
        return issues
    
    def _check_regulatory_violations(self, content: str) -> List[str]:
        """Check for potential regulatory violations"""
        violations = []
        
        # Check for unlicensed advice
        if any(phrase in content.lower() for phrase in ['you should buy', 'i recommend purchasing', 'best investment']):
            if 'licensed' not in content.lower() and 'registered' not in content.lower():
                violations.append("Potential unlicensed investment advice")
        
        # Check for market manipulation language
        manipulation_terms = ['pump and dump', 'insider information', 'hot tip']
        for term in manipulation_terms:
            if term in content.lower():
                violations.append(f"Potential market manipulation language: '{term}'")
        
        return violations
    
    # Helper methods for suitability assessment
    def _extract_age(self, profile: str) -> Optional[str]:
        age_match = re.search(r'age[:\s]*(\d+)', profile, re.IGNORECASE)
        return age_match.group(1) if age_match else None
    
    def _extract_risk_tolerance(self, profile: str) -> Optional[str]:
        risk_patterns = ['conservative', 'moderate', 'aggressive', 'high risk', 'low risk']
        for pattern in risk_patterns:
            if pattern in profile.lower():
                return pattern
        return None
    
    def _extract_investment_horizon(self, profile: str) -> Optional[str]:
        horizon_patterns = ['short term', 'long term', 'retirement', 'years']
        for pattern in horizon_patterns:
            if pattern in profile.lower():
                return pattern
        return None
    
    def _extract_financial_situation(self, profile: str) -> Optional[str]:
        income_match = re.search(r'income[:\s]*\$?(\d+(?:,\d+)*)', profile, re.IGNORECASE)
        return f"${income_match.group(1)}" if income_match else None
    
    def _analyze_investment_risk(self, investment: str) -> Dict[str, str]:
        """Analyze investment risk characteristics"""
        investment_lower = investment.lower()
        
        # Determine risk level
        if any(term in investment_lower for term in ['bonds', 'treasury', 'cd']):
            risk_level = 'Low'
        elif any(term in investment_lower for term in ['mutual fund', 'etf', 'index']):
            risk_level = 'Moderate'
        elif any(term in investment_lower for term in ['individual stocks', 'options', 'crypto']):
            risk_level = 'High'
        else:
            risk_level = 'Unknown'
        
        return {
            'risk_level': risk_level,
            'liquidity': 'Variable',
            'complexity': 'Moderate'
        }
    
    def _assess_suitability(self, client_factors: Dict, investment_analysis: Dict) -> Dict[str, Any]:
        """Assess investment suitability"""
        # Simple suitability logic (would be more complex in practice)
        client_age = int(client_factors.get('age', 0)) if client_factors.get('age') else 0
        client_risk = client_factors.get('risk_tolerance', '').lower()
        investment_risk = investment_analysis.get('risk_level', '').lower()
        
        suitable = True
        rationale_parts = []
        recommendations = []
        
        # Age-based checks
        if client_age > 65 and investment_risk == 'high':
            suitable = False
            rationale_parts.append("High-risk investments may not be suitable for older investors")
            recommendations.append("Consider more conservative investments approaching retirement")
        
        # Risk tolerance matching
        if client_risk == 'conservative' and investment_risk == 'high':
            suitable = False
            rationale_parts.append("Investment risk level exceeds client's risk tolerance")
            recommendations.append("Recommend lower-risk alternatives aligned with conservative profile")
        
        if suitable:
            determination = "SUITABLE"
            rationale = "Investment recommendation appears suitable based on available client information"
        else:
            determination = "UNSUITABLE"
            rationale = "; ".join(rationale_parts)
        
        if not recommendations:
            recommendations = ["Ensure comprehensive suitability review with client", "Document suitability rationale"]
        
        return {
            'determination': determination,
            'rationale': rationale,
            'recommendations': recommendations
        } 