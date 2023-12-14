from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, OrganismosIntervinientes, \
    UnidadesIntervinientes
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.formularios_sectoriales.models import Paso2
from .base_serializer import FormularioSectorialDetailSerializer

User = get_user_model()


class OrganismosIntervinientesSerializer(serializers.ModelSerializer):
    organismo_display = serializers.SerializerMethodField()

    class Meta:
        model = OrganismosIntervinientes
        fields = [
            'id',
            'organismo',
            'organismo_display',
            'sector_ministerio_servicio',
            'descripcion'
        ]

    def get_organismo_display(self, obj):
        return obj.get_organismo_display()

    def create(self, validated_data):
        # Lógica para crear una nueva instancia
        print("Creando OrganismoInterviniente con datos:", validated_data)
        return OrganismosIntervinientes.objects.create(**validated_data)

    def update(self, instance, validated_data):
        print("Actualizando OrganismoInterviniente, instancia:", instance, "con datos:", validated_data)
        # Actualizar los campos de la instancia existente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UnidadesIntervinientesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnidadesIntervinientes
        fields = [
            'id',
            'nombre_unidad',
            'descripcion_unidad'
        ]


class Paso2EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()

    class Meta:
        model = Paso2
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso2Serializer(serializers.ModelSerializer):

    encabezado = Paso2EncabezadoSerializer(source='paso2', required=False)
    p_2_1_organismos_intervinientes = OrganismosIntervinientesSerializer(many=True, read_only=False)
    p_2_2_unidades_intervinientes = UnidadesIntervinientesSerializer(many=True, read_only=False)

    class Meta:
        model = FormularioSectorial
        fields = [
            'encabezado',
            'p_2_1_organismos_intervinientes',
            'p_2_2_unidades_intervinientes'
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
        internal_value = super(Paso2Serializer, self).to_internal_value(data)

        # Procesar campos anidados utilizando la función auxiliar
        if 'p_2_1_organismos_intervinientes' in data:
            internal_value['p_2_1_organismos_intervinientes'] = self.process_nested_field(
                'p_2_1_organismos_intervinientes', data)

        if 'p_2_2_unidades_intervinientes' in data:
            internal_value['p_2_2_unidades_intervinientes'] = self.process_nested_field('p_2_2_unidades_intervinientes',
                                                                                        data)
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
        organismos_data = validated_data.pop('p_2_1_organismos_intervinientes', None)
        unidades_data = validated_data.pop('p_2_2_unidades_intervinientes', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear OrganismosIntervinientes
        if organismos_data is not None:
            self.update_or_create_nested_instances(OrganismosIntervinientes, organismos_data, instance)

        # Similar para UnidadesIntervinientes
        if unidades_data is not None:
            self.update_or_create_nested_instances(UnidadesIntervinientes, unidades_data, instance)

        # Repetir para otros modelos relacionados

        return instance