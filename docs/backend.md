# Backend Development (MVP)

## Overview
This document describes the backend implementation for the MVP version of the Financial Investment Advisor Agent.

## Technical Stack

### Core Technologies
- Python 3.9+
- FastAPI
- Pydantic
- SQLite (for MVP)
- Alpha Vantage API

### Key Dependencies
```python
# requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.6.0
python-dotenv==1.0.0
httpx==0.26.0
```

## Project Structure
```
src/
├── api/              # FastAPI endpoints
├── services/         # Business logic
├── models/          # Pydantic models
├── utils/           # Utility functions
└── main.py          # Application entry point
```

## Models

### Interest Model
```python
from pydantic import BaseModel
from typing import List

class InterestData(BaseModel):
    age: int
    income: int
    risk_tolerance: str
    goals: List[str]
    time_horizon: str
```

### Recommendation Model
```python
class AssetAllocation(BaseModel):
    stocks: float
    bonds: float
    cash: float

class Investment(BaseModel):
    symbol: str
    allocation: float
    reasoning: str

class RecommendationData(BaseModel):
    asset_allocation: AssetAllocation
    specific_investments: List[Investment]
    risk_metrics: dict
```

## Implementation

### API Endpoints
```python
from fastapi import FastAPI
from .models import InterestData, RecommendationData

app = FastAPI()

@app.post("/api/v1/interests")
async def submit_interests(data: InterestData):
    risk_assessment = await risk_service.assess_risk(data)
    return {"risk_score": risk_assessment.score}

@app.get("/api/v1/recommendations")
async def get_recommendations():
    recommendations = await recommendation_service.generate_recommendations()
    return recommendations

@app.get("/api/v1/market/overview")
async def get_market_overview():
    market_data = await market_data_service.get_market_overview()
    return market_data
```

### Services

#### Risk Assessment Service
```python
class RiskAssessmentService:
    def __init__(self):
        self.risk_categories = {
            "conservative": (0, 30),
            "moderate": (31, 70),
            "aggressive": (71, 100)
        }
    
    async def assess_risk(self, data: InterestData) -> dict:
        score = self._calculate_risk_score(data)
        category = self._get_risk_category(score)
        return {
            "score": score,
            "category": category
        }
```

#### Market Data Service
```python
class MarketDataService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_market_overview(self) -> dict:
        # Implementation for fetching market data
        pass
```

## Testing

### API Tests
```python
from fastapi.testclient import TestClient

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

### Service Tests
```python
def test_risk_assessment():
    service = RiskAssessmentService()
    data = InterestData(
        age=30,
        income=100000,
        risk_tolerance="moderate",
        goals=["growth"],
        time_horizon="long_term"
    )
    result = service.assess_risk(data)
    assert 0 <= result["score"] <= 100
```

## Best Practices

### Development
- Use type hints
- Follow FastAPI best practices
- Implement proper error handling
- Add logging
- Use environment variables

### API Design
- RESTful endpoints
- Clear error messages
- Proper status codes
- Input validation
- Response models

## Future Enhancements
1. Add database integration
2. Implement authentication
3. Add rate limiting
4. Improve error handling
5. Add more market data sources 