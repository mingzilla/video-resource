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


async def example_database1_error():
    print("=== Database1 Error Example ===")
    try:
        async with Database1() as db:
            print(f"2. Working with database1... {db}")
            raise ValueError("Simulated database error")
    except ValueError as e:
        print(f"5. Caught error: {e}")
    print("6. Context manager finished\n")


async def example_database1_error_reraise():
    print("=== Database1 Error and Reraise Example ===")
    try:
        async with Database1() as db:
            print(f"2. Working with database1... {db}")
            raise ValueError("Simulated database error")
    except ValueError as e:
        print(f"5. Caught error: {e}")
        raise  # reraise
    print("NOT RUN - Context manager finished\n")


#############


class Database2:
    async def close(self):
        print("4. Closing database2")


@asynccontextmanager
async def database2_context() -> AsyncIterator[Database2]:
    db = Database2()
    print("1. Opening database2")
    try:
        yield db
    finally:
        print("3. Before closing database2")
        await db.close()


async def example_database2_success():
    print("=== Database2 Success Example ===")
    async with database2_context() as db:
        print(f"2. Working with database2... {db}")
    print("5. Context manager finished\n")


async def example_database2_error():
    print("=== Database2 Error Example ===")
    try:
        async with database2_context() as db:
            print(f"2. Working with database2... {db}")
            raise ValueError("Simulated database error")
    except ValueError as e:
        print(f"5. Caught error: {e}")
    print("6. Context manager finished\n")


if __name__ == "__main__":
    # asyncio.run(example_database1_success())
    # asyncio.run(example_database1_error())
    #
    # try:
    #     asyncio.run(example_database1_error_reraise())
    # except Exception as e:
    #     print(f"6. Caught same error: {e}")
    #
    # asyncio.run(example_database2_success())
    asyncio.run(example_database2_error())
