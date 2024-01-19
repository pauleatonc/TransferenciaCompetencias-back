from rest_framework import serializers

from applications.competencias.models import Competencia
from applications.formularios_sectoriales.api.v1.serializers.base_serializer import CompetenciaSerializer
from applications.users.models import User
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)
    grupo_de_usuario = serializers.SerializerMethodField()
    competencias_asignadas = serializers.SerializerMethodField()

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
            'competencias_asignadas'
        )

    def create(self, validated_data):
        user = User(**validated_data)
        password = validated_data.pop('password', None)  # Usa pop para evitar KeyError y manejar el caso si falta
        if password:
            user.set_password(password)
        user.save()
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

        return CompetenciaSerializer(competencias, many=True).data


class UpdateUserSerializer(serializers.ModelSerializer):
    competencias_modificar = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = ('nombre_completo', 'email', 'is_active', 'perfil', 'sector', 'region', 'competencias_modificar')

    def update(self, instance, validated_data):
        competencias_modificar = validated_data.pop('competencias_modificar', None)

        # Procesar la actualización normal del usuario
        instance = super(UpdateUserSerializer, self).update(instance, validated_data)

        # Lógica para modificar competencias
        if competencias_modificar:
            perfil = instance.perfil
            for competencia_data in competencias_modificar:
                competencia_id = competencia_data.get('id')
                action = competencia_data.get('action')  # 'add' o 'delete'

                try:
                    competencia = Competencia.objects.get(id=competencia_id)

                    if action == 'delete':
                        # Lógica para eliminar la competencia
                        if perfil == 'SUBDERE':
                            competencia.usuarios_subdere.remove(instance)
                        if perfil == 'DIPRES':
                            competencia.usuarios_dipres.remove(instance)
                        if perfil == 'Usuario Sectorial':
                            competencia.usuarios_sectoriales.remove(instance)
                        if perfil == 'GORE':
                            competencia.usuarios_gore.remove(instance)
                    elif action == 'add':
                        # Lógica para agregar la competencia
                        if perfil == 'SUBDERE':
                            competencia.usuarios_subdere.add(instance)
                        if perfil == 'DIPRES':
                            competencia.usuarios_dipres.add(instance)
                        if perfil == 'Usuario Sectorial':
                            competencia.usuarios_sectoriales.add(instance)
                        if perfil == 'GORE':
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

    class Meta:
        model = User
        fields = ['id', 'rut', 'nombre_completo', 'email', 'is_active', 'perfil', 'sector', 'region']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = '__all__'