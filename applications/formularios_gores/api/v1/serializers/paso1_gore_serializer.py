from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_gores.models import (
    FormularioGORE,
    FlujogramaEjercicioCompetencia,
    Paso1
)

User = get_user_model()

class FlujogramaEjercicioCompetenciaSerializer(serializers.ModelSerializer):
    documento = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = FlujogramaEjercicioCompetencia
        fields = [
            'id',
            'documento',
        ]


class Paso1EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()
    denominacion_region = serializers.SerializerMethodField()
    organigrama_gore = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Paso1
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'denominacion_region',
            'descripcion_ejercicio_competencia',
            'organigrama_gore',
            'descripcion_organigrama_gore',
        ]

    def avance(self, obj):
        return obj.avance()

    def get_denominacion_region(self, obj):
        # Asegúrate de que obj es una instancia de Paso1
        if isinstance(obj, Paso1) and obj.formulario_gore:
            return obj.formulario_gore.region.region
        return None


class Paso1Serializer(WritableNestedModelSerializer):
    paso1_gore = Paso1EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    flujograma_ejercicio_competencia = FlujogramaEjercicioCompetenciaSerializer(many=True)

    class Meta:
        model = FormularioGORE
        fields = [
            'id',
            'paso1_gore',
            'solo_lectura',
            'flujograma_ejercicio_competencia',
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario GORE' pueden editar
            return user.perfil != 'GORE'

    def update_paso1_instance(self, instance, paso1_data):
        paso1_instance = getattr(instance, 'paso1', None)
        if paso1_instance:
            for attr, value in paso1_data.items():
                setattr(paso1_instance, attr, value)
            paso1_instance.save()
        else:
            Paso1.objects.create(formulario_gore=instance, **paso1_data)

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'flujograma_ejercicio_competencia',
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
        paso1 = validated_data.pop('paso1', None)
        flujograma_competencia_data = validated_data.pop('flujogramaejerciciocompetencia', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear Paso1
        if paso1 is not None:
            self.update_paso1_instance(instance, paso1)

        # Actualizar o crear FlujogramaCompetencia
        if flujograma_competencia_data is not None:
            self.update_or_create_nested_instances(FlujogramaEjercicioCompetencia, flujograma_competencia_data, instance)

        return instance
