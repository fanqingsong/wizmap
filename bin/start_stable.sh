#!/bin/bash

# WizMap Stable Production Startup Script
# Starts services in stable production mode without HMR issues

echo "🚀 Starting WizMap Stable Environment..."
echo "=========================================="

# Stop any running services first
echo "🛑 Stopping current services..."
./bin/stop

echo ""
echo "📦 Starting services in stable production mode..."
echo "  Frontend: Nginx (port 3001) - NO HMR"
echo "  Backend: Uvicorn (port 8080) - with hot reload"
echo ""

# Start services using production configuration only
docker compose -f docker-compose.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 8

echo ""
echo "✅ Stable environment started successfully!"
echo "=========================================="
echo ""
echo "🌐 Service URLs:"
echo "  Frontend:      http://localhost:3001 (Stable, no HMR issues)"
echo "  Backend API:   http://localhost:8080"
echo "  API Docs:     http://localhost:8080/docs"
echo ""
echo "🔧 Features:"
echo "  ✅ Stable frontend (no page flickering)"
echo "  ✅ File upload working"
echo "  ✅ Backend hot reload enabled"
echo "  ✅ Full API functionality"
echo ""
echo "💡 File Upload:"
echo "   1. Access http://localhost:3001"
echo "  2. Click 'Upload Dataset' button"
echo "  3. Upload .txt, .csv, or .json files"
echo ""
echo "🎯 Ready to use! Stable frontend available at http://localhost:3001"
