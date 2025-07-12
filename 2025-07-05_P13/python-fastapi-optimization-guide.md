# FastAPI Performance Optimization Guide

## 1. Understanding Performance Impact Areas

- (what) - performance impact analysis
- (why) - how python import works
- (how) - what is lazy loading and how it works
- (recommendation) - optimisation for source and tests

### 1.1 Startup Time vs Request Time

| Performance Area | Impact                                | When It Matters                          |
|------------------|---------------------------------------|------------------------------------------|
| **Startup Time** | Model schema building, imports        | App initialization, testing, development |
| **Request Time** | Active model validation/serialization | Production traffic, user experience      |

**Key Insight**:

- If your endpoint uses 3 Pydantic models,
- the other 77 models in your codebase won't affect that specific request's performance.
- Only the models actively used in the request pipeline matter for response time.

### 1.2 Performance Bottleneck Identification

```
Application Lifecycle
│
├── Startup Phase
│   ├── Python imports (eager loading)
│   ├── Pydantic schema building
│   └── Framework initialization
│
└── Request Phase
    ├── Route matching
    ├── Model validation (only used models)
    └── Response serialization (only used models)
```

## 2. The Python Import Problem (Universal Issue)

### 2.1 How Python Import Works

| Import Pattern    | Loading Behavior                                 | When Schema Builds      |
|-------------------|--------------------------------------------------|-------------------------|
| **Eager Loading** | import is written on the top of a Python file    | At module import time   |
| **Lazy Loading**  | imports are written inside every method/function | When function is called |

- **If a class is not imported by anything else** → everything stays lazy loaded
- **This is a Python language issue, not a FastAPI/Pydantic specific problem.**

| Framework   | Same Import Behavior                 |
|-------------|--------------------------------------|
| Flask       | ✅ Top-level imports load immediately |
| FastAPI     | ✅ Top-level imports load immediately |
| Pure Python | ✅ Top-level imports load immediately |

### 2.2 How FastAPI Works and Why It's Slow

```
FastAPI App Import Chain
│
app = FastAPI()
│
├── Router 1 (users.py)
│   ├── from models.user import User, UserCreate, UserUpdate
│   ├── @router.post("/", response_model=User)
│   └── def create_user(data: UserCreate) → triggers schema validation
│
├── Router 2 (orders.py) 
│   ├── from models.order import Order, OrderCreate, OrderUpdate
│   ├── from models.user import User  # Cross-dependencies!
│   ├── @router.post("/", response_model=Order)
│   └── def create_order(data: OrderCreate) → triggers schema validation
│
├── Router 3 (products.py)
│   ├── from models.product import Product, ProductCreate, ProductUpdate
│   ├── from models.order import Order  # More cross-dependencies!
│   └── → triggers more schema validations
│
└── ... (17 more routers)
    └── Each pulls more models via imports
        └── Cascading schema building for all imported models
```

**Key Insight**:

- If its imports pull in 20 models due to cross-dependencies, **all 20 schemas get built at startup**.
- **FastAPI endpoint signatures trigger schema validation, adding extra processing time during startup.**
- Schema validation calls `_core_utils.py:walk`, which takes processing time

### 2.3. Schema Build Time Optimization

#### 2.3.1 Pydantic Version Impact

**Use Pydantic 2.11+ for improved schema build time performance.** Recent versions have significantly optimized the schema building process.

### 2.3.2 Model Type Differentiation

| Model Type             | Your Code Example                | Performance Impact           |
|------------------------|----------------------------------|------------------------------|
| **Pydantic BaseModel** | `ProductCreate`, `ProductUpdate` | ✅ Normal usage - no concerns |
| **TypeAdapters**       | `TypeAdapter(list[int])`         | ❌ Avoid recreating these     |

**Recommendation**: Avoid constructing TypeAdapters repeatedly. Your standard Pydantic models (`ProductCreate`, `ProductUpdate`) are not TypeAdapters and don't have this issue.

## 3. How to make use of Lazy Loading

### 3.1 Lazy Loading - Code Examples

```python
# ❌ Eager Loading (Current Pattern)
from models.product import Product, ProductCreate


class ProductController:
    def create_product(self, data: ProductCreate) -> Product:
        return Product(**data.model_dump())


# ✅ Lazy Loading Pattern  
class ProductController:
    def create_product(self, data: dict) -> dict:
        # Import only when method is called
        from models.product import Product, ProductCreate
        product_model = ProductCreate(**data)
        return Product(**product_model.model_dump()).model_dump()
```

#### Lazy Loading Chain Effect

```
Import Chain Analysis
│
├── main.py → controller.py
│   ├── If controller imports models at top-level
│   └── All models load immediately ❌
│
└── Lazy Chain Alternative
    ├── main.py → controller.py  
    ├── Controller doesn't import models
    ├── Models imported inside methods only
    └── Models load only when needed ✅
```

## 4. Trade-offs and Recommendations

### 4.1 Approach Comparison

| Approach          | Pros                                | Cons                             | Consideration   |
|-------------------|-------------------------------------|----------------------------------|-----------------|
| **Eager Loading** | Type safety, IDE support, fail-fast | Slower startup                   | Source code     |
| **Lazy Loading**  | Faster startup, minimal memory      | Runtime overhead, delayed errors | e.g. unit tests |

### 4.2 Production Code

**Startup Time Estimates (Pydantic 2.11+)**

| Model Count     | Conservative Estimate | Pessimistic Estimate | Real-World Impact                |
|-----------------|-----------------------|----------------------|----------------------------------|
| **50 models**   | ~3-8 seconds          | ~10-15 seconds       | Acceptable for most cases        |
| **80 models**   | ~5-12 seconds         | ~15-25 seconds       | Noticeable delay                 |
| **200 models**  | ~12-25 seconds        | ~30-50 seconds       | ❌ Problematic for development    |
| **500+ models** | ~30+ seconds          | ~60+ seconds         | ❌ Requires architectural changes |

### 4.3 Test Code

**Test Performance Suggestion**

```
Test Lifecycle
│
├── Test Startup Phase
│   ├── Import test modules   <-- Reasonable
│   └── Import source modules <-- Avoid (Slow for large code base)
│
└── Test Execution Phase
    └── Import source modules <-- Fast
```

**Test Code Example:**

```python
# ❌ Eager Loading in Tests
from models.product import Product, ProductCreate  # Loaded immediately


def test_product_creation():
    # Test implementation
    pass


# ✅ Lazy Loading in Tests  
def test_product_creation():
    from models.product import Product, ProductCreate  # Loaded only when test runs
    # Test implementation
    pass
```
