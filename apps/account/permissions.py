from rest_framework import permissions

class IsAnonymous(permissions.BasePermission):
    '''
    Custom permission to only allow access to anonymous user(unauthenticated users).
    '''
    message = "You do no have permission to perform this action. You are currently logged in."
    def has_permission(self, request, view):
        return not bool(request.user.is_authenticated)
    
class IsProfileOwnerOrAdmin(permissions.IsAuthenticated):
    '''
    only profile owner or admin can access it 
    '''
    message = "You don't have access to modify or view this profile"

    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user or request.user.is_staff)
