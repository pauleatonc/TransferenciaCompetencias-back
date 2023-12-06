from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from django.contrib.auth import get_user_model

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

User = get_user_model()


class FormularioSectorialDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'nombre',
        ]