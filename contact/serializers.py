from rest_framework import serializers
from .models import ContactQuery


class ContactQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactQuery
        fields = ["id", "name", "email", "mobile", "message", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]
