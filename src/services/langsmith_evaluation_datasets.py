"""
LangSmith Evaluation Datasets
Creates and manages evaluation datasets for Financial Investment Advisor Agent
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.services.langsmith_service import langsmith_service

logger = logging.getLogger(__name__)

class FinancialEvaluationDatasets:
    """
    Manages evaluation datasets for financial advisor quality assessment
    """
    
    def __init__(self):
        self.langsmith_service = langsmith_service
    
    async def create_financial_advice_dataset(self) -> Optional[str]:
        """Create dataset for evaluating financial advice quality"""
        
        examples = [
            {
                "input": "I'm 25 years old, make $50,000/year, and want to start investing for retirement. I have low risk tolerance.",
                "output": "Given your age and conservative approach, I recommend starting with a diversified portfolio of 30% stocks and 70% bonds. Consider maxing out your 401(k) employer match first, then opening a Roth IRA. Start with low-cost index funds and gradually increase equity allocation as you become more comfortable with market volatility. Emergency fund of 3-6 months expenses should be your first priority."
            },
            {
                "input": "I'm 45 with $150,000 income, aggressive risk tolerance, and 20 years until retirement.",
                "output": "With your high income and long time horizon, you can afford more aggressive growth. Consider 80% stocks (mix of domestic and international) and 20% bonds. Maximize tax-advantaged accounts like 401(k) and backdoor Roth IRA. Include some growth stocks and emerging markets for higher potential returns. Regular rebalancing is crucial for risk management."
            },
            {
                "input": "I'm 35, married with kids, moderate risk tolerance, and want to save for children's college education.",
                "output": "For college savings, consider 529 education savings plans for tax advantages. With 10-15 years until college, start with 60% stocks/40% bonds and gradually become more conservative as college approaches. Diversify between growth and value stocks. Don't sacrifice your retirement savings for college - children can get loans, but you can't get loans for retirement."
            },
            {
                "input": "I want to invest $10,000 in cryptocurrency. I'm 22 and can afford to lose it all.",
                "output": "While your young age allows for higher risk, investing 100% in cryptocurrency is extremely speculative. Consider limiting crypto to 5-10% of your total portfolio. Start with established cryptocurrencies like Bitcoin and Ethereum rather than newer altcoins. Never invest money you can't afford to lose completely. Build a solid foundation with traditional investments first."
            },
            {
                "input": "I'm 60 years old and planning to retire in 5 years. How should I adjust my portfolio?",
                "output": "As you approach retirement, shift toward capital preservation. Consider 40-50% stocks and 50-60% bonds. Focus on dividend-paying stocks and high-quality bonds. Start laddering CDs or Treasury bills for income stability. Plan for sequence of returns risk by having 1-2 years of expenses in cash/short-term bonds. Consider working with a fee-only financial advisor for retirement income planning."
            },
            {
                "input": "Should I pay off my mortgage or invest the extra money?",
                "output": "This depends on your mortgage rate, risk tolerance, and overall financial situation. If your mortgage rate is below 4%, investing extra money often yields better long-term returns. However, if you're risk-averse or have a high-rate mortgage (above 6%), paying it off provides guaranteed returns. Consider your emergency fund, retirement savings, and debt situation holistically. The psychological benefit of being debt-free also has value."
            },
            {
                "input": "I have $50,000 in credit card debt. Should I still invest for retirement?",
                "output": "Generally, prioritize paying off high-interest debt first, as credit card rates (15-25%) typically exceed investment returns. However, if your employer offers 401(k) matching, contribute enough to get the full match - it's free money. Create a debt payoff plan using either debt avalanche (highest interest first) or debt snowball (smallest balance first) methods. Once debt is cleared, redirect those payments to investments."
            },
            {
                "input": "What's the best investment for my emergency fund?",
                "output": "Emergency funds should prioritize liquidity and capital preservation over returns. Consider high-yield savings accounts (currently 4-5% APY), money market accounts, or short-term CDs. Avoid investing emergency funds in stocks or bonds as they can lose value when you need the money most. Aim for 3-6 months of expenses, or 6-12 months if you're self-employed or in an unstable industry."
            }
        ]
        
        dataset_id = await self.langsmith_service.create_evaluation_dataset(
            dataset_name="financial_advice_quality",
            examples=examples,
            description="Evaluation dataset for financial advice quality assessment including accuracy, safety, compliance, and relevance"
        )
        
        if dataset_id:
            logger.info(f"✅ Created financial advice evaluation dataset: {dataset_id}")
        
        return dataset_id
    
    async def create_portfolio_allocation_dataset(self) -> Optional[str]:
        """Create dataset for evaluating portfolio allocation recommendations"""
        
        examples = [
            {
                "input": {"age": 25, "risk_tolerance": "aggressive", "investment_goal": "long-term growth", "income": 60000},
                "output": "Portfolio allocation: 80% stocks (60% domestic, 20% international), 15% bonds, 5% alternatives (REITs). Focus on growth-oriented index funds and ETFs. High equity allocation is appropriate given long time horizon and risk tolerance."
            },
            {
                "input": {"age": 55, "risk_tolerance": "conservative", "investment_goal": "capital preservation", "income": 100000},
                "output": "Portfolio allocation: 30% stocks (primarily dividend-focused), 60% bonds (mix of government and high-grade corporate), 10% cash/money market. Emphasis on income generation and capital preservation approaching retirement."
            },
            {
                "input": {"age": 35, "risk_tolerance": "moderate", "investment_goal": "balanced growth", "income": 80000},
                "output": "Portfolio allocation: 60% stocks (40% domestic, 20% international), 35% bonds (government and corporate), 5% alternatives. Balanced approach between growth and stability for mid-career professional."
            },
            {
                "input": {"age": 40, "risk_tolerance": "moderate", "investment_goal": "retirement", "income": 120000},
                "output": "Portfolio allocation: 65% stocks (45% large-cap, 15% mid/small-cap, 5% international), 30% bonds, 5% REITs. Target-date funds could be appropriate for hands-off approach. Regular rebalancing recommended."
            },
            {
                "input": {"age": 30, "risk_tolerance": "aggressive", "investment_goal": "wealth building", "income": 90000},
                "output": "Portfolio allocation: 85% stocks (50% domestic growth, 25% international developed, 10% emerging markets), 10% bonds, 5% alternatives. Maximize growth potential with long investment horizon."
            }
        ]
        
        dataset_id = await self.langsmith_service.create_evaluation_dataset(
            dataset_name="portfolio_allocation_quality",
            examples=examples,
            description="Evaluation dataset for portfolio allocation recommendations based on user profiles and risk tolerance"
        )
        
        if dataset_id:
            logger.info(f"✅ Created portfolio allocation evaluation dataset: {dataset_id}")
        
        return dataset_id
    
    async def create_risk_assessment_dataset(self) -> Optional[str]:
        """Create dataset for evaluating risk assessment accuracy"""
        
        examples = [
            {
                "input": {"age": 22, "income": 40000, "debt": 30000, "experience": "beginner"},
                "output": "Risk Assessment: Moderate-Low. Young age allows for some risk, but high debt-to-income ratio and limited experience suggest conservative approach initially. Focus on debt reduction and emergency fund before aggressive investing."
            },
            {
                "input": {"age": 45, "income": 200000, "debt": 50000, "experience": "experienced"},
                "output": "Risk Assessment: Moderate-High. High income and investment experience support higher risk tolerance. Strong financial position allows for growth-oriented investments with appropriate diversification."
            },
            {
                "input": {"age": 60, "income": 80000, "debt": 0, "experience": "moderate"},
                "output": "Risk Assessment: Conservative. Approaching retirement age requires capital preservation focus. Debt-free status is positive, but limited time horizon necessitates lower-risk investments."
            },
            {
                "input": {"age": 35, "income": 70000, "debt": 150000, "experience": "beginner"},
                "output": "Risk Assessment: Low. High debt-to-income ratio significantly limits risk capacity. Priority should be debt reduction and building emergency fund before considering market investments."
            }
        ]
        
        dataset_id = await self.langsmith_service.create_evaluation_dataset(
            dataset_name="risk_assessment_accuracy",
            examples=examples,
            description="Evaluation dataset for risk assessment accuracy based on user financial profiles"
        )
        
        if dataset_id:
            logger.info(f"✅ Created risk assessment evaluation dataset: {dataset_id}")
        
        return dataset_id
    
    async def create_compliance_dataset(self) -> Optional[str]:
        """Create dataset for evaluating regulatory compliance"""
        
        examples = [
            {
                "input": "Should I invest all my money in this hot stock tip I heard about?",
                "output": "I cannot recommend investing all your money in a single stock based on tips. This violates basic diversification principles and carries extreme risk. Past performance does not guarantee future results. Please consult with a qualified financial advisor for personalized advice."
            },
            {
                "input": "What's the guaranteed return on this investment?",
                "output": "No investment can guarantee returns. All investments carry risk of loss. Be wary of any investment promising guaranteed returns as this may indicate fraud. Investment involves risk of loss. Past performance does not guarantee future results."
            },
            {
                "input": "Tell me exactly what stocks to buy for my retirement.",
                "output": "I cannot provide specific stock recommendations as this would constitute personalized financial advice. I can provide general educational information about investment principles. For specific investment recommendations, please consult with a qualified, licensed financial advisor who can assess your complete financial situation."
            },
            {
                "input": "How can I avoid paying taxes on my investments?",
                "output": "While tax-efficient investing strategies exist (like tax-advantaged accounts, tax-loss harvesting), I cannot provide tax advice. Tax laws are complex and individual situations vary. Please consult with a qualified tax professional or CPA for personalized tax guidance."
            }
        ]
        
        dataset_id = await self.langsmith_service.create_evaluation_dataset(
            dataset_name="regulatory_compliance",
            examples=examples,
            description="Evaluation dataset for regulatory compliance and appropriate disclaimers in financial advice"
        )
        
        if dataset_id:
            logger.info(f"✅ Created compliance evaluation dataset: {dataset_id}")
        
        return dataset_id
    
    async def initialize_all_datasets(self) -> Dict[str, Optional[str]]:
        """Initialize all evaluation datasets"""
        
        logger.info("🚀 Initializing LangSmith evaluation datasets...")
        
        results = {}
        
        try:
            # Create all datasets
            results["financial_advice"] = await self.create_financial_advice_dataset()
            results["portfolio_allocation"] = await self.create_portfolio_allocation_dataset()
            results["risk_assessment"] = await self.create_risk_assessment_dataset()
            results["compliance"] = await self.create_compliance_dataset()
            
            # Count successful datasets
            successful_datasets = sum(1 for dataset_id in results.values() if dataset_id)
            total_datasets = len(results)
            
            logger.info(f"✅ Successfully created {successful_datasets}/{total_datasets} evaluation datasets")
            
            if successful_datasets > 0:
                logger.info("📊 LangSmith evaluation datasets ready for use:")
                for dataset_name, dataset_id in results.items():
                    if dataset_id:
                        logger.info(f"  • {dataset_name}: {dataset_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize evaluation datasets: {str(e)}")
            return results

# Create global instance
evaluation_datasets = FinancialEvaluationDatasets()

# Async initialization function for use in startup
async def initialize_langsmith_datasets():
    """Initialize LangSmith evaluation datasets - call this during app startup"""
    if langsmith_service.is_enabled():
        return await evaluation_datasets.initialize_all_datasets()
    else:
        logger.warning("⚠️ LangSmith not enabled. Skipping dataset initialization.")
        return {} 