from typing import AsyncIterator, AsyncGenerator
import asyncio


# AsyncIterator - just produces values
async def simple_iterator() -> AsyncIterator[int]:
    for i in range(3):
        yield i


# AsyncGenerator - can be controlled
async def controlled_generator() -> AsyncGenerator[int, str]:
    received = None
    for i in range(3):
        # Can receive values sent from outside
        received = yield i
        if received:
            print(f"Received: {received}")


async def demo1():
    async for value in simple_iterator():
        print(f"Iterator value: {value}")


async def demo2():
    async for value in controlled_generator():
        print(f"Generator value: {value}")


async def demo3():
    gen = controlled_generator()
    print(f"First: {await gen.__anext__()}")
    print(f"Second: {await gen.asend('hello')}")  # Send value back!
    await gen.aclose()  # Can close it
    # print(f"Third: {await gen.__anext__()}")


if __name__ == "__main__":
    asyncio.run(demo1())
    asyncio.run(demo2())
    asyncio.run(demo3())
