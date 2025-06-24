# Feature Integration Design

## 1. Frontend Structure

### 1.1 Component Organization
```
frontend/
├── src/
│   ├── components/
│   │   ├── education/
│   │   │   ├── InvestmentConcepts.tsx
│   │   │   ├── RiskExplanation.tsx
│   │   │   ├── MarketTerminology.tsx
│   │   │   ├── Calculators.tsx
│   │   │   └── FAQ.tsx
│   │   ├── portfolio/
│   │   │   ├── PerformanceDisplay.tsx
│   │   │   ├── AllocationChart.tsx
│   │   │   ├── HistoricalRecommendations.tsx
│   │   │   └── GoalProgress.tsx
│   │   ├── profile/
│   │   │   ├── RiskAssessment.tsx
│   │   │   ├── GoalSetting.tsx
│   │   │   ├── InvestmentHistory.tsx
│   │   │   └── Preferences.tsx
│   │   └── market/
│   │       ├── MarketTrends.tsx
│   │       ├── SectorAnalysis.tsx
│   │       ├── EconomicIndicators.tsx
│   │       └── NewsFeed.tsx
│   ├── pages/
│   │   ├── Education.tsx
│   │   ├── Portfolio.tsx
│   │   ├── Profile.tsx
│   │   └── Market.tsx
│   └── services/
       ├── educationService.ts
       ├── portfolioService.ts
       ├── profileService.ts
       └── marketService.ts
```

### 1.2 Key UI Components

#### Education Section
```typescript
// InvestmentConcepts.tsx
interface Concept {
  title: string;
  description: string;
  examples: string[];
  relatedTerms: string[];
}

const InvestmentConcepts: React.FC = () => {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  
  return (
    <div className="concepts-container">
      {concepts.map(concept => (
        <ConceptCard
          key={concept.title}
          title={concept.title}
          description={concept.description}
          examples={concept.examples}
          relatedTerms={concept.relatedTerms}
        />
      ))}
    </div>
  );
};
```

#### Portfolio Tracking
```typescript
// PerformanceDisplay.tsx
interface Performance {
  currentValue: number;
  change: number;
  changePercentage: number;
  timeRange: string;
}

const PerformanceDisplay: React.FC = () => {
  const [performance, setPerformance] = useState<Performance>({});
  
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

## 2. Backend Structure

### 2.1 API Endpoints
```python
# src/api/main.py

# Education Endpoints
@app.get("/api/education/concepts")
async def get_investment_concepts():
    return await education_service.get_concepts()

@app.get("/api/education/risk")
async def get_risk_explanation():
    return await education_service.get_risk_explanation()

# Portfolio Endpoints
@app.get("/api/portfolio/performance")
async def get_portfolio_performance():
    return await portfolio_service.get_performance()

@app.get("/api/portfolio/allocation")
async def get_portfolio_allocation():
    return await portfolio_service.get_allocation()

# Profile Endpoints
@app.post("/api/profile/risk-assessment")
async def update_risk_assessment(assessment: RiskAssessment):
    return await profile_service.update_risk_assessment(assessment)

@app.get("/api/profile/history")
async def get_investment_history():
    return await profile_service.get_history()

# Market Endpoints
@app.get("/api/market/trends")
async def get_market_trends():
    return await market_service.get_trends()

@app.get("/api/market/news")
async def get_market_news():
    return await market_service.get_news()
```

### 2.2 Service Layer
```python
# src/services/education_service.py
class EducationService:
    async def get_concepts(self) -> List[Dict]:
        # Fetch from database or external source
        return concepts

    async def get_risk_explanation(self) -> Dict:
        # Generate risk explanation using LLM
        return explanation

# src/services/portfolio_service.py
class PortfolioService:
    async def get_performance(self) -> Dict:
        # Calculate portfolio performance
        return performance

    async def get_allocation(self) -> Dict:
        # Get current allocation
        return allocation

# src/services/profile_service.py
class ProfileService:
    async def update_risk_assessment(self, assessment: RiskAssessment) -> Dict:
        # Update risk assessment
        return updated_assessment

    async def get_history(self) -> List[Dict]:
        # Get investment history
        return history

# src/services/market_service.py
class MarketService:
    async def get_trends(self) -> Dict:
        # Get market trends
        return trends

    async def get_news(self) -> List[Dict]:
        # Get market news
        return news
```

### 2.3 Data Models
```python
# src/models/education.py
class Concept(BaseModel):
    title: str
    description: str
    examples: List[str]
    related_terms: List[str]

# src/models/portfolio.py
class Performance(BaseModel):
    current_value: float
    change: float
    change_percentage: float
    time_range: str

# src/models/profile.py
class RiskAssessment(BaseModel):
    risk_score: float
    risk_level: str
    factors: Dict[str, float]
    recommendations: List[str]

# src/models/market.py
class MarketTrend(BaseModel):
    indicator: str
    value: float
    change: float
    trend: str
```

## 3. Integration Steps

### 3.1 Frontend Integration
1. Add new routes in React Router
2. Create new components
3. Implement service calls
4. Add state management
5. Style components

### 3.2 Backend Integration
1. Add new endpoints
2. Implement services
3. Create data models
4. Add database schemas
5. Implement caching

### 3.3 Database Updates
```sql
-- Education Tables
CREATE TABLE concepts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    examples JSONB,
    related_terms JSONB
);

-- Portfolio Tables
CREATE TABLE portfolio_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    current_value DECIMAL,
    change DECIMAL,
    change_percentage DECIMAL,
    time_range VARCHAR(50),
    timestamp TIMESTAMP
);

-- Profile Tables
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    risk_score DECIMAL,
    risk_level VARCHAR(50),
    factors JSONB,
    recommendations JSONB,
    timestamp TIMESTAMP
);

-- Market Tables
CREATE TABLE market_trends (
    id SERIAL PRIMARY KEY,
    indicator VARCHAR(100),
    value DECIMAL,
    change DECIMAL,
    trend VARCHAR(50),
    timestamp TIMESTAMP
);
```

## 4. Implementation Phases

### Phase 1: Education Content
1. Implement basic concept display
2. Add risk explanation
3. Create market terminology
4. Build simple calculators
5. Add FAQ section

### Phase 2: Portfolio Tracking
1. Add performance display
2. Implement allocation visualization
3. Create historical recommendations
4. Add goal progress tracking

### Phase 3: User Profile
1. Enhance risk assessment
2. Improve goal setting
3. Add investment history
4. Implement preferences

### Phase 4: Market Insights
1. Add market trends
2. Implement sector analysis
3. Add economic indicators
4. Integrate news feed

## 5. Testing Strategy

### 5.1 Frontend Tests
```typescript
// Education component tests
describe('InvestmentConcepts', () => {
  it('should display concepts correctly', () => {
    // Test implementation
  });
  
  it('should handle loading state', () => {
    // Test implementation
  });
});

// Portfolio component tests
describe('PerformanceDisplay', () => {
  it('should show correct performance data', () => {
    // Test implementation
  });
});
```

### 5.2 Backend Tests
```python
# Education service tests
def test_get_concepts():
    # Test implementation

# Portfolio service tests
def test_get_performance():
    # Test implementation
```

## 6. Deployment Considerations

### 6.1 Frontend
- Build optimization
- Asset compression
- Cache configuration
- CDN setup

### 6.2 Backend
- API rate limiting
- Caching strategy
- Database indexing
- Load balancing

## 7. Monitoring and Maintenance

### 7.1 Metrics to Track
- API response times
- Error rates
- User engagement
- Feature usage

### 7.2 Maintenance Tasks
- Regular updates
- Performance optimization
- Security patches
- Content updates 