from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_sectoriales.models import (
    FormularioSectorial,
    Paso3,
    CoberturaAnual, Paso3Encabezado
)
from applications.regioncomuna.models import Region  # Asegúrate de importar el modelo Region

User = get_user_model()


class CoberturaAnualSerializer(serializers.ModelSerializer):
    total_cobertura_efectiva = serializers.SerializerMethodField()

    class Meta:
        model = CoberturaAnual
        fields = [
            'id',
            'anio',
            'universo_cobertura',
            'cobertura_efectivamente_abordada',
            'recursos_ejecutados',
            'total_cobertura_efectiva'
        ]

    def get_total_cobertura_efectiva(self, obj):
        return obj.total_cobertura_efectiva


class Paso3Serializer(serializers.ModelSerializer):
    avance = serializers.SerializerMethodField()

    class Meta:
        model = Paso3
        fields = [
            'id',
            'avance',
            'universo_cobertura',
            'descripcion_cobertura'
        ]

    def get_avance(self, obj):
        return obj.avance()


class RegionPaso3CoberturaSerializer(serializers.Serializer):
    region = serializers.CharField()
    paso3 = Paso3Serializer(many=True)
    cobertura_anual = CoberturaAnualSerializer(many=True)


class Paso3EncabezadoSerializer(serializers.ModelSerializer):
    nombre_paso = serializers.ReadOnlyField()
    numero_paso = serializers.ReadOnlyField()
    avance = serializers.SerializerMethodField()
    campos_obligatorios_completados = serializers.ReadOnlyField()
    estado_stepper = serializers.ReadOnlyField()

    class Meta:
        model = Paso3Encabezado
        fields = [
            'id',
            'nombre_paso',
            'numero_paso',
            'avance',
            'campos_obligatorios_completados',
            'estado_stepper'
        ]

    def get_avance(self, obj):
        return obj.avance()


class Paso3GeneralSerializer(WritableNestedModelSerializer):
    paso3encabezado = Paso3EncabezadoSerializer()
    solo_lectura = serializers.SerializerMethodField()
    regiones = serializers.SerializerMethodField()

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'paso3encabezado',
            'solo_lectura',
            'regiones',
        ]

    def get_solo_lectura(self, obj):
        user = self.context['request'].user
        if obj.formulario_enviado:
            return True  # Si el formulario ya fue enviado, siempre es solo lectura
        else:
            return user.perfil != 'Usuario Sectorial'  # Solo los usuarios con perfil 'Usuario Sectorial' pueden editar

    def get_regiones(self, obj):
        regiones_data = []
        regiones = obj.competencia.regiones.all()

        for region in regiones:
            paso3_instances = Paso3.objects.filter(formulario_sectorial=obj, region=region)
            cobertura_instances = CoberturaAnual.objects.filter(formulario_sectorial=obj, region=region)

            regiones_data.append({
                'region': region.region,
                'paso3': Paso3Serializer(paso3_instances, many=True).data,
                'cobertura_anual': CoberturaAnualSerializer(cobertura_instances, many=True).data
            })

        return regiones_data

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)

        if 'regiones' in data:
            nested_data = data['regiones']
            internal_nested_data = []
            for region_data in nested_data:
                region = region_data.get('region')
                paso3_data = region_data.get('paso3', [])
                cobertura_anual_data = region_data.get('cobertura_anual', [])

                internal_paso3_data = []
                for item in paso3_data:
                    if 'DELETE' in item and item['DELETE'] == True:
                        internal_paso3_data.append({'id': item['id'], 'DELETE': True})
                    else:
                        item_data = Paso3Serializer().to_internal_value(item)
                        item_data['id'] = item.get('id')
                        internal_paso3_data.append(item_data)

                internal_cobertura_anual_data = []
                for item in cobertura_anual_data:
                    if 'DELETE' in item and item['DELETE'] == True:
                        internal_cobertura_anual_data.append({'id': item['id'], 'DELETE': True})
                    else:
                        item_data = CoberturaAnualSerializer().to_internal_value(item)
                        item_data['id'] = item.get('id')
                        internal_cobertura_anual_data.append(item_data)

                internal_nested_data.append({
                    'region': region,
                    'paso3': internal_paso3_data,
                    'cobertura_anual': internal_cobertura_anual_data
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
                paso3_data = region_data.pop('paso3', [])
                cobertura_data = region_data.pop('cobertura_anual', [])

                # Obtener la región correspondiente
                region = instance.competencia.regiones.get(region=region_name)

                if paso3_data:
                    for paso_data in paso3_data:
                        paso_data['region'] = region.region
                    self.update_or_create_nested_instances(Paso3, paso3_data, instance)

                if cobertura_data:
                    for cobertura_data_item in cobertura_data:
                        cobertura_data_item['region'] = region.region
                    self.update_or_create_nested_instances(CoberturaAnual, cobertura_data, instance)

        return instance