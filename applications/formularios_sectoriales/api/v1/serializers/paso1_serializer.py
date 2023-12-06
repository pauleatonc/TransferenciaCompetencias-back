from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.formularios_sectoriales.models import Paso1

User = get_user_model()


class Meta:
    model = Paso1
    fields = [
        'id',
        'competencia_nombre',
        'sector_nombre',
        'nombre',
        'plazo_dias',
        'calcular_tiempo_transcurrido',
        'ultimo_editor',
        'fecha_ultima_modificacion',
    ]