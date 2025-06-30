#!/bin/bash

# Test MCP server running on localhost:8080
MCP_SERVER_URL="http://127.0.0.1:8000/mcp/"

echo "=== List Tools ==="
curl -X POST "$MCP_SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

echo -e "\n\n=== Read Resource: config://api-configs/all ==="
curl -X POST "$MCP_SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "resources/read",
    "params": {
      "uri": "config://api-configs/all"
    }
  }'

echo "=== Call Tools ==="
curl -X POST "$MCP_SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params":{"name":"get_all_api_configs","arguments":{"limit":10}}
  }'
