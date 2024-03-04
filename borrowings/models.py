import datetime

from django.contrib.auth import get_user_model
from django.db import models

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="borrowings"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book} - {self.expected_return_date}"

    def save(self, *args, **kwargs):
        self.expected_return_date = self.borrow_date + datetime.timedelta(
            weeks=2
        )
        super().save(*args, **kwargs)
