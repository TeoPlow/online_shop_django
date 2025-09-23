from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)
from .utils import parse
from .models import (
    Image,
)
from .serializers import (
    UserProfileSerializer,
)
import logging

log = logging.getLogger(__name__)


User = get_user_model()


class SignInView(APIView):
    def post(self, request):
        data = parse(request)
        if not data:
            return Response({"error": "Invalid data"}, HTTP_400_BAD_REQUEST)
        username = data.get("username")
        password = data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Signed in"}, HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, HTTP_400_BAD_REQUEST)


class SignUpView(APIView):
    def post(self, request):
        data = parse(request)
        if not data:
            return Response({"error": "Invalid data"}, HTTP_400_BAD_REQUEST)
        name = data.get("name")
        username = data.get("username")
        password = data.get("password")
        if not all([name, username, password]):
            return Response({"error": "Missing fields"}, HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            username=username, password=password, fullName=name, email=username
        )
        return Response({"message": "Signed up"}, HTTP_200_OK)


class SignOutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Signed out"}, HTTP_200_OK)


class ProfileView(APIView):
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data.pop("avatar", None)
        serializer = UserProfileSerializer(
            request.user, data=data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ProfilePasswordView(APIView):
    def post(self, request):
        user = request.user
        current = request.data.get("currentPassword")
        new = request.data.get("newPassword")
        if not user.check_password(current):
            return Response({"error": "Wrong current password"}, status=400)
        user.set_password(new)
        user.save()
        return Response({"message": "Password updated"}, HTTP_200_OK)


class ProfileAvatarView(APIView):
    def post(self, request):
        user = request.user
        avatar_file = request.FILES.get("avatar")
        if not avatar_file:
            return Response({"error": "No avatar file"}, status=400)
        image = Image.objects.create(src=avatar_file)
        user.avatar = image
        user.save()
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
