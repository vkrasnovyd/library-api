from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "cover",
            "total_amount",
            "inventory",
            "daily_fee",
        )


class BookCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "cover",
            "total_amount",
            "daily_fee",
        )


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("title", "author", "inventory", "daily_fee")
