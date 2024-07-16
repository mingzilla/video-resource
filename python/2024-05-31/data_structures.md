# Summary

* list - create / get / add / update / remove / mapping / filter
* set - create / get / add / update / remove
* dictionary - create / get / add / update / remove / keys / values / mapping / filter
* Common Functions

## List

```Ask chatGPT
* create a list and assign 2 values [1, 2] in one line
* add an item to a list
* get an item from a list at index
* remove an item from a list
* remove an item at a certain index from a list
* lambda map function on a list, e.g. a list [1, 2] runs a map function to add 1 to each item
* lambda filter function on a list, e.g. return odd numbers only
```

```python
# 1. Create a list and assign 2 values [1, 2] in one line
my_list = [1, 2]

# 2. Add an item to a list
my_list.append(3)
# my_list is now [1, 2, 3]

# 3. Remove an item from a list
my_list.remove(2)
# my_list is now [1, 3]

# 4. Remove an item at a certain index from a list
item = my_list[1]  # getting item
del my_list[1]
# my_list is now [1]

# Re-assign for the next examples
my_list = [1, 2]

# 5. Lambda map function on a list (e.g., add 1 to each item)
mapped_list = list(map(lambda x: x + 1, my_list))
# mapped_list is now [2, 3]

# Re-assign for the next example
my_list = [1, 2, 3, 4, 5]

# 6. Lambda filter function on a list (e.g., return odd numbers only)
filtered_list = list(filter(lambda x: x % 2 != 0, my_list))
# filtered_list is now [1, 3, 5]
```

## Set

```Ask chatGPT
show me how you can use a Set in python, i want
create  - create a set in one line, with 2 values
get  - get a value from a set
add - add an item to a set
update - update an item in a set
remove - remove an item from a set
```

```python
# Create a set
my_set = {1, 2}
print(f"Initial set: {my_set}")  # Output: {1, 2}

# Get a value from a set - you cannot directly access elements by index
value = 1
if value in my_set:
    print(f"{value} is in the set")  # Output: 1 is in the set
else:
    print(f"{value} is not in the set")

# Add an item to a set
my_set.add(3)
print(f"Set after adding 3: {my_set}")  # Output: {1, 2, 3}

# Update an item in a set (remove 2 and add 4) - does not support updating
my_set.remove(2)
my_set.add(4)
print(f"Set after updating 2 to 4: {my_set}")  # Output: {1, 3, 4}

# Remove an item from a set
my_set.remove(3)
print(f"Set after removing 3: {my_set}")  # Output: {1, 4}

# Discard an item (4) from a set
my_set.discard(4)
print(f"Set after discarding 4: {my_set}")  # Output: {1}

```

```python
set1 = {'Jenny', 26, 'Parker', 'Parker', 10.5}  # use {}, not []
print(set1)  # prints {10.5, 26, 'Jenny', 'Parker'} # auto sorting
```

## Dictionary

```Ask chatGPT
* create - create a dictionary and assign 2 values {'x': 1, 'y': 2} in one line
* add - add an item to a dictionary
* get - get an item from a dictionary
* remove - remove an item from a dictionary
* keys - get all the keys from a dictionary
* values - get all the values from a dictionary
* mapping - lambda map function on a dictionary, so that each value `+1`
* filter - lambda filter function on a dictionary, e.g. return entries that are odd numbers
```

```python
# 1. Create a dictionary and assign 2 values [x: 1, y: 2] in one line
my_dict = {'x': 1, 'y': 2}

# 2. Add an item to a dictionary
my_dict['z'] = 3
# my_dict is now {'x': 1, 'y': 2, 'z': 3}

# 3. Get an item from a dictionary
value = my_dict['x']
# value is 1

# 4. Remove an item from a dictionary
del my_dict['y']
# my_dict is now {'x': 1, 'z': 3}

# 5. Get all the keys from a dictionary
keys = list(my_dict.keys())
# keys is ['x', 'z']

# 6. Get all the values from a dictionary
values = list(my_dict.values())
# values is [1, 3]

# 7. Lambda map function on a dictionary (each value +1)
mapped_dict = {k: v + 1 for k, v in my_dict.items()}
# mapped_dict is {'x': 2, 'z': 4}

# 8. Lambda filter function on a dictionary (return entries that are odd numbers)
filtered_dict = {k: v for k, v in my_dict.items() if v % 2 != 0}
# filtered_dict is {'x': 1, 'z': 3}
```

The following are the same

```python
my_dict = {'x': 1, 'y': 2}


### Approach 1
def complex_operation(x):
    return x ** 2 + 3


mapped_dict1 = {k: complex_operation(v) for k, v in my_dict.items()}

### Approach 2
### The keyword `lambda` makes an inline function
mapped_dict2 = {k: (lambda x: x ** 2 + 3)(v) for k, v in my_dict.items()}
```

## Common Functions

### Built-In Python Functions:

* print()
* type()
* str()
* int()
* float()
* input()
* round()
* sorted()
* len()
* range()
* list()
* min()
* max()
* sum()
* zip()
* bin()
* hex()
* set()
* bool()
* super()

### String Methods:

* .upper()
* .lower()
* .title()
* .strip()
* .count()
* .join()
* .startswith()
* .replace()
* .split()

### Lists Methods:

* .append()
* .insert()
* .pop()
* .remove()
* .sort()
* .reverse()
* .copy()
* .index()

### Dictionary Methods:

* .items()
* .keys()
* .values()
* .most_common()

### And External Libraries:

* math
* datetime
* cmath
* random
* collections
* time
* matplotlib
* tkinter
