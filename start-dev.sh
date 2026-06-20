#!/bin/bash

# WizMap Development Server Startup Script
# This script starts both frontend and backend with hot reload

echo "🚀 Starting WizMap Development Servers..."
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    jobs -p | xargs -r kill
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend (FastAPI with auto-reload)
echo "📦 Starting Backend Server (FastAPI + Uvicorn)..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Backend URL: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

# Start Frontend (Vite with HMR)
echo "🎨 Starting Frontend Dev Server (Svelte + Vite)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Frontend URL: http://localhost:3000"
echo ""

echo "✅ Development servers started successfully!"
echo ""
echo "📋 Server Information:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Hot reload is enabled for both frontend and backend"
echo "   Press Ctrl+C to stop all servers"
echo ""

# Wait for any process to exit
wait -n
