# Python Asyncio Error Handling

## 1. Three Fundamental Error Types in Asyncio

| Error Type           | When It Happens                 |
|----------------------|---------------------------------|
| **`CancelledError`** | `task.cancel()`, timeouts       |
| **`TimeoutError`**   | `wait_for()`, `asyncio.timeout` |
| **Business Errors**  | API failures, DB errors, etc.   |

## 2. What `Clean Up a Task` means

- Clean up Myth:
    - Myth: "When an error occurs, you need to clean up tasks."
    - Reality: There is no such a method called `cleanup` associated to tasks
- Clean up involves 2 things:
    - Task - Cancel a task, then the `task` object is memory recycled
    - Resource - Clean up resource - e.g. db connection

### Cancel a task

```text
# Cancelling a task manually
task = asyncio.create_task(fetch_user())
task.cancel()  # ← This is the ONLY way to cancel
```

### Clean up resource

- `Cancelling a task` has nothing to do with `clean up resource`
- Regardless if you use `TaskGroup`, you need to `clean up resource`

## 3. Task Cancellation - When Error Occurs

### Common Methods & Their Cleanup Rules

| Method (error occurs)      | Explicitly call `task.cancel()`?   | Needs Resource Cleanup? | Best Practice                                                  |
|----------------------------|------------------------------------|-------------------------|----------------------------------------------------------------|
| **`task = create_task()`** | ❌ No (unless orphaned) [1]         | ✅ Yes (per-task)        | Track tasks in a set or `await` them to prevent leaks          |
| **`wait_for()`**           | ❌ No (auto-cancels on timeout) [2] | ✅ Yes (if interrupted)  | Use `try/finally` inside the coroutine being waited on         |
| **`TaskGroup`**            | ❌ No (auto-handled)                | ✅ Yes (per-task)        | Handle resources in `except*` or `finally` inside each task    |
| **`gather()`**             | ❌ No (if `return_exceptions=True`) | ✅ Yes (per-task)        | Always use `return_exceptions=True` + check results for errors |
| **`asyncio.run()`**        | N/A                                | ✅ Yes (global)          | Wrap in `try/finally` for global resources (DB pools, etc.)    |
| **`sleep()`**              | N/A                                | N/A                     | Safe to ignore (no resources)                                  |

### Manual Task Cancelling When Error Occurs - Details for [1] create_task() and [2] wait_for()

When an error occurs, do you need to **explicitly call `task.cancel()`** in the `except` block?

| Error Type           | [1] `create_task()`                  | [2] `wait_for()`                          |
|----------------------|--------------------------------------|-------------------------------------------|
| **`CancelledError`** | ❌ No (task already cancelled)        | ❌ No (task already cancelled)             |
| **`TimeoutError`**   | ❌ No (not applicable to create_task) | ❌ No (task already cancelled by wait_for) |
| **Business Errors**  | ❌ No (task completed normally)       | ❌ No (task completed normally)            |

### WHAT?! So when do you manually cancel a task?

```python
# The Only Time You Call task.cancel(): Manually aborting a background task
task = asyncio.create_task(long_running_job())

try:
    await asyncio.wait_for(task, timeout=10)
except asyncio.TimeoutError:
    task.cancel()  # Now this makes more sense in context
    await task  # Important to await after cancellation
    raise
```

## 4. Resource Cleanup - Patterns

| Pattern             | When to Use                             | Example                                          |
|---------------------|-----------------------------------------|--------------------------------------------------|
| **Context Manager** | ✅ **Preferred** - Automatic cleanup     | `async with pool.acquire() as conn:`             |
| **`finally` block** | When context manager not available      | `try: ... finally: await conn.close()`           |
| **`except` block**  | Conditional cleanup based on error type | `except SpecificError: await cleanup_on_error()` |

### Key Points

**Context Manager (Best Practice):**

```python
async with database.get_connection() as conn:
    # Resource automatically cleaned up even if cancelled/timeout
    result = await conn.execute(query)
```

**finally Block (Fallback):**

```python
conn = None
try:
    conn = await database.get_connection()
    result = await conn.execute(query)
finally:
    if conn:
        await conn.close()  # Always runs
```

**except Block (Conditional):**

```python
try:
    result = await risky_operation()
except SpecificError:
    await cleanup_partial_state()  # Only on certain errors
    raise
```

The resource cleanup

- has **nothing to do with asyncio task cancellation**
- it's standard Python resource management that happens to work the same way in async code.
- Whether you use `TaskGroup`, `gather()`, or plain `create_task()`, you still need these same cleanup patterns.

## 5. Benefits of TaskGroup Resource Management

- Task Cancelling:
    - Python cancels tasks automatically, so regardless if you use `TaskGroup`, you don't manually do `task.cancel()` when error occurs
    - You do `task.cancel()` because you want to do it, not because there is an error
- Resource Cleanup:
    - You have to do resource clean up (e.g. close db connection) regardless if you use TaskGroup

So in reality, what `TaskGroup` offers is: if error occurs, auto cancel unfinished tasks. NOT clean up. TaskGroup does not do clean up.

## 6. Usage Comparison - TaskGroup, gather, as_completed

|                              | Use Case (parallel requests)                         | Notes                                                                          |
|------------------------------|------------------------------------------------------|--------------------------------------------------------------------------------|
| **`asyncio.TaskGroup`**      | When errors - Auto cancel unfinished tasks           | Cancel unfinished tasks                                                        |
| **`asyncio.gather()`**       | When errors - ignore broken tasks                    | Always use `return_exceptions=True` [1]. All tasks finished, nothing to cancel |
| **`asyncio.as_completed()`** | Process results as they complete (streaming pattern) | Warning - Program crashes on unhandled exceptions                              |

### Real-World Examples

**✅ Use gather() for:**

- [1] IMPORTANT: gather needs to use "return_exceptions=True", otherwise it's a broken feature because it does not stop unfinished tasks and ignores them.
- Checking 100 flight prices (some airlines might be down)
- Web scraping multiple pages (some might 404)
- Sending notifications to multiple services (some might fail)

**✅ Use TaskGroup for:**

- If your cooker is broken, might as well cancel your order of a raw chicken.

## 7. `asyncio.to_thread()` Error Handling

```python
async def handle_sync_operation():
    try:
        # Can timeout if used with wait_for()
        result = await asyncio.wait_for(
            asyncio.to_thread(slow_blocking_function, arg1, arg2),
            timeout=30.0
        )
        return result
    except RegularBusinessError as e:
        # Handle sync function errors normally
        logging.exception(f"Sync operation failed: {e}")
        raise
    except asyncio.CancelledError:
        # Task was cancelled, but thread may still be running
        logging.warning("Task cancelled - sync operation may continue in background")
        raise
    except TimeoutError:
        # Timeout expired, but thread is still running!
        logging.warning("Sync operation timed out - still running in background")
        raise
```

### Critical `to_thread()` Behavior

**Key Implication:** You cannot interrupt blocking I/O operations mid-execution

| Scenario                 | Thread Behavior                                              | Asyncio Task Behavior |
|--------------------------|--------------------------------------------------------------|-----------------------|
| **Async Task cancelled** | Sync fn continues running - **can't cancel** sync operations | Raises CancelledError |
| **Timeout occurs**       | Sync fn continues running - in the background                | Raises TimeoutError   |
| **Process exits**        | Terminated by OS                                             | N/A                   |
