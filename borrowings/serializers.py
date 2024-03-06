from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "book",
            "user",
            "is_active",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )
