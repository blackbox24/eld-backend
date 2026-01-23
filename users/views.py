from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.http.request import HttpRequest
from guardian.shortcuts import get_objects_for_user
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from .serializers import UserSerializer

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

User = get_user_model()


@api_view(["GET"])
def get_users(request: HttpRequest) -> Response:
    data: QuerySet = get_objects_for_user(
        request.user, "users.view_customuser", accept_global_perms=False
    )
    users = UserSerializer(data).data
    return Response({"users": users}, status=HTTP_200_OK)


@api_view(["GET"])
def get_single_user(request: HttpRequest, id: int) -> Response:
    try:
        data: QuerySet = get_objects_for_user(
            request.user, "users.view_customuser", accept_global_perms=False
        )
    except User.DoesNotExist:
        return Response({"data": "user not found"}, status=HTTP_404_NOT_FOUND)
    return Response({"data": data}, status=HTTP_200_OK)
