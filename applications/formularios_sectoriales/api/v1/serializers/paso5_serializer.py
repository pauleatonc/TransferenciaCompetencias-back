from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso5,
    Subtitulos,
    ItemSubtitulo,
    CostosDirectos,
    CostosIndirectos,
    ResumenCostosPorSubtitulo,
    CostoAnio,
    EvolucionGastoAsociado,
    VariacionPromedio
)
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from .base_serializer import FormularioSectorialDetailSerializer

User = get_user_model()


class SubtitulosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtitulos
        fields = [
            'id',
            'subtitulo',
        ]

class ItemSubtituloSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemSubtitulo
        fields = [
            'id',
            'item',
        ]


class CostosDirectosSerializer(serializers.ModelSerializer):
    nombre_item_subtitulo = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectos
        fields = [
            'id',
            'etapa',
            'item_subtitulo',
            'nombre_item_subtitulo',
            'total_anual',
            'es_transversal',
            'descripcion',
        ]

    def get_nombre_item_subtitulo(self, obj):
        return obj.item_subtitulo.nombre_item if obj.item_subtitulo else None

class CostosIndirectosSerializer(serializers.ModelSerializer):
    nombre_item_subtitulo = serializers.SerializerMethodField()
    class Meta:
        model = CostosIndirectos
        fields = [
            'id',
            'etapa',
            'item_subtitulo',
            'nombre_item_subtitulo',
            'total_anual',
            'es_transversal',
            'descripcion',
        ]

    def get_nombre_item_subtitulo(self, obj):
        return obj.item_subtitulo.nombre_item if obj.item_subtitulo else None


class  ResumenCostosPorSubtituloSerializer(serializers.ModelSerializer):
    nombre_subtitulo = serializers.SerializerMethodField()
    class Meta:
        model = ResumenCostosPorSubtitulo
        fields = [
            'id',
            'subtitulo',
            'nombre_subtitulo',
            'total_anual',
            'descripcion',
        ]

    def get_nombre_subtitulo(self, obj):
        return obj.subtitulo.nombre_item if obj.subtitulo else None


class CostoAnioSerializer(serializers.ModelSerializer):
    class  Meta:
        model = CostoAnio
        fields = [
            'id',
            'anio',
            'costo',
        ]


class EvolucionGastoAsociadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvolucionGastoAsociado
        fields = [
            'id',
            'subtitulo',
            'costo_anio',
            'descripcion',
        ]

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


class VariacionPromedioSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariacionPromedio
        fields = [
            'id',
            'subtitulo',
            'gasto_n_5',
            'gasto_n_1',
            'variacion',
            'descripcion',
        ]


class Paso5EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()

    class Meta:
        model = Paso5
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'total_costos_directos',
            'total_costos_indirectos',
            'costos_totales',
            'glosas_especificas',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso5Serializer(serializers.ModelSerializer):
    paso5 = Paso5EncabezadoSerializer(many=True, read_only=False)
    listado_subtitulos = serializers.SerializerMethodField()
    listado_item_subtitulos = serializers.SerializerMethodField()
    p_5_1_a_costos_directos = CostosDirectosSerializer(many=True, read_only=False)
    p_5_1_b_costos_indirectos = CostosIndirectosSerializer(many=True, read_only=False)
    p_5_1_c_resumen_costos_por_subtitulo = ResumenCostosPorSubtituloSerializer(many=True, read_only=False)
    p_5_2_evolucion_gasto_asociado = EvolucionGastoAsociadoSerializer(many=True, read_only=False)
    p_5_2_variacion_promedio = VariacionPromedioSerializer(many=True, read_only=False)

    class Meta:
        model = FormularioSectorial
        fields = [
            'paso5',
            'p_5_1_a_costos_directos',
            'p_5_1_b_costos_indirectos',
            'p_5_1_c_resumen_costos_por_subtitulo',
            'p_5_2_evolucion_gasto_asociado',
            'p_5_2_variacion_promedio',
            'listado_subtitulos',
            'listado_item_subtitulos',
        ]

    def get_listado_subtitulos(self, obj):
        # Obtener todos los registros de Subtitulos y serializarlos
        subtitulos = Subtitulos.objects.all()
        return SubtitulosSerializer(subtitulos, many=True).data

    def get_listado_item_subtitulos(self, obj):
        # Agrupar ItemSubtitulo por Subtitulos
        items_agrupados = {}
        for item in ItemSubtitulo.objects.all().select_related('subtitulo'):
            subtitulo = item.subtitulo.subtitulo
            if subtitulo not in items_agrupados:
                items_agrupados[subtitulo] = []
            items_agrupados[subtitulo].append(ItemSubtituloSerializer(item).data)

        return items_agrupados

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
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados utilizando la función auxiliar
        if 'p_5_1_a_costos_directos' in data:
            internal_value['p_5_1_a_costos_directos'] = self.process_nested_field(
                'p_5_1_a_costos_directos', data)

        if 'p_5_1_b_costos_indirectos' in data:
            internal_value['p_5_1_b_costos_indirectos'] = self.process_nested_field(
                'p_5_1_b_costos_indirectos', data)

        if  'p_5_1_c_resumen_costos_por_subtitulo' in data:
            internal_value['p_5_1_c_resumen_costos_por_subtitulo'] = self.process_nested_field(
                'p_5_1_c_resumen_costos_por_subtitulo', data)

        if 'p_5_2_evolucion_gasto_asociado' in data:
            internal_value['p_5_2_evolucion_gasto_asociado'] = self.process_nested_field(
                'p_5_2_evolucion_gasto_asociado', data)

        if 'p_5_2_variacion_promedio' in data:
            internal_value['p_5_2_variacion_promedio'] = self.process_nested_field(
                'p_5_2_variacion_promedio', data)

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
        costos_directos_data = validated_data.pop('p_5_1_a_costos_directos', None)
        costos_indirectos_data = validated_data.pop('p_5_1_b_costos_indirectos', None)
        resumen_costos_data = validated_data.pop('p_5_1_c_resumen_costos_por_subtitulo', None)
        evolucion_gasto_data = validated_data.pop('p_5_2_evolucion_gasto_asociado', None)
        variacion_promedio_data = validated_data.pop('p_5_2_variacion_promedio', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear CostosDirectos
        if costos_directos_data is not None:
            self.update_or_create_nested_instances(CostosDirectos, costos_directos_data, instance)

        # Actualizar o crear CostosIndirectos
        if costos_indirectos_data is not None:
            self.update_or_create_nested_instances(CostosIndirectos, costos_indirectos_data, instance)

        # Actualizar o crear ResumenCostosPorSubtitulo
        if resumen_costos_data is not None:
            self.update_or_create_nested_instances(ResumenCostosPorSubtitulo, resumen_costos_data, instance)

        # Actualizar o crear EvolucionGastoAsociado
        if evolucion_gasto_data is not None:
            for evolucion_gasto_data in evolucion_gasto_data:
                evolucion_gasto_id = evolucion_gasto_data.pop('id', None)
                costo_anio_data = evolucion_gasto_data.pop('costo_anio', [])

                evolucion_gasto_instance, _ = EvolucionGastoAsociado.objects.update_or_create(
                    id=evolucion_gasto_id,
                    defaults=evolucion_gasto_data,
                    formulario_sectorial=instance
                )

                for costo_data in costo_anio_data:
                    costo_id = costo_data.pop('id', None)
                    costo_data['evolucion_gasto_asociado'] = evolucion_gasto_instance
                    CostoAnio.objects.update_or_create(
                        id=costo_id,
                        defaults=costo_data
                    )
        # Actualizar o crear EvolucionGastoAsociado
        if evolucion_gasto_data is not None:
            self.update_or_create_nested_instances(EvolucionGastoAsociado, evolucion_gasto_data, instance)

        # Actualizar o crear VariacionPromedio
        if variacion_promedio_data is not None:
            self.update_or_create_nested_instances(VariacionPromedio, variacion_promedio_data, instance)

        return instance