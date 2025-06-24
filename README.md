# Financial Investment Advisor Agent

A personalized investment advisor system that provides tailored investment recommendations based on user profiles, risk tolerance, and market conditions.

## Features

- **Personalized Investment Advice**: Get customized investment recommendations based on your profile and preferences
- **Risk Assessment**: Understand your risk tolerance and get appropriate investment suggestions
- **Portfolio Management**: Track and manage your investment portfolio
- **Market Analysis**: Stay informed about market conditions and trends
- **Interactive Dashboard**: Visualize your portfolio allocation and track performance

## Tech Stack

### Backend
- Python 3.13+
- FastAPI
- Pydantic
- LangChain
- OpenAI API
- Alpha Vantage API
- Yahoo Finance API

### Frontend
- React
- TypeScript
- Tailwind CSS
- Chart.js

## Getting Started

### Prerequisites

- Python 3.13 or higher
- Node.js 16 or higher
- npm or yarn
- OpenAI API key
- Alpha Vantage API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financial-advisor-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

5. Create a `.env` file in the root directory:
```
# Copy .env.example to .env and fill in your API keys
cp .env.example .env
```

### Running the Application

1. Start the backend server:
```bash
cd src
uvicorn api.main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
financial-advisor-agent/
├── src/
│   ├── api/             # FastAPI endpoints
│   ├── agents/          # AI agents
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── frontend/            # React frontend
├── tests/               # Test suite
├── docs/                # Documentation
├── config/              # Configuration files
└── requirements.txt     # Project dependencies
```

## API Endpoints

- `POST /api/v1/chat`: Process chat messages and return responses
- `POST /api/v1/profile`: Create a new user profile
- `GET /api/v1/portfolio/summary`: Get user's portfolio summary
- `GET /api/v1/health`: Health check endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the language model
- Alpha Vantage for market data
- Yahoo Finance for additional market data

## 🚀 Quick Start Guide

### Prerequisites
- A computer with internet access
- Basic understanding of using a computer
- An Alpha Vantage API key (free tier available at https://www.alphavantage.co/)

### Step 1: Download and Setup
1. Download this project to your computer
2. Open Cursor IDE
3. Open the project folder in Cursor IDE

### Step 2: Get Your API Key
1. Go to https://www.alphavantage.co/
2. Sign up for a free account
3. Copy your API key

### Step 3: Configure the Application
1. Create a new file named `.env` in the project folder
2. Add your API key to the file:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

### Step 4: Install Dependencies
1. Open the terminal in Cursor IDE
2. Run these commands:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Run the Application
1. In the terminal, run:
```bash
   uvicorn src.main:app --reload
   ```
2. Open your web browser
3. Go to http://localhost:8000

## 📚 Features

### 1. Personalized Investment Recommendations
- Get investment advice based on your goals
- Consider your risk tolerance
- Account for market conditions

### 2. User-Friendly Interface
- Simple and intuitive design
- Easy-to-understand recommendations
- Clear explanations of investment choices

### 3. Educational Resources
- Learn about investment strategies
- Understand market trends
- Get explanations of financial terms

## 🔧 Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Check if you're in the virtual environment
   - Verify your API key is correct
   - Make sure all dependencies are installed

2. **API Key Not Working**
   - Verify your API key is correct
   - Check if you've exceeded the free tier limits
   - Ensure the `.env` file is in the correct location

3. **Dependencies Not Installing**
   - Make sure you have Python installed
   - Check your internet connection
   - Try running `pip install -r requirements.txt` again

## 📖 Learning Resources

1. **Investment Basics**
   - [Investopedia](https://www.investopedia.com/)
   - [Morningstar](https://www.morningstar.com/)
   - [Yahoo Finance](https://finance.yahoo.com/)

2. **Technical Documentation**
   - [FastAPI Documentation](https://fastapi.tiangolo.com/)
   - [Alpha Vantage API](https://www.alphavantage.co/documentation/)
   - [Python Documentation](https://docs.python.org/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 

## 🙏 Acknowledgments

- Alpha Vantage for providing market data
- FastAPI for the web framework
- All contributors and users

## 📞 Support

If you need help:
1. Check the troubleshooting guide above
2. Look for similar issues in the documentation
3. Contact support if needed

## 🔄 Updates

We regularly update the application with:
- New features
- Bug fixes
- Performance improvements
- Security updates

## 🎯 Next Steps

1. Customize your investment preferences
2. Set up your financial goals
3. Start receiving personalized recommendations
4. Learn about different investment strategies

Remember: This is a learning project. Take your time to understand each component before moving to the next step. 