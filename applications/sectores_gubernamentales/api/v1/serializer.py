from rest_framework import serializers
#
from ...models import SectorGubernamental


class SectorGubernamentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorGubernamental
        fields = (
            'id',
            'nombre',
        )