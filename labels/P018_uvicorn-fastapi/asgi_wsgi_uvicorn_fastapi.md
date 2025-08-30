## Uvicorn FastAPI Execution Behavior

**Key Principle**:

- FastAPI is always ASGI, but handles sync/async functions differently
- **both** working together - FastAPI **always** coordinates with Uvicorn, but uses different execution paths:

Responsibility Breakdown:

- **FastAPI**: Makes the decision (async vs sync)
- **Uvicorn**: Provides the thread pool infrastructure

| Function Type | FastAPI Action              | Uvicorn Role            |
|---------------|-----------------------------|-------------------------|
| **async def** | Runs directly in event loop | Provides the event loop |
| **def**       | Calls `run_in_threadpool()` | Executes in thread pool |

### Function Type Handling

| Function Declaration   | Execution Method                 | Performance | Use Case                             |
|------------------------|----------------------------------|-------------|--------------------------------------|
| `async def endpoint()` | Event loop (single thread)       | ⚡ High      | I/O-bound, database calls, API calls |
| `def endpoint()`       | Thread pool (ThreadPoolExecutor) | 🐌 Lower    | CPU-bound, legacy sync code          |

## Flow Diagram

```
Request Flow:
[Uvicorn] ── [FastAPI] ──┬── async def ── Event Loop
                         └── def ── Thread Pool
```

## Code Example

```text
# FastAPI makes the decision
@app.get("/sync")
def sync_endpoint():  # FastAPI sees "def" 
    pass              # → Tells Uvicorn: "use thread pool"


@app.get("/async")
async def async_endpoint():  # FastAPI sees "async def"
    pass                     # → Uses event loop directly
```

## Technical Detail

```python
# Simplified FastAPI internal logic
if inspect.iscoroutinefunction(endpoint):
    # Run directly in event loop
    result = await endpoint()
else:
    # FastAPI asks Uvicorn's thread pool to run it
    result = await run_in_threadpool(endpoint)
```

----

## `Real Threads + GIL` vs `Virtual Threads`

### Real Threads vs Virtual Threads

| Type                | Definition                           | Python Support           |
|---------------------|--------------------------------------|--------------------------|
| **Real Threads**    | OS-managed threads                   | ✅ Yes (threading module) |
| **Virtual Threads** | Language-managed lightweight threads | ❌ No (Java 21+ concept)  |

### The GIL (Global Interpreter Lock) Effect

```
Python GIL Reality:
[CPU Process]  ── [Real Thread 1] ──┐
               ── [Real Thread 2] ──┼── Only ONE executes Python at a time
               ── [Real Thread 3] ──┘
```

| Scenario           | Thread Behavior                                       |
|--------------------|-------------------------------------------------------|
| **CPU-bound work** | Threads blocked by GIL, no parallelism                |
| **I/O-bound work** | Threads release GIL during I/O, effective parallelism |
