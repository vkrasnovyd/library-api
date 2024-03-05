from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from paginators import Pagination
from permissions import IsUserAdminOrOwnUserProfileAccessOnly
from users.serializers import (
    UserSerializer,
    UserDetailSerializer,
    UserListSerializer,
)


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

        return queryset
