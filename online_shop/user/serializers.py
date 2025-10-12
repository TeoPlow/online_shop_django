from rest_framework import serializers
from .models import (
    Image,
    User,
)


class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор изображения"""

    class Meta:
        model = Image
        fields = ["src", "alt"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя"""

    avatar = ImageSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "fullName", "email", "phone", "avatar"]
