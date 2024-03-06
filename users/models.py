from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from settings import BASE_URL


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True)

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse("users:user-detail", kwargs={"pk": self.id})

    def get_full_absolute_url(self):
        return f"{BASE_URL}{self.get_absolute_url()}"
