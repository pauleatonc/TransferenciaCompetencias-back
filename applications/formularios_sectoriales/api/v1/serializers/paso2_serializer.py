from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    OrganismosIntervinientes,
    UnidadesIntervinientes,
    EtapasEjercicioCompetencia,
    ProcedimientosEtapas,
    PlataformasySoftwares,
    FlujogramaCompetencia
)
from applications.formularios_sectoriales.models import Paso2

User = get_user_model()


class OrganismosIntervinientesSerializer(serializers.ModelSerializer):
    organismo_display = serializers.SerializerMethodField()

    class Meta:
        model = OrganismosIntervinientes
        fields = [
            'id',
            'organismo',
            'organismo_display',
            'nombre_ministerio_servicio',
            'descripcion'
        ]

    def get_organismo_display(self, obj):
        return obj.get_organismo_display()


class UnidadesIntervinientesSerializer(serializers.ModelSerializer):
    organismo_id = serializers.IntegerField(write_only=True)
    organismo = OrganismosIntervinientesSerializer()

    class Meta:
        model = UnidadesIntervinientes
        fields = [
            'id',
            'nombre_unidad',
            'descripcion_unidad',
            'organismo',
            'organismo_id'
        ]


class ProcedimientosEtapasSerializer(serializers.ModelSerializer):
    unidades_intervinientes_label_value = serializers.SerializerMethodField()

    class Meta:
        model = ProcedimientosEtapas
        fields = [
            'id',
            'etapa',
            'descripcion_procedimiento',
            'unidades_intervinientes',
            'unidades_intervinientes_label_value',  # Campo personalizado
        ]

    def get_unidades_intervinientes_label_value(self, obj):
        # Obtiene todas las unidades intervinientes y las transforma al formato {label, value}
        return [{
            'label': unidad.nombre_unidad,  # Suponiendo que 'nombre_unidad' es el campo de label deseado
            'value': str(unidad.id)  # Convierte el ID de la unidad a string para el value
        } for unidad in obj.unidades_intervinientes.all()]


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
    etapas_label_value = serializers.SerializerMethodField()
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
            'capacitacion_plataforma',
            'etapas_label_value'
        ]

    def get_etapas_label_value(self, obj):
        # Obtiene todas las etapas asociadas y las transforma al formato {label, value}
        return [{
            'label': etapa.nombre_etapa,  # Usamos nombre_etapa para el label
            'value': str(etapa.id)  # El ID de la etapa como value
        } for etapa in obj.etapas.all()]


class FlujogramaCompetenciaSerializer(serializers.ModelSerializer):
    flujograma_competencia = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = FlujogramaCompetencia
        fields = [
            'id',
            'flujograma_competencia'
        ]


class Paso2EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    multiplicador_caracteres_region = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso2
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'multiplicador_caracteres_region',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
            'descripcion_cualitativa'
        ]

    def avance(self, obj):
        return obj.avance()


class Paso2Serializer(serializers.ModelSerializer):
    paso2 = Paso2EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    p_2_1_organismos_intervinientes = OrganismosIntervinientesSerializer(many=True, read_only=False)
    p_2_2_unidades_intervinientes = UnidadesIntervinientesSerializer(many=True, read_only=False)
    p_2_3_etapas_ejercicio_competencia = EtapasEjercicioCompetenciaSerializer(many=True, read_only=False)
    p_2_4_plataformas_y_softwares = PlataformasySoftwaresSerializer(many=True, read_only=False)
    p_2_5_flujograma_competencia = FlujogramaCompetenciaSerializer(many=True, read_only=False)
    listado_unidades = serializers.SerializerMethodField()
    listado_etapas = serializers.SerializerMethodField()
    listado_organismos = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'paso2',
            'solo_lectura',
            'p_2_1_organismos_intervinientes',
            'p_2_2_unidades_intervinientes',
            'p_2_3_etapas_ejercicio_competencia',
            'p_2_4_plataformas_y_softwares',
            'p_2_5_flujograma_competencia',
            'listado_unidades',
            'listado_etapas',
            'listado_organismos',
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario Sectorial' pueden editar
            return user.perfil != 'Usuario Sectorial'

    def get_listado_unidades(self, obj):
        unidades = UnidadesIntervinientes.objects.filter(formulario_sectorial=obj)
        return [{'id': unidad.id, 'nombre_unidad': unidad.nombre_unidad} for unidad in unidades]

    def get_listado_etapas(self, obj):
        etapas = EtapasEjercicioCompetencia.objects.filter(formulario_sectorial=obj)
        return [{'id': etapa.id, 'nombre_etapa': etapa.nombre_etapa} for etapa in etapas]

    def get_listado_organismos(self, obj):
        # Obtener todos los organismos asignados al FormularioSectorial actual
        organismos_asignados = OrganismosIntervinientes.objects.filter(
            formulario_sectorial=obj
        ).values_list('organismo', flat=True)

        # Retornar clave y valor para choices ORGANISMO, excluyendo los ya asignados
        return {
            clave: valor
            for clave, valor in OrganismosIntervinientes.ORGANISMO
            if clave not in organismos_asignados
        }

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
        plataformas_data = validated_data.pop('p_2_4_plataformas_y_softwares', [])
        flujograma_data = validated_data.pop('p_2_5_flujograma_competencia', None)
        paso2_data = validated_data.pop('paso2', None)
        if paso2_data is not None:
            paso2_instance, created = Paso2.objects.update_or_create(
                formulario_sectorial=instance, 
                defaults=paso2_data
            )
            instance.paso2 = paso2_instance

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
            for plataforma_data in plataformas_data:
                plataforma_id = plataforma_data.pop('id', None)
                delete_flag = plataforma_data.pop('DELETE', False)
                etapas = plataforma_data.pop('etapas', [])

                if delete_flag:
                    PlataformasySoftwares.objects.filter(id=plataforma_id).delete()
                    print(f"Plataforma eliminada: ID {plataforma_id}")
                    continue

                plataforma_instance, _ = PlataformasySoftwares.objects.update_or_create(
                    id=plataforma_id,
                    defaults=plataforma_data,
                    formulario_sectorial=instance
                )

                if etapas is not None:
                    plataforma_instance.etapas.set(etapas)  # Actualiza la lista de etapas en plataformas
                    continue

        if flujograma_data is not None:
            self.update_or_create_nested_instances(FlujogramaCompetencia, flujograma_data, instance)

        return instance
