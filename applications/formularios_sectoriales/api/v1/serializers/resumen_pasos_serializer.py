from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, MarcoJuridico, OrganigramaRegional
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.formularios_sectoriales.models import PasoBase, Paso1, Paso2, Paso3, Paso4, Paso5
from .base_serializer import FormularioSectorialDetailSerializer


User = get_user_model()


class PasoBaseSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = PasoBase
        fields = [
            'pk',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso1ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso1


class Paso2ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso2


class Paso3ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso3


class Paso4ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso4


class Paso5ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso5


class ResumenFormularioSerializer(serializers.ModelSerializer):
    competencia_nombre = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    paso1 = Paso1ResumenSerializer(many=True,  read_only=True)
    paso2 = Paso2ResumenSerializer(many=True,  read_only=True)
    paso3 = Paso3ResumenSerializer(many=True,  read_only=True)
    paso4 = Paso4ResumenSerializer(many=True,  read_only=True)
    paso5 = Paso5ResumenSerializer(many=True,  read_only=True)

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'competencia_nombre',
            'sector_nombre',
            'formulario_enviado',
            'fecha_envio',
            'intento_envio',
            'paso1',
            'paso2',
            'paso3',
            'paso4',
            'paso5'
        ]

    def get_competencia_nombre(self, obj):
        return obj.competencia.nombre if obj.competencia else None

    def get_sector_nombre(self, obj):
        return obj.sector.nombre if obj.sector else None