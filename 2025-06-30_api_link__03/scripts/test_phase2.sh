#!/bin/bash

# Configuration: Base URL for Server 1
BASE_URL="http://172.22.240.1:9000"

echo "=== Phase 2 Testing Script ==="
echo "Testing Server 1 (LLM-MCP Integration) with tool calling at $BASE_URL"
echo ""

# Wait for server to be ready
echo "Waiting for server to start..."
sleep 3

echo "1. Testing Health Check (should show MCP connection)..."
curl -X GET "$BASE_URL/health" -H "Content-Type: application/json"

echo ""
echo "2. Testing Available Tools Discovery..."
curl -X GET "$BASE_URL/api/v1/tools" -H "Content-Type: application/json"

echo ""
echo "3. Testing Direct Tool Call (if tools are available)..."
echo "Note: This will only work if Server 2 (MCP Proxy) is running and has tools"
curl -X POST "$BASE_URL/api/v1/tools/call" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "tool_name": "get_all_api_configs",
    "arguments": {}
  }'

echo ""
echo "4. Testing LLM Chat with Tool Integration..."
echo "Note: This should discover tools and make them available to the LLM"
curl -X POST "$BASE_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you list all available API configurations? Use any tools you have available.",
    "model": "gpt-4-1106-preview"
  }'

echo ""
echo "5. Testing Streaming Chat with Tool Integration..."
echo "Note: This will show tool calls in real-time via SSE"
curl -X POST "$BASE_URL/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Please help me understand what API configurations are available. Use any tools to find this information.",
    "model": "gpt-4-1106-preview"
  }' -N

echo ""
echo "=== Phase 2 Testing Complete ==="
echo ""
echo "Expected behavior:"
echo "- Health check should show both LLM and MCP connections"
echo "- Tools endpoint should list available MCP tools"
echo "- Direct tool call should execute MCP functions"
echo "- Chat endpoints should automatically use tools when LLM requests them"
