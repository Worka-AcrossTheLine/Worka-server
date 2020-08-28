from .models import User
from .serializers import SignupSerializer
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.
def create_user():
    User.objects.create_user(
        username="testcase", email="testcase@test.com", password="strong_password"
    )
    return None


class AccountsTestCase(APITestCase):
    def login_user(self):
        data = {
            "username": "testcase",
            "password": "strong_password",
        }

        create_user()
        user = self.client.post("/accounts/login/", data=data)
        token = user.data["token"]

        return token

    def test_signup(self):
        data = {
            "username": "testcase",
            "email": "testcase@test.com",
            "password": "strong_password",
        }

        response = self.client.post("/accounts/signup/", data=data)
        self.assertIn("token", response.data)
        self.assertIn("pk", response.data)
        self.assertIn("username", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        data = {
            "username": "testcase",
            "password": "strong_password",
        }

        create_user()
        response = self.client.post("/accounts/login/", data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_forgot_username(self):
        create_user()

        response = self.client.post(
            "/accounts/forgot-username/", data={"email": "wrongemail@test.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(
            "/accounts/forgot-username/", data={"email": "testcase@test.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("username", response.data)
        self.assertIn("***", response.data.get("username", ""))

    def test_tendency(self):
        token = self.login_user()

        response = self.client.patch(
            "/accounts/tendency/",
            data={"mbti": "ENFJ"},
            HTTP_AUTHORIZATION="JWT " + token,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.patch(
            "/accounts/tendency/", data={}, HTTP_AUTHORIZATION="JWT " + token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_passwword(self):
        token = self.login_user()

        data = {
            "old_password": "strong_password",
            "new_password": "new_strong_password",
        }

        response = self.client.patch(
            "/accounts/password/", data=data, HTTP_AUTHORIZATION="JWT " + token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "old_password": "wrong_password",
            "new_password": "new_strong_password",
        }
        response = self.client.patch(
            "/accounts/password/", data=data, HTTP_AUTHORIZATION="JWT " + token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
