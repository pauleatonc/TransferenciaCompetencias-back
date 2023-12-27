from rest_framework import viewsets
from applications.competencias.models import Ambito
from .serializers import AmbitoSerializer


class AmbitoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ambito.objects.all()
    serializer_class = AmbitoSerializer
