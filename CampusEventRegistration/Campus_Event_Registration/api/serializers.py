from rest_framework import serializers
from .models import Events, EventRegistration, Users

class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'
        read_only_fields = ['organizer', 'created_at', 'updated_at']


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['id', 'full_name', 'roll_number', 'university_email', 'status', 'waitlist_position']

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'