# Python Asyncio (3.11+): Main Usage Guide

## Core Asyncio Methods

| Method                      | Purpose                                            | Use Case                                                | Code Example                                           |
|-----------------------------|----------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| **`asyncio.sleep()`**       | Non-blocking pause/delay                           | Yield control to other tasks during delays              | `await asyncio.sleep(1)`                               |
| **`asyncio.run()`**         | Entry point for async programs                     | Start the event loop and run main coroutine             | `asyncio.run(main())`                                  |
| **`asyncio.create_task()`** | Schedule coroutines for concurrent execution       | **Start tasks immediately** for **parallel** execution  | `task = asyncio.create_task(fetch_data())`             |
| **`asyncio.gather()`**      | Run multiple coroutines concurrently, wait for all | **Execute parallel tasks** and collect results in order | `results = await asyncio.gather(task1(), task2())`     |
| **`asyncio.wait_for()`**    | Add timeout to any awaitable                       | Prevent tasks from running indefinitely                 | `result = await asyncio.wait_for(task(), timeout=5.0)` |

## Coroutine

```python
# fetch_data() is an async function

# 1. Coroutine Object Creation (Not Executed)
coro = fetch_data(1)  # Not executed
print(type(coro))  # <class 'coroutine'>

# 2. Sequential Execution
coro = fetch_data(1)
await coro  # ✅ EXECUTES HERE

# 3. Allows Parallel Execution
task = asyncio.create_task(fetch_data(1))  # ✅ EXECUTES HERE
await task  # Waits for already-running task
```

## Core Usage Example

```python
async def fetch_data(id: int):
    await asyncio.sleep(2)
    return f"Data {id}"


async def run_parallel_using_create_task():
    task1 = asyncio.create_task(fetch_data(1))  # Starts immediately
    task2 = asyncio.create_task(fetch_data(2))  # Starts immediately

    result1 = await task1
    result2 = await task2
    print(f"Results: {result1}, {result2}")


async def run_parallel_using_gather():
    # Run multiple coroutines concurrently
    tasks = asyncio.gather(
        fetch_data(1),
        fetch_data(2),
    )
    results = await tasks
    print(f"All results: {results}")


async def run_parallel_using_create_task_with_timeout():
    task1 = asyncio.create_task(fetch_data(1))  # Starts immediately
    task2 = asyncio.create_task(fetch_data(2))  # Starts immediately

    try:
        result1 = await asyncio.wait_for(task1, timeout=1.0)
        result2 = await asyncio.wait_for(task2, timeout=1.0)
        print(f"Results: {result1}, {result2}")
    except asyncio.TimeoutError:
        print("At least one task timed out!")
        # Note: wait_for() cancelled timed out tasks automatically


async def run_parallel_using_gather_with_timeout():
    tasks = asyncio.gather(
        fetch_data(1),
        fetch_data(2),
    )
    try:
        results = await asyncio.wait_for(tasks, timeout=2.0)
        print(f"All results: {results}")
    except asyncio.TimeoutError:
        print("Entire operation timed out!")
        # Note: wait_for() cancelled timed out tasks automatically


asyncio.run(run_parallel_using_create_task())
asyncio.run(run_parallel_using_gather())
asyncio.run(run_parallel_using_create_task_with_timeout())
asyncio.run(run_parallel_using_gather_with_timeout())
```

### Output

```text
# Example 1 & 2: Success (no timeout)
Results: Data 1, Data 2
All results: ['Data 1', 'Data 2']

# Example 3: Individual timeouts
At least one task timed out!

# Example 4: Total timeout  
Entire operation timed out!
```

### Analysis of Your Examples

| Example                | Pattern                                       | Execution Time       | Key Insight                               |
|------------------------|-----------------------------------------------|----------------------|-------------------------------------------|
| **1. `create_task()`** | Manual task creation + sequential awaiting    | ~2 seconds           | Tasks start immediately, run concurrently |
| **2. `gather()`**      | Automatic task creation + concurrent awaiting | ~2 seconds           | Simpler syntax, same performance          |
| **3. Single timeout**  | One task with timeout                         | ~1 second (timeout)  | Will timeout since task takes 2s          |
| **4. Gather timeout**  | Multiple tasks with timeout                   | ~2 seconds (timeout) | Will timeout since tasks take 2s each     |

## Threading Methods

| Method                          | Purpose                                  | Why It's Anti-Pattern                                              |
|---------------------------------|------------------------------------------|--------------------------------------------------------------------|
| **`asyncio.to_thread()`**       | Run blocking code in thread pool         | **Defeats event loop efficiency** - use async libraries instead    |
| **`asyncio.run_in_executor()`** | Run blocking code in thread/process pool | **Breaks async paradigm** - indicates missing async implementation |

Notes:

- **Anti-Pattern**: * `to_thread()` or `run_in_executor()` should be avoided in async ASGI server, where you can use async generators and coroutines.
- **Key Principle**: Well-designed (full ASGI support) async applications should rarely need threading methods - they indicate missing async-native implementations.