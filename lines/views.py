from rest_framework import viewsets, permissions, mixins

from lines.helpers import presigned_upload_url
from lines.models import Script
from lines.permissions import IsOwner
from lines.serializers import (
    ScriptSerializer,
    UploadSerializer,
    UploadParamSerializer,
)


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
