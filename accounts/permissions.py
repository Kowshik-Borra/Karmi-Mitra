from rest_framework import permissions

class IsCustomer(permissions.BasePermission):
    """
    Allows access only to customer users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'customer_profile'))


class IsWorker(permissions.BasePermission):
    """
    Allows access only to worker users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'worker_profile'))


class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to staff / admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))
