#!/bin/bash

# Simple development startup script
# This script starts frontend and backend with minimal configuration

echo "🚀 Starting WizMap Development Environment..."

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    jobs -p | xargs -r kill
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend (FastAPI with auto-reload)
echo "📦 Starting Backend Server (port 8080)..."
cd /home/fqs/workspace/self/wizmap/backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q fastapi uvicorn[standard] pydantic-settings python-multipart
else
    source venv/bin/activate
fi

# Check if additional dependencies are needed
if ! python -c "import sqlalchemy" 2>/dev/null; then
    echo "Installing additional dependencies..."
    pip install -q sqlalchemy psycopg2-binary redis celery
fi

python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Backend URL: http://localhost:8080"
echo ""

# Start Frontend (Simple HTTP server with production build)
echo "🎨 Starting Frontend Server (port 3002)..."
cd /home/fqs/workspace/self/wizmap/frontend

# Build frontend if needed or use existing build
if [ ! -d "dist" ] || [ "dist/index.html" -ot "src/" ]; then
    echo "Building frontend..."
    npm run build
fi

# Start simple HTTP server
cd dist
python3 -m http.server 3002 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Frontend URL: http://localhost:3002"
echo ""

echo "✅ Development servers started successfully!"
echo ""
echo "📋 Server Information:"
echo "   Frontend: http://localhost:3002"
echo "   Backend:  http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo ""
echo "📝 Notes:"
echo "   Frontend: Using production build (no HMR)"
echo "   Backend:  Auto-reload enabled for Python files"
echo "   To rebuild frontend: cd frontend && npm run build"
echo ""
echo "💡 Press Ctrl+C to stop all servers"
echo ""

# Wait for any process to exit
wait -n
