from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from applications.competencias.models import (
    Competencia,
    RecomendacionesDesfavorables,
    Temporalidad,
    Gradualidad
)

from applications.competencias.api.v1.serializers import (
    AmbitoSerializer,
    SectorSerializer
)

from applications.regioncomuna.api.v1.serializer import RegionSerializer


class RecomendacionesDesfavorablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecomendacionesDesfavorables
        fields = [
            'id',
            'region',
            'justificacion'
        ]


class TemporalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporalidad
        fields = [
            'id',
            'region',
            'temporalidad',
            'justificacion_temporalidad'
        ]


class GradualidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gradualidad
        fields = [
            'id',
            'region',
            'gradualidad_meses',
            'justificacion_gradualidad'
        ]


class RevisionFinalCompetenciaSerializer(WritableNestedModelSerializer):
    recomendaciones_desfavorables = RecomendacionesDesfavorablesSerializer(many=True)
    temporalidad = TemporalidadSerializer(many=True)
    gradualidad = GradualidadSerializer(many=True)
    ambito_definitivo_competencia = AmbitoSerializer()
    sectores = SectorSerializer(many=True, read_only=True)
    regiones_recomendadas = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
            'sectores',
            'ambito_definitivo_competencia',
            'regiones_recomendadas',
            'recomendaciones_desfavorables',
            'temporalidad',
            'gradualidad',
            'recursos_requeridos',
            'modalidad_ejercicio',
            'implementacion_acompanamiento',
            'condiciones_ejercicio',
        ]

    def get_regiones_recomendadas(self, obj):
        # Filtramos las regiones que ya están en 'regiones' para la competencia.
        regiones_qs = obj.regiones.all()

        # Serializamos las regiones y devolvemos los datos.
        return RegionSerializer(regiones_qs, many=True).data