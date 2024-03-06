import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User
from users.serializers import (
    UserDetailSerializer,
    UserSerializer,
    UserListSerializer,
)

USER_LIST_URL = reverse("users:user-list")
USER_DETAIL_1_URL = reverse("users:user-detail", kwargs={"pk": 1})
USER_DETAIL_2_URL = reverse("users:user-detail", kwargs={"pk": 2})
USER_DETAIL_ME_URL = reverse("users:user-detail", kwargs={"pk": "me"})


def get_sample_user(**params) -> User:
    num_users = User.objects.count()
    defaults = {
        "username": f"user{num_users}",
        "password": "samplepass",
        "email": f"user{num_users}@user.com",
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)

    return User.objects.create_user(**defaults)


class UnauthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_user_list_auth_required(self):
        res = self.client.get(USER_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail_auth_required(self):
        res = self.client.get(USER_DETAIL_1_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="testpass",
        )
        self.client.force_authenticate(self.user)

    def test_get_user_list_forbidden(self):
        res = self.client.get(USER_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_other_user_detail_forbidden(self):
        get_sample_user()
        res = self.client.get(USER_DETAIL_2_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_own_detail(self):
        res = self.client.get(USER_DETAIL_1_URL)
        serializer = UserDetailSerializer(self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_own_detail_by_me_pk(self):
        res = self.client.get(USER_DETAIL_ME_URL)
        serializer = UserDetailSerializer(self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_put_own_detail(self):
        payload = {"username": "new_username", "password": "new_password"}
        json_data = json.dumps(payload)

        res = self.client.put(
            USER_DETAIL_1_URL, json_data, content_type="application/json"
        )
        user = get_user_model().objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], payload["username"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_put_other_user_detail_forbidden(self):
        get_sample_user()
        payload = {"username": "new_username", "password": "new_password"}
        json_data = json.dumps(payload)

        res = self.client.put(
            USER_DETAIL_2_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_new_user_forbidden(self):
        payload = {
            "username": "new_username",
            "email": "test@email.com",
            "password": "new_password",
        }
        json_data = json.dumps(payload)

        res = self.client.put(
            USER_LIST_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_forbidden(self):
        get_sample_user()

        res = self.client.delete(USER_DETAIL_2_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_admin_user", password="testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_get_user_list(self):
        get_sample_user()

        res = self.client.get(USER_LIST_URL)
        users = get_user_model().objects.all()
        serializer = UserListSerializer(users, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_user_list(self):
        user2 = get_sample_user(first_name="Jessika")
        user3 = get_sample_user()

        res = self.client.get(USER_LIST_URL, {"search": "Es"})
        serializer1 = UserListSerializer(self.user, many=False)
        serializer2 = UserListSerializer(user2, many=False)
        serializer3 = UserListSerializer(user3, many=False)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.json()["results"])
        self.assertIn(serializer2.data, res.json()["results"])
        self.assertNotIn(serializer3.data, res.json()["results"])

    def test_get_other_user_detail(self):
        user = get_sample_user()
        res = self.client.get(USER_DETAIL_2_URL)

        serializer = UserDetailSerializer(user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_own_detail(self):
        res = self.client.get(USER_DETAIL_1_URL)
        serializer = UserDetailSerializer(self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_put_own_detail(self):
        payload = {"username": "new_username", "password": "new_password"}
        json_data = json.dumps(payload)

        res = self.client.put(
            USER_DETAIL_1_URL, json_data, content_type="application/json"
        )
        user = get_user_model().objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], payload["username"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_put_other_user_detail_forbidden(self):
        get_sample_user()
        payload = {"username": "new_username", "password": "new_password"}
        json_data = json.dumps(payload)

        res = self.client.put(
            USER_DETAIL_2_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_new_user_forbidden(self):
        payload = {
            "username": "new_username",
            "email": "test@email.com",
            "password": "new_password",
        }
        json_data = json.dumps(payload)

        res = self.client.put(
            USER_LIST_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_forbidden(self):
        get_sample_user()

        res = self.client.delete(USER_DETAIL_2_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
