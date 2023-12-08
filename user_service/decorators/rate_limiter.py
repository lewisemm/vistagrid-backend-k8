import functools

from flask import g


def rate_limit(limit):
    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            with g.limiter.limit(limit):
                return func(*args, **kwargs)
        return wrapper_decorator
    return decorator