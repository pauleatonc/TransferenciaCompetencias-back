from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from applications.competencias.models import (
    Competencia,
    RecomendacionesDesfavorables,
    Temporalidad,
    PasoBase,
    Paso1RevisionFinalSubdere,
    Paso2RevisionFinalSubdere,
    ImagenesRevisionSubdere,
)

from applications.competencias.api.v1.serializers import (
    AmbitoSerializer,
    SectorSerializer,
)

from applications.regioncomuna.api.v1.serializer import RegionSerializer
from applications.regioncomuna.models import Region

User = get_user_model()


class RecomendacionesDesfavorablesSerializer(serializers.ModelSerializer):
    region_label_value = serializers.SerializerMethodField()
    class Meta:
        model = RecomendacionesDesfavorables
        fields = [
            'id',
            'region',
            'region_label_value',
            'justificacion'
        ]

    def get_region_label_value(self, obj):
        # Asume que obj.region es una única instancia de Region y no un conjunto (QuerySet).
        region = obj.region
        return [{
            'label': region.region,  # Asume que 'region' es el campo que quieres usar como etiqueta.
            'value': str(region.id)  # El ID de la región como valor.
        }]


class TemporalidadSerializer(serializers.ModelSerializer):
    region_label_value = serializers.SerializerMethodField()
    class Meta:
        model = Temporalidad
        fields = [
            'id',
            'region',
            'region_label_value',
            'temporalidad',
            'anios',
            'justificacion_temporalidad',
            'gradualidad_meses',
            'justificacion_gradualidad'
        ]

    def get_region_label_value(self, obj):
        # Obtiene todas las regiones asociadas y las transforma al formato {label, value}
        return [{
            'label': region.region,  # Usamos nombre_region para el label
            'value': str(region.id)  # El ID de la region como value
        } for region in obj.region.all()]


class Paso1RevisionFinalSubdereSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()
    class Meta:
        model = Paso1RevisionFinalSubdere
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'regiones_seleccionadas'
        ]

    def avance(self, obj):
        return obj.avance()


class Paso2RevisionFinalSubdereSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso2RevisionFinalSubdere
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper'
        ]

    def avance(self, obj):
        return obj.avance()


class RevisionFinalCompetenciaDetailSerializer(serializers.ModelSerializer):
    competencia_nombre = serializers.SerializerMethodField()
    sector_nombre = serializers.SerializerMethodField()
    calcular_tiempo_transcurrido = serializers.SerializerMethodField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'competencia_nombre',
            'sector_nombre',
            'sectores',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
        ]


    def get_competencia_nombre(self, obj):
        if obj:
            return obj.nombre
        return None

    def get_sector_nombre(self, obj):
        # Usamos force_str para asegurar que los nombres se conviertan a string correctamente.
        sectores_nombres = [force_str(sect.nombre) for sect in obj.sectores.all()]
        return ', '.join(sectores_nombres)

    def get_calcular_tiempo_transcurrido(self, obj):
        return obj.tiempo_transcurrido()

    def get_ultimo_editor(self, obj):
        historial = obj.historical.all().order_by('-history_date')
        for record in historial:
            if record.history_user:
                return {
                    'nombre_completo': record.history_user.nombre_completo,
                    'perfil': record.history_user.perfil
                }
        return None

    def get_fecha_ultima_modificacion(self, obj):
        try:
            ultimo_registro = obj.historical.latest('history_date')
            if ultimo_registro:
                fecha_local = timezone.localtime(ultimo_registro.history_date)
                return fecha_local.strftime('%d/%m/%Y - %H:%M')
            return None
        except obj.historical.model.DoesNotExist:
            return None


class RevisionFinalCompetenciaPaso1Serializer(WritableNestedModelSerializer):
    paso1_revision_final_subdere = Paso1RevisionFinalSubdereSerializer()
    solo_lectura = serializers.SerializerMethodField()
    ambito_definitivo_competencia = AmbitoSerializer()
    sectores = SectorSerializer(many=True, read_only=True)
    regiones_recomendadas_listado = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'solo_lectura',
            'paso1_revision_final_subdere',
            'nombre',
            'sectores',
            'ambito_definitivo_competencia',
            'regiones_recomendadas',
            'regiones_recomendadas_listado'
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_final_enviado y el perfil del usuario
        if obj.formulario_final_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'SUBDERE' pueden editar
            return user.perfil != 'SUBDERE'

    def get_regiones_recomendadas_listado(self, obj):
        # Filtramos las regiones que ya están en 'regiones' para la competencia.
        regiones_qs = obj.regiones.all()

        # Serializamos las regiones y devolvemos los datos.
        return RegionSerializer(regiones_qs, many=True).data


class RevisionFinalCompetenciaPaso2Serializer(serializers.ModelSerializer):
    paso2_revision_final_subdere = Paso2RevisionFinalSubdereSerializer()
    solo_lectura = serializers.SerializerMethodField()
    recomendaciones_desfavorables = RecomendacionesDesfavorablesSerializer(many=True, read_only=False)
    temporalidad_gradualidad = TemporalidadSerializer(many=True, read_only=False)
    sectores = SectorSerializer(many=True, read_only=True)
    regiones_temporalidad = serializers.SerializerMethodField()
    temporalidad_opciones = serializers.SerializerMethodField()
    modalidad_ejercicio_opciones = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'solo_lectura',
            'paso2_revision_final_subdere',
            'nombre',
            'sectores',
            'regiones_recomendadas',
            'recomendaciones_desfavorables',
            'temporalidad_gradualidad',
            'recursos_requeridos',
            'modalidad_ejercicio',
            'implementacion_acompanamiento',
            'condiciones_ejercicio',
            'regiones_temporalidad',
            'temporalidad_opciones',
            'modalidad_ejercicio_opciones'
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_final_enviado y el perfil del usuario
        if obj.formulario_final_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'SUBDERE' pueden editar
            return user.perfil != 'SUBDERE'

    def get_unused_regions(self, obj, related_name):
        # Asume que el campo regiones_recomendadas almacena directamente los IDs de las regiones recomendadas
        # Obtiene las instancias de Region basadas en los IDs almacenados en regiones_recomendadas
        regiones_recomendadas = Region.objects.filter(id__in=obj.regiones_recomendadas.all())

        # Obtiene las IDs de las regiones ya usadas en la relación especificada
        # Asegúrate de que solo se consideren instancias con regiones asociadas
        regiones_usadas = getattr(obj, related_name).all().exclude(region__isnull=True)
        regiones_usadas_ids = regiones_usadas.values_list('region__id', flat=True).distinct()

        # Filtra las recomendadas que no están usadas
        if regiones_usadas_ids:
            regiones_no_usadas = regiones_recomendadas.exclude(id__in=regiones_usadas_ids)
        else:
            regiones_no_usadas = regiones_recomendadas

        # Transforma las regiones restantes al formato deseado
        regiones_no_usadas_label_value = [{
            'label': region.region,
            'value': str(region.id)
        } for region in regiones_no_usadas]

        return regiones_no_usadas_label_value

    def get_regiones_temporalidad(self, obj):
        return self.get_unused_regions(obj, 'temporalidad_gradualidad')

    def get_temporalidad_opciones(self, obj):
        # Retornar las opciones de TEMPORALIDAD como una lista de diccionarios
        return [{'key': key, 'value': value} for key, value in Temporalidad.TEMPORALIDAD]

    def get_modalidad_ejercicio_opciones(self, obj):
        # Retornar las opciones de MODALIDAD_EJERCICIO como una lista de diccionarios
        return [{'key': key, 'value': value} for key, value in Competencia.MODALIDAD_EJERCICIO]

    def to_internal_value(self, data):

        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'recomendaciones_desfavorables',
            'temporalidad_gradualidad'
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
            region_data = data.pop('region', [])  # Extrae region data aquí y asegúrate de que sea una lista

            if item_id is not None and not delete_flag:
                obj, created = model.objects.update_or_create(
                    id=item_id,
                    competencia=instance,
                    defaults={**data}
                )
                obj.region.set(region_data)  # Usa set() para actualizar ManyToManyField
                obj.save()
            elif not delete_flag:
                obj = model.objects.create(competencia=instance, **data)
                obj.region.set(region_data)  # Igual aquí, después de crear el objeto
                obj.save()
            elif delete_flag:
                model.objects.filter(id=item_id).delete()

    def update(self, instance, validated_data):
        recomendaciones_desfavorables_data = validated_data.pop('recomendaciones_desfavorables', None)
        temporalidad_data = validated_data.pop('temporalidad_gradualidad', None)

        # Actualizar los atributos de Competencia
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear modelos anidados

        if recomendaciones_desfavorables_data:
            self.update_or_create_nested_instances(RecomendacionesDesfavorables, recomendaciones_desfavorables_data, instance)

        if temporalidad_data:
            self.update_or_create_nested_instances(Temporalidad, temporalidad_data, instance)
        return instance


class ImagenesRevisionSubdereSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ImagenesRevisionSubdere
        fields = ['imagen']


class PasoBaseSerializer(serializers.ModelSerializer):
    avance = serializers.SerializerMethodField()

    class Meta:
        model = PasoBase
        fields = [
            'pk',
            'nombre_paso',
            'numero_paso',
            'avance',
            'completado',
            'estado_stepper',
        ]

    def avance(self, obj):
        return obj.avance()


class Paso1ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso1RevisionFinalSubdere


class Paso2ResumenSerializer(PasoBaseSerializer):
    class Meta(PasoBaseSerializer.Meta):
        model = Paso2RevisionFinalSubdere


class ResumenFormularioSerializer(serializers.ModelSerializer):
    competencia_nombre = serializers.SerializerMethodField()
    paso1_revision_final_subdere = Paso1ResumenSerializer(read_only=True)
    paso2_revision_final_subdere = Paso2ResumenSerializer(read_only=True)
    formulario_completo = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'competencia_nombre',
            'formulario_final_enviado',
            'fecha_envio_formulario_final',
            'paso1_revision_final_subdere',
            'paso2_revision_final_subdere',
            'formulario_completo',
            'imprimir_formulario_final'
        ]

    def get_competencia_nombre(self, obj):
        return obj.nombre if obj else None

    def get_formulario_completo(self, obj):
        # Asume que ya existen las instancias de paso1 y paso2 para el objeto Competencia actual.
        paso1_completado = obj.paso1_revision_final_subdere.completado if hasattr(obj,
                                                                                  'paso1_revision_final_subdere') else False
        paso2_completado = obj.paso2_revision_final_subdere.completado if hasattr(obj,
                                                                                  'paso2_revision_final_subdere') else False
        # Retorna True si ambos pasos están completados, False en caso contrario.
        return paso1_completado and paso2_completado
