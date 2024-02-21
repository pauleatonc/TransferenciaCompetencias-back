from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso3,
    CoberturaAnual
)

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


class Paso3EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso3
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'universo_cobertura',
            'descripcion_cobertura'
        ]

    def avance(self, obj):
        return obj.avance()


class Paso3Serializer(WritableNestedModelSerializer):
    paso3 = Paso3EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    cobertura_anual = CoberturaAnualSerializer(many=True)

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'paso3',
            'solo_lectura',
            'cobertura_anual',
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario Sectorial' pueden editar
            return user.perfil != 'Usuario Sectorial'

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'cobertura_anual',
        ]:
            if field_name in data:
                nested_data = data[field_name]
                internal_nested_data = []
                for item in nested_data:
                    # Manejar la clave 'DELETE' si está presente
                    if 'DELETE' in item and item['DELETE'] == True:
                        internal_nested_data.append({'id': item['id'], 'DELETE': True})
                    else:
                        item_data = self.fields[field_name].child.to_internal_value(item)
                        item_data['id'] = item.get('id')
                        internal_nested_data.append(item_data)
                internal_value[field_name] = internal_nested_data

        return internal_value


    def update_or_create_nested_instances(self, model, nested_data, instance):
        for data in nested_data:
            item_id = data.pop('id', None)
            delete_flag = data.pop('DELETE', False)

            if item_id is not None:
                if delete_flag:
                    model.objects.filter(id=item_id).delete()
                else:
                    obj, created = model.objects.update_or_create(
                        id=item_id,
                        formulario_sectorial=instance,
                        defaults=data
                    )
            elif not delete_flag:
                obj = model.objects.create(formulario_sectorial=instance, **data)

    def update_paso3_instance(self, instance, paso3_data):
        # Asume que 'paso3_data' contiene los datos del objeto relacionado
        paso3_instance = getattr(instance, 'paso3', None)
        if paso3_instance:
            for attr, value in paso3_data.items():
                setattr(paso3_instance, attr, value)
            paso3_instance.save()
        else:
            Paso3.objects.create(formulario_sectorial=instance, **paso3_data)


    def update(self, instance, validated_data):
        paso3 = validated_data.pop('paso3', None)
        cobertura_data = validated_data.pop('cobertura_anual', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear Paso3
        if paso3 is not None:
            self.update_paso3_instance(instance, paso3)

        # Actualizar o crear OrganismosIntervinientes
        if cobertura_data is not None:
            self.update_or_create_nested_instances(CoberturaAnual, cobertura_data, instance)

        return instance
