from django.utils.http import urlencode
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse


def reverse_with_params(*args, **kwargs):
    params = kwargs.pop("params", {})
    url = reverse(*args, **kwargs)
    if params:
        url += "?" + urlencode(params)
    return url


class ApiRootView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            200: inline_serializer(
                name="ApiRootResponse",
                fields={
                    "Auth endpoints": serializers.URLField(),
                    "Managing own profile endpoints": serializers.URLField(),
                    "Retrieving users and posts endpoints": serializers.URLField(),
                },
            )
        }
    )
    def get(self, request, format=None):
        """
        Root endpoint with links to the key endpoints.
        """

        response_data = {
            "Documentation": {
                "Schema": reverse(
                    "schema", request=request, format=format
                ),
                "Swagger documentation": reverse(
                    "swagger", request=request, format=format
                ),
                "Redoc documentation": reverse(
                    "redoc", request=request, format=format
                ),
            },
            "User endpoints": {
                "My profile": reverse(
                    "users:user-detail",
                    request=request,
                    format=format,
                    kwargs={"pk": "me"},
                ),
                "My active borrowings": reverse_with_params(
                    "borrowings:borrowing-list",
                    request=request,
                    format=format,
                    params={"is_active": "True", "user_id": request.user.id},
                ),
            },
        }

        if request.user.is_staff:
            response_data.update(
                {
                    "Admin endpoints": {
                        "Books": reverse(
                            "books:book-list", request=request, format=format
                        ),
                        "Users": reverse(
                            "users:user-list", request=request, format=format
                        ),
                        "Borrowings": reverse(
                            "borrowings:borrowing-list",
                            request=request,
                            format=format,
                        ),
                    }
                }
            )
        return Response(response_data)
