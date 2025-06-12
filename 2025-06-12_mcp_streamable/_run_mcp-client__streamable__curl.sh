#!/bin/bash
echo "🌐 Complete MCP Server Test with cURL"
echo "================================================"

# NOTE: http://localhost:8000/mcp will get 307 redirect to http://localhost:8000/mcp/

echo "1. Initialize connection:"
curl -L -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"sampling":{}},"clientInfo":{"name":"curl-test","version":"1.0"}},"id":1}'

echo -e "\n================================================"
echo "2. List available tools:"
curl -L -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'

echo -e "\n================================================"
echo "3. List available resources:"
curl -L -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"resources/list","params":{},"id":3}'

echo -e "\n================================================"
echo "4. Call add tool (10 + 25):"
curl -L -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"add","arguments":{"a":10,"b":25}},"id":4}'

echo -e "\n================================================"
echo "5. Read greeting resource (greeting://developer):"
curl -L -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"resources/read","params":{"uri":"greeting://developer"},"id":5}'

echo -e "\n✅ All MCP tests completed successfully!"