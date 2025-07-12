# LLM Streaming: Resource Management

1. Request Types and Connection Behavior; streaming (problem)
2. Timeout Strategy Considerations (solution)
3. Resource Consumption Analysis (justification)
4. Implementation (example)

## 1. Request Types and Connection Behavior

| **Request Type** | **Scenario**                  | **Connection Behavior**       | **Timeout Applied**      |
|------------------|-------------------------------|-------------------------------|--------------------------|
| **Batch**        | Response complete / error     | Close connection immediately  | Standard request timeout |
| **Streaming**    | Done signal received          | Close connection              | N/A                      |
| **Streaming**    | Error signal received         | Close connection              | N/A                      |
| **Streaming**    | Chunk received before timeout | Reset chunk timeout, continue | Chunk timeout resets     |
| **Streaming**    | No chunk within timeout       | Force close connection        | Chunk timeout triggers   |

### Streaming Connection Lifecycle

```
Timeline: [Start] → [Chunk 1] → [Delay] → [Chunk 2] → [Delay] → [Done/Error/Timeout]
          ↓         ↓           ↓         ↓           ↓         ↓
Timeout:  [Reset]   [Reset]     [Count]   [Reset]     [Count]   [Close]
```

**Key Point - Timeout**:

- When chunk timeout triggers, the connection closes regardless of whether the remote server has more data to send.
- The remote server detects the closed connection and may stop processing.

## 2. Timeout Strategy Considerations

### **Chunk Timeout vs Total Timeout**

| **Timeout Type**  | **Purpose**              | **Use Case**                   | **Recommended Value**     |
|-------------------|--------------------------|--------------------------------|---------------------------|
| **Chunk Timeout** | Zombie request detection | Detect stuck/silent streams    | 30-60 seconds             |
| **Total Timeout** | Resource protection      | Limit overall request duration | 300-600 seconds (or None) |

### **When to Use Each Strategy**

```
Research/MCP Requests:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Tool Call (60s) │  →  │ Thinking (90s)  │  →  │ Response (30s)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
 ↓ Chunk timeout: 30s   ↓ Chunk timeout: 30s    ↓ Chunk timeout: 30s
 ↓ Total timeout: None  ↓ Total timeout: None   ↓ Total timeout: None

Simple Chat Requests:
┌─────────────────┐
│ Response (45s)  │
└─────────────────┘
 ↓ Chunk timeout: 30s
 ↓ Total timeout: 120s
```

**Decision Matrix**:

- **No total timeout**: Research queries, MCP tool chains, document analysis
- **With total timeout**: Simple chat, user-facing APIs, resource-constrained environments

## 3. Resource Consumption Analysis

### **Why Python async Long Streams are Resource-Efficient**

```python
async def long_running_stream():
    async for chunk in llm_stream():  # 10+ minute duration
        # Memory usage ---- constant ~8KB
        # CPU usage ------- spikes only when chunk arrives
        # Between chunks -- virtually zero resource usage
        yield chunk
```

## 4. Implementation Example

```python
async def mcp_stream_with_dual_timeout():
    chunk_timeout = httpx.Timeout(
        connect=10.0,  # -- 10s to establish connection
        read=30.0,  # ----- 30s between chunks (this is your zombie detector!)
        write=10.0,  # ---- 10s to send request
        pool=None  # ------ Unlimited time to get a connection from the pool
    )
    total_timeout = 300  # 5 minutes total

    async with AsyncClient(timeout=chunk_timeout) as client:
        try:
            async with asyncio.timeout(total_timeout):  # Python 3.11+
                async with client.stream("POST", url, json=data) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
        except asyncio.TimeoutError:
            raise ZombieRequestError("Total timeout - reached")
        except ReadTimeout:
            raise ZombieRequestError("Chunk timeout - stream went silent")
```
