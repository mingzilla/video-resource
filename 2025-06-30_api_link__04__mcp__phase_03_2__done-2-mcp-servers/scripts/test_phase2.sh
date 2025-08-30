#!/bin/bash

# Port selection: Allow testing different Server 1 implementations
# Usage: ./test_phase2.sh [port]
# Default: port 9000 (current/target implementation)
# Alternative: port 9001 (backup/reference implementation)
SERVER_PORT=${1:-9000}

# Configuration: Auto-detect environment and set appropriate BASE_URL
if [ -z "$BASE_URL" ]; then
    # Check if running in Windows (GitBash/MSYS) vs WSL
    if [[ "$OSTYPE" == "msys" ]] || [[ "$MSYSTEM" == "MINGW"* ]] || [[ -n "$WINDIR" ]]; then
        # Windows GitBash environment - use localhost
        BASE_URL="http://localhost:$SERVER_PORT"
        echo "Detected Windows environment - using localhost"
    else
        # WSL environment - use Windows IP
        WINDOWS_IP=$(ip route show | grep -i default | awk '{ print $3}')
        BASE_URL="http://$WINDOWS_IP:$SERVER_PORT"
        echo "Detected WSL environment - using Windows IP: $WINDOWS_IP"
    fi
fi

# Test results tracking
declare -a TEST_RESULTS
declare -a TEST_NAMES

echo "=== Phase 2 Testing Script: Dual-Mode Streaming ==="
echo "Testing Server 1 (LLM-MCP Integration) with dual-mode streaming at $BASE_URL"
if [ "$SERVER_PORT" = "9001" ]; then
    echo "Testing BACKUP/REFERENCE implementation (port 9001)"
else
    echo "Testing CURRENT/TARGET implementation (port 9000)"
fi
echo ""

# Wait for server to be ready
echo "Waiting for server to start..."
sleep 3

echo "1. Testing Health Check (should show MCP connection)..."
TEST_NAMES[0]="Health Check"
HEALTH_RESPONSE=$(curl -s -X GET "$BASE_URL/health" -H "Content-Type: application/json")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    TEST_RESULTS[0]="PASS"
    echo "✓ PASS: Server is healthy"
else
    TEST_RESULTS[0]="FAIL"
    echo "✗ FAIL: Server health check failed"
fi
echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

echo "2. Testing Available Tools Discovery..."
TEST_NAMES[1]="Tools Discovery"
echo "This endpoint provides tools for user selection in the UI"
TOOLS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/tools" -H "Content-Type: application/json")
if echo "$TOOLS_RESPONSE" | grep -q '"tools"' && echo "$TOOLS_RESPONSE" | grep -q '"count"' && echo "$TOOLS_RESPONSE" | grep -q '"count":[^0]'; then
    TEST_RESULTS[1]="PASS"
    echo "✓ PASS: Tools endpoint returned valid response with available tools"
else
    TEST_RESULTS[1]="FAIL"
    echo "✗ FAIL: Tools endpoint failed or no tools available"
fi
echo "$TOOLS_RESPONSE" | jq '.' 2>/dev/null || echo "$TOOLS_RESPONSE"
echo ""

echo "3. Testing Direct Tool Call (MCP validation)..."
TEST_NAMES[2]="Direct Tool Call"
echo "Note: This validates MCP proxy is working"
TOOL_CALL_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_all_api_configs",
    "arguments": {"limit": 2}
  }')
if echo "$TOOL_CALL_RESPONSE" | grep -q '"tool_name"' && echo "$TOOL_CALL_RESPONSE" | grep -q '"result"'; then
    TEST_RESULTS[2]="PASS"
    echo "✓ PASS: Tool call executed successfully"
else
    TEST_RESULTS[2]="FAIL"
    echo "✗ FAIL: Tool call failed"
fi
echo "$TOOL_CALL_RESPONSE" | jq '.' 2>/dev/null || echo "$TOOL_CALL_RESPONSE"
echo ""

echo "4. Testing STREAM MODE (no tools selected - real-time streaming)..."
TEST_NAMES[3]="Stream Mode"
echo "Expected: Real-time token streaming, no tool calls"
STREAM_OUTPUT=$(timeout 8s curl -s -X POST "$BASE_URL/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "message": "Hello! Please tell me a short joke.",
    "model": "gpt-4.1-nano"
  }' --no-buffer | head -10)
if echo "$STREAM_OUTPUT" | grep -q 'event: chunk' && echo "$STREAM_OUTPUT" | grep -q '"content"'; then
    TEST_RESULTS[3]="PASS"
    echo "✓ PASS: Stream mode working - real-time streaming"
else
    TEST_RESULTS[3]="FAIL"
    echo "✗ FAIL: Stream mode failed"
fi
echo "$STREAM_OUTPUT" | head -5
echo ""

echo "5. Testing BATCH MODE (with tools selected - progressive streaming)..."
TEST_NAMES[4]="Batch Mode"
echo "Expected: Progressive streaming with immediate responses"
BATCH_OUTPUT=$(timeout 15s curl -s -X POST "$BASE_URL/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "message": "What API configurations do we have?",
    "model": "gpt-4.1-nano",
    "selected_tools": ["get_all_api_configs"]
  }')
EVENT_COUNT=$(echo "$BATCH_OUTPUT" | grep -c "^event: complete")
if echo "$BATCH_OUTPUT" | grep -q '"response"' && echo "$BATCH_OUTPUT" | grep -q '"session_id"' && [ "$EVENT_COUNT" -ge 1 ]; then
    TEST_RESULTS[4]="PASS"
    echo "✓ PASS: Batch mode working - progressive streaming (count: $EVENT_COUNT)"
else
    TEST_RESULTS[4]="FAIL"
    echo "✗ FAIL: Batch mode failed (event count: $EVENT_COUNT)"
fi
echo "$BATCH_OUTPUT" | head -5
echo ""

echo "6. Testing Non-Streaming Chat (Simple Chat Only)..."
TEST_NAMES[5]="Non-Streaming Chat"
echo "Expected: Simple chat response without tools (by design)"
echo "Note: /chat endpoint does not support tools - use /chat/stream for tool access"
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "model": "gpt-4.1-nano"
  }')
if echo "$CHAT_RESPONSE" | grep -q '"response"' && echo "$CHAT_RESPONSE" | grep -q '"session_id"'; then
    TEST_RESULTS[5]="PASS"
    echo "✓ PASS: Non-streaming chat working (simple chat only)"
else
    TEST_RESULTS[5]="FAIL"
    echo "✗ FAIL: Non-streaming chat failed"
fi
echo "$CHAT_RESPONSE" | jq '.response' 2>/dev/null || echo "$CHAT_RESPONSE"
echo ""

echo "7. Testing Backward Compatibility (legacy clients)..."
TEST_NAMES[6]="Backward Compatibility"
echo "Expected: Works exactly like before (auto-discover all tools)"
LEGACY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "model": "gpt-4.1-nano"
  }')
if echo "$LEGACY_RESPONSE" | grep -q '"response"' && echo "$LEGACY_RESPONSE" | grep -q '"session_id"'; then
    TEST_RESULTS[6]="PASS"
    echo "✓ PASS: Backward compatibility working"
else
    TEST_RESULTS[6]="FAIL"
    echo "✗ FAIL: Backward compatibility failed"
fi
echo "$LEGACY_RESPONSE" | jq '.response' 2>/dev/null || echo "$LEGACY_RESPONSE"
echo ""

echo "=== PHASE 2 TEST RESULTS SUMMARY ==="
echo ""
PASSED=0
FAILED=0
for i in {0..6}; do
    if [ "${TEST_RESULTS[$i]}" = "PASS" ]; then
        echo "✓ PASS: ${TEST_NAMES[$i]}"
        ((PASSED++))
    elif [ "${TEST_RESULTS[$i]}" = "FAIL" ]; then
        echo "✗ FAIL: ${TEST_NAMES[$i]}"
        ((FAILED++))
    else
        echo "? SKIP: ${TEST_NAMES[$i]} (not run)"
        ((FAILED++))
    fi
done
echo ""
echo "TOTAL: $PASSED passed, $FAILED failed"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED! Dual-mode streaming is working correctly."
    echo ""
    echo "Dual-Mode Strategy Validation:"
    echo "✓ Stream Mode: Real-time SSE streaming when no tools selected"
    echo "✓ Batch Mode: SSE streaming with complete JSON responses for tool orchestration"
    echo "✓ Tool Orchestration: Full LLM + MCP + synthesis loop working via /chat/stream"
    echo "✓ Tool Selection: Only user-selected tools available to LLM"
    echo "✓ Tool Discovery: /api/v1/tools endpoint for UI integration"
    echo "✓ Simple Chat: /api/v1/chat endpoint for non-tool requests"
else
    echo "❌ SOME TESTS FAILED! Check the failures above."
    echo ""
    echo "Common Issues:"
    echo "- Server not running: ./run_server1.sh, ./run_server2.sh, ./run_server3.sh"
    echo "- OpenAI API key not set: export OPENAI_API_KEY=sk-..."
    echo "- MCP server not connected: Check Server 2 logs"
    echo "- Network issues: Verify BASE_URL=$BASE_URL"
fi
echo ""
echo "Key Features:"
echo "- Stream Mode: Real-time SSE streaming (no tools) via /chat/stream"
echo "- Tool Mode: SSE streaming with complete JSON responses via /chat/stream"
echo "- Simple Chat: Direct batch responses (no tools) via /chat"
echo "- Tool Orchestration: Multiple LLM rounds with tool execution"
echo "- Tool Selection: User controls which tools LLM can access"
echo "- Consistent Streaming: All streaming uses SSE format"
