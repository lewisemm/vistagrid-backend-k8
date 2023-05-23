from rest_framework import authentication, exceptions

from apiv1 import utils


class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        Customizes authentication by fetching the owner_id from the "Owner-Id"
        header. This value has been passed down to the API from nginx where it
        has been extracted from a validated JWT.
        This functionality guarantees that an "Owner-Id" header has to be
        present and it has to have a valid (int) value, else authentication will
        fail.
        If valid, subsequent request.user and request.auth attributes will
        contain the int value of owner_id for use in other areas of the app e.g.
        applying permissions.
        """
        current_user_id = request.headers.get('Owner-Id', None)
        if not (utils.owner_id_header_is_valid(current_user_id)):
            raise exceptions.AuthenticationFailed(
                'Invalid value for "Owner-Id" header.')
        current_user_id = int(current_user_id)
        return (current_user_id, current_user_id)

    def authenticate_header(self, request):
        """
        Returns the value of the "WWW-Authenticate" header that should be present
        with every Http 401 response.
        """
        return 'Bearer'
