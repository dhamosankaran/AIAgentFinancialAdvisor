#!/bin/bash

# =============================================================================
# Enterprise AgenticAI Startup Script
# Starts the complete enterprise system with all features
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Enterprise banner
echo -e "${PURPLE}🏢============================================================${NC}"
echo -e "${PURPLE}🏢  Enterprise AgenticAI - Complete System Startup${NC}"
echo -e "${PURPLE}🏢  Bank-grade Financial AI with Enterprise Features${NC}"
echo -e "${PURPLE}🏢============================================================${NC}"

# Create necessary directories
mkdir -p logs data cache/plugins backups

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
check_port() {
    if command_exists lsof; then
        lsof -i :$1 >/dev/null 2>&1
    else
        netstat -an | grep "LISTEN" | grep ":$1 " >/dev/null 2>&1
    fi
}

# Function to kill process on a port
kill_port() {
    if command_exists lsof; then
        lsof -ti :$1 | xargs kill -9 2>/dev/null
    else
        pid=$(netstat -anp | grep ":$1 " | grep "LISTEN" | awk '{print $7}' | cut -d'/' -f1)
        if [ ! -z "$pid" ]; then
            kill -9 $pid 2>/dev/null
        fi
    fi
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 required${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js required${NC}"
    exit 1
fi

# Check virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [[ -d "venv" ]]; then
        echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${BLUE}🔄 Creating virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
    fi
fi

echo -e "${GREEN}✅ Virtual environment active${NC}"

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1
cd frontend && npm install > /dev/null 2>&1 && cd ..

# Clean up old processes
echo -e "${BLUE}🧹 Cleaning up old processes...${NC}"
kill_port 8000
kill_port 5173
sleep 2

# Start servers
timestamp=$(date +"%Y%m%d_%H%M%S")
backend_log="logs/enterprise_backend_${timestamp}.log"
frontend_log="logs/enterprise_frontend_${timestamp}.log"

echo -e "${BLUE}🚀 Starting enterprise servers...${NC}"

# Start backend
echo -e "${GREEN}   Starting Enterprise API Server...${NC}"
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 > "$backend_log" 2>&1 &
backend_pid=$!

# Start frontend
echo -e "${GREEN}   Starting Frontend Server...${NC}"
cd frontend
npm run dev > "../$frontend_log" 2>&1 &
frontend_pid=$!
cd ..

# Wait and check
echo -e "${BLUE}   ⏳ Waiting for servers...${NC}"
sleep 8

if check_port 8000 && check_port 5173; then
    echo ""
    echo -e "${PURPLE}🎉 Enterprise AgenticAI Successfully Started!${NC}"
    echo ""
    echo -e "${GREEN}🌐 URLs:${NC}"
    echo -e "${GREEN}   • Frontend:     http://localhost:5173${NC}"
    echo -e "${GREEN}   • API Docs:     http://localhost:8000/docs${NC}"
    echo -e "${GREEN}   • Health Check: http://localhost:8000/api/v2/health/enterprise${NC}"
    echo ""
    echo -e "${BLUE}🏢 Enterprise Features:${NC}"
    echo -e "${BLUE}   • Toggle 'Enterprise Mode' ON${NC}"
    echo -e "${BLUE}   • Toggle 'Admin Access' ON for Plugin Manager${NC}"
    echo -e "${BLUE}   • Responsible AI with content moderation${NC}"
    echo -e "${BLUE}   • Hot-swappable plugin architecture${NC}"
    echo ""
    echo -e "${YELLOW}⚡ Press Ctrl+C to stop${NC}"
    
    # Open browser
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:5173
    fi
    
else
    echo -e "${RED}❌ Failed to start servers${NC}"
    kill $backend_pid $frontend_pid 2>/dev/null
    exit 1
fi

# Cleanup function
cleanup() {
    echo ""
    echo -e "${BLUE}🛑 Shutting down...${NC}"
    kill $backend_pid $frontend_pid 2>/dev/null
    kill_port 8000
    kill_port 5173
    echo -e "${GREEN}✅ Shutdown complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep running
wait 