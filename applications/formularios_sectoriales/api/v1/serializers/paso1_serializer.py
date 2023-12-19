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

    class Meta:
        model = MarcoJuridico
        fields = ['pk', 'documento', 'documento_url']

    def get_documento_url(self, obj):
        if obj.documento and hasattr(obj.documento, 'url'):
            return obj.documento.url
        return None

    def validate(self, data):
        """
        Validar que la cantidad de archivos (incluyendo los ya existentes) no exceda el máximo permitido.
        Esta validación asume que se pasa el ID de FormularioSectorial y se cuentan los archivos ya asociados.
        """
        formulario_sectorial = data.get('formulario_sectorial')
        if formulario_sectorial:
            total_files = MarcoJuridico.objects.filter(formulario_sectorial=formulario_sectorial).count()
            if total_files >= 5:
                raise serializers.ValidationError("No se pueden asociar más de 5 archivos.")
        return data


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
    denominacion_organismo = serializers.SerializerMethodField()

    class Meta:
        model = Paso1
        fields = [
            'pk',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'denominacion_organismo',
            'forma_juridica_organismo',
            'descripcion_archivo_marco_juridico',
            'mision_institucional',
            'informacion_adicional_marco_juridico',
            'organigrama_nacional',
            'descripcion_archivo_organigrama_regional',
            'identificacion_competencia',
            'fuentes_normativas',
            'territorio_competencia',
            'enfoque_territorial_competencia',
            'ambito',
            'posibilidad_ejercicio_por_gobierno_regional',
            'organo_actual_competencia'
        ]

    def avance(self, obj):
        return obj.avance()

    def get_denominacion_organismo(self, obj):
        # Asegúrate de que obj es una instancia de Paso1
        if isinstance(obj, Paso1) and obj.formulario_sectorial:
            return obj.formulario_sectorial.sector.nombre
        return None


class Paso1Serializer(WritableNestedModelSerializer):
    paso1 = Paso1EncabezadoSerializer(many=True)
    marcojuridico = MarcoJuridicoSerializer(many=True)
    organigramaregional = OrganigramaRegionalSerializer(many=True)

    class Meta:
        model = FormularioSectorial
        fields = [
            'pk',
            'paso1',
            'marcojuridico',
            'organigramaregional'
        ]


def process_nested_field(self, field_name, data):
    nested_data = data.get(field_name)
    internal_nested_data = []
    for item in nested_data:
        item_id = item.get('id')  # Extraer el ID
        item_data = self.fields[field_name].child.to_internal_value(item)
        item_data['id'] = item_id  # Asegurarse de que el ID se incluya
        internal_nested_data.append(item_data)
    return internal_nested_data


def to_internal_value(self, data):
    # Maneja primero los campos no anidados
    internal_value = super(Paso1Serializer, self).to_internal_value(data)

    # Procesar campos anidados utilizando la función auxiliar
    if 'paso1' in data:
        internal_value['paso1'] = self.process_nested_field(
            'paso1', data)

    if 'marcojuridico' in data:
        internal_value['marcojuridico'] = self.process_nested_field(
            'marcojuridico', data)

    if 'organigramaregional' in data:
        internal_value['organigramaregional'] = self.process_nested_field(
            'organigramaregional', data)

    return internal_value


def update_or_create_nested_instances(self, model, nested_data, instance):
    for data in nested_data:
        item_id = data.pop('id', None)
        if item_id is not None:
            obj, created = model.objects.update_or_create(
                id=item_id,
                formulario_sectorial=instance,
                defaults=data
            )
        else:
            model.objects.create(formulario_sectorial=instance, **data)


def update(self, instance, validated_data):
    paso1 = validated_data.pop('paso1', None)
    marco_juridico_data = validated_data.pop('marcojuridico', None)
    organigrama_regional_data = validated_data.pop('organigramaregional', None)

    # Actualizar los atributos de FormularioSectorial
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()

    # Actualizar o crear Paso1
    if paso1 is not None:
        self.update_or_create_nested_instances(Paso1, paso1, instance)

    # Actualizar o crear MarcoJuridico
    if marco_juridico_data is not None:
        self.update_or_create_nested_instances(MarcoJuridico, marco_juridico_data, instance)

    # Actualizar o crear OrganigramaRegional
    if organigrama_regional_data is not None:
        self.update_or_create_nested_instances(OrganigramaRegional, organigrama_regional_data, instance)

    return instance
