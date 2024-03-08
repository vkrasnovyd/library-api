from datetime import timedelta

from django.db.models import Q
from django.utils.timezone import now
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from library_api.paginators import Pagination
from library_api.permissions import IsUserAdminOrOwnInstancesAccessOnly


def annotate_borrowing_is_overdue(queryset):
    tomorrow = now().date() + timedelta(days=1)
    queryset = queryset.annotate(
        is_overdue=Q(is_active=True) & Q(expected_return_date__lte=tomorrow)
    )
    return queryset


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsUserAdminOrOwnInstancesAccessOnly,)
    pagination_class = Pagination

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        queryset = annotate_borrowing_is_overdue(queryset)

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        else:
            if self.action == "list":
                user_id = self.request.query_params.get("user_id", None)

                if user_id:
                    queryset = queryset.filter(user_id=int(user_id))

        if self.action == "list":
            is_active = self.request.query_params.get("is_active", None)

            if is_active:
                if is_active == "true":
                    queryset = queryset.filter(is_active=True)
                elif is_active == "false":
                    queryset = queryset.filter(is_active=False)

        return queryset

    def get_serializer_class(self):

        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer

    @action(
        methods=["GET"],
        detail=True,
        url_path="return",
        permission_classes=(IsUserAdminOrOwnInstancesAccessOnly,),
    )
    def return_toggle(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.is_active:
            borrowing.is_active = False
            borrowing.actual_return_date = now().date()
            borrowing.save()

            # Trigger book.save() method to update book.inventory
            book = borrowing.book
            book.save()

            serializer = BorrowingSerializer(borrowing, many=False)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "This borrowing is already returned."},
            status=status.HTTP_400_BAD_REQUEST,
        )
