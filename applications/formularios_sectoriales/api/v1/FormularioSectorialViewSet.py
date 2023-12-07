from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from applications.formularios_sectoriales.models import FormularioSectorial, Paso1
from applications.etapas.models import Etapa1
from .serializers import FormularioSectorialDetailSerializer, Paso1Serializer
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

    @action(detail=True, methods=['get', 'post', 'put', 'patch'], url_path='paso-1')
    def paso_1(self, request, pk=None):

        if request.method == 'GET':
        # Obtén el objeto FormularioSectorial basado en el pk proporcionado
            formulario_sectorial = self.get_object()

            # Obtén el objeto Paso1 asociado con este FormularioSectorial
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

        elif request.method in ['POST', 'PUT', 'PATCH']:
            formulario_sectorial = self.get_object()

            # Obtén o crea el objeto Paso1
            paso1_obj, created = Paso1.objects.get_or_create(formulario_sectorial=formulario_sectorial)

            # Serializa y guarda/actualiza los datos
            serializer = Paso1Serializer(paso1_obj, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

