# Python Style Guide
> This document defines code-level style conventions for Python development. Use this as the primary reference for formatting, structure, and technical implementation details when writing individual modules or functions.

## Navigation

| Section | Topic | Quick Access |
|---------|-------|--------------|
| **1. Environment Setup** | Virtual environment, package management, Python version | [→ Section 1](#1-environment-setup) |
| **2. Code Organization** | Class structure, imports, module organization | [→ Section 2](#2-code-organization) |
| **3. Python Class Organization** | Class properties, direct access, import style | [→ Section 3](#3-python-class-organization) |
| **4. Type Annotations** | Function parameters, return values, Pydantic models | [→ Section 4](#4-type-annotations) |
| **5. Project Structure & Layout** | Directory layout, 3-tier architecture structure | [→ Section 5](#5-project-structure--layout) |
| **5.1. Default 3-Tier Structure** | Standard project layout | [→ Section 5.1](#51-default-3-tier-project-structure) |
| **5.2. Advanced Structure** | Enterprise structure when requested | [→ Section 5.2](#52-advanced-structure-only-when-explicitly-requested) |
| **5.3. Multi-Project Organization** | Organization namespace examples | [→ Section 5.3](#53-multi-project-organization-example) |
| **5.6. Import Patterns** | Namespace and import examples | [→ Section 5.6](#56-sample-import-patterns-default-3-tier) |
| **6. Architecture Selection & Patterns** | How to choose and implement architecture patterns | [→ Section 6](#6-architecture-selection--patterns) |
| **6.1. Architecture Decision Guidelines** | When to use which architecture pattern | [→ Section 6.1](#61-architecture-decision-guidelines) |
| **6.2. Simple 3-Tier Architecture** | Default architecture pattern | [→ Section 6.2](#62-default-simple-3-tier-architecture) |
| **6.3. Advanced Service Architecture** | Enterprise architecture patterns | [→ Section 6.3](#63-advanced-service-architecture) |
| **7. Incremental Development Methodology** | Quality-gated development process | [→ Section 7](#7-incremental-development-methodology) |
| **7.1. Core Principles** | Dependency-first ordering, quality gates | [→ Section 7.1](#71-core-principles) |
| **7.2. Development Flow** | Phase structure and progression | [→ Section 7.2](#72-development-flow) |
| **7.3. Human-in-the-Loop Principle** | Decision points and collaboration | [→ Section 7.3](#73-human-in-the-loop-principle) |
| **8. API Development Standards** | FastAPI, documentation, request validation | [→ Section 8](#8-api-development-standards) |
| **9. Database Integration** | MySQL, SQLAlchemy, migrations, connections | [→ Section 9](#9-database-integration) |
| **10. Caching Strategies** | Simple vs advanced caching patterns | [→ Section 10](#10-caching-strategies) |
| **10.1. Default Caching** | Simple caching approaches | [→ Section 10.1](#101-default-caching-simple) |
| **10.2. Advanced Caching** | Enterprise caching patterns | [→ Section 10.2](#102-advanced-caching-when-explicitly-requested) |
| **11. Pure Assembly & Testing Philosophy** | Code structure and testing strategy | [→ Section 11](#11-pure-assembly--testing-philosophy) |
| **12. Test Naming Conventions** | File patterns, class patterns, method patterns | [→ Section 12](#12-test-naming-conventions) |
| **12.1. General Rules** | Basic test naming conventions | [→ Section 12.1](#121-general-test-naming-rules) |
| **12.2. Unit Test Naming** | Unit test specific patterns | [→ Section 12.2](#122-unit-test-naming-tests) |
| **12.3. Integration Test Naming** | Integration test patterns | [→ Section 12.3](#123-integration-test-naming-integration) |
| **13. Development Best Practices** | Code formatting, documentation, constants | [→ Section 13](#13-development-best-practices) |
| **14. Cross-References** | Links to related documents and sections | [→ Section 14](#14-cross-references) |

---

## 1. Environment Setup

| Requirement | Specification |
|-------------|---------------|
| Virtual Environment | Create in `.venv` directory at project root |
| Compatibility | Ensure project runs both inside Docker and locally using the `.venv` |
| Package Management | Use `uv` for dependency management and virtual environment creation |
| Python Version | Specify minimum Python version in `pyproject.toml` |

## 2. Code Organization

| Guideline | Details |
|-----------|---------|
| Class Structure | Organize code in classes with static methods rather than standalone functions |
| Method Order | Public methods above private methods in a class |
| Module Structure | One primary class per module with related helper classes when needed |
| Import Style | Group imports: standard library, third-party, local modules |

## 3. Python Class Organization

| Rule | Example | Reasoning |
|------|---------|-----------|
| **Class properties over module variables** | `Database.engine` not `engine = Database.get_engine()` | Clear ownership and namespace |
| **Direct access over getter methods** | `Database.engine` not `Database.get_engine()` | Simple properties don't need methods |
| **Class name matches file name** | `Database` class in `database.py` | Predictable and discoverable |
| **Caller chooses aliasing** | Let users do `engine = Database.engine` where needed | Don't force module-level aliases |

**Import Style**:
- Import the class: `from github_mingzilla.api_link.core.database import Database`
- Access components: `Database.engine`, `Database.get_session()`
- Avoid importing components directly: ~~`from database import engine, Base`~~

**Key Principle**: Prefer explicit class interfaces over magic module-level variables. The class should own its components, and callers should access them directly through the class namespace.

## 4. Type Annotations

| Requirement | Details |
|-------------|---------|
| Function Parameters | Required for all parameters |
| Return Values | Required for all functions and methods |
| Local Variables | Optional within methods |
| Pydantic Models | Use Pydantic with "Strict Mode" for data validation |
| Collection Types | Prefer explicit collection types (e.g., `list[str]` over `List[str]`) |

## 5. Project Structure & Layout

**Default structure follows simple 3-tier architecture pattern.** The key principle is organization/project_name/modules structure to support multiple projects under the same organization namespace.

| Directory | Purpose | Notes |
|-----------|---------|-------|
| `src/` | **EXPLICIT SOURCE ROOT** | All application source code lives here |
| `tests/` | Unit tests | Mirrors `src/` structure for unit tests |
| `integration/` | Integration tests | Tests for component interactions |
| `functional/` | End-to-end tests | For testing complete workflows and API endpoints |

### 5.1. Default 3-Tier Project Structure

IMPORTANT: DO NOT create empty directories upfront. Follow this structure if you decide where to put new files.

```
project_root/                       # Root directory for the project
├── .venv/                           # Virtual environment
├── src/                             # EXPLICIT SOURCE ROOT
│   └── github_mingzilla/            # Organization namespace
│       └── api_link/                # PROJECT NAME (e.g., api_link, data_processor, web_scraper)
│           ├── controllers/         # API controllers (FastAPI routes)
│           │   ├── chart_controller.py
│           │   └── user_controller.py
│           ├── services/            # Business logic services
│           │   ├── chart_service.py
│           │   └── user_service.py
│           ├── repositories/                # Data Access Objects
│           │   ├── chart_repository.py
│           │   └── user_repository.py
│           ├── models/              # Pydantic models and SQLAlchemy entities
│           │   ├── entities/        # SQLAlchemy database entities
│           │   │   ├── chart.py
│           │   │   └── user.py
│           │   ├── requests/        # API request models
│           │   │   ├── chart_request.py
│           │   │   └── user_request.py
│           │   └── responses/       # API response models
│           │       ├── chart_response.py
│           │       └── user_response.py
│           ├── core/                # Core functionality
│           │   ├── config.py        # Application configuration
│           │   ├── database.py      # Database connection and session management
│           │   └── exceptions.py    # Custom exceptions
│           └── utils/               # Utility functions and helpers
│               └── validators.py
├── tests/                           # Unit tests (mirrors src/ structure)
│   └── github_mingzilla/            # Organization namespace
│       └── api_link/                # PROJECT NAME
│           ├── controllers/         # Tests for controllers
│           ├── services/            # Tests for services
│           ├── repositories/                # Tests for Repositories
│           ├── models/              # Tests for models
│           ├── core/                # Tests for core functionality
│           └── utils/               # Tests for utilities
├── integration/                     # Integration tests
│   └── github_mingzilla/            # Organization namespace
│       └── api_link/                # PROJECT NAME
│           ├── controllers/         # Controller-Service integration tests
│           ├── services/            # Service-Repository integration tests
│           └── database/            # Database integration tests
├── functional/                      # Functional/E2E tests
│   └── github_mingzilla/            # Organization namespace
│       └── api_link/                # PROJECT NAME
│           ├── api/                 # Complete API endpoint tests
│           └── workflows/           # Complete workflow tests
├── conftest.py                      # Global pytest fixtures
├── pyproject.toml                   # Project metadata and dependencies
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker services configuration
└── README.md                        # Project documentation
```

### 5.2. Advanced Structure (Only When Explicitly Requested)

When advanced service architecture is specifically requested, refer to `system-service-architecture_generic.md` and restructure the services directory to include:

```
├── services/                        # Business logic services (Advanced)
│   ├── integration/                 # Integration services
│   ├── cache/                       # Cache services
│   │   ├── long_term/               # LongTermCache services
│   │   ├── l1/                      # L1Cache services
│   │   └── l2/                      # L2Cache (Redis) services
│   └── db/                          # DbService layer
```

### 5.3. Multi-Project Organization Example

This structure allows for multiple projects under the same organization:

```
src/github_mingzilla/
├── api_link/                        # API linking project
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   └── models/
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

### 5.4. Test Structure Notes

| Test Type | Location | Purpose |
|-----------|----------|---------|
| Unit Tests | `tests/github_mingzilla/api_link/` | Test individual units in isolation, mock dependencies |
| Integration Tests | `integration/github_mingzilla/api_link/` | Test component interactions, using real internal dependencies |
| Functional Tests | `functional/github_mingzilla/api_link/` | Test complete workflows, through API endpoints |

### 5.5. Source & Test Development

| Guideline | Details |
|-----------|---------|
| Package Installation | Use `pip install -e .` during development to enable imports |
| pytest Configuration | Configure `pyproject.toml` or `pytest.ini` to manage test roots |
| Import Pathing | Source imports use the full namespace path |
| Multi-Project Support | Each project maintains its own namespace under the organization |

### 5.6. Sample Import Patterns (Default 3-Tier)

```python
# In source code (api_link project)
from github_mingzilla.api_link.services.chart_service import ChartService
from github_mingzilla.api_link.repositories.chart_repository import ChartRepository
from github_mingzilla.api_link.models.entities.chart import Chart

# In unit tests (api_link project)
from github_mingzilla.api_link.controllers.chart_controller import ChartController
from github_mingzilla.api_link.services.chart_service import ChartService

# In integration tests (api_link project)
from github_mingzilla.api_link.controllers.chart_controller import ChartController
from github_mingzilla.api_link.services.chart_service import ChartService
from github_mingzilla.api_link.repositories.chart_repository import ChartRepository

# Cross-project imports (if needed)
from github_mingzilla.data_processor.services.data_service import DataService
from github_mingzilla.web_scraper.services.scraper_service import ScraperService
```

### 5.7. Project Configuration (pyproject.toml)

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "api-link"
description = "API linking service"
dynamic = ["version"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

## 6. Architecture Selection & Patterns

**[Trigger: When choosing system architecture or designing application layers]**

### 6.1. Architecture Decision Guidelines

| Scenario | Recommended Approach | Reasoning |
|----------|---------------------|-----------|
| **New project or simple application** | 3-tier architecture (Controller → Service → Repository) | Simpler, easier to understand and maintain |
| **CRUD operations with basic business logic** | 3-tier architecture | Standard pattern, well-understood |
| **Small to medium team** | 3-tier architecture | Less complexity, faster development |
| **Enterprise application with complex caching** | Advanced service architecture | When explicitly requested for complex requirements |
| **Multi-node distributed system** | Advanced service architecture | When L1/L2/LongTermCache patterns are specifically needed |
| **High-performance caching requirements** | Advanced service architecture | Only when cache invalidation and multi-layer caching is critical |

> **Key Rule**: Start with 3-tier architecture by default. Only move to advanced service architecture when explicitly requested or when simple patterns prove insufficient for specific enterprise requirements.

### 6.2. Default: Simple 3-Tier Architecture

**Use this approach by default unless explicitly told to use the advanced service architecture.**

```
[Controller/API Layer]
        |
        v
[Service Layer]
        |
        v
[Repository/Entity Layer]
```

| Layer | Responsibility | Implementation |
|-------|---------------|----------------|
| **Controller/API** | Handle HTTP requests, validation, response formatting | FastAPI routers, endpoint functions |
| **Service** | Business logic, orchestration, transaction management | Service classes with business methods |
| **Repository/Entity** | Data access, database operations, entity mapping | SQLAlchemy models, repository pattern |

### 6.3. Advanced Service Architecture

**Only use when explicitly requested or for complex enterprise applications.**

Refer to `system-service-architecture_generic.md` for:
- Multi-layer caching (L1Cache, LongTermCache, L2Cache)
- Integration services
- Complex service hierarchies
- Advanced caching strategies

## 7. Incremental Development Methodology

**[Trigger: When developing layered architecture, implementing CRUD systems, or conducting incremental development]**

This methodology ensures systematic development with quality gates at each layer, preventing integration issues and ensuring each commit contains fully working, tested code.

### 7.1. Core Principles

| Principle | Description | Benefit |
|-----------|-------------|---------|
| **Dependency-First Ordering** | Build layers in order of dependencies (Domain → Database → API) | Minimal dependencies per layer, easier debugging |
| **Quality Gates Before Progression** | Complete each layer with tests before moving to next | Catch issues early, commit working code per layer |
| **Incremental Build-Up** | Like foundation → walls → roof construction | Validate each layer works before building on top |
| **1-to-1 Layer Relationships** | Follow 3-tier architecture with clean dependencies | Maintainable, testable, clear separation of concerns |

### 7.2. Development Flow

```
Phase 1: Domain Foundation
    |
    v
[Quality Gate: Unit tests pass]
    |
    v
Phase 2: Database Integration
    |
    v
[Quality Gate: Integration tests pass]
    |
    v
Phase 3: API Layer
    |
    v
[Quality Gate: Functional tests pass]
```

#### 7.2.1. Phase Structure

| Phase | Layer Focus | Dependencies | Quality Gate |
|-------|-------------|--------------|--------------|
| **Phase 1** | Domain Foundation | Minimal (pydantic only) | Unit tests pass |
| **Phase 2** | Database Integration | Domain + SQLAlchemy | Integration tests pass |
| **Phase 3** | API Layer | Repository + FastAPI | Functional tests pass |

### 7.3. Human-in-the-Loop Principle

**Definition**: When conducting checklist analysis or breaking down development actions, each item should represent a decision point requiring human confirmation, validation, or choice before proceeding.

**Application**:
- Library installation decisions ("Is this the correct version?")
- Directory structure choices ("Where should this file be placed?")
- Configuration confirmations ("Are these database settings correct?")
- Test validation checkpoints ("Do all tests pass before proceeding?")
- Implementation approach selections ("Should we use this pattern?")

**Benefits**:
- Natural pause points for course correction
- Explicit decision documentation
- Reduced automation errors from assumed choices
- Better human-AI collaboration in development workflows

**Usage in Checklists**: Structure checklist items so each requires human input:
```markdown
✅ Good: "Install library pydantic (confirm version choice)"
❌ Bad: "Install all required libraries automatically"

✅ Good: "Create domain Book in desired directory (specify location if not provided)"
❌ Bad: "Create domain models"
```

## 8. API Development Standards

| Standard | Implementation |
|----------|---------------|
| Framework | FastAPI for API implementation |
| Documentation | Auto-generate OpenAPI docs with complete descriptions |
| Request Validation | Use Pydantic models for request/response validation |
| Error Handling | Consistent error responses with appropriate HTTP status codes |
| Architecture | **DEFAULT: Use simple 3-tier architecture (Controller/API ↔ Service ↔ Repository/Entity)** |

## 9. Database Integration

| Guideline | Details |
|-----------|---------|
| Database | MySQL as primary database |
| ORM | Use SQLAlchemy with type annotations |
| Migrations | Implement with Alembic |
| Connection | Use environment variables for connection details |
| Architecture | **DEFAULT: Use simple 3-tier architecture with Repository pattern** |

## 10. Caching Strategies (Only When Explicitly Requested)

### 10.1. Default Caching (When Explicitly Requested - Simple)

| Pattern | Implementation | Use Case |
|---------|---------------|----------|
| **Simple Cache** | Redis via redis-py or in-memory cache | Basic caching needs |
| **Application Cache** | cachetools.LRUCache | Local application caching |

### 10.2. Advanced Caching (When Explicitly Requested - Advanced)

| Layer | Implementation | Details |
|-------|---------------|---------|
| L1Cache | cachetools.LRUCache | Very short-lived cache for rate-limiting |
| LongTermCache | cachetools.TTLCache | Longer-lived cache with validity checking |
| L2Cache | Redis via redis-py | Distributed cache for multi-node consistency |

> **Note**: Advanced caching patterns from `system-service-architecture_generic.md` should only be implemented when specifically requested or for enterprise-scale applications.

## 11. Pure Assembly & Testing Philosophy

### Pure Assembly Pattern

- **Services are assemblers, not logic containers**
- **All logic (conditions, looping, mapping, filtering, reducing, etc.) belongs in pure functions/static methods**
- **Services coordinate repositories and pure functions**
- **Immutable objects for better memory management**

### Testing Strategy (Consequence of Pure Assembly)

| Component Type | Testing Strategy | Tools | Reasoning |
|----------------|------------------|-------|-----------|
| **Pure Logic** | Unit tests with real data | pytest | Easy to test because functions are pure |
| **Services** | Integration tests with real DB | pytest + test database | Services are assemblers - test the complete assembly |
| **Controllers** | Integration tests with real services | TestClient + real stack | Test the complete request flow |
| **End-to-End** | Functional tests | Full application stack | Validate complete user workflows |

**Key Principle**: If you need to mock it, you're probably testing at the wrong level or your code isn't properly separated. Pure assembly makes mocking unnecessary.

## 12. Test Naming Conventions

**[Trigger: When writing tests or organizing test files]**

### 12.1. General Test Naming Rules

| Rule | Convention | Example |
|------|------------|---------|
| File Names | `test_<module_or_feature>.py` | `test_chart_service.py` |
| Class Names | `Test<ClassName>` or `Test<Feature>` | `TestChartService`, `TestUserAuthentication` |
| Method Names | `test_<action>_<condition>_<expected_result>` | `test_create_chart_with_valid_data_returns_chart_id` |
| Constants | `UPPER_CASE` for test data constants | `VALID_CHART_DATA`, `MOCK_USER_ID` |

### 12.2. Unit Test Naming (tests/)

| Component | File Pattern | Class Pattern | Method Pattern |
|-----------|--------------|---------------|----------------|
| **Controllers/API** | `test_<endpoint_name>_controller.py` | `Test<EndpointName>Controller` | `test_<http_method>_<scenario>_<status_code>` |
| **Services** | `test_<service_name>_service.py` | `Test<ServiceName>Service` | `test_<method_name>_<scenario>_<result>` |
| **Repositories** | `test_<repository_name>_repository.py` | `Test<RepositoryName>Repository` | `test_<operation>_<scenario>_<result>` |
| **Models/Entities** | `test_<model_name>_model.py` | `Test<ModelName>Model` | `test_<validation_or_method>_<scenario>_<result>` |
| **Utilities** | `test_<utility_name>_utils.py` | `Test<UtilityName>Utils` | `test_<function_name>_<scenario>_<result>` |

**Examples:**
```python
# tests/github_mingzilla/api_link/controllers/test_chart_controller.py
class TestChartController:
    def test_get_chart_with_valid_id_returns_200(self):
    def test_get_chart_with_invalid_id_returns_404(self):
    def test_post_chart_with_valid_data_returns_201(self):

# tests/github_mingzilla/api_link/services/test_chart_service.py
class TestChartService:
    def test_get_chart_by_id_with_valid_id_returns_chart(self):
    def test_get_chart_by_id_with_invalid_id_raises_not_found(self):
    def test_create_chart_with_duplicate_name_raises_conflict(self):

# tests/github_mingzilla/api_link/repositories/test_chart_repository.py
class TestChartRepository:
    def test_find_by_id_with_existing_id_returns_chart(self):
    def test_find_by_id_with_nonexistent_id_returns_none(self):
    def test_save_with_valid_chart_persists_to_database(self):
```

### 12.3. Integration Test Naming (integration/)

| Component | File Pattern | Class Pattern | Method Pattern |
|-----------|--------------|---------------|----------------|
| **Controller-Service** | `test_<controller>_<service>_integration.py` | `Test<Controller><Service>Integration` | `test_<workflow>_<scenario>_<result>` |
| **Service-Repository** | `test_<service>_<repository>_integration.py` | `Test<Service><Repository>Integration` | `test_<operation>_<scenario>_<result>` |
| **Database Integration** | `test_<component>_db_integration.py` | `Test<Component>DbIntegration` | `test_<operation>_<scenario>_<result>` |
| **Full Stack** | `test_<feature>_full_stack_integration.py` | `Test<Feature>FullStackIntegration` | `test_<complete_flow>_<scenario>_<result>` |

### 12.4. Functional API Test Naming (functional/)

| Component | File Pattern | Class Pattern | Method Pattern |
|-----------|--------------|---------------|----------------|
| **API Endpoints** | `test_<resource>_api_functional.py` | `Test<Resource>ApiFunctional` | `test_<http_method>_<endpoint>_<scenario>_<status>` |
| **Workflows** | `test_<workflow_name>_workflow.py` | `Test<WorkflowName>Workflow` | `test_<complete_user_journey>_<scenario>_<result>` |
| **Authentication** | `test_<auth_feature>_auth_functional.py` | `Test<AuthFeature>AuthFunctional` | `test_<auth_flow>_<scenario>_<result>` |

### 12.5. Test Data and Fixture Naming

| Type | Convention | Example |
|------|------------|---------|
| **Fixture Functions** | `<resource_type>_<state>` | `valid_chart_data`, `authenticated_user`, `empty_database` |
| **Test Constants** | `<SCOPE>_<TYPE>_<PURPOSE>` | `VALID_CHART_DATA`, `INVALID_USER_ID`, `TEST_DATABASE_URL` |
| **Parametrized Data** | `<test_case>_<scenarios>` | `chart_validation_scenarios`, `auth_failure_cases` |

## 13. Development Best Practices

| Practice | Details |
|----------|---------|
| Optional Parameters | **NEVER use optional parameters with default values** - callers must explicitly pass None or a value. Use `param: Optional[str]` not `param: str = None` |
| Constants | Define constants at module level using UPPER_CASE |
| Documentation | Docstrings for all public classes and methods (Google style) |
| Line Length | Maximum 999 characters (manually maintained for readability) |
| Code Formatting | Use Ruff for linting, formatting, and import sorting |
| Import Ordering | Use Ruff to automatically organize imports in groups: standard library, third-party, local modules |
| Import Style | Avoid relative imports with "." or ".."; configure Ruff to maintain this pattern |
| Trailing Commas | **ALWAYS use trailing commas in multi-line function calls and data structures to prevent formatters from collapsing to single line** |
| List Operations | **Prefer explicit step-by-step filtering and transformations over complex list comprehensions or method chaining** |
| Architecture Choice | **DEFAULT: Use simple 3-tier architecture unless advanced patterns explicitly requested** |

### 13.1. Optional Parameters - Explicit Examples

**❌ NEVER DO THIS:**
```python
# BAD - Default values hide caller intent
def process_data(data: str, model: str = None, timeout: int = 30):
    pass

def calculate(value: float, precision: int = 2):
    pass
```

**✅ ALWAYS DO THIS:**
```python
# GOOD - Caller must be explicit about every parameter
from typing import Optional

def process_data(data: str, model: Optional[str], timeout: int):
    pass

def calculate(value: float, precision: int):
    pass

# Callers must be explicit:
process_data("test", None, 30)  # Clear intent
process_data("test", "gpt-4", 60)  # Clear intent
calculate(3.14159, 2)  # Clear intent
```

**Reasoning**: Optional parameters with defaults hide caller intent and make it unclear what values are actually being passed. Requiring explicit values makes code more readable and prevents bugs from assumed defaults.

### 13.2. Trailing Commas - Preserving Multi-Line Format

**Use trailing commas to preserve intentional multi-line formatting and prevent code formatters from collapsing to single lines.**

**✅ ALWAYS DO THIS for multi-line structures:**
```python
# Function calls with multiple parameters
response = await llm_client.chat_completion(
    messages=conversation,
    model=chat_request.model,
    stream=False,
    tools=tools if tools else None,  # <- Trailing comma preserves multi-line
)

# Function definitions with multiple parameters
async def chat_completion(
    self,
    messages: List[ChatMessage],
    model: Optional[str],
    stream: bool,
    tools: Optional[List[dict]],  # <- Trailing comma preserves multi-line
) -> str:

# Dictionary definitions
config = {
    "database_url": os.getenv("DATABASE_URL"),
    "pool_size": 20,
    "max_overflow": 30,
    "echo": False,  # <- Trailing comma preserves multi-line
}

# List definitions
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",  # <- Trailing comma preserves multi-line
]
```

**❌ WITHOUT trailing commas (gets collapsed by formatter):**
```python
# This gets collapsed to single line by Ruff:
response = await llm_client.chat_completion(messages=conversation, model=chat_request.model, stream=False, tools=tools if tools else None)

# This gets collapsed to single line by Ruff:
config = {"database_url": os.getenv("DATABASE_URL"), "pool_size": 20, "max_overflow": 30, "echo": False}
```

**Key Benefits:**
- **Preserves intentional formatting**: Multi-line structure stays multi-line
- **Better diffs**: Adding new parameters doesn't change existing lines
- **Consistent style**: Works with Ruff, Black, and other formatters
- **Community standard**: Widely adopted Python practice

**When to use:**
- Multi-line function calls with 3+ parameters
- Multi-line function definitions
- Multi-line dictionaries and lists
- Any time you want to preserve multi-line format

### 13.3. List Operations - Explicit Step-by-Step Processing

**Prefer explicit, debuggable operations over complex one-liners that combine multiple concerns.**

#### **The Problem with Complex List Comprehensions and Chaining**

**❌ AVOID: Complex list comprehensions with multiple conditions**
```python
# Hard to debug, difficult to test individual conditions
result = [item.process() for sublist in data
          if sublist.is_valid()
          for item in sublist.items
          if item.status == 'active'
          if item.priority > threshold
          if not item.is_expired()]

# Even worse: nested access makes it unreadable
tools = [tool for tool in all_tools if tool["function"]["name"] in selected_tools]
```

**❌ AVOID: Method chaining that can't be debugged**
```python
# Can't inspect intermediate results without breaking the chain
result = (data
    .filter(lambda sublist: sublist.is_valid())
    .flatMap(lambda sublist: sublist.items)
    .filter(lambda item: item.status == 'active')
    .filter(lambda item: item.priority > threshold)
    .map(lambda item: item.process()))
```

#### **✅ PREFERRED: Step-by-Step with Debug Points**

```python
# Each step is debuggable and testable - be sure filtering happens before other operation if possible
valid_sublists = filter(lambda sublist: sublist.is_valid(), data)
all_items = flatMap(lambda sublist: sublist.items, valid_sublists)
active_items = filter(lambda item: item.status == 'active', all_items)
priority_items = filter(lambda item: item.priority > threshold, active_items)
unexpired_items = filter(lambda item: not item.is_expired(), priority_items)
result = list(map(lambda item: item.process(), unexpired_items))

# For simple filtering, convert to list for easier debugging:
selected_tool_names = set(selected_tools)  # Only if performance matters
filtered_tools = filter(lambda tool: tool["function"]["name"] in selected_tools, all_tools)
tools = list(filtered_tools)
```

#### **Why This Approach is Superior**

| Benefit | Explanation | Example |
|---------|-------------|---------|
| **Debugging** | Can set breakpoints and inspect `active_items`, `priority_items`, etc. | `print(f"Active items: {len(active_items)}")` |
| **Testing** | Each step can be unit tested independently | Test priority filtering logic separately |
| **Maintenance** | Easy to add/remove/modify individual filters | Add `if debug: print(priority_items)` between steps |
| **Performance Analysis** | Can profile each step to find bottlenecks | Time each filter operation individually |
| **Conditional Logic** | Easy to add conditional processing | `if enable_priority_filter: priority_items = filter(...)` |

#### **Language-Specific Reasoning**

**Python lacks the optimization benefits of other languages:**

| Language | Why Chaining Works | Python Reality |
|----------|-------------------|----------------|
| **Java Streams** | JIT compiler fuses operations, lazy evaluation, parallel optimization | No JIT optimization, no operation fusion |
| **C# LINQ** | Compiler optimizations, deferred execution | Eager evaluation, no compiler optimization |
| **Groovy Collections** | Performance optimizations for chained operations | No special optimization for chains |

**In Python, there's no performance penalty for step-by-step operations, but massive debugging benefits.**

#### **Guidelines for List Operations**

1. **Simple filtering**: Use `filter()` with lambda over list comprehensions
2. **Multiple conditions**: Break into separate filter steps
3. **Complex transformations**: Use intermediate variables for each step
4. **Method chaining**: Avoid - use step-by-step assignments instead
5. **Set optimization**: Only convert to `set()` for large lists (>100 items) when lookup performance matters

**Key Principle**: **Code is read more often than written.** Optimize for debugging and maintenance, not clever one-liners.

## 14. Cross-References

**→ Advanced Architecture:** See `system-service-architecture_generic.md` for complete L1Cache/L2Cache/LongTermCache implementation
**→ Incremental Development:** Use Human-in-the-Loop principle (Section 7.3) for phase-by-phase implementation validation
**→ Project Structure:** Default 3-tier structure (Section 5.1) unless enterprise caching explicitly requested
**→ Multi-Project Setup:** Reference organization structure (Section 5.3) for cross-project imports
**→ Cache Implementation:** Use simple Redis/LRUCache (Section 10.1) unless advanced patterns (Section 10.2) explicitly requested
**→ Test Organization:** Follow naming conventions (Section 12) for unit/integration/functional test separation
**→ Architecture Decisions:** Use decision table (Section 6.1) and decision trees (Section 6.2, Section 6.3) for pattern selection
