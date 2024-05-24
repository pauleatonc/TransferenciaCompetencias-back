from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from applications.competencias.models import Competencia
import logging
from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso5Encabezado,
    Paso5,
    Subtitulos,
    ItemSubtitulo,
    CostosDirectos,
    CostosIndirectos,
    ResumenCostosPorSubtitulo,
    CostoAnio,
    EvolucionGastoAsociado,
    VariacionPromedio,
    Estamento,
    CalidadJuridica,
    PersonalDirecto,
    PersonalIndirecto,
    EtapasEjercicioCompetencia
)

from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from .base_serializer import FormularioSectorialDetailSerializer

User = get_user_model()

logger = logging.getLogger(__name__)


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
    id = serializers.IntegerField(required=False, allow_null=True)
    DELETE = serializers.BooleanField(required=False, default=False)
    subtitulo_label_value = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()
    etapa_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectos
        fields = [
            'id',
            'DELETE',
            'subtitulo',
            'subtitulo_label_value',
            'item_subtitulo',
            'item_subtitulo_label_value',
            'etapa',
            'etapa_label_value',
            'total_anual',
            'es_transversal',
            'descripcion',
        ]

    def get_subtitulo_label_value(self, obj):
        # obj es una instancia de CostosDirectos
        if obj.subtitulo and obj.subtitulo.subtitulo:
            return {
                'label': obj.subtitulo.subtitulo,
                'value': str(obj.subtitulo.id)
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

    def get_etapa_label_value(self, obj):
        # Obtiene todas las etapas asociadas y las transforma al formato {label, value}
        return [{
            'label': etapa.nombre_etapa,  # Usamos nombre_etapa para el label
            'value': str(etapa.id)  # El ID de la etapa como value
        } for etapa in obj.etapa.all()]


class CostosIndirectosSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    DELETE = serializers.BooleanField(required=False, default=False)
    subtitulo_label_value = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()
    etapa_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectos
        fields = [
            'id',
            'DELETE',
            'subtitulo',
            'subtitulo_label_value',
            'item_subtitulo',
            'item_subtitulo_label_value',
            'etapa',
            'etapa_label_value',
            'total_anual',
            'es_transversal',
            'descripcion',
        ]

    def get_subtitulo_label_value(self, obj):
        # obj es una instancia de CostosDirectos
        if obj.subtitulo and obj.subtitulo.subtitulo:
            return {
                'label': obj.subtitulo.subtitulo,
                'value': str(obj.subtitulo.id)
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

    def get_etapa_label_value(self, obj):
        # Obtiene todas las etapas asociadas y las transforma al formato {label, value}
        return [{
            'label': etapa.nombre_etapa,  # Usamos nombre_etapa para el label
            'value': str(etapa.id)  # El ID de la etapa como value
        } for etapa in obj.etapa.all()]


class ResumenCostosPorSubtituloSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = CostoAnio
        fields = [
            'id',
            'anio',
            'costo',
        ]


class EvolucionGastoAsociadoSerializer(serializers.ModelSerializer):
    nombre_subtitulo = serializers.SerializerMethodField()
    costo_anio = CostoAnioSerializer(many=True)

    class Meta:
        model = EvolucionGastoAsociado
        fields = [
            'id',
            'subtitulo',
            'nombre_subtitulo',
            'costo_anio',
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


class VariacionPromedioSerializer(serializers.ModelSerializer):
    nombre_subtitulo = serializers.SerializerMethodField()

    class Meta:
        model = VariacionPromedio
        fields = [
            'id',
            'subtitulo',
            'nombre_subtitulo',
            'variacion_gasto_n_5',
            'variacion_gasto_n_4',
            'variacion_gasto_n_3',
            'variacion_gasto_n_2',
            'descripcion',
        ]

    def get_nombre_subtitulo(self, obj):
        return obj.subtitulo.nombre_item if obj.subtitulo else None


class CalidadJuridicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalidadJuridica
        fields = [
            'id',
            'calidad_juridica',
        ]


class EstamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estamento
        fields = [
            'id',
            'estamento',
        ]


class PersonalDirectoSerializer(serializers.ModelSerializer):
    calidad_juridica = serializers.PrimaryKeyRelatedField(queryset=CalidadJuridica.objects.all())
    estamento = serializers.PrimaryKeyRelatedField(queryset=Estamento.objects.all())
    nombre_estamento = serializers.SerializerMethodField()
    calidad_juridica_label_value = serializers.SerializerMethodField()
    nombre_calidad_juridica = serializers.SerializerMethodField()
    estamento_label_value = serializers.SerializerMethodField()

    class Meta:
        model = PersonalDirecto
        fields = [
            'id',
            'estamento',
            'nombre_estamento',
            'estamento_label_value',
            'calidad_juridica',
            'nombre_calidad_juridica',
            'calidad_juridica_label_value',
            'renta_bruta',
            'grado',
        ]

    def get_nombre_estamento(self, obj):
        return obj.estamento.estamento if obj.estamento else None

    def get_estamento_label_value(self, obj):
        # Método para el campo personalizado de item_subtitulo
        if obj.estamento:
            return {
                'label': obj.estamento.estamento,
                'value': str(obj.estamento.id)
            }
        return {'label': '', 'value': ''}

    def get_nombre_calidad_juridica(self, obj):
        return obj.calidad_juridica.calidad_juridica if obj.calidad_juridica else None

    def get_calidad_juridica_label_value(self, obj):
        if obj.calidad_juridica:
            return {
                'label': obj.calidad_juridica.calidad_juridica,
                'value': str(obj.calidad_juridica.id)
            }


class PersonalIndirectoSerializer(serializers.ModelSerializer):
    calidad_juridica = serializers.PrimaryKeyRelatedField(queryset=CalidadJuridica.objects.all())
    estamento = serializers.PrimaryKeyRelatedField(queryset=Estamento.objects.all())
    nombre_estamento = serializers.SerializerMethodField()
    calidad_juridica_label_value = serializers.SerializerMethodField()
    nombre_calidad_juridica = serializers.SerializerMethodField()
    estamento_label_value = serializers.SerializerMethodField()

    class Meta:
        model = PersonalIndirecto
        fields = [
            'id',
            'estamento',
            'nombre_estamento',
            'estamento_label_value',
            'calidad_juridica',
            'nombre_calidad_juridica',
            'calidad_juridica_label_value',
            'numero_personas',
            'renta_bruta',
            'total_rentas',
            'grado',
        ]

    def get_nombre_estamento(self, obj):
        return obj.estamento.estamento if obj.estamento else None

    def get_estamento_label_value(self, obj):
        # Método para el campo personalizado de item_subtitulo
        if obj.estamento:
            return {
                'label': obj.estamento.estamento,
                'value': str(obj.estamento.id)
            }
        return {'label': '', 'value': ''}

    def get_nombre_calidad_juridica(self, obj):
        return obj.calidad_juridica.calidad_juridica if obj.calidad_juridica else None

    def get_calidad_juridica_label_value(self, obj):
        if obj.calidad_juridica:
            return {
                'label': obj.calidad_juridica.calidad_juridica,
                'value': str(obj.calidad_juridica.id)
            }


class Paso5EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso5Encabezado
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso5Serializer(serializers.ModelSerializer):
    avance = serializers.SerializerMethodField()

    años = serializers.SerializerMethodField(read_only=True)
    años_variacion = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paso5
        fields = [
            'id',
            'avance',
            'total_costos_directos',
            'total_costos_indirectos',
            'costos_totales',
            'descripcion_costos_totales',
            'glosas_especificas',
            'descripcion_funciones_personal_directo',
            'descripcion_funciones_personal_indirecto',
            'años',
            'años_variacion',
            'sub21_total_personal_planta',
            'sub21_personal_planta_justificado',
            'sub21_personal_planta_justificar',
            'sub21_total_personal_contrata',
            'sub21_personal_contrata_justificado',
            'sub21_personal_contrata_justificar',
            'sub21_total_otras_remuneraciones',
            'sub21_otras_remuneraciones_justificado',
            'sub21_otras_remuneraciones_justificar',
            'sub21_total_gastos_en_personal',
            'sub21_gastos_en_personal_justificado',
            'sub21_gastos_en_personal_justificar',
            'sub21b_total_personal_planta',
            'sub21b_personal_planta_justificado',
            'sub21b_personal_planta_justificar',
            'sub21b_total_personal_contrata',
            'sub21b_personal_contrata_justificado',
            'sub21b_personal_contrata_justificar',
            'sub21b_total_otras_remuneraciones',
            'sub21b_otras_remuneraciones_justificado',
            'sub21b_otras_remuneraciones_justificar',
            'sub21b_total_gastos_en_personal',
            'sub21b_gastos_en_personal_justificado',
            'sub21b_gastos_en_personal_justificar'
        ]

    def get_años(self, obj):
        competencia = obj.formulario_sectorial.competencia
        if competencia and competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
            años = list(range(año_actual - 5, año_actual))
            return años
        return []

    def get_años_variacion(self, obj):
        competencia = obj.formulario_sectorial.competencia
        if competencia and competencia.fecha_inicio:
            año_actual = competencia.fecha_inicio.year
            n_5 = año_actual - 5
            n_4 = año_actual - 4
            n_3 = año_actual - 3
            n_2 = año_actual - 2
            return {
                'n_5': n_5,
                'n_4': n_4,
                'n_3': n_3,
                'n_2': n_2,
            }
        return {}

    def avance(self, obj):
        return obj.avance()


def eliminar_instancia_costo(modelo, instancia_id):
    try:
        instancia = modelo.objects.get(id=instancia_id)
        instancia.delete()  # Esto disparará la señal post_delete
    except modelo.DoesNotExist:
        pass


def get_subtitulos_disponibles(modelo_costos, formulario_obj, region):
    # Obtiene todos los ID de ItemSubtitulo utilizados por el modelo_costos para este formulario y región
    items_utilizados = modelo_costos.objects.filter(
        formulario_sectorial=formulario_obj,
        region=region,
        item_subtitulo__isnull=False
    ).values_list('item_subtitulo__id', flat=True)

    # Filtra ItemSubtitulo para excluir los utilizados en la región actual
    item_subtitulos_disponibles = ItemSubtitulo.objects.exclude(id__in=items_utilizados)

    # Obtiene los Subtitulos asociados a los item_subtitulos disponibles
    subtitulos_ids = item_subtitulos_disponibles.values_list('subtitulo__id', flat=True).distinct()
    subtitulos_disponibles = Subtitulos.objects.filter(id__in=subtitulos_ids)

    return SubtitulosSerializer(subtitulos_disponibles, many=True).data


def get_item_subtitulos_disponibles_y_agrupados(modelo_costos, formulario_obj, region):
    # Obtiene todos los ID de ItemSubtitulo utilizados por el modelo de costos para este formulario y región
    items_utilizados = modelo_costos.objects.filter(
        formulario_sectorial=formulario_obj,
        region=region,
        item_subtitulo__isnull=False
    ).values_list('item_subtitulo__id', flat=True)

    # Filtra ItemSubtitulo para excluir los utilizados en la región actual
    item_subtitulos_disponibles = ItemSubtitulo.objects.exclude(id__in=items_utilizados).select_related('subtitulo')

    # Agrupa los ItemSubtitulo disponibles por Subtitulos
    items_agrupados = {}
    for item in item_subtitulos_disponibles:
        subtitulo = item.subtitulo.subtitulo
        if subtitulo not in items_agrupados:
            items_agrupados[subtitulo] = []
        items_agrupados[subtitulo].append(ItemSubtituloSerializer(item).data)

    return items_agrupados


class RegionPaso5Serializer(serializers.Serializer):
    region = serializers.CharField()
    paso5 = Paso5Serializer(many=True)
    p_5_1_a_costos_directos = CostosDirectosSerializer(many=True, read_only=False)
    p_5_1_b_costos_indirectos = CostosIndirectosSerializer(many=True, read_only=False)
    p_5_1_c_resumen_costos_por_subtitulo = ResumenCostosPorSubtituloSerializer(many=True, read_only=False)
    p_5_2_evolucion_gasto_asociado = EvolucionGastoAsociadoSerializer(many=True, read_only=False)
    p_5_2_variacion_promedio = VariacionPromedioSerializer(many=True, read_only=False)
    p_5_3_a_personal_directo = PersonalDirectoSerializer(many=True, read_only=False)
    p_5_3_b_personal_indirecto = PersonalIndirectoSerializer(many=True, read_only=False)

    listado_subtitulos_directos = serializers.SerializerMethodField()
    listado_subtitulos_indirectos = serializers.SerializerMethodField()
    listado_item_subtitulos_directos = serializers.SerializerMethodField()
    listado_item_subtitulos_indirectos = serializers.SerializerMethodField()
    listado_calidades_juridicas_directas = serializers.SerializerMethodField()
    listado_calidades_juridicas_indirectas = serializers.SerializerMethodField()

    def get_listado_subtitulos_directos(self, obj):
        formulario_sectorial = obj['paso5'][0]['formulario_sectorial'] if obj['paso5'] else None
        region = obj['region']
        if formulario_sectorial:
            return get_subtitulos_disponibles(CostosDirectos, formulario_sectorial, region)
        return []

    def get_listado_subtitulos_indirectos(self, obj):
        formulario_sectorial = obj['paso5'][0]['formulario_sectorial'] if obj['paso5'] else None
        region = obj['region']
        if formulario_sectorial:
            return get_subtitulos_disponibles(CostosIndirectos, formulario_sectorial, region)
        return []

    def get_listado_item_subtitulos_directos(self, obj):
        formulario_sectorial = obj['paso5'][0]['formulario_sectorial'] if obj['paso5'] else None
        region = obj['region']
        if formulario_sectorial:
            return get_item_subtitulos_disponibles_y_agrupados(CostosDirectos, formulario_sectorial, region)
        return {}

    def get_listado_item_subtitulos_indirectos(self, obj):
        formulario_sectorial = obj['paso5'][0]['formulario_sectorial'] if obj['paso5'] else None
        region = obj['region']
        if formulario_sectorial:
            return get_item_subtitulos_disponibles_y_agrupados(CostosIndirectos, formulario_sectorial, region)
        return {}

    def get_filtered_calidades_juridicas(self, formulario_sectorial, region, modelo_costos):
        mapeo_items_calidades = {
            '01 - Personal de Planta': ['Planta'],
            '02 - Personal de Contrata': ['Contrata'],
            '03 - Otras Remuneraciones': ['Honorario a suma alzada'],
            '04 - Otros Gastos en Personal': ['Honorario asimilado a grado', 'Comisión de servicio', 'Otro'],
        }

        items_usados = modelo_costos.objects.filter(
            formulario_sectorial=formulario_sectorial,
            region=region
        ).values_list('item_subtitulo__item', flat=True).distinct()

        calidades_incluidas = set()

        for item_usado in items_usados:
            for item, calidades in mapeo_items_calidades.items():
                if item == item_usado:
                    calidades_incluidas.update(calidades)

        calidades_filtradas = list(CalidadJuridica.objects.filter(
            calidad_juridica__in=calidades_incluidas
        ).values('id', 'calidad_juridica'))

        return calidades_filtradas

    def get_listado_calidades_juridicas_directas(self, obj):
        formulario_sectorial = obj['paso5'][0]['formulario_sectorial'] if obj['paso5'] else None
        region = obj['region']
        if formulario_sectorial:
            return self.get_filtered_calidades_juridicas(formulario_sectorial, region, CostosDirectos)
        return []

    def get_listado_calidades_juridicas_indirectas(self, obj):
        formulario_sectorial = obj['paso5'][0]['formulario_sectorial'] if obj['paso5'] else None
        region = obj['region']
        if formulario_sectorial:
            return self.get_filtered_calidades_juridicas(formulario_sectorial, region, CostosIndirectos)
        return []


class Paso5GeneralSerializer(WritableNestedModelSerializer):
    paso5encabezado = Paso5EncabezadoSerializer(read_only=True)
    solo_lectura = serializers.SerializerMethodField()
    listado_etapas = serializers.SerializerMethodField()
    listado_estamentos = serializers.SerializerMethodField()
    regiones = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'paso5encabezado',
            'solo_lectura',
            'regiones',
            'listado_estamentos',
            'listado_etapas'
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        if obj.formulario_enviado:
            return True
        else:
            return user.perfil != 'Usuario Sectorial'

    def get_listado_estamentos(self, obj):
        estamentos = Estamento.objects.all()
        return EstamentoSerializer(estamentos, many=True).data

    def get_listado_etapas(self, obj):
        etapas = EtapasEjercicioCompetencia.objects.filter(formulario_sectorial=obj)
        return [{'id': etapa.id, 'nombre_etapa': etapa.nombre_etapa} for etapa in etapas]

    def get_regiones(self, obj):
        regiones_data = []
        regiones = obj.competencia.regiones.all()

        for region in regiones:
            paso5_instances = Paso5.objects.filter(formulario_sectorial=obj, region=region)
            costos_directos_instances = CostosDirectos.objects.filter(formulario_sectorial=obj, region=region)
            costos_indirectos_instances = CostosIndirectos.objects.filter(formulario_sectorial=obj, region=region)
            resumen_costos_por_subtitulo_instances = ResumenCostosPorSubtitulo.objects.filter(formulario_sectorial=obj, region=region)
            evolucion_gasto_asociado_instances = EvolucionGastoAsociado.objects.filter(formulario_sectorial=obj, region=region)
            variacion_promedio_instances = VariacionPromedio.objects.filter(formulario_sectorial=obj, region=region)
            personal_directo_instances = PersonalDirecto.objects.filter(formulario_sectorial=obj, region=region)
            personal_indirecto_instances = PersonalIndirecto.objects.filter(formulario_sectorial=obj, region=region)

            region_data = {
                'region': region.region,
                'paso5': Paso5Serializer(paso5_instances, many=True).data,
                'p_5_1_a_costos_directos': CostosDirectosSerializer(costos_directos_instances, many=True).data,
                'p_5_1_b_costos_indirectos': CostosIndirectosSerializer(costos_indirectos_instances, many=True).data,
                'p_5_1_c_resumen_costos_por_subtitulo': ResumenCostosPorSubtituloSerializer(resumen_costos_por_subtitulo_instances, many=True).data,
                'p_5_2_evolucion_gasto_asociado': EvolucionGastoAsociadoSerializer(evolucion_gasto_asociado_instances, many=True).data,
                'p_5_2_variacion_promedio': VariacionPromedioSerializer(variacion_promedio_instances, many=True).data,
                'p_5_3_a_personal_directo': PersonalDirectoSerializer(personal_directo_instances, many=True).data,
                'p_5_3_b_personal_indirecto': PersonalIndirectoSerializer(personal_indirecto_instances, many=True).data,
            }

            region_data.update({
                'listado_subtitulos_directos': get_subtitulos_disponibles(CostosDirectos, obj, region),
                'listado_subtitulos_indirectos': get_subtitulos_disponibles(CostosIndirectos, obj, region),
                'listado_item_subtitulos_directos': get_item_subtitulos_disponibles_y_agrupados(CostosDirectos, obj, region),
                'listado_item_subtitulos_indirectos': get_item_subtitulos_disponibles_y_agrupados(CostosIndirectos, obj, region),
                'listado_calidades_juridicas_directas': RegionPaso5Serializer().get_filtered_calidades_juridicas(obj, region, CostosDirectos),
                'listado_calidades_juridicas_indirectas': RegionPaso5Serializer().get_filtered_calidades_juridicas(obj, region, CostosIndirectos),
            })

            regiones_data.append(region_data)

        return regiones_data

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)

        def process_nested_data(nested_data, serializer_class):
            internal_data = []
            for item in nested_data:
                if 'DELETE' in item and item['DELETE'] == True:
                    internal_data.append({'id': item['id'], 'DELETE': True})
                else:
                    item_data = serializer_class().to_internal_value(item)
                    item_data['id'] = item.get('id')
                    internal_data.append(item_data)
            return internal_data

        if 'regiones' in data:
            nested_data = data['regiones']
            internal_nested_data = []
            for region_data in nested_data:
                region = region_data.get('region')
                paso_data = region_data.get('paso5', [])
                costos_directos_data = region_data.get('p_5_1_a_costos_directos', [])
                costos_indirectos_data = region_data.get('p_5_1_b_costos_indirectos', [])
                resumen_costos_por_subtitulo_data = region_data.get('p_5_1_c_resumen_costos_por_subtitulo', [])
                evolucion_gasto_asociado_data = region_data.get('p_5_2_evolucion_gasto_asociado', [])
                variacion_promedio_data = region_data.get('p_5_2_variacion_promedio', [])
                personal_directo_data = region_data.get('p_5_3_a_personal_directo', [])
                personal_indirecto_data = region_data.get('p_5_3_b_personal_indirecto', [])

                internal_paso_data = process_nested_data(paso_data, Paso5Serializer)
                internal_costos_directos_data = process_nested_data(costos_directos_data, CostosDirectosSerializer)
                internal_costos_indirectos_data = process_nested_data(costos_indirectos_data, CostosIndirectosSerializer)
                internal_resumen_costos_data = process_nested_data(resumen_costos_por_subtitulo_data, ResumenCostosPorSubtituloSerializer)
                internal_evolucion_gasto_data = process_nested_data(evolucion_gasto_asociado_data, EvolucionGastoAsociadoSerializer)
                internal_variacion_promedio_data = process_nested_data(variacion_promedio_data, VariacionPromedioSerializer)
                internal_personal_directo_data = process_nested_data(personal_directo_data, PersonalDirectoSerializer)
                internal_personal_indirecto_data = process_nested_data(personal_indirecto_data, PersonalIndirectoSerializer)

                internal_nested_data.append({
                    'region': region,
                    'paso5': internal_paso_data,
                    'p_5_1_a_costos_directos': internal_costos_directos_data,
                    'p_5_1_b_costos_indirectos': internal_costos_indirectos_data,
                    'p_5_1_c_resumen_costos_por_subtitulo': internal_resumen_costos_data,
                    'p_5_2_evolucion_gasto_asociado': internal_evolucion_gasto_data,
                    'p_5_2_variacion_promedio': internal_variacion_promedio_data,
                    'p_5_3_a_personal_directo': internal_personal_directo_data,
                    'p_5_3_b_personal_indirecto': internal_personal_indirecto_data,
                })

            internal_value['regiones'] = internal_nested_data

        return internal_value

    def update_or_create_nested_instances(self, model, nested_data, instance, region):
        for data in nested_data:
            item_id = data.pop('id', None)
            delete_flag = data.pop('DELETE', False)

            # Asigna la región a los datos
            data['region'] = region

            if item_id is not None:
                if delete_flag:
                    model.objects.filter(id=item_id).delete()
                else:
                    # Obtener la instancia, actualizar los valores y guardarla
                    obj = model.objects.get(id=item_id)
                    for attr, value in data.items():
                        setattr(obj, attr, value)
                    obj.save()  # Esto debería disparar la señal post_save
            elif not delete_flag:
                model.objects.create(formulario_sectorial=instance, **data)

    def update(self, instance, validated_data):
        regiones_data = validated_data.pop('regiones', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if regiones_data is not None:
            for region_data in regiones_data:
                region_name = region_data.get('region')
                region = instance.competencia.regiones.get(region=region_name)

                paso_data = region_data.pop('paso5', [])
                costos_directos_data = region_data.pop('p_5_1_a_costos_directos', [])
                costos_indirectos_data = region_data.pop('p_5_1_b_costos_indirectos', [])
                resumen_costos_por_subtitulo_data = region_data.pop('p_5_1_c_resumen_costos_por_subtitulo', [])
                evolucion_gasto_asociado_data = region_data.pop('p_5_2_evolucion_gasto_asociado', [])
                variacion_promedio_data = region_data.pop('p_5_2_variacion_promedio', [])
                personal_directo_data = region_data.pop('p_5_3_a_personal_directo', [])
                personal_indirecto_data = region_data.pop('p_5_3_b_personal_indirecto', [])

                self.update_or_create_nested_instances(Paso5, paso_data, instance, region)
                self.update_or_create_nested_instances(CostosDirectos, costos_directos_data, instance, region)
                self.update_or_create_nested_instances(CostosIndirectos, costos_indirectos_data, instance, region)
                self.update_or_create_nested_instances(ResumenCostosPorSubtitulo, resumen_costos_por_subtitulo_data, instance, region)
                self.update_or_create_nested_instances(EvolucionGastoAsociado, evolucion_gasto_asociado_data, instance, region)
                self.update_or_create_nested_instances(VariacionPromedio, variacion_promedio_data, instance, region)
                self.update_or_create_nested_instances(PersonalDirecto, personal_directo_data, instance, region)
                self.update_or_create_nested_instances(PersonalIndirecto, personal_indirecto_data, instance, region)

        return instance
