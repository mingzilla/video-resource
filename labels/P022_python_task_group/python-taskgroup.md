# Python TaskGroup

## What is TaskGroup?

TaskGroup is a new feature introduced in Python 3.11 that provides a more modern alternative to gather() for managing concurrent tasks.

## Basic Usage Pattern

```python
import asyncio


async def worker_task(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"Task {name} completed"


async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(worker_task("A", 1))
        task2 = tg.create_task(worker_task("B", 2))
        task3 = tg.create_task(worker_task("C", 0.5))

    # All tasks are automatically awaited when exiting context
    print(f"Results: {task1.result()}, {task2.result()}, {task3.result()}")


asyncio.run(main())
```

## Error Handling Behavior

### Success Case

```text
[Task A] -----> [Complete]
[Task B] ---------> [Complete]  
[Task C] ---> [Complete]
          |
          v
    [All Results Available]
```

### Failure Case

```text
[Task A] -----> [Complete]
[Task B] ----X [Exception] 
[Task C] --X [Cancelled]
          |
          v
    [ExceptionGroup Raised]
```

## `gather()` compared to `TaskGroup`:

| Aspect                     | `asyncio.gather()`                                                  | `asyncio.TaskGroup`                                                               |
|----------------------------|---------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **Automatic Cancellation** | No - other tasks continue running in background when one fails      | Yes - cancels remaining tasks when one fails                                      |
| **Result Access**          | All-or-nothing results - you lose ALL results when any task fails   | Granular result access - preserve successful results even after group failure     |
| **Resource Management**    | No automatic resource management - you must manually handle cleanup | Automatic resource management - context manager (`async with`) guarantees cleanup |