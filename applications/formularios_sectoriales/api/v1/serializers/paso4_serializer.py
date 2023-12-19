from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso4,
    IndicadorDesempeno
)
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from .base_serializer import FormularioSectorialDetailSerializer

User = get_user_model()


class IndicadorDesempenoSerializer(serializers.ModelSerializer):
    indicador_display = serializers.SerializerMethodField()
    class Meta:
        model = IndicadorDesempeno
        fields = [
            'id',
            'indicador',
            'indicador_display',
            'formula_calculo',
            'descripcion_indicador',
            'medios_calculo',
            'verificador_asociado'
        ]

    def get_indicador_display(self, obj):
        return obj.get_indicador_display()


class Paso4EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()

    class Meta:
        model = Paso4
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso4Serializer(serializers.ModelSerializer):

    paso4 = Paso4EncabezadoSerializer(many=True)
    indicador_desempeno = IndicadorDesempenoSerializer(many=True)
    lista_indicadores = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'paso4',
            'indicador_desempeno',
            'lista_indicadores',
        ]

    def get_lista_indicadores(self, obj):
        # Retornar clave y valor para choices INDICADOR
        return {clave: valor for clave, valor in IndicadorDesempeno.INDICADOR}

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
        internal_value = super(Paso4Serializer, self).to_internal_value(data)

        # Procesar campos anidados utilizando la función auxiliar
        if 'indicador_desempeno' in data:
            internal_value['indicador_desempeno'] = self.process_nested_field(
                'indicador_desempeno', data)

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
        indicador_desempeno = validated_data.pop('indicador_desempeno', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear IndicadorDesempeno
        if indicador_desempeno is not None:
            self.update_or_create_nested_instances(IndicadorDesempeno, indicador_desempeno, instance)

        return instance