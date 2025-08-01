import asyncio
import time


async def worker_task(name: str, delay: float, start_time: float) -> str:
    await asyncio.sleep(delay)
    elapsed = time.time() - start_time
    print(f"Task {name} itself completed after {elapsed:.2f}s")
    return f"Task {name} completed"


async def run_with_task_group():
    print("run_with_task_group")
    start_time = time.time()

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(worker_task("A", 1, start_time))
        task2 = tg.create_task(worker_task("B", 2, start_time))
        task3 = tg.create_task(worker_task("C", 0.5, start_time))

    total_elapsed = time.time() - start_time
    print(f"All tasks completed after {total_elapsed:.2f}s")

    print(f"Results: {task1.result()}, {task2.result()}, {task3.result()}")


async def run_with_gather():
    print("run_with_gather")

    start_time = time.time()

    results = await asyncio.gather(
        worker_task("A", 1, start_time),
        worker_task("B", 2, start_time),
        worker_task("C", 0.5, start_time),
    )

    total_elapsed = time.time() - start_time
    print(f"All tasks completed after {total_elapsed:.2f}s")

    print(f"Results: {results[0]}, {results[1]}, {results[2]}")


########################

async def worker_task_hates_b(name: str, delay: float, start_time: float) -> str:
    if name == "B":
        raise ValueError(f"Task {name} failed")

    await asyncio.sleep(delay)
    elapsed = time.time() - start_time
    print(f"Task {name} itself completed after {elapsed:.2f}s")
    return f"Task {name} completed"


async def run_with_task_group_hates_b():
    print("run_with_task_group_hates_b")

    start_time = time.time()

    task1 = task2 = task3 = None  # IMPORTANT: initialize first, otherwise may not exist when showing results

    try:
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(worker_task_hates_b("A", 1, start_time))
            task2 = tg.create_task(worker_task_hates_b("B", 2, start_time))
            task3 = tg.create_task(worker_task_hates_b("C", 0.5, start_time))
    except* ValueError as eg:
        print(f"Caught {len(eg.exceptions)} ValueError(s)")

    total_elapsed = time.time() - start_time
    print(f"All tasks completed after {total_elapsed:.2f}s")

    # Check task results safely
    results = []
    for task in [task1, task2, task3]:
        if task and task.done():
            try:
                results.append(task.result())
            except asyncio.CancelledError:
                results.append("Cancelled")
            except Exception as e:
                results.append(f"Failed: {e}")
        else:
            results.append("Not completed")

    print(f"Results: {results[0]}, {results[1]}, {results[2]}")


########################

async def worker_task_hates_a(name: str, delay: float, start_time: float) -> str:
    await asyncio.sleep(delay)

    if name == "A":
        raise ValueError(f"Task {name} failed")
    elapsed = time.time() - start_time
    print(f"Task {name} itself completed after {elapsed:.2f}s")
    return f"Task {name} completed"


async def run_with_task_group_hates_a():
    print("run_with_task_group_hates_a - done: remain done; not done: cancelled")

    start_time = time.time()

    task1 = task2 = task3 = None  # IMPORTANT: initialize first, otherwise may not exist when showing results

    try:
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(worker_task_hates_a("A", 1, start_time))
            task2 = tg.create_task(worker_task_hates_a("B", 2, start_time))
            task3 = tg.create_task(worker_task_hates_a("C", 0.5, start_time))
    except* ValueError as eg:
        print(f"Caught {len(eg.exceptions)} ValueError(s)")

    total_elapsed = time.time() - start_time
    print(f"All tasks completed after {total_elapsed:.2f}s")

    # Check task results safely
    results = []
    for task in [task1, task2, task3]:
        if task and task.done():
            try:
                results.append(task.result())
            except asyncio.CancelledError:
                results.append("Cancelled")
            except Exception as e:
                results.append(f"Failed: {e}")
        else:
            results.append("Not completed")

    print(f"Results: {results[0]}, {results[1]}, {results[2]}")


async def run_with_gather_hates_a():
    print("run_with_gather_hates_a - tasks continue running in background")

    start_time = time.time()
    gathered_results = None

    try:
        gathered_results = await asyncio.gather(
            worker_task_hates_a("A", 1, start_time),
            worker_task_hates_a("B", 2, start_time),
            worker_task_hates_a("C", 0.5, start_time)
        )
    except ValueError as e:
        print(f"Caught ValueError: {e}")
        print("Note: Other tasks continue running in background!")

    # Give time to see Task B complete in background
    await asyncio.sleep(2)

    total_elapsed = time.time() - start_time
    print(f"All tasks completed after {total_elapsed:.2f}s")

    results = []
    if gathered_results:  # gather() limitation - since one of them failed, you cannot have a variable to store the value returned by C
        # gather() succeeded - we have all results
        for result in gathered_results:
            results.append(result)
    else:
        # gather() failed - we lose all partial results
        results = ["Lost due to exception", "Lost due to exception", "Lost due to exception"]

    print(f"Results: {results[0]}, {results[1]}, {results[2]}")


if __name__ == "__main__":
    # 1 same result
    asyncio.run(run_with_task_group())
    print("\n\n")
    asyncio.run(run_with_gather())

    # 2 cancelled vs not cancelled
    asyncio.run(run_with_task_group())
    print("\n\n")
    asyncio.run(run_with_task_group_hates_b())

    # 3 early error vs real demo
    asyncio.run(run_with_task_group_hates_b())
    print("\n\n")
    asyncio.run(run_with_task_group_hates_a())

    # 4 get each item
    asyncio.run(run_with_task_group_hates_a())
    print("\n\n")
    asyncio.run(run_with_gather_hates_a())
