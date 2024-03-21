from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
import logging

from applications.formularios_gores.models import (
    FormularioGORE,
    Paso3,
    PersonalDirectoGORE,
    PersonalIndirectoGORE,
    RecursosComparados,
    SistemasInformaticos,
    RecursosFisicosInfraestructura,
    CostosDirectosGore,
    CostosIndirectosGore,
)

from applications.formularios_sectoriales.models import (
    CalidadJuridica,
    Estamento,
    Subtitulos,
    ItemSubtitulo
)

from applications.formularios_sectoriales.api.v1.serializers import (
    SubtitulosSerializer,
    ItemSubtituloSerializer,
    EstamentoSerializer,
    CalidadJuridicaSerializer,
)

User = get_user_model()

logger = logging.getLogger(__name__)


class PersonalDirectoGoreSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    DELETE = serializers.BooleanField(required=False, default=False)
    calidad_juridica = serializers.PrimaryKeyRelatedField(queryset=CalidadJuridica.objects.all())
    sector_nombre = serializers.SerializerMethodField()
    estamento = serializers.PrimaryKeyRelatedField(queryset=Estamento.objects.all())
    nombre_estamento = serializers.SerializerMethodField()
    calidad_juridica_label_value = serializers.SerializerMethodField()
    nombre_calidad_juridica = serializers.SerializerMethodField()
    estamento_label_value = serializers.SerializerMethodField()

    class Meta:
        model = PersonalDirectoGORE
        fields = [
            'id',
            'id_sectorial',
            'DELETE',
            'sector',
            'sector_nombre',
            'estamento',
            'nombre_estamento',
            'estamento_label_value',
            'calidad_juridica',
            'nombre_calidad_juridica',
            'calidad_juridica_label_value',
            'renta_bruta',
            'grado',
            'comision_servicio',
            'utilizara_recurso'
        ]

    def get_sector_nombre(self, obj):
        # Método para el campo personalizado de sector
        if obj.sector:
            return obj.sector.nombre
        return ''
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
        

class PersonalIndirectoGoreSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    DELETE = serializers.BooleanField(required=False, default=False)
    calidad_juridica = serializers.PrimaryKeyRelatedField(queryset=CalidadJuridica.objects.all())
    sector_nombre = serializers.SerializerMethodField()
    estamento = serializers.PrimaryKeyRelatedField(queryset=Estamento.objects.all())
    nombre_estamento = serializers.SerializerMethodField()
    calidad_juridica_label_value = serializers.SerializerMethodField()
    nombre_calidad_juridica = serializers.SerializerMethodField()
    estamento_label_value = serializers.SerializerMethodField()

    class Meta:
        model = PersonalIndirectoGORE
        fields = [
            'id',
            'id_sectorial',
            'DELETE',
            'sector',
            'sector_nombre',
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
            'comision_servicio',
            'utilizara_recurso'
        ]

    def get_sector_nombre(self, obj):
        # Método para el campo personalizado de sector
        if obj.sector:
            return obj.sector.nombre
        return ''

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

class RecursosComparadosSerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()

    class Meta:
        model = RecursosComparados
        fields = [
            'id',
            'sector',
            'sector_nombre',
            'subtitulo_label_value',
            'item_subtitulo',
            'item_subtitulo_label_value',
            'costo_sector',
            'costo_gore',
            'diferencia_monto'
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


class SistemasInformaticosSerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()

    class Meta:
        model = SistemasInformaticos
        fields = [
            'id',
            'sector',
            'sector_nombre',
            'subtitulo_label_value',
            'item_subtitulo',
            'item_subtitulo_label_value',
            'nombre_plataforma',
            'descripcion_tecnica',
            'costo',
            'funcion'
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
    

class RecursosFisicosInfraestructuraSerializer(serializers.ModelSerializer):
    subtitulo_label_value = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    item_subtitulo_label_value = serializers.SerializerMethodField()

    class Meta:
        model = RecursosFisicosInfraestructura
        fields = [
            'id',
            'sector',
            'sector_nombre',
            'subtitulo_label_value',
            'item_subtitulo',
            'item_subtitulo_label_value',
            'costo_unitario',
            'cantidad',
            'costo_total',
            'fundamentacion'
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



class Paso3EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()
    denominacion_region = serializers.SerializerMethodField()


    class Meta:
        model = Paso3
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'denominacion_region',
            
            'descripcion_perfiles_tecnicos_directo',
            'descripcion_perfiles_tecnicos_indirecto',
            
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
            'sub21b_gastos_en_personal_justificar',

            'subtitulo_22_diferencia_sector',
            'subtitulo_22_justificados_gore',
            'subtitulo_22_por_justificar',

            'subtitulo_29_diferencia_sector',
            'subtitulo_29_justificados_gore',
            'subtitulo_29_por_justificar',
            
            'costos_informados_gore',
            'costos_justificados_gore',
            'costos_justificar_gore'
        ]

    def avance(self, obj):
        return obj.avance()

    def get_denominacion_region(self, obj):
        # Asegúrate de que obj es una instancia de Paso1
        if isinstance(obj, Paso3) and obj.formulario_gore:
            return obj.formulario_gore.region.region
        return None


class Paso3Serializer(WritableNestedModelSerializer):
    paso3_gore = Paso3EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    p_3_1_a_personal_directo = PersonalDirectoGoreSerializer(many=True, read_only=False)
    p3_personal_directo_sector = serializers.SerializerMethodField()
    p3_personal_directo_gore = serializers.SerializerMethodField()
    p_3_1_b_personal_indirecto = PersonalIndirectoGoreSerializer(many=True, read_only=False)
    p3_personal_indirecto_sector = serializers.SerializerMethodField()
    p3_personal_indirecto_gore = serializers.SerializerMethodField()
    p_3_2_recursos_comparados = RecursosComparadosSerializer(many=True, read_only=False)
    p_3_2_a_sistemas_informaticos = SistemasInformaticosSerializer(many=True, read_only=False)
    p_3_2_b_recursos_fisicos_infraestructura = RecursosFisicosInfraestructuraSerializer(many=True, read_only=False)
    listado_subtitulos = serializers.SerializerMethodField()
    listado_item_subtitulos = serializers.SerializerMethodField()
    listado_estamentos = serializers.SerializerMethodField()
    listado_calidades_juridicas_directas = serializers.SerializerMethodField()
    listado_calidades_juridicas_indirectas = serializers.SerializerMethodField()

    class Meta:
        model = FormularioGORE
        fields = [
            'id',
            'paso3_gore',
            'solo_lectura',
            'p_3_1_a_personal_directo',
            'p3_personal_directo_sector',
            'p3_personal_directo_gore',
            'p_3_1_b_personal_indirecto',
            'p3_personal_indirecto_sector',
            'p3_personal_indirecto_gore',
            'p_3_2_recursos_comparados',
            'p_3_2_a_sistemas_informaticos',
            'p_3_2_b_recursos_fisicos_infraestructura',
            'listado_subtitulos',
            'listado_item_subtitulos',
            'listado_estamentos',
            'listado_estamentos',
            'listado_calidades_juridicas_directas',
            'listado_calidades_juridicas_indirectas'
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario GORE' pueden editar
            return user.perfil != 'GORE'

    def update_paso3_instance(self, instance, paso3_data):
        paso3_instance = getattr(instance, 'paso3', None)
        if paso3_instance:
            for attr, value in paso3_data.items():
                setattr(paso3_instance, attr, value)
            paso3_instance.save()
        else:
            Paso3.objects.create(formulario_gore=instance, **paso3_data)

    def get_p3_personal_directo_sector(self, obj):
        queryset = PersonalDirectoGORE.objects.filter(formulario_gore=obj, sector__isnull=False)
        return PersonalDirectoGoreSerializer(queryset, many=True).data

    def get_p3_personal_directo_gore(self, obj):
        queryset = PersonalDirectoGORE.objects.filter(formulario_gore=obj, sector__isnull=True)
        return PersonalDirectoGoreSerializer(queryset, many=True).data

    def get_p3_personal_indirecto_sector(self, obj):
        queryset = PersonalIndirectoGORE.objects.filter(formulario_gore=obj, sector__isnull=False)
        return PersonalIndirectoGoreSerializer(queryset, many=True).data

    def get_p3_personal_indirecto_gore(self, obj):
        queryset = PersonalIndirectoGORE.objects.filter(formulario_gore=obj, sector__isnull=True)
        return PersonalIndirectoGoreSerializer(queryset, many=True).data

    def get_listado_subtitulos(self, obj):
        # Obtener IDs de subtitulos usados en RecursosComparados para un formulario_gore específico
        subtitulos_usados_ids = RecursosComparados.objects.filter(
            formulario_gore=obj  # Usar el objeto formulario_gore pasado al serializador
        ).values_list('item_subtitulo__subtitulo__id', flat=True).distinct()

        # Filtrar Subtitulos por los IDs obtenidos
        subtitulos = Subtitulos.objects.filter(id__in=subtitulos_usados_ids)

        return SubtitulosSerializer(subtitulos, many=True).data

    def get_listado_item_subtitulos(self, obj):
        items_agrupados = {}

        # Obtener IDs de ItemSubtitulo usados en RecursosComparados para un formulario_gore específico
        items_usados_ids = RecursosComparados.objects.filter(
            formulario_gore=obj  # Usar el objeto formulario_gore pasado al serializador
        ).values_list('item_subtitulo__id', flat=True).distinct()

        # Filtrar ItemSubtitulo por los IDs obtenidos y realizar la agrupación
        for item in ItemSubtitulo.objects.filter(id__in=items_usados_ids).select_related('subtitulo'):
            subtitulo = item.subtitulo.subtitulo
            if subtitulo not in items_agrupados:
                items_agrupados[subtitulo] = []
            items_agrupados[subtitulo].append(ItemSubtituloSerializer(item).data)

        return items_agrupados

    def get_listado_estamentos(self, obj):
        # Obtener todos los registros de Estamento y serializarlos
        estamentos = Estamento.objects.all()
        return EstamentoSerializer(estamentos, many=True).data

    def get_filtered_calidades_juridicas(self, obj, modelo_costos):
        # Mapeo de items a calidades jurídicas
        mapeo_items_calidades = {
            '01 - Personal de Planta': ['Planta'],
            '02 - Personal de Contrata': ['Contrata'],
            '03 - Otras Remuneraciones': ['Honorario a suma alzada'],
            '04 - Otros Gastos en Personal': ['Honorario asimilado a grado', 'Comisión de servicio', 'Otro'],
        }

        # Obtener los items usados en el modelo de costos para el formulario GORE actual
        items_usados = modelo_costos.objects.filter(
            formulario_gore=obj
        ).values_list('item_subtitulo__item', flat=True).distinct()

        # Inicializar el conjunto para recoger las calidades jurídicas basadas en los items usados
        calidades_incluidas = set()

        # Iterar sobre los items usados y agregar las calidades jurídicas correspondientes
        for item_usado in items_usados:
            for item, calidades in mapeo_items_calidades.items():
                if item == item_usado:
                    calidades_incluidas.update(calidades)

        # Filtrar las calidades jurídicas basadas en el conjunto de calidades incluidas
        calidades_filtradas = list(CalidadJuridica.objects.filter(
            calidad_juridica__in=calidades_incluidas
        ).values('id', 'calidad_juridica'))

        return calidades_filtradas

    def get_listado_calidades_juridicas_directas(self, obj):
        return self.get_filtered_calidades_juridicas(obj, CostosDirectosGore)

    def get_listado_calidades_juridicas_indirectas(self, obj):
        return self.get_filtered_calidades_juridicas(obj, CostosIndirectosGore)

    def to_internal_value(self, data):

        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'paso3_gore'
            'p_3_1_a_personal_directo',
            'p_3_1_b_personal_indirecto',
            'p_3_2_recursos_comparados',
            'p_3_2_a_sistemas_informaticos',
            'p_3_2_b_recursos_fisicos_infraestructura'
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
            item_id = data.get('id', None)
            delete_flag = data.get('DELETE', False)

            if delete_flag and item_id:
                deleted, _ = model.objects.filter(id=item_id).delete()

            elif not delete_flag:
                if item_id:
                    # Actualizar la instancia existente
                    obj = model.objects.get(id=item_id)
                    for attr, value in data.items():
                        setattr(obj, attr, value)
                    obj.formulario_gore = instance  # Asegurar que la instancia está correctamente asociada
                    obj.save()  # Invoca explícitamente el método save para aplicar la validación
                else:
                    # Crear una nueva instancia si no hay ID y el flag 'DELETE' no está presente
                    data.pop('DELETE', None)  # Remover el flag 'DELETE' si está presente
                    new_obj = model(**data)
                    new_obj.formulario_gore = instance  # Asegurar que la instancia está correctamente asociada
                    new_obj.save()

    def update(self, instance, validated_data):
        paso3 = validated_data.pop('paso3', None)
        personal_directo_data = validated_data.pop('p_3_1_a_personal_directo', None)
        personal_indirecto_data = validated_data.pop('p_3_1_b_personal_indirecto', None)
        recursos_comparados_data = validated_data.pop('p_3_2_recursos_comparados', None)
        sistemas_informaticos_data = validated_data.pop('p_3_2_a_sistemas_informaticos', None)
        recursos_fisicos_infraestructura_data = validated_data.pop('p_3_2_b_recursos_fisicos_infraestructura', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear Paso3
        if paso3 is not None:
            self.update_paso3_instance(instance, paso3)

        if personal_directo_data is not None:
            self.update_or_create_nested_instances(PersonalDirectoGORE, personal_directo_data, instance)

        if  personal_indirecto_data is not None:
            self.update_or_create_nested_instances(PersonalIndirectoGORE, personal_indirecto_data, instance)

        if recursos_comparados_data is not None:
            self.update_or_create_nested_instances(RecursosComparados, recursos_comparados_data, instance)

        if sistemas_informaticos_data is not None:
            self.update_or_create_nested_instances(SistemasInformaticos, sistemas_informaticos_data, instance)

        if recursos_fisicos_infraestructura_data is not None:
            self.update_or_create_nested_instances(RecursosFisicosInfraestructura, recursos_fisicos_infraestructura_data, instance)

        return instance
