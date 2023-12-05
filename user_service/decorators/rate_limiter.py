import functools

from flask import g


def jwt_limiter(func):
    @functools.wraps(func)
    def wrapper_jwt_limiter(*args, **kwargs):
        # TODO: Rate limit is currently hard coded. Ideal solution would be to
        # pass in the rate limit as a string argument to this decorator.
        # However, accepting multiple arguments (changing jwt_limiter signature
        # to jwt_limiter(*func)) will cause the decorator to run outside the
        # flask application context.
        # This means that we will not be able to access attributes inside the
        # "g" namespace (where the limiter has been stored.)
        # The `with g.limiter.limit` line below will result to a RuntimeError
        with g.limiter.limit('2/15 minutes'):
            return func(*args, **kwargs)
    return wrapper_jwt_limiter
