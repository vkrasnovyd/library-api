from django.contrib.auth import get_user_model
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from settings import BASE_URL
from views import reverse_with_params


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
    @extend_schema_field(OpenApiTypes.URI_TPL)
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
    @extend_schema_field(OpenApiTypes.URI_TPL)
    def get_active_borrowings_url(instance):
        user_active_borrowings_list_url = reverse_with_params(
            "borrowings:borrowing-list",
            params={"is_active": "True", "user_id": instance.id},
        )
        return f"{BASE_URL}{user_active_borrowings_list_url}"
