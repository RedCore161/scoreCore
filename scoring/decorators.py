from functools import wraps

# Dictionary to store counts of function calls
call_counts = {}


def count_calls(func):
    """
    Decorator that counts the number of times a function is called.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Increment the function call count
        call_counts[func.__name__] = call_counts.get(func.__name__, 0) + 1
        return func(*args, **kwargs)

    return wrapper
