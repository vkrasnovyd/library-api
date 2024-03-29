from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("book", "user")


class BorrowingListSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField()
    book = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "is_active",
            "is_overdue",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "detail_url",
        )

    @staticmethod
    @extend_schema_field(OpenApiTypes.URI_TPL)
    def get_detail_url(instance):
        return instance.get_full_absolute_url()


class BorrowingDetailSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField()
    book = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "is_active",
            "is_overdue",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )
