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
        formulario_sectorial = self.get_object()
        print("Método de Solicitud:", request.method)
        print("Datos de Solicitud:", request.data)

        if request.method in ['POST', 'PUT', 'PATCH']:
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