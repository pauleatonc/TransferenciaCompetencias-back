from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_sectoriales.models import FormularioSectorial
from applications.formularios_sectoriales.models import ObservacionesSubdereFormularioSectorial

User = get_user_model()


class CamposObservacionesSerializer(serializers.ModelSerializer):
    documento = serializers.FileField(required=False, allow_null=True)

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
            'documento',
            'descripcion_documento',
            'fecha_envio',
        ]


class ObservacionesSubdereSerializer(WritableNestedModelSerializer):
    observaciones_sectoriales = CamposObservacionesSerializer()

    class Meta:
        model = FormularioSectorial
        fields = [
            'id',
            'observaciones_sectoriales'
        ]

    def update_observaciones_instance(self, instance, observaciones_sectoriales_data):
        observaciones_sectoriales_instance = getattr(instance, 'observaciones_sectoriales', None)
        if observaciones_sectoriales_instance:
            for attr, value in observaciones_sectoriales_data.items():
                setattr(observaciones_sectoriales_instance, attr, value)
            observaciones_sectoriales_instance.save()
        else:
            ObservacionesSubdereFormularioSectorial.objects.create(formulario_sectorial=instance, **observaciones_sectoriales_data)

    def update(self, instance, validated_data):
        observaciones_data = validated_data.pop('observaciones_sectoriales', None)

        # Actualizar los atributos de FormularioSectorial
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear ObservacionesSubdereFormularioSectorial
        if observaciones_data is not None:
            self.update_observaciones_instance(instance, observaciones_data)


        return instance
