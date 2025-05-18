from rest_framework.permissions import BasePermission, IsAuthenticated

class IsAdminOrAuthenticated(BasePermission):
    """
    Allow admins for GET and authenticated users for POST.
    """

    def has_permission(self, request, view):
        if request.method == 'GET':
            # Only admins can access GET method
            return request.user and request.user.is_staff
        elif request.method == 'POST':
            # Any authenticated user can access POST method
            return request.user and request.user.is_authenticated
        return False
