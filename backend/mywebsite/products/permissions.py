from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    All users can view.
    """

    def has_permission(self, request, view):
        # Allow any user to read (GET, HEAD or OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow admin users to perform write actions
        return request.user and request.user.is_staff
    
    

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to edit objects.
    All users can view.
    """

    def has_permission(self, request, view):
        # Allow any user to read (GET, HEAD or OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow authenticated users to perform write actions
        return request.user and request.user.is_authenticated
