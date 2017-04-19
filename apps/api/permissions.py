from rest_framework import permissions


class IsObjectOwner(permissions.BasePermission):
    """
    Makes sure the user making the request is the owner of `obj`
    """

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user_id
