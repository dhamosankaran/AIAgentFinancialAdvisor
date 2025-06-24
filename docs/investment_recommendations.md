# Investment Recommendations (MVP)

## Overview
This document describes the investment recommendation methodology for the MVP version of the Financial Investment Advisor Agent.

## Recommendation Process

### Input Factors
1. **Risk Assessment**
   - Risk score
   - Risk category
   - Investment goals

2. **Market Conditions**
   - Current market state
   - Sector performance
   - Economic indicators

### Asset Allocation

#### Conservative Portfolio
```python
CONSERVATIVE_ALLOCATION = {
    "stocks": 30,
    "bonds": 60,
    "cash": 10
}
```

#### Moderate Portfolio
```python
MODERATE_ALLOCATION = {
    "stocks": 60,
    "bonds": 35,
    "cash": 5
}
```

#### Aggressive Portfolio
```python
AGGRESSIVE_ALLOCATION = {
    "stocks": 80,
    "bonds": 15,
    "cash": 5
}
```

## Implementation

### Recommendation Service
```python
class RecommendationService:
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
        self.allocations = {
            "conservative": CONSERVATIVE_ALLOCATION,
            "moderate": MODERATE_ALLOCATION,
            "aggressive": AGGRESSIVE_ALLOCATION
        }
        
    async def generate_recommendations(self, risk_assessment: Dict) -> Dict:
        """
        Generate investment recommendations based on risk assessment
        """
        allocation = self.allocations[risk_assessment["category"]]
        market_data = await self.market_data.get_market_overview()
        
        recommendations = {
            "asset_allocation": allocation,
            "specific_investments": self._get_specific_investments(
                allocation,
                market_data
            ),
            "market_conditions": market_data,
            "risk_metrics": self._calculate_risk_metrics(allocation)
        }
        
        return recommendations
```

### Specific Investments

#### Stock Recommendations
```python
STOCK_ETFS = {
    "conservative": ["VTI", "VXUS"],
    "moderate": ["VTI", "VXUS", "QQQ"],
    "aggressive": ["VTI", "VXUS", "QQQ", "ARKK"]
}
```

#### Bond Recommendations
```python
BOND_ETFS = {
    "conservative": ["BND", "BNDX"],
    "moderate": ["BND", "BNDX"],
    "aggressive": ["BND"]
}
```

## Testing

### Test Cases
1. Allocation calculation
2. Specific investment selection
3. Market condition integration
4. Risk metric calculation

### Mock Data
```python
TEST_RECOMMENDATIONS = {
    "conservative": {
        "stocks": ["VTI", "VXUS"],
        "bonds": ["BND", "BNDX"],
        "cash": 10
    },
    "moderate": {
        "stocks": ["VTI", "VXUS", "QQQ"],
        "bonds": ["BND", "BNDX"],
        "cash": 5
    }
}
```

## Best Practices

### Development
- Validate all inputs
- Handle market data errors
- Document assumptions
- Add logging

### Recommendations
- Clear explanations
- Conservative defaults
- Regular updates
- Transparent methodology

## Future Enhancements
1. Add more investment options
2. Implement portfolio optimization
3. Add tax considerations
4. Improve risk metrics
5. Add historical performance 