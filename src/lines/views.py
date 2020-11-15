from rest_framework import viewsets

from lines.models import Script
from lines.serializers import ScriptSerializer


class ScriptsViewSet(viewsets.ModelViewSet):

    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
