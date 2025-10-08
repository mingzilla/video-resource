## Python Event Loops and Execution Model (asyncio)

1. Standard way to run async app
2. Code Break down
3. Difference: `await main()` vs `asyncio.run(main())`
4. Python Thread Execution Model

## 1. What does the code below mean?

```python
# The `standard way` to structure Python `async applications`, especially for CLI tools, servers, and production scripts.

import asyncio
import sys


async def main() -> int:
    print("Hello, async world!")
    await asyncio.sleep(1)
    print("Done!")
    return 0  # Success - return 0 / None; Failed - return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

## 2. Code Break down

### `if __name__ == "__main__":`

Prevents the code from running when the module is imported by another script

### `sys.exit(asyncio.run(main()))`

```python
coroutine_obj = main()  # Creates coroutine object (not executed yet)
result = asyncio.run(coroutine_obj)  # Runs the coroutine and gets return value
sys.exit(result)  # Exits with that return value
```

| Code                | What Happens                          | State                                |
|---------------------|---------------------------------------|--------------------------------------|
| `async def main():` | **Defines** async function            | Function exists                      |
| `main`              | **Creates** function object           | Not executed                         |
| `main()`            | **Creates** coroutine object          | Coroutine created but not running    |
| `asyncio.run(..)`   | **Executes** coroutine via event loop | Same as await but creates event loop |
| `sys.exit(..)`      | **Exits** program                     | 0/None: Success; 1: Failure          |

## 3. Difference: `await main()` vs `asyncio.run(main())`

```python
if __name__ == "__main__":
    # ❌ This would fail:
    # result = await main()  # SyntaxError

    # ✅ This works:
    result = asyncio.run(main())  # Creates event loop + runs coroutine
    sys.exit(result)
```

- Use `await main()` inside an `async def my_function()`
- Use `asyncio.run(main())` at `root level code`

## 4. Python Thread Execution Model

```
[1 CPU Core] ← GIL (Global Interpreter Lock) constraint
    │
[1 Main Thread] ───────── [0/1 Event Loop] ──── [0+ Async Coroutines]
    │
    ├── [Sub-Thread 1] ──── [1 Event Loop] ──── [0+ Async Coroutines]
    │
    ├── [Sub-Thread 2] ──── [0 Event Loop] ──── [Sync Functions only]
    │
    └── [Sub-Thread 3] ──── [1 Event Loop] ──── [0+ Async Coroutines]

0/1 Event Loop:
- 0 - sync functions: Run directly in a thread (no event loop object used)
- 1 - async functions: managed by a python event loop `object` (1 event loop object created/used)
```

| Component            | Relationship                     | Details                  |
|----------------------|----------------------------------|--------------------------|
| **CPU Core**         | `1 only`                         | GIL limitation           |
| **Threads**          | `1 main + N sub-threads`         | Can create multiple      |
| **Event Loops**      | `0 or 1 per thread`              | Optional for each thread |
| **Sync Functions**   | `Managed by OS thread scheduler` | No event loop needed     |
| **Async Coroutines** | `Managed by event loop only`     | Require event loop       |

### Common Misconceptions

| Common Misconceptions                         | Reality         | Why                                                     |
|-----------------------------------------------|-----------------|---------------------------------------------------------|
| **"1 event loop - (1 to 1) - sync function"** | ❌ **Incorrect** | Event loops don't manage sync functions                 |
| **"sub-threads - (1 to 1) - event loop"**     | ⚠️ **Optional** | Sub-threads *can* have event loops, but don't need them |
