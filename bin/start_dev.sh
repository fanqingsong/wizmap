#!/bin/bash

# WizMap Development Environment Startup Script
# Starts all services with hot reload enabled

set -e

echo "🚀 Starting WizMap Development Environment..."
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Change to project root directory
cd "$(dirname "$0")/.."

echo "📦 Starting services with hot reload..."
echo "  Frontend: Vite HMR (port 3002)"
echo "  Backend:  Uvicorn --reload (port 8080)"
echo ""

# Start services using development configuration.
# --build ensures images are (re)built from the current Dockerfile/requirements,
# so backend deps like wizmap are baked into the image and survive container
# recreates. Docker layer cache keeps this fast when nothing changed.
echo "🔨 Building images (uses cache when unchanged)..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ Development environment started successfully!"
echo "=========================================="
echo ""
echo "🌐 Service URLs:"
echo "  Frontend (Dev):  http://localhost:3002"
echo "  Frontend (Prod): http://localhost:3001"
echo "  Backend API:    http://localhost:8080"
echo "  API Docs:      http://localhost:8080/docs"
echo ""
echo "🔥 Hot Reload Enabled:"
echo "  ✅ Frontend: Vite HMR - auto-refresh on file changes"
echo "  ✅ Backend:  Uvicorn --reload - auto-restart on file changes"
echo "  ✅ Celery: watchfiles - auto-restart on file changes"
echo ""
echo "💡 Development Tips:"
echo "  - Frontend files: ./frontend/ (auto-refreshes browser)"
echo "  - Backend files:  ./backend/ (auto-restarts server)"
echo "  - View logs: docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f"
echo "  - Stop services: ./bin/stop"
echo ""
echo "🎯 Ready to develop! Access http://localhost:3002 to start."
