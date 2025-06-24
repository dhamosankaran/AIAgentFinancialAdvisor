# Development Guide

This guide provides detailed instructions for setting up and working with the Financial Investment Advisor Agent project.

## Table of Contents
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Debugging](#debugging)
- [Deployment](#deployment)

## Environment Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git
- Virtual environment

### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
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

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Project Structure

```
financial-advisor-agent/
├── src/                    # Backend source
│   ├── api/              # FastAPI endpoints
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Application pages
│   │   └── services/     # API integration
├── tests/                # Test suite
└── docs/                # Documentation
```

## Development Workflow

### Backend Development

1. Start development server:
```bash
uvicorn src.api.main:app --reload
```

2. Run tests:
```bash
pytest
```

3. Check code style:
```bash
flake8 src tests
black src tests
isort src tests
```

### Frontend Development

1. Start development server:
```bash
cd frontend
npm start
```

2. Run tests:
```bash
npm test
```

3. Check code style:
```bash
npm run lint
npm run format
```

## Testing

### Backend Tests

1. Unit Tests:
```bash
pytest tests/unit
```

2. Integration Tests:
```bash
pytest tests/integration
```

3. Coverage Report:
```bash
pytest --cov=src tests/
```

### Frontend Tests

1. Unit Tests:
```bash
npm test
```

2. Coverage Report:
```bash
npm test -- --coverage
```

## Debugging

### Backend Debugging

1. Use logging:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

2. Use debugger:
```bash
python -m pdb src/api/main.py
```

### Frontend Debugging

1. Use React Developer Tools
2. Use browser console
3. Use debugger statements

## Deployment

### Local Deployment

1. Build frontend:
```bash
cd frontend
npm run build
```

2. Start backend:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Production Deployment

1. Set environment variables:
```bash
export ENVIRONMENT=production
```

2. Build and deploy:
```bash
# Backend
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run build
```

## Best Practices

### Code Quality
- Write clean, maintainable code
- Follow style guides
- Add comments and documentation
- Write tests

### Performance
- Optimize database queries
- Cache API responses
- Minimize network requests
- Use efficient algorithms

### Security
- Validate user input
- Use environment variables
- Implement rate limiting
- Handle errors gracefully 