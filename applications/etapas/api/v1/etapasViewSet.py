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

class IsDIPRESAndAssignedToCompetition(BasePermission):
    """
    Permite el acceso solo a los usuarios DIPRES asignados a la competencia relacionada con la etapa.
    """

    def has_permission(self, request, view):
        # Esta implementación es solo un esquema. Deberás adaptarla según tu modelo y lógica específica.
        user = request.user
        # Asumiendo que puedes obtener la instancia de la etapa (Etapa3, Etapa5, etc.) de esta manera
        etapa = view.get_object()
        competencia = etapa.competencia

        # Verificación de pertenencia al grupo DIPRES y asignación a la competencia
        return user.groups.filter(name='DIPRES').exists() and competencia.usuarios_dipres.filter(id=user.id).exists()

    def has_object_permission(self, request, view, obj):
        # Implementación similar a has_permission, pero aplicada a nivel de objeto.
        # Aquí, obj es la instancia específica de la etapa.
        user = request.user
        competencia = obj.competencia

        return user.groups.filter(name='DIPRES').exists() and competencia.usuarios_dipres.filter(id=user.id).exists()



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

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsSUBDEREOrSuperuser, IsDIPRESAndAssignedToCompetition]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class  Etapa4ViewSet(viewsets.ModelViewSet):
    queryset = Etapa4.objects.all()
    serializer_class = Etapa4Serializer
    permission_classes = [IsSUBDEREOrSuperuser]


class Etapa5ViewSet(viewsets.ModelViewSet):
    queryset = Etapa5.objects.all()
    serializer_class = Etapa5Serializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsSUBDEREOrSuperuser, IsDIPRESAndAssignedToCompetition]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
