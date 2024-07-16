# Summary

* typing
* function as type

## Typing

```python

class Person:
    age = 0
    height = 0.0  # `height: float` does not make it a float field, the only way for python to know the type is by forcing a value into a field 
    is_active = False
```

* param: x can be str or int
* param: y can only be int
* return: -> type

```python
from typing import Union


def my_function(x: Union[str, int], y: int) -> int:
    if isinstance(x, int):
        return x + y
    elif isinstance(x, str):
        return int(x) + y  # Convert the string to an integer before adding y
    else:
        raise ValueError("Parameter x must be a string or an integer")


# Example usage:
result1 = my_function(5, 3)  # Output: 8
result2 = my_function("5", 3)  # Output: 8

```

### function as param with typing

```python
from typing import Callable


def apply_operation(x: int, y: int, operation: Callable[[int, int], int]) -> int:
    """Apply the specified operation to x and y."""
    return operation(x, y)


# Example usage:
def add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y


def subtract(x: int, y: int) -> int:
    """Subtract y from x."""
    return x - y


result1 = apply_operation(5, 3, add)  # Output: 8
result2 = apply_operation(5, 3, subtract)  # Output: 2
```
