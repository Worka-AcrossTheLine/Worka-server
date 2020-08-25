from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.


class AccountsTestCase(APITestCase):
    def test_signup(self):
        data = {
            "username": "testcase",
            "email": "testcase@test.com",
            "password": "strong_password",
        }

        response = self.client.post("/accounts/signup/", data=data)
        self.assertTrue(response.data["token"])
        self.assertTrue(response.data["pk"])
        self.assertTrue(response.data["username"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        pass
