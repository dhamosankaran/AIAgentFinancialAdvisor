from setuptools import setup, find_packages

setup(
    name="financial-advisor-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.2",
        "python-dotenv>=1.0.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "langgraph>=0.0.15",
        "openai>=1.3.0",
        "alpha_vantage>=2.3.1",
        "yfinance>=0.2.31",
        "aiohttp>=3.9.0",
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "httpx>=0.25.1",
        "pytest-cov>=4.1.0"
    ],
    python_requires=">=3.9",
) 