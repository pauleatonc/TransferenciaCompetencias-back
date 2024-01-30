from rest_framework import serializers
from applications.competencias.models import Competencia, Ambito
from applications.etapas.models import Etapa1, Etapa2, Etapa3, Etapa4, Etapa5
from django.contrib.auth import get_user_model

from applications.regioncomuna.models import Region
from applications.sectores_gubernamentales.models import SectorGubernamental

from applications.etapas.api.v1.serializers import Etapa1Serializer, Etapa2Serializer, Etapa3Serializer, \
    Etapa4Serializer, Etapa5Serializer

User = get_user_model()


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorGubernamental
        fields = ('id', 'nombre')

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'region')

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
        return obj.ambito_competencia.nombre if obj.ambito_competencia else None

    def get_competencia_nombre(self, obj):
        return obj.competencia.nombre if obj.competencia else None

    def get_estado(self, obj):
        return obj.get_estado_display()

    def get_origen(self, obj):
        return obj.get_origen_display()


class CompetenciaListAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
        ]


class CompetenciaHomeListSerializer(serializers.ModelSerializer):

    etapas_info = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = ['id', 'nombre', 'etapas_info', 'tiempo_transcurrido']

    def get_etapas_info(self, obj):
        return obtener_informacion_etapas(obj)


class CompetenciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = '__all__'


class CompetenciaUpdateSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False)
    plazo_formulario_sectorial = serializers.IntegerField(required=False)
    plazo_formulario_gore = serializers.IntegerField(required=False)
    sectores = serializers.PrimaryKeyRelatedField(many=True, queryset=SectorGubernamental.objects.all(), required=False)
    regiones = serializers.PrimaryKeyRelatedField(many=True, queryset=Region.objects.all(), required=False)

    class Meta:
        model = Competencia
        fields = '__all__'
        extra_kwargs = {'creado_por': {'read_only': True}}


def obtener_informacion_etapas(competencia):
    etapas_info = {}
    for i in range(1, 6):
        etapa_model = globals().get(f'Etapa{i}')
        if etapa_model:
            etapa = etapa_model.objects.filter(competencia=competencia).first()
            if etapa:
                etapas_info[f'Etapa{i}'] = {
                    'nombre': etapa.nombre_etapa,
                    'estado': etapa.get_estado_display()
                }
    return etapas_info


class CompetenciaDetailSerializer(serializers.ModelSerializer):
    etapa1 = Etapa1Serializer()
    etapa2 = Etapa2Serializer()
    etapa3 = Etapa3Serializer()
    etapa4 = Etapa4Serializer()
    etapa5 = Etapa5Serializer()
    usuarios_subdere = UsuarioSerializer(many=True, read_only=True)
    usuarios_dipres = UsuarioSerializer(many=True, read_only=True)
    usuarios_sectoriales = UsuarioSerializer(many=True, read_only=True)
    usuarios_gore = UsuarioSerializer(many=True, read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    sectores = SectorSerializer(many=True, read_only=True)
    resumen_competencia = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id',
            'nombre',
            'resumen_competencia',
            'sectores',
            'regiones',
            'origen',
            'ambito_competencia',
            'oficio_origen',
            'fecha_inicio',
            'plazo_formulario_sectorial',
            'plazo_formulario_gore',
            'etapa1',
            'etapa2',
            'etapa3',
            'etapa4',
            'etapa5',
            'tiempo_transcurrido',
            'usuarios_subdere',
            'usuarios_dipres',
            'usuarios_sectoriales',
            'usuarios_gore',

        ]

    def get_tiempo_transcurrido(self, obj):
        return obj.tiempo_transcurrido()

    def get_resumen_competencia(self, obj):
        etapas_info = obtener_informacion_etapas(obj)
        return {
            'id': obj.id,
            'nombre': obj.nombre,
            'etapas_info': etapas_info,
            'tiempo_transcurrido': obj.tiempo_transcurrido()
        }


class AmbitoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambito
        fields = ('id', 'nombre')


class OrigenSerializer(serializers.Serializer):
    clave = serializers.CharField(max_length=2)
    descripcion = serializers.CharField(max_length=30)
