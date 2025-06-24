# API Documentation

This document describes the API endpoints available in the Financial Investment Advisor Agent.

## Table of Contents
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Models](#models)
- [Error Handling](#error-handling)

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication for the MVP version.

## Endpoints

### User Interests

#### Submit User Interests
```
POST /interests
```

Submit user financial interests and preferences.

**Request Body:**
```json
{
  "age": 35,
  "income": 100000,
  "risk_tolerance": "moderate",
  "investment_goals": ["retirement", "wealth_building"],
  "time_horizon": "20_years"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "age": 35,
  "income": 100000,
  "risk_tolerance": "moderate",
  "investment_goals": ["retirement", "wealth_building"],
  "time_horizon": "20_years",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Recommendations

#### Get Investment Recommendations
```
GET /recommendations
```

Get personalized investment recommendations based on user interests.

**Response:**
```json
{
  "recommendations": [
    {
      "asset_class": "stocks",
      "allocation": 60,
      "reasoning": "Based on your moderate risk tolerance and long-term goals"
    },
    {
      "asset_class": "bonds",
      "allocation": 30,
      "reasoning": "To provide stability and income"
    },
    {
      "asset_class": "cash",
      "allocation": 10,
      "reasoning": "For liquidity and emergency fund"
    }
  ],
  "market_conditions": {
    "overview": "Current market conditions are favorable for long-term investments",
    "risk_level": "moderate"
  }
}
```

### Market Data

#### Get Market Overview
```
GET /market/overview
```

Get current market overview and conditions.

**Response:**
```json
{
  "market_conditions": {
    "overview": "Current market conditions are favorable for long-term investments",
    "risk_level": "moderate",
    "trend": "bullish",
    "volatility": "low"
  },
  "key_indicators": {
    "sp500": {
      "current": 4500.0,
      "change": 1.5,
      "change_percent": 0.03
    },
    "nasdaq": {
      "current": 15000.0,
      "change": 2.0,
      "change_percent": 0.04
    }
  }
}
```

## Models

### User Interests
```python
class UserInterests(BaseModel):
    age: int
    income: float
    risk_tolerance: str
    investment_goals: List[str]
    time_horizon: str
```

### Investment Recommendations
```python
class AssetRecommendation(BaseModel):
    asset_class: str
    allocation: float
    reasoning: str

class MarketConditions(BaseModel):
    overview: str
    risk_level: str

class RecommendationsResponse(BaseModel):
    recommendations: List[AssetRecommendation]
    market_conditions: MarketConditions
```

### Market Data
```python
class MarketIndicator(BaseModel):
    current: float
    change: float
    change_percent: float

class MarketOverview(BaseModel):
    overview: str
    risk_level: str
    trend: str
    volatility: str

class MarketDataResponse(BaseModel):
    market_conditions: MarketOverview
    key_indicators: Dict[str, MarketIndicator]
```

## Error Handling

The API uses standard HTTP status codes and returns error messages in JSON format.

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Error Codes
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

### Example Error Response
```json
{
  "detail": "Invalid input data: age must be between 18 and 100"
}
``` 