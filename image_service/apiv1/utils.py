import os
from urllib import request as req

def get_user_id_from_auth_service(token):
    """
    Takes in a token, sets it in the "Authorization" header and then sends a get
    request to the auth service.
    Returns the response from the auth service.
    """
    auth_service_url = os.environ['AUTH_SERVICE_URL']
    endpoint = '/api/user/auth'
    url = f'{auth_service_url}{endpoint}'
    print(f'url: {url}')
    request = req.Request(url)
    request.add_header('Authorization', token)
    return req.urlopen(request)

def owner_id_header_is_valid(owner_id):
    """
    Returns True of owner_id value is valid and returns False if otherwise.
    """
    if owner_id == None:
        return False
    for digit in owner_id:
        try:
            int(digit)
        except ValueError:
            return False
    return True
