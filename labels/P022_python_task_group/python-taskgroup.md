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

| Aspect                                 | `asyncio.gather()` with `return_exceptions=True`          | `asyncio.TaskGroup`                                                               |
|----------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|
| **Behaviour**                          | Wait for all, finish all, ignore failures                 | Wait for all. If error occurs, cancel unfinished tasks                            |
| **Result Access**                      | Access success or failure results from the returned array | Granular result access - preserve successful results even after group failure     |
| **Resource Management for task group** | None, all tasks are finished                              | Automatic resource management - context manager (`async with`) guarantees cleanup |
| **Resource Management for each task**  | You must manually handle cleanup for each task            | You must manually handle cleanup for each task                                    |

Resource Management for each task e.g. 

```text
# TaskGroup doesn't magically clean up YOUR resources
async def task_with_resources():
    connection = await db.connect()  # You still need try/finally!
    try:
        return await do_work(connection)
    finally:
        await connection.close()  # TaskGroup won't do this for you

async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(task_with_resources())  # Task must handle its own cleanup
    task2 = tg.create_task(another_task())
# TaskGroup manages the group, not the individual task resources
```
