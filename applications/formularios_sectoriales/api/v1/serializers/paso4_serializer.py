from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso4,
    Paso4Encabezado,
    IndicadorDesempeno
)
from applications.regioncomuna.models import Region

User = get_user_model()


class IndicadorDesempenoSerializer(serializers.ModelSerializer):
    indicador_display = serializers.SerializerMethodField()
    class Meta:
        model = IndicadorDesempeno
        fields = [
            'id',
            'indicador',
            'indicador_display',
            'formula_calculo',
            'descripcion_indicador',
            'medios_calculo',
            'verificador_asociado'
        ]

    def get_indicador_display(self, obj):
        return obj.get_indicador_display()


class Paso4Serializer(serializers.ModelSerializer):
    avance = serializers.SerializerMethodField()

    class Meta:
        model = Paso4
        fields = [
            'id',
            'avance'
        ]

    def get_avance(self, obj):
        return obj.avance()


class Paso4EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    multiplicador_caracteres_region = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso4Encabezado
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'multiplicador_caracteres_region',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper',
        ]

    def avance(self, obj):
        return obj.avance()


class RegionPaso4DesempenoSerializer(serializers.Serializer):
    region = serializers.CharField()
    paso4 = Paso4Serializer(many=True)
    indicador_desempeno = IndicadorDesempenoSerializer(many=True)


class Paso4GeneralSerializer(WritableNestedModelSerializer):
    paso4encabezado = Paso4EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    regiones = serializers.SerializerMethodField()
    lista_indicadores = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'paso4encabezado',
            'solo_lectura',
            'regiones',
            'lista_indicadores',
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        # La lógica se actualiza para considerar el estado de formulario_enviado y el perfil del usuario
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            # Si el formulario no ha sido enviado, solo los usuarios con perfil 'Usuario Sectorial' pueden editar
            return user.perfil != 'Usuario Sectorial'

    def get_lista_indicadores(self, obj):
        # Retornar clave y valor para choices INDICADOR
        return {clave: valor for clave, valor in IndicadorDesempeno.INDICADOR}

    def get_regiones(self, obj):
        regiones_data = []
        regiones = obj.competencia.regiones.all()

        for region in regiones:
            paso4_instances = Paso4.objects.filter(formulario_sectorial=obj, region=region)
            indicador_desempeno_instances = IndicadorDesempeno.objects.filter(formulario_sectorial=obj, region=region)

            regiones_data.append({
                'region': region.region,
                'paso4': Paso4Serializer(paso4_instances, many=True).data,
                'indicador_desempeno': IndicadorDesempenoSerializer(indicador_desempeno_instances, many=True).data
            })

        return regiones_data

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)

        if 'regiones' in data:
            nested_data = data['regiones']
            internal_nested_data = []
            for region_data in nested_data:
                region = region_data.get('region')
                paso4_data = region_data.get('paso4', [])
                indicador_desempeno_data = region_data.get('indicador_desempeno', [])

                internal_paso4_data = []
                for item in paso4_data:
                    if 'DELETE' in item and item['DELETE'] == True:
                        internal_paso4_data.append({'id': item['id'], 'DELETE': True})
                    else:
                        item_data = Paso4Serializer().to_internal_value(item)
                        item_data['id'] = item.get('id')
                        internal_paso4_data.append(item_data)

                internal_data = []
                for item in indicador_desempeno_data:
                    if 'DELETE' in item and item['DELETE'] == True:
                        internal_data.append({'id': item['id'], 'DELETE': True})
                    else:
                        item_data = IndicadorDesempenoSerializer().to_internal_value(item)
                        item_data['id'] = item.get('id')
                        internal_data.append(item_data)

                internal_nested_data.append({
                    'region': region,
                    'paso4': internal_paso4_data,
                    'indicador_desempeno': internal_data
                })

            internal_value['regiones'] = internal_nested_data

        return internal_value

    def update_or_create_nested_instances(self, model, nested_data, instance):
        for data in nested_data:
            print(f"Processing data: {data}")
            item_id = data.pop('id', None)
            delete_flag = data.pop('DELETE', False)
            region_name = data.pop('region', None)

            # Obtener la instancia de Region
            if region_name:
                region = Region.objects.get(region=region_name)
                data['region'] = region

            if item_id is not None:
                if delete_flag:
                    print(f"Deleting {model.__name__} with id: {item_id}")
                    model.objects.filter(id=item_id).delete()
                else:
                    print(f"Updating {model.__name__} with id: {item_id}")
                    model.objects.filter(id=item_id).update(**data)
            elif not delete_flag:
                print(f"Creating new {model.__name__} with data: {data}")
                model.objects.create(formulario_sectorial=instance, **data)

    def update(self, instance, validated_data):
        regiones_data = validated_data.pop('regiones', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if regiones_data is not None:
            for region_data in regiones_data:
                region_name = region_data.get('region')
                paso4_data = region_data.pop('paso4', [])
                indicador_data = region_data.pop('indicador_desempeno', [])

                # Obtener la región correspondiente
                region = instance.competencia.regiones.get(region=region_name)

                if paso4_data:
                    for paso_data in paso4_data:
                        paso_data['region'] = region.region
                    self.update_or_create_nested_instances(Paso4, paso4_data, instance)

                if indicador_data:
                    for cobertura_data_item in indicador_data:
                        cobertura_data_item['region'] = region.region
                    self.update_or_create_nested_instances(IndicadorDesempeno, indicador_data, instance)

        return instance