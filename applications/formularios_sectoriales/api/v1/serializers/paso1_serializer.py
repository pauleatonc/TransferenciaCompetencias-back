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
    documento = serializers.FileField(write_only=True, required=False)
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = MarcoJuridico
        fields = ['documento', 'documento_url']

    def get_documento_url(self, obj):
        if obj.documento and hasattr(obj.documento, 'url'):
            return obj.documento.url
        return None

    def create(self, validated_data):
        return MarcoJuridico.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.documento = validated_data.get('documento', instance.documento)
        instance.save()
        return instance


class OrganigramaRegionalSerializer(serializers.ModelSerializer):
    region = serializers.SerializerMethodField()
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = OrganigramaRegional
        fields = [
            'region',
            'documento',
            'documento_url'
        ]

    def get_region(self, obj):
        # Asegurándote de que 'obj' sea un objeto OrganigramaRegional
        return obj.region.region if obj.region else None

    def get_documento_url(self, obj):
        if obj.documento and hasattr(obj.documento, 'url'):
            return obj.documento.url
        return None
    def create(self, validated_data):
        return OrganigramaRegional.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.documento = validated_data.get('documento', instance.documento)
        instance.save()
        return instance


class FichaDescripcionOrganizacionalSerializer(serializers.ModelSerializer):
    denominacion_organismo = serializers.SerializerMethodField()
    marco_juridico = MarcoJuridicoSerializer(source='marcojuridico_set', many=True)

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


class FichaOrganizacionInstitucionalSerializer(serializers.ModelSerializer):
    organigrama_regional = OrganigramaRegionalSerializer(source='organigramaregional_set', many=True)
    class Meta:
        model = Paso1
        fields = [
            'organigrama_nacional',
            'organigrama_regional',
            'descripcion_archivo_organigrama_regional'
        ]


class FichaMarcoRegulatorioFuncionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paso1
        fields = [
            'identificacion_competencia',
            'fuentes_normativas',
            'territorio_competencia',
            'enfoque_territorial_competencia',
            'ambito',
            'posibilidad_ejercicio_por_gobierno_regional',
            'organo_actual_competencia'
        ]


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
        serializer = FichaOrganizacionInstitucionalSerializer(obj)
        return serializer.data

    def get_p_1_3_marco_regulatorio_y_funcional_competencia(self, obj):
        serializer = FichaMarcoRegulatorioFuncionalSerializer(obj)
        return serializer.data

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
        ficha_data = validated_data.pop('p_1_1_ficha_descripcion_organizacional', {})

        # Actualiza los campos individuales de la ficha
        if ficha_data:
            for attr, value in ficha_data.items():
                setattr(instance, attr, value)

        # Guarda los cambios en el modelo Paso1
        instance.save()

        return instance


