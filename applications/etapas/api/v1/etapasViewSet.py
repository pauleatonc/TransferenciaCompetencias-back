from rest_framework import permissions
from rest_framework import viewsets

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


class IsSUBDEREOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.groups.filter(name='SUBDERE').exists()


class IsDIPRESOrSUBDEREOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or \
            request.user.groups.filter(name='DIPRES').exists() or \
            request.user.groups.filter(name='SUBDERE').exists()


class ReadOnly(permissions.BasePermission):
    """
    Permiso global de solo lectura.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class CustomDIPRESPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='DIPRES').exists() and \
            request.method in permissions.SAFE_METHODS


class ReadOnlyForCompetencia(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS and \
            (obj.competencia.usuarios_dipres.filter(id=request.user.id).exists() or \
             obj.competencia.usuarios_sectoriales.filter(id=request.user.id).exists() or \
             obj.competencia.usuarios_gore.filter(id=request.user.id).exists())


class Etapa1ViewSet(viewsets.ModelViewSet):
    queryset = Etapa1.objects.all()
    serializer_class = Etapa1Serializer
    permission_classes = [IsSUBDEREOrSuperuser | ReadOnly]


class Etapa2ViewSet(viewsets.ModelViewSet):
    queryset = Etapa2.objects.all()
    serializer_class = Etapa2Serializer
    permission_classes = [IsSUBDEREOrSuperuser | ReadOnly]


class Etapa3ViewSet(viewsets.ModelViewSet):
    queryset = Etapa3.objects.all()
    serializer_class = Etapa3Serializer
    permission_classes = [IsDIPRESOrSUBDEREOrSuperuser | CustomDIPRESPermission | ReadOnlyForCompetencia]


class Etapa4ViewSet(viewsets.ModelViewSet):
    queryset = Etapa4.objects.all()
    serializer_class = Etapa4Serializer
    permission_classes = [IsSUBDEREOrSuperuser | ReadOnly]


class Etapa5ViewSet(viewsets.ModelViewSet):
    queryset = Etapa5.objects.all()
    serializer_class = Etapa5Serializer
    permission_classes = [IsDIPRESOrSUBDEREOrSuperuser | CustomDIPRESPermission | ReadOnlyForCompetencia]
