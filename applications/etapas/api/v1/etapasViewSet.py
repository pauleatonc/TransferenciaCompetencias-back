from rest_framework import viewsets

from applications.etapas.models import (
    Etapa1,
    Etapa2,
    Etapa3,
    Etapa4,
    Etapa5,
)
from applications.users.permissions import IsSUBDEREOrSuperuser
from .serializers import (
    Etapa1Serializer,
    Etapa2Serializer,
    Etapa3Serializer,
    Etapa4Serializer,
    Etapa5Serializer,
)


class Etapa1ViewSet(viewsets.ModelViewSet):
    queryset = Etapa1.objects.all()
    serializer_class = Etapa1Serializer
    permission_classes = [IsSUBDEREOrSuperuser]


class  Etapa2ViewSet(viewsets.ModelViewSet):
    queryset = Etapa2.objects.all()
    serializer_class = Etapa2Serializer
    permission_classes = [IsSUBDEREOrSuperuser]


class Etapa3ViewSet(viewsets.ModelViewSet):
    queryset = Etapa3.objects.all()
    serializer_class = Etapa3Serializer
    permission_classes = [IsSUBDEREOrSuperuser]


class  Etapa4ViewSet(viewsets.ModelViewSet):
    queryset = Etapa4.objects.all()
    serializer_class = Etapa4Serializer
    permission_classes = [IsSUBDEREOrSuperuser]


class Etapa5ViewSet(viewsets.ModelViewSet):
    queryset = Etapa5.objects.all()
    serializer_class = Etapa5Serializer
    permission_classes = [IsSUBDEREOrSuperuser]
