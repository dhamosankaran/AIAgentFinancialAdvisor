from typing import Annotated, Sequence, TypedDict
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from .market_analysis_agent import MarketAnalysisAgent
from .risk_assessment_agent import RiskAssessmentAgent
from .portfolio_agent import PortfolioAgent
from .coordinator_agent import CoordinatorAgent

# Define the state type for our graph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    next: Annotated[str, "The next agent to call"]

def create_agent_workflow():
    # Initialize the agents
    market_agent = MarketAnalysisAgent()
    risk_agent = RiskAssessmentAgent()
    portfolio_agent = PortfolioAgent()
    coordinator = CoordinatorAgent()

    # Define the workflow
    workflow = StateGraph(AgentState)

    # Add nodes for each agent
    workflow.add_node("market_analysis", market_agent.analyze)
    workflow.add_node("risk_assessment", risk_agent.assess)
    workflow.add_node("portfolio_management", portfolio_agent.manage)
    workflow.add_node("coordination", coordinator.coordinate)

    # Define the edges
    workflow.add_edge("market_analysis", "risk_assessment")
    workflow.add_edge("risk_assessment", "portfolio_management")
    workflow.add_edge("portfolio_management", "coordination")

    # Set the entry point
    workflow.set_entry_point("market_analysis")

    # Set the exit point
    workflow.set_finish_point("coordination")

    return workflow.compile()

def run_workflow(user_input: str):
    # Create the workflow
    workflow = create_agent_workflow()

    # Initialize the state
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "next": "market_analysis"
    }

    # Run the workflow
    result = workflow.invoke(initial_state)
    return result 