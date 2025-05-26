from rest_framework.permissions import BasePermission

class IsAdminOrAuthenticated(BasePermission):
    """
    Permission:
    - GET requests only allowed for admin users (is_staff).
    - POST requests allowed for any authenticated user.
    """

    def has_permission(self, request, view):
        user = request.user
        if request.method == 'GET':
            return bool(user and user.is_authenticated and user.is_staff)
        elif request.method == 'POST':
            return bool(user and user.is_authenticated)
        return False
