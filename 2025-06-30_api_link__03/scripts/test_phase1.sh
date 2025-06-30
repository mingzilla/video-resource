#!/bin/bash

# Configuration: Base URL for Server 1
BASE_URL="http://172.22.240.1:9000"

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
    "model": "gpt-4-1106-preview"
  }'

echo ""
echo "4. Testing Streaming Chat..."
echo "Note: This will show Server-Sent Events format"
curl -X POST "$BASE_URL/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Count to 3 and explain what you are doing.",
    "model": "gpt-4-1106-preview"
  }' -N

echo ""
echo "=== Phase 1 Testing Complete ==="
