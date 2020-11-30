from functools import wraps

import jwt
from django.http import JsonResponse
from rest_framework import viewsets, permissions, mixins

from lines.helpers import presigned_upload_url
from lines.models import Script
from lines.permissions import IsOwner
from lines.serializers import (
    ScriptSerializer,
    UploadSerializer,
    UploadParamSerializer,
)


def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header"""
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """

    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse(
                {"message": "You don't have access to this resource"}
            )
            response.status_code = 403
            return response

        return decorated

    return require_scope


class ScriptsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class GetUploadUrlViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = UploadSerializer
    lookup_field = "object_name"
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        query_params = UploadParamSerializer(data=self.kwargs)
        query_params.is_valid(raise_exception=True)
        result = presigned_upload_url(query_params.validated_data["object_name"])
        return result
