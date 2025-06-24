# Financial Investment Advisor Agent - Architecture Diagrams

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph Frontend
        UI[React UI]
        Components[UI Components]
        State[State Management]
    end

    subgraph Backend
        API[FastAPI Server]
        Services[Business Services]
        Agents[LangGraph Agents]
        LLM[LLM Integration]
    end

    subgraph External
        MarketData[Market Data APIs]
        OpenAI[OpenAI API]
    end

    UI --> API
    API --> Services
    Services --> Agents
    Agents --> LLM
    Services --> MarketData
    LLM --> OpenAI
```

## 2. Request Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant LangGraph
    participant LLM
    participant MarketData

    User->>Frontend: Submit Profile
    Frontend->>API: POST /api/analyze
    API->>LangGraph: Initialize Workflow
    LangGraph->>MarketData: Fetch Market Data
    MarketData-->>LangGraph: Return Data
    LangGraph->>LLM: Process Profile
    LLM-->>LangGraph: Generate Recommendations
    LangGraph-->>API: Return Results
    API-->>Frontend: Send Response
    Frontend-->>User: Display Recommendations
```

## 3. LangGraph Workflow

```mermaid
stateDiagram-v2
    [*] --> AnalyzeProfile
    AnalyzeProfile --> ResearchMarket
    ResearchMarket --> GenerateRecommendations
    GenerateRecommendations --> ExplainRecommendations
    ExplainRecommendations --> [*]

    state AnalyzeProfile {
        [*] --> ValidateInput
        ValidateInput --> ProcessProfile
        ProcessProfile --> [*]
    }

    state ResearchMarket {
        [*] --> FetchMarketData
        FetchMarketData --> AnalyzeConditions
        AnalyzeConditions --> [*]
    }

    state GenerateRecommendations {
        [*] --> CreateStrategy
        CreateStrategy --> CalculateAllocation
        CalculateAllocation --> [*]
    }

    state ExplainRecommendations {
        [*] --> GenerateExplanation
        GenerateExplanation --> FormatResponse
        FormatResponse --> [*]
    }
```

## 4. Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input
        Profile[User Profile]
        Market[Market Data]
    end

    subgraph Processing
        Risk[Risk Assessment]
        Strategy[Strategy Generation]
        Allocation[Asset Allocation]
    end

    subgraph Output
        Recs[Recommendations]
        Explanation[Explanations]
    end

    Profile --> Risk
    Market --> Risk
    Risk --> Strategy
    Strategy --> Allocation
    Allocation --> Recs
    Recs --> Explanation
```

## 5. Component Interaction

```mermaid
graph TB
    subgraph Frontend Components
        ProfileForm[Profile Form]
        RecDisplay[Recommendation Display]
        MarketChart[Market Chart]
        EduResources[Educational Resources]
    end

    subgraph Backend Services
        RiskService[Risk Assessment Service]
        MarketService[Market Data Service]
        RecService[Recommendation Service]
        LLMService[LLM Service]
    end

    ProfileForm --> RiskService
    RiskService --> RecService
    MarketService --> RecService
    RecService --> LLMService
    LLMService --> RecDisplay
    MarketService --> MarketChart
    RecService --> EduResources
```

## 6. Error Handling Flow

```mermaid
graph TD
    A[Request Received] --> B{Input Valid?}
    B -->|No| C[Return 400]
    B -->|Yes| D{Service Available?}
    D -->|No| E[Return 503]
    D -->|Yes| F{LLM Response Valid?}
    F -->|No| G[Fallback Response]
    F -->|Yes| H[Process Response]
    H --> I[Return 200]
    G --> I
```

## 7. State Management

```mermaid
classDiagram
    class AgentState {
        +List[Dict] messages
        +Dict user_profile
        +Dict market_data
        +Dict recommendations
        +str comments
    }

    class UserProfile {
        +int age
        +float income
        +str risk_tolerance
        +List[str] investment_goals
        +str time_horizon
    }

    class Recommendation {
        +Dict asset_allocation
        +List[Dict] specific_recommendations
        +Dict expected_returns
        +Dict risk_metrics
        +Dict explanation
    }

    AgentState --> UserProfile
    AgentState --> Recommendation
```

## 8. API Endpoints Structure

```mermaid
graph TD
    A[API Root] --> B[/api/analyze]
    A --> C[/api/risk-assessment]
    A --> D[/api/recommendations]
    A --> E[/api/market-data]
    
    B --> B1[POST]
    C --> C1[POST]
    D --> D1[GET]
    E --> E1[GET]
```

## 9. Security Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Services

    Client->>API: Request with Token
    API->>Auth: Validate Token
    Auth-->>API: Token Valid
    API->>Services: Process Request
    Services-->>API: Response
    API-->>Client: Secure Response
```

## 10. Caching Strategy

```mermaid
graph TD
    A[Request] --> B{Cache Hit?}
    B -->|Yes| C[Return Cached Data]
    B -->|No| D[Process Request]
    D --> E[Update Cache]
    E --> F[Return Response]
    C --> G[Response]
    F --> G
```

## Notes

1. **System Architecture**
   - Frontend and Backend are clearly separated
   - External services are isolated
   - Clear data flow paths

2. **Request Flow**
   - Sequential processing of user requests
   - Clear interaction between components
   - Error handling at each step

3. **LangGraph Workflow**
   - State-based processing
   - Clear transition between states
   - Modular design for each state

4. **Data Flow**
   - Clear input/output paths
   - Processing steps are well-defined
   - Data transformation points are clear

5. **Component Interaction**
   - Clear service boundaries
   - Defined communication paths
   - Modular design

6. **Error Handling**
   - Multiple validation points
   - Fallback mechanisms
   - Clear error responses

7. **State Management**
   - Clear state structure
   - Well-defined relationships
   - Type safety

8. **API Structure**
   - RESTful design
   - Clear endpoint hierarchy
   - Proper HTTP methods

9. **Security**
   - Token-based authentication
   - Secure communication
   - Service isolation

10. **Caching**
    - Performance optimization
    - Clear cache invalidation
    - Fallback mechanisms 