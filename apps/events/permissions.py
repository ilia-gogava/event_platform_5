from rest_framework import permissions


class IsOrganizer(permissions.BasePermission):
    """
    Allows access only to users with role='organizer'.
    """
    message = "Only organizers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'organizer'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    - Safe methods (GET, HEAD, OPTIONS): allowed for everyone
    - Unsafe methods (POST, PUT, PATCH, DELETE): only the owner (organizer field)
    """
    message = "You can only modify your own events."

    def has_object_permission(self, request, view, obj):
        # Read is allowed to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write is only allowed to the owner
        return obj.organizer == request.user


class IsConfirmedAttendee(permissions.BasePermission):
    """
    Allows creating a review only if the user has a confirmed registration.
    """
    message = "You must be a confirmed attendee to leave a review."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Safe methods (listing reviews) are allowed for all
        if request.method in permissions.SAFE_METHODS:
            return True

        # For POST, check if user has a confirmed registration for this event
        event_pk = view.kwargs.get('event_pk') or view.kwargs.get('pk')
        return request.user.registrations.filter(
            event_id=event_pk,
            status='confirmed'
        ).exists()


class IsReviewOwner(permissions.BasePermission):
    """
    Only the author of the review can edit or delete it.
    """
    message = "You can only modify your own review."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
