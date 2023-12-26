from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    OrganismosIntervinientes,
    UnidadesIntervinientes,
    EtapasEjercicioCompetencia,
    ProcedimientosEtapas,
    PlataformasySoftwares,
    FlujogramaCompetencia
)
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.formularios_sectoriales.models import Paso2
from .base_serializer import FormularioSectorialDetailSerializer

User = get_user_model()


class OrganismosIntervinientesSerializer(serializers.ModelSerializer):
    organismo_display = serializers.SerializerMethodField()

    class Meta:
        model = OrganismosIntervinientes
        fields = [
            'id',
            'organismo',
            'organismo_display',
            'sector_ministerio_servicio',
            'descripcion'
        ]

    def get_organismo_display(self, obj):
        return obj.get_organismo_display()


class UnidadesIntervinientesSerializer(serializers.ModelSerializer):
    organismo = OrganismosIntervinientesSerializer(read_only=True)

    class Meta:
        model = UnidadesIntervinientes
        fields = [
            'id',
            'nombre_unidad',
            'descripcion_unidad',
            'organismo'
        ]


class ProcedimientosEtapasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedimientosEtapas
        fields = [
            'id',
            'etapa',
            'descripcion_procedimiento',
            'unidades_intervinientes'
        ]


class EtapasEjercicioCompetenciaSerializer(serializers.ModelSerializer):
    procedimientos = ProcedimientosEtapasSerializer(many=True)

    class Meta:
        model = EtapasEjercicioCompetencia
        fields = [
            'id',
            'nombre_etapa',
            'descripcion_etapa',
            'procedimientos'
        ]

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'procedimientos',
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


class PlataformasySoftwaresSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlataformasySoftwares
        fields = [
            'id',
            'nombre_plataforma',
            'descripcion_tecnica',
            'costo_adquisicion',
            'costo_mantencion_anual',
            'descripcion_costos',
            'descripcion_tecnica',
            'funcion_plataforma',
            'etapas',
            'capacitacion_plataforma'
        ]


class FlujogramaCompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlujogramaCompetencia
        fields = [
            'id',
            'flujograma_competencia',
            'descripcion_cualitativa'
        ]


class Paso2EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso2
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


class Paso2Serializer(serializers.ModelSerializer):
    paso2 = Paso2EncabezadoSerializer(many=True, read_only=False)
    p_2_1_organismos_intervinientes = OrganismosIntervinientesSerializer(many=True, read_only=False)
    p_2_2_unidades_intervinientes = UnidadesIntervinientesSerializer(many=True, read_only=False)
    p_2_3_etapas_ejercicio_competencia = EtapasEjercicioCompetenciaSerializer(many=True, read_only=False)
    p_2_4_plataformas_y_softwares = PlataformasySoftwaresSerializer(many=True, read_only=False)
    p_2_5_flujograma_competencia = FlujogramaCompetenciaSerializer(many=True, read_only=False)
    listado_unidades = serializers.SerializerMethodField()
    listado_etapas = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'paso2',
            'p_2_1_organismos_intervinientes',
            'p_2_2_unidades_intervinientes',
            'p_2_3_etapas_ejercicio_competencia',
            'p_2_4_plataformas_y_softwares',
            'p_2_5_flujograma_competencia',
            'listado_unidades',
            'listado_etapas',
        ]

    def get_listado_unidades(self, obj):
        unidades = UnidadesIntervinientes.objects.filter(formulario_sectorial=obj)
        return [{'id': unidad.id, 'nombre_unidad': unidad.nombre_unidad} for unidad in unidades]

    def get_listado_etapas(self, obj):
        etapas = EtapasEjercicioCompetencia.objects.filter(formulario_sectorial=obj)
        return [{'id': etapa.id, 'nombre_etapa': etapa.nombre_etapa} for etapa in etapas]

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'p_2_1_organismos_intervinientes',
            'p_2_2_unidades_intervinientes',
            'p_2_3_etapas_ejercicio_competencia',
            'p_2_4_plataformas_y_softwares',
            'p_2_5_flujograma_competencia',
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
        organismos_data = validated_data.pop('p_2_1_organismos_intervinientes', None)
        unidades_data = validated_data.pop('p_2_2_unidades_intervinientes', None)
        etapas_data = validated_data.pop('p_2_3_etapas_ejercicio_competencia', None)
        plataformas_data = validated_data.pop('p_2_4_plataformas_y_softwares', None)
        flujograma_data = validated_data.pop('p_2_5_flujograma_competencia', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear OrganismosIntervinientes
        if organismos_data is not None:
            self.update_or_create_nested_instances(OrganismosIntervinientes, organismos_data, instance)

        # Similar para UnidadesIntervinientes
        if unidades_data is not None:
            self.update_or_create_nested_instances(UnidadesIntervinientes, unidades_data, instance)

        if etapas_data is not None:
            for etapa_data in etapas_data:
                etapa_id = etapa_data.pop('id', None)
                delete_flag = etapa_data.pop('DELETE', False)  # Flag de eliminación para etapas
                procedimientos_data = etapa_data.pop('procedimientos', [])

                if delete_flag:
                    EtapasEjercicioCompetencia.objects.filter(id=etapa_id).delete()
                    print(f"Etapa eliminada: ID {etapa_id}")
                    continue  # Continúa con la siguiente etapa

                etapa_instance, _ = EtapasEjercicioCompetencia.objects.update_or_create(
                    id=etapa_id,
                    defaults=etapa_data,
                    formulario_sectorial=instance
                )

                for proc_data in procedimientos_data:
                    proc_id = proc_data.pop('id', None)
                    delete_flag_proc = proc_data.pop('DELETE', False)  # Flag de eliminación para procedimientos
                    unidades = proc_data.pop('unidades_intervinientes', [])

                    if delete_flag_proc:
                        ProcedimientosEtapas.objects.filter(id=proc_id).delete()
                        print(f"Procedimiento eliminado: ID {proc_id}")
                        continue  # Continúa con el siguiente procedimiento

                    proc_instance, _ = ProcedimientosEtapas.objects.update_or_create(
                        id=proc_id,
                        defaults={
                            **proc_data,
                            'etapa': etapa_instance,
                            'formulario_sectorial': instance
                        }
                    )

                    if unidades is not None:  # Revisa si 'unidades' es None o una lista vacía
                        proc_instance.unidades_intervinientes.set(unidades)

        if plataformas_data is not None:
            self.update_or_create_nested_instances(PlataformasySoftwares, plataformas_data, instance)

        if flujograma_data is not None:
            self.update_or_create_nested_instances(FlujogramaCompetencia, flujograma_data, instance)

        return instance
