from rest_framework import serializers
from applications.users.models import User
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass

class UserSerializer(serializers.ModelSerializer):
    tipo_de_usuario = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'rut', 'email', 'tipo_de_usuario', 'is_active')

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_tipo_de_usuario(self, obj):
        if obj.is_superuser:
            return 'Superusuario'

        # Obtener nombres de todos los grupos a los que pertenece el usuario
        group_names = [group.name for group in obj.groups.all()]

        # Si pertenece a algún grupo, retornar esos nombres unidos por coma
        if group_names:
            return ', '.join(group_names)

        return 'Registrado'

    def get_full_name(self, obj):  # Método para obtener el nombre completo
        return obj.get_full_name()


class UpdateUserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False
    )

    """
    Indicar solo los campos actualizables
    """
    class Meta:
        model = User
        fields = ('email', 'is_active', 'groups')

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
        Indicar solo los campos actualizables
        """

    class Meta:
        model = User
        fields = ('nombres',
                  'primer_apellido',
                  'segundo_apellido',
                  'comuna',
                  'email',
                  'institucion'
                  )


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
    tipo_de_usuario = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'rut', 'nombres', 'email', 'is_active', 'tipo_de_usuario']

    def get_tipo_de_usuario(self, obj):
        if obj.is_superuser:
            return 'Superusuario'

        # Obtener nombres de todos los grupos a los que pertenece el usuario
        group_names = [group.name for group in obj.groups.all()]

        # Si pertenece a algún grupo, retornar esos nombres unidos por coma
        if group_names:
            return ', '.join(group_names)

        return 'Registrado'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = '__all__'