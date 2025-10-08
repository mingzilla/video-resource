# aiohttp vs httpx: HTTP Client Comparison

## 1. Usage Context

- **Server**: FastAPI + Uvicorn (already handling HTTP server responsibilities)
- **Client Need**: HTTP client library for making outbound requests
- **Use Cases**: Batch requests, streaming responses, LLM API calls

## 2. Key Insight: Scope vs Performance

| Library     | Scope                    | Concurrent Requests Before Issues | Size    | Comment                    |
|-------------|--------------------------|-----------------------------------|---------|----------------------------|
| **aiohttp** | Contains: Client, Server | ~300                              | Bigger  | More than needed, but fast |
| **httpx**   | Contains: Client         | ~30                               | Smaller | Smaller, but slow          |

## 3. FastAPI ASGI Compatibility

**Important**: Both libraries work perfectly with FastAPI ASGI applications as HTTP clients.

| Scenario                         | aiohttp     | httpx       | Best Choice          |
|----------------------------------|-------------|-------------|----------------------|
| **FastAPI → External API calls** | ✅ Yes       | ✅ Yes       | Either works         |
| **FastAPI → LLM APIs**           | ✅ Yes       | ✅ Yes       | Both excellent       |
| **FastAPI → HTTP/2 services**    | ❌ No        | ✅ Yes       | **httpx required**   |
| **FastAPI + WebSocket clients**  | ✅ Yes       | ❌ No        | **aiohttp required** |
| **Async API**                    | ✅ Yes       | ✅ Yes       | Both native async    |
| **LLM Streaming**                | ✅ Excellent | ✅ Excellent | Both excellent       |
| **High Concurrency**             | ✅ Optimized | ⚠️ Issues*  | **aiohttp**          |

## 4. Performance Comparison with Evidence

| Scenario                        | aiohttp Performance | httpx Performance | Evidence Source     |
|---------------------------------|---------------------|-------------------|---------------------|
| **Low concurrency (< 20 req)**  | Excellent           | Good              | Both work fine      |
| **Medium concurrency (20-100)** | Excellent           | **10x slower**    | GitHub Issue #3215  |
| **High concurrency (300+ req)** | Excellent           | **Fails/crashes** | GitHub Issue #3348  |
| **HTTP/2 optimized APIs**       | N/A                 | Superior          | Only httpx supports |
| **Streaming responses**         | Excellent           | Good              | Both work           |

### Httpx issue root cause:

- Root Cause - **httpx uses `anyio`** instead of direct `asyncio`.
- Can they swap out? - **Not easily**, because it's a **fundamental architectural decision**, backward compatibility:

| Library     | Implementation                    | Performance Impact              |
|-------------|-----------------------------------|---------------------------------|
| **aiohttp** | Direct `asyncio`                  | Fast, no overhead               |
| **httpx**   | `asyncio` → `anyio` → actual work | Slower due to abstraction layer |

## 5 Side by side example code

```python
# aiohttp approach
async def stream_llm_aiohttp(prompt: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json={"messages": [{"role": "user", "content": prompt}], "stream": True},
                headers={"Authorization": f"Bearer {api_key}"},
        ) as response:
            async for line in response.content:
                if line.startswith(b"data: "):
                    yield line[6:].decode()


# httpx approach  
async def stream_llm_httpx(prompt: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                json={"messages": [{"role": "user", "content": prompt}], "stream": True},
                headers={"Authorization": f"Bearer {api_key}"},
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line[6:]
```

## Summary

### Key Trade-offs for FastAPI + Uvicorn Users:

| Factor              | aiohttp                                     | httpx                                  |
|---------------------|---------------------------------------------|----------------------------------------|
| **Library Weight**  | ❌ **Heavier** (includes unused server code) | ✅ **Lighter** (client-only)            |
| **Performance**     | ✅ **Excellent** (direct asyncio)            | ❌ **Poor under load** (anyio overhead) |
| **HTTP/2 Support**  | ❌ No                                        | ✅ Yes                                  |
| **Concurrent Load** | ✅ Rough Scale: **300 requests**             | ❌ Rough Scale: **30 requests**         |
