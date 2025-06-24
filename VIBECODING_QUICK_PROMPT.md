# Financial Investment Advisor Agent - Quick Start Prompt

Create a Financial Investment Advisor Agent with the following specifications:

## Core Features
1. User Profile Management
   - Age and income input
   - Risk tolerance assessment
   - Investment goals selection
   - Time horizon specification

2. Market Data Integration
   - Real-time stock data via Alpha Vantage API
   - Market trend analysis
   - Historical data analysis

3. Investment Recommendations
   - Personalized portfolio suggestions
   - Risk-adjusted return calculations
   - Asset allocation recommendations
   - Investment strategy explanations

4. User Interface
   - Clean, intuitive dashboard
   - Interactive charts
   - Easy-to-understand recommendations
   - Educational resources

## Technical Stack
- Backend: FastAPI (Python)
- Frontend: React with Material-UI
- Data Source: Alpha Vantage API
- Charts: Recharts
- Testing: pytest

## Project Structure
```
financial-advisor-agent/
├── src/
│   ├── api/             # FastAPI endpoints
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── frontend/            # React frontend
├── tests/               # Test suite
└── config/              # Configuration files
```

## API Endpoints
- POST /api/v1/profile
- GET /api/v1/recommendations
- GET /api/v1/market-data
- GET /api/v1/education

## Data Models
```python
class UserProfile:
    age: int
    income: float
    risk_tolerance: str
    investment_goals: List[str]
    time_horizon: str

class InvestmentRecommendation:
    portfolio: Dict[str, float]
    risk_score: float
    expected_return: float
    explanation: str
```

## Requirements
1. User-friendly interface
2. Real-time market data
3. Personalized recommendations
4. Educational resources
5. Error handling
6. Input validation
7. API key management
8. Performance optimization
9. Comprehensive testing
10. Clear documentation

## Success Criteria
1. All core features implemented
2. Passing test suite
3. Complete documentation
4. User-friendly interface
5. Performance requirements met
6. Security requirements met

Remember to:
- Write clean, maintainable code
- Include comprehensive tests
- Document all components
- Follow best practices
- Consider edge cases
- Implement proper error handling
- Optimize performance
- Ensure security
- Make it user-friendly 