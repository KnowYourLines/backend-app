from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from lines.models import Script
from lines.permissions import IsOwner
from lines.serializers import ScriptSerializer, UserSerializer


class ScriptsViewSet(viewsets.ModelViewSet):

    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
