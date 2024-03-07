from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso2,
    CostosDirectosGore,
    CostosIndirectosGore,
    ResumenCostosGore,
    FluctuacionPresupuestaria,
    CostoAnioGore
)

User = get_user_model()


class CostosDirectosGOREBaseSerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectosGore
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
        if obj.item_subtitulo and obj.item_subtitulo.subtitulo:
            return {'label': obj.item_subtitulo.subtitulo.subtitulo, 'value': str(obj.item_subtitulo.subtitulo.id)}
        return {'label': '', 'value': ''}

    def get_item_subtitulo_label_value(self, obj):
        if obj.item_subtitulo:
            return {'label': obj.item_subtitulo.item, 'value': str(obj.item_subtitulo.id)}
        return {'label': '', 'value': ''}

    def get_sector_nombre(self, obj):
        if obj.sector:
            return obj.sector.nombre
        return ''


class CostosDirectosSectorSerializer(CostosDirectosGOREBaseSerializer):
    pass


class PersonalDirectoSectorSerializer(CostosDirectosGOREBaseSerializer):
    pass


class CostosDirectosGoreSerializer(CostosDirectosGOREBaseSerializer):
    pass


class CostosDirectosGORESerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectosGore
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


class CostosIndirectosGORESerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosIndirectosGore
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


class ResumenCostosGORESerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumenCostosGore
        fields = '__all__'
        extra_kwargs = {'field_name': {'read_only': True} for field_name in ResumenCostosGore._meta.fields}


class CostoAnioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostoAnioGore
        fields = [
            'id',
            'anio',
            'costo',
        ]


class FluctuacionPresupuestariaSerializer(serializers.ModelSerializer):
    nombre_subtitulo = serializers.SerializerMethodField()
    costo_anio_gore = CostoAnioSerializer(many=True)
    class Meta:
        model = FluctuacionPresupuestaria
        fields = [
            'id',
            'subtitulo',
            'nombre_subtitulo',
            'costo_anio_gore',
            'descripcion',
        ]

    def get_nombre_subtitulo(self, obj):
        return obj.subtitulo.nombre_item if obj.subtitulo else None

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        if 'costo_anio' in data:
            costo_anio = data.get('costo_anio')
            internal_costo_anio = []
            for item in costo_anio:
                costo_anio_id = item.get('id')  # Extraer el ID
                costo_anio_data = self.fields['costo_anio'].child.to_internal_value(item)
                costo_anio_data['id'] = costo_anio_id  # Asegurarse de que el ID se incluya
                internal_costo_anio.append(costo_anio_data)
            internal_value['costo_anio'] = internal_costo_anio

        return internal_value


class Paso2EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()
    denominacion_region = serializers.SerializerMethodField()

    años = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paso2
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'denominacion_region',
            'años',
        ]

    def avance(self, obj):
        return obj.avance()

    def get_denominacion_region(self, obj):
        # Asegúrate de que obj es una instancia de Paso1
        if isinstance(obj, Paso2) and obj.formulario_gore:
            return obj.formulario_gore.region.region
        return None

    def get_años(self, obj):
        competencia = obj.formulario_gore.competencia
        if competencia and competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
            años = list(range(año_actual + 5, año_actual))
            return años
        return []


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
    costos_directos_sector = serializers.SerializerMethodField()
    personal_directo_sector = serializers.SerializerMethodField()
    costos_directos_gore = serializers.SerializerMethodField()
    p_2_1_b_costos_indirectos = CostosIndirectosGORESerializer(many=True, read_only=False)
    resumen_costos = ResumenCostosGORESerializer(many=True)
    p_2_1_c_fluctuaciones_presupuestarias = FluctuacionPresupuestariaSerializer(many=True, read_only=False)

    class Meta:
        model = FormularioGORE
        fields = [
            'id',
            'paso2_gore',
            'solo_lectura',
            'p_2_1_a_costos_directos',
            'costos_directos_sector',
            'personal_directo_sector',
            'costos_directos_gore',
            'p_2_1_b_costos_indirectos',
            'resumen_costos',
            'p_2_1_c_fluctuaciones_presupuestarias',
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

    def get_costos_directos_sector(self, obj):
        queryset = CostosDirectosGore.objects.filter(formulario_gore=obj, sector__isnull=False).exclude(
            item_subtitulo__subtitulo__subtitulo='Sub. 21')
        return CostosDirectosSectorSerializer(queryset, many=True).data

    def get_personal_directo_sector(self, obj):
        queryset = CostosDirectosGore.objects.filter(formulario_gore=obj,
                                                     item_subtitulo__subtitulo__subtitulo='Sub. 21')
        return PersonalDirectoSectorSerializer(queryset, many=True).data

    def get_costos_directos_gore(self, obj):
        queryset = CostosDirectosGore.objects.filter(formulario_gore=obj, sector__isnull=True)
        return CostosDirectosGoreSerializer(queryset, many=True).data

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'p_2_1_a_costos_directos',
            'p_2_1_b_costos_indirectos',
            'p_2_1_c_fluctuaciones_presupuestarias',
        ]:
            if field_name in data:
                nested_data = data[field_name]
                internal_nested_data = []
                for item in nested_data:
                    # Manejar la clave 'DELETE' si está presente
                    if 'DELETE' in item and item['DELETE'] == True:
                        if field_name == 'p_2_1_a_costos_directos':
                            eliminar_instancia_costo(CostosDirectosGore, item['id'])
                        elif field_name == 'p_2_1_b_costos_indirectos':
                            eliminar_instancia_costo(CostosIndirectosGore, item['id'])
                        elif field_name == 'p_2_1_c_fluctuaciones_presupuestarias':
                            eliminar_instancia_costo(FluctuacionPresupuestaria, item['id'])
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
        costos_indirectos_data = validated_data.pop('p_2_1_b_costos_indirectos', None)
        fluctuaciones_presupuestarias_data = validated_data.pop('p_2_1_c_fluctuaciones_presupuestarias', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear Paso1
        if paso2 is not None:
            self.update_paso2_instance(instance, paso2)

        # Actualizar o crear CostosDirectos
        if costos_directos_data is not None:
            self.update_or_create_nested_instances(CostosDirectosGore, costos_directos_data, instance)

        # Actualizar o crear CostosIndirectos
        if costos_indirectos_data is not None:
            self.update_or_create_nested_instances(CostosIndirectosGore, costos_indirectos_data, instance)

        # Actualizar o crear FluctuacionPresupuestaria
        if fluctuaciones_presupuestarias_data is not None:
            for fluctuacion_data in fluctuaciones_presupuestarias_data:
                fluctuacion_id = fluctuacion_data.pop('id', None)
                costo_anio_data = fluctuacion_data.pop('costo_anio_gore', [])

                fluctuacion_instance, _ = FluctuacionPresupuestaria.objects.update_or_create(
                    id=fluctuacion_id,
                    defaults=fluctuacion_data,
                    formulario_sectorial=instance
                )

                for costo_data in costo_anio_data:
                    costo_id = costo_data.pop('id', None)
                    costo_data['evolucion_gasto'] = fluctuacion_instance
                    CostoAnioGore.objects.update_or_create(
                        id=costo_id,
                        defaults=costo_data
                    )

        return instance
