#!/bin/bash

# WizMap Production Environment Startup Script
# Starts all services in production mode

set -e

echo "🚀 Starting WizMap Production Environment..."
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Change to project root directory
cd "$(dirname "$0")/.."

echo "📦 Starting services in production mode..."
echo "  Frontend: Nginx (port 3001)"
echo "  Backend: Uvicorn (port 8080)"
echo ""

# Start services using production configuration
docker compose -f docker-compose.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ Production environment started successfully!"
echo "=========================================="
echo ""
echo "🌐 Service URLs:"
echo "  Frontend:      http://localhost:3001"
echo "  Backend API:   http://localhost:8080"
echo "  API Docs:     http://localhost:8080/docs"
echo "  MinIO Console: http://localhost:9101"
echo ""
echo "🔧 Production Features:"
echo "  ✅ Optimized frontend build"
echo "  ✅ Production-grade backend"
echo "  ✅ Database persistence"
echo "  ✅ Object storage (MinIO)"
echo "  ✅ Cache layer (Redis)"
echo ""
echo "💡 Management Commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Check status: docker compose ps"
echo "  - Stop services: ./bin/stop"
echo ""
echo "🎯 Production ready! Access http://localhost:3001"
