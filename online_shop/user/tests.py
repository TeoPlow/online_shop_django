from django.test import TestCase, RequestFactory
from rest_framework.test import APITestCase
from .utils import parse
from .models import User


class UtilsTests(TestCase):
    def test_parse_valid_json(self):
        """
        Тестирование функции parse.
        """
        factory = RequestFactory()
        data = '{"name":"test","username":"user","password":"pass"}'
        request = factory.post(
            "/some-url", data, content_type="application/x-www-form-urlencoded"
        )
        request.data = {data: ""}
        result = parse(request)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["username"], "user")
        self.assertEqual(result["password"], "pass")


class AuthEndpointsTests(APITestCase):
    def test_sign_up_and_sign_in(self):
        """
        Тестирование регистрации и входа в систему.
        """
        name = "TestName"
        username = "testusername"
        password = "testpassword"

        # Sign up
        response = self.client.post(
            "/api/sign-up",
            {"name": name, "username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        # Sign in
        response = self.client.post(
            "/api/sign-in",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def test_sign_out(self):
        """
        Тестирование выхода из системы.
        """
        response = self.client.post("/api/sign-out")
        self.assertEqual(response.status_code, 200)


class ProfileEndpointsTests(APITestCase):
    def setUp(self):
        """
        Предустановка пользователя для тестирования.
        """
        self.user = User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="testpass",
            fullName="Test User",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """
        Тестирование получения профиля.
        """
        response = self.client.get("/api/profile")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "test@mail.com")

    def test_update_profile(self):
        """
        Тестирование обновления профиля.
        """
        response = self.client.post(
            "/api/profile", {"fullName": "New Name"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["fullName"], "New Name")

    def test_change_password(self):
        """
        Тестирование изменения пароля.
        """
        self.assertTrue(self.user.check_password("testpass"))
        response = self.client.post(
            "/api/profile/password",
            {"currentPassword": "testpass", "newPassword": "password_new123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("password_new123!"))
