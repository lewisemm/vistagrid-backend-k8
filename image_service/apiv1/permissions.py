from rest_framework import permissions, exceptions

from apiv1 import utils

class OnlyOwnerCanAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, object):
        """
        Restrict photo access to photo owners at `photo-detail` route.
        """
        if not (object.owner_id == request.user):
            raise exceptions.PermissionDenied(
                "Access to this resource is restricted to owner.")
        return True
