#!/bin/bash

# Simple CLIP API Startup Script
# This script starts the simplified API version and runs tests

set -e  # Exit on any error

echo "🚀 Starting Simple CLIP Analysis API"
echo "====================================="

# Function to check if a service is ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting 2 seconds..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start within timeout"
    return 1
}

# Start services
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.simple.yml up -d

# Wait for services to be ready
wait_for_service "http://localhost:8080/" "Simple API"
wait_for_service "http://localhost:8081/" "Kafka UI"

echo ""
echo "🎉 All services are ready!"
echo ""
echo "📖 Available services:"
echo "   • Simple API: http://localhost:8080"
echo "   • API Documentation: http://localhost:8080/docs"
echo "   • Kafka UI: http://localhost:8081"
echo ""

# Check if test image exists
if [ ! -f "test_image.jpg" ]; then
    echo "⚠️  No test_image.jpg found. Please add an image file for testing."
    echo "   You can download one with:"
    echo "   curl -o test_image.jpg https://via.placeholder.com/600x400/0080FF/FFFFFF?text=Test+Image"
    echo ""
fi

# Ask if user wants to run tests
read -p "🧪 Would you like to run the API tests now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running API tests..."
    python test_api.py
    
    echo ""
    echo "📊 Checking final stats..."
    curl -s http://localhost:8080/stats | python -m json.tool
else
    echo "⏭️  Skipping tests. You can run them later with:"
    echo "   python test_api.py"
fi

echo ""
echo "🎯 What to try next:"
echo "   1. Visit http://localhost:8080/docs for interactive API testing"
echo "   2. Upload an image: curl -X POST -F 'file=@your_image.jpg' http://localhost:8080/analyze-image"
echo "   3. Monitor Kafka messages at http://localhost:8081"
echo "   4. Check container logs: docker-compose -f docker-compose.simple.yml logs -f"
echo ""
echo "🛑 To stop all services: docker-compose -f docker-compose.simple.yml down"
