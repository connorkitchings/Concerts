#!/bin/bash

# Run script for Jam Band Predictions web application
# This script helps with starting both the frontend and backend services

# Colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constants
BACKEND_DIR="./backend"
FRONTEND_DIR="./frontend"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display help
show_help() {
    echo -e "${BLUE}Jam Band Predictions Web App Runner${NC}"
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup      - Install all dependencies for frontend and backend"
    echo "  backend    - Start the backend server only"
    echo "  frontend   - Start the frontend development server only"
    echo "  both       - Start both backend and frontend servers"
    echo "  help       - Show this help message"
}

# Setup function - install dependencies
setup() {
    echo -e "${YELLOW}Setting up the application...${NC}"
    
    # Check if Python is installed
    if command_exists python3; then
        echo -e "${GREEN}Python 3 is installed.${NC}"
    else
        echo -e "${YELLOW}Python 3 is not installed. Please install Python 3 to continue.${NC}"
        exit 1
    fi
    
    # Check if pip is installed
    if command_exists pip3; then
        echo -e "${GREEN}pip3 is installed.${NC}"
    else
        echo -e "${YELLOW}pip3 is not installed. Please install pip3 to continue.${NC}"
        exit 1
    fi
    
    # Create virtual environment for backend
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd "$BACKEND_DIR" || exit
    python3 -m venv venv
    
    # Activate virtual environment and install dependencies
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
    
    # Check if Node.js is installed
    if command_exists node; then
        echo -e "${GREEN}Node.js is installed.${NC}"
        
        # Install frontend dependencies
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        cd "$FRONTEND_DIR" || exit
        npm install
        cd ..
    else
        echo -e "${YELLOW}Node.js is not installed. Frontend dependencies cannot be installed.${NC}"
        echo -e "${YELLOW}Please install Node.js to run the frontend.${NC}"
    fi
    
    echo -e "${GREEN}Setup complete!${NC}"
}

# Start backend function
start_backend() {
    echo -e "${YELLOW}Starting backend server...${NC}"
    cd "$BACKEND_DIR" || exit
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend server running at http://localhost:8000${NC}"
    cd ..
}

# Start frontend function
start_frontend() {
    if command_exists node; then
        echo -e "${YELLOW}Starting frontend development server...${NC}"
        cd "$FRONTEND_DIR" || exit
        npm start &
        FRONTEND_PID=$!
        echo -e "${GREEN}Frontend server running at http://localhost:3000${NC}"
        cd ..
    else
        echo -e "${YELLOW}Node.js is not installed. Cannot start frontend.${NC}"
    fi
}

# Process arguments
case "$1" in
    setup)
        setup
        ;;
    backend)
        start_backend
        # Keep script running
        echo -e "${YELLOW}Press Ctrl+C to stop the server...${NC}"
        wait $BACKEND_PID
        ;;
    frontend)
        start_frontend
        # Keep script running
        echo -e "${YELLOW}Press Ctrl+C to stop the server...${NC}"
        wait $FRONTEND_PID
        ;;
    both)
        start_backend
        start_frontend
        echo -e "${GREEN}Both servers are running. Access the application at http://localhost:3000${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop all servers...${NC}"
        wait $BACKEND_PID $FRONTEND_PID
        ;;
    help|*)
        show_help
        ;;
esac
