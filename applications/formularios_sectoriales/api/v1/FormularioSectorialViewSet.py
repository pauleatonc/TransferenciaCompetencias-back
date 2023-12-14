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
    Paso2Serializer
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

        if request.method in ['PATCH']:
            paso1_obj = Paso1.objects.filter(formulario_sectorial=formulario_sectorial).first()
            partial = request.method == 'PATCH'  # True si la solicitud es PATCH

            if paso1_obj is None:
                paso1_serializer = Paso1Serializer(data=request.data)
            else:
                paso1_serializer = Paso1Serializer(paso1_obj, data=request.data, partial=partial)

            if paso1_serializer.is_valid():
                paso1_serializer.save()
                return Response(paso1_serializer.data, status=status.HTTP_200_OK)
            return Response(paso1_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:  # GET
            paso1_obj = Paso1.objects.filter(formulario_sectorial=formulario_sectorial).first()
            if paso1_obj:
                paso1_serializer = Paso1Serializer(paso1_obj)
                response_data = {
                    'formulario_sectorial': FormularioSectorialDetailSerializer(formulario_sectorial).data,
                    'paso1': paso1_serializer.data
                }
            else:
                response_data = {
                    'formulario_sectorial': FormularioSectorialDetailSerializer(formulario_sectorial).data,
                    'paso1': None
                }
            return Response(response_data)

    @action(detail=True, methods=['post'], url_path='cargar-marco-juridico')
    def cargar_marco_juridico(self, request, pk=None):
        """
        API para cargar Marco Jurídico en el paso 1.1 Ficha de descripción organizacional

        Es necesario enviar el ID del Formulario Sectorial
        """
        # Obtener o crear un objeto Paso1 asociado al FormularioSectorial
        paso1, created = Paso1.objects.get_or_create(formulario_sectorial_id=pk)

        # Construir el serializador con 'paso1' incluido
        marco_juridico_data = request.data.copy()
        marco_juridico_data['paso1'] = paso1.id

        marco_juridico_serializer = MarcoJuridicoSerializer(data=marco_juridico_data)

        if marco_juridico_serializer.is_valid():
            marco_juridico_serializer.save()
            return Response(marco_juridico_serializer.data, status=status.HTTP_201_CREATED)
        return Response(marco_juridico_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='cargar-organigrama-regional')
    def cargar_organigrama_regional(self, request, pk=None):
        """
        API para cargar organigrama regional en el paso 1.2 Organización Institucional

        Para asociarlo a la region correcta se debe incluir el id de la región junto al 'documento' en la petición.
        """
        # Obtener la instancia de FormularioSectorial
        formulario_sectorial = self.get_object()

        # Verificar si la región está asociada a la competencia correspondiente
        region_id = request.data.get('region')
        if not region_id or not formulario_sectorial.competencia.regiones.filter(id=region_id).exists():
            return Response({'error': 'La región especificada no está asociada a esta competencia.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear un objeto Paso1 asociado al FormularioSectorial
        paso1, created = Paso1.objects.get_or_create(formulario_sectorial=formulario_sectorial)

        # Obtener o crear un objeto OrganigramaRegional asociado a la región y Paso1
        organigrama, created = OrganigramaRegional.objects.get_or_create(region_id=region_id, paso1=paso1)

        # Construir el serializador con el objeto OrganigramaRegional y los datos de la solicitud
        organigrama_serializer = OrganigramaRegionalSerializer(organigrama, data=request.data)

        if organigrama_serializer.is_valid():
            organigrama_serializer.save()
            return Response(organigrama_serializer.data, status=status.HTTP_201_CREATED)
        return Response(organigrama_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
