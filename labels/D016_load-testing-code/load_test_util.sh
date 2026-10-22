#!/bin/bash

# Load Testing Utilities - Shared functions for all load test scripts
# Common verification, setup, and output functions

# Function: Verify OpenAI configuration
verify_openai_config() {
    echo "🔍 Checking OpenAI provider configuration..."

    if grep -q "LLM_PROVIDER=openai" ../.env 2>/dev/null; then
        echo "✅ Provider set to openai in .env"
    else
        echo "⚠️  Please add 'LLM_PROVIDER=openai' to your .env file"
        echo "   Current .env contents:"
        cat ../.env 2>/dev/null || echo "   (.env file not found)"
        exit 1
    fi

    # Check OpenAI API key
    echo "🔍 Checking OpenAI API key..."
    if grep -q "OPENAI_API_KEY=sk-" ../.env 2>/dev/null; then
        echo "✅ OpenAI API key configured"
    else
        echo "❌ OpenAI API key not found. Please add OPENAI_API_KEY=sk-... to your .env file"
        exit 1
    fi
}

# Function: Verify Ollama configuration
verify_ollama_config() {
    echo "🔍 Checking Ollama provider configuration..."

    if grep -q "LLM_PROVIDER=ollama" ../.env 2>/dev/null; then
        echo "✅ Provider set to ollama in .env"
    else
        echo "⚠️  Please add 'LLM_PROVIDER=ollama' to your .env file"
        echo "   Current .env contents:"
        cat ../.env 2>/dev/null || echo "   (.env file not found)"
        exit 1
    fi

    # Check OLLAMA_BASE_URL configuration
    echo "🔍 Checking Ollama base URL configuration..."
    if grep -q "OLLAMA_BASE_URL=" ../.env 2>/dev/null; then
        local ollama_url=$(grep "OLLAMA_BASE_URL=" ../.env | cut -d'=' -f2)
        echo "✅ OLLAMA_BASE_URL configured: $ollama_url"

        # Check if Ollama is running at the configured URL
        echo "🔍 Checking Ollama availability at $ollama_url..."
        if curl -s "${ollama_url}/api/version" > /dev/null; then
            echo "✅ Ollama is running and accessible"
        else
            echo "❌ Ollama not available at $ollama_url"
            echo "   Check:"
            echo "   1. External Ollama server is running (dev-docker/tool-ollama/)"
            echo "   2. IP address is correct in OLLAMA_BASE_URL"
            echo "   3. Port 11435 is accessible"
            exit 1
        fi
    else
        echo "⚠️  Please add 'OLLAMA_BASE_URL=http://192.168.1.209:11435' to your .env file"
        exit 1
    fi

    # Check OLLAMA_MODEL configuration
    echo "🔍 Checking Ollama model configuration..."
    if grep -q "OLLAMA_MODEL=" ../.env 2>/dev/null; then
        local ollama_model=$(grep "OLLAMA_MODEL=" ../.env | cut -d'=' -f2)
        echo "✅ OLLAMA_MODEL configured: $ollama_model"
    else
        echo "⚠️  Please add 'OLLAMA_MODEL=tinyllama' (or qwen2.5:3b) to your .env file"
        exit 1
    fi
}

# Function: Verify Ollama configuration for tooled tests (requires qwen2.5:3b)
verify_ollama_tooled_config() {
    echo "🔍 Checking Ollama provider configuration for tooled tests..."

    if grep -q "LLM_PROVIDER=ollama" ../.env 2>/dev/null; then
        echo "✅ Provider set to ollama in .env"
    else
        echo "⚠️  Please add 'LLM_PROVIDER=ollama' to your .env file"
        echo "   Current .env contents:"
        cat ../.env 2>/dev/null || echo "   (.env file not found)"
        exit 1
    fi

    # Check OLLAMA_BASE_URL configuration
    echo "🔍 Checking Ollama base URL configuration..."
    if grep -q "OLLAMA_BASE_URL=" ../.env 2>/dev/null; then
        local ollama_url=$(grep "OLLAMA_BASE_URL=" ../.env | cut -d'=' -f2)
        echo "✅ OLLAMA_BASE_URL configured: $ollama_url"

        # Check if Ollama is running at the configured URL
        echo "🔍 Checking Ollama availability at $ollama_url..."
        if curl -s "${ollama_url}/api/version" > /dev/null; then
            echo "✅ Ollama is running and accessible"
        else
            echo "❌ Ollama not available at $ollama_url"
            echo "   Check:"
            echo "   1. External Ollama server is running (dev-docker/tool-ollama/)"
            echo "   2. IP address is correct in OLLAMA_BASE_URL"
            echo "   3. Port 11435 is accessible"
            exit 1
        fi
    else
        echo "⚠️  Please add 'OLLAMA_BASE_URL=http://192.168.1.209:11435' to your .env file"
        exit 1
    fi

    # Check OLLAMA_MODEL configuration - MUST be qwen2.5:3b for tooled tests
    echo "🔍 Checking Ollama model configuration for tool calling..."
    if grep -q "OLLAMA_MODEL=qwen2.5:3b" ../.env 2>/dev/null; then
        echo "✅ OLLAMA_MODEL configured: qwen2.5:3b (tool calling supported)"
    else
        echo "❌ Tooled tests require qwen2.5:3b model for tool calling support"
        echo "   Please update your .env file: OLLAMA_MODEL=qwen2.5:3b"
        echo "   Current model configuration:"
        grep "OLLAMA_MODEL=" ../.env 2>/dev/null || echo "   (OLLAMA_MODEL not set)"
        exit 1
    fi
}

# Function: Common setup for all load tests
common_setup() {
    local test_name="$1"

    echo "=== $test_name ==="
    echo "📊 Load testing with environment auto-detection"
    echo

    # Load common environment utilities (from parent directory)
    source ../_common/env_utils.sh

    # Setup environment for port 9000
    setup_complete_environment 9000

    # Create output directory
    mkdir -p ../load_testing_output
}

# Function: System warm-up phase
run_warmup_phase() {
    local description="${1:-System warm-up for accurate baseline measurements}"

    echo
    echo "🔥 Phase 2: Fast Locust-based warm-up..."
    echo "   $description"
    echo "   Using same logic as load test for consistency"

    # Use existing environment detection utilities
    if [ -z "$UV_ENV_PREFIX" ]; then
        source ../_common/env_utils.sh
        setup_uv_environment
    fi

    echo "   Running 3 streaming requests over 10 seconds..."

    # Run brief warmup using same Locust logic - 1 user, 3 requests over 10s
    # Need to run from scripts directory to avoid import issues
    echo "   Executing warmup command..."
    if ! (cd ../scripts && eval "${UV_ENV_PREFIX}uv run locust -f load_test_stream_mode.py --headless -u 1 -r 1 -t 10s --html=/dev/null" 2>&1); then
        echo "   ❌ Warmup failed! Error output:"
        (cd ../scripts && eval "${UV_ENV_PREFIX}uv run locust -f load_test_stream_mode.py --headless -u 1 -r 1 -t 10s --html=/dev/null")
        exit 1
    fi

    echo "   Warm-up completed - system ready for baseline measurement"

    # Brief pause to ensure system reaches steady state
    sleep 1
}

# Function: Run benchmark phase
run_benchmark_phase() {
    local output_file="$1"
    local description="$2"

    echo
    echo "📈 Phase 1: Running baseline benchmarks..."
    echo "   $description"
    run_uv_command "run pytest ../scripts/benchmark_baseline.py --benchmark-json=../load_testing_output/$output_file -v"
}

# Function: Run single benchmark test (for mini tests)
run_mini_benchmark_phase() {
    local output_file="$1"

    echo
    echo "📈 Phase 1: Mini benchmark (15 sec)..."
    echo "   Quick single-user performance check"
    run_uv_command "run pytest ../scripts/benchmark_baseline.py::test_health_check_baseline --benchmark-json=../load_testing_output/$output_file -v"
}

# Function: Run stream mode test
run_stream_phase() {
    local users="$1"
    local ramp_rate="$2"
    local user_request_interval="$3"
    local duration="$4"
    local output_file="$5"
    local description="$6"
    local failure_threshold="${7:-0}"  # Optional 7th parameter, defaults to 0 (disabled)

    echo
    echo "📈 Phase 2: Stream mode load test ($duration)..."
    echo "   $description"
    echo "   Users: $users, Ramp: $ramp_rate/s, Max cycle: ${user_request_interval}s (request + wait)"
    if [ "$failure_threshold" -gt 0 ]; then
        echo "   Failure threshold: $failure_threshold failures (early termination enabled)"
    fi

    # Extract base filename for generating both HTML and CSV
    local base_name="${output_file%.*}"

    # Set environment variables for the load test script
    export USER_REQUEST_INTERVAL="$user_request_interval"
    export FAILURE_THRESHOLD="$failure_threshold"

    # Need to run from scripts directory to avoid import issues
    (cd ../scripts && run_uv_command "run locust -f load_test_stream_mode.py --headless -u $users -r $ramp_rate -t $duration --host=$BASE_URL --html=../load_testing_output/$output_file --csv=../load_testing_output/$base_name")

    # Clean up environment variables
    unset USER_REQUEST_INTERVAL
    unset FAILURE_THRESHOLD
}

# Function: Run batch mode test
run_batch_phase() {
    local users="$1"
    local ramp_rate="$2"
    local user_request_interval="$3"
    local duration="$4"
    local output_file="$5"
    local description="$6"

    echo
    echo "📈 Phase 3: Batch mode load test ($duration)..."
    echo "   $description"
    echo "   Users: $users, Ramp: $ramp_rate/s, Max cycle: ${user_request_interval}s (request + wait)"

    # Set the request interval as environment variable for the load test script
    export USER_REQUEST_INTERVAL="$user_request_interval"

    run_uv_command "run locust -f ../scripts/load_test_batch_mode.py --headless -u $users -r $ramp_rate -t $duration --host=$BASE_URL --html=../load_testing_output/$output_file"

    # Clean up environment variable
    unset USER_REQUEST_INTERVAL
}

# Function: Run batch mode test
run_batch_phase() {
    local users="$1"
    local ramp_rate="$2"
    local user_request_interval="$3"
    local duration="$4"
    local output_file="$5"
    local description="$6"

    echo
    echo "📈 Phase 2: Batch mode load test ($duration)..."
    echo "   $description"
    echo "   Users: $users, Ramp: $ramp_rate/s, Max cycle: ${user_request_interval}s (request + wait)"

    # Extract base filename for generating both HTML and CSV
    local base_name="${output_file%.*}"

    # Set the request interval as environment variable for the load test script
    export USER_REQUEST_INTERVAL="$user_request_interval"

    run_uv_command "run locust -f ../scripts/load_test_batch_mode.py --headless -u $users -r $ramp_rate -t $duration --host=$BASE_URL --html=../load_testing_output/$output_file --csv=../load_testing_output/$base_name"

    # Clean up environment variable
    unset USER_REQUEST_INTERVAL
}

# Function: Run tool mode test
run_tool_phase() {
    local users="$1"
    local ramp_rate="$2"
    local user_request_interval="$3"
    local duration="$4"
    local output_file="$5"
    local description="$6"

    echo
    echo "📈 Phase 2: Tool mode load test ($duration)..."
    echo "   $description"
    echo "   Users: $users, Ramp: $ramp_rate/s, Max cycle: ${user_request_interval}s (request + wait)"

    # Extract base filename for generating both HTML and CSV
    local base_name="${output_file%.*}"

    # Set the request interval as environment variable for the load test script
    export USER_REQUEST_INTERVAL="$user_request_interval"

    run_uv_command "run locust -f ../scripts/load_test_tool_mode.py --headless -u $users -r $ramp_rate -t $duration --host=$BASE_URL --html=../load_testing_output/$output_file --csv=../load_testing_output/$base_name"

    # Clean up environment variable
    unset USER_REQUEST_INTERVAL
}

# Function: Run mixed mode test
run_mixed_phase() {
    local users="$1"
    local ramp_rate="$2"
    local user_request_interval="$3"
    local duration="$4"
    local output_file="$5"
    local description="$6"

    echo
    echo "📈 Phase 4: Mixed workload test ($duration)..."
    echo "   $description"
    echo "   Users: $users, Ramp: $ramp_rate/s, Max cycle: ${user_request_interval}s (request + wait)"

    # Set the request interval as environment variable for the load test script
    export USER_REQUEST_INTERVAL="$user_request_interval"

    run_uv_command "run locust -f ../scripts/load_test_mixed_mode.py --headless -u $users -r $ramp_rate -t $duration --host=$BASE_URL --html=../load_testing_output/$output_file"

    # Clean up environment variable
    unset USER_REQUEST_INTERVAL
}

# Function: Run analysis phase
run_analysis_phase() {
    local baseline_file="$1"

    echo
    echo "📊 Analysis: Processing results..."
    run_uv_command "run python ../scripts/analyze_load_test_results.py ../load_testing_output/$baseline_file"
}

# Function: Display OpenAI completion message
display_openai_completion() {
    local test_type="$1"
    local duration="$2"
    shift 2
    local files=("$@")

    echo
    echo "🎉 OpenAI load testing complete!"
    echo "📁 Results saved in: ../load_testing_output/"
    echo "📄 Files generated:"
    for file in "${files[@]}"; do
        echo "   - $file"
    done
    echo
    echo "⏱️  Total runtime: ~$duration"
    echo "💰 Cost Note: OpenAI testing incurs API costs. Monitor usage at https://platform.openai.com/usage"
}

# Function: Display Ollama completion message
display_ollama_completion() {
    local test_type="$1"
    local duration="$2"
    shift 2
    local files=("$@")

    echo
    echo "🎉 Ollama load testing complete!"
    echo "📁 Results saved in: ../load_testing_output/"
    echo "📄 Files generated:"
    for file in "${files[@]}"; do
        echo "   - $file"
    done
    echo
    echo "⏱️  Total runtime: ~$duration"
    echo "💰 Cost-free testing with Ollama"
}

# =============================================================================
# THRESHOLD DISCOVERY AND CONFIGURATION FUNCTIONS
# =============================================================================

# Function: Get default thresholds for a provider
get_provider_thresholds() {
    local provider="$1"

    case "$provider" in
        "openai")
            echo "TTFT_THRESHOLD=5.0"
            echo "BATCH_THRESHOLD=10.0"
            echo "HEALTH_THRESHOLD=3.0"
            ;;
        "ollama")
            # Check if this is qwen2.5:3b (slower but with tools)
            if grep -q "OLLAMA_MODEL=qwen2.5:3b" ../.env 2>/dev/null; then
                echo "TTFT_THRESHOLD=30.0"
                echo "BATCH_THRESHOLD=45.0"
                echo "HEALTH_THRESHOLD=10.0"
            else
                # tinyllama or other models
                echo "TTFT_THRESHOLD=15.0"
                echo "BATCH_THRESHOLD=20.0"
                echo "HEALTH_THRESHOLD=5.0"
            fi
            ;;
        *)
            # Conservative defaults
            echo "TTFT_THRESHOLD=30.0"
            echo "BATCH_THRESHOLD=30.0"
            echo "HEALTH_THRESHOLD=10.0"
            ;;
    esac
}

# Function: Run benchmark with custom thresholds
run_benchmark_with_thresholds() {
    local output_file="$1"
    local ttft_threshold="$2"
    local batch_threshold="$3"
    local health_threshold="$4"
    local description="$5"

    echo
    echo "📈 Phase 1: Running baseline benchmarks with custom thresholds..."
    echo "   $description"
    echo "   TTFT threshold: ${ttft_threshold}s"
    echo "   Batch threshold: ${batch_threshold}s"
    echo "   Health threshold: ${health_threshold}s"

    # Set environment variables for the benchmark script to use
    export TTFT_THRESHOLD="$ttft_threshold"
    export BATCH_THRESHOLD="$batch_threshold"
    export HEALTH_THRESHOLD="$health_threshold"

    run_uv_command "run pytest ../scripts/benchmark_baseline.py --benchmark-json=../load_testing_output/$output_file -v"

    # Clean up environment variables
    unset TTFT_THRESHOLD BATCH_THRESHOLD HEALTH_THRESHOLD
}

# Function: Run benchmark with provider-specific thresholds
run_provider_benchmark_phase() {
    local output_file="$1"
    local provider="$2"
    local description="$3"

    # Get thresholds for this provider
    local thresholds=$(get_provider_thresholds "$provider")
    local ttft_threshold=$(echo "$thresholds" | grep TTFT_THRESHOLD | cut -d'=' -f2)
    local batch_threshold=$(echo "$thresholds" | grep BATCH_THRESHOLD | cut -d'=' -f2)
    local health_threshold=$(echo "$thresholds" | grep HEALTH_THRESHOLD | cut -d'=' -f2)

    run_benchmark_with_thresholds "$output_file" "$ttft_threshold" "$batch_threshold" "$health_threshold" "$description"
}


# Function: Auto-detect provider and run appropriate benchmark
run_auto_benchmark_phase() {
    local output_file="$1"
    local description="$2"

    # Auto-detect provider
    local provider="unknown"
    if grep -q "LLM_PROVIDER=openai" ../.env 2>/dev/null; then
        provider="openai"
    elif grep -q "LLM_PROVIDER=ollama" ../.env 2>/dev/null; then
        provider="ollama"
    fi

    echo "🔍 Auto-detected provider: $provider"
    run_provider_benchmark_phase "$output_file" "$provider" "$description"
}

# Function: Check if capacity discovery is recommended
recommend_capacity_discovery() {
    local provider="$1"

    echo "💡 CAPACITY DISCOVERY AVAILABLE"
    echo "   To find optimal load test parameters, consider running:"
    echo "   ./run_capacity_discovery.sh $provider"
    echo
    echo "   This will discover maximum concurrent users and optimal load settings"
    echo "   for your specific environment and model configuration."
    echo
}
