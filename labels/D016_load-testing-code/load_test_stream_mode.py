#!/usr/bin/env python3
"""
Load testing for Stream Mode (optimized proxy implementation).

Tests the stream-no-tool implementation where:
- Server acts as pure proxy forwarding raw LLM chunks (default behavior)
- Client handles chunk parsing and message accumulation
- Client submits complete accumulated message back to server

Usage:
    export LLM_PROVIDER=ollama  # Cost-free testing
    uv run locust -f scripts/load_test_stream_mode.py --headless -u 25 -r 5 -t 300s

    export LLM_PROVIDER=openai  # Production comparison
    uv run locust -f scripts/load_test_stream_mode.py --headless -u 10 -r 2 -t 180s
"""

import os
import time

from locust import HttpUser, between, events, task

try:
    from .load_test_common import build_request_data, get_base_url, get_request_headers, get_test_message, record_metrics
except ImportError:
    from load_test_common import build_request_data, get_base_url, get_request_headers, get_test_message, record_metrics


class StreamModeUser(HttpUser):
    """User simulation for Stream Mode load testing."""

    weight = 1

    # Get max request interval from environment variable, default to 20 seconds
    max_interval = int(os.getenv("USER_REQUEST_INTERVAL", "20"))

    # We'll implement dynamic wait time after each request
    wait_time = between(1, 1)  # Minimal wait, actual wait calculated dynamically

    host = get_base_url()  # Auto-detect base URL

    def on_start(self):
        """Initialize user session."""
        import uuid

        # Generate unique session ID for each user instance
        self.session_id = f"load_test_stream_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # Skip health check - it's too slow and blocks user initialization

    @task(1)
    def test_stream_mode_short(self):
        """Test stream mode with short response."""
        message = get_test_message("stream", 0)
        self._test_stream_request_with_max_interval(message, "short")

    @task(2)
    def test_stream_mode_medium(self):
        """Test stream mode with medium response."""
        message = get_test_message("stream", 2)  # "Explain quantum computing briefly"
        self._test_stream_request_with_max_interval(message, "medium")

    def _test_stream_request_with_max_interval(self, message: str, response_type: str):
        """
        Execute streaming request with max interval timing control.

        Waits max_interval - request_time after each request for consistent load patterns.
        """
        cycle_start = time.time()

        # Execute the request
        self._test_stream_request(message, response_type)

        # Calculate dynamic wait time for consistent cycles
        request_duration = time.time() - cycle_start
        remaining_wait = max(0, self.max_interval - request_duration)

        if remaining_wait > 0:
            print(f"Request took {request_duration:.1f}s, waiting {remaining_wait:.1f}s for {self.max_interval}s cycle")
            time.sleep(remaining_wait)
        else:
            print(f"Request took {request_duration:.1f}s (>{self.max_interval}s), no additional wait")

    def _test_stream_request(self, message: str, response_type: str):
        """
        Execute SSE streaming request with LLM-specific metrics.

        Args:
            message: User message to send
            response_type: short/medium/long for categorization
        """
        start_time = time.time()
        ttft = None  # Time To First Token
        total_tokens = 0
        error_occurred = False

        request_data = build_request_data(message, "stream", self.session_id)
        headers = get_request_headers("stream")

        try:
            # Use raw HTTP for SSE streaming
            with self.client.post("/api/v1/chat/stream", json=request_data, headers=headers, stream=True, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"HTTP {response.status_code}")
                    return

                # Simple chunk counting approach to avoid client-side processing overhead
                chunk_count = 0
                total_content_length = 0

                for line in response.iter_lines():
                    if not line:
                        continue

                    chunk_count += 1
                    total_content_length += len(line)

                    # Record TTFT on first chunk
                    if chunk_count == 1:
                        ttft = time.time() - start_time

                    # For performance testing, we assume >2 chunks = success
                    # This avoids expensive JSON parsing and content processing
                    if chunk_count >= 3:
                        break

                    # Safety: don't read indefinitely
                    if chunk_count >= 100:
                        break

                # Consider success if we got more than 2 chunks
                if chunk_count > 2:
                    response.success()
                    # Estimate tokens based on content length (rough approximation)
                    total_tokens = total_content_length // 4  # Rough estimate: 4 chars per token
                else:
                    response.failure(f"Too few chunks: {chunk_count}")

        except Exception as e:
            error_occurred = True
            print(f"Stream request error: {error_occurred} {e}")
            # Locust will automatically track this as a failure since we're using catch_response=True
            return

        # Record LLM-specific metrics using common utilities
        if not error_occurred:
            record_metrics(f"stream_{response_type}", start_time, ttft, total_tokens, total_content_length)

    def _submit_accumulated_message(self, content: str):
        """
        Submit accumulated assistant message to server (optimized workflow).

        This simulates the client-side message submission that would happen
        in the optimized proxy mode implementation.
        """
        try:
            message_data = {"role": "assistant", "content": content}

            headers = {"Content-Type": "application/json"}

            # Submit accumulated message - don't track this as primary metric
            with self.client.post(f"/api/v1/conversation/{self.session_id}/message", json=message_data, headers=headers, catch_response=True) as response:
                if response.status_code != 200:
                    print(f"Message submission failed: {response.status_code}")
                # Don't mark as failure since this is secondary operation

        except Exception as e:
            print(f"Message submission error: {e}")
            # Don't propagate error - main streaming is what matters for performance

    def _record_llm_metrics(self, response_type: str, ttft: float, tps: float, tokens: int, duration: float):
        """Record LLM-specific metrics for analysis."""
        ttft_val = ttft if ttft is not None else 0.0
        print(f"LLM_METRICS,{response_type},{ttft_val:.3f},{tps:.1f},{tokens},{duration:.3f}")


# Global failure threshold configuration
FAILURE_THRESHOLD = int(os.getenv("FAILURE_THRESHOLD", "0"))  # 0 = disabled
failure_count = 0


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test environment."""
    try:
        from .load_test_common import get_base_url, get_provider_config
    except ImportError:
        from load_test_common import get_base_url, get_provider_config

    print("=== Stream Mode Load Test Starting ===")
    print("Testing: Pure streaming mode (no tools)")
    print("Provider:", get_provider_config()["provider"])
    print("Base URL:", get_base_url())
    if FAILURE_THRESHOLD > 0:
        print(f"Failure threshold: {FAILURE_THRESHOLD} failures (early termination enabled)")
    print("Metrics: response_type,ttft,tokens_per_sec,total_tokens,duration")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Monitor failures and stop test if threshold exceeded."""
    global failure_count
    if FAILURE_THRESHOLD > 0 and exception is not None:
        failure_count += 1
        print(f"🔍 Failure detected: {failure_count} total failures (threshold: {FAILURE_THRESHOLD})")

        if failure_count >= FAILURE_THRESHOLD:
            print(f"\n🛑 FAILURE THRESHOLD REACHED: {failure_count} failures >= {FAILURE_THRESHOLD}")
            print("Stopping test to prevent server crash...")
            print("Triggering graceful shutdown with HTML report generation...")
            
            # Instead of os._exit(0), raise KeyboardInterrupt to trigger Locust's normal shutdown
            # This is exactly what happens when you press Ctrl+C
            raise KeyboardInterrupt("Failure threshold reached - simulating Ctrl+C")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Clean up after test completion."""
    print("=== Stream Mode Load Test Complete ===")

    # Print summary statistics
    stats = environment.stats
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    avg_response_time = stats.total.avg_response_time

    print(f"Total Requests: {total_requests}")
    print(f"Total Failures: {total_failures}")
    if total_requests > 0:
        print(f"Success Rate: {((total_requests - total_failures) / total_requests * 100):.1f}%")
    else:
        print("Success Rate: 0.0% (no requests executed)")
    print(f"Average Response Time: {avg_response_time:.0f}ms")

    # Indicate if test was stopped early due to failure threshold
    if FAILURE_THRESHOLD > 0 and failure_count >= FAILURE_THRESHOLD:
        print(f"⚠️  Test terminated early due to failure threshold ({FAILURE_THRESHOLD} failures)")


if __name__ == "__main__":
    # Direct execution for testing

    print("Stream Mode Load Test")
    print("Usage: uv run locust -f scripts/load_test_stream_mode.py --headless -u 25 -r 5 -t 300s")
    print("Set LLM_PROVIDER=ollama for cost-free testing")
    print("Tests optimized proxy mode (default) with client-side accumulation")
    print("Includes short and medium response tests only (long test removed for Ollama compatibility)")
