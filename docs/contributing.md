# Contributing to Financial Investment Advisor Agent

Thank you for your interest in contributing to the Financial Investment Advisor Agent project! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [License](#license)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/yourusername/financial-advisor-agent.git
cd financial-advisor-agent
```

3. Set up the development environment:
```bash
# Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

4. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

1. Make your changes
2. Run tests:
```bash
# Backend
pytest

# Frontend
npm test
```

3. Commit your changes:
```bash
git commit -m "Description of your changes"
```

4. Push to your fork:
```bash
git push origin feature/your-feature-name
```

5. Create a Pull Request

## Code Style

### Python
- Follow PEP 8 style guide
- Use type hints
- Document functions and classes
- Keep functions small and focused

### JavaScript/TypeScript
- Follow ESLint rules
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks

## Testing

### Backend
- Write unit tests for all new features
- Use pytest fixtures for test data
- Mock external API calls
- Maintain test coverage

### Frontend
- Write unit tests for components
- Test user interactions
- Mock API calls
- Test error handling

## Documentation

- Update README.md for major changes
- Document new features
- Add comments for complex logic
- Keep API documentation up to date

## Pull Request Process

1. Ensure tests pass
2. Update documentation
3. Describe changes in PR
4. Request review from maintainers

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 