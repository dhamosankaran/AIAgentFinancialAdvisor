"""
Mock data for testing
"""

MOCK_MARKET_DATA = {
    "sources": {
        "alpha_vantage": {
            "SPY": {
                "price": 450.25,
                "change": 2.5,
                "change_percent": 0.56,
                "volume": 50000000
            }
        }
    },
    "market_sentiment": "Bullish",
    "timestamp": "2024-03-20T10:00:00Z"
}

MOCK_PORTFOLIO = {
    "stocks": 100000,
    "bonds": 50000,
    "cash": 25000,
    "real_estate": 25000
}

MOCK_RISK_PROFILE = {
    "age": 35,
    "income": 150000,
    "risk_tolerance": "moderate",
    "investment_goals": "retirement",
    "time_horizon": "long_term"
} 