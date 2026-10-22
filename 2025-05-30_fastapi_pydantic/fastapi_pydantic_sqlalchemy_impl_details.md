# FastAPI + Pydantic + SQLAlchemy Guide

## Summary
### Naming Conventions

- Use `entity` for SQLAlchemy database objects
- Use `model` for Pydantic request/response objects
- Use `entity_class` instead of `model_class` for SQLAlchemy classes

### SQLAlchemy 2.0+

- `flush()` is sufficient for getting auto-generated IDs
- `refresh()` is good practice for consistency and complex scenarios

### FastAPI Endpoints

- One Pydantic model per endpoint for request body
- Path parameters come from URL, query parameters from query string
- Use `Depends()` for dependency injection (DB sessions, auth, etc.)

### Generator Type Hints

- Always specify all three types: `Generator[YieldType, SendType, ReturnType]`
- Use `None` for unused SendType/ReturnType in simple cases

---

## Core Concepts & Terminology

### Model vs Entity Naming Convention

| Term         | Purpose                        | Key Method               | Database Mapping     | Usage                 |
|--------------|--------------------------------|--------------------------|----------------------|-----------------------|
| **`model`**  | Data transfer/validation       | `.model_dump()`          | ❌ No direct mapping  | Request/response DTOs |
| **`entity`** | Database record representation | N/A (SQLAlchemy handles) | ✅ Direct 1:1 mapping | Database operations   |

## SQLAlchemy 2.0+ Session Operations

### flush() vs refresh() Behavior

| Version             | After `flush()`           | After `refresh()`       | Reason                   |
|---------------------|---------------------------|-------------------------|--------------------------|
| **SQLAlchemy 1.x**  | ID might not be available | ID definitely available | Older lazy-loading       |
| **SQLAlchemy 2.0+** | **ID is available**       | ID remains available    | Improved auto-population |

### What happens with flush() in SQLAlchemy 2.0+:

1. **Sends INSERT to database**
2. **Immediately retrieves auto-generated values** (`id`, `created_at`, `updated_at`)
3. **Populates them back into the object instance**

### When refresh() is still useful:

- **Computed columns** or **database triggers**
- **Complex server-side transformations**
- **Ensuring 100% consistency** with database state
- **Backwards compatibility** with older SQLAlchemy versions

```python
@staticmethod
def create(session: Session, entity: T) -> T:
    session.add(entity)
    session.flush()  # ID available here in SQLAlchemy 2.0+
    session.refresh(entity)  # Optional for basic fields, good for consistency
    return entity
```

## FastAPI Parameter Resolution

### Request Body Mapping

FastAPI automatically maps Pydantic models to request bodies:

```python
# POST endpoint - Pydantic model becomes request body
@router.post("/")
def create_api_config(api_config_create: ApiConfigCreate, db: Session = Depends(Database.get_session)):
    # api_config_create contains the JSON request body
    pass


# PUT endpoint - Path parameter + Pydantic model
@router.put("/{api_config_id}")
def update_api_config(api_config_id: int, api_config_update: ApiConfigUpdate, db: Session = Depends(Database.get_session)):
    # api_config_id from URL path: /api_configs/123
    # api_config_update from JSON request body
    pass
```

### Key Rules:

| Parameter Type       | Source                         | Notes                                |
|----------------------|--------------------------------|--------------------------------------|
| **Pydantic Model**   | Request body                   | Only ONE Pydantic model per endpoint |
| **Path Parameters**  | URL path (`{id}`)              | Defined in route decorator           |
| **Query Parameters** | URL query string (`?limit=10`) | Simple types (int, str, bool)        |
| **Dependencies**     | `Depends()`                    | Database sessions, auth, etc.        |

**Important:** Having multiple Pydantic models as parameters won't work - FastAPI can't determine which should be the request body.

## Generator Type Annotations Explained

### Why Generator[Session, None, None]?

```python
def get_session() -> Generator[Session, None, None]:
    session = Database.db_local_session()
    try:
        yield session  # Yields Session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

#### FastAPI - Depends

```python
# What FastAPI does internally (simplified):
def process_request():
    # 1. Call your generator
    session_generator = get_session()
    
    # 2. Get the session
    session = next(session_generator)  # Calls code before yield
    
    # 3. Pass session to your endpoint
    result = your_endpoint_function(session)
    
    # 4. Continue generator (cleanup code)
    try:
        next(session_generator)  # Calls code after yield
    except StopIteration:
        pass  # Generator finished normally
```

### Generator[YieldType, SendType, ReturnType]

| Position            | Type      | Purpose                          | Example         |
|---------------------|-----------|----------------------------------|-----------------|
| **1st: YieldType**  | `Session` | What the generator yields        | `yield session` |
| **2nd: SendType**   | `None`    | What can be sent to generator    | Not used here   |
| **3rd: ReturnType** | `None`    | What generator returns when done | Implicit `None` |

### Interactive Generator Example

```python
def interactive_generator() -> Generator[str, int, None]:
    count = 0
    while True:
        received = yield f"Count is {count}"  # Yield str, receive int
        #    ↑              ↑
        #    |              |
        # What we receive   What we yield (send out)

        if received:  # Someone sent us an integer
            count += received

# Usage:
gen = interactive_generator()
print(next(gen))        # "Count is 0"
print(gen.send(5))      # Send 5, get "Count is 5"  
print(gen.send(3))      # Send 3, get "Count is 8"
```

### How yield Works (Two-Way Communication)

```python
received = yield f"Count is {count}"
#    ↑              ↑
#    |              |
# What we GET     What we SEND
# from .send()    to caller
```

### Visual Flow Diagram

```
Generator State                    Caller Action
---------------                    -------------

count = 0
received = yield "Count is 0"      ← next(gen) returns "Count is 0"
    ↑ PAUSED HERE
    
received = 5                       ← gen.send(5) 
count += 5  (count = 5)
received = yield "Count is 5"      ← gen.send(5) returns "Count is 5"
    ↑ PAUSED HERE
    
received = 3                       ← gen.send(3)
count += 3  (count = 8)
received = yield "Count is 8"      ← gen.send(3) returns "Count is 8"
    ↑ PAUSED HERE
```