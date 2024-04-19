from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from applications.competencias.models import Competencia
from applications.competencias.api.v1.serializers import CompetenciaListAllSerializer
from applications.users.models import User
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from applications.sectores_gubernamentales.api.v1.serializer import SectorGubernamentalSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)
    grupo_de_usuario = serializers.SerializerMethodField()
    competencias_asignadas = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)
    last_login_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'nombre_completo',
            'rut',
            'email',
            'perfil',
            'sector',
            'region',
            'is_active',
            'grupo_de_usuario',
            'competencias_asignadas',
            'created',
            'last_login_display',
        )

    def validate_rut(self, value):
        # Verifica si el RUT ya existe en la base de datos
        if User.objects.filter(rut=value).exists():
            raise ValidationError("Este RUT ya está registrado en el sistema.")
        return value

    def create(self, validated_data):
        competencias_modificar = validated_data.pop('competencias_modificar', [])
        user = User.objects.create(**validated_data)
        if validated_data.get('password'):
            user.set_password(validated_data['password'])
        user.save()

        # Procesar competencias para modificar
        for competencia_data in competencias_modificar:
            competencia_id = competencia_data.get('id')
            action = competencia_data.get('action')

            try:
                competencia = Competencia.objects.get(id=competencia_id)

                if action == 'add':
                    # Usuarios SUBDERE o DIPRES pueden ser asignados a cualquier competencia
                    if user.perfil in ['SUBDERE', 'DIPRES']:
                        competencia.usuarios_subdere.add(user)
                        competencia.usuarios_dipres.add(user)

                    # Usuarios Sectoriales solo a competencias con sectores coincidentes
                    elif user.perfil == 'Usuario Sectorial' and user.sector in competencia.sectores.all():
                        competencia.usuarios_sectoriales.add(user)

                    # Usuarios GORE solo a competencias con regiones coincidentes
                    elif user.perfil == 'GORE' and user.region in competencia.regiones.all():
                        competencia.usuarios_gore.add(user)

            except Competencia.DoesNotExist:
                # Manejar el caso en que la competencia no exista
                pass

        return user

    def get_grupo_de_usuario(self, obj):
        if obj.is_superuser:
            return 'Superusuario'

        # Obtener nombres de todos los grupos a los que pertenece el usuario
        group_names = [group.name for group in obj.groups.all()]

        # Si pertenece a algún grupo, retornar esos nombres unidos por coma
        if group_names:
            return ', '.join(group_names)

        return 'Registrado'

    def get_competencias_asignadas(self, obj):
        perfil = obj.perfil
        competencias = []

        if perfil == 'SUBDERE':
            competencias = Competencia.objects.filter(usuarios_subdere=obj)
        elif perfil == 'DIPRES':
            competencias = Competencia.objects.filter(usuarios_dipres=obj)
        elif perfil == 'Usuario Sectorial':
            competencias = Competencia.objects.filter(usuarios_sectoriales=obj)
        elif perfil == 'GORE':
            competencias = Competencia.objects.filter(usuarios_gore=obj)

        return CompetenciaListAllSerializer(competencias, many=True).data

    def get_last_login_display(self, obj):
        # Este método retorna el valor personalizado para el campo 'last_login_display'
        if obj.last_login is None:
            return "Aún no ha iniciado sesión"
        else:
            # Formatea last_login como deseas, por ejemplo, en 'dd/mm/yyyy'
            return obj.last_login.strftime("%d/%m/%Y")


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Enpoint para actualizar un usuario.

    Se utiliza para modificar competencias asignadas. Deben enviarse un listado con los ids de las competencias por asignar
    """
    competencias_asignadas = serializers.ListField(
        child=serializers.IntegerField(),  # Asume que recibirás un listado de IDs enteros
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = ('nombre_completo', 'email', 'is_active', 'perfil', 'sector', 'region', 'competencias_asignadas')

    def update(self, instance, validated_data):
        competencias_asignadas_ids = validated_data.pop('competencias_asignadas', None)

        # Procesar la actualización normal del usuario
        instance = super(UpdateUserSerializer, self).update(instance, validated_data)

        # Lógica para actualizar competencias asignadas
        if competencias_asignadas_ids is not None:
            # Limpia todas las relaciones existentes
            instance.competencias_subdere.clear()
            instance.competencias_dipres.clear()
            instance.competencias_sectoriales.clear()
            instance.competencias_gore.clear()

            # Establece las nuevas relaciones basadas en el listado de IDs
            for competencia_id in competencias_asignadas_ids:
                try:
                    competencia = Competencia.objects.get(id=competencia_id)

                    # Añade el usuario a la relación apropiada basada en su perfil
                    if instance.groups.filter(name='SUBDERE').exists():
                        competencia.usuarios_subdere.add(instance)
                    elif instance.groups.filter(name='DIPRES').exists():
                        competencia.usuarios_dipres.add(instance)
                    elif instance.groups.filter(name='Usuario Sectorial').exists():
                        competencia.usuarios_sectoriales.add(instance)
                    elif instance.groups.filter(name='GORE').exists():
                        competencia.usuarios_gore.add(instance)

                except Competencia.DoesNotExist:
                    # Manejar el caso en que la competencia no exista
                    pass

        return instance


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Indicar solo los campos actualizables
    """

    class Meta:
        model = User
        fields = [
                  'perfil',
                  'sector',
                  'region'
                  ]


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=128, min_length=6, write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password':'Debe ingresar ambas contraseñas iguales'}
            )
        return data


class UserListSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.SerializerMethodField()
    region_nombre = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'rut', 'nombre_completo', 'email', 'is_active', 'perfil', 'sector', 'sector_nombre', 'region', 'region_nombre']

    def get_sector_nombre(self, obj):
        # Verifica si el usuario tiene un sector asociado
        if obj.sector:
            return obj.sector.nombre
        # Retorna None o un valor predeterminado si el usuario no tiene un sector asociado
        return None

    def get_region_nombre(self, obj):
        # Verifica si el usuario tiene una región asociada
        if obj.region:
            return obj.region.region
        # Retorna None o un valor predeterminado si el usuario no tiene una región asociada
        return None


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = '__all__'