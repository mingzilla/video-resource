#!/bin/bash

# Usage:
#
#  ./claude-qwen3pt5_9b                 # enter claude code
#  ./claude-qwen3pt5_9b -p "say hello"  # headless mode

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:40221 ANTHROPIC_API_KEY="" claude --model qwen3.5 "$@"
