from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, Q
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1
from .serializers import (
    CompetenciaListSerializer,
    CompetenciaCreateSerializer,
    CompetenciaUpdateSerializer,
    CompetenciaDetailSerializer,
    CompetenciaHomeListSerializer,
    CompetenciaListAllSerializer
)

from applications.users.permissions import IsSUBDEREOrSuperuser


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


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10

class CustomHomePagination(PageNumberPagination):
    page_size = 2

class CompetenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD para el modelo Competencia.
    Ofrece listado, creación, actualización, detalle y eliminación de competencias.
    """
    queryset = Competencia.objects.all()
    filter_backends = (SearchFilter, OrderingFilter)
    pagination_class = CustomPageNumberPagination
    search_fields = [
        'id',
        'nombre',
        'sectores__nombre',
        'ambito_competencia__nombre',
        'regiones__region',
        'origen',
        'usuarios_subdere__nombre_completo',
        'usuarios_dipres__nombre_completo',
        'usuarios_sectoriales__nombre_completo',
        'usuarios_gore__nombre_completo'
    ]
    ordering_fields = ['estado']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Selecciona el serializer adecuado en función de la acción
        if self.action == 'list':
            return CompetenciaListSerializer
        elif self.action == 'create':
            return CompetenciaCreateSerializer
        elif self.action == 'retrieve':
            return CompetenciaDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return CompetenciaUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """
        Devuelve las clases de permisos de instancia para la acción solicitada.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSUBDEREOrSuperuser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """
        Listado de Competencias

        Devuelve una lista paginada(10) de todas las competencias disponibles.
        Acceso para usuarios autenticados.
        Se puede usar search y ordering para filtrar y ordenar la lista. Los campos
        permitidos son los siguientes:
        - id
        - nombre
        - sectores__nombre
        - ambito_competencia__nombre
        - regiones__region
        - origen
        - usuarios_subdere__nombre_completo
        - usuarios_dipres__nombre_completo
        - usuarios_sectoriales__nombre_completo
        - usuarios_gore__nombre_completo

        Los campos permitidos para ordenamiento son los siguientes:
        - estado

        Ejemplo de uso:
        GET /api/competencias/?search=nombre&ordering=estado
        GET /api/competencias/?search=nombre&ordering=-estado
        GET /api/competencias/?search=nombre&ordering=estado,-id
        GET /api/competencias/?search=nombre&ordering=-estado,-id
        GET /api/competencias/?search=nombre&ordering=estado,-id&page=2&page_size=5
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Usar el paginador para paginar el queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Si no hay paginación, devolver todos los datos
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='lista-home')
    def lista_home(self, request):
        user = request.user
        queryset = Competencia.objects.all().order_by('-modified_date')

        # Filtrar según el tipo de usuario
        if user.groups.filter(name='SUBDERE').exists():
            queryset = queryset.filter(usuarios_subdere=user)
        elif user.groups.filter(name='GORE').exists():
            queryset = queryset.filter(usuarios_gore=user)
        elif user.groups.filter(name='DIPRES').exists():
            queryset = queryset.filter(usuarios_dipres=user)
        elif user.groups.filter(name='Usuario Sectorial').exists():
            queryset = queryset.filter(usuarios_sectoriales=user)

        paginator = CustomHomePagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = CompetenciaHomeListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CompetenciaHomeListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Crear Competencia

        Permite la creación de una nueva competencia.
        Acceso restringido a usuarios SUBDERE o superusuarios.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        competencia = serializer.save(creado_por=request.user)

        # Añadir el usuario a usuarios_subdere
        competencia.usuarios_subdere.add(request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Detalle de Competencia

        Devuelve el detalle de una competencia específica.
        Acceso para usuarios autenticados.
        """
        competencia = self.get_object()
        serializer = self.get_serializer(competencia)
        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Actualizar Competencia

        Permite actualizar los datos de una competencia existente.
        Acceso solo para usuarios con permisos adecuados.
        """
        competencia = self.get_object()
        serializer = self.get_serializer(competencia, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Eliminar Competencia

        Permite eliminar una competencia.
        Acceso solo para usuarios con permisos adecuados.
        """
        competencia = self.get_object()
        competencia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='filtrar-por-criterio')
    def filtrar_por_criterio(self, request):
        """
        Endpoint para filtrar competencias por región o sector.

        Para utilizar este endpoint:
        Para filtrar por región: http://tuservidor.com/competencias/filtrar-por-criterio/?region_id=ID_DE_LA_REGION
        Para filtrar por sector: http://tuservidor.com/competencias/filtrar-por-criterio/?sector_id=ID_DEL_SECTOR
        Para obtener todas las competencias: http://tuservidor.com/competencias/filtrar-por-criterio/
        """
        # Obtén los parámetros de la solicitud
        region_id = request.query_params.get('region_id')
        sector_id = request.query_params.get('sector_id')

        # Filtrar competencias basadas en región o sector
        if region_id:
            queryset = Competencia.objects.filter(regiones__id=region_id)
        elif sector_id:
            queryset = Competencia.objects.filter(sectores__id=sector_id)
        else:
            # Devolver todas las competencias si no se especifica un filtro
            queryset = Competencia.objects.all()

        serializer = CompetenciaListAllSerializer(queryset, many=True)
        return Response(serializer.data)