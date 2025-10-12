import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)
from .utils import parse
from .models import Image
from .serializers import UserProfileSerializer
from django.contrib.auth.models import AbstractUser


log = logging.getLogger(__name__)

User = get_user_model()


class SignInView(APIView):
    """Вьюха для входа пользователя в аккаунт"""

    def post(self, request):
        # Парсю кривые данные от фронта
        data = parse(request)
        if not data:
            log.warning("Sign in failed: invalid data format")
            return Response({"error": "Invalid data"}, HTTP_400_BAD_REQUEST)

        # Провожу авторизацию
        username = data.get("username")
        password = data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log.info(f'User "{username}" signed in')
            return Response({"message": "Signed in"}, HTTP_200_OK)
        log.warning(f'Sign in failed for user "{username}"')
        return Response({"error": "Invalid credentials"}, HTTP_400_BAD_REQUEST)


class SignUpView(APIView):
    """Вьюха для регистрации пользователя"""

    def post(self, request):
        # Парсю кривые данные от фронта
        data = parse(request)
        if not data:
            log.warning("Sign up failed: invalid data format")
            return Response({"error": "Invalid data"}, HTTP_400_BAD_REQUEST)

        # Проверяю нужные поля
        name = data.get("name")
        username = data.get("username")
        password = data.get("password")
        if not all([name, username, password]):
            log.warning(
                f'Sign up failed: missing fields for user "{username}"'
            )
            return Response({"error": "Missing fields"}, HTTP_400_BAD_REQUEST)

        # Проверяю уникальность логина
        if User.objects.filter(username=username).exists():
            log.warning(
                f'Sign up failed: username "{username}" already exists'
            )
            return Response(
                {"error": "Username already exists"}, HTTP_400_BAD_REQUEST
            )

        # Создаю пользователя
        User.objects.create_user(
            username=username, password=password, fullName=name, email=username
        )
        log.info(f'User "{username}" signed up')
        return Response({"message": "Signed up"}, HTTP_200_OK)


class SignOutView(APIView):
    """Вьюха для выхода пользователя из аккаунта"""

    def post(self, request):
        """Выход пользователя из аккаунта"""
        logout(request)
        log.info(f'User "{request.user}" signed out')
        return Response({"message": "Signed out"}, HTTP_200_OK)


class ProfileView(APIView):
    """Вьюха для профиля пользователя"""

    def get(self, request):
        """Получение данных профиля пользователя"""
        log.info(f"Profile data requested for user: {request.user}")
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        """Обновление данных профиля пользователя"""
        data = request.data.copy()

        # Убираю аватар, так как он меняется отдельно
        data.pop("avatar", None)

        # Обновляю профиль
        serializer = UserProfileSerializer(
            request.user, data=data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            log.info(f"Profile updated for user: {request.user}")
            return Response(serializer.data)
        log.warning(
            "Profile update failed for user: %d errors: %d",
            request.user.id, serializer.errors
        )
        return Response(serializer.errors, status=400)


class ProfilePasswordView(APIView):
    """Вьюха для изменения пароля пользователя"""

    def post(self, request):
        """Изменение пароля пользователя"""
        user: AbstractUser = request.user
        current = request.data.get("currentPassword")
        new = request.data.get("newPassword")
        if not user.check_password(current):
            log.warning(
                f"Password change failed for user: {user} (wrong password)"
            )
            return Response({"error": "Wrong current password"}, status=400)
        user.set_password(new)
        user.save()
        log.info(f"Password updated for user: {user}")
        return Response({"message": "Password updated"}, HTTP_200_OK)


class ProfileAvatarView(APIView):
    """Вьюха для изменения аватара пользователя"""

    def post(self, request):
        user: AbstractUser = request.user

        # Проверяю наличие файла с аватаром
        avatar_file = request.FILES.get("avatar")
        if not avatar_file:
            log.warning(f"Avatar update failed for user: {user} (no file)")
            return Response({"error": "No avatar file"}, status=400)

        # Добавляю изображение аватара в БД и обновляю профиль
        image = Image.objects.create(src=avatar_file)
        user.avatar = image
        user.save()
        log.info(f"Avatar updated for user: {user}")
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
