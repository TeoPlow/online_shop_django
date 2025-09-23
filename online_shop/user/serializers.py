from rest_framework import serializers
from .models import (
    Image,
    User,
)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["src", "alt"]


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "fullName", "email", "phone", "avatar"]
