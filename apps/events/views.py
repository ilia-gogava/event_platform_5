from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category, Tag, Event, Registration, Review
from .serializers import (
    CategorySerializer, TagSerializer,
    EventSerializer, EventWriteSerializer,
    RegistrationSerializer, ReviewSerializer,
)
from .permissions import IsOrganizer, IsOwnerOrReadOnly, IsConfirmedAttendee, IsReviewOwner
from .filters import EventFilter


# ─────────────────────────────────────────────
# Category & Tag (read-only lists)
# ─────────────────────────────────────────────

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


# ─────────────────────────────────────────────
# Events CRUD
# ─────────────────────────────────────────────

class EventViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/events/           — anyone can list events
    create: POST /api/events/           — organizers only
    retrieve: GET /api/events/{id}/     — anyone
    update: PATCH /api/events/{id}/     — event owner only
    destroy: DELETE /api/events/{id}/   — event owner only
    """
    queryset = Event.objects.select_related('organizer', 'category').prefetch_related('tags')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'created_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventWriteSerializer
        return EventSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Only organizers can create events
            return [permissions.IsAuthenticated(), IsOrganizer()]
        if self.action in ['update', 'partial_update', 'destroy']:
            # Only the event owner can edit or delete
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        # List and retrieve are public
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Automatically set the organizer to the logged-in user
        serializer.save(organizer=self.request.user)


# ─────────────────────────────────────────────
# Registrations
# ─────────────────────────────────────────────

class RegistrationViewSet(viewsets.ModelViewSet):
    """
    GET  /api/events/{event_pk}/registrations/       — list registrations (organizer)
    POST /api/events/{event_pk}/registrations/       — register for event (authenticated user)
    PATCH /api/events/{event_pk}/registrations/{id}/ — change status (organizer)
    DELETE /api/events/{event_pk}/registrations/{id}/— cancel registration (owner)
    """
    serializer_class = RegistrationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_event(self):
        event_pk = self.kwargs.get('event_pk')
        try:
            return Event.objects.get(pk=event_pk)
        except Event.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Event not found.")

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        return Registration.objects.filter(event_id=event_pk).select_related('user', 'event')

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        event = self.get_event()

        # Check if event is published
        if event.status != 'published':
            return Response(
                {'detail': 'You can only register for published events.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check capacity
        if event.is_full:
            return Response(
                {'detail': 'This event is full. No spots available.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent duplicate registration
        if Registration.objects.filter(user=request.user, event=event).exists():
            return Response(
                {'detail': 'You are already registered for this event.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration = Registration.objects.create(
            user=request.user,
            event=event,
            status='confirmed'
        )
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        registration = self.get_object()
        # Only the registration owner can cancel
        if registration.user != request.user:
            return Response(
                {'detail': 'You can only cancel your own registration.'},
                status=status.HTTP_403_FORBIDDEN
            )
        registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────
# Reviews
# ─────────────────────────────────────────────

class ReviewViewSet(viewsets.ModelViewSet):
    """
    GET  /api/events/{event_pk}/reviews/       — list reviews (anyone)
    POST /api/events/{event_pk}/reviews/       — create review (confirmed attendee only)
    PATCH /api/events/{event_pk}/reviews/{id}/ — update own review
    DELETE /api/events/{event_pk}/reviews/{id}/— delete own review
    """
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        return Review.objects.filter(event_id=event_pk).select_related('user')

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsConfirmedAttendee()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsReviewOwner()]
        return [permissions.AllowAny()]

    def get_event(self):
        event_pk = self.kwargs.get('event_pk')
        try:
            return Event.objects.get(pk=event_pk)
        except Event.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Event not found.")

    def create(self, request, *args, **kwargs):
        event = self.get_event()

        # Prevent duplicate review
        if Review.objects.filter(user=request.user, event=event).exists():
            return Response(
                {'detail': 'You have already reviewed this event.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, event=event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
