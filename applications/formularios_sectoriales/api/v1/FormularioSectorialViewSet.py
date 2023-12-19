from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso1,
    OrganigramaRegional,
    Paso2
)
from applications.etapas.models import Etapa1
from .serializers import (
    FormularioSectorialDetailSerializer,
    Paso1Serializer,
    MarcoJuridicoSerializer,
    OrganigramaRegionalSerializer,
    Paso2Serializer,
    Paso3Serializer
)
from applications.users.permissions import IsSUBDEREOrSuperuser


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

        if request.method == 'PATCH':
            serializer = Paso1Serializer(formulario_sectorial, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:  # GET
            serializer = Paso1Serializer(formulario_sectorial)
            return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-2')
    def paso_2(self, request, pk=None):
        formulario_sectorial = self.get_object()

        if request.method == 'PATCH':
            serializer = Paso2Serializer(formulario_sectorial, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:  # GET
            serializer = Paso2Serializer(formulario_sectorial)
            return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'], url_path='paso-3')
    def paso_3(self, request, pk=None):
        formulario_sectorial = self.get_object()

        if request.method == 'PATCH':
            print("Datos recibidos para PATCH:", request.data)  # Datos recibidos
            serializer = Paso3Serializer(formulario_sectorial, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                print("Datos después de la serialización:", serializer.data)  # Datos después de la serialización
                return Response(serializer.data, status=status.HTTP_200_OK)
            print("Errores de serialización:", serializer.errors)  # Errores de serialización
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:  # GET
            serializer = Paso3Serializer(formulario_sectorial)
            return Response(serializer.data)



