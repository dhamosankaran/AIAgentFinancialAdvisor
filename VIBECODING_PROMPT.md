# Financial Investment Advisor Agent - Vibecoding Prompt Template

## Project Description
Create a Financial Investment Advisor Agent that provides personalized investment recommendations based on user financial goals, risk tolerance, and market conditions. The application should be user-friendly and accessible to non-technical users.

## Technical Requirements

### Backend Stack
- Framework: FastAPI
- Language: Python 3.9+
- Data Source: Alpha Vantage API
- Database: In-memory (for MVP)
- Testing: pytest

### Frontend Stack
- Framework: React 18+
- UI Components: Material-UI (MUI)
- Charts: Recharts
- Build Tool: Vite

## Core Features to Implement

### 1. User Profile Management
- Age and income input
- Risk tolerance assessment
- Investment goals selection
- Time horizon specification

### 2. Market Data Integration
- Real-time stock data fetching
- Market trend analysis
- Economic indicators monitoring
- Historical data analysis

### 3. Investment Recommendations
- Personalized portfolio suggestions
- Risk-adjusted return calculations
- Asset allocation recommendations
- Investment strategy explanations

### 4. User Interface
- Clean, intuitive dashboard
- Interactive charts and graphs
- Easy-to-understand recommendations
- Educational resources section

## Implementation Guidelines

### 1. Project Structure
```
financial-advisor-agent/
├── src/
│   ├── api/             # FastAPI endpoints
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── frontend/            # React frontend
├── tests/               # Test suite
├── docs/                # Documentation
└── config/              # Configuration files
```

### 2. API Endpoints
- POST /api/v1/profile - Create/update user profile
- GET /api/v1/recommendations - Get investment recommendations
- GET /api/v1/market-data - Fetch market data
- GET /api/v1/education - Get educational resources

### 3. Data Models
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

### 4. Frontend Components
- UserProfileForm
- RecommendationDisplay
- MarketDataChart
- EducationalResources
- NavigationBar

## Security Requirements
- API key management
- Input validation
- Rate limiting
- Error handling
- Data sanitization

## Performance Requirements
- Response time < 2 seconds
- Caching for API calls
- Optimized data fetching
- Efficient state management

## Testing Requirements
- Unit tests for all components
- Integration tests for API
- End-to-end testing
- Performance testing

## Documentation Requirements
- API documentation
- User guide
- Setup instructions
- Troubleshooting guide

## Development Phases

### Phase 1: Basic Setup
1. Project structure creation
2. Environment configuration
3. Dependencies installation
4. Basic API setup

### Phase 2: Core Features
1. User profile management
2. Market data integration
3. Basic recommendations
4. Simple UI implementation

### Phase 3: Enhancement
1. Advanced recommendations
2. UI improvements
3. Performance optimization
4. Additional features

### Phase 4: Finalization
1. Testing completion
2. Documentation
3. Deployment preparation
4. User guide creation

## Code Style Guidelines
- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Write clear comments
- Use meaningful variable names
- Keep functions small and focused

## Error Handling
- Graceful error recovery
- User-friendly error messages
- Proper logging
- Fallback mechanisms

## Accessibility Requirements
- Screen reader support
- Keyboard navigation
- Color contrast compliance
- Responsive design

## Deployment Requirements
- Environment variables
- Build process
- Deployment scripts
- Monitoring setup

## Maintenance Guidelines
- Regular updates
- Security patches
- Performance monitoring
- User feedback integration

## Success Criteria
1. All core features implemented
2. Passing test suite
3. Complete documentation
4. User-friendly interface
5. Performance requirements met
6. Security requirements met

## Additional Notes
- Focus on user experience
- Prioritize code quality
- Maintain scalability
- Consider future enhancements

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