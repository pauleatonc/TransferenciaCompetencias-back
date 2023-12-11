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
    paso1 = serializers.PrimaryKeyRelatedField(queryset=Paso1.objects.all(), write_only=True)

    class Meta:
        model = MarcoJuridico
        fields = ['documento', 'documento_url', 'paso1']

    def get_documento_url(self, obj):
        if obj.documento and hasattr(obj.documento, 'url'):
            return obj.documento.url
        return None

    def validate(self, data):
        """
        Validar que la cantidad de archivos (incluyendo los ya existentes) no exceda el máximo permitido.
        Esta validación asume que se pasa el ID de Paso1 y se cuentan los archivos ya asociados.
        """
        paso1 = data.get('paso1')
        if paso1:
            total_files = MarcoJuridico.objects.filter(paso1=paso1).count()
            if total_files >= 5:
                raise serializers.ValidationError("No se pueden asociar más de 5 archivos.")
        return data

    def create(self, validated_data):
        """
        Crear un nuevo objeto MarcoJuridico.
        """
        # Aquí puedes manejar la lógica para crear un nuevo archivo
        return MarcoJuridico.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Actualizar un objeto MarcoJuridico existente.
        """
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
    marco_juridico = MarcoJuridicoSerializer(source='marcojuridico_set', many=True, required=False)

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


class FichaOrganizacionInstitucionalSerializer(serializers.ModelSerializer):
    organigrama_regional = OrganigramaRegionalSerializer(source='organigramaregional_set', many=True, required=False)
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
        # Función para procesar y validar un campo
        def process_field(field_data, serializer_class):
            if field_data is not None:
                serializer = serializer_class(data=field_data)
                if serializer.is_valid():
                    return serializer.validated_data
                else:
                    raise serializers.ValidationError(serializer.errors)

        # Deserializar campos
        ficha_desc_org_data = data.pop('p_1_1_ficha_descripcion_organizacional', None)
        ficha_org_inst_data = data.pop('p_1_2_organizacion_institucional', None)
        ficha_marco_reg_func_data = data.pop('p_1_3_marco_regulatorio_y_funcional_competencia', None)

        internal_value = super().to_internal_value(data)

        # Procesar cada campo
        internal_value['p_1_1_ficha_descripcion_organizacional'] = process_field(
            ficha_desc_org_data, FichaDescripcionOrganizacionalSerializer)

        internal_value['p_1_2_organizacion_institucional'] = process_field(
            ficha_org_inst_data, FichaOrganizacionInstitucionalSerializer)

        internal_value['p_1_3_marco_regulatorio_y_funcional_competencia'] = process_field(
            ficha_marco_reg_func_data, FichaMarcoRegulatorioFuncionalSerializer)

        return internal_value

    def update(self, instance, validated_data):
        # Función para actualizar los atributos de la instancia
        def update_instance_attributes(data):
            for attr, value in data.items():
                setattr(instance, attr, value)

        # Diccionario de claves y métodos
        update_keys = {
            'p_1_1_ficha_descripcion_organizacional': update_instance_attributes,
            'p_1_2_organizacion_institucional': update_instance_attributes,
            'p_1_3_marco_regulatorio_y_funcional_competencia': update_instance_attributes
        }

        # Iterar sobre las claves y actualizar la instancia
        for key, update_method in update_keys.items():
            data = validated_data.pop(key, {})
            update_method(data)

        # Guardar los cambios en el modelo Paso1
        instance.save()

        return instance



