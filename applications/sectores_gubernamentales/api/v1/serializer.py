from rest_framework import serializers
#
from applications.sectores_gubernamentales.models import SectorGubernamental, Ministerio


class SectorGubernamentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorGubernamental
        fields = (
            'id',
            'nombre',
        )


class MinisterioSerializer(serializers.ModelSerializer):
    sectores = SectorGubernamentalSerializer(many=True, read_only=True, source='servicios')

    class Meta:
        model = Ministerio
        fields = (
            'id',
            'nombre',
            'sectores',
        )

