from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from applications.formularios_gores.models import(
    FormularioGORE, FlujogramaEjercicioCompetencia
)
from applications.users.permissions import IsSUBDEREOrSuperuser
from .serializers import (
    FormularioGOREDetailSerializer
)


def manejar_formularios_pasos(request, formulario_gore, serializer_class):
    if request.method == 'PATCH':
        print("Datos recibidos para PATCH:", request.data)
        # Asegúrate de pasar el contexto aquí
        serializer = serializer_class(formulario_gore, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:  # GET
        # Y también aquí
        serializer = serializer_class(formulario_gore, context={'request': request})
        return Response(serializer.data)



def es_usuario_autorizado_para_region(request, formulario_gore):
    """
        Verifica si el usuario pertenece a la misma region que el formulario.
        """
    return request.user.region == formulario_gore.sector


def manejar_permiso_patch(request, formulario_gore, serializer_class):
    """
        Maneja los permisos para operaciones PATCH y la serialización.
        """
    if request.method == 'PATCH':
        if not es_usuario_autorizado_para_region(request, formulario_gore):
            return Response({"detail": "No autorizado para editar este formulario GORE."},
                            status=status.HTTP_403_FORBIDDEN)

        return manejar_formularios_pasos(request, formulario_gore, serializer_class)

    return manejar_formularios_pasos(request, formulario_gore, serializer_class)


class FormularioGOREViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de un Formulario GORE.
    Ofrece Creación, actualización, detalle y eliminación de Formularios.
    """
    queryset = FormularioGORE.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Selecciona el serializer adecuado en función de la acción
        if self.action == 'retrieve':
            return FormularioGOREDetailSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """
        Devuelve las clases de permisos de instancia para la acción solicitada.
        """
        if self.action == 'create':
            permission_classes = [IsSUBDEREOrSuperuser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Detalle de Competencia

        Devuelve el detalle de una competencia específica.
        Acceso para usuarios autenticados.
        """
        competencia = self.get_object()
        serializer = self.get_serializer(competencia)
        return Response(serializer.data)

    '''@action(detail=True, methods=['get', 'patch'], url_path='paso-1')
    def paso_1(self, request, pk=None):
        """
        API Paso 1 - Descripción de la Institución de Formulario Sectorial
        """
        formulario_gore = self.get_object()
        return manejar_permiso_patch(request, formulario_gore, Paso1Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-2')
    def paso_2(self, request, pk=None):
        formulario_gore = self.get_object()
        return manejar_permiso_patch(request, formulario_gore, Paso2Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-3')
    def paso_3(self, request, pk=None):
        formulario_gore = self.get_object()
        return manejar_permiso_patch(request, formulario_gore, Paso3Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-4')
    def paso_4(self, request, pk=None):
        formulario_gore = self.get_object()
        return manejar_permiso_patch(request, formulario_gore, Paso4Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-5')
    def paso_5(self, request, pk=None):
        formulario_gore = self.get_object()
        return manejar_permiso_patch(request, formulario_gore, Paso5Serializer)

    @action(detail=True, methods=['get'], url_path='resumen')
    def resumen(self, request, pk=None):
        """
        API para obtener el resumen de todos los pasos del Formulario Sectorial
        """
        formulario_gore = self.get_object()
        serializer = ResumenFormularioSerializer(formulario_gore)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'], url_path='observaciones-subdere-sectorial')
    def observaciones_sectoriales(self, request, pk=None):
        formulario_gore = self.get_object()
        competencia = formulario_gore.competencia

        # Verifica si el usuario es un usuario SUBDERE autorizado para la competencia del formulario sectorial
        if request.method == 'PATCH' and not request.user in competencia.usuarios_subdere.all():
            return Response({"detail": "No autorizado para editar las observaciones de SUBDERE."},
                            status=status.HTTP_403_FORBIDDEN)

        return manejar_formularios_pasos(request, formulario_gore, ObservacionesSubdereSerializer)'''

    @action(detail=True, methods=['patch'], url_path='update-flujograma-competencia',
        parser_classes=(MultiPartParser, FormParser))
    def update_flujograma_competencia(self, request, pk=None):
        """
        Un endpoint dedicado para actualizar el documento de un FlujogramaCompetencia específico
        o crear uno nuevo si no se proporciona flujograma_competencia_id.

        Se deben agregar en el body dos keys, flujograma_competencia_id: el valor del ID y documento: el archivo a subir.
        Si se proporciona flujograma_competencia_id, el endpoint actualiza el documento existente. Si no se proporciona
        flujograma_competencia_id, el endpoint crea un nuevo FlujogramaCompetencia.
        """
        flujograma_competencia_id = request.data.get('flujograma_competencia_id')
        documento_file = request.FILES.get('documento')  # Esta es la línea que extrae el archivo del request

        if not documento_file:
            return Response({"error": "Documento es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        formulario_gore = self.get_object()

        if flujograma_competencia_id:
            # Intenta actualizar un FlujogramaCompetencia existente
            try:
                flujograma_competencia = FlujogramaEjercicioCompetencia.objects.get(id=flujograma_competencia_id, formulario_gore=formulario_gore)
            except FlujogramaEjercicioCompetencia.DoesNotExist:
                return Response({"error": "FlujogramaCompetencia no encontrado."}, status=status.HTTP_404_NOT_FOUND)
            
            flujograma_competencia.flujograma_ejercicio_competencia = documento_file  # Asegúrate de usar el campo correcto aquí
            flujograma_competencia.save()

            return Response({"mensaje": "Documento actualizado con éxito."})
        else:
            # Crea un nuevo FlujogramaCompetencia si no se proporciona ID
            flujograma_competencia = FlujogramaEjercicioCompetencia.objects.create(
                formulario_gore=formulario_gore,
                flujograma_ejercicio_competencia=documento_file  # Asegúrate de usar el campo correcto aquí también
            )

            return Response({"mensaje": "Documento creado con éxito.", "flujograma_ejercicio_competencia_id": flujograma_competencia.id},
                            status=status.HTTP_201_CREATED)

