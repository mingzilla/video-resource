## Python `async`

- Python `async` Usage
- The `async` syntax Rule
- iterator vs async iterator - break down `async for`
- `async with`
- The 3-Part Pattern - return a list from iterator
- "Coroutine function" and "Coroutine object"

## Python `async` Usage

| Syntax            | Purpose                          | Usage                                  |
|-------------------|----------------------------------|----------------------------------------|
| **`async def`**   | Define async/coroutine functions | `async def my_func():`                 |
| - **`async for`** | Iterate over async iterators     | `async for item in async_generator():` |
| - **`await`**     | Wait for **coroutine** objects   | `result = await some_coroutine()`      |
| **`async with`**  | Async context managers           | `async with async_resource():`         |

## The `async` syntax Rule

| Function Pattern       | How to Consume              | What You Get       |
|------------------------|-----------------------------|--------------------|
| `async def` + `yield`  | `async for` item in func(): | Each yielded item  |
| `async def` + `return` | result = `await` func()     | The returned value |

`async def` with both `yield` and `return`

- Any yield → AsyncGenerator → use async for (HIGH priority)
- No yield → Coroutine → use await

### `async def` + `yield`

```python
# Pattern 1: yield -> use async for
async def get_users():
    yield user1
    yield user2
    yield user3
    # same as `return None`


# ✅ Correct consumption
async def my_function():
    # `for user in await get_users():` -  ❌ Wrong - You may expect to see the keyword `await`
    # but in fact - ✅ `async for` does the "await" in an iteration format
    async for user in get_users():
        process(user)


# ❌ Wrong - can't await an AsyncGenerator
result = await get_users()  # TypeError
```

### `async def` + `return`

```python
# Pattern 2: return -> use await  
async def get_user():
    return single_user


# ✅ Correct consumption
async def my_function():
    user = await get_user()


# ❌ Wrong - can't iterate a Coroutine
async for u in get_user():  # TypeError
```

----

## iterator vs async iterator - break down `async for`

- `regular iterator - 1` is the same as `regular iterator - 2`
- `async iterator - 1` is the same as `async iterator - 2`
- Note: `async for` is not applying the `async def` pattern to `for`

```python
# regular iterator - 1
def print_items():
    for item in [1, 2, 3]:
        print(item)


# regular iterator - 2
def print_items():
    iterator = iter([1, 2, 3])
    while True:
        try:
            item = next(iterator)  # ← This throws StopIteration when done
            print(item)
        except StopIteration:
            break


# async iterator - 1
async def process_stream():
    async for chunk in openai_stream:  # means: `async def` + `yield`
        print(chunk)
        yield chunk


# async iterator - 2
async def process_stream():
    iterator = openai_stream.__aiter__()
    while True:
        try:
            chunk = await iterator.__anext__()
            print(chunk)
            yield chunk
        except StopAsyncIteration:
            break
```

### What if we want to get `1`

```python
async def get_users():
    yield user1
    yield user2
    yield user3
    return 1  # This is the "return value"


# Any yield → AsyncGenerator → use async for (HIGH priority)
# No yield → Coroutine → use await
result = await get_users()  # ❌ Wrong - TypeError - get_users() has `yield`


# Method 1: Not possible
async def get_return_value():
    async for user in get_users():  # The return value is lost in async for!
        print(user)


# Method 2: Using the generator protocol directly
async def get_return_value():
    gen = get_users()
    # iter = get_users().__aiter__() - also correct, use iterator protocol
    try:
        while True:
            user = await gen.__anext__()
            # user = await iter.__anext__()
            print(user)
    except StopAsyncIteration as e:
        return_value = e.value  # The return value is here!
        print(f"Return value: {return_value}")  # 1
```

## async with

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:  # 3 ✅
    # db_local_session = async_sessionmaker(...)
    async with Database.db_local_session() as session:  # 1 ✅
        try:
            yield session  # 4a ✅ `yield` relates to `async def`, the caller needs to use `async for`
            await session.commit()  # 2 ✅
        except Exception:
            await session.rollback()
            raise


# ✅ Correct usage - async context manager
@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    async for session in Database.get_session():  # 4b ✅
        yield session
```

### The sequence:

1. ✅ `async with` needed because `Database.db_local_session()` **returns** an async context manager
2. ✅ `await` needed because `session.commit()` is an async function
1. ✅ `async def` needed because we use `async with` keyword inside
3. ✅ `async def` needed because we use `await` keyword inside
4. ✅ `async def` + `yield` (4a) needs `async for` (4b)

### Async Context Manager - means it has `__aenter__` and `__aexit__`

```python
# Database.session() returns an object that has:
class AsyncSession:
    async def __aenter__(self): ...  # ← async context manager

    async def __aexit__(self): ...  # ← async context manager
```

### `await` has nothing to do with `async with`

| Keyword      | Why Needed                                                  |
|--------------|-------------------------------------------------------------|
| `await`      | `session.commit()` is async                                 |
| `async with` | `Database.db_local_session()` returns async context manager |

## The 3-Part Pattern - return a list from iterator

| Part                         | Sync Version               | Async Version                          |
|------------------------------|----------------------------|----------------------------------------|
| **1. Generator execution**   | `generator()`              | `async_generator()`                    |
| **2. Collection conversion** | `for item in generator():` | `async for item in async_generator():` |
| **3. Variable assignment**   | `result = collect_func()`  | `result = await collect_func()`        |

### SYNC VERSION

```python
def sync_generator() -> Generator[int, None, None]:
    yield 1
    yield 2


def collect_sync() -> list[int]:
    items = []
    for item in sync_generator():  # Part 2: regular for
        items.append(item)
    return items


result = collect_sync()  # Part 3: direct assignment
```

### ASYNC VERSION

```python
async def async_generator() -> AsyncGenerator[int, None]:
    yield 1
    yield 2


async def collect_async() -> list[int]:
    items = []
    async for item in async_generator():  # Part 2: `async for`, not `await`
        items.append(item)
    return items


result = await collect_async()  # Part 3: await assignment
```

### The Pattern Summary

```
Part 1: Generator Creation
    ↓
Part 2: Collection (iterate + convert to list/etc)
    ↓  
Part 3: Assignment (get final result)
```

---

## "Coroutine function" and "Coroutine object"

| Function Contains           | Function Type            | Returns When Called   | Define                   | Use                                |
|-----------------------------|--------------------------|-----------------------|--------------------------|------------------------------------|
| `return` (with `async def`) | Coroutine function       | Coroutine object      | `async def get_users():` | `await` get_user()                 |
| `yield` (with `async def`)  | Async generator function | AsyncGenerator object | `stream_users()`         | `async for` user in stream_users() |

```python
# Pattern 1: Async Function - use await
async def get_user() -> User:  # User is NOT a `coroutine object`, this specifies the type you get when calling `await get_user()`
    response = await api_call()
    return User(response.data)  # ← return = use await -- function returns a Coroutine OBJECT


user = await get_user()


# Pattern 2: Async Generator - use async for  
async def stream_users() -> AsyncGenerator[User, None]:
    async for data in api_stream():
        yield User(data)  # ← yield = use async for


async for user in stream_users():
    process(user)
```
