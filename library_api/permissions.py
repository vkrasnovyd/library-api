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
