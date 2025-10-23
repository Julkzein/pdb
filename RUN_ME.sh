#!/bin/bash

# Orchestration Graph Scheduler - Quick Start Script
# This script will help you start both backend and frontend

echo "═══════════════════════════════════════════════════════════"
echo "   Orchestration Graph Scheduler - Quick Start"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from /Users/jules/Desktop/pdb/"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "Found backend and frontend directories"
echo ""

# Function to start backend
start_backend() {
    echo "Starting backend..."
    cd backend

    if [ ! -d "venv" ]; then
        echo "Virtual environment not found!"
        echo "   Please create it first:"
        echo "   cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi

    source venv/bin/activate
    python app_new.py &
    BACKEND_PID=$!
    cd ..

    echo "✅ Backend started (PID: $BACKEND_PID)"
    echo "   Running at: http://127.0.0.1:5000"
    echo ""
}

# Function to start frontend
start_frontend() {
    echo "Starting frontend..."
    cd frontend

    if [ ! -d "node_modules" ]; then
        echo "⚠️  node_modules not found, installing..."
        npm install
    fi

    npm start &
    FRONTEND_PID=$!
    cd ..

    echo "✅ Frontend started (PID: $FRONTEND_PID)"
    echo "   Running at: http://localhost:3000"
    echo ""
}

# Main execution
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Starting Services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

start_backend
sleep 3

start_frontend
sleep 5

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎉 Both services are starting!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Backend:  http://127.0.0.1:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Browser should open automatically in a few seconds..."
echo ""
echo "To stop both services, press Ctrl+C"
echo ""
echo "Logs will appear below:"
echo "═══════════════════════════════════════════════════════════"

# Wait for user interrupt
wait
