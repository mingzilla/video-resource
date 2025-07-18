# Service Structure Options Comparison

This document compares different approaches to service instantiation in Python web applications, with specific focus on FastAPI implementations.

## Option 1: Flat Global Variables

**Pattern**: Module-level global variables with runtime checks

### Code Example

```python
# Global variables at module level
llm_client = LLMClient()
mcp_client = MCPClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runtime checks for cleanup
    if "mcp_client" in globals():
        await mcp_client.disconnect()
    if "llm_client" in globals():
        await llm_client.disconnect()


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Direct global access
    response = await llm_client.invoke(request.message)
    return response
```

### Pros and Cons

| **Pros**                     | **Cons**                                     |
|------------------------------|----------------------------------------------|
| [+] Simple and direct        | [-] Hard to test (global state)              |
| [+] No configuration needed  | [-] Import order dependencies                |
| [+] Fast access              | [-] Difficult to mock                        |
| [+] Obvious resource sharing | [-] Unsafe string-based checks (`globals()`) |
|                              | [-] Namespace pollution                      |
|                              | [-] No lifecycle management                  |

---

## Option 2: FastAPI Depends with New Instances

**Pattern**: Dependency injection creating new instances per request

### Code Example

```python
def get_llm_client():
    return LLMClient()


def get_chat_service(llm_client: LLMClient = Depends(get_llm_client)):
    return ChatService(llm_client)


@app.post("/chat")
async def chat_endpoint(
        request: ChatRequest,
        chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.handle_chat(request)
```

### Pros and Cons

| **Pros**                       | **Cons**                                       |
|--------------------------------|------------------------------------------------|
| [+] Easy to test (mockable)    | [-] Resource waste (new instances per request) |
| [+] Clean dependency injection | [-] Expensive initialization repeated          |
| [+] No global state            | [-] No connection pooling benefits             |
| [+] Standard FastAPI pattern   | [-] Complex dependency chains                  |
|                                | [-] Memory overhead                            |
|                                | [-] Slower request processing                  |

---

## Option 3: FastAPI Depends with @lru_cache()

**Pattern**: Dependency injection with cached singletons

### Code Example

```python
from functools import lru_cache


@lru_cache()
def get_llm_client():
    return LLMClient()


@lru_cache()
def get_chat_service():
    return ChatService(
        llm_client=get_llm_client(),
        mcp_client=get_mcp_client(),
        history_repo=get_chat_history_repo()
    )


@app.post("/chat")
async def chat_endpoint(
        request: ChatRequest,
        chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.handle_chat(request)
```

### Pros and Cons

| **Pros**                         | **Cons**                           |
|----------------------------------|------------------------------------|
| [+] Resource efficiency (cached) | [-] Manual dependency wiring       |
| [+] Standard Python pattern      | [-] Complex factory functions      |
| [+] Testable with proper setup   | [-] Dependency chain explosion     |
| [+] FastAPI compatible           | [-] Fragile (break one, break all) |
|                                  | [-] No automatic cleanup           |
|                                  | [-] Hard to manage lifecycle       |

---

## Option 4: Singleton Solution

**Pattern**: Module-level singleton with automatic registration

Python's module system ensures a module is not loaded more than once, which avoids multiple copies of an instance. When a module is imported, all module-level code executes once and the resulting objects persist for the application lifetime.

### Code Example

```python
# llm_client.py - Client definition with auto-registration
class _LLMClient(ClosableService):
    def __init__(self):
        # Initialize client
        pass

    async def disconnect(self):
        # Cleanup logic
        pass


# Module-level singleton instance
llm_client = _LLMClient()
singleton_manager.register(llm_client)


# chat_service.py - Service definition
class _ChatService:
    def __init__(self):
        self.llm_client = llm_client  # Import singleton instances
        self.mcp_client = mcp_client
        self.history_repo = chat_history_repo


# Module-level singleton instance
chat_service = _ChatService()
singleton_manager.register(chat_service)

# main.py - Application setup
from .singleton_manager import singleton_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # All singletons auto-registered during import
    print(f"Registered {singleton_manager.get_registered_count()} services")
    yield
    await singleton_manager.shutdown_all()


# chat_router.py - Usage in endpoints
from .services.chat_service import chat_service


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return await chat_service.handle_chat(request)  # Use singleton directly
```

### Pros and Cons

| **Pros**                             | **Cons**                             |
|--------------------------------------|--------------------------------------|
| [+] Leverages Python's module system | [-] Import order dependencies        |
| [+] No metaclass complexity          | [-] Less familiar to some developers |
| [+] Automatic registration           | [-] Requires documentation           |
| [+] Resource efficiency              |                                      |
| [+] Easy to test (reset capability)  |                                      |
| [+] Guaranteed persistence           |                                      |
| [+] Interface-based cleanup          |                                      |
| [+] Simple, Pythonic approach        |                                      |

### Important Note

- Python's module system ensures that modules are only loaded once per interpreter session, so importing the same module won't create a new instance
- Module objects are stored in `sys.modules`
- if `src` is also registered as python root, `src.x.y.my_service` and `x.y.my_service` could potentially be treated as 2 different instances depending on how you set up singleton

### Mocking and Testing

If you want mocking and testing, you can consider:

```python
class _ChatService:

    def __init__(self):
        self.llm_client = llm_client  # allows mocking
```
