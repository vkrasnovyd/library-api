from datetime import timedelta

from django.db.models import Q
from django.utils.timezone import now
from rest_framework import mixins, viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer
from paginators import Pagination
from permissions import IsUserAdminOrOwnInstancesAccessOnly


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
                    queryset = queryset.filter(user_id=user_id)

        if self.action == "list":
            is_active = self.request.query_params.get("is_active", None)

            if is_active:
                if is_active == "True":
                    queryset = queryset.filter(is_active=True)
                elif is_active == "False":
                    queryset = queryset.filter(is_active=False)

        return queryset

    def get_serializer_class(self):

        if self.action == "list":
            return BorrowingListSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(borrow_date=now().date())
