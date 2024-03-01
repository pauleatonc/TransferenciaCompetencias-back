from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from applications.competencias.models import Competencia
from applications.etapas.models import (
    Etapa1,
    Etapa2,
    Etapa3,
    Etapa4,
    Etapa5,
)

from .serializers import (
    Etapa1Serializer,
    Etapa2Serializer,
    Etapa3Serializer,
    Etapa4Serializer,
    Etapa5Serializer,
)

from applications.users.permissions import IsSUBDEREOrSuperuser, is_DIPRES


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
    permission_classes = [IsSUBDEREOrSuperuser, is_DIPRES]


class  Etapa4ViewSet(viewsets.ModelViewSet):
    queryset = Etapa4.objects.all()
    serializer_class = Etapa4Serializer
    permission_classes = [IsSUBDEREOrSuperuser]


class Etapa5ViewSet(viewsets.ModelViewSet):
    queryset = Etapa5.objects.all()
    serializer_class = Etapa5Serializer
    permission_classes = [IsSUBDEREOrSuperuser, is_DIPRES]
