from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers

from settings import BASE_URL


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password", "is_staff")
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user with correctly encrypted password"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserListSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "detail_url")

    @staticmethod
    def get_detail_url(instance):
        return instance.get_full_absolute_url()


class UserDetailSerializer(serializers.ModelSerializer):
    active_borrowings_url = serializers.SerializerMethodField()
    num_active_borrowings = serializers.IntegerField()
    num_overdue_borrowings = serializers.IntegerField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "active_borrowings_url",
            "num_active_borrowings",
            "num_overdue_borrowings",
        )

    @staticmethod
    def get_active_borrowings_url(instance):
        user_active_borrowings_list_url = reverse("borrowings:borrowing-list")
        query_params = f"is_active=True&user_id={instance.id}"
        return f"{BASE_URL}{user_active_borrowings_list_url}?{query_params}"
