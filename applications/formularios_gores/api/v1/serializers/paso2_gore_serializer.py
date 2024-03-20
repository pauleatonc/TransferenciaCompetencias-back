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
from applications.formularios_sectoriales.models import ItemSubtitulo, Subtitulos, EtapasEjercicioCompetencia, \
    FormularioSectorial

from applications.formularios_sectoriales.api.v1.serializers import ItemSubtituloSerializer, SubtitulosSerializer

User = get_user_model()


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

        if 'costo_anio_gore' in data:
            costo_anio = data.get('costo_anio_gore')
            internal_costo_anio = []
            for item in costo_anio:
                costo_anio_id = item.get('id')  # Extraer el ID
                costo_anio_data = self.fields['costo_anio_gore'].child.to_internal_value(item)
                costo_anio_data['id'] = costo_anio_id  # Asegurarse de que el ID se incluya
                internal_costo_anio.append(costo_anio_data)
            internal_value['costo_anio_gore'] = internal_costo_anio

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


def get_subtitulos_disponibles(modelo_costos, formulario_obj):
    # Obtiene todos los ID de ItemSubtitulo utilizados por el modelo_costos para este formulario
    # Asegura que solo se consideren las instancias con un item_subtitulo definido
    items_utilizados = modelo_costos.objects.filter(
        formulario_gore=formulario_obj, item_subtitulo__isnull=False
    ).values_list('item_subtitulo__id', flat=True)

    # Filtra ItemSubtitulo para excluir los utilizados
    item_subtitulos_disponibles = ItemSubtitulo.objects.exclude(id__in=items_utilizados)

    # Obtiene los Subtitulos asociados a los item_subtitulos disponibles
    subtitulos_ids = item_subtitulos_disponibles.values_list('subtitulo__id', flat=True).distinct()
    subtitulos_disponibles = Subtitulos.objects.filter(id__in=subtitulos_ids)

    return subtitulos_disponibles



def get_item_subtitulos_disponibles_y_agrupados(modelo_costos, formulario_obj):
    # Obtiene todos los ID de ItemSubtitulo utilizados por el modelo de costos para este formulario
    # Asegura que solo se consideren las instancias con un item_subtitulo definido
    items_utilizados = modelo_costos.objects.filter(
        formulario_gore=formulario_obj, item_subtitulo__isnull=False
    ).values_list('item_subtitulo__id', flat=True)

    # Filtra ItemSubtitulo para excluir los utilizados
    item_subtitulos_disponibles = ItemSubtitulo.objects.exclude(id__in=items_utilizados).select_related('subtitulo')

    # Agrupa los ItemSubtitulo disponibles por Subtitulos
    items_agrupados = {}
    for item in item_subtitulos_disponibles:
        subtitulo = item.subtitulo.subtitulo
        if subtitulo not in items_agrupados:
            items_agrupados[subtitulo] = []
        items_agrupados[subtitulo].append(ItemSubtituloSerializer(item).data)

    return items_agrupados



class Paso2Serializer(WritableNestedModelSerializer):
    paso2_gore = Paso2EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    p_2_1_a_costos_directos = CostosDirectosGORESerializer(many=True, read_only=False)
    costos_directos_sector = serializers.SerializerMethodField()
    personal_directo_sector = serializers.SerializerMethodField()
    costos_directos_gore = serializers.SerializerMethodField()
    p_2_1_b_costos_indirectos = CostosIndirectosGORESerializer(many=True, read_only=False)
    costos_indirectos_sector = serializers.SerializerMethodField()
    personal_indirecto_sector = serializers.SerializerMethodField()
    costos_indirectos_gore = serializers.SerializerMethodField()
    resumen_costos = ResumenCostosGORESerializer(many=True)
    p_2_1_c_fluctuaciones_presupuestarias = FluctuacionPresupuestariaSerializer(many=True, read_only=False)
    listado_subtitulos_directos = serializers.SerializerMethodField()
    listado_subtitulos_indirectos = serializers.SerializerMethodField()
    listado_item_subtitulos_directos = serializers.SerializerMethodField()
    listado_item_subtitulos_indirectos = serializers.SerializerMethodField()
    listado_etapas = serializers.SerializerMethodField()

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
            'costos_indirectos_sector',
            'personal_indirecto_sector',
            'costos_indirectos_gore',
            'resumen_costos',
            'p_2_1_c_fluctuaciones_presupuestarias',
            'listado_subtitulos_directos',
            'listado_subtitulos_indirectos',
            'listado_item_subtitulos_directos',
            'listado_item_subtitulos_indirectos',
            'listado_etapas'

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

    def filtrar_queryset_por_obj(self, modelo, obj, subtitulo_excluir, incluir_sector):
        # Filtro previo de los queryset
        if incluir_sector:
            return modelo.objects.filter(formulario_gore=obj, sector__isnull=False).exclude(
                item_subtitulo__subtitulo__subtitulo=subtitulo_excluir).select_related('sector')
        else:
            return modelo.objects.filter(formulario_gore=obj,
                                         item_subtitulo__subtitulo__subtitulo=subtitulo_excluir).select_related(
                'sector')

    def serializar_y_agrupar_por_sector(self, queryset, serializer_cls):
        # Agrupación de los objetos por sector y serialización
        agrupados_por_sector = {}
        for item in queryset:
            if item.sector is None:
                continue  # Omitimos los que no tienen sector
            sector_nombre = item.sector.nombre
            if sector_nombre not in agrupados_por_sector:
                agrupados_por_sector[sector_nombre] = []
            agrupados_por_sector[sector_nombre].append(item)

        # Ahora, cada sector será una clave en el resultado
        resultado = []
        for sector_nombre, items in agrupados_por_sector.items():
            data_serializada = serializer_cls(items, many=True).data
            sector_dict = {'sector': sector_nombre, 'items': data_serializada}
            resultado.append(sector_dict)

        return resultado

    def get_items_por_sector(self, obj, modelo, serializer_cls, subtitulo_excluir=None, incluir_sector=True):
        # Obtención del queryset y llamada a la función de agrupación/serialización
        queryset = self.filtrar_queryset_por_obj(modelo, obj, subtitulo_excluir, incluir_sector)
        return self.serializar_y_agrupar_por_sector(queryset, serializer_cls)

    def get_costos_directos_sector(self, obj):
        return self.get_items_por_sector(obj, CostosDirectosGore, CostosDirectosGORESerializer, 'Sub. 21')

    def get_costos_indirectos_sector(self, obj):
        return self.get_items_por_sector(obj, CostosIndirectosGore, CostosIndirectosGORESerializer, 'Sub. 21')

    def get_personal_directo_sector(self, obj):
        return self.get_items_por_sector(obj, CostosDirectosGore, CostosDirectosGORESerializer, 'Sub. 21', False)

    def get_personal_indirecto_sector(self, obj):
        return self.get_items_por_sector(obj, CostosIndirectosGore, CostosIndirectosGORESerializer, 'Sub. 21', False)


    def get_costos_directos_gore(self, obj):
        queryset = CostosDirectosGore.objects.filter(formulario_gore=obj, sector__isnull=True)
        return CostosDirectosGORESerializer(queryset, many=True).data

    def get_costos_indirectos_gore(self, obj):
        queryset = CostosIndirectosGore.objects.filter(formulario_gore=obj, sector__isnull=True)
        return CostosIndirectosGORESerializer(queryset, many=True).data

    def get_listado_item_subtitulos_directos(self, obj):
        items_agrupados_directos = get_item_subtitulos_disponibles_y_agrupados(CostosDirectosGore, obj)
        return items_agrupados_directos

    def get_listado_item_subtitulos_indirectos(self, obj):
        items_agrupados_indirectos = get_item_subtitulos_disponibles_y_agrupados(CostosIndirectosGore, obj)
        return items_agrupados_indirectos

    def get_listado_subtitulos_directos(self, obj):
        subtitulos_disponibles = get_subtitulos_disponibles(CostosDirectosGore, obj)
        return SubtitulosSerializer(subtitulos_disponibles, many=True).data

    def get_listado_subtitulos_indirectos(self, obj):
        subtitulos_disponibles = get_subtitulos_disponibles(CostosIndirectosGore, obj)
        return SubtitulosSerializer(subtitulos_disponibles, many=True).data

    def get_listado_etapas(self, obj):
        # obj es una instancia de FormularioGORE
        competencia = obj.competencia

        # Usamos la competencia para encontrar todos los formularios sectoriales relacionados
        formularios_sectoriales = FormularioSectorial.objects.filter(competencia=competencia)

        # Luego, usamos esos formularios sectoriales para filtrar las etapas
        etapas = EtapasEjercicioCompetencia.objects.filter(formulario_sectorial__in=formularios_sectoriales)

        return [{'id': etapa.id, 'nombre_etapa': etapa.nombre_etapa, 'descripcion_etapa': etapa.descripcion_etapa} for
                etapa in etapas]

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
                    formulario_gore=instance
                )

                for costo_data in costo_anio_data:
                    costo_id = costo_data.pop('id', None)
                    costo_data['evolucion_gasto'] = fluctuacion_instance
                    CostoAnioGore.objects.update_or_create(
                        id=costo_id,
                        defaults=costo_data
                    )

        return instance
