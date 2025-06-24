"""
Coordinator Agent for orchestrating the financial advisor system
"""

from typing import Dict, List, Any, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import asyncio
import json
import logging

from .base_agent import BaseFinancialAgent
from .market_analysis_agent import MarketAnalysisAgent
from .risk_assessment_agent import RiskAssessmentAgent
from .portfolio_agent import PortfolioAgent
from ..services.user_profile_service import UserProfileService

class CoordinatorAgent(BaseFinancialAgent):
    """Agent responsible for coordinating between different specialized agents"""
    
    def __init__(self, llm: ChatOpenAI = None, user_profile_service: UserProfileService = None):
        # Initialize specialized agents
        self.market_agent = MarketAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.portfolio_agent = PortfolioAgent()
        self.user_profile_service = user_profile_service or UserProfileService()
        
        # Initialize tools with proper async handling
        tools = [
            Tool(
                name="analyze_market",
                func=self._run_market_analysis,
                description="Analyze current market conditions and trends"
            ),
            Tool(
                name="assess_risk",
                func=self._run_risk_assessment,
                description="Assess investment risk based on user profile and market conditions"
            ),
            Tool(
                name="generate_portfolio",
                func=self._run_portfolio_generation,
                description="Generate investment portfolio recommendations"
            )
        ]
        
        # Define system prompt
        system_prompt = """You are a financial advisor coordinator that helps users make investment decisions.
        You have access to specialized agents for market analysis, risk assessment, and portfolio management.
        Use these tools to provide comprehensive investment advice.
        
        When analyzing a request:
        1. First analyze the market conditions
        2. Then assess the user's risk profile
        3. Finally, generate a suitable portfolio recommendation
        
        Always explain your reasoning and provide clear, actionable advice."""
        
        # Initialize base class
        super().__init__(llm=llm, tools=tools, system_prompt=system_prompt)
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Set up detailed logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
    
    def _run_market_analysis(self, query: str) -> str:
        """Run market analysis with proper error handling"""
        self.logger.debug(f"Starting market analysis with query: {query}")
        try:
            result = asyncio.run(self.market_agent.analyze_market(query))
            self.logger.debug(f"Market analysis result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error in market analysis: {str(e)}", exc_info=True)
            return f"Error analyzing market conditions: {str(e)}"
    
    def _run_risk_assessment(self, profile: str) -> str:
        """Run risk assessment with proper error handling"""
        self.logger.debug(f"Starting risk assessment with profile: {profile}")
        try:
            result = asyncio.run(self.risk_agent.assess_risk(profile))
            self.logger.debug(f"Risk assessment result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {str(e)}", exc_info=True)
            return f"Error assessing risk: {str(e)}"
    
    def _run_portfolio_generation(self, profile: str) -> str:
        """Run portfolio generation with proper error handling"""
        self.logger.debug(f"Starting portfolio generation with profile: {profile}")
        try:
            # Running the async function correctly
            result = asyncio.run(self.portfolio_agent.generate_portfolio(profile))
            self.logger.debug(f"Portfolio generation result: {result}")
            # The result from generate_portfolio is a Pydantic model, so we convert it to a dict and then to a JSON string
            if hasattr(result, 'model_dump_json'):
                return result.model_dump_json()
            return str(result)
        except Exception as e:
            self.logger.error(f"Error in portfolio generation: {str(e)}", exc_info=True)
            return f"Error generating portfolio: {str(e)}"
    
    def _extract_response_content(self, response: Any) -> str:
        """Extract content from various response types"""
        self.logger.debug(f"Extracting content from response type: {type(response)}")
        try:
            if isinstance(response, str):
                self.logger.debug("Response is a string")
                return response
            elif isinstance(response, dict):
                self.logger.debug(f"Response is a dictionary with keys: {list(response.keys())}")
                # Try to get output from different possible keys
                for key in ['output', 'response', 'content', 'text', 'result']:
                    if key in response:
                        self.logger.debug(f"Found content in key: {key}")
                        return str(response[key])
                # If no known keys found, convert dict to string
                self.logger.debug("No known keys found, converting dict to string")
                return json.dumps(response, indent=2)
            elif hasattr(response, 'content'):
                self.logger.debug("Response has content attribute")
                return str(response.content)
            elif hasattr(response, 'output'):
                self.logger.debug("Response has output attribute")
                return str(response.output)
            else:
                self.logger.debug(f"Response is of type {type(response)}, converting to string")
                return str(response)
        except Exception as e:
            self.logger.error(f"Error extracting response content: {str(e)}", exc_info=True)
            return str(response)
    
    async def process_message(self, message: str, user_id: str | None = None) -> str:
        """Process a user message and return a response"""
        self.logger.debug(f"Processing message: {message}")
        self.logger.debug(f"User ID: {user_id}")
        
        try:
            contextual_message = message
            if user_id and self.user_profile_service:
                profile = self.user_profile_service.load_profile()
                if profile:
                    profile_summary = (
                        f"Current user's profile:\n"
                        f"- Name: {profile.name}\n"
                        f"- Age: {profile.age}\n"
                        f"- Income: {profile.income}\n"
                        f"- Risk Tolerance: {profile.risk_tolerance}\n"
                        f"- Investment Goal: {profile.investment_goal}\n"
                        f"- Investment Horizon: {profile.investment_horizon}\n"
                    )
                    contextual_message = (
                        f"Please answer the user's question based on their profile and the investment report context.\n\n"
                        f"---USER PROFILE---\n{profile_summary}\n\n"
                        f"---USER QUESTION---\n{message}"
                    )

            # For this MVP, we are not persisting chat history between calls in the chat bubble.
            lc_chat_history = []
            
            self.logger.debug("Invoking agent executor")
            response = await self.agent_executor.ainvoke({
                "input": contextual_message,
                "chat_history": lc_chat_history
            })
            
            self.logger.debug(f"Agent executor response type: {type(response)}")
            self.logger.debug(f"Agent executor response: {response}")
            
            # Extract and return response content
            result = self._extract_response_content(response)
            self.logger.debug(f"Final extracted response: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    async def generate_comprehensive_report(self, user_profile: Dict) -> Dict[str, Any]:
        """Generate a comprehensive investment report with synchronized allocation data"""
        try:
            # Generate portfolio allocation using the portfolio agent
            risk_level = user_profile.get("risk_tolerance", "moderate").lower()
            allocation_result = await self.portfolio_agent.generate_portfolio(risk_level)
            
            # Convert allocation to the format expected by the frontend
            allocation_list = []
            allocation_dict = allocation_result.model_dump()
            
            for asset_type, percentage in allocation_dict.items():
                allocation_list.append({
                    "asset_type": asset_type,
                    "allocation_percentage": percentage * 100
                })
            
            # Generate the report text with exact percentage matching
            allocation_text_lines = []
            for asset_type, percentage in allocation_dict.items():
                asset_name = asset_type.replace('_', ' ').title()
                if asset_type == "etfs":
                    asset_name = "ETFs"
                elif asset_type == "reits":
                    asset_name = "REITs"
                allocation_text_lines.append(f"**{asset_name} ({int(percentage * 100)}%)**")
            
            # Create comprehensive report sections
            profile_summary = (
                f"Based on your profile (Age: {user_profile.get('age', 'N/A')}, "
                f"Risk Tolerance: {user_profile.get('risk_tolerance', 'N/A')}, "
                f"Investment Goal: {user_profile.get('investment_goal', 'N/A')}, "
                f"Time Horizon: {user_profile.get('investment_horizon', 'N/A')}), "
                f"we recommend a {risk_level} investment approach."
            )
            
            market_outlook = (
                "Current market conditions suggest a balanced approach to asset allocation. "
                "Diversification across multiple asset classes helps manage risk while "
                "maintaining growth potential."
            )
            
            recommendations = (
                f"Your recommended portfolio allocation: {', '.join(allocation_text_lines)}. "
                f"This allocation balances risk and return potential based on your {risk_level} "
                f"risk profile and {user_profile.get('investment_horizon', 'long-term')} investment horizon."
            )
            
            report = f"""Summary:
{profile_summary}

Market Outlook:
{market_outlook}

Recommendations:
{recommendations}"""
            
            return {
                "allocation": allocation_list,
                "report": report,
                "risk_level": risk_level
            }
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {str(e)}", exc_info=True)
            return {
                "allocation": [],
                "report": f"Error generating investment report: {str(e)}",
                "risk_level": "moderate"
            } 