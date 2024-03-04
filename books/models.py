from django.db import models


BOOK_COVER_CHOICES = [
    ("H", "Hard"),
    ("S", "Soft"),
]


class Book(models.Model):
    title = models.CharField(max_length=150)
    author = models.CharField(max_length=150)
    cover = models.CharField(choices=BOOK_COVER_CHOICES, max_length=1)
    total_amount = models.PositiveIntegerField()
    daily_fee = models.DecimalField(default=0, decimal_places=2, max_digits=4)

    def __str__(self):
        return f"{self.title} ({self.author})"