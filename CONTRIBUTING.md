# Contributing to Financial Investment Advisor Agent

Thank you for your interest in contributing to the Financial Investment Advisor Agent project! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/financial-advisor-agent.git
   cd financial-advisor-agent
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file based on `.env.example`
6. Run tests:
   ```bash
   pytest
   ```

## Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Write or update tests
4. Run tests and ensure they pass
5. Commit your changes:
   ```bash
   git commit -m "Description of your changes"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

## Code Style

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

## Testing

- Write unit tests for all new features
- Ensure test coverage remains high
- Mock external API calls in tests
- Test edge cases and error conditions

## Documentation

- Update documentation when adding new features
- Keep docstrings up-to-date
- Add examples for complex functionality
- Document any breaking changes

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation as needed
3. Provide a clear description of changes
4. Reference any related issues
5. Request review from maintainers

## Security

- Never commit API keys or sensitive information
- Report security vulnerabilities privately
- Follow security best practices
- Validate all user inputs

## Questions?

Feel free to open an issue if you have any questions about contributing to the project. 