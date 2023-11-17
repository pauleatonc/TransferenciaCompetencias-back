from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1


class CompetenciaListSerializer(serializers.ModelSerializer):

    ambito = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    origen = serializers.SerializerMethodField()
    class Meta:
        model = Competencia
        fields = ['id', 'nombre', 'ambito', 'estado', 'origen']

    def get_ambito(self, obj):
        return obj.get_ambito_display()

    def get_estado(self, obj):
        return obj.get_estado_display()

    def get_origen(self, obj):
        return obj.get_origen_display()

class CompetenciaHomeListSerializer(serializers.ModelSerializer):

    etapas_info = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = ['id', 'nombre', 'etapas_info', 'tiempo_transcurrido']

    def get_etapas_info(self, obj):
        etapas_info = {}
        for i in range(1, 6):  # Asumiendo que tienes etapas de 1 a 5
            etapa_model = globals().get(f'Etapa{i}')
            if etapa_model:
                etapa = etapa_model.objects.filter(competencia=obj).first()
                if etapa:
                    etapas_info[f'Etapa{i}'] = {
                        'nombre': etapa.nombre_etapa,
                        'estado': etapa.estado
                    }
        return etapas_info


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
