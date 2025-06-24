#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p logs

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

# Function to rotate logs
rotate_logs() {
    local log_file=$1
    local max_size=$((10 * 1024 * 1024))  # 10MB
    
    if [ -f "$log_file" ]; then
        local size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file")
        if [ "$size" -gt "$max_size" ]; then
            mv "$log_file" "${log_file}.$(date +%Y%m%d_%H%M%S)"
            touch "$log_file"
        fi
    fi
}

# Check if Python is installed
if ! command_exists python3; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Node.js is installed
if ! command_exists node; then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command_exists npm; then
    echo "npm is not installed. Please install npm first."
    exit 1
fi

# Kill any existing processes on ports 8000 and 5173
kill_port 8000
kill_port 5173

# Function to create virtual environment if it doesn't exist
create_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate

    echo -e "${BLUE}Installing backend dependencies...${NC}"
    pip install -r requirements.txt

    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
}

# Function to start servers
start_servers() {
    # Generate timestamp for log files
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backend_log="logs/backend_${timestamp}.log"
    frontend_log="logs/frontend_${timestamp}.log"

    # Start backend server
    echo -e "${GREEN}Starting backend server...${NC}"
    echo "=== Backend Server Started at $(date) ===" > "$backend_log"
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 >> "$backend_log" 2>&1 &
    backend_pid=$!

    # Start frontend server
    echo -e "${GREEN}Starting frontend server...${NC}"
    echo "=== Frontend Server Started at $(date) ===" > "$frontend_log"
    cd frontend
    npm run dev >> "../$frontend_log" 2>&1 &
    frontend_pid=$!
    cd ..

    # Wait for servers to start
    echo "Waiting for servers to start..."
    sleep 5

    # Check if servers are running
    if check_port 8000 && check_port 5173; then
        echo "Servers are running!"
        echo -e "${GREEN}Backend: http://localhost:8000${NC}"
        echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
        echo -e "${BLUE}Press Ctrl+C to stop the servers${NC}"
        echo -e "${BLUE}Logs are being written to:${NC}"
        echo -e "${BLUE}Backend: $backend_log${NC}"
        echo -e "${BLUE}Frontend: $frontend_log${NC}"
        
        # Open browser
        echo "Opening browser..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open http://localhost:5173
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            xdg-open http://localhost:5173
        elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            start http://localhost:5173
        fi
    else
        echo "Error: Servers failed to start"
        kill_port 8000
        kill_port 5173
        exit 1
    fi

    # Function to handle cleanup
    cleanup() {
        echo -e "\n${BLUE}Shutting down servers...${NC}"
        echo "=== Backend Server Stopped at $(date) ===" >> "$backend_log"
        echo "=== Frontend Server Stopped at $(date) ===" >> "$frontend_log"
        kill $backend_pid 2>/dev/null
        kill $frontend_pid 2>/dev/null
        
        # Rotate logs before exiting
        rotate_logs "$backend_log"
        rotate_logs "$frontend_log"
        
        exit 0
    }

    # Set up trap for cleanup
    trap cleanup SIGINT SIGTERM

    # Keep script running
    wait
}

# Main execution
echo "Starting Financial Advisor Agent..."

# Create and activate virtual environment
create_venv

# Install dependencies
install_dependencies

# Start servers
start_servers

# Function to monitor and rotate logs periodically
monitor_logs() {
    while true; do
        rotate_logs "$backend_log"
        rotate_logs "$frontend_log"
        sleep 300  # Check every 5 minutes
    done
}

# Start log monitoring in the background
monitor_logs &
MONITOR_PID=$!

# Wait for both processes
wait

# Clean up monitor process if script exits
kill $MONITOR_PID 2>/dev/null 