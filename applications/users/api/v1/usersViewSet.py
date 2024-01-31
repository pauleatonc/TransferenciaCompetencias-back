from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, Permission

from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from applications.users.models import User
from applications.users.api.v1.serializers import (
    UserSerializer,
    UserListSerializer,
    UpdateUserSerializer,
    PasswordSerializer,
    GroupSerializer,
    PermissionSerializer,
    UserProfileUpdateSerializer
)
from applications.users.permissions import CanEditUser, IsSUBDEREOrSuperuser


class CustomUsersNumberPagination(PageNumberPagination):
    page_size = 10

class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer
    list_serializer_class = UserListSerializer
    queryset = None
    filter_backends = (SearchFilter, OrderingFilter)
    pagination_class = CustomUsersNumberPagination
    search_fields = ['id', 'rut', 'nombre_completo', 'email', 'perfil', 'sector__nombre', 'region__region']
    ordering_fields = ['is_active']

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)

    def get_queryset(self):
        return self.model.objects.all()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'set_password':
            permission_classes = [IsAuthenticated]  # Los usuarios deben estar autenticados para cambiar su contraseña.
        elif self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsSUBDEREOrSuperuser]  # Solo SUBDERE o superusuarios pueden realizar estas acciones.
        elif self.action == 'retrieve':
            permission_classes = [
                IsAuthenticated]  # Los usuarios pueden ver sus detalles o si son SUBDERE o superusuarios.
        elif self.action == 'update_profile':
            permission_classes = [IsAuthenticated]  # Los usuarios pueden editar su propio perfil.
        else:
            permission_classes = [AllowAny]  # Define tu política por defecto aquí.
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request, pk=None):
        """
        Endpoint para cambio de contraseñas.

        Cualquier usuario solo puede cambiar su propia contraseña.
        """
        user = self.get_object(pk)
        password_serializer = PasswordSerializer(data=request.data)
        if password_serializer.is_valid():
            user.set_password(password_serializer.validated_data['password'])
            user.save()
            return Response({
                'message': 'Contraseña actualizada correctamente'
            })
        return Response({
            'message': 'Hay errores en la información enviada',
            'errors': password_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        Listado de usuarios

        Detalles del usuario solo de lectura
        """

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Endpoint para creación de nuevos usuarios.

        Cualquier usuario nuevo solo es creado como autenticado, debe solicitar el acceso a un grupo superior si lo
        requiere.

        Los campos obligatorios para un usuario nuevo son:
            'rut',
            'tipo_usuario',
        """
        user_serializer = self.serializer_class(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({
                'message': 'Usuario registrado correctamente.'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'errors': user_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Detalle de usuario

        Detalles del usuario solo de lectura
        """
        user = self.get_object(pk)
        if request.user.is_authenticated and (user == request.user or IsSUBDEREOrSuperuser):
            user_serializer = self.serializer_class(user)
            return Response(user_serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        """
        Edición de atributos de administración de usuarios


        Permite editar todos los campos del usuario.
        Para los campos perfil, sector y region considerar lo siguiente:
                'perfil': elegir entre los perfiles ('SUBDERE', 'DIPRES', 'Usuario Sectorial', 'GORE' o 'Usuario Observador')
                'sector': clave primaria del sector,
                'region': clave primaria de la región
        """
        pk = kwargs.get('pk')  # Obtiene el id del usuario
        user = self.get_object(pk)
        partial = kwargs.pop('partial', True)

        print("Datos recibidos para PATCH:", request.data)

        user_serializer = UpdateUserSerializer(user, data=request.data, partial=partial)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({
                'message': 'Usuario actualizado correctamente'
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Hay errores en la actualización',
            'errors': user_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], name='Actualizar mi Perfil de Usuario')
    def update_profile(self, request, *args, **kwargs):
        """
        Edición de campos del propio usuario autenticado


        Permite editar solo los campos:
                'perfil': elegir entre los perfiles ('SUBDERE', 'DIPRES', 'Usuario Sectorial', 'GORE' o 'Usuario Observador')
                'sector': clave primaria del sector,
                'region': clave primaria de la región
        """
        instance = request.user
        serializer = UserProfileUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Eliminación de usuario

        Solo vuelve al usuario inactivo, no lo elimina de la base de datos
        """
        user = self.get_object(pk)

        # Verificar el permiso
        if not CanEditUser().has_object_permission(request, self, user):
            return Response({
                'message': 'No tienes permiso para eliminar este usuario'
            }, status=status.HTTP_403_FORBIDDEN)

        # Continuar con la lógica de eliminación
        user_destroy = self.model.objects.filter(id=pk).update(is_active=False)
        if user_destroy == 1:
            return Response({
                'message': 'Usuario eliminado correctamente'
            })
        return Response({
            'message': 'No existe el usuario que desea eliminar'
        }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='get-users-by-sector-region', permission_classes=[IsAuthenticated])
    def get_users_by_sector_region(self, request):
        """
        Obtener usuarios por sector y region

        Para utilizar este endpoint:
        Para filtrar por región: http://tuservidor.com/users/get-users-by-sector-region/?region_id=ID_DE_LA_REGION
        Para filtrar por sector: http://tuservidor.com/users/get-users-by-sector-region/?sector_id=ID_DEL_SECTOR
        Para obtener todas las competencias: http://tuservidor.com/users/get-users-by-sector-region/
        """
        sector_id = request.query_params.get('sector_id')
        region_id = request.query_params.get('region_id')

        # Si no se proporcionan parámetros de filtro, devolver todos los usuarios
        if not sector_id and not region_id:
            queryset = User.objects.all()
        else:
            # Inicialmente, incluir usuarios SUBDERE y DIPRES
            base_query = User.objects.filter(Q(perfil='SUBDERE') | Q(perfil='DIPRES'))

            # Filtros adicionales para usuarios sectoriales y GORE
            if sector_id:
                sectorial_users = User.objects.filter(perfil='Usuario Sectorial', sector__id=sector_id)
                base_query = base_query.union(sectorial_users)
            if region_id:
                gore_users = User.objects.filter(perfil='GORE', region__id=region_id)
                base_query = base_query.union(gore_users)

            queryset = base_query

        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer