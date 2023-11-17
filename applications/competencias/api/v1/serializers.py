from rest_framework import serializers
from applications.competencias.models import Competencia
from applications.etapas.models import Etapa1
from django.contrib.auth import get_user_model

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

from applications.etapas.api.v1.serializers import Etapa1Serializer

User = get_user_model()


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorGubernamental
        fields = ('nombre',)  # Asume que tu modelo SectorGubernamental tiene un campo 'nombre'

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('region',)

class UsuarioSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.SerializerMethodField()
    region_nombre = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'nombre_completo', 'email', 'sector_nombre', 'region_nombre')  # Añade los campos necesarios

    def get_sector_nombre(self, obj):
        if obj.sector:
            return obj.sector.nombre
        return None

    def get_region_nombre(self, obj):
        if obj.region:
            return obj.region.region
        return None


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
    etapa1 = Etapa1Serializer(source='etapa1_set', many=True)
    usuarios_subdere = UsuarioSerializer(many=True, read_only=True)
    usuarios_dipres = UsuarioSerializer(many=True, read_only=True)
    usuarios_sectoriales = UsuarioSerializer(many=True, read_only=True)
    usuarios_gore = UsuarioSerializer(many=True, read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
            'etapa1',
            'tiempo_transcurrido',
            'usuarios_subdere',
            'usuarios_dipres',
            'usuarios_sectoriales',
            'usuarios_gore',

        ]

    def get_tiempo_transcurrido(self, obj):
        return obj.tiempo_transcurrido()
