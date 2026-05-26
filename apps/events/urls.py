from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    TagViewSet,
    EventViewSet,
    RegistrationViewSet,
    ReviewViewSet,
)

# Main router
router = DefaultRouter()
router.register('events', EventViewSet, basename='event')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')

# Manual nested routes for registrations and reviews
# /api/events/{event_pk}/registrations/
# /api/events/{event_pk}/reviews/

registration_list = RegistrationViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
registration_detail = RegistrationViewSet.as_view({
    'patch': 'partial_update',
    'delete': 'destroy',
})

review_list = ReviewViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
review_detail = ReviewViewSet.as_view({
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('', include(router.urls)),

    # Nested: registrations under an event
    path(
        'events/<int:event_pk>/registrations/',
        registration_list,
        name='event-registration-list'
    ),
    path(
        'events/<int:event_pk>/registrations/<int:pk>/',
        registration_detail,
        name='event-registration-detail'
    ),

    # Nested: reviews under an event
    path(
        'events/<int:event_pk>/reviews/',
        review_list,
        name='event-review-list'
    ),
    path(
        'events/<int:event_pk>/reviews/<int:pk>/',
        review_detail,
        name='event-review-detail'
    ),
]
