from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book


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


class BookModelTests(TestCase):
    def setUp(self) -> None:
        self.book_data = {
            "title": "Test book",
            "author": "Name Surname",
            "cover": "Hard",
            "total_amount": 25,
            "daily_fee": 0.10,
        }

    def test_book_str_is_title_author(self):
        book = Book.objects.create(**self.book_data)
        expected_str = (
            f"{self.book_data['title']} ({self.book_data['author']})"
        )

        self.assertEqual(str(book), expected_str)
