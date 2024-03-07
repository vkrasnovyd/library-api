import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import (
    BookDetailSerializer,
    BookListSerializer,
)
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer

BOOK_LIST_URL = reverse("books:book-list")
BOOK_DETAIL_URL = reverse("books:book-detail", kwargs={"pk": 1})
BOOK_BORROW_TOGGLE_URL = reverse("books:book-borrow-toggle", kwargs={"pk": 1})


SAMPLE_BOOK_DATA = {
    "title": "Another book",
    "author": "John Doe",
    "cover": "S",
    "total_amount": 10,
    "daily_fee": "0.25",
}


def get_sample_book(**params) -> Book:
    defaults = {
        "title": "Sample book",
        "author": "Name Surname",
        "cover": "H",
        "total_amount": 25,
        "daily_fee": "0.10",
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_book_list(self):
        get_sample_book()
        get_sample_book(title="Another book")

        res = self.client.get(BOOK_LIST_URL)
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_get_book_detail(self):
        book = get_sample_book()

        res = self.client.get(BOOK_DETAIL_URL)
        serializer = BookDetailSerializer(book, many=False)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_book_auth_required(self):
        json_data = json.dumps(SAMPLE_BOOK_DATA)

        res = self.client.post(
            BOOK_LIST_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_book_auth_required(self):
        get_sample_book()
        json_data = json.dumps(SAMPLE_BOOK_DATA)

        res = self.client.put(
            BOOK_DETAIL_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_auth_required(self):
        get_sample_book()

        res = self.client.delete(BOOK_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_book_borrow_toggle_auth_required(self):
        book = get_sample_book()

        res = self.client.get(BOOK_BORROW_TOGGLE_URL, args={"pk": book.id})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="testpass",
        )
        self.client.force_authenticate(self.user)

    def test_post_book_forbidden(self):
        json_data = json.dumps(SAMPLE_BOOK_DATA)

        res = self.client.post(
            BOOK_LIST_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_book_forbidden(self):
        get_sample_book()
        json_data = json.dumps(SAMPLE_BOOK_DATA)

        res = self.client.put(
            BOOK_DETAIL_URL, json_data, content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        get_sample_book()

        res = self.client.delete(BOOK_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_borrow_toggle(self):
        book = get_sample_book()

        res = self.client.get(BOOK_BORROW_TOGGLE_URL, args={"pk": book.id})
        borrowing = Borrowing.objects.get(id=1)
        serializer = BorrowingSerializer(borrowing, many=False)
        book = Book.objects.get(id=book.id)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(book.inventory, book.total_amount - 1)

    def test_book_borrow_toggle_returns_bad_request_if_book_inventory_is_zero(
        self,
    ):
        book = get_sample_book(total_amount=0)

        res = self.client.get(BOOK_BORROW_TOGGLE_URL, args={"pk": book.id})
        expected_error_message = (
            "There are no copies of this book available for borrowing."
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["error"], expected_error_message)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_admin_user",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_post_book(self):
        json_data = json.dumps(SAMPLE_BOOK_DATA)

        res = self.client.post(
            BOOK_LIST_URL, json_data, content_type="application/json"
        )
        book = Book.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key, value in SAMPLE_BOOK_DATA.items():
            self.assertEqual(res.data[key], value)
        self.assertEqual(book.inventory, SAMPLE_BOOK_DATA["total_amount"])

    def test_put_book_without_active_borrowings(self):
        book = get_sample_book()
        json_data = json.dumps(SAMPLE_BOOK_DATA)

        res = self.client.put(
            BOOK_DETAIL_URL, json_data, content_type="application/json"
        )
        book = Book.objects.get(id=book.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in SAMPLE_BOOK_DATA.items():
            self.assertEqual(res.data[key], value)
        self.assertEqual(book.inventory, SAMPLE_BOOK_DATA["total_amount"])

    def test_put_book_with_active_borrowings(self):
        book = get_sample_book()
        Borrowing.objects.create(user=self.user, book=book)
        json_data = json.dumps(SAMPLE_BOOK_DATA)

        self.client.put(
            BOOK_DETAIL_URL, json_data, content_type="application/json"
        )
        book = Book.objects.get(id=book.id)

        self.assertEqual(book.inventory, SAMPLE_BOOK_DATA["total_amount"] - 1)

    def test_delete_book(self):
        get_sample_book()

        res = self.client.delete(BOOK_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
