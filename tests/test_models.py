from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book

SAMPLE_BOOK_DATA = {
    "title": "Test book",
    "author": "Name Surname",
    "cover": "Hard",
    "total_amount": 25,
    "daily_fee": 0.10,
}


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
    def test_book_str_is_title_author(self):
        book_data = SAMPLE_BOOK_DATA
        book = Book.objects.create(**book_data)
        expected_str = f"{book_data['title']} ({book_data['author']})"

        self.assertEqual(str(book), expected_str)
