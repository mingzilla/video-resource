### 🧼 Simplified Python Style Guide

#### 1. Core Principles
- Keep code readable and practical.
- Prioritize clarity over strict rule adherence.
- Use Ruff for automated formatting and linting.
- Follow PEP8, but allow modern exceptions for readability.

#### 2. Import Rules
✅ Prefer absolute imports:
```python
from mcp.client.session import ClientSession
```
❌ Avoid relative imports:
```python
from ..session import ClientSession  # ❌ Not allowed
```

Grouped by source:
```python
# Standard library
import os
import sys

# Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# Local modules
from github_mingzilla.utils.helpers import format_data
```

#### 3. Function & Method Writing
✅ Use clear function names with descriptive parameters:
```python
def connect(self) -> bool:
    """Establish connection to service."""
    ...
```

❌ Avoid default parameter values like timeout=30:
```python
def connect(self, timeout=30): ...  # ❌ timeout=30 is not allowed - caller must explicitly pass values
```

Use `Optional[T]` for optional arguments:
```python
def find_user(user_id: Optional[int]) -> User: # Good - caller must explicitly pass None or value
    ...
```

#### 4. Class Design
✅ One primary class per file named after the file:
```python
# In database.py
class Database:
    ...
```

Prefer static methods over standalone functions:
```python
class RepoUtil:
    @staticmethod
    def create(...):
        ...
```

Avoid unnecessary getters; prefer direct access:
```python
config = Config.instance  # ✅ Good
config.get_instance()     # ❌ Unnecessary
```

#### 5. Service Logic to Static Utils
**Rule:** Refactor service methods by extracting pure computation into `@staticmethod`s in a `xx_utils.py` file when:
1. Logic has no service dependencies (DB/API calls)
2. Only operates on input parameters
3. Has clear single responsibility

**Example:**
```python
# ❌ Before - Service contains computation
class ChartService:
    def generate_chart(self, data: list[dict]) -> bytes:
        valid = [d for d in data if d.get('value')]  # Pure logic
        return self._render_chart(valid)  # Service dep

# ✅ After - Computation moved to utils
# chart_utils.py
class ChartUtils:
    @staticmethod
    def filter_valid(data: list[dict]) -> list[dict]:
        return [d for d in data if d.get('value')]

# chart_service.py
class ChartService:
    def generate_chart(self, data: list[dict]) -> bytes:
        valid = ChartUtils.filter_valid(data)
        return self._render_chart(valid)
```

#### 6. Formatting Preferences

ALWAYS add trailing comma for multi-line structures:
```python
config = {
    "pool_size": 20,
    "echo": False, # always add , here
}
```

#### 7. Type Hints
Always prefer type hints:
```python
def get_user(user_id: int) -> Optional[User]:
    ...
```

Avoid overly broad types like `Any`. Use specific types where possible:
```python
data: Dict[str, Any]  # Better than just dict
```

Use Pydantic models for request/response validation:
```python
class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    num_results: int = Field(default=5, ge=1, le=50)
```

#### 8. Error Handling
Be explicit when catching errors:
```python
except Exception: # don't just put except without adding specific error or `Exception`, otherwise pre-commit hook will fail
```

#### 9. Testing Philosophy
- Integration tests should test a running system. They should not use mocks.
- Minimize mocking; refactor code to be testable without mocks.
- Prefer debuggable steps over complex one-liners.

✅ Good:
```python
valid_items = [item for item in data if item.is_valid()]
results = process_items(valid_items)
```

❌ Bad:
```python
results = [process(item) for item in data if item.is_valid() and item.priority > 3]
```

#### 10. Naming Guidelines
- Constants: `UPPER_CASE`
- Classes: `PascalCase`
- Functions/variables: `snake_case`

Examples:
```python
MAX_RETRY_ATTEMPTS = 3
def discover_tools():
tool_name: str = None
```

## 11. Project Structure - Use 3-Tier Project Structure (supports Multi-Projects)

```
├── .venv/
├── src/github_mingzilla/
      ├── data_processor/                  # Data processing project
      │   ├── processors/
      │   ├── transformers/
      │   ├── services/
      │   └── models/
      └── web_scraper/                     # Web scraping project
          ├── scrapers/
          ├── parsers/
          ├── services/
          └── models/
```

| Directory | Purpose | Notes |
|-----------|---------|-------|
| `src/` | **EXPLICIT SOURCE ROOT** | All application source code lives here |
| `tests/` | Unit tests | Mirrors `src/` structure for unit tests |
| `integration/` | Integration tests | Tests for component interactions |
| `functional/` | End-to-end tests | For testing complete workflows and API endpoints |


### 12. Avoid Base URL in Constructors

**Rule: Always pass the full URL to HTTP methods; never hardcode or lock a base URL in the constructor.**

```python
# ✅ Good - use Full URL in methods
class MyClient:
    async def get(self, url: str, **kwargs):
        return await self.session.get(url, **kwargs)
```

```python
# ❌ Bad - Base URL locked in constructor
class MyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url # ❌ Bad

    async def get_resource(self, path: str):
        # Hidden URL composition makes it harder to trace and test
        return await self.session.get(f"{self.base_url}/{path}")
```