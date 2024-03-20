from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated

from applications.etapas.models import (
    Etapa1,
    Etapa2,
    Etapa3,
    Etapa4,
    Etapa5,
)
from applications.users.permissions import (
    IsSUBDEREOrSuperuser
)

from .serializers import (
    Etapa1Serializer,
    Etapa2Serializer,
    Etapa3Serializer,
    Etapa4Serializer,
    Etapa5Serializer,
)


from rest_framework.permissions import BasePermission


class IsDIPRESOrSUBDEREOrSuperuser(BasePermission):
    """
    Permite el acceso solo a usuarios que son superusuarios, pertenecen al grupo SUBDERE o al grupo DIPRES,
    y además están asignados a la misma competencia que la etapa.
    """

    def has_permission(self, request, view):
        # Permitir si es superusuario.
        if request.user and request.user.is_superuser:
            return True

        user_groups = request.user.groups.values_list('name', flat=True)
        is_subdere_or_dipres = 'SUBDERE' in user_groups or 'DIPRES' in user_groups

        # Para las operaciones que no requieren un objeto específico (como POST), se retorna True aquí.
        # Esto porque la verificación detallada se hace en has_object_permission.
        return is_subdere_or_dipres

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True

        user_groups = request.user.groups.values_list('name', flat=True)
        is_subdere = 'SUBDERE' in user_groups
        is_dipres = 'DIPRES' in user_groups

        # Si el usuario es SUBDERE, solo se verifica la pertenencia al grupo.
        if is_subdere:
            return True

        # Si el usuario es DIPRES, se verifica además que pertenezca a la misma competencia.
        if is_dipres:
            competencia = obj.competencia  # Asumiendo que 'obj' tiene un atributo 'competencia'.
            return request.user in competencia.usuarios_dipres.all()

        return False


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
    permission_classes = [IsDIPRESOrSUBDEREOrSuperuser]


class  Etapa4ViewSet(viewsets.ModelViewSet):
    queryset = Etapa4.objects.all()
    serializer_class = Etapa4Serializer
    permission_classes = [IsSUBDEREOrSuperuser]


class Etapa5ViewSet(viewsets.ModelViewSet):
    queryset = Etapa5.objects.all()
    serializer_class = Etapa5Serializer
    permission_classes = [IsDIPRESOrSUBDEREOrSuperuser]
