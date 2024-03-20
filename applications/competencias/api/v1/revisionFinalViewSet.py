from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from applications.competencias.models import Competencia
from applications.competencias.api.v1.revision_final_serializers import (
    RevisionFinalCompetenciaPaso1Serializer,
    RevisionFinalCompetenciaPaso2Serializer,
    RevisionFinalCompetenciaDetailSerializer
)
from applications.users.permissions import IsSUBDEREOrSuperuser


def manejar_formularios_pasos(request, competencia, serializer_class):
    if request.method == 'PATCH':
        print("Datos recibidos para PATCH:", request.data)
        # Asegúrate de pasar el contexto aquí
        serializer = serializer_class(competencia, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:  # GET
        # Y también aquí
        serializer = serializer_class(competencia, context={'request': request})
        return Response(serializer.data)


def manejar_permiso_patch(request, formulario_gore, serializer_class):
    """
        Maneja los permisos para operaciones PATCH y la serialización.
        """
    if request.method == 'PATCH':
        if not IsSUBDEREOrSuperuser(request, formulario_gore):
            return Response({"detail": "No autorizado para editar este formulario GORE."},
                            status=status.HTTP_403_FORBIDDEN)

        return manejar_formularios_pasos(request, formulario_gore, serializer_class)

    return manejar_formularios_pasos(request, formulario_gore, serializer_class)


class RevisionFinalCompetenciaViewSet(viewsets.ModelViewSet):
    queryset = Competencia.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RevisionFinalCompetenciaDetailSerializer

    def get_permissions(self):
        """
        Devuelve las clases de permisos de instancia para la acción solicitada.
        """
        if self.action in ['create']:
            permission_classes = [IsSUBDEREOrSuperuser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get', 'patch'], url_path='paso-1')
    def paso_1(self, request, pk=None):
        """
        API para el Paso 1 de Revision Final Competencia
        """
        competencia = self.get_object()
        # Aquí podrías añadir lógica similar a manejar_permiso_patch si necesitas control de acceso específico
        return manejar_formularios_pasos(request, competencia, RevisionFinalCompetenciaPaso1Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-2')
    def paso_2(self, request, pk=None):
        """
        API para el Paso 2 de Revision Final Competencia
        """
        competencia = self.get_object()
        # Implementación similar a paso_1 para manejo de PATCH y GET
        return manejar_formularios_pasos(request, competencia, RevisionFinalCompetenciaPaso2Serializer)

