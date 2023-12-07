from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, MarcoJuridico, OrganigramaRegional
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.formularios_sectoriales.models import Paso1
from .base_serializer import FormularioSectorialDetailSerializer

User = get_user_model()


class MarcoJuridicoSerializer(serializers.ModelSerializer):
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = MarcoJuridico
        fields = [
            'documento_url'
        ]

    def get_documento_url(self, obj):
        return obj.documento.url if obj.documento and obj.documento.name else None



class OrganigramaRegionalSerializer(serializers.ModelSerializer):
    region = serializers.SerializerMethodField()
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = OrganigramaRegional
        fields = [
            'region',
            'documento_url'
        ]

    def get_region(self, obj):
        return obj.region.region if obj.region else None

    def get_documento_url(self, obj):
        return obj.documento.url if obj.documento and obj.documento.name else None


class Paso1Serializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    ficha_descripcion_organizacional = serializers.SerializerMethodField()
    organizacion_institucional = serializers.SerializerMethodField()
    marco_regulatorio_y_funcional_competencia = serializers.SerializerMethodField()

    class Meta:
        model = Paso1
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'ficha_descripcion_organizacional',
            'organizacion_institucional',
            'marco_regulatorio_y_funcional_competencia'
        ]

    def get_ficha_descripcion_organizacional(self, obj):
        return {
            'denominacion_organismo': self.get_denominacion_organismo(obj),
            'forma_juridica_organismo': obj.forma_juridica_organismo,
            'marco_juridico': MarcoJuridicoSerializer(obj.marcojuridico_set.all(), many=True).data,
            'descripcion_archivo_marco_juridico': obj.descripcion_archivo_marco_juridico,
            'mision_institucional': obj.mision_institucional,
            'informacion_adicional_marco_juridico': obj.informacion_adicional_marco_juridico
        }

    def get_organizacion_institucional(self, obj):
        return {
            'organigrama_nacional': obj.organigrama_nacional.url if obj.organigrama_nacional and obj.organigrama_nacional.name else None,
            'organigrama_regional': OrganigramaRegionalSerializer(obj.organigramaregional_set.all(), many=True).data,
            'descripcion_archivo_organigrama_regional': obj.descripcion_archivo_organigrama_regional,
        }

    def get_marco_regulatorio_y_funcional_competencia(self, obj):
        return {
            'identificacion_competencia': obj.identificacion_competencia,
            'fuentes_normativas': obj.fuentes_normativas,
            'territorio_competencia': obj.territorio_competencia,
            'enfoque_territorial_competencia': obj.enfoque_territorial_competencia,
            'ambito': obj.ambito,
            'posibilidad_ejercicio_por_gobierno_regional': obj.posibilidad_ejercicio_por_gobierno_regional,
            'organo_actual_competencia': obj.organo_actual_competencia,
        }

    def avance(self, obj):
        return obj.avance()

    def get_denominacion_organismo(self, obj):
        if obj.formulario_sectorial:
            return obj.formulario_sectorial.sector.nombre
        return None

    def validate_marco_juridico(self, value):
        """
        Mínimo 1 archivo, máximo 5 archivos, peso máximo 20MB, formato PDF
        """
        if not (1 <= len(value) <= 5):
            raise serializers.ValidationError("Mínimo 1 archivo, máximo 5 archivos.")
        return value
