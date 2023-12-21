from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso3,
    CoberturaAnual
)
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from .base_serializer import FormularioSectorialDetailSerializer

User = get_user_model()


class CoberturaAnualSerializer(serializers.ModelSerializer):
    total_cobertura_efectiva = serializers.SerializerMethodField()

    class Meta:
        model = CoberturaAnual
        fields = [
            'id',
            'anio',
            'universo_cobertura',
            'cobertura_efectivamente_abordada',
            'recursos_ejecutados',
            'total_cobertura_efectiva'
        ]

    def total_cobertura_efectiva(self, obj):
        return obj.total_cobertura_efectiva()

    def update(self, instance, validated_data):
        print("Actualizar CoberturaAnual:", instance, validated_data)
        return super().update(instance, validated_data)


class Paso3EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()

    class Meta:
        model = Paso3
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'universo_cobertura',
            'descripcion_cobertura'
        ]

    def avance(self, obj):
        return obj.avance()


class Paso3Serializer(serializers.ModelSerializer):

    paso3 = Paso3EncabezadoSerializer(many=True)
    cobertura_anual = CoberturaAnualSerializer(many=True)

    class Meta:
        model = FormularioSectorial
        fields = [
            'paso3',
            'cobertura_anual',
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
        internal_value = super(Paso3Serializer, self).to_internal_value(data)

        # Procesar campos anidados utilizando la función auxiliar
        if 'paso3' in data:
            internal_value['paso3'] = self.process_nested_field(
                'paso3', data)

        if 'cobertura_anual' in data:
            internal_value['cobertura_anual'] = self.process_nested_field(
                'cobertura_anual', data)

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
        paso3 = validated_data.pop('paso3', None)
        cobertura_data = validated_data.pop('cobertura_anual', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear Paso3
        if paso3 is not None:
            self.update_or_create_nested_instances(Paso3, paso3, instance)

        # Actualizar o crear OrganismosIntervinientes
        if cobertura_data is not None:
            self.update_or_create_nested_instances(CoberturaAnual, cobertura_data, instance)

        return instance