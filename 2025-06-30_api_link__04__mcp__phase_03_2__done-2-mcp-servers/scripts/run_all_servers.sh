#!/bin/bash

echo "Starting all servers in parallel..."
echo "Server 1 (LLM-MCP): http://localhost:9000"
echo "Server 2 (API Config MCP): http://localhost:8000/mcp"
echo "Server 2B (Calculator MCP): http://localhost:8010/mcp (manual start required)"
echo "Server 3 (FastAPI): http://localhost:8001"
echo ""

# Function to cleanup background jobs on script exit
cleanup() {
    echo "Stopping all servers..."
    jobs -p | xargs -r kill
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Start Server 3 (FastAPI REST API) on port 8001
echo "Starting Server 3 (FastAPI REST API)..."
./run_server3.sh &
SERVER3_PID=$!

# Start Server 2 (MCP Proxy Server) on port 8000/mcp
echo "Starting Server 2 (MCP Proxy Server)..."
./run_server2.sh &
SERVER2_PID=$!

# Start Server 1 (LLM-MCP Integration) on port 9000
echo "Starting Server 1 (LLM-MCP Integration)..."
./run_server1.sh &
SERVER1_PID=$!

echo ""
echo "All servers started successfully!"
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for any server to exit
wait
