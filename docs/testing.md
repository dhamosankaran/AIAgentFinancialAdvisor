# Testing Strategy (MVP)

## Overview
This document describes the testing strategy for the MVP version of the Financial Investment Advisor Agent.

## Testing Levels

### 1. Unit Tests
- Test individual components
- Mock external dependencies
- Focus on business logic

### 2. Integration Tests
- Test component interactions
- Test API endpoints
- Test service integration

### 3. End-to-End Tests
- Test complete user flows
- Test frontend-backend integration
- Test real API calls

## Test Structure

### Backend Tests
```
tests/
├── unit/
│   ├── services/
│   │   ├── test_risk_assessment.py
│   │   ├── test_market_data.py
│   │   └── test_recommendations.py
│   └── utils/
│       └── test_helpers.py
├── integration/
│   ├── test_api.py
│   └── test_services.py
└── e2e/
    └── test_user_flow.py
```

### Frontend Tests
```
frontend/
└── src/
    ├── __tests__/
    │   ├── components/
    │   │   ├── InterestForm.test.tsx
    │   │   ├── MarketOverview.test.tsx
    │   │   └── Recommendations.test.tsx
    │   ├── services/
    │   │   └── api.test.ts
    │   └── App.test.tsx
    └── setupTests.ts
```

## Test Implementation

### Backend Unit Tests
```python
# tests/unit/services/test_risk_assessment.py
def test_calculate_risk_score():
    service = RiskAssessmentService()
    data = InterestData(
        age=30,
        income=100000,
        risk_tolerance="moderate",
        goals=["growth"],
        time_horizon="long_term"
    )
    score = service._calculate_risk_score(data)
    assert 0 <= score <= 100

def test_get_risk_category():
    service = RiskAssessmentService()
    assert service._get_risk_category(25) == "conservative"
    assert service._get_risk_category(50) == "moderate"
    assert service._get_risk_category(75) == "aggressive"
```

### Backend Integration Tests
```python
# tests/integration/test_api.py
def test_submit_interests():
    client = TestClient(app)
    response = client.post("/api/v1/interests", json={
        "age": 30,
        "income": 100000,
        "risk_tolerance": "moderate",
        "goals": ["growth"],
        "time_horizon": "long_term"
    })
    assert response.status_code == 200
    assert "risk_score" in response.json()
```

### Frontend Component Tests
```typescript
// frontend/src/__tests__/components/InterestForm.test.tsx
describe('InterestForm', () => {
  it('submits form data correctly', () => {
    const onSubmit = jest.fn();
    render(<InterestForm onSubmit={onSubmit} />);
    
    fireEvent.change(screen.getByLabelText('Age'), {
      target: { value: '30' }
    });
    
    fireEvent.click(screen.getByText('Submit'));
    
    expect(onSubmit).toHaveBeenCalledWith({
      age: 30,
      income: expect.any(Number),
      riskTolerance: expect.any(String),
      goals: expect.any(Array),
      timeHorizon: expect.any(String)
    });
  });
});
```

### Frontend Integration Tests
```typescript
// frontend/src/__tests__/App.test.tsx
describe('App Integration', () => {
  it('completes full user flow', async () => {
    render(<App />);
    
    // Fill out interest form
    fireEvent.change(screen.getByLabelText('Age'), {
      target: { value: '30' }
    });
    
    // Submit form
    fireEvent.click(screen.getByText('Submit'));
    
    // Wait for recommendations
    await waitFor(() => {
      expect(screen.getByText('Your Recommendations')).toBeInTheDocument();
    });
  });
});
```

## Test Data

### Mock Data
```python
# tests/fixtures/mock_data.py
MOCK_INTEREST_DATA = {
    "age": 30,
    "income": 100000,
    "risk_tolerance": "moderate",
    "goals": ["growth"],
    "time_horizon": "long_term"
}

MOCK_MARKET_DATA = {
    "sp500": {
        "price": 4500.0,
        "change": 1.5,
        "volume": 2000000
    },
    "nasdaq": {
        "price": 15000.0,
        "change": 2.0,
        "volume": 1500000
    }
}
```

## Best Practices

### Development
- Write tests before implementation
- Use meaningful test names
- Keep tests focused and simple
- Mock external dependencies
- Clean up test data

### Testing
- Test edge cases
- Test error conditions
- Test input validation
- Test API responses
- Test UI interactions

## Future Enhancements
1. Add performance tests
2. Add load tests
3. Add security tests
4. Add accessibility tests
5. Add visual regression tests

## Test Coverage

### Coverage Reports
- Generate HTML coverage reports
- Track coverage trends
- Set coverage thresholds
- Monitor uncovered code

### Coverage Commands
```bash
# Generate coverage report
pytest --cov=src --cov-report=html tests/

# Check coverage thresholds
pytest --cov=src --cov-fail-under=80 tests/
```

## Mocking and Fixtures

### API Mocking
```python
@pytest.fixture
def mock_market_data():
    return {
        "symbol": "AAPL",
        "price": 150.0,
        "change": 1.5
    }

@pytest.mark.asyncio
async def test_market_data_service(mock_market_data):
    with patch('src.services.market_data.MarketDataService.get_market_data',
              return_value=mock_market_data):
        service = MarketDataService()
        data = await service.get_market_data("AAPL")
        assert data == mock_market_data
```

### Database Fixtures
```python
@pytest.fixture
async def test_db():
    # Setup test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

## Test Data

### Test Data Management
- Use fixtures for common data
- Generate random test data
- Maintain test data separately
- Document test data structure

### Example Test Data
```python
TEST_USER_PROFILE = {
    "age": 35,
    "income": 100000,
    "risk_tolerance": "moderate",
    "investment_goals": ["retirement", "wealth_building"],
    "time_horizon": "20_years"
}
```

## Continuous Integration

### CI Pipeline
1. Run unit tests
2. Run integration tests
3. Generate coverage report
4. Check coverage thresholds
5. Run security scans
6. Build documentation

### CI Configuration
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Generate coverage
        run: pytest --cov=src --cov-report=xml
```

## Best Practices

### Writing Tests
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Test edge cases
- Keep tests independent
- Mock external dependencies

### Maintaining Tests
- Update tests with code changes
- Remove obsolete tests
- Document test dependencies
- Review test coverage regularly

### Performance
- Run tests in parallel
- Use appropriate fixtures
- Minimize database operations
- Cache test data when possible

## Troubleshooting

### Common Issues
1. **Test Failures**
   - Check test data
   - Verify mocks
   - Review error messages
   - Check dependencies

2. **Performance Issues**
   - Optimize test setup
   - Use appropriate fixtures
   - Parallelize tests
   - Cache test data

3. **Coverage Issues**
   - Identify uncovered code
   - Add missing tests
   - Review test strategy
   - Update coverage thresholds

### Support
For testing-related issues, contact:
- Backend: backend-tests@financial-advisor-agent.com
- Frontend: frontend-tests@financial-advisor-agent.com 