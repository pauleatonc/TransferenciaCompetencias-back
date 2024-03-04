from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    MarcoJuridico,
    OrganigramaRegional,
    Paso1
)

User = get_user_model()


class MarcoJuridicoSerializer(serializers.ModelSerializer):
    documento = serializers.FileField(required=False, allow_null=True)
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = MarcoJuridico
        fields = ['id', 'documento', 'documento_url']

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
    documento = serializers.FileField(required=False, allow_null=True)
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = OrganigramaRegional
        fields = [
            'id',
            'region',
            'documento',
            'documento_url'
        ]

    def get_region(self, obj):
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
    estado_stepper = serializers.ReadOnlyField()
    denominacion_organismo = serializers.SerializerMethodField()
    organigrama_nacional = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Paso1
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'denominacion_organismo',
            'forma_juridica_organismo',
            'descripcion_archivo_marco_juridico',
            'mision_institucional',
            'informacion_adicional_marco_juridico',
            'organigrama_nacional',
            'descripcion_archivo_organigrama_nacional',
            'descripcion_archivo_organigrama_regional',
            'identificacion_competencia',
            'fuentes_normativas',
            'territorio_competencia',
            'enfoque_territorial_competencia',
            'ambito_paso1',
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
    paso1 = Paso1EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    marcojuridico = MarcoJuridicoSerializer(many=True)
    organigramaregional = OrganigramaRegionalSerializer(many=True)

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'paso1',
            'solo_lectura',
            'marcojuridico',
            'organigramaregional'
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario Sectorial' pueden editar
            return user.perfil != 'Usuario Sectorial'
        
    def update_paso1_instance(self, instance, paso1_data):
        paso1_instance = getattr(instance, 'paso1', None)
        if paso1_instance:
            for attr, value in paso1_data.items():
                setattr(paso1_instance, attr, value)
            paso1_instance.save()
        else:
            Paso1.objects.create(formulario_sectorial=instance, **paso1_data)

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)
    
        # Procesar campos anidados
        for field_name in [
            'marcojuridico',
            'organigramaregional',
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
                obj.formulario_sectorial = instance  # Asegurar que la instancia está correctamente asociada
                obj.save()  # Invoca explícitamente el método save para aplicar la validación
            elif item_id is None and not delete_flag:
                # Crear una nueva instancia y guardarla explícitamente para invocar el método save
                new_obj = model(**data)
                new_obj.formulario_sectorial = instance  # Asegurar que la instancia está correctamente asociada
                new_obj.save()
            elif delete_flag:
                model.objects.filter(id=item_id).delete()

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
            self.update_paso1_instance(instance, paso1)
    
        # Actualizar o crear MarcoJuridico
        if marco_juridico_data is not None:
            self.update_or_create_nested_instances(MarcoJuridico, marco_juridico_data, instance)
    
        # Actualizar o crear OrganigramaRegional
        if organigrama_regional_data is not None:
            self.update_or_create_nested_instances(OrganigramaRegional, organigrama_regional_data, instance)
    
        return instance
