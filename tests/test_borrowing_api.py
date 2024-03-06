from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingSerializer
from borrowings.views import annotate_borrowing_is_overdue
from tests.test_book_api import get_sample_book
from tests.test_user_api import get_sample_user

BORROWING_LIST_URL = reverse("borrowings:borrowing-list")
BORROWING_DETAIL_URL = reverse("borrowings:borrowing-detail", kwargs={"pk": 1})


SAMPLE_PAYLOAD = {
    "book": 1,
    "user": 1,
}


def get_sample_borrowing(book=None, user=None, **params) -> Borrowing:
    borrow_date = now().date()

    if not user:
        user = get_sample_user()

    if not book:
        book = get_sample_book()

    defaults = {
        "borrow_date": borrow_date,
        "book": book,
        "user": user,
    }
    defaults.update(**params)

    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_borrowings_list_auth_required(self):
        res = self.client.get(BORROWING_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_borrowing_detail_auth_required(self):
        res = self.client.get(BORROWING_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="testpass",
        )
        self.client.force_authenticate(self.user)

    def test_get_borrowings_list_returns_only_own_borrowings(self):
        borrowing1 = get_sample_borrowing(user=self.user)
        borrowing2 = get_sample_borrowing(user=self.user)
        borrowing3 = get_sample_borrowing()

        res = self.client.get(BORROWING_LIST_URL)

        borrowings = annotate_borrowing_is_overdue(Borrowing.objects.all())

        serializer1 = BorrowingListSerializer(borrowings.get(id=borrowing1.id))
        serializer2 = BorrowingListSerializer(borrowings.get(id=borrowing2.id))
        serializer3 = BorrowingListSerializer(borrowings.get(id=borrowing3.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.json()["results"])
        self.assertIn(serializer2.data, res.json()["results"])
        self.assertNotIn(serializer3.data, res.json()["results"])

    def test_filter_borrowings_list_by_is_active(self):
        borrowing1 = get_sample_borrowing(user=self.user)
        borrowing2 = get_sample_borrowing(user=self.user)
        borrowing2.is_active = False
        borrowing2.save()

        res_is_active_true = self.client.get(
            BORROWING_LIST_URL, {"is_active": "True"}
        )
        res_is_active_false = self.client.get(
            BORROWING_LIST_URL, {"is_active": "False"}
        )

        borrowings = annotate_borrowing_is_overdue(Borrowing.objects.all())

        serializer1 = BorrowingListSerializer(borrowings.get(id=borrowing1.id))
        serializer2 = BorrowingListSerializer(borrowings.get(id=borrowing2.id))

        self.assertEqual(res_is_active_true.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res_is_active_true.json()["results"])
        self.assertNotIn(
            serializer2.data, res_is_active_true.json()["results"]
        )

        self.assertEqual(res_is_active_false.status_code, status.HTTP_200_OK)
        self.assertNotIn(
            serializer1.data, res_is_active_false.json()["results"]
        )
        self.assertIn(serializer2.data, res_is_active_false.json()["results"])

    def test_get_borrowing_detail(self):
        borrowing = get_sample_borrowing(user=self.user)

        res = self.client.get(BORROWING_DETAIL_URL)
        serializer = BorrowingSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_borrowing_forbidden(self):
        get_sample_borrowing(user=self.user)

        res = self.client.post(BORROWING_LIST_URL, SAMPLE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_borrowing_forbidden(self):
        get_sample_borrowing()

        res = self.client.put(BORROWING_DETAIL_URL, SAMPLE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_borrowing_forbidden(self):
        get_sample_borrowing()

        res = self.client.delete(BORROWING_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_admin_user",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_get_borrowings_list_returns_all_users_borrowings(self):
        borrowing1 = get_sample_borrowing(user=self.user)
        borrowing2 = get_sample_borrowing()

        res = self.client.get(BORROWING_LIST_URL)

        borrowings = annotate_borrowing_is_overdue(Borrowing.objects.all())

        serializer1 = BorrowingListSerializer(borrowings.get(id=borrowing1.id))
        serializer2 = BorrowingListSerializer(borrowings.get(id=borrowing2.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.json()["results"])
        self.assertIn(serializer2.data, res.json()["results"])

    def test_filter_borrowings_list_by_user_id(self):
        borrowing1 = get_sample_borrowing(user=self.user)
        borrowing2 = get_sample_borrowing()

        res = self.client.get(BORROWING_LIST_URL, {"user_id": "2"})

        borrowings = annotate_borrowing_is_overdue(Borrowing.objects.all())

        serializer1 = BorrowingListSerializer(borrowings.get(id=borrowing1.id))
        serializer2 = BorrowingListSerializer(borrowings.get(id=borrowing2.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer1.data, res.json()["results"])
        self.assertIn(serializer2.data, res.json()["results"])

    def test_post_borrowing(self):
        book = get_sample_book()

        res = self.client.post(BORROWING_LIST_URL, SAMPLE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["book"], book.id)
        self.assertEqual(res.data["user"], self.user.id)

    def test_put_borrowing_not_allowed(self):
        get_sample_borrowing()

        res = self.client.put(BORROWING_DETAIL_URL, SAMPLE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_borrowing_not_allowed(self):
        get_sample_borrowing()

        res = self.client.delete(BORROWING_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
