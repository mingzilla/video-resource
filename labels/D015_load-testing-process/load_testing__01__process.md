# Load Testing Process - Complete Methodology

## Document Structure

```
Load Testing Methodology
|-- 1. WHAT: The 5-Phase Load Testing Process
|   |-- 1.1 Phase 1: Capacity Discovery (One-time setup)
|   |-- 1.2 Phase 2: System Warm-up (Before baseline measurement)
|   |-- 1.3 Phase 3: Baseline Establishment (After system warm-up)
|   |-- 1.4 Phase 4: Load Testing (Main test with discovered capacity)
|   |   +-- 1.4.1 Test Type - Example Config
|   +-- 1.5 Phase 5: Result Validation (Performance analysis)
|-- 2. WHY: Key Decisions
|   |-- 2.1 Capacity Discovery Benefits
|   |-- 2.2 System Warm-up Benefits
|   |-- 2.3 Baseline Testing Benefits
|   |-- 2.4 Intentional 2-8% Failure Rate Benefits
|   |-- 2.5 Comparison Analysis Benefits
|   +-- 2.6 Deployment Config and Resource Settings
|-- 3. HOW: Implementation in This Project
|   |-- 3.1 Usage of Ollama
|   |-- 3.2 Scripts and Tools
|   |-- 3.3 File Outputs
|   |-- 3.4 LLM-Powered Comparison Analysis
|   |   |-- 3.4.1 LLM-Powered Comparison Analysis
|   |   |-- 3.4.2 Why CSV vs JSON Issue Exists
|   |   +-- 3.4.3 Comparison Workflow
|   +-- 3.5 Result Storage
+-- 4. Key Success Metrics
```

## Overview

This document outlines the 5-phase load testing methodology that provides reliable, data-driven performance insights for production capacity planning.

```text
Quick 5-Step Process Flow:

[1] Capacity Discovery --> [2] System Warm-up --> [3] Baseline Establishment --> [4] Load Testing --> [5] Result Validation
      |                          |                      |                              |                      |
    Find system limits     Wake up system         Measure 1-user speed           Test with N users      Analyze e.g. 1 vs N users
      |                          |                      |                              |                      |
    "Max 650 users"        "2-3 requests"         "2000ms response"              "2300ms @ 650 users"   "15% degradation ~= reasonable"
```

## 1. The 5-Phase Load Testing Process

### 1.1 Phase 1: Capacity Discovery (One-time setup)

**Purpose**: Find the maximum users your system can handle

**Process**:

- Run automated capacity discovery script
- Uses adaptive binary search to find system limits
- Tests multiple load levels until failure point

**Example Output**:

```
[OK] 650 users: 100.0% success, 2012ms avg, 110.8 RPS
[FAIL] 675 users: 0.0% success (Windows FD limit reached)

RECOMMENDATIONS:
- SAFE LOAD: 650 concurrent users (OS-safe margin)
- MAXIMUM: 675 concurrent users (edge of OS constraint)
```

**Action**: Use discovery results to set realistic test parameters

### 1.2 Phase 2: System Warm-up (Before baseline measurement)

**Purpose**: Prepare system for accurate baseline measurements by eliminating cold start effects

**Process**:

- Send 2-3 simple requests to wake up application components
- Allow database connections to establish and connection pools to initialize
- Let JIT compilation, caches, and lazy loading complete
- Brief pause to ensure system reaches steady state

**Example Output**:

```
Warming up system...
Health check 1: 4500ms (cold start)
Health check 2: 2100ms (warming up)
Health check 3: 2000ms (steady state)
System ready for baseline measurement
```

**Action**: Proceed to baseline measurement with warmed-up system

**Why System Warm-up Matters**:
Cold start issues can make the first request 2-10x slower due to:

- Application initialization and framework setup
- Database connection pool establishment
- JIT compilation and code optimization
- Cache loading and lazy component initialization

Without warm-up, baseline measurements would be inflated (e.g., 5000ms instead of 2000ms), making load test comparisons meaningless.

### 1.3 Phase 3: Baseline Establishment (After system warm-up)

**Purpose**: Measure single-user performance to ensure system health

**Process**:

- Run pytest-benchmark on individual endpoints
- Measure response times with no load
- Establish performance baseline before load testing

**Example Output**:

```
test_stream_mode_baseline: 2000ms average response time
test_health_check_baseline: 300ms average response time
```

**Action**: Verify system is healthy before proceeding to load testing

**Why Baseline Testing Matters**:
The baseline helps you understand:

- How fast is one user vs 650 users?
- Is the system degrading under load?
- What is the performance cost of concurrency?

For example, if single-user response time is 2000ms and 650-user average is 2300ms, you know the system handles load well with only 15% degradation.

### 1.4 Phase 4: Load Testing (Main test with discovered capacity)

**Purpose**: Measure system performance under realistic load

**Process**:

- Run Locust with parameters from capacity discovery (e.g., 650 users)
- Generate both HTML reports (visual) and CSV data (analysis)
- Measure throughput, response times, and failure rates

**Example Output**:

```
650 concurrent users: 2300ms average response time
Success rate: 96.2% (2-8% failure rate target)
Throughput: 100.6 RPS
```

**Action**: Collect structured performance data for analysis

#### 1.4.1. Test Type - Example Config

| Test Type          | Users (Capacity %) | Ramp Rate     | Duration | Benchmark | Purpose              |
|--------------------|--------------------|---------------|----------|-----------|----------------------|
| **Average Load**   | 500 (70-80%)       | 10 users/sec  | 10 min   | 0%        | Production Usage     |
| **Stress Testing** | 650 (90-100%)      | 10 users/sec  | 10 min   | 2-8%      | Regression Detection |
| **Spike Testing**  | 500 (70-80%)       | 250 users/sec | 3 min    | 2-8%      | Recovery Benchmark   |

### 1.5 Phase 5: Result Validation (Performance analysis)

**Purpose**: Analyze results and generate actionable recommendations

**Target Metrics**:

- 2-8% failure rate: More realistic than 100% success, better regression detection
- Performance degradation: Compare load vs baseline (2300ms vs 2000ms = 15% degradation)
- Scaling assessment: Determine if system scales well under load

**Example Analysis**:

```
PERFORMANCE ANALYSIS:
[EXCELLENT] Classification: Outstanding performance
Baseline: 2000ms (single user)
Load test: 2300ms (650 users)
Degradation: 15% (Excellent scaling)

BUSINESS RECOMMENDATIONS:
Production Safe Load: 454 concurrent users
Optimal Load: 650 concurrent users
Scaling: System can likely handle more load
```

**Action**: Use recommendations for production capacity planning

## 2. Key Decisions

### 2.1 Capacity Discovery Benefits

- Prevents wasting time with unrealistic parameters
- Avoid long manual process to hunt for this value e.g. 650
- Finds actual system limits rather than guessing
- Accounts for OS constraints (file descriptors, memory, etc.)

### 2.2 System Warm-up Benefits

- Eliminates cold start bias from baseline measurements
- Ensures accurate single-user performance data
- Prevents inflated response times from system initialization
- Industry standard practice for reliable load testing
- Makes baseline vs load test comparisons meaningful

### 2.3 Baseline Testing Benefits

- Ensures system health before load testing
- Provides comparison point for load test results
- Detects infrastructure issues before they affect load tests
- Shows performance cost of concurrency (1 user vs N users)
- Enables regression detection over time

### 2.4 Intentional 2-8% Failure Rate Benefits

- More realistic than 100% success testing
- Ability for regression detection - catches performance degradation
- Simulates real-world conditions where some requests may fail
- Provides meaningful stress testing data

### 2.5 Comparison Analysis Benefits

- Shows scaling characteristics of your system
- Identifies bottlenecks before they become production issues
- Provides confidence in production capacity planning
- Enables data-driven scaling decisions

### 2.6 Deployment Config and Resource Settings

Recommended Docker Deployment for FastAPI Applications:

**Single-CPU FastAPI Container Setup**:

```bash
# Build container
docker build -t fastapi-app .

# Run with 1 CPU limit and memory constraint
docker run -d \
  --cpus="1.0" \
  --memory="2g" \
  --name fastapi-load-test \
  -p 9000:9000 \
  fastapi-app

# Monitor resources during load testing
docker stats fastapi-load-test
```

**Load Testing Considerations**:

1. **CPU Utilization**: FastAPI async performance degrades significantly above 80% CPU
2. **Memory Monitoring**: Watch for memory leaks during sustained load
3. **Container vs Host**: Ensure load test results reflect production container limits
4. **Production Parity**: Use same CPU/memory limits in load testing as production

**Key Metrics to Monitor**:

- CPU usage should stay below 80% at optimal load
- Memory usage should remain stable (no continuous growth)
- Container networking overhead vs direct host testing

## 3. Implementation in This Project

### 3.1 Usage of Ollama

Use ollama to avoid cost. Models:

- tinyllama - no tool
- Qwen 2.5:3b - tooled

```text
limits:
  cpus: '4'
  memory: '4096M'
```

### 3.2 Scripts and Tools

- Capacity Discovery: `./run_capacity_discovery.sh ollama`
- System Warm-up: Automated via `run_warmup_phase()`
- Baseline: Automated via `run_provider_benchmark_phase()`
- Load Testing: `./run_load_testing_ollama_8min.sh`
- Analysis: `generate_csv_report.py` with business recommendations

### 3.3 File Outputs

- Baseline: `baseline_ollama_8min.json` (pytest-benchmark format)
- Load Test: `stream_ollama_8min_stats.csv` (Locust CSV format)

#### 3.4.1. LLM-Powered Comparison Analysis

For comprehensive 1-user vs N-user comparison analysis, use the LLM prompt template approach:

**Files to provide to LLM**:

- `load_testing__01__section_5_result_comparison_prompt.md` (analysis instructions)
- `baseline_ollama_8min.json` (single-user performance data)
- `stream_ollama_8min_stats.csv` (multi-user load test data)

**Benefits**:

- Robust to tool format changes (pytest-benchmark, Locust output schemas)
- Natural language business insights and recommendations
- Can test with multiple LLM providers for different perspectives
- No maintenance of parsing logic for evolving tool formats

#### 3.4.2. Why CSV vs JSON Issue Exists

```text
The Problem: We have two different tools generating two different formats:

1. Baseline (1 user): pytest-benchmark → JSON format
- Tool: pytest with --benchmark-json flag
- Output: baseline_ollama_8min.json
- Format: pytest-benchmark specific JSON structure
2. Load Test (650 users): Locust → CSV format
- Tool: Locust with --csv flag
- Output: stream_ollama_8min_stats.csv
- Format: Locust CSV structure

Why Not Both JSON?

Locust JSON Issue: Locust doesn't have a native --json flag (that's why we got the error earlier). It only supports:
- --html (visual reports)
- --csv (structured data)

Different Tool, Different Format:
- pytest-benchmark naturally outputs JSON
- Locust naturally outputs CSV
- They're different tools - so the best way for comparision is using an LLM
```

#### 3.4.3. Comparison Workflow

```text
Usage Workflow:

1. Run your load test (generates the 2 data files)
2. Copy 3 files to any LLM (Claude, ChatGPT, etc.):
- load_testing__01__section_5_result_comparison_prompt.md
- baseline_ollama_8min.json
- stream_ollama_8min_stats.csv
3. Get comprehensive business analysis comparing 1-user vs 650-user performance
```

### 3.4 Result Storage

Consider storing results into SQL database, so that different versions of tests can perform comparison.

## 4. Key Success Metrics

| Metric Category             | Excellent Performance Indicators         | Warning Signs                         |
|-----------------------------|------------------------------------------|---------------------------------------|
| **Single-user Performance** | Sub-3 second response times              | Getting slower over time              |
| **Load Degradation**        | Less than 25% increase under load *      | More than 50% response time increase  |
| **Failure Rate**            | 2-8% under stress testing                | More than 10% failures at target load |
| **Scaling**                 | Linear relationship with user throughput | Hitting OS limits at low user counts  |

- Load Degradation - depends on application (some may need <5%)

This 5-phase methodology provides reliable, data-driven insights for production capacity planning while minimizing testing costs through local Ollama usage.
