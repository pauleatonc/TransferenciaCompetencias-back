from rest_framework import viewsets, status
from rest_framework.response import Response
from applications.competencias.models import Competencia
from .serializers import (CompetenciaListSerializer, CompetenciaCreateSerializer,
                          CompetenciaUpdateSerializer, CompetenciaDetailSerializer)

class CompetenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD para el modelo Competencia.
    Ofrece listado, creación, actualización, detalle y eliminación de competencias.
    """
    queryset = Competencia.objects.all()

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

    def list(self, request, *args, **kwargs):
        """
        Listado de Competencias

        Devuelve una lista de todas las competencias disponibles.
        Acceso para usuarios autenticados.
        """
        competencias = self.get_queryset()
        serializer = self.get_serializer(competencias, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Crear Competencia

        Permite la creación de una nueva competencia.
        Acceso solo para usuarios con permisos adecuados.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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