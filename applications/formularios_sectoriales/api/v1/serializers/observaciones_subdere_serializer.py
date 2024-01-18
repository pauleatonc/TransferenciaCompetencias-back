from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.formularios_sectoriales.models import FormularioSectorial, MarcoJuridico, OrganigramaRegional
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental
from applications.formularios_sectoriales.models import ObservacionesSubdereFormularioSectorial
from .base_serializer import FormularioSectorialDetailSerializer


User = get_user_model()


class CamposObservacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservacionesSubdereFormularioSectorial
        fields = [
            'id',
            'observacion_paso1',
            'observacion_paso2',
            'observacion_paso3',
            'observacion_paso4',
            'observacion_paso5',
            'observacion_enviada',
            'fecha_envio',
        ]


class ObservacionesSubdereSerializer(serializers.ModelSerializer):
    observaciones_sectoriales = CamposObservacionesSerializer()

    class Meta:
        model = FormularioSectorial
        fields = [
            'observaciones_sectoriales'
        ]

    def to_internal_value(self, data):
        # Maneja primero los campos no anidados
        internal_value = super().to_internal_value(data)

        # Procesar campos anidados
        for field_name in [
            'observaciones_sectoriales',
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
        observaciones_data = validated_data.pop('observaciones_sectoriales', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear ObservacionesSubdereFormularioSectorial
        if observaciones_data is not None:
            self.update_or_create_nested_instances(ObservacionesSubdereFormularioSectorial, observaciones_data, instance)


        return instance
