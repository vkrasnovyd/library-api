from django.contrib.auth import get_user_model
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
