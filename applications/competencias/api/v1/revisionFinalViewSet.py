from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from applications.competencias.models import Competencia
from applications.competencias.api.v1.revision_final_serializers import RevisionFinalCompetenciaSerializer
from applications.users.permissions import IsSUBDEREOrSuperuser


class RevisionFinalCompetenciaViewSet(viewsets.ModelViewSet):
    queryset = Competencia.objects.all()
    serializer_class = RevisionFinalCompetenciaSerializer

    def get_permissions(self):
        """
        Devuelve las clases de permisos de instancia para la acción solicitada.
        """
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsSUBDEREOrSuperuser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def partial_update(self, request, *args, **kwargs):
        print("Datos recibidos para PATCH:", request.data)
        return super().partial_update(request, *args, **kwargs)

    def get_object(self):
        """
        Sobrescribe este método si necesitas manejar la lógica para obtener el objeto
        de manera personalizada.
        """
        return super().get_object()
