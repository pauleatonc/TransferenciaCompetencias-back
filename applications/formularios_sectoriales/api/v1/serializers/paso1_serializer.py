from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, MarcoJuridico, OrganigramaRegional
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.formularios_sectoriales.models import Paso1
from .base_serializer import FormularioSectorialDetailSerializer
from drf_writable_nested.serializers import WritableNestedModelSerializer

User = get_user_model()


class MarcoJuridicoSerializer(serializers.ModelSerializer):
    documento_url = serializers.SerializerMethodField()
    #paso1 = serializers.PrimaryKeyRelatedField(queryset=Paso1.objects.all(), write_only=True)

    class Meta:
        model = MarcoJuridico
        fields = ['pk', 'documento', 'documento_url']

    def get_documento_url(self, obj):
        if obj.documento and hasattr(obj.documento, 'url'):
            return obj.documento.url
        return None

    '''def validate(self, data):
        """
        Validar que la cantidad de archivos (incluyendo los ya existentes) no exceda el máximo permitido.
        Esta validación asume que se pasa el ID de Paso1 y se cuentan los archivos ya asociados.
        """
        paso1 = data.get('paso1')
        if paso1:
            total_files = MarcoJuridico.objects.filter(paso1=paso1).count()
            if total_files >= 5:
                raise serializers.ValidationError("No se pueden asociar más de 5 archivos.")
        return data'''


class OrganigramaRegionalSerializer(serializers.ModelSerializer):
    region = serializers.SerializerMethodField()
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = OrganigramaRegional
        fields = [
            'pk',
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


class Paso1EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()

    class Meta:
        model = Paso1
        fields = [
            'pk',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
        ]

    def avance(self, obj):
        return obj.avance()

    def to_representation(self, instance):
        print("Paso1EncabezadoSerializer - Instancia:", instance)
        return super().to_representation(instance)


class FichaDescripcionOrganizacionalSerializer(serializers.ModelSerializer):
    denominacion_organismo = serializers.SerializerMethodField()

    class Meta:
        model = Paso1
        fields = [
            'pk',
            'denominacion_organismo',
            'forma_juridica_organismo',
            'descripcion_archivo_marco_juridico',
            'mision_institucional',
            'informacion_adicional_marco_juridico'
        ]

    def get_denominacion_organismo(self, obj):
        # Asegúrate de que obj es una instancia de Paso1
        if isinstance(obj, Paso1) and obj.formulario_sectorial:
            return obj.formulario_sectorial.sector.nombre
        return None


class FichaOrganizacionInstitucionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Paso1
        fields = [
            'pk',
            'organigrama_nacional',
            'descripcion_archivo_organigrama_regional'
        ]


class FichaMarcoRegulatorioFuncionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paso1
        fields = [
            'pk',
            'identificacion_competencia',
            'fuentes_normativas',
            'territorio_competencia',
            'enfoque_territorial_competencia',
            'ambito',
            'posibilidad_ejercicio_por_gobierno_regional',
            'organo_actual_competencia'
        ]


class Paso1Serializer(WritableNestedModelSerializer):
   # encabezado = Paso1EncabezadoSerializer(many=True, source='paso1_set')
    #p_1_1_ficha_descripcion_organizacional = FichaDescripcionOrganizacionalSerializer(many=True, source='paso1_set')
    marcojuridico_set = MarcoJuridicoSerializer(many=True)
    p_1_2_organizacion_institucional = FichaOrganizacionInstitucionalSerializer(many=True, source='paso1_set')
    organigramaregional_set = OrganigramaRegionalSerializer(many=True)
    p_1_3_marco_regulatorio_y_funcional_competencia = FichaMarcoRegulatorioFuncionalSerializer(many=True, source='paso1_set')

    class Meta:
        model = FormularioSectorial
        fields = [
            'pk',
            #'encabezado',
            #'p_1_1_ficha_descripcion_organizacional',
            'marcojuridico_set',
            'p_1_2_organizacion_institucional',
            'organigramaregional_set',
            'p_1_3_marco_regulatorio_y_funcional_competencia'
        ]

    def to_representation(self, instance):
        print("Paso1Serializer - Instancia FormularioSectorial:", instance)
        paso1_instance = getattr(instance, 'paso1', None)
        print("Paso1Serializer - Instancia relacionada de Paso1:", paso1_instance)
        return super().to_representation(instance)

    def create(self, validated_data):
        print("Paso1Serializer - Datos Validados en Crear:", validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        print("Paso1Serializer - Datos Validados en Actualizar:", validated_data)
        return super().update(instance, validated_data)
