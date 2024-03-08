from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils.timezone import now
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from library_api.paginators import Pagination
from library_api.permissions import IsUserAdminOrOwnUserProfileAccessOnly
from users.serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserListSerializer,
)


def annotate_user_num_borrowings(queryset):
    tomorrow = now().date() + timedelta(days=1)

    queryset = queryset.annotate(
        num_active_borrowings=Count(
            "borrowings", filter=Q(borrowings__is_active=True)
        )
    )
    queryset = queryset.annotate(
        num_overdue_borrowings=Count(
            "borrowings",
            filter=Q(borrowings__is_active=True)
            & Q(borrowings__expected_return_date__lte=tomorrow),
        )
    )
    return queryset


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsUserAdminOrOwnUserProfileAccessOnly,)
    pagination_class = Pagination
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer

        if self.action == "update":
            return UserSerializer

        return UserListSerializer

    def get_queryset(self):
        queryset = get_user_model().objects.all()

        if self.action == "list":
            search_string = self.request.query_params.get("search", None)

            if search_string:
                queryset = queryset.filter(
                    Q(username__icontains=search_string)
                    | Q(first_name__icontains=search_string)
                    | Q(last_name__icontains=search_string)
                ).distinct()

        if self.action == "retrieve":
            queryset = annotate_user_num_borrowings(queryset)

        return queryset

    def get_object(self):
        if self.kwargs.get("pk", None) == "me":
            self.kwargs["pk"] = self.request.user.pk
        return super(UserViewSet, self).get_object()

    # Only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                description="Filter by part of username, first_name or last_name (case insensitive) (ex. ?search=smit)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
