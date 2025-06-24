# Risk Assessment (MVP)

## Overview
This document describes the risk assessment methodology for the MVP version of the Financial Investment Advisor Agent.

## Risk Factors

### Primary Factors
1. **Age**
   - Younger investors: Higher risk tolerance
   - Older investors: Lower risk tolerance

2. **Income**
   - Higher income: Higher risk tolerance
   - Lower income: Lower risk tolerance

3. **Investment Goals**
   - Growth: Higher risk tolerance
   - Income: Lower risk tolerance
   - Preservation: Lowest risk tolerance

4. **Time Horizon**
   - Long-term (>10 years): Higher risk tolerance
   - Medium-term (5-10 years): Moderate risk tolerance
   - Short-term (<5 years): Lower risk tolerance

## Risk Scoring

### Score Calculation
```python
def calculate_risk_score(age: int, income: int, goals: List[str], horizon: str) -> int:
    """
    Calculate risk score based on user inputs
    Returns score between 0-100
    """
    score = 0
    
    # Age factor (0-30 points)
    if age < 30:
        score += 30
    elif age < 50:
        score += 20
    else:
        score += 10
        
    # Income factor (0-30 points)
    if income > 150000:
        score += 30
    elif income > 75000:
        score += 20
    else:
        score += 10
        
    # Goals factor (0-20 points)
    if "growth" in goals:
        score += 20
    elif "income" in goals:
        score += 10
    else:
        score += 5
        
    # Time horizon factor (0-20 points)
    if horizon == "long_term":
        score += 20
    elif horizon == "medium_term":
        score += 10
    else:
        score += 5
        
    return min(score, 100)
```

### Risk Categories
- **Conservative** (0-30): Focus on capital preservation
- **Moderate** (31-70): Balanced approach
- **Aggressive** (71-100): Growth-oriented

## Implementation

### Risk Assessment Service
```python
class RiskAssessmentService:
    def __init__(self):
        self.risk_categories = {
            "conservative": (0, 30),
            "moderate": (31, 70),
            "aggressive": (71, 100)
        }
        
    def assess_risk(self, user_data: Dict) -> Dict:
        """
        Assess user risk tolerance
        Returns risk score and category
        """
        score = calculate_risk_score(
            age=user_data["age"],
            income=user_data["income"],
            goals=user_data["goals"],
            horizon=user_data["horizon"]
        )
        
        category = self.get_risk_category(score)
        
        return {
            "score": score,
            "category": category,
            "recommendations": self.get_recommendations(category)
        }
```

## Testing

### Test Cases
1. Risk score calculation
2. Risk category assignment
3. Edge cases
4. Input validation

### Mock Data
```python
TEST_CASES = [
    {
        "age": 25,
        "income": 100000,
        "goals": ["growth"],
        "horizon": "long_term",
        "expected_score": 100
    },
    {
        "age": 60,
        "income": 50000,
        "goals": ["preservation"],
        "horizon": "short_term",
        "expected_score": 30
    }
]
```

## Best Practices

### Development
- Validate all inputs
- Handle edge cases
- Document assumptions
- Add logging

### Risk Assessment
- Regular updates
- Clear explanations
- Conservative defaults
- Transparent methodology

## Future Enhancements
1. Add more risk factors
2. Implement machine learning
3. Add historical analysis
4. Improve scoring algorithm
5. Add risk tolerance questionnaire 