# Python Project Folder Structure

## Folder Structure

* common practice to call root source directory the same as root directory
* package names are in singular form
* test directory is commonly called `tests`

```markdown
pet_store/
├── pet_store/
│ ├── __init__.py
│ ├── main.py
│ ├── model/
│ │ ├── __init__.py
│ │ ├── pet.py
│ │ ├── owner.py
│ ├── service/
│ │ ├── __init__.py
│ │ ├── pet_service.py
│ │ ├── owner_service.py
│ ├── repository/
│ │ ├── __init__.py
│ │ ├── pet_repository.py
│ │ ├── owner_repository.py
│ ├── controller/
│ │ ├── __init__.py
│ │ ├── pet_controller.py
│ │ ├── owner_controller.py
│ ├── util/
│ │ ├── __init__.py
│ │ ├── cats/
│ │ │ ├── __init__.py
│ │ │ ├── cat_helper.py
│ │ ├── dogs/
│ │ │ ├── __init__.py
│ │ │ ├── dog_helper.py
├── tests/
│ ├── __init__.py
│ ├── model/
│ │ ├── __init__.py
│ │ ├── test_pet.py
│ │ ├── test_owner.py
│ ├── service/
│ │ ├── __init__.py
│ │ ├── test_pet_service.py
│ │ ├── test_owner_service.py
│ ├── repository/
│ │ ├── __init__.py
│ │ ├── test_pet_repository.py
│ │ ├── test_owner_repository.py
│ ├── controller/
│ │ ├── __init__.py
│ │ ├── test_pet_controller.py
│ │ ├── test_owner_controller.py
│ ├── util/
│ │ ├── __init__.py
│ │ ├── cat/
│ │ │ ├── __init__.py
│ │ │ ├── test_cat_helper.py
│ │ ├── dog/
│ │ │ ├── __init__.py
│ │ │ ├── test_dog_helper.py
├── .venv/
│ ├── ... (virtual environment files)
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── LICENSE
```

## Explanation

1. **pet_store/**: Root directory of your project.
    - **pet_store/**: Main package directory containing the application code.
        - `__init__.py`: Makes this directory a package.
        - `main.py`: Entry point of your application.
        - **model/**: Contains data models.
            - `pet.py`: Defines the Pet model.
            - `owner.py`: Defines the Owner model.
        - **service/**: Contains business logic.
            - `pet_service.py`: Contains business logic related to pets.
            - `owner_service.py`: Contains business logic related to owners.
        - **repository/**: Contains data access layer.
            - `pet_repository.py`: Handles CRUD operations for pets.
            - `owner_repository.py`: Handles CRUD operations for owners.
        - **controller/**: Contains application controllers (or handlers).
            - `pet_controller.py`: Manages pet-related endpoints.
            - `owner_controller.py`: Manages owner-related endpoints.
        - **util/**: Contains utility modules organized by topic.
            - **cats/**: Contains helper modules for cats.
                - `cat_helper.py`: Helper functions related to cats.
            - **dogs/**: Contains helper modules for dogs.
                - `dog_helper.py`: Helper functions related to dogs.
2. **tests/**: Contains all the test cases.
    - `__init__.py`: Makes this directory a package.
    - `test_pet.py`: Tests for the Pet model.
    - `test_owner.py`: Tests for the Owner model.
    - `test_pet_service.py`: Tests for Pet service.
    - `test_owner_service.py`: Tests for Owner service.
3. **.venv/**: Directory for the virtual environment (ensure this is included in `.gitignore`).
4. **.gitignore**: Specifies files and directories to be ignored by git (including `.venv`).
5. **README.md**: Provides an overview of the project.
6. **requirements.txt**: Lists project dependencies.
7. **setup.py**: Used for packaging the project.
8. **LICENSE**: The license for your project.

## .gitignore Example

Ensure the `.venv` directory is included in your `.gitignore` to avoid committing it to your repository:

```gitignore
# Virtual environment
.venv/