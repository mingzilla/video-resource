# Python Async Concepts
- Generator and Coroutine (`yield` & `await`)
- Async Programming in Python
- Does `await` consume resource?
- Does `await` hang another FastAPI Requests?

## Generator and Coroutine

- `yield` & `await`
- `Event Loop` = A single-threaded manager that coordinates all async tasks

### English Word "Yield"

"Yield" has multiple meanings in English:

| Context         | Meaning            | Example                       |
|-----------------|--------------------|-------------------------------|
| **Production**  | Create/Generate    | "Farm yields crops"           |
| **Traffic**     | Give way/surrender | "Yield to oncoming traffic"   |
| **Programming** | Give up/hand over  | "Yield control to event loop" |

- `yield` means: Give UP CPU control to `event loop`

### Generator and Coroutine

| Concept                 | Note                                                                                                    |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| `yield` → Generator     | Any function with `yield` becomes generator                                                             |
| `await` → Coroutine     | Any function with `await` becomes coroutine, function with `await` **must** be defined with `async def` |
| `async def` → Coroutine | Any function with `async def` becomes coroutine, Having `await` is just one version of it               |

#### `await` without `async def` - SyntaxError:

```python
# ❌ SyntaxError
def regular_function():
    await something()


# ✅ Has await, so function has to have `async def`
async def coroutine_function():
    await something()
```

### `yield` and `await`

| Keyword     | What It Does                   | Who Gets Control             |
|-------------|--------------------------------|------------------------------|
| **`yield`** | ✅ Yields control to caller     | Specific caller gets control |
| **`await`** | ✅ Yields control to event loop | Event loop decides next task |

### Both Yield Control, But Differently

```python
# yield - yields to CALLER  
def function_with_yield():
    print("Before yield")
    yield "some value"  # ← Yields to CALLER (whoever called next())
    print("After yield")

# await - yields to EVENT LOOP
async def function_with_await():
    print("Before await")
    await asyncio.sleep(1)  # ← Yields to EVENT LOOP
    print("After await")

```

### Visual Comparison

#### `await` Flow

```
[Task A] ──await──> [Event Loop] ──decides──> [Task B]
    ^                     |                       |
    |                     |                       |
    |<──resumes when ready<|<──await yields back<─|
```

#### `yield` Flow

```
[Generator] ──yield──> [Caller] 
    ^                     |
    |                     |
    |<──resumes when      |
       caller calls next()
```

## Async Programming in Python

The point of async functions is to avoid blocking the Python thread.

### Sync (Blocking):

```python
import time


def sync_function():
    time.sleep(1)  # ❌ BLOCKS entire thread for 1 second


def sync_example():
    sync_function()  # ❌ Thread frozen here - nothing else can run
    sync_function()  # ❌ Thread frozen again


sync_example()
# Total time: 2+ seconds (sequential)
```

### Async (NON-blocking):

```python
import asyncio


async def async_function():
    await asyncio.sleep(1)  # ✅ YIELDS control - other tasks can run


async def async_example():
    task1 = asyncio.create_task(async_function())  # Start task 1
    task2 = asyncio.create_task(async_function())  # Start task 2

    await task1  # ✅ Yields control if task1 not done yet
    await task2  # ✅ Yields control if task2 not done yet


await async_example()
# Total time: ~1 second (concurrent)
```

### Async (But Blocking):

```python
import asyncio


async def async_function():
    await asyncio.sleep(1)  # ✅ YIELDS control - other tasks can run


async def async_example():
    await asyncio.create_task(async_function())
    await asyncio.create_task(async_function())


await async_example()
# Total time: 2+ seconds (sequential)
```

### Async (no await):

```python
import asyncio


# async function without await
async def async_no_await(x: int) -> int:
    print(f"Processing {x}")
    return x * 2


async def test_comparison():
    # ❌ This creates a coroutine object but doesn't run it
    coro = async_no_await(5)  # Returns coroutine, doesn't execute
    print(type(coro))  # <class 'coroutine'>

    # ✅ Must await to actually execute
    result1 = await async_no_await(5)  # Actually executes
    print(f"async result: {result1}")


# Running the test
asyncio.run(test_comparison())
```

## Does `await` consume resource?

Your understanding is **spot-on**:

### What `await` Actually Does

| Aspect             | Reality                          | Resource Usage         |
|--------------------|----------------------------------|------------------------|
| **Code execution** | ✅ Pauses/hangs this coroutine    | None - just a bookmark |
| **Thread**         | ✅ Continues running other tasks  | No blocking            |
| **Memory**         | ✅ Stores minimal state to resume | ~few KB per coroutine  |
| **CPU**            | ✅ Zero CPU while waiting         | None while suspended   |

### Visual Representation

```python
# Timeline of what happens during await
async def get_users():
    print("1. Start function")  # Uses CPU

    async with AsyncSession() as session:
        print("2. About to await")  # Uses CPU

        result = await session.execute(...)  # ← AWAIT POINT
        # |
        # | Code is "hung" here, but:
        # | - Thread continues with other work
        # | - No CPU usage
        # | - Just a memory reference to resume point
        # |
        # ↓ Database returns result

        print("3. Resumed after await")  # Uses CPU again
        return result.fetchall()
```

## Does `await` hang another FastAPI Requests

**No!** Each FastAPI request gets its own coroutine:

### Request Independence

```python
@app.get("/users-correct")
async def get_users_correct():
    user_id = request.state.user_id  # Each request has unique ID
    print(f"Request {user_id} starting")

    async with AsyncSession() as session:
        # Request 1 hangs here, but Request 2 can start independently
        result = await session.execute(text("SELECT * FROM users"))
        data = result.fetchall()

    print(f"Request {user_id} finishing")
    return {"users": data}
```

### Timeline of Concurrent Requests

```
Time: 0s    1s    2s    3s
      |     |     |     |
Req1: [--await database--][response]
      |     |     |     |
Req2:   [--await database--][response]  ← Started while Req1 waiting
      |     |     |     |
Req3:     [--await database--][response]  ← Started while Req1&2 waiting
```

## Memory Footprint Comparison

| Pattern           | Memory per Request     | CPU per Request    |
|-------------------|------------------------|--------------------|
| **Sync blocking** | ~8MB (full thread)     | Blocked during I/O |
| **Async await**   | ~2KB (coroutine state) | Zero during I/O    |

### Why This Works

```python
# FastAPI automatically creates independent coroutines
@app.get("/users")
async def get_users():  # ← Each call becomes separate coroutine
    # Each request gets its own:
    # - Coroutine object (~2KB)
    # - Local variables
    # - Execution state
    # - Resume point for await

    await session.execute(...)  # ← Independent await per request
```

## System Resource View

```
Single Thread Managing Multiple Requests:

[Python Event Loop]
    ├── Coroutine 1 (Request 1) ──[await]──► (waiting for DB)
    ├── Coroutine 2 (Request 2) ──[await]──► (waiting for DB)  
    ├── Coroutine 3 (Request 3) ──[await]──► (waiting for DB)
    └── Managing other tasks...

Total CPU usage while all 3 are "hung" on await: ~0%
Total memory overhead: ~6KB for all 3 coroutines
```

## Summary

1. **`await` = bookmark + yield control** (not blocking + minimal resources)
2. **Each FastAPI request = independent coroutine** (no interference)
3. **One thread handles thousands of "hung" awaits** (incredible efficiency)

This is why async Python can handle thousands of concurrent requests with minimal resources - each `await` is just a tiny bookmark in memory! 🎯