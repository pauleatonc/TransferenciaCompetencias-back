from rest_framework import serializers
#
from ...models import (
    Region,
    Comuna
)


class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = (
            'id',
            'comuna',
        )


class ComunaRegionSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='region.region')

    class Meta:
        model = Comuna
        fields = (
            'id',
            'comuna',
            'region'
        )


class RegionComunaSerializer(serializers.ModelSerializer):
    comunas = ComunaSerializer(many=True, read_only=True, source='comunas.all')

    class Meta:
        model = Region
        fields = (
            'id',
            'region',
            'comunas'
        )

class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = (
            'id',
            'region',
        )