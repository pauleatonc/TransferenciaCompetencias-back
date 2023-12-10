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


class FichaDescripcionOrganizacionalSerializer(serializers.ModelSerializer):
    denominacion_organismo = serializers.SerializerMethodField()
    marco_juridico = MarcoJuridicoSerializer(many=True, read_only=True)

    class Meta:
        model = Paso1
        fields = [
            'denominacion_organismo',
            'forma_juridica_organismo',
            'marco_juridico',
            'descripcion_archivo_marco_juridico',
            'mision_institucional',
            'informacion_adicional_marco_juridico'
        ]

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


class Paso1Serializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    p_1_1_ficha_descripcion_organizacional = serializers.SerializerMethodField()
    p_1_2_organizacion_institucional = serializers.SerializerMethodField()
    p_1_3_marco_regulatorio_y_funcional_competencia = serializers.SerializerMethodField()

    class Meta:
        model = Paso1
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'p_1_1_ficha_descripcion_organizacional',
            'p_1_2_organizacion_institucional',
            'p_1_3_marco_regulatorio_y_funcional_competencia'
        ]

    def get_p_1_1_ficha_descripcion_organizacional(self, obj):
        serializer = FichaDescripcionOrganizacionalSerializer(obj)
        return serializer.data

    def get_p_1_2_organizacion_institucional(self, obj):
        return {
            'organigrama_nacional': obj.organigrama_nacional.url if obj.organigrama_nacional and obj.organigrama_nacional.name else None,
            'organigrama_regional': OrganigramaRegionalSerializer(obj.organigramaregional_set.all(), many=True).data,
            'descripcion_archivo_organigrama_regional': obj.descripcion_archivo_organigrama_regional,
        }

    def get_p_1_3_marco_regulatorio_y_funcional_competencia(self, obj):
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

    def to_internal_value(self, data):
        ficha_data = data.pop('p_1_1_ficha_descripcion_organizacional', None)
        internal_value = super().to_internal_value(data)

        if ficha_data is not None:
            ficha_serializer = FichaDescripcionOrganizacionalSerializer(data=ficha_data)
            if ficha_serializer.is_valid():
                internal_value.update({
                    'p_1_1_ficha_descripcion_organizacional': ficha_serializer.validated_data
                })
            else:
                raise serializers.ValidationError(ficha_serializer.errors)

        return internal_value

    def update(self, instance, validated_data):
        print("Datos Validados:", validated_data)
        ficha_data = validated_data.pop('p_1_1_ficha_descripcion_organizacional', {})

        # Actualiza los campos individuales de la ficha
        if ficha_data:
            print("Actualizando Ficha Descripción Organizacional:", ficha_data)
            for attr, value in ficha_data.items():
                setattr(instance, attr, value)

        # Guarda los cambios en el modelo Paso1
        instance.save()

        return instance


