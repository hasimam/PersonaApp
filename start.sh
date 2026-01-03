#!/bin/bash

# PersonaApp Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting PersonaApp..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -e "${BLUE}Checking PostgreSQL...${NC}"
if ! pgrep -x postgres > /dev/null; then
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    brew services start postgresql@14
    sleep 3
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"
echo ""

# Start backend
echo -e "${BLUE}Starting Backend Server...${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload > /tmp/personaapp-backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "  Logs: /tmp/personaapp-backend.log"
echo -e "  API Docs: http://localhost:8000/docs"
echo ""

# Wait for backend to be ready
echo -e "${BLUE}Waiting for backend to be ready...${NC}"
sleep 5

# Start frontend
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd ../frontend
npm start > /tmp/personaapp-frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "  Logs: /tmp/personaapp-frontend.log"
echo ""

# Wait a bit for frontend to start
sleep 8

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ PersonaApp is running! ✨${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "  📱 App: ${BLUE}http://localhost:3000${NC}"
echo -e "  📚 API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "  Backend PID: $BACKEND_PID"
echo -e "  Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}To stop the servers, run:${NC}"
echo -e "  ./stop.sh"
echo ""
echo -e "${YELLOW}Or manually kill processes:${NC}"
echo -e "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Save PIDs to file for stop script
cd ..
echo "$BACKEND_PID" > .personaapp.pid
echo "$FRONTEND_PID" >> .personaapp.pid

# Try to open browser (macOS)
sleep 3
if command -v open &> /dev/null; then
    open http://localhost:3000
fi
