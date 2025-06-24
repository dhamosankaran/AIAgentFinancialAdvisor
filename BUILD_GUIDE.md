# Financial Investment Advisor Agent - Build Guide

## Overview
This guide will help you build a Financial Investment Advisor Agent that provides personalized investment recommendations. The application uses modern technologies but is designed to be built with minimal technical knowledge.

## Prerequisites
1. A computer with internet access
2. Basic understanding of using a computer
3. An Alpha Vantage API key (free tier available at https://www.alphavantage.co/)

## Step-by-Step Build Process

### 1. Initial Setup
1. Open Cursor IDE
2. Create a new folder for your project
3. Copy and paste the following files into your project:
   - `.cursorrules`
   - `requirements.txt`
   - `.env.example`
   - `README.md`

### 2. Environment Setup
1. Create a `.env` file
2. Add your Alpha Vantage API key:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

### 3. Project Structure
Create the following folders in your project:
```
financial-advisor-agent/
├── src/
│   ├── api/
│   ├── services/
│   └── utils/
├── frontend/
├── tests/
├── docs/
└── config/
```

### 4. Building the Application

#### Step 1: Backend Setup
1. Open Cursor IDE
2. Create a new file `src/main.py`
3. Copy and paste the basic FastAPI setup code
4. Create the following files in the `src/api` folder:
   - `routes.py`
   - `models.py`
   - `schemas.py`

#### Step 2: Frontend Setup
1. Create a new file `frontend/index.html`
2. Create a new file `frontend/styles.css`
3. Create a new file `frontend/script.js`

#### Step 3: Testing Setup
1. Create a new file `tests/test_main.py`
2. Create a new file `tests/test_api.py`

### 5. Running the Application
1. Open terminal in Cursor IDE
2. Run the following commands:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```

### 6. Testing the Application
1. Open terminal in Cursor IDE
2. Run:
   ```bash
   pytest tests/
   ```

## Common Issues and Solutions

### 1. API Key Issues
- Problem: "Invalid API Key"
- Solution: Double-check your Alpha Vantage API key in the `.env` file

### 2. Installation Issues
- Problem: "Package not found"
- Solution: Make sure you're in the virtual environment and run `pip install -r requirements.txt`

### 3. Running Issues
- Problem: "Port already in use"
- Solution: Change the port in the uvicorn command to a different number

## Next Steps
1. Customize the investment strategies
2. Add more financial data sources
3. Enhance the user interface
4. Add more test cases

## Support
If you encounter any issues:
1. Check the error messages
2. Review the documentation
3. Search for similar issues online
4. Contact support if needed

## Additional Resources
1. FastAPI Documentation: https://fastapi.tiangolo.com/
2. Alpha Vantage Documentation: https://www.alphavantage.co/documentation/
3. Python Documentation: https://docs.python.org/
4. HTML/CSS Documentation: https://developer.mozilla.org/

## Notes
- Keep your API keys secure
- Regularly update your dependencies
- Back up your code regularly
- Test thoroughly before deploying

Remember: This is a learning project. Take your time to understand each component before moving to the next step. 