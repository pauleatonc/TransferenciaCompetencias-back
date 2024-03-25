from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from applications.competencias.models import (
    Competencia,
    RecomendacionesDesfavorables,
    Temporalidad,
    Gradualidad,
    Paso1RevisionFinalSubdere,
    Paso2RevisionFinalSubdere,
)

from applications.competencias.api.v1.serializers import (
    AmbitoSerializer,
    SectorSerializer
)

from applications.regioncomuna.api.v1.serializer import RegionSerializer


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
            'justificacion_temporalidad'
        ]

    def get_region_label_value(self, obj):
        # Obtiene todas las regiones asociadas y las transforma al formato {label, value}
        return [{
            'label': region.region,  # Usamos nombre_region para el label
            'value': str(region.id)  # El ID de la region como value
        } for region in obj.region.all()]


class GradualidadSerializer(serializers.ModelSerializer):
    region_label_value = serializers.SerializerMethodField()
    class Meta:
        model = Gradualidad
        fields = [
            'id',
            'region',
            'region_label_value',
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
    calcular_tiempo_transcurrido = serializers.SerializerMethodField()
    ultimo_editor = serializers.SerializerMethodField()
    fecha_ultima_modificacion = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
            'sectores',
            'calcular_tiempo_transcurrido',
            'ultimo_editor',
            'fecha_ultima_modificacion',
        ]

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
    ambito_definitivo_competencia = AmbitoSerializer()
    sectores = SectorSerializer(many=True, read_only=True)
    regiones_recomendadas = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'paso1_revision_final_subdere',
            'nombre',
            'sectores',
            'ambito_definitivo_competencia',
            'regiones_recomendadas'
        ]

    def get_regiones_recomendadas(self, obj):
        # Filtramos las regiones que ya están en 'regiones' para la competencia.
        regiones_qs = obj.regiones.all()

        # Serializamos las regiones y devolvemos los datos.
        return RegionSerializer(regiones_qs, many=True).data


class RevisionFinalCompetenciaPaso2Serializer(serializers.ModelSerializer):
    paso2_revision_final_subdere = Paso2RevisionFinalSubdereSerializer()
    recomendaciones_desfavorables = RecomendacionesDesfavorablesSerializer(many=True, read_only=False)
    temporalidad = TemporalidadSerializer(many=True, read_only=False)
    gradualidad = GradualidadSerializer(many=True, read_only=False)
    sectores = SectorSerializer(many=True, read_only=True)

    class Meta:
        model = Competencia
        fields = [
            'id',
            'paso2_revision_final_subdere',
            'nombre',
            'sectores',
            'recomendaciones_desfavorables',
            'temporalidad',
            'gradualidad',
            'recursos_requeridos',
            'modalidad_ejercicio',
            'implementacion_acompanamiento',
            'condiciones_ejercicio',
        ]

    def to_internal_value(self, data):

        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'recomendaciones_desfavorables',
            'temporalidad',
            'gradualidad'
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
        temporalidad_data = validated_data.pop('temporalidad', None)
        gradualidad_data = validated_data.pop('gradualidad', None)

        # Actualizar los atributos de Competencia
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear modelos anidados

        if recomendaciones_desfavorables_data:
            self.update_or_create_nested_instances(RecomendacionesDesfavorables, recomendaciones_desfavorables_data, instance)

        if temporalidad_data:
            self.update_or_create_nested_instances(Temporalidad, temporalidad_data, instance)

        if gradualidad_data:
            self.update_or_create_nested_instances(Gradualidad, gradualidad_data, instance)

        return instance