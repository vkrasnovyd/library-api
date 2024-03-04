from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_user_str_is_first_name_last_name(self):
        user_data = {
            "username": "john_doe",
            "password": "testpass",
            "first_name": "John",
            "last_name": "Doe",
        }

        user = get_user_model().objects.create_user(**user_data)
        expected_str = f"{user_data['first_name']} {user_data['last_name']}"

        self.assertEqual(str(user), expected_str)
