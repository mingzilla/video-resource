#!/bin/bash

# Ollama Load Testing - 8 Minute Optimal Load Test (STREAM ONLY - NO TOOL CALLING)
#
# Uses capacity discovery recommendations: 50 concurrent users (optimal load)
#
# Prerequisites:
# 1. Ollama server running: External machine at configured OLLAMA_BASE_URL
# 2. .env file has: LLM_PROVIDER=ollama
# 3. .env file has: OLLAMA_BASE_URL=http://192.168.1.209:11435
# 4. .env file has: OLLAMA_MODEL=tinyllama (fast, basic model)
# 5. Dependencies synced: uv sync --extra dev
#
# Note: This script only tests stream mode (no tool calling).
# For full testing including batch/mixed modes, use: run_load_testing_ollama_8min_tooled.sh

set -e  # Exit on any error

# Load shared utilities
source load_test_util.sh

# Load Ollama-specific thresholds
source load_testing_ollama_config.sh

# Common setup
common_setup "Ollama 8-Minute Quick Test"

# Quick 5-Step Process Flow:
#
# [1] Capacity Discovery --> [2] System Warm-up --> [3] Baseline Establishment --> [4] Load Testing --> [5] Result Validation
#       |                          |                      |                              |                      |
#     Find system limits     Wake up system         Measure 1-user speed           Test with N users      Analyze e.g. 1 vs N users
#       |                          |                      |                              |                      |
#     "Max 650 users"        "2-3 requests"         "2000ms response"              "2300ms @ 650 users"   "15% degradation ~= reasonable"

# Verify Ollama configuration
verify_ollama_config

# Optional: Show capacity discovery recommendation
recommend_capacity_discovery "ollama"

# Phase 2: System warm-up to eliminate cold start effects
run_warmup_phase "Preparing system for accurate baseline measurements"

# Phase 3: Fast Locust-based baseline (single user)
echo
echo "📈 Phase 3: Running fast single-user baseline..."
echo "   Single-user streaming performance using same logic as load test"
echo "   Testing: Stream mode only (no batch/tool tests)"

# Ensure UV environment is set up
if [ -z "$UV_ENV_PREFIX" ]; then
    source ../_common/env_utils.sh
    setup_uv_environment
fi

echo "   Running baseline with 1 user, 10 requests over 30 seconds..."

# Run single-user baseline using same Locust logic as load test
# Need to run from scripts directory to avoid import issues
(cd ../scripts && eval "${UV_ENV_PREFIX}uv run locust -f load_test_stream_mode.py --headless -u 1 -r 1 -t 30s --html=../load_testing_output/baseline_ollama_8min.html --csv=../load_testing_output/baseline_ollama_8min")

# Phase 4: Realistic load test (adjusted for sustainable load)
run_stream_phase 500 5 15 240s "stream_ollama_8min.html" "500 users, 4 minutes, 15s intervals (equivalent load to pre-refactor)" 3

# Skip batch and mixed tests - these require tool calling support
echo "⏭️  Skipping batch/mixed tests (require tool calling - use *_tooled.sh scripts)"

# Phase 5: Analysis
echo
echo "📊 Phase 5: Analysis complete - using Locust CSV format"
echo "   Baseline data: baseline_ollama_8min_stats.csv"
echo "   Load test data: stream_ollama_8min_stats.csv"

# Results ready for LLM analysis
echo
echo "📊 Load testing complete! Files generated for LLM analysis:"
echo "   - baseline_ollama_8min_stats.csv (single-user performance)"
echo "   - stream_ollama_8min_stats.csv (multi-user load test)"
echo "   - baseline_ollama_8min.html (baseline visual report)"
echo "   - stream_ollama_8min.html (load test visual report)"
echo
echo "💡 For 1-user vs N-user comparison analysis:"
echo "   Copy these 3 files to your preferred LLM:"
echo "   1. load_testing__01__section_5_result_comparison_prompt.md"
echo "   2. baseline_ollama_8min_stats.csv"
echo "   3. stream_ollama_8min_stats.csv"

# Completion message
display_ollama_completion "8-minute test (stream only)" "2 minutes" \
    "baseline_ollama_8min_stats.csv" \
    "stream_ollama_8min.html" \
    "stream_ollama_8min_stats.csv"

echo
echo "🔄 Next steps:"
echo "   - Stream validation: ./run_load_testing_ollama_2min.sh (tinyllama)"
echo "   - Full tool testing: ./run_load_testing_ollama_8min_tooled.sh (qwen2.5:3b)"
echo "   - Compare with OpenAI: ./run_load_testing_openai_8min.sh"
