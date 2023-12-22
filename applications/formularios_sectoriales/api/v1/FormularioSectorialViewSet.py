from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from applications.formularios_sectoriales.models import (
    FormularioSectorial
)
from applications.users.permissions import IsSUBDEREOrSuperuser
from .serializers import (
    FormularioSectorialDetailSerializer,
    Paso1Serializer,
    Paso2Serializer,
    Paso3Serializer,
    Paso4Serializer,
    Paso5Serializer,
)


def manejar_formularios_pasos(request, formulario_sectorial, serializer_class):
    if request.method == 'PATCH':
        print("Datos recibidos para PATCH:", request.data)
        serializer = serializer_class(formulario_sectorial, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:  # GET
        serializer = serializer_class(formulario_sectorial)
        return Response(serializer.data)


class FormularioSectorialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de un Formulario Sectorial.
    Ofrece Creación, actualización, detalle y eliminación de Formularios.
    """
    queryset = FormularioSectorial.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Selecciona el serializer adecuado en función de la acción
        if self.action == 'retrieve':
            return FormularioSectorialDetailSerializer
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


    @action(detail=True, methods=['get', 'patch'], url_path='paso-1')
    def paso_1(self, request, pk=None):
        """
        API Paso 1 - Descripción de la Institución de Formulario Sectorial

        Con GET devuelve el detalle de todos los campos.

        Mediante PATCH se pueden editar los siguientes campos:

        "p_1_1_ficha_descripcion_organizacional": {
            "denominacion_organismo": "",
            "forma_juridica_organismo": "",
            "descripcion_archivo_marco_juridico": "",
            "mision_institucional": "",
            "informacion_adicional_marco_juridico": ""
        },
        "p_1_2_organizacion_institucional": {
            "organigrama_nacional": "",
            "descripcion_archivo_organigrama_regional": ""
        },
        "p_1_3_marco_regulatorio_y_funcional_competencia": {
            "identificacion_competencia": "",
            "fuentes_normativas": "",
            "territorio_competencia": "",
            "enfoque_territorial_competencia": "",
            "ambito": "",
            "posibilidad_ejercicio_por_gobierno_regional": "",
            "organo_actual_competencia": ""
        }
        """
        formulario_sectorial = self.get_object()
        return manejar_formularios_pasos(request, formulario_sectorial, Paso1Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-2')
    def paso_2(self, request, pk=None):
        formulario_sectorial = self.get_object()

        return manejar_formularios_pasos(request, formulario_sectorial, Paso2Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-3')
    def paso_3(self, request, pk=None):
        formulario_sectorial = self.get_object()

        return manejar_formularios_pasos(request, formulario_sectorial, Paso3Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-4')
    def paso_4(self, request, pk=None):
        formulario_sectorial = self.get_object()

        return manejar_formularios_pasos(request, formulario_sectorial, Paso4Serializer)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-5')
    def paso_5(self, request, pk=None):
        formulario_sectorial = self.get_object()

        return manejar_formularios_pasos(request, formulario_sectorial, Paso5Serializer)