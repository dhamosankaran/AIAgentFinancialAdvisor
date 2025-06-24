# Implementation Plan

## Current Status Analysis
The codebase follows a well-structured organization with clear separation of concerns:
- Backend: FastAPI-based architecture with services, agents, and API layers
- Frontend: React-based application with TypeScript support
- Testing: Jest and Cypress for comprehensive testing

## Phase 1: Education Content Integration

### 1.1 Backend Implementation
1. Create education service
```python
# src/services/education_service.py
from typing import List, Dict
from fastapi import HTTPException
from ..models.education import Concept, RiskExplanation

class EducationService:
    def __init__(self):
        self.concepts_db = {}  # Will be replaced with actual database
        self.risk_explanations = {}

    async def get_concepts(self) -> List[Concept]:
        try:
            return list(self.concepts_db.values())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_risk_explanation(self) -> RiskExplanation:
        try:
            return self.risk_explanations.get("default")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

2. Add education endpoints
```python
# src/api/education.py
from fastapi import APIRouter, Depends
from ..services.education_service import EducationService

router = APIRouter(prefix="/education", tags=["education"])

@router.get("/concepts")
async def get_concepts(service: EducationService = Depends()):
    return await service.get_concepts()

@router.get("/risk")
async def get_risk_explanation(service: EducationService = Depends()):
    return await service.get_risk_explanation()
```

### 1.2 Frontend Implementation
1. Create education components
```typescript
// frontend/src/components/education/InvestmentConcepts.tsx
import React, { useEffect, useState } from 'react';
import { Concept } from '../../types/education';
import { educationService } from '../../services/educationService';

export const InvestmentConcepts: React.FC = () => {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConcepts = async () => {
      try {
        const data = await educationService.getConcepts();
        setConcepts(data);
      } catch (error) {
        console.error('Error fetching concepts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConcepts();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="concepts-container">
      {concepts.map(concept => (
        <ConceptCard key={concept.id} concept={concept} />
      ))}
    </div>
  );
};
```

2. Add education service
```typescript
// frontend/src/services/educationService.ts
import { Concept, RiskExplanation } from '../types/education';
import { api } from './api';

export const educationService = {
  async getConcepts(): Promise<Concept[]> {
    const response = await api.get('/education/concepts');
    return response.data;
  },

  async getRiskExplanation(): Promise<RiskExplanation> {
    const response = await api.get('/education/risk');
    return response.data;
  }
};
```

## Phase 2: Portfolio Tracking Integration

### 2.1 Backend Implementation
1. Create portfolio service
```python
# src/services/portfolio_service.py
from typing import Dict
from fastapi import HTTPException
from ..models.portfolio import Performance, Allocation

class PortfolioService:
    def __init__(self):
        self.performance_db = {}  # Will be replaced with actual database
        self.allocation_db = {}

    async def get_performance(self, user_id: int) -> Performance:
        try:
            return self.performance_db.get(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_allocation(self, user_id: int) -> Allocation:
        try:
            return self.allocation_db.get(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

2. Add portfolio endpoints
```python
# src/api/portfolio.py
from fastapi import APIRouter, Depends
from ..services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/performance/{user_id}")
async def get_performance(
    user_id: int,
    service: PortfolioService = Depends()
):
    return await service.get_performance(user_id)

@router.get("/allocation/{user_id}")
async def get_allocation(
    user_id: int,
    service: PortfolioService = Depends()
):
    return await service.get_allocation(user_id)
```

### 2.2 Frontend Implementation
1. Create portfolio components
```typescript
// frontend/src/components/portfolio/PerformanceDisplay.tsx
import React, { useEffect, useState } from 'react';
import { Performance } from '../../types/portfolio';
import { portfolioService } from '../../services/portfolioService';

export const PerformanceDisplay: React.FC = () => {
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPerformance = async () => {
      try {
        const data = await portfolioService.getPerformance();
        setPerformance(data);
      } catch (error) {
        console.error('Error fetching performance:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPerformance();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!performance) return <div>No performance data available</div>;

  return (
    <div className="performance-container">
      <ValueDisplay
        label="Current Value"
        value={performance.currentValue}
        format="currency"
      />
      <ChangeIndicator
        value={performance.change}
        percentage={performance.changePercentage}
      />
    </div>
  );
};
```

## Phase 3: User Profile Enhancement

### 3.1 Backend Implementation
1. Create profile service
```python
# src/services/profile_service.py
from typing import Dict, List
from fastapi import HTTPException
from ..models.profile import RiskAssessment, InvestmentHistory

class ProfileService:
    def __init__(self):
        self.risk_assessments = {}  # Will be replaced with actual database
        self.investment_history = {}

    async def update_risk_assessment(
        self,
        user_id: int,
        assessment: RiskAssessment
    ) -> RiskAssessment:
        try:
            self.risk_assessments[user_id] = assessment
            return assessment
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_investment_history(
        self,
        user_id: int
    ) -> List[InvestmentHistory]:
        try:
            return self.investment_history.get(user_id, [])
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

### 3.2 Frontend Implementation
1. Create profile components
```typescript
// frontend/src/components/profile/RiskAssessment.tsx
import React, { useState } from 'react';
import { RiskAssessment } from '../../types/profile';
import { profileService } from '../../services/profileService';

export const RiskAssessmentForm: React.FC = () => {
  const [assessment, setAssessment] = useState<RiskAssessment>({
    riskScore: 0,
    riskLevel: 'medium',
    factors: {},
    recommendations: []
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await profileService.updateRiskAssessment(assessment);
      // Handle success
    } catch (error) {
      console.error('Error updating risk assessment:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

## Phase 4: Market Insights Integration

### 4.1 Backend Implementation
1. Create market service
```python
# src/services/market_service.py
from typing import Dict, List
from fastapi import HTTPException
from ..models.market import MarketTrend, NewsItem

class MarketService:
    def __init__(self):
        self.trends_db = {}  # Will be replaced with actual database
        self.news_db = {}

    async def get_trends(self) -> List[MarketTrend]:
        try:
            return list(self.trends_db.values())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_news(self) -> List[NewsItem]:
        try:
            return list(self.news_db.values())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

### 4.2 Frontend Implementation
1. Create market components
```typescript
// frontend/src/components/market/MarketTrends.tsx
import React, { useEffect, useState } from 'react';
import { MarketTrend } from '../../types/market';
import { marketService } from '../../services/marketService';

export const MarketTrends: React.FC = () => {
  const [trends, setTrends] = useState<MarketTrend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const data = await marketService.getTrends();
        setTrends(data);
      } catch (error) {
        console.error('Error fetching market trends:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="market-trends-container">
      {trends.map(trend => (
        <TrendCard key={trend.id} trend={trend} />
      ))}
    </div>
  );
};
```

## Testing Strategy

### Backend Tests
```python
# tests/services/test_education_service.py
import pytest
from src.services.education_service import EducationService

@pytest.mark.asyncio
async def test_get_concepts():
    service = EducationService()
    concepts = await service.get_concepts()
    assert isinstance(concepts, list)
    assert len(concepts) > 0

@pytest.mark.asyncio
async def test_get_risk_explanation():
    service = EducationService()
    explanation = await service.get_risk_explanation()
    assert explanation is not None
```

### Frontend Tests
```typescript
// frontend/src/components/education/__tests__/InvestmentConcepts.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { InvestmentConcepts } from '../InvestmentConcepts';
import { educationService } from '../../../services/educationService';

jest.mock('../../../services/educationService');

describe('InvestmentConcepts', () => {
  it('renders concepts correctly', async () => {
    const mockConcepts = [
      {
        id: 1,
        title: 'Test Concept',
        description: 'Test Description',
        examples: ['Example 1'],
        relatedTerms: ['Term 1']
      }
    ];

    (educationService.getConcepts as jest.Mock).mockResolvedValue(mockConcepts);

    render(<InvestmentConcepts />);

    await waitFor(() => {
      expect(screen.getByText('Test Concept')).toBeInTheDocument();
    });
  });
});
```

## Deployment Checklist

### Backend
- [ ] Set up database migrations
- [ ] Configure environment variables
- [ ] Set up API rate limiting
- [ ] Implement caching strategy
- [ ] Configure logging
- [ ] Set up monitoring

### Frontend
- [ ] Configure build optimization
- [ ] Set up asset compression
- [ ] Configure CDN
- [ ] Implement error tracking
- [ ] Set up analytics
- [ ] Configure PWA features

## Next Steps
1. Begin implementation of Phase 1 (Education Content)
2. Set up database schema
3. Create initial API endpoints
4. Implement basic frontend components
5. Add tests for implemented features 