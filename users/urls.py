from django.urls import path, include
from rest_framework import routers

from users.views import CreateUserView, CreateTokenView, UserViewSet

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="user")


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("", include(router.urls)),
]


app_name = "users"
