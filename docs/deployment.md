# Deployment Guide (MVP)

## Overview
This document describes the deployment process for the MVP version of the Financial Investment Advisor Agent.

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 18+
- Git
- Virtual environment

### Required Accounts
- Alpha Vantage API key
- GitHub account

## Local Development Setup

### Backend Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/financial-advisor-agent.git
cd financial-advisor-agent
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your Alpha Vantage API key
```

### Frontend Setup
1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running Locally

### Backend
```bash
# Start API server
uvicorn src.api.main:app --reload
```

### Frontend
```bash
# Start development server
npm run dev
```

## Production Deployment

### Backend Deployment
1. Build the application:
```bash
# Install production dependencies
pip install -r requirements.txt --no-dev

# Run tests
pytest
```

2. Start the production server:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment
1. Build the application:
```bash
# Install production dependencies
npm install --production

# Run tests
npm test

# Build for production
npm run build
```

2. Serve the built files:
```bash
# Using a static file server
npm install -g serve
serve -s build
```

## Environment Configuration

### Backend (.env)
```
ALPHA_VANTAGE_API_KEY=your_api_key
ENVIRONMENT=production
DEBUG=false
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=production
```

## Monitoring

### Logging
```python
# src/utils/logger.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Error Tracking
- Log errors to console
- Monitor API responses
- Track user interactions

## Best Practices

### Development
- Use environment variables
- Follow security best practices
- Implement proper error handling
- Add logging
- Write tests

### Deployment
- Use version control
- Follow CI/CD practices
- Monitor performance
- Backup data
- Document changes

## Future Enhancements
1. Add CI/CD pipeline
2. Implement containerization
3. Add monitoring tools
4. Improve logging
5. Add automated testing 