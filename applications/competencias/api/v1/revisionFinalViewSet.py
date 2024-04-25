import os
from django.conf import settings

from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from applications.competencias.models import Competencia, ImagenesRevisionSubdere
from applications.competencias.api.v1.revision_final_serializers import (
    RevisionFinalCompetenciaPaso1Serializer,
    RevisionFinalCompetenciaPaso2Serializer,
    RevisionFinalCompetenciaDetailSerializer,
    ImagenesRevisionSubdereSerializer,
    ResumenFormularioSerializer
)
from applications.users.permissions import IsSUBDEREOrSuperuser


def manejar_formularios_pasos(request, competencia, serializer_class, require_subdere_permission=False):
    if request.method == 'PATCH':
        if require_subdere_permission and not IsSUBDEREOrSuperuser().has_permission(request, None):
            return Response({"detail": "No autorizado para editar esta Competencia."},
                            status=status.HTTP_403_FORBIDDEN)

        print("Datos recibidos para PATCH:", request.data)
        serializer = serializer_class(competencia, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:  # GET
        serializer = serializer_class(competencia, context={'request': request})
        return Response(serializer.data)


def manejar_permiso_patch(request, competencia, serializer_class):
    """
    Maneja los permisos para operaciones PATCH y la serialización.
    """
    permiso = IsSUBDEREOrSuperuser()
    if request.method == 'PATCH':
        # Verificar permiso usando el objeto de permiso creado
        if not permiso.has_permission(request, view=None):  # Pasar `None` o la vista actual si es necesario
            return Response({"detail": "No autorizado para editar esta Competencia."},
                            status=status.HTTP_403_FORBIDDEN)

        # Si el permiso es concedido, procesar el PATCH
        return manejar_formularios_pasos(request, competencia, serializer_class, True)

    # Si el método no es PATCH, manejar como una solicitud normal
    return manejar_formularios_pasos(request, competencia, serializer_class, False)


class RevisionFinalCompetenciaViewSet(viewsets.ModelViewSet):
    queryset = Competencia.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RevisionFinalCompetenciaDetailSerializer

    def get_permissions(self):
        """
        Devuelve las clases de permisos de instancia para la acción solicitada.
        """
        if self.action in ['patch']:
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
        return manejar_formularios_pasos(request, competencia, RevisionFinalCompetenciaPaso1Serializer, require_subdere_permission=request.method == 'PATCH')

    @action(detail=True, methods=['get', 'patch'], url_path='paso-2')
    def paso_2(self, request, pk=None):
        """
        API para el Paso 2 de Revision Final Competencia
        """
        competencia = self.get_object()
        # Implementación similar a paso_1 para manejo de PATCH y GET
        return manejar_formularios_pasos(request, competencia, RevisionFinalCompetenciaPaso2Serializer, require_subdere_permission=request.method == 'PATCH')

    @action(detail=True, methods=['get', 'patch'], url_path='resumen')
    def resumen(self, request, pk=None):
        """
        API para obtener o actualizar el resumen de todos los pasos del Revision Final Subdere
        """
        competencia = self.get_object()

        if request.method == 'PATCH':
            # Aquí manejas el PATCH utilizando la lógica de permisos y actualización
            return manejar_permiso_patch(request, competencia, ResumenFormularioSerializer)

        # Si el método es GET, simplemente serializas y retornas los datos como antes
        serializer = ResumenFormularioSerializer(competencia)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subir-imagen', parser_classes=[MultiPartParser, FormParser])
    def subir_imagen(self, request, pk=None):
        competencia = self.get_object()
        if not IsSUBDEREOrSuperuser():
            return Response({"detail": "No autorizado para subir imágenes a esta competencia."},
                            status=status.HTTP_403_FORBIDDEN)
        imagen_serializer = ImagenesRevisionSubdereSerializer(data=request.data)
        if imagen_serializer.is_valid():
            imagen_serializer.save(competencia=competencia)
            return Response(imagen_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(imagen_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar-imagen/(?P<imagen_id>\d+)')
    def eliminar_imagen(self, request, pk=None, imagen_id=None):
        competencia = self.get_object()
        if not IsSUBDEREOrSuperuser():
            return Response({"detail": "No autorizado para eliminar imágenes de esta competencia."},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            imagen = ImagenesRevisionSubdere.objects.get(pk=imagen_id, competencia=competencia)
            imagen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ImagenesRevisionSubdere.DoesNotExist:
            return Response({"detail": "Imagen no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='descargar-documento')
    def descargar_documento(self, request, pk=None):
        """
        API endpoint to download the complete document PDF for a specific 'Competencia'.
        """
        competencia = self.get_object()

        document_path = os.path.join(settings.MEDIA_ROOT, 'documento_final',
                                     f'competencia_{competencia.id}_document.pdf')

        if os.path.exists(document_path):
            return FileResponse(open(document_path, 'rb'), content_type='application/pdf',
                                filename=f'competencia_{competencia.id}_document.pdf')
        else:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
