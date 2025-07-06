"""
Risk Assessment Agent for evaluating investment risk profiles
"""

from typing import Dict, List, Optional
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from .base_agent import BaseFinancialAgent

class RiskProfile(BaseModel):
    """Structured input for risk assessment"""
    age: int = Field(description="Age of the investor")
    income: float = Field(description="Annual income")
    risk_tolerance: str = Field(description="Risk tolerance level (conservative/moderate/aggressive)")
    investment_goals: str = Field(description="Primary investment goal")
    time_horizon: str = Field(description="Investment time horizon")

class RiskAssessment(BaseModel):
    """Structured output for risk assessment"""
    risk_score: float = Field(description="Calculated risk score (0-1)")
    risk_level: str = Field(description="Overall risk level (Low/Moderate/High)")
    profile_analysis: Dict[str, str] = Field(description="Analysis of profile factors")
    recommendations: List[str] = Field(description="Investment recommendations")

class RiskAssessmentAgent(BaseFinancialAgent):
    """Agent responsible for risk assessment and profile analysis"""
    
    def __init__(self):
        # Define tools
        tools = [
            Tool(
                name="parse_profile",
                func=self._parse_profile,
                description="Parse user profile information from text"
            ),
            Tool(
                name="calculate_risk_score",
                func=self._calculate_risk_score,
                description="Calculate risk score based on profile data"
            ),
            Tool(
                name="generate_recommendations",
                func=self._generate_recommendations,
                description="Generate investment recommendations based on risk assessment"
            )
        ]
        
        # Initialize with custom system prompt
        system_prompt = """You are a risk assessment expert. Your role is to:
        1. Analyze investor profiles
        2. Calculate risk scores
        3. Provide personalized recommendations
        4. Explain risk factors
        
        Always provide clear, data-driven risk assessments."""
        
        super().__init__(
            tools=tools,
            system_prompt=system_prompt
        )
    
    async def assess_risk(self, profile: str) -> RiskAssessment:
        """Assess investment risk based on user profile"""
        try:
            # Parse profile information
            profile_data = await self._parse_profile(profile)
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(profile_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(risk_score, profile_data)
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = "High"
            elif risk_score >= 0.4:
                risk_level = "Moderate"
            else:
                risk_level = "Low"
            
            # Create structured output
            return RiskAssessment(
                risk_score=risk_score,
                risk_level=risk_level,
                profile_analysis={
                    "age": f"{profile_data.age} years",
                    "income": f"${int(profile_data.income):,}",
                    "risk_tolerance": profile_data.risk_tolerance.title(),
                    "investment_goals": profile_data.investment_goals,
                    "time_horizon": profile_data.time_horizon
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {str(e)}")
            raise
    
    async def _parse_profile(self, profile: str) -> RiskProfile:
        """Parse user profile information from text"""
        # This is a simplified implementation
        # In a real system, you would use NLP to extract structured data
        profile_data = {
            "age": 30,  # Default values
            "income": 100000,
            "risk_tolerance": "moderate",
            "investment_goals": "retirement",
            "time_horizon": "long_term"
        }
        
        # Extract age
        if "year old" in profile.lower():
            try:
                age = int(profile.split("year old")[0].strip().split()[-1])
                profile_data["age"] = age
            except:
                pass
        
        # Extract income
        if "$" in profile:
            try:
                income = int(profile.split("$")[1].split()[0].replace(",", ""))
                profile_data["income"] = income
            except:
                pass
        
        # Extract risk tolerance
        risk_levels = ["conservative", "moderate", "aggressive"]
        for level in risk_levels:
            if level in profile.lower():
                profile_data["risk_tolerance"] = level
                break
        
        return RiskProfile(**profile_data)
    
    async def _calculate_risk_score(self, profile: RiskProfile) -> float:
        """Calculate risk score based on profile data"""
        score = 0.0
        
        # Age factor (0-1)
        if profile.age < 30:
            score += 0.8
        elif profile.age < 50:
            score += 0.5
        else:
            score += 0.2
        
        # Income factor (0-1)
        if profile.income > 200000:
            score += 0.8
        elif profile.income > 100000:
            score += 0.5
        else:
            score += 0.3
        
        # Risk tolerance factor (0-1)
        if profile.risk_tolerance == "aggressive":
            score += 0.8
        elif profile.risk_tolerance == "moderate":
            score += 0.5
        else:
            score += 0.2
        
        # Normalize score to 0-1 range
        return score / 3.0
    
    async def _generate_recommendations(self, risk_score: float, profile: RiskProfile) -> List[str]:
        """Generate investment recommendations based on risk assessment"""
        recommendations = []
        
        if risk_score >= 0.7:
            recommendations.extend([
                "Consider a growth-oriented portfolio",
                "Focus on equities with some alternative investments",
                "Regular portfolio rebalancing recommended"
            ])
        elif risk_score >= 0.4:
            recommendations.extend([
                "Balanced portfolio of stocks and bonds",
                "Consider index funds for core holdings",
                "Quarterly portfolio review recommended"
            ])
        else:
            recommendations.extend([
                "Conservative portfolio with focus on stability",
                "Higher allocation to bonds and cash equivalents",
                "Annual portfolio review sufficient"
            ])
        
        return recommendations
    
    async def process_message(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Process a message and return a response"""
        try:
            # Get structured assessment
            assessment = await self.assess_risk(message)
            
            # Format the response
            response = [
                f"Risk Assessment:",
                f"Overall Risk Level: {assessment.risk_level}",
                f"Risk Score: {assessment.risk_score:.2f}",
                "\nProfile Analysis:",
                *[f"- {key}: {value}" for key, value in assessment.profile_analysis.items()],
                "\nRecommendations:",
                *[f"- {rec}" for rec in assessment.recommendations]
            ]
            
            return "\n".join(response)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}" 