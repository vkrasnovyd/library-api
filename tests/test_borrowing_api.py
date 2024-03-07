from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingSerializer
from borrowings.views import annotate_borrowing_is_overdue
from tests.test_book_api import get_sample_book
from tests.test_user_api import get_sample_user

BORROWING_LIST_URL = reverse("borrowings:borrowing-list")
BORROWING_DETAIL_URL = reverse("borrowings:borrowing-detail", kwargs={"pk": 1})
BORROWING_RETURN_TOGGLE_URL = reverse(
    "borrowings:borrowing-return-toggle", kwargs={"pk": 1}
)


SAMPLE_PAYLOAD = {
    "book": 1,
    "user": 1,
}


def get_sample_borrowing(book=None, user=None, **params) -> Borrowing:
    if not user:
        user = get_sample_user()

    if not book:
        book = get_sample_book()

    defaults = {
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

    def test_get_borrowing_return_toggle_auth_required(self):
        res = self.client.get(BORROWING_RETURN_TOGGLE_URL)

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

    def test_return_borrowing_toggle(self):
        book = get_sample_book()
        borrowing = get_sample_borrowing(book=book, user=self.user)

        res = self.client.get(BORROWING_RETURN_TOGGLE_URL)
        borrowing = Borrowing.objects.get(id=borrowing.id)
        book = Book.objects.get(id=book.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(borrowing.is_active)
        self.assertEqual(borrowing.actual_return_date, now().date())
        self.assertEqual(book.inventory, book.total_amount)

    def test_return_borrowing_toggle_when_is_active_false_returns_bad_request(
        self,
    ):
        borrowing = get_sample_borrowing(user=self.user)
        borrowing.is_active = False
        borrowing.save()

        res = self.client.get(BORROWING_RETURN_TOGGLE_URL)
        expected_error_message = "This borrowing is already returned."

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["error"], expected_error_message)

    def test_return_borrowing_toggle_accessible_only_for_own_borrowings(self):
        get_sample_borrowing()

        res = self.client.get(BORROWING_RETURN_TOGGLE_URL)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_return_borrowing_toggle_accessible_not_only_for_own_borrowings(
        self,
    ):
        get_sample_borrowing()

        res = self.client.get(BORROWING_RETURN_TOGGLE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_put_borrowing_not_allowed(self):
        get_sample_borrowing()

        res = self.client.put(BORROWING_DETAIL_URL, SAMPLE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_borrowing_not_allowed(self):
        get_sample_borrowing()

        res = self.client.delete(BORROWING_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
