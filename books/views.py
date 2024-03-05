from rest_framework import viewsets

from books.models import Book
from books.serializers import (
    BookListSerializer,
    BookSerializer,
    BookCreateUpdateSerializer,
)
from paginators import Pagination
from permissions import IsAdminUserOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = Pagination
    queryset = Book.objects.all()

    def get_serializer_class(self):

        if self.action == "list":
            return BookListSerializer

        if self.action in ["create", "update", "partial_update"]:
            return BookCreateUpdateSerializer

        return BookSerializer
