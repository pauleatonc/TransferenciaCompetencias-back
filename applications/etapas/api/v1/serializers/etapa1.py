from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1
from django.contrib.auth import get_user_model

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

User = get_user_model()


class Etapa1Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado = serializers.CharField(source='get_estado_display')
    competencia_creada = serializers.SerializerMethodField()
    usuarios_vinculados = serializers.SerializerMethodField()

    class Meta:
        model = Etapa1
        fields = ['nombre_etapa', 'estado', 'competencia_creada', 'usuarios_vinculados']

    def get_competencia_creada(self, obj):
        return [{
            "nombre": "Competencia creada",
            "estado": obj.estado_competencia_creada,
            "accion": "Finalizada"
        }]

    def get_usuarios_vinculados(self, obj):
        user = self.context['request'].user
        nombre = "Usuario sectorial vinculado a la competencia creada"
        if obj.competencia.sectores.count() > 1:
            nombre = "Usuarios sectoriales vinculados a la competencia creada"

        estado = obj.estado_usuarios_vinculados
        accion = "Usuario(s) pendiente(s)"

        if estado == 'finalizada':
            if user.groups.filter(name='SUBDERE').exists():
                accion = "Editar usuarios"
            else:
                accion = "Finalizada"
        else:
            if not user.groups.filter(name='SUBDERE').exists():
                accion = "Usuario(s) pendiente(s)"

        return [{
            "nombre": nombre,
            "estado": estado,
            "accion": accion
        }]