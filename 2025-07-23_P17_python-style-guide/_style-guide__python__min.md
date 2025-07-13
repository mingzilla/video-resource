### 🧼 Python Style Guide

#### 1. Core Principles
- Tooling handles formatting (Ruff/pre-commit)
- Explicit > Implicit, Readable > Clever
- Document exceptions with `# NOTE:`

#### 2. Import Rules
```python
# Standard library
import os

# Third-party
from fastapi import FastAPI

# Local (absolute only)
from project.models.user import User
```

#### 3. Function Rules
❌ No default values:
```python
def connect(timeout=30): ...  # ❌ Bad
```

✅ Explicit parameters:
```python
def connect(timeout: int) -> bool:  # ✅ Good
    """Timeout in seconds (30 recommended)."""

def find_user(user_id: Optional[int]) -> User: # Good
    """Caller must explicitly pass None or value."""
```

#### 4. Class Design
```python
# database.py
class Database:
    @staticmethod
    def create(): ...  # Prefer static methods
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

#### 6. Add trailing comma for multi-line structures
```python
config = {
    "pool_size": 20,  # Trailing comma
}

def get_user(id: int) -> User | None:  # Explicit types
```

#### 7. Error Handling
```python
except ValueError as e:  # Always name exceptions
    logger.error(f"Bad value: {e}")
```

#### 8. Testing
- Add Unit Tests for static methods
- Integration Tests must run against real systems (no mocks)
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

#### 9. Naming Guidelines
```python
MAX_RETRIES = 3  # UPPER_CASE Constants
class UserService:  # PascalCase Classes
def save_to_db():  # snake_case Functions
```

### 10. Project Structure - Use 3-Tier Project Structure (supports Multi-Projects)

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

### 11. Avoid Base URL in Constructors
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
