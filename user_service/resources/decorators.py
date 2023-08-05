import functools

from flask_jwt_extended import get_jwt_identity


def is_owner(func):
    """
    Compares `user_id` in JWT payload belongs to the resource id that is being
    accessed.
    """
    @functools.wraps(func)
    def wrapper_is_owner(*args, **kwargs):
        current_user = get_jwt_identity()
        if int(current_user) == kwargs['user_id']:
            value = func(*args, **kwargs)
            return value
        return {'error': 'Unauthorized access.'}, 403
    return wrapper_is_owner
