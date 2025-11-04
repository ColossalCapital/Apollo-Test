#!/bin/bash

# Apollo Restart Script with Theta GPU Integration
# This script restarts Apollo and verifies Theta GPU is working

set -e

echo "🚀 Restarting Apollo with Theta GPU..."
echo ""

# Navigate to Infrastructure directory
cd "/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/Infrastructure"

# Restart Apollo
echo "📦 Restarting Apollo container..."
docker-compose -f docker-compose.complete-system.yml restart apollo

echo ""
echo "⏳ Waiting for Apollo to start (5 seconds)..."
sleep 5

echo ""
echo "🔍 Checking Apollo health..."
HEALTH=$(curl -s http://localhost:8002/health || echo "ERROR")

if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ Apollo is healthy!"
else
    echo "❌ Apollo health check failed"
    echo "Response: $HEALTH"
    exit 1
fi

echo ""
echo "🔍 Checking Theta GPU configuration..."
CHAT_HEALTH=$(curl -s http://localhost:8002/api/chat/health || echo "ERROR")

if [[ $CHAT_HEALTH == *"theta_gpu"* ]]; then
    echo "✅ Theta GPU is configured!"
else
    echo "⚠️  Theta GPU not showing in health check"
    echo "Response: $CHAT_HEALTH"
fi

echo ""
echo "🧪 Testing chat endpoint..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8002/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Are you smart yet?", "entity_id": "test_user"}' || echo "ERROR")

if [[ $TEST_RESPONSE == *"provider"* ]]; then
    PROVIDER=$(echo $TEST_RESPONSE | grep -o '"provider":"[^"]*"' | cut -d'"' -f4)
    MODEL=$(echo $TEST_RESPONSE | grep -o '"model":"[^"]*"' | cut -d'"' -f4)
    
    echo "✅ Chat endpoint working!"
    echo "   Provider: $PROVIDER"
    echo "   Model: $MODEL"
    
    if [[ $PROVIDER == "theta_gpu" ]]; then
        echo ""
        echo "🎉 SUCCESS! Theta GPU is working!"
        echo ""
        echo "Try it in Akashic IDE:"
        echo "  1. Open Akashic IDE"
        echo "  2. Load a codebase"
        echo "  3. Ask: 'Are you smart yet?'"
        echo "  4. Get real AI responses! 🧠✨"
    else
        echo ""
        echo "⚠️  Using $PROVIDER instead of Theta GPU"
        echo "Check Apollo logs for errors:"
        echo "  docker-compose -f docker-compose.complete-system.yml logs apollo"
    fi
else
    echo "❌ Chat endpoint test failed"
    echo "Response: $TEST_RESPONSE"
fi

echo ""
echo "📊 View logs:"
echo "  docker-compose -f docker-compose.complete-system.yml logs -f apollo"
echo ""
