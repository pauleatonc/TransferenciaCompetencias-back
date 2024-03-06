from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso2,
    CostosDirectosGore as CostosDirectosGORE,
    CostosIndirectosGore as CostosIndirectosGORE,
)

User = get_user_model()


class CostosDirectosGORESerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectosGORE
        fields = [
            'id',
            'sector',
            'sector_nombre',
            'subtitulo_label_value',
            'item_subtitulo',
            'item_subtitulo_label_value',
            'total_anual_sector',
            'total_anual_gore',
            'diferencia_monto',
            'es_transitorio',
            'descripcion',
        ]

    def get_subtitulo_label_value(self, obj):
        # obj es una instancia de CostosDirectos
        if obj.item_subtitulo and obj.item_subtitulo.subtitulo:
            return {
                'label': obj.item_subtitulo.subtitulo.subtitulo,
                'value': str(obj.item_subtitulo.subtitulo.id)
            }
        return {'label': '', 'value': ''}

    def get_item_subtitulo_label_value(self, obj):
        # Método para el campo personalizado de item_subtitulo
        if obj.item_subtitulo:
            return {
                'label': obj.item_subtitulo.item,
                'value': str(obj.item_subtitulo.id)
            }
        return {'label': '', 'value': ''}

    def get_sector_nombre(self, obj):
        # Método para el campo personalizado de sector
        if obj.sector:
            return obj.sector.nombre
        return ''


class Paso2EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()
    denominacion_region = serializers.SerializerMethodField()

    class Meta:
        model = Paso2
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'denominacion_region'
        ]

    def avance(self, obj):
        return obj.avance()

    def get_denominacion_region(self, obj):
        # Asegúrate de que obj es una instancia de Paso1
        if isinstance(obj, Paso2) and obj.formulario_gore:
            return obj.formulario_gore.region.region
        return None


def eliminar_instancia_costo(modelo, instancia_id):
    try:
        instancia = modelo.objects.get(id=instancia_id)
        instancia.delete()  # Esto disparará la señal post_delete
    except modelo.DoesNotExist:
        pass


class Paso2Serializer(WritableNestedModelSerializer):
    paso2_gore = Paso2EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    p_2_1_a_costos_directos = CostosDirectosGORESerializer(many=True, read_only=False)

    class Meta:
        model = FormularioGORE
        fields = [
            'id',
            'paso2_gore',
            'solo_lectura',
            'p_2_1_a_costos_directos',
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario GORE' pueden editar
            return user.perfil != 'GORE'

    def update_paso2_instance(self, instance, paso2_data):
        paso2_instance = getattr(instance, 'paso2', None)
        if paso2_instance:
            for attr, value in paso2_data.items():
                setattr(paso2_instance, attr, value)
            paso2_instance.save()
        else:
            Paso2.objects.create(formulario_gore=instance, **paso2_data)

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'p_2_1_a_costos_directos',
        ]:
            if field_name in data:
                nested_data = data[field_name]
                internal_nested_data = []
                for item in nested_data:
                    # Manejar la clave 'DELETE' si está presente
                    if 'DELETE' in item and item['DELETE'] == True:
                        if field_name == 'p_2_1_a_costos_directos':
                            eliminar_instancia_costo(CostosDirectosGORE, item['id'])
                        else:
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

            if item_id is not None and not delete_flag:
                obj = model.objects.get(id=item_id)
                for attr, value in data.items():
                    setattr(obj, attr, value)
                obj.formulario_gore = instance  # Asegurar que la instancia está correctamente asociada
                obj.save()  # Invoca explícitamente el método save para aplicar la validación
            elif item_id is None and not delete_flag:
                # Crear una nueva instancia y guardarla explícitamente para invocar el método save
                new_obj = model(**data)
                new_obj.formulario_gore = instance  # Asegurar que la instancia está correctamente asociada
                new_obj.save()
            elif delete_flag:
                model.objects.filter(id=item_id).delete()

    def update(self, instance, validated_data):
        paso2 = validated_data.pop('paso2', None)
        costos_directos_data = validated_data.pop('p_2_1_a_costos_directos', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear Paso1
        if paso2 is not None:
            self.update_paso2_instance(instance, paso2)

        # Actualizar o crear CostosDirectos
        if costos_directos_data is not None:
            self.update_or_create_nested_instances(CostosDirectosGORE, costos_directos_data, instance)

        return instance
