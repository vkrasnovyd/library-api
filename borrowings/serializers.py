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
