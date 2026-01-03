#!/bin/bash

# PersonaApp Stop Script
# This script stops both the backend and frontend servers

echo "🛑 Stopping PersonaApp..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PID file exists
if [ -f .personaapp.pid ]; then
    # Read PIDs from file
    BACKEND_PID=$(sed -n '1p' .personaapp.pid)
    FRONTEND_PID=$(sed -n '2p' .personaapp.pid)

    # Kill backend
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID
        echo -e "${GREEN}✓ Backend stopped${NC}"
    else
        echo -e "${YELLOW}Backend not running${NC}"
    fi

    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        echo -e "${YELLOW}Frontend not running${NC}"
    fi

    # Remove PID file
    rm .personaapp.pid
else
    echo -e "${YELLOW}No PID file found. Searching for processes...${NC}"

    # Try to find and kill processes by port
    BACKEND_PORT_PID=$(lsof -ti:8000)
    FRONTEND_PORT_PID=$(lsof -ti:3000)

    if [ ! -z "$BACKEND_PORT_PID" ]; then
        echo -e "${YELLOW}Stopping process on port 8000 (PID: $BACKEND_PORT_PID)...${NC}"
        kill $BACKEND_PORT_PID
        echo -e "${GREEN}✓ Backend stopped${NC}"
    fi

    if [ ! -z "$FRONTEND_PORT_PID" ]; then
        echo -e "${YELLOW}Stopping process on port 3000 (PID: $FRONTEND_PORT_PID)...${NC}"
        kill $FRONTEND_PORT_PID
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ PersonaApp stopped${NC}"
