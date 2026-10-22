#!/bin/bash

# Configuration: Auto-detect environment and set appropriate BASE_URL
if [ -z "$BASE_URL" ]; then
    # Check if running in Windows (GitBash/MSYS) vs WSL
    if [[ "$OSTYPE" == "msys" ]] || [[ "$MSYSTEM" == "MINGW"* ]] || [[ -n "$WINDIR" ]]; then
        # Windows GitBash environment - use localhost
        BASE_URL="http://localhost:9000"
        echo "Detected Windows environment - using localhost"
    else
        # WSL environment - use Windows IP
        WINDOWS_IP=$(ip route show | grep -i default | awk '{ print $3}')
        BASE_URL="http://$WINDOWS_IP:9000"
        echo "Detected WSL environment - using Windows IP: $WINDOWS_IP"
    fi
fi

echo "=== Phase 1 Testing Script ==="
echo "Testing Server 1 (LLM-MCP Integration) at $BASE_URL"
echo ""

# Wait for server to be ready
echo "Waiting for server to start..."
sleep 3

echo "1. Testing Health Check..."
curl -X GET "$BASE_URL/health" -H "Content-Type: application/json"

echo ""
echo "2. Testing Root Endpoint..."
curl -X GET "$BASE_URL/" -H "Content-Type: application/json"

echo ""
echo "3. Testing Basic Chat (non-streaming)..."
curl -X POST "$BASE_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you tell me what you are?",
    "model": "gpt-4.1-nano"
  }'

echo ""
echo "4. Testing Streaming Chat..."
echo "Note: This will show Server-Sent Events format"
curl -X POST "$BASE_URL/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Count to 3 and explain what you are doing.",
    "model": "gpt-4.1-nano"
  }' -N

echo ""
echo "=== Phase 1 Testing Complete ==="
