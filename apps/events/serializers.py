from rest_framework import serializers
from .models import Category, Tag, Event, Registration, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class EventSerializer(serializers.ModelSerializer):
    """
    Used for listing and retrieving events.
    Shows organizer username, category name, and tag names.
    """
    organizer_username = serializers.CharField(source='organizer.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tag_names = serializers.SlugRelatedField(
        source='tags',
        many=True,
        read_only=True,
        slug_field='name'
    )
    available_spots = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description',
            'organizer', 'organizer_username',
            'category', 'category_name',
            'tags', 'tag_names',
            'status', 'event_type',
            'start_date', 'end_date',
            'location', 'max_attendees', 'available_spots',
            'created_at',
        ]
        read_only_fields = ['organizer', 'created_at']


class EventWriteSerializer(serializers.ModelSerializer):
    """
    Used for creating and updating events.
    Organizer is set automatically from request.user.
    """
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description',
            'category', 'tags',
            'status', 'event_type',
            'start_date', 'end_date',
            'location', 'max_attendees',
        ]

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError("end_date must be after start_date.")
        return data

    def validate_max_attendees(self, value):
        if value < 1:
            raise serializers.ValidationError("max_attendees must be at least 1.")
        return value


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'user', 'username', 'event', 'event_title', 'status', 'registered_at']
        read_only_fields = ['user', 'event', 'registered_at']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'event', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'event', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
