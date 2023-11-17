from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1
from django.contrib.auth import get_user_model

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

User = get_user_model()


class Etapa1Serializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField()
    estado_competencia_creada = serializers.ReadOnlyField(source='get_estado_competencia_creada_display')
    estado = serializers.CharField(source='get_estado_display')

    class Meta:
        model = Etapa1
        fields = ('nombre_etapa', 'estado_competencia_creada', 'estado', 'competencia_creada')