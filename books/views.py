from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from books.models import Book
from books.serializers import (
    BookListSerializer,
    BookDetailSerializer,
    BookCreateUpdateSerializer,
)
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
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
                if is_available == "true":
                    queryset = queryset.filter(inventory__gt=0)
                elif is_available == "false":
                    queryset = queryset.filter(inventory__exact=0)

        return queryset

    def get_serializer_class(self):

        if self.action == "list":
            return BookListSerializer

        if self.action in ["create", "update", "partial_update"]:
            return BookCreateUpdateSerializer

        return BookDetailSerializer

    @action(
        methods=["GET"],
        detail=True,
        url_path="borrow",
        permission_classes=(IsAuthenticated,),
    )
    def borrow_toggle(self, request, pk=None):
        book = Book.objects.get(id=pk)

        if book.inventory > 0:
            user = request.user
            borrowing = Borrowing.objects.create(user=user, book=book)
            book.save()
            serializer = BorrowingSerializer(borrowing, many=False)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {
                "error": "There are no copies of this book available for borrowing."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
