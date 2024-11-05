from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True  # Permite a cualquiera registrarse
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)

class IsNormalUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_superuser)