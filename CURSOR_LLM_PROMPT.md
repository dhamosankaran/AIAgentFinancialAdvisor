# Financial Investment Advisor Agent - Cursor LLM Prompt

You are a senior software engineer tasked with building a Financial Investment Advisor Agent. Follow these instructions to create the application using Cursor IDE:

## Project Overview
Build a web application that provides personalized investment recommendations based on user financial goals, risk tolerance, and market conditions. The application should be user-friendly and accessible to non-technical users.

## Technical Stack
- Backend: FastAPI (Python 3.9+)
- Frontend: React 18+ with Material-UI
- Data Source: Alpha Vantage API
- Database: In-memory (for MVP)
- Testing: pytest
- Build Tool: Vite

## Implementation Steps

### 1. Project Setup
1. Create the following directory structure:
```
financial-advisor-agent/
├── src/
│   ├── api/
│   ├── services/
│   └── utils/
├── frontend/
├── tests/
├── docs/
└── config/
```

2. Create essential files:
- requirements.txt
- .env.example
- README.md
- .gitignore
- package.json (for frontend)

### 2. Backend Implementation
1. Create FastAPI application with these endpoints:
   - POST /api/v1/profile
   - GET /api/v1/recommendations
   - GET /api/v1/market-data
   - GET /api/v1/education

2. Implement these core components:
   - User profile management
   - Market data integration
   - Investment recommendations
   - Error handling
   - Input validation
   - API key management

3. Create data models:
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

### 3. Frontend Implementation
1. Create React application with these components:
   - UserProfileForm
   - RecommendationDisplay
   - MarketDataChart
   - EducationalResources
   - NavigationBar

2. Implement features:
   - User profile input
   - Real-time market data display
   - Investment recommendations
   - Educational resources
   - Interactive charts

### 4. Testing
1. Write unit tests for:
   - API endpoints
   - Business logic
   - Frontend components
   - Data models

2. Implement integration tests for:
   - API integration
   - Frontend-backend communication
   - Data flow

### 5. Documentation
1. Create documentation for:
   - API endpoints
   - Setup instructions
   - User guide
   - Troubleshooting guide

## Code Quality Requirements
1. Follow PEP 8 for Python
2. Use ESLint for JavaScript
3. Write clear comments
4. Use meaningful variable names
5. Keep functions small and focused
6. Implement proper error handling
7. Add type hints
8. Write comprehensive tests

## Security Requirements
1. API key management
2. Input validation
3. Rate limiting
4. Error handling
5. Data sanitization

## Performance Requirements
1. Response time < 2 seconds
2. Caching for API calls
3. Optimized data fetching
4. Efficient state management

## Success Criteria
1. All core features implemented
2. Passing test suite
3. Complete documentation
4. User-friendly interface
5. Performance requirements met
6. Security requirements met

## Implementation Guidelines
1. Start with basic setup
2. Implement core features
3. Add testing
4. Enhance UI/UX
5. Optimize performance
6. Add documentation

## Important Notes
1. Use environment variables for sensitive data
2. Implement proper error handling
3. Write comprehensive tests
4. Document all components
5. Follow best practices
6. Consider edge cases
7. Optimize performance
8. Ensure security
9. Make it user-friendly

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