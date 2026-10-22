from contextlib import contextmanager
from typing import Iterator


class Database1:
    def __enter__(self):
        print("1. Opening database1")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"3. Database1 __exit__ called with exception: {exc_type}")
        self.close()

    def close(self):
        print("4. Closing database1")


def example_database1_success():
    print("=== Database1 Success Example ===")
    with Database1() as db:
        print(f"2. Working with database1... {db}")
    print("Context manager finished\n")


def example_database1_error():
    print("=== Database1 Error Example ===")
    try:
        with Database1() as db:
            print(f"2. Working with database1... {db}")
            raise ValueError("Simulated database error")
    except ValueError as e:
        print(f"5. Caught error: {e}")
    print("6. Context manager finished\n")


def example_database1_error_reraise():
    print("=== Database1 Error and Reraise Example ===")
    try:
        with Database1() as db:
            print(f"2. Working with database1... {db}")
            raise ValueError("Simulated database error")
    except ValueError as e:
        print(f"5. Caught error: {e}")
        raise  # reraise
    print("NOT RUN - Context manager finished\n")


#############


class Database2:
    def close(self):
        print("4. Closing database2")


@contextmanager
def database2_context() -> Iterator[Database2]:
    db = Database2()
    print("1. Opening database2")
    try:
        yield db
    finally:
        print("3. Before closing database2")
        db.close()


def example_database2_success():
    print("=== Database2 Success Example ===")
    with database2_context() as db:
        print(f"2. Working with database2... {db}")
    print("5. Context manager finished\n")


def example_database2_error():
    print("=== Database2 Error Example ===")
    try:
        with database2_context() as db:
            print(f"2. Working with database2... {db}")
            raise ValueError("Simulated database error")
    except ValueError as e:
        print(f"5. Caught error: {e}")
    print("6. Context manager finished\n")


if __name__ == "__main__":
    # example_database1_success()
    # example_database1_error()

    # try:
    #     example_database1_error_reraise()
    # except Exception as e:
    #     print(f"6. Caught same error: {e}")

    # example_database2_success()
    example_database2_error()
