from rest_framework import serializers
from applications.competencias.models import Competencia

class CompetenciaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = ['id', 'nombre', 'ambito', 'origen', 'estado']

class CompetenciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = '__all__'

class CompetenciaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = '__all__'

class CompetenciaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = '__all__'
