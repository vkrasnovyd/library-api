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
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsUserAdminOrOwnInstancesAccessOnly,)
    pagination_class = Pagination
