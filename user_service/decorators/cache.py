import functools
import os
import redis


CACHE_CONNECTION = {}

def get_redis_connection(func):
    @functools.wraps(func)
    def wrapper_redis_connection(*args, **kwargs):
        if CACHE_CONNECTION.get('redis') == None:
            CACHE_CONNECTION['redis'] = redis.Redis(
                host=os.environ['REDIS_HOST'],
                port=os.environ['REDIS_PORT'],
                decode_responses=True
            )
        kwargs['redis_conn'] = kwargs.get('redis_conn', None) or CACHE_CONNECTION
        return func(*args, **kwargs)
    return wrapper_redis_connection
