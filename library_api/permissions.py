from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUserAdminOrOwnUserProfileAccessOnly(BasePermission):
    """
    Allows access to all users to admin users
    or access to retrieving and updating own profile to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(
            (
                view.action in ["retrieve", "update"]
                and request.user
                and request.user.is_authenticated
            )
            or (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_staff
            )
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            obj == request.user
            or (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_staff
            )
        )


class IsAdminUserOrReadOnly(BasePermission):
    """
    The request is authenticated as an admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_staff)
        )


class IsUserAdminOrOwnInstancesAccessOnly(BasePermission):
    """
    Allows all users to get list and detail endpoints of their instances.
    Allows admins to get detail endpoints of all instances and create new.
    """

    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            obj.user == request.user
            or (request.user and request.user.is_staff)
        )
