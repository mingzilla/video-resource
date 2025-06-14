```python
class Database:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"Connecting to {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        print(f"Disconnecting from {self.name}")

# Usage
with Database("users") as db:  # calls __enter__()
    print(f"Using {db.name}")  # calls __exit__() after last line
```


```python
from contextlib import contextmanager

@contextmanager
def database_context(name: str) -> ContextManager[Database]:
    print(f"Connecting to {name}")
    db = Database(name)
    try:
        yield db
    finally:
        db.close()

# Usage
with database_context("users") as db:  # calls __enter__()
    print(f"Using {db.name}")          # calls __exit__() after last line
```