# Frontend Development (MVP)

## Overview
This document describes the frontend implementation for the MVP version of the Financial Investment Advisor Agent.

## Technical Stack

### Core Technologies
- React 18+
- TypeScript
- Material-UI (MUI)
- Vite
- Axios

### Key Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@mui/material": "^5.15.0",
    "@mui/icons-material": "^5.15.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0"
  }
}
```

## Project Structure
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── services/      # API integration
│   ├── types/         # TypeScript types
│   ├── utils/         # Utility functions
│   └── App.tsx        # Main application
├── public/            # Static assets
└── package.json       # Dependencies
```

## Components

### Interest Form
```typescript
interface InterestFormProps {
  onSubmit: (data: InterestData) => void;
}

interface InterestData {
  age: number;
  income: number;
  riskTolerance: string;
  goals: string[];
  timeHorizon: string;
}
```

### Market Overview
```typescript
interface MarketOverviewProps {
  data: MarketData;
}

interface MarketData {
  sp500: MarketIndex;
  nasdaq: MarketIndex;
  sectors: SectorPerformance[];
}
```

### Recommendations
```typescript
interface RecommendationsProps {
  data: RecommendationData;
}

interface RecommendationData {
  assetAllocation: AssetAllocation;
  specificInvestments: Investment[];
  riskMetrics: RiskMetrics;
}
```

## Implementation

### API Service
```typescript
class APIService {
  private baseURL: string;
  
  constructor() {
    this.baseURL = 'http://localhost:8000/api/v1';
  }
  
  async submitInterests(data: InterestData): Promise<Response> {
    return axios.post(`${this.baseURL}/interests`, data);
  }
  
  async getRecommendations(): Promise<RecommendationData> {
    return axios.get(`${this.baseURL}/recommendations`);
  }
  
  async getMarketOverview(): Promise<MarketData> {
    return axios.get(`${this.baseURL}/market/overview`);
  }
}
```

### Main Application
```typescript
function App() {
  const [step, setStep] = useState(1);
  const [interests, setInterests] = useState<InterestData | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationData | null>(null);
  
  const handleSubmitInterests = async (data: InterestData) => {
    await apiService.submitInterests(data);
    setInterests(data);
    setStep(2);
  };
  
  const handleGetRecommendations = async () => {
    const data = await apiService.getRecommendations();
    setRecommendations(data);
    setStep(3);
  };
  
  return (
    <Container>
      {step === 1 && <InterestForm onSubmit={handleSubmitInterests} />}
      {step === 2 && <MarketOverview onNext={handleGetRecommendations} />}
      {step === 3 && <Recommendations data={recommendations} />}
    </Container>
  );
}
```

## Testing

### Component Tests
```typescript
describe('InterestForm', () => {
  it('submits form data correctly', () => {
    const onSubmit = jest.fn();
    render(<InterestForm onSubmit={onSubmit} />);
    
    // Test form submission
  });
  
  it('validates input fields', () => {
    render(<InterestForm onSubmit={jest.fn()} />);
    
    // Test input validation
  });
});
```

### Integration Tests
```typescript
describe('App Integration', () => {
  it('completes full user flow', async () => {
    render(<App />);
    
    // Test complete user flow
  });
});
```

## Best Practices

### Development
- Use TypeScript for type safety
- Follow React best practices
- Implement proper error handling
- Add loading states
- Use proper form validation

### UI/UX
- Responsive design
- Clear error messages
- Loading indicators
- Consistent styling
- Accessible components

## Future Enhancements
1. Add more interactive charts
2. Implement dark mode
3. Add animations
4. Improve mobile experience
5. Add more customization options 