from rest_framework import viewsets

from books.models import Book
from books.serializers import (
    BookListSerializer,
    BookDetailSerializer,
    BookCreateUpdateSerializer,
)
from paginators import Pagination
from permissions import IsAdminUserOrReadOnly
from library_api.paginators import Pagination
from library_api.permissions import IsAdminUserOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = Pagination

    def get_queryset(self):
        queryset = Book.objects.all()

        if self.action == "list":
            title = self.request.query_params.get("title", None)
            author = self.request.query_params.get("author", None)
            is_available = self.request.query_params.get("is_available", None)

            if title:
                queryset = queryset.filter(title__icontains=title)

            if author:
                queryset = queryset.filter(author__icontains=author)

            if is_available is not None:
                if is_available == "True":
                    queryset = queryset.filter(inventory__gt=0)
                elif is_available == "False":
                    queryset = queryset.filter(inventory__exact=0)

        return queryset

    def get_serializer_class(self):

        if self.action == "list":
            return BookListSerializer

        if self.action in ["create", "update", "partial_update"]:
            return BookCreateUpdateSerializer

        return BookDetailSerializer
