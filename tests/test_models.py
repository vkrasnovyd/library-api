import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now

from books.models import Book
from borrowings.models import Borrowing

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

    def test_setting_inventory_on_instance_creation(self):
        book_data = SAMPLE_BOOK_DATA
        book = Book.objects.create(**book_data)

        self.assertEqual(book.inventory, book.total_amount)

    def test_setting_inventory_on_instance_update_without_borrowed_books(self):
        book_data = SAMPLE_BOOK_DATA
        book = Book.objects.create(**book_data)
        new_total_amount = 30

        book.total_amount = new_total_amount
        book.save()

        self.assertEqual(book.inventory, new_total_amount)

    def test_setting_inventory_on_instance_update_with_borrowed_books(self):
        book_data = SAMPLE_BOOK_DATA
        book = Book.objects.create(**book_data)
        user = get_user_model().objects.create_user(
            username="john_doe", password="testpass"
        )
        Borrowing.objects.create(user=user, book=book, borrow_date=now().date())
        new_total_amount = 30

        book.total_amount = new_total_amount
        book.save()

        self.assertEqual(book.inventory, new_total_amount - 1)


class BorrowingModelTests(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            username="john_doe", password="testpass"
        )
        book = Book.objects.create(**SAMPLE_BOOK_DATA)
        self.borrowing_data = {
            "borrow_date": now().date(),
            "user": user,
            "book": book,
        }

    def test_borrowing_expected_return_date_is_today_plus_two_weeks(self):
        borrowing = Borrowing.objects.create(**self.borrowing_data)

        expected_result = self.borrowing_data[
            "borrow_date"
        ] + datetime.timedelta(weeks=2)

        self.assertEqual(borrowing.expected_return_date, expected_result)

    def test_borrowing_str_is_book_str_title_expected_return_date(self):
        borrowing = Borrowing.objects.create(**self.borrowing_data)

        expected_return_date = self.borrowing_data[
            "borrow_date"
        ] + datetime.timedelta(weeks=2)
        expected_str = (
            f"{self.borrowing_data['book']} - {expected_return_date}"
        )

        self.assertEqual(str(borrowing), expected_str)
