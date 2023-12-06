from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from django.contrib.auth import get_user_model

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

User = get_user_model()


class CompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = [
            'nombre',
        ]


class FormularioSectorialDetailSerializer(serializers.ModelSerializer):
    competencia_nombre = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'competencia_nombre',
            'nombre',
        ]

    def get_competencia_nombre(self, obj):
        if obj.competencia:
            return obj.competencia.nombre
        return None