"""
Financial Analysis Pipeline (FAP) Main Workflow
Orchestrates the complete financial analysis process through sequential nodes
"""
from src.models.fap_context import FAPContext
from src.agents.fap_nodes import (
    risk_assessment_node,
    market_analysis_node,
    portfolio_generation_node,
    report_generation_node,
)

import asyncio

async def run_fap_pipeline(context: FAPContext) -> FAPContext:
    """
    Execute the complete Financial Analysis Pipeline
    
    Processes user financial profile through 4 sequential analysis steps:
    1. Risk Assessment - Analyze user risk tolerance and capacity
    2. Market Analysis - Evaluate current market conditions
    3. Portfolio Generation - Create personalized allocation recommendations
    4. Report Generation - Compile comprehensive investment report
    
    Args:
        context (FAPContext): Initial context with user profile
        
    Returns:
        FAPContext: Completed context with all analysis results and history
    """
    context = await risk_assessment_node(context)
    context = await market_analysis_node(context)
    context = await portfolio_generation_node(context)
    context = await report_generation_node(context)
    return context 