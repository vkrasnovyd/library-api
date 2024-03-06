from rest_framework import mixins, viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
from paginators import Pagination
from permissions import IsUserAdminOrOwnInstancesAccessOnly


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BorrowingSerializer
    permission_classes = (IsUserAdminOrOwnInstancesAccessOnly,)
    pagination_class = Pagination

    def get_queryset(self):
        queryset = Borrowing.objects.all()

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
