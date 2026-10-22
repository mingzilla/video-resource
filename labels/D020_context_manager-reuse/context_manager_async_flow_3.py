import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator


class Database1:
    async def __aenter__(self):
        print("1. Opening database1")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"3. Database1 __exit__ called with exception: {exc_type}")
        await self.close()

    async def close(self):
        print("4. Closing database1")


async def example_database1_success():
    print("=== Database1 Success Example ===")
    async with Database1() as db:
        print(f"2. Working with database1... {db}")
    print("Context manager finished\n")


@asynccontextmanager
async def database1_shared() -> AsyncIterator[Database1]:
    print("=== Database1 Success Example ===")
    async with Database1() as db:
        print(f"2.1 Very duplicated logic")
        try:
            yield db  # Bookmark 1.1
            print(f"2.3 Finished using database")
        except Exception as e:
            print(f"2.4 Caught error: {e}")  # Bookmark 1.2
    print("Context manager finished\n")


async def example_database1_shared():
    async with database1_shared() as db:
        print(f"2.2 Working with database1... {db}")


async def example_database1_shared_error():
    async with database1_shared() as db:
        print(f"2.2 Working with database1... {db}")
        raise ValueError("2.2 Error Occurred")


#############


class Database2:
    async def close(self):
        print("4. Closing database2")


@asynccontextmanager
async def database2_context() -> AsyncIterator[Database2]:
    db = Database2()
    print("1. Opening database2")
    try:
        yield db  # Bookmark 2.2
    except Exception as e:
        print(f"??. Caught error 1: {e}")  # Bookmark 2.3
    finally:
        print("3. Before closing database2")
        await db.close()


async def example_database2_success():
    print("=== Database2 Success Example ===")
    async with database2_context() as db:
        print(f"2. Working with database2... {db}")
    print("5. Context manager finished\n")


@asynccontextmanager
async def database2_shared() -> AsyncIterator[Database2]:
    try:
        async with database2_context() as db:
            print(f"2.1. Working with database2... {db}")
            yield db  # Bookmark 2.1
            print(f"2.3. Working with database2... {db}")
    except Exception as e:
        print(f"??. Caught error 2: {e}")
    print("5. Context manager finished\n")


async def example_database2_shared():
    async for db in database2_shared():
        print(f"2.2 Working with database2... {db}")


async def example_database2_shared_error():
    async with database2_shared() as db:  # --------- context_manager_async_flow_2.py uses `async for` here
        print(f"2.2 Working with database2... {db}")
        raise ValueError("2.2 Error Occurred")  # -- `async with` makes sure it resumes at Bookmark 2.1, so it continues at Bookmark 2.2,


if __name__ == "__main__":
    asyncio.run(example_database1_success())
    asyncio.run(example_database1_shared())
    asyncio.run(example_database1_shared_error())  # does not need to catch exception because Bookmark 1.2 does not throw it again

    asyncio.run(example_database2_success())
    asyncio.run(example_database2_shared())
    asyncio.run(example_database2_shared_error())  # does not need to catch exception because Bookmark 2.3 does not throw it again
