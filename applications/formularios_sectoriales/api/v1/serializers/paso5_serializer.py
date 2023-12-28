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
    costo_anio = CostoAnioSerializer(many=True)
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
    nombre_calidad_juridica = serializers.SerializerMethodField()
    nombre_estamento = serializers.SerializerMethodField()

    class Meta:
        model = PersonalDirecto
        fields = [
            'id',
            'estamento',
            'nombre_estamento',
            'calidad_juridica',
            'nombre_calidad_juridica',
            'renta_bruta',
            'grado',
        ]

    def get_nombre_calidad_juridica(self, obj):
        return obj.calidad_juridica.calidad_juridica if obj.calidad_juridica else None

    def  get_nombre_estamento(self, obj):
        return obj.estamento.estamento if obj.estamento else None

    def to_representation(self, instance):
        # Representación original del objeto
        representation = super(PersonalDirectoSerializer, self).to_representation(instance)
        estamento = instance.estamento.estamento if instance.estamento else None
        return {estamento: representation}


class PersonalIndirectoSerializer(serializers.ModelSerializer):
    calidad_juridica = serializers.PrimaryKeyRelatedField(queryset=CalidadJuridica.objects.all())
    estamento = serializers.PrimaryKeyRelatedField(queryset=Estamento.objects.all())
    nombre_calidad_juridica = serializers.SerializerMethodField()
    nombre_estamento = serializers.SerializerMethodField()

    class Meta:
        model = PersonalIndirecto
        fields = [
            'id',
            'estamento',
            'nombre_estamento',
            'calidad_juridica',
            'nombre_calidad_juridica',
            'numero_personas',
            'renta_bruta',
            'grado',
        ]

    def get_nombre_calidad_juridica(self, obj):
        return obj.calidad_juridica.calidad_juridica if obj.calidad_juridica else None

    def  get_nombre_estamento(self, obj):
        return obj.estamento.estamento if obj.estamento else None

    def to_representation(self, instance):
        # Representación original del objeto
        representation = super(PersonalIndirectoSerializer, self).to_representation(instance)
        estamento = instance.estamento.estamento if instance.estamento else None
        return {estamento: representation}


class Paso5EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso5
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'total_costos_directos',
            'total_costos_indirectos',
            'costos_totales',
            'glosas_especificas',
            'descripcion_funciones_personal_directo',
            'descripcion_funciones_personal_indirecto',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso5Serializer(serializers.ModelSerializer):
    paso5 = Paso5EncabezadoSerializer()
    listado_subtitulos = serializers.SerializerMethodField()
    listado_item_subtitulos = serializers.SerializerMethodField()
    listado_estamentos = serializers.SerializerMethodField()
    listado_calidades_juridicas = serializers.SerializerMethodField()
    listado_etapas = serializers.SerializerMethodField()
    p_5_1_a_costos_directos = CostosDirectosSerializer(many=True, read_only=False)
    p_5_1_b_costos_indirectos = CostosIndirectosSerializer(many=True, read_only=False)
    p_5_1_c_resumen_costos_por_subtitulo = ResumenCostosPorSubtituloSerializer(many=True, read_only=False)
    p_5_2_evolucion_gasto_asociado = EvolucionGastoAsociadoSerializer(many=True, read_only=False)
    p_5_2_variacion_promedio = VariacionPromedioSerializer(many=True, read_only=False)
    p_5_3_a_personal_directo = PersonalDirectoSerializer(many=True, read_only=False)
    p_5_3_b_personal_indirecto = PersonalIndirectoSerializer(many=True, read_only=False)

    class Meta:
        model = FormularioSectorial
        fields = [
            'paso5',
            'p_5_1_a_costos_directos',
            'p_5_1_b_costos_indirectos',
            'p_5_1_c_resumen_costos_por_subtitulo',
            'p_5_2_evolucion_gasto_asociado',
            'p_5_2_variacion_promedio',
            'p_5_3_a_personal_directo',
            'p_5_3_b_personal_indirecto',
            'listado_subtitulos',
            'listado_item_subtitulos',
            'listado_estamentos',
            'listado_calidades_juridicas',
            'listado_etapas'
        ]

    def get_listado_subtitulos(self, obj):
        # Obtener todos los registros de Subtitulos y serializarlos
        subtitulos = Subtitulos.objects.all()
        return SubtitulosSerializer(subtitulos, many=True).data

    def get_listado_estamentos(self, obj):
        # Obtener todos los registros de Estamento y serializarlos
        estamentos = Estamento.objects.all()
        return EstamentoSerializer(estamentos, many=True).data

    def get_listado_calidades_juridicas(self, obj):
        # Obtener todos los registros de CalidadJuridica y serializarlos
        calidades_juridicas = CalidadJuridica.objects.all()
        return CalidadJuridicaSerializer(calidades_juridicas, many=True).data

    def get_listado_item_subtitulos(self, obj):
        # Agrupar ItemSubtitulo por Subtitulos
        items_agrupados = {}
        for item in ItemSubtitulo.objects.all().select_related('subtitulo'):
            subtitulo = item.subtitulo.subtitulo
            if subtitulo not in items_agrupados:
                items_agrupados[subtitulo] = []
            items_agrupados[subtitulo].append(ItemSubtituloSerializer(item).data)

        return items_agrupados

    def get_listado_etapas(self, obj):
        etapas = EtapasEjercicioCompetencia.objects.filter(formulario_sectorial=obj)
        return [{'id': etapa.id, 'nombre_etapa': etapa.nombre_etapa} for etapa in etapas]

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'p_5_1_a_costos_directos',
            'p_5_1_b_costos_indirectos',
            'p_5_1_c_resumen_costos_por_subtitulo',
            'p_5_2_evolucion_gasto_asociado',
            'p_5_2_variacion_promedio',
            'p_5_3_a_personal_directo',
            'p_5_3_b_personal_indirecto',
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

    def update(self, instance, validated_data):
        costos_directos_data = validated_data.pop('p_5_1_a_costos_directos', None)
        costos_indirectos_data = validated_data.pop('p_5_1_b_costos_indirectos', None)
        resumen_costos_data = validated_data.pop('p_5_1_c_resumen_costos_por_subtitulo', None)
        evolucion_gasto_data = validated_data.pop('p_5_2_evolucion_gasto_asociado', None)
        variacion_promedio_data = validated_data.pop('p_5_2_variacion_promedio', None)
        personal_directo_data = validated_data.pop('p_5_3_a_personal_directo', None)
        personal_indirecto_data = validated_data.pop('p_5_3_b_personal_indirecto', None)

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

        # Actualizar o crear VariacionPromedio
        if variacion_promedio_data is not None:
            self.update_or_create_nested_instances(VariacionPromedio, variacion_promedio_data, instance)

        # Actualizar o crear PersonalDirecto
        if personal_directo_data is not None:
            self.update_or_create_nested_instances(PersonalDirecto, personal_directo_data, instance)

        # Actualizar o crear PersonalIndirecto
        if personal_indirecto_data is not None:
            self.update_or_create_nested_instances(PersonalIndirecto, personal_indirecto_data, instance)

        return instance

    def to_representation(self, instance):
        representation = super(Paso5Serializer, self).to_representation(instance)
        personal_directo_agrupado = {}
        personal_indirecto_agrupado = {}

        # Agrupar Personal Directo por Estamento
        for personal in representation.get('p_5_3_a_personal_directo', []):
            for estamento, datos in personal.items():
                if estamento not in personal_directo_agrupado:
                    personal_directo_agrupado[estamento] = []
                personal_directo_agrupado[estamento].append(datos)

        # Agrupar Personal Indirecto por Estamento
        for personal in representation.get('p_5_3_b_personal_indirecto', []):
            for estamento, datos in personal.items():
                if estamento not in personal_indirecto_agrupado:
                    personal_indirecto_agrupado[estamento] = []
                personal_indirecto_agrupado[estamento].append(datos)

        representation['p_5_3_a_personal_directo'] = personal_directo_agrupado
        representation['p_5_3_b_personal_indirecto'] = personal_indirecto_agrupado

        return representation