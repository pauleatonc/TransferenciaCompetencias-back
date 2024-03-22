from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from applications.formularios_gores.models import ObservacionesSubdereFormularioGORE, FormularioGORE

User = get_user_model()


class CamposObservacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservacionesSubdereFormularioGORE
        fields = [
            'id',
            'observacion_paso1',
            'observacion_paso2',
            'observacion_paso3',
            'observacion_enviada',
            'fecha_envio',
        ]


class ObservacionesSubdereSerializer(WritableNestedModelSerializer):
    observaciones_gore = CamposObservacionesSerializer()

    class Meta:
        model = FormularioGORE
        fields = [
            'id',
            'observaciones_gore'
        ]

    def update_observaciones_instance(self, instance, observaciones_gore_data):
        observaciones_gore_instance = getattr(instance, 'observaciones_gore', None)
        if observaciones_gore_instance:
            for attr, value in observaciones_gore_data.items():
                setattr(observaciones_gore_instance, attr, value)
            observaciones_gore_instance.save()
        else:
            ObservacionesSubdereFormularioGORE.objects.create(formulario_gore=instance, **observaciones_gore_data)

    def update(self, instance, validated_data):
        observaciones_data = validated_data.pop('observaciones_gore', None)

        # Actualizar los atributos de FormularioGORE
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear ObservacionesSubdereFormularioGORE
        if observaciones_data is not None:
            self.update_observaciones_instance(instance, observaciones_data)


        return instance
