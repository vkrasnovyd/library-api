from django.db import models
from django.urls import reverse

from settings import BASE_URL

BOOK_COVER_CHOICES = [
    ("H", "Hard"),
    ("S", "Soft"),
]


class Book(models.Model):
    title = models.CharField(max_length=150)
    author = models.CharField(max_length=150)
    cover = models.CharField(choices=BOOK_COVER_CHOICES, max_length=1)
    total_amount = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(default=0, decimal_places=2, max_digits=4)

    def __str__(self):
        return f"{self.title} ({self.author})"

    def save(self, *args, **kwargs):
        if not self.id:
            self.inventory = self.total_amount
        else:
            num_borrowed_books = self.borrowings.count()
            self.inventory = self.total_amount - num_borrowed_books

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("books:book-detail", kwargs={"pk": self.id})

    def get_full_absolute_url(self):
        return f"{BASE_URL}{self.get_absolute_url()}"
