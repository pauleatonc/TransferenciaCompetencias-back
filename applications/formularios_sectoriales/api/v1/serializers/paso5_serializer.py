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
    subtitulo_label_value = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()
    etapa_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectos
        fields = [
            'id',
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

    def get_etapa_label_value(self, obj):
        # Obtiene todas las etapas asociadas y las transforma al formato {label, value}
        return [{
            'label': etapa.nombre_etapa,  # Usamos nombre_etapa para el label
            'value': str(etapa.id)  # El ID de la etapa como value
        } for etapa in obj.etapa.all()]


class CostosIndirectosSerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()
    etapa_label_value = serializers.SerializerMethodField()

    class Meta:
        model = CostosDirectos
        fields = [
            'id',
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


class Paso5EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    años = serializers.SerializerMethodField(read_only=True)
    años_variacion = serializers.SerializerMethodField(read_only=True)

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
            'sub21_total_resto',
            'sub21_resto_justificado',
            'sub21_resto_justificar'
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

class Paso5Serializer(WritableNestedModelSerializer):
    paso5 = Paso5EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
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
            'solo_lectura',
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

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario Sectorial' pueden editar
            return user.perfil != 'Usuario Sectorial'

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
    
    def update_paso5_instance(self, instance, paso5_data):
        # Asume que 'paso5_data' contiene los datos del objeto relacionado
        paso5_instance = getattr(instance, 'paso5', None)
        if paso5_instance:
            for attr, value in paso5_data.items():
                setattr(paso5_instance, attr, value)
            paso5_instance.save()
        else:
            Paso5.objects.create(formulario_sectorial=instance, **paso5_data)

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
                        if field_name == 'p_5_1_a_costos_directos':
                            eliminar_instancia_costo(CostosDirectos, item['id'])
                        elif field_name == 'p_5_1_b_costos_indirectos':
                            eliminar_instancia_costo(CostosIndirectos, item['id'])
                        elif field_name == 'p_5_2_evolucion_gasto_asociado':
                            eliminar_instancia_costo(CostosIndirectos, item['id'])
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
        paso5 = validated_data.pop('paso5', None)
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

        # Actualizar o crear Paso5
        if paso5 is not None:
            self.update_paso5_instance(instance, paso5)
    
        # Actualizar o crear CostosDirectos
        if costos_directos_data is not None:
            for costo_data in costos_directos_data:
                costo_id = costo_data.pop('id', None)
                delete_flag = costo_data.pop('DELETE', False)
                etapa_ids = costo_data.pop('etapa', None)  # Asume que etapa_ids es una lista de IDs

                if delete_flag and costo_id:
                    CostosDirectos.objects.filter(id=costo_id).delete()
                    continue

                # Excluyendo 'etapa' de defaults porque no se puede asignar directamente
                costo_instance, _ = CostosDirectos.objects.update_or_create(
                    id=costo_id,
                    defaults={key: value for key, value in costo_data.items() if key != 'etapa'},
                    formulario_sectorial=instance)

                if etapa_ids is not None:
                    # Asegurarse de que etapa_ids solo contenga números (IDs)
                    costo_instance.etapa.set(etapa_ids)
    
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